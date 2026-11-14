"""Tests for EVAL-34 final consolidated strategy falsification + portfolio decision."""

import json
import math
import os

import pytest

from scripts.eval34_final_strategy_falsification import (
    REPORT_ID,
    build_consolidated_evidence_table,
    build_final_falsification_statement,
    build_md,
    build_report,
    make_portfolio_decision,
    _find_artifact,
    _load_json,
    _num,
    _safe_get,
)


def _artifact_exists(report_id_prefix: str) -> bool:
    from pathlib import Path
    return any(Path("research_state").glob(f"{report_id_prefix}_*.json"))


def test_consolidated_table_loads_all_sealed_artifacts():
    """The consolidated evidence table loads all sealed artifacts EVAL-23..33."""
    table = build_consolidated_evidence_table()
    evals = [row["eval"] for row in table]
    assert evals == ["EVAL-23", "EVAL-24", "EVAL-27", "EVAL-28", "EVAL-29", "EVAL-30", "EVAL-31", "EVAL-32", "EVAL-33"]
    for row in table:
        assert row["report_id"] is not None
        assert row["generated_at"] is not None
        assert row["verdict"] in ("GO", "NO-GO")
        assert row["key_reason"] is not None and len(row["key_reason"]) > 0


def test_consolidated_table_extracts_correct_measured_numbers():
    """Key measured numbers match the sealed artifacts exactly."""
    table = build_consolidated_evidence_table()
    by_eval = {row["eval"]: row for row in table}

    # EVAL-23: combined IC mean -0.0168 adverse, options degenerate
    e23 = by_eval["EVAL-23"]
    assert e23["verdict"] == "NO-GO"
    assert abs(e23["combined_ic_mean"] - (-0.016776209431115855)) < 1e-12
    assert abs(e23["combined_ic_tstat"] - (-4.100752115549735)) < 1e-6
    assert e23["options_leg_degenerate"] is True
    assert e23["permutation_p_value"] is not None and e23["permutation_p_value"] < 0.01

    # EVAL-24: NO-GO, options leg not tradable
    e24 = by_eval["EVAL-24"]
    assert e24["verdict"] == "NO-GO"
    assert "coverage 0%" in e24["key_reason"] or "0%" in e24["key_reason"]

    # EVAL-28: GO (additive parity), 1017/1017 pairs, min R^2=0.999919
    e28 = by_eval["EVAL-28"]
    assert e28["verdict"] == "GO"
    assert "1017/1017" in e28["key_reason"] or "100%" in e28["key_reason"]

    # EVAL-30: NO-GO, measurement ic_mean -0.002957; net_of_cost combined_alpha ic_mean -0.032686
    e30 = by_eval["EVAL-30"]
    assert e30["verdict"] == "NO-GO"
    assert abs(e30["measurement_ic_mean"] - (-0.0029570304267226336)) < 1e-12
    assert abs(e30["combined_ic_mean"] - (-0.032685903772096424)) < 1e-6

    # EVAL-31: GO marginal, combined Sharpe 0.3016
    e31 = by_eval["EVAL-31"]
    assert e31["verdict"] == "GO"
    assert abs(e31["combined_sharpe"] - 0.30156596306364075) < 1e-6
    assert e31["options_only_trades"] == 0

    # EVAL-32: NO-GO validation, combined Sharpe 5.0195 vs orderflow-only 4.8115
    e32 = by_eval["EVAL-32"]
    assert e32["verdict"] == "NO-GO"
    assert abs(e32["combined_sharpe"] - 5.019467339381368) < 1e-6
    assert abs(e32["orderflow_only_sharpe"] - 4.811462185754629) < 1e-6
    assert abs(e32["orderflow_only_trades"] - 129) < 1e-6
    assert abs(e32["orderflow_only_cost_usd"] - 157.0180100586245) < 1e-6
    assert e32["permutation_p_value"] is not None and e32["permutation_p_value"] > 0.05

    # EVAL-33: NO-GO falsification, all options-only variants flat
    e33 = by_eval["EVAL-33"]
    assert e33["verdict"] == "NO-GO"
    assert e33["options_only_sharpe"] == 0.0
    assert e33["options_only_trades"] == 0
    assert e33["options_only_cost_usd"] == 0.0
    assert abs(e33["orderflow_only_sharpe"] - 4.811462185754629) < 1e-6
    assert e33["orderflow_only_trades"] == 129


def test_final_statement_references_every_sealed_no_go():
    """The final falsification statement references every sealed NO-GO from EVAL-23..33."""
    table = build_consolidated_evidence_table()
    statement = build_final_falsification_statement(table)
    stmt = statement["statement"]

    # Every NO-GO eval must be mentioned by number
    for ev in ("23", "24", "27", "29", "30", "32", "33"):
        assert f"EVAL-{ev}" in stmt, f"Statement must reference EVAL-{ev}"

    # EVAL-28 (GO additive) and EVAL-31 (GO marginal, invalidated by EVAL-32)
    assert "EVAL-28" in stmt
    assert "EVAL-31" in stmt

    # Explicit tradability statements
    assert statement["combined_strategy_net_of_cost_tradable"] is False
    assert statement["options_leg_carries_positive_net_of_cost_alpha"] is False
    assert statement["orderflow_only_is_only_non_degenerate_pillar"] is True

    # Measured orderflow-only numbers
    assert abs(statement["orderflow_only_held_out_sharpe"] - 4.811462185754629) < 1e-6
    assert statement["orderflow_only_held_out_trades"] == 129
    assert abs(statement["orderflow_only_held_out_cost_usd"] - 157.0180100586245) < 1e-6


