"""Tests for EVAL-36 final termination memo (paper-only)."""

import json
from pathlib import Path

from scripts.eval36_final_termination_memo import (
    EVAL34_REPORT_ID,
    EVAL35_REPORT_ID,
    REPORT_ID,
    _find_artifact,
    build_consolidated_evidence_table,
    build_final_decision,
    build_md,
    build_report,
    load_eval34,
    load_eval35,
)

EVAL34_PATH = Path("research_state/FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.json")
EVAL35_PATH = Path("research_state/ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z.json")


def test_sealed_inputs_exist_and_validate():
    """EVAL-36 consumes the sealed EVAL-34 and EVAL-35 artifacts, not synthetic data."""
    assert EVAL34_PATH.exists(), f"missing sealed EVAL-34 artifact: {EVAL34_PATH}"
    assert EVAL35_PATH.exists(), f"missing sealed EVAL-35 artifact: {EVAL35_PATH}"

    p34, d34 = load_eval34()
    p35, d35 = load_eval35()

    assert p34.name.startswith(EVAL34_REPORT_ID)
    assert p35.name.startswith(EVAL35_REPORT_ID)
    assert d34["verdict"] == "NO-GO"
    assert d35["verdict"] == "NO-GO"
    assert d34["final_falsification_statement"]["combined_strategy_net_of_cost_tradable"] is False
    assert d35["portfolio_certification"]["decision"] == "TERMINATE_NO_GO"


def test_eval35_measured_numbers_match_sealed_artifact():
    """The memo records the exact EVAL-35 measured failure, not a paraphrase."""
    _, d35 = load_eval35()
    wf = d35["walkforward"]
    pc = d35["portfolio_certification"]
    ks = d35["kill_switch"]

    assert abs(float(wf["oos_sharpe"]) - (-18.17767893333353)) < 1e-12
    assert int(wf["num_trades"]) == 1255
    assert abs(float(wf["total_cost_usd"]) - 184.9265410980795) < 1e-9
    assert abs(float(wf["oos_max_drawdown"]) - 0.9662457344138068) < 1e-12
    assert ks["triggers"] == ["max_drawdown", "cost_bps", "toxicity"]
    assert pc["non_degenerate"] is False
    assert pc["within_eval34_band"] is False
    assert pc["kill_switch_breach"] is True


def test_consolidated_table_covers_eval23_to_eval35():
    """The evidence table has one row per eval and preserves measured numbers."""
    table = build_consolidated_evidence_table()
    assert [row["eval"] for row in table] == [
        "EVAL-23", "EVAL-24", "EVAL-27", "EVAL-28", "EVAL-29",
        "EVAL-30", "EVAL-31", "EVAL-32", "EVAL-33", "EVAL-34", "EVAL-35",
    ]
    assert len(table) == 11

    by_eval = {row["eval"]: row for row in table}
    assert by_eval["EVAL-34"]["verdict"] == "NO-GO"
    assert abs(by_eval["EVAL-34"]["combined_sharpe"] - 5.019467339381368) < 1e-12
    assert by_eval["EVAL-34"]["orderflow_only_trades"] == 129

    e35 = by_eval["EVAL-35"]
    assert e35["verdict"] == "NO-GO"
    assert abs(e35["orderflow_only_sharpe"] - (-18.17767893333353)) < 1e-12
    assert e35["orderflow_only_trades"] == 1255
    assert abs(e35["orderflow_only_cost_usd"] - 184.9265410980795) < 1e-9
    assert "kill-switch" in e35["key_reason"]
    assert "within_band=False" in e35["key_reason"]


def test_final_decision_is_terminate_no_go_with_preconditions():
    """The decision is TERMINATE_NO_GO only when the sealed EVAL-35 failure is present."""
    table = build_consolidated_evidence_table()
    decision = build_final_decision(table)

    assert decision["decision"] == "TERMINATE_NO_GO"
    assert decision["verdict"] == "NO-GO"
    assert decision["campaign_status"] == "TERMINATED"
    assert decision["paper_rollout_certified"] is False
    assert decision["live_trading_enabled"] is False
    assert decision["options_leg_zero_alpha_confirmed"] is True
    assert decision["orderflow_only_replication_failed"] is True
    assert decision["orderflow_only_certified"] is False
    assert decision["pre_declared_options"] == ["TERMINATE_NO_GO"]
    assert decision["eval35_second_window"]["non_degenerate"] is False
    assert decision["eval35_second_window"]["within_eval34_band"] is False


def test_report_structure_serialization_and_no_synthetic_fallback():
    """The report is strict-serializable and records paper-only/no-synthetic invariants."""
    report = build_report()

    assert report["report_id"] == REPORT_ID
    assert report["verdict"] == "NO-GO"
    assert report["trading_mode"] == "paper"
    assert report["live_trading_enabled"] is False
    assert report["authenticity_verified"] is False
    assert report["data_provenance"] == "real_public_exchange_export"
    assert report["never_valid_true"] is True
    assert report["final_decision"]["decision"] == "TERMINATE_NO_GO"
    assert len(report["consolidated_evidence_table"]) == 11
    assert len(report["lessons_learned"]) >= 5
    assert report["infrastructure_disposition"]["live_trading_enabled"] is False
    assert report["infrastructure_disposition"]["env_file_present"] is False
    assert report["infrastructure_disposition"]["paper_rollout"] is False
    assert report["infrastructure_disposition"]["never_valid_true"] is True
    assert len(report["commands"]) == 3

    json.dumps(report, allow_nan=False)


def test_md_contains_required_sections_and_evidence():
    """The markdown memo is renderable and carries the final decision and key evidence."""
    report = build_report()
    md = build_md(report)

    assert REPORT_ID in md
    assert "TERMINATE_NO_GO" in md
    assert "EVAL-23" in md
    assert "EVAL-34" in md
    assert "EVAL-35" in md
    assert "-18.1777" in md
    assert "## Final Decision" in md
    assert "## Consolidated Evidence" in md
    assert "## EVAL-35 Independent Replication Result" in md
    assert "## Lessons Learned" in md
    assert "## Infrastructure Disposition" in md
    assert "## Commands" in md


def test_find_artifact_returns_none_when_missing():
    """The artifact lookup helper is safe for missing report IDs."""
    assert _find_artifact("DOES_NOT_EXIST_FINAL_TERMINATION_PREFIX") is None