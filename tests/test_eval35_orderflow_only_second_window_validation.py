"""Tests for EVAL-35 orderflow-only second independent real data window validation (paper-only)."""

import json
import math

import pytest

from scripts.eval35_orderflow_only_second_window_validation import (
    REPORT_ID,
    TAPE_PATH,
    _all_finite_numbers,
    _kill_switch_triggers,
    _load_new_tape,
    _signal_positions,
    build_md,
    build_report,
)


def test_loads_new_real_window_via_real_loader():
    """(a) The new tape is loaded via the real loader; it is non-synthetic and has trades."""
    snap = _load_new_tape()
    assert snap is not None
    assert snap.trades is not None and len(snap.trades) > 0
    assert str(snap.venue).lower() == "okx"
    assert TAPE_PATH.exists(), f"EVAL-35 tape must exist at {TAPE_PATH}"
    # Tape must be the new independent window, not the sealed EVAL-23..34 tape.
    assert TAPE_PATH.name != "orderflow_okx_BTC-USD-SWAP.json"


def test_signal_positions_applies_threshold():
    """Thresholding maps net_aggression to -1/0/1 positions."""
    sigs = [0.5, -0.5, 0.05, -0.05, 0.0]
    pos = _signal_positions(sigs, threshold=0.1)
    assert pos == [1, -1, 0, 0, 0]


def test_kill_switch_triggers_read_only():
    """Kill-switch evaluation is read-only and reports breaches deterministically."""
    res = _kill_switch_triggers(
        max_dd=0.25, cost_usd=600.0, notional_usd=2_000_000.0, nav=100_000.0,
        toxic_gate_active_fraction=0.9,
    )
    assert res["max_drawdown_breached"] is True
    assert res["cost_bps_breached"] is True
    assert res["toxicity_breached"] is True
    assert res["notional_breached"] is True
    assert res["any_breach"] is True
    assert "max_drawdown" in res["triggers"]
    assert "cost_bps" in res["triggers"]
    assert "toxicity" in res["triggers"]
    assert "max_notional" in res["triggers"]

    res2 = _kill_switch_triggers(
        max_dd=0.05, cost_usd=1.0, notional_usd=100.0, nav=100_000.0,
        toxic_gate_active_fraction=0.1,
    )
    assert res2["any_breach"] is False
    assert res2["triggers"] == []


def test_build_report_structure_and_serialization():
    """(d) build_report returns a strict-serializable, fully-populated report."""
    report = build_report()
    assert report["report_id"] == REPORT_ID
    assert report["verdict"] in ("GO", "NO-GO")
    assert report["verdict_reason"] is not None and len(report["verdict_reason"]) > 0
    assert report["trading_mode"] == "paper"
    assert report["live_trading_enabled"] is False
    assert report["authenticity_verified"] is False
    assert report["data_provenance"] == "real_public_exchange_export"
    assert report["never_valid_true"] is True

    # Tape block
    assert report["tape"]["n_trades_total"] > 0
    assert report["tape"]["n_bars"] > 0
    assert report["tape"]["independent_of_eval_23_to_34"] is True
    assert report["tape"]["tape_path"] == str(TAPE_PATH)

    # Signal block
    assert report["signal"]["n_bars"] == report["tape"]["n_bars"]

    # Toxicity block
    assert report["toxicity"]["toxicity_measured"] is True
    assert 0.0 <= report["toxicity"]["mean_toxicity"] <= 1.0

    # Walk-forward block
    wf = report["walkforward"]
    assert wf["num_windows"] > 0
    assert wf["num_trades"] >= 0
    assert math.isfinite(wf["oos_sharpe"])
    assert math.isfinite(wf["total_cost_usd"])
    assert math.isfinite(wf["oos_max_drawdown"])

    # Kill-switch block
    ks = report["kill_switch"]
    assert "triggers" in ks
    assert isinstance(ks["any_breach"], bool)

    # Success block
    sc = report["success"]
    assert isinstance(sc["non_degenerate"], bool)
    assert isinstance(sc["within_band"], bool)
    assert sc["min_sharpe"] == 1.0

    # Portfolio certification
    pc = report["portfolio_certification"]
    assert pc["decision"] in ("CERTIFY_DEPLOY_PAPER_ONLY", "TERMINATE_NO_GO")
    assert len(pc["rationale"]) > 0
    assert pc["pre_declared_options"] == ["CERTIFY_DEPLOY_PAPER_ONLY", "TERMINATE_NO_GO"]

    # MD renderable
    md = build_md(report)
    assert REPORT_ID in md
    assert report["verdict"] in md
    assert pc["decision"] in md
    assert "## PORTFOLIO CERTIFICATION DECISION" in md
    assert "## KILL-SWITCH TRIGGERS" in md
    assert "## SUCCESS vs EVAL-34 HELD-OUT BAND" in md

    # Commands present
    assert len(report["commands"]) == 3
    assert "python3 -m py_compile" in report["commands"][0]
    assert "python3 -m pytest" in report["commands"][1]
    assert "python3 scripts/eval35_orderflow_only_second_window_validation.py" in report["commands"][2]


