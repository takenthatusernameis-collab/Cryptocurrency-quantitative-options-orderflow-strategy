"""Targeted tests for R3-R7 reduction-evidence validator (paper-only, advisory)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import validate_r3_r7_reduction_evidence as v  # noqa: E402


def _base(kind: str) -> dict:
    return {
        "artifact_type": v.ARTIFACT_TYPES[kind],
        "timestamp_utc": "2026-11-07T07:20:00Z",
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
    }


def _r3():
    d = _base("R3")
    d.update({
        "venues": ["deribit", "okx", "binance"],
        "symbols": ["BTC", "ETH"],
        "rehearsal_scope": "deterministic venue/ops checklist; no external mutation",
        "checklist": [{"id": "R3.1", "item": "adapter init", "status": "verified_paper"}],
        "evidence_refs": ["research_state/CROSSVENUE_ORCHESTRATION_REPORT.json"],
        "no_external_venue_mutation": True,
    })
    return d


def _r4():
    d = _base("R4")
    d.update({
        "checklist": [{"control": "paper_live_separation", "confirmed": True, "attestation": "no live keys in repo"}],
        "secrets_committed": False,
        "attestation_only": True,
    })
    return d


def _r5():
    d = _base("R5")
    d.update({
        "simulation_scope": "paper campaign/backtest-derived execution quality",
        "evidence_refs": ["research_state/PAPER_TRADING_CAMPAIGN_20261107T023814Z.json"],
        "metrics": {"slippage_assumption_documented": True, "fill_quality_documented": True, "reconciliation_match_rate": 1.0},
        "paper_or_backtest_derived": True,
    })
    return d


def _r6():
    d = _base("R6")
    d.update({
        "thresholds": {"pnl_drift": 0.05, "greeks_drift": 0.08, "fills_drift": 0.1},
        "flags": {"within_bounds": True, "anomaly_count": 0},
        "evidence_refs": ["research_state/PHASE20_DRIFT_DETECTION_REPORT.json"],
        "deterministic": True,
    })
    return d


def _r7():
    d = _base("R7")
    d.update({
        "process_checklist": [{"id": f"A{i}", "process_item": f"A{i}", "approved": False} for i in range(1, 8)],
        "cannot_grant_approval": True,
        "next9_validator_ref": "scripts/validate_next9_approval_artifact.py",
    })
    return d


def test_r3_valid():
    ok, issues = v.validate_artifact(_r3(), "R3")
    assert ok is True, issues


def test_r4_valid_no_secrets():
    ok, issues = v.validate_artifact(_r4(), "R4")
    assert ok is True, issues


def test_r4_rejects_secret_like_value():
    d = _r4()
    d["checklist"][0]["api_key"] = "sk-live-supersecretvalue123456"
    ok, issues = v.validate_artifact(d, "R4")
    assert ok is False
    assert any("secret" in i.lower() for i in issues)


def test_r4_rejects_secrets_committed():
    d = _r4()
    d["secrets_committed"] = True
    ok, issues = v.validate_artifact(d, "R4")
    assert ok is False
    assert "R4_secrets_committed_must_be_false" in issues


def test_r5_valid():
    ok, issues = v.validate_artifact(_r5(), "R5")
    assert ok is True, issues


def test_r6_valid():
    ok, issues = v.validate_artifact(_r6(), "R6")
    assert ok is True, issues


def test_r7_valid_but_cannot_grant_approval():
    ok, issues = v.validate_artifact(_r7(), "R7")
    assert ok is True, issues
    assert _r7()["cannot_grant_approval"] is True
    assert _r7()["next9_unblocked"] is False


def test_r7_rejects_approval_granting_claim():
    d = _r7()
    d["cannot_grant_approval"] = False
    ok, issues = v.validate_artifact(d, "R7")
    assert ok is False
    assert "R7_cannot_grant_approval_must_be_true" in issues


def test_common_guard_rejects_live_enabling():
    d = _r5()
    d["live_trading_enabled"] = True
    ok, issues = v.validate_artifact(d, "R5")
    assert ok is False
    assert "R5_must_not_enable_live_trading" in issues


def test_common_guard_rejects_next9_unblock():
    d = _r6()
    d["next9_unblocked"] = True
    ok, issues = v.validate_artifact(d, "R6")
    assert ok is False
    assert "R6_must_not_unblock_next9" in issues


def test_check_repo_reports_missing_without_strict_block_default():
    # --check-repo on a tmp-style call via main is fine; artifacts may or may not exist.
    # Default (no --strict) must exit 0 even when missing.
    rc = v.main(["--check-repo"])
    assert rc == 0


def test_check_repo_strict_requires_all_present():
    rc = v.main(["--check-repo", "--strict"])
    # May be 0 or 1 depending on repo state; contract is deterministic given state.
    result = v.check_repo(REPO)
    assert rc == (0 if result["all_present_and_valid"] else 1)


def test_artifact_not_found_strict():
    rc = v.main(["--artifact", "research_state/NOPE_R3.json", "--kind", "R3", "--strict"])
    assert rc == 1


def test_r5_stricter_fields_present():
    # ensure stricter generator produces required fields
    from generate_r5_execution_slippage_evidence import gen_r5_strict
    d = gen_r5_strict("20261107T072823Z")
    ok, issues = v.validate_artifact(d, "R5")
    assert ok is True, issues
    m = d["metrics"]
    for k in ("filled_orders", "rejected_orders", "partial_fill_rate", "reject_rate", "within_conservative_caps", "slippage_bps_conservative_cap"):
        assert k in m
    assert d["paper_or_backtest_derived"] is True
    assert d["next9_unblocked"] is False
    assert d["live_trading_enabled"] is False