def test_portfolio_decision_is_pre_declared_option_with_measured_justification():
    """The portfolio decision is one of the two pre-declared options with measured justification."""
    table = build_consolidated_evidence_table()
    statement = build_final_falsification_statement(table)
    decision = make_portfolio_decision(statement, table)

    assert decision["decision"] in ("DEPLOY_ORDERFLOW_ONLY_WITH_CAVEATS", "TERMINATE")
    assert len(decision["rationale"]) > 0
    assert len(decision["caveats"]) > 0
    assert decision["options_leg_zero_alpha_confirmed"] is True
    assert decision["options_leg_terminated"] is True

    # Measured justification present
    assert abs(decision["orderflow_only_held_out_sharpe"] - 4.811462185754629) < 1e-6
    assert decision["orderflow_only_held_out_trades"] == 129

    # Risk parameters pre-declared
    assert decision["max_notional_usd"] == 1_000_000.0
    assert decision["max_daily_loss_usd"] == 50_000.0
    assert decision["max_drawdown_pct"] == 0.20
    assert decision["toxicity_kill_switch_pct"] == 0.80
    assert decision["cost_kill_switch_bps"] == 5.0


def test_artifact_is_valid_json_and_md_with_strict_serialization():
    """The sealed artifact is valid JSON/MD with strict serialization."""
    report = build_report()
    assert report["report_id"] == REPORT_ID
    assert report["verdict"] in ("GO", "NO-GO")
    assert report["verdict_reason"] is not None
    assert report["trading_mode"] == "paper"
    assert report["live_trading_enabled"] is False
    assert report["authenticity_verified"] is False
    assert report["data_provenance"] == "real_public_exchange_export"

    # Consolidated table present with all evals
    assert len(report["consolidated_evidence_table"]) == 9
    assert len(report["final_falsification_statement"]["statement"]) > 0
    assert report["final_falsification_statement"]["combined_strategy_net_of_cost_tradable"] is False

    # Portfolio decision present and pre-declared
    assert report["portfolio_decision"]["decision"] in ("DEPLOY_ORDERFLOW_ONLY_WITH_CAVEATS", "TERMINATE")

    # MD renderable
    md = build_md(report)
    assert REPORT_ID in md
    assert "EVAL-23" in md
    assert "EVAL-33" in md
    assert "DEPLOY_ORDERFLOW_ONLY_WITH_CAVEATS" in md or "TERMINATE" in md
    assert "## Final Falsification Statement" in md
    assert "## Portfolio Decision" in md

    # Commands present
    assert len(report["commands"]) == 3
    assert "python3 -m py_compile" in report["commands"][0]
    assert "python3 -m pytest" in report["commands"][1]
    assert "python3 scripts/eval34_final_strategy_falsification.py" in report["commands"][2]


def test_num_and_safe_get_helpers():
    """Helper functions handle missing/None values gracefully."""
    assert _num(None) == 0.0
    assert _num(float("nan")) == 0.0
    assert _num(float("inf")) == 0.0
    assert _num(3.14) == 3.14
    assert _num(42) == 42.0

    d = {"a": {"b": 5}}
    assert _safe_get(d, "a", "b") == 5
    assert _safe_get(d, "a", "c", default="x") == "x"
    assert _safe_get(d, "missing", default="x") == "x"
    assert _safe_get({}, "a", default="x") == "x"


def test_find_artifact_returns_none_when_missing():
    """_find_artifact returns None when no artifact matches."""
    result = _find_artifact("DOES_NOT_EXIST_PREFIX")
    assert result is None


def test_run_report_consistent():
    """build_report returns a consistent, fully-populated report."""
    report = build_report()
    assert report["eval_chain"] == ["EVAL-23", "EVAL-24", "EVAL-27", "EVAL-28", "EVAL-29", "EVAL-30", "EVAL-31", "EVAL-32", "EVAL-33"]
    for row in report["consolidated_evidence_table"]:
        assert row["eval"] in report["eval_chain"]

    # No-GO evals are NO-GO
    no_go = {r["eval"] for r in report["consolidated_evidence_table"] if r["verdict"] == "NO-GO"}
    assert no_go == {"EVAL-23", "EVAL-24", "EVAL-27", "EVAL-29", "EVAL-30", "EVAL-32", "EVAL-33"}
    go = {r["eval"] for r in report["consolidated_evidence_table"] if r["verdict"] == "GO"}
    assert go == {"EVAL-28", "EVAL-31"}