def test_non_degenerate_or_explicit_no_go():
    """(c) Non-degenerate (Sharpe > 1.0, trades > 0, cost > 0) or explicit NO-GO."""
    report = build_report()
    sc = report["success"]
    pc = report["portfolio_certification"]
    wf = report["walkforward"]

    if sc["non_degenerate"]:
        assert wf["oos_sharpe"] > 1.0, f"Sharpe {wf['oos_sharpe']} must exceed 1.0 when non-degenerate"
        assert wf["num_trades"] > 0, f"Trades {wf['num_trades']} must exceed 0 when non-degenerate"
        assert wf["total_cost_usd"] > 0.0, f"Cost {wf['total_cost_usd']} must exceed 0 when non-degenerate"
    else:
        # Explicitly records NO-GO with justification
        assert report["verdict"] == "NO-GO"
        assert pc["decision"] == "TERMINATE_NO_GO"
        assert len(pc["rationale"]) > 0


def test_decision_is_pre_declared_with_measured_justification():
    """(e) The decision is one of the two pre-declared options with measured justification."""
    report = build_report()
    pc = report["portfolio_certification"]
    wf = report["walkforward"]

    assert pc["decision"] in ("CERTIFY_DEPLOY_PAPER_ONLY", "TERMINATE_NO_GO")
    assert len(pc["rationale"]) > 0
    assert pc["max_notional_usd"] == 1_000_000.0
    assert pc["max_daily_loss_usd"] == 50_000.0
    assert pc["max_drawdown_pct"] == 0.20
    assert pc["toxicity_kill_switch_pct"] == 0.80
    assert pc["cost_kill_switch_bps"] == 5.0

    # Measured justification present in rationale
    assert f"{wf['oos_sharpe']:.4f}" in pc["rationale"] or f"{wf['oos_sharpe']:.6f}" in pc["rationale"]
    assert str(wf["num_trades"]) in pc["rationale"]
    assert f"{wf['total_cost_usd']:.2f}" in pc["rationale"]


def test_artifact_is_valid_json_strict_serialization():
    """The sealed report passes assert_json_valid and serialize_metrics_strict round-trip."""
    from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

    report = build_report()
    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)
    assert serialized["report_id"] == REPORT_ID
    # Round-trip JSON with allow_nan=False must not raise
    json.dumps(serialized, allow_nan=False)


def test_all_finite_numbers_helper():
    """Helper handles non-finite values gracefully."""
    assert _all_finite_numbers(3.14) is True
    assert _all_finite_numbers(float("nan")) is False
    assert _all_finite_numbers(float("inf")) is False
    assert _all_finite_numbers({"a": 1.0, "b": 2.0}) is True
    assert _all_finite_numbers({"a": float("nan")}) is False
    assert _all_finite_numbers([1.0, 2.0, 3.0]) is True
    assert _all_finite_numbers([1.0, float("inf")]) is False
    assert _all_finite_numbers(True) is True
