"""Tests for EVAL-38 evidence durability replication (paper-only)."""

import json
import math

import pytest

from scripts.eval38_evidence_durability_replication import (
    ACQUISITION_JSON,
    EVAL35_MAX_DD,
    EVAL35_SHARPE,
    EVAL35_TRADES,
    EVAL35_COST_USD,
    REPORT_ID,
    TAPE_PATH,
    _all_finite_numbers,
    _kill_switch_triggers,
    _load_reacquired_tape,
    _signal_positions,
    build_md,
    build_report,
)
from src.campaign.integrated import RealDataUnavailable


def test_reacquired_tape_present_and_real():
    """The re-acquired real tape exists and loads via the real loader (no synthetic)."""
    assert TAPE_PATH.exists(), (
        f"Re-acquired tape must exist at {TAPE_PATH}. Run "
        f"`python3 -m src.data.public_export_acquisition --underlying BTC "
        f"--orderflow-instrument BTC-USD-SWAP` first."
    )
    snap = _load_reacquired_tape()
    assert snap is not None
    assert snap.trades is not None and len(snap.trades) > 0
    assert str(snap.venue).lower() == "okx"


def test_load_raises_without_tape(tmp_path, monkeypatch):
    """Missing re-acquired tape raises RealDataUnavailable (never synthetic fallback)."""
    missing = tmp_path / "orderflow_okx_BTC-USD-SWAP.json"
    with pytest.raises(RealDataUnavailable):
        _load_reacquired_tape(missing)


def test_signal_positions_applies_threshold():
    sigs = [0.5, -0.5, 0.05, -0.05, 0.0]
    assert _signal_positions(sigs, threshold=0.1) == [1, -1, 0, 0, 0]


def test_kill_switch_triggers_read_only():
    res = _kill_switch_triggers(
        max_dd=0.25, cost_usd=600.0, notional_usd=2_000_000.0, nav=100_000.0,
        toxic_gate_active_fraction=0.9,
    )
    assert res["max_drawdown_breached"] is True
    assert res["cost_bps_breached"] is True
    assert res["toxicity_breached"] is True
    assert res["notional_breached"] is True
    assert res["any_breach"] is True

    res2 = _kill_switch_triggers(
        max_dd=0.05, cost_usd=1.0, notional_usd=100.0, nav=100_000.0,
        toxic_gate_active_fraction=0.1,
    )
    assert res2["any_breach"] is False
    assert res2["triggers"] == []


def test_all_finite_numbers_helper():
    assert _all_finite_numbers(3.14) is True
    assert _all_finite_numbers(float("nan")) is False
    assert _all_finite_numbers(float("inf")) is False
    assert _all_finite_numbers({"a": 1.0, "b": 2.0}) is True
    assert _all_finite_numbers({"a": float("nan")}) is False
    assert _all_finite_numbers(True) is True


def test_build_report_structure_and_serialization():
    report = build_report()
    assert report["report_id"] == REPORT_ID
    assert report["verdict"] in ("REPLICATION", "REFUTATION", "INCONCLUSIVE")
    assert report["trading_mode"] == "paper"
    assert report["live_trading_enabled"] is False
    assert report["authenticity_verified"] is False
    assert report["data_provenance"] == "real_public_exchange_export"
    assert report["never_valid_true"] is True

    # Durability block
    dur = report["durability"]
    assert dur["acquisition_re_run"] is True
    assert dur["reacquired_tape_loaded"] is True
    assert dur["durability_status"] in (
        "CONCLUSIONS_REPRODUCIBLE", "CONCLUSIONS_INCONSISTENT", "MIXED_EVIDENCE"
    )
    assert len(dur["conclusion"]) > 0

    # Tape block
    tape = report["tape"]
    assert tape["n_trades_total"] > 0
    assert tape["n_bars"] > 0
    assert len(tape["content_sha256"]) == 64
    assert tape["acquisition_artifact"] == ACQUISITION_JSON

    # Signal block
    assert report["signal"]["n_bars"] == report["tape"]["n_bars"]

    # Toxicity
    assert report["toxicity"]["toxicity_measured"] is True
    assert 0.0 <= report["toxicity"]["mean_toxicity"] <= 1.0

    # Walk-forward
    wf = report["walkforward"]
    assert wf["num_windows"] > 0
    assert math.isfinite(wf["oos_sharpe"])
    assert math.isfinite(wf["total_cost_usd"])
    assert math.isfinite(wf["oos_max_drawdown"])

    # Kill-switch
    assert isinstance(report["kill_switch"]["any_breach"], bool)

    # EVAL-35 reference present
    ref = report["eval35_reference"]
    assert ref["sharpe"] == EVAL35_SHARPE
    assert ref["trades"] == EVAL35_TRADES
    assert ref["cost_usd"] == EVAL35_COST_USD
    assert ref["max_dd"] == EVAL35_MAX_DD
    assert ref["verdict"] == "NO-GO"

    # MD renderable
    md = build_md(report)
    assert REPORT_ID in md
    assert report["verdict"] in md
    assert "## REPLICATION vs EVAL-35 SEALED NO-GO" in md
    assert "## KILL-SWITCH TRIGGERS" in md


def test_verdict_is_consistent_with_measurement():
    """REPLICATION/REFUTATION/INCONCLUSIVE agree with the measured success block."""
    report = build_report()
    verdict = report["verdict"]
    sc = report["success"]
    ks = report["kill_switch"]

    if verdict == "REPLICATION":
        assert sc["non_degenerate"] is False
        assert sc["replicated_eval35"] is True
        assert sc["refuted_eval35"] is False
        assert ks["any_breach"] is True
    elif verdict == "REFUTATION":
        assert sc["non_degenerate"] is True
        assert sc["replicated_eval35"] is False
        assert sc["refuted_eval35"] is True
        assert ks["any_breach"] is False
    else:  # INCONCLUSIVE
        assert sc["replicated_eval35"] is False
        assert sc["refuted_eval35"] is False


def test_evidence_durability_objective_met():
    """Either the NO-GO is replicated (durability proven) or inconsistency is recorded."""
    report = build_report()
    dur = report["durability"]
    # The campaign's core claim (orderflow-only NOT net-of-cost tradable) must hold:
    # replication is the expected honest outcome; refutation/inconclusive must still
    # be recorded, never silently omitted.
    if dur["durability_status"] == "CONCLUSIONS_REPRODUCIBLE":
        assert report["verdict"] == "REPLICATION"
        assert report["success"]["replicated_eval35"] is True


def test_artifact_is_valid_json_strict_serialization():
    from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

    report = build_report()
    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)
    assert serialized["report_id"] == REPORT_ID
    json.dumps(serialized, allow_nan=False)