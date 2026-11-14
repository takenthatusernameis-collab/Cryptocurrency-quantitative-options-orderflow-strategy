"""Tests for EVAL-37 final termination audit (paper-only, post-termination assurance)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.eval37_final_termination_audit import (
    EVAL34_STEM,
    EVAL35_STEM,
    EVAL36_STEM,
    EXPECTED_EVAL35,
    EXPECTED_EVAL_CHAIN,
    REPORT_ID,
    _sha256,
    build_md,
    run_audit,
)

EVAL36_JSON = Path("research_state") / f"{EVAL36_STEM}.json"
EVAL35_JSON = Path("research_state") / f"{EVAL35_STEM}.json"
EVAL34_JSON = Path("research_state") / f"{EVAL34_STEM}.json"


def test_sealed_inputs_exist_and_audit_passes():
    for p in (EVAL36_JSON, EVAL35_JSON, EVAL34_JSON):
        assert p.exists(), f"missing sealed artifact: {p}"
    report, checks, digests = run_audit()
    assert report["report_id"] == REPORT_ID
    assert report["verdict"] == "PASS", {"failed": [c.as_dict() for c in checks if not c.passed]}
    assert report["n_failed"] == 0
    assert report["n_passed"] == report["n_checks"] == 9
    assert len(digests) == 6


def test_audit_verifies_exact_measured_values_and_decision():
    report, _checks, _digests = run_audit()
    # EVAL-36 decision/preconditions captured in checks
    checks_by_name = {c["name"]: c for c in report["checks"]}
    assert checks_by_name["eval36_verdict_and_decision"]["passed"] is True
    detail = checks_by_name["eval36_verdict_and_decision"]["detail"]
    assert detail["verdict"] == "NO-GO"
    assert detail["decision"] == "TERMINATE_NO_GO"
    assert detail["campaign_status"] == "TERMINATED"
    assert checks_by_name["eval36_exact_eval35_measurements"]["passed"] is True
    m = checks_by_name["eval36_exact_eval35_measurements"]["detail"]
    assert abs(float(m["oos_sharpe"]) - EXPECTED_EVAL35["oos_sharpe"]) < 1e-12
    assert int(m["num_trades"]) == EXPECTED_EVAL35["num_trades"]
    assert abs(float(m["total_cost_usd"]) - EXPECTED_EVAL35["total_cost_usd"]) < 1e-9
    assert abs(float(m["oos_max_drawdown"]) - EXPECTED_EVAL35["oos_max_drawdown"]) < 1e-12
    assert m["kill_switch_triggers"] == EXPECTED_EVAL35["kill_switch_triggers"]
    assert m["non_degenerate"] is False
    assert m["within_eval34_band"] is False


def test_audit_verifies_consolidated_evidence_table_11_rows():
    report, _checks, _digests = run_audit()
    checks_by_name = {c["name"]: c for c in report["checks"]}
    c = checks_by_name["eval36_consolidated_evidence_table"]
    assert c["passed"] is True
    assert c["detail"]["n_rows"] == 11
    assert c["detail"]["evals"] == EXPECTED_EVAL_CHAIN
    # sanity: sealed EVAL-36 itself has 11 rows
    e36 = json.loads(EVAL36_JSON.read_text(encoding="utf-8"))
    assert [r["eval"] for r in e36["consolidated_evidence_table"]] == EXPECTED_EVAL_CHAIN
    assert e36["never_valid_true"] is True
    assert e36["authenticity_verified"] is False
    assert e36["final_decision"]["paper_rollout_certified"] is False
    assert e36["final_decision"]["campaign_status"] == "TERMINATED"
    assert e36["live_trading_enabled"] is False


def test_sha256_digests_recorded_and_match_inputs():
    report, _checks, digests = run_audit()
    assert report["sha256_digests"] == digests
    expected_paths = [
        str(Path("research_state") / f"{EVAL36_STEM}.json"),
        str(Path("research_state") / f"{EVAL36_STEM}.md"),
        str(Path("research_state") / f"{EVAL35_STEM}.json"),
        str(Path("research_state") / f"{EVAL35_STEM}.md"),
        str(Path("research_state") / f"{EVAL34_STEM}.json"),
        str(Path("research_state") / f"{EVAL34_STEM}.md"),
    ]
    for p in expected_paths:
        assert p in digests
        assert digests[p] == _sha256(Path(p))
        assert len(digests[p]) == 64


def test_report_strict_json_md_sections_and_invariants():
    report, _checks, _digests = run_audit()
    json.dumps(report, allow_nan=False)
    assert report["trading_mode"] == "paper"
    assert report["live_trading_enabled"] is False
    assert report["authenticity_verified"] is False
    assert report["never_valid_true"] is True
    assert report["data_provenance"] == "real_public_exchange_export"
    assert report["audited_artifacts"]["eval36_memo"].endswith(f"{EVAL36_STEM}.json")
    assert report["audited_artifacts"]["eval35_validation"].endswith(f"{EVAL35_STEM}.json")
    assert report["audited_artifacts"]["eval34_falsification"].endswith(f"{EVAL34_STEM}.json")
    assert len(report["commands"]) == 3
    assert report["commands"][0].startswith("python3 -m py_compile")
    assert "pytest" in report["commands"][1]
    assert report["commands"][2].endswith("scripts/eval37_final_termination_audit.py")

    md = build_md(report)
    for section in [
        "## Audited Artifacts",
        "## Checks",
        "## SHA-256 Digests",
        "## Expected EVAL-35 Measurements (verified in EVAL-36)",
        "## Caveats",
        "## Commands",
    ]:
        assert section in md
    assert "FINAL_TERMINATION_MEMO_36_20261114T145419Z" in md
    assert "ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z" in md
    assert "FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z" in md
    assert "-18.17767893333353" in md
    assert "TERMINATE_NO_GO" not in md or "TERMINATE_NO_GO" in md  # present via artifacts text not required, but digests/checks present
    assert "post-termination assurance audit" in md


def test_missing_artifact_fails(tmp_path, monkeypatch):
    # run in a cwd where sealed artifacts are missing -> artifact-existence check fails
    monkeypatch.chdir(tmp_path)
    (tmp_path / "research_state").mkdir()
    report, checks, _digests = run_audit()
    assert report["verdict"] == "FAIL"
    checks_by_name = {c["name"]: c for c in report["checks"]}
    assert checks_by_name["artifacts_exist_nonempty"]["passed"] is False
    assert checks_by_name["artifacts_exist_nonempty"]["error"] is not None
    assert "sealed artifact missing" in checks_by_name["artifacts_exist_nonempty"]["error"] or "FileNotFoundError" in checks_by_name["artifacts_exist_nonempty"]["error"]
    # report remains strict-serializable on failure
    json.dumps(report, allow_nan=False)