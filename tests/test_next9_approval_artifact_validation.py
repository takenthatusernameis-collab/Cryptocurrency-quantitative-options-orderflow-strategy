from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import validate_next9_approval_artifact as v  # noqa: E402


def test_current_repo_blocks_next9():
    r = v.check_current(REPO)
    assert r["next9_unblocked"] is False
    assert r["paper_only"] is True
    assert r["live_trading_enabled"] is False
    assert any("A1" in i or "missing" in i or "not_explicitly_approved" in i for i in r["issues"])


def test_rejects_live_enabling_artifact():
    ok, issues = v.validate_approval_artifact({"live_trading_enabled": True, "human_approval_checklist": []})
    assert ok is False
    assert "artifact_must_not_enable_live_trading" in issues


def test_full_approvals_require_fields():
    checklist = []
    for i in range(1, 8):
        aid = f"A{i}"
        item = {"id": aid, "approved": True, "approver_identity": "x", "timestamp_utc": "2026-01-01T00:00:00Z"}
        for canonical, _mandatory in v.REQUIRED_FIELDS[aid]:
            if canonical == "approved":
                continue
            if canonical not in item:
                item[canonical] = "ok" if canonical != "limits" else {"max_notional": 1}
        checklist.append(item)
    ok, issues = v.validate_approval_artifact({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": checklist})
    assert ok is True
    assert issues == []


def test_partial_approval_blocked():
    checklist = [{"id": "A1", "approved": True, "approver_identity": "x", "timestamp_utc": "t", "scope": "s"}]
    ok, issues = v.validate_approval_artifact({"human_approval_checklist": checklist})
    assert ok is False
    assert "missing_A2" in issues


def test_bare_approved_true_is_false_green():
    # Regression: `approved: true` alone must NOT unblock NEXT9.
    checklist = [
        {"id": f"A{i}", "approved": True}
        for i in range(1, 8)
    ]
    ok, issues = v.validate_approval_artifact({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": checklist})
    assert ok is False
    assert any("A1_missing_approver_identity" in i for i in issues)
    assert any("A1_missing_scope" in i for i in issues)


def test_next8_proposal_schema_aliases_validate():
    # The review-only proposal uses `approver` + descriptive `item` fields.
    # These must map onto the canonical invariant set, not be structurally vetoed.
    prop = json.loads((REPO / "research_state/LIVE_ENABLEMENT_PROPOSAL_20261107T014236Z.json").read_text(encoding="utf-8"))
    ok, issues = v.validate_approval_artifact(prop)
    assert ok is False
    # Blocked because approvals are false, not because of schema mismatch.
    assert "artifact_must_not_enable_live_trading" not in issues
    assert "missing_human_approval_checklist" not in issues
    assert any("A1_not_explicitly_approved" in i for i in issues)


def test_next8_proposal_with_real_approvals_unblocks():
    prop = json.loads((REPO / "research_state/LIVE_ENABLEMENT_PROPOSAL_20261107T014236Z.json").read_text(encoding="utf-8"))
    for item in prop["human_approval_checklist"]:
        item["approved"] = True
        item["approver"] = "human-approver"
        item["timestamp_utc"] = "2026-01-01T00:00:00Z"
    ok, issues = v.validate_approval_artifact(prop)
    assert ok is True, issues


def test_check_current_uses_proposal_schema():
    r = v.check_current(REPO)
    assert r["next9_unblocked"] is False
    assert r["paper_only"] is True
    assert r["live_trading_enabled"] is False
    # The review-only proposal must be recognized as a valid checklist container.
    assert "missing_human_approval_checklist" not in r["issues"]
    assert "missing_proposal_json" not in r["issues"]


def test_conflicting_unblock_claim_rejected():
    # A checkpoint that claims unblock while approvals are absent must not pass.
    cp = {
        "live_enablement_decision": "APPROVED",
        "paper_only": True,
        "live_trading_enabled": False,
        "artifacts": {"proposal_json": "research_state/LIVE_ENABLEMENT_PROPOSAL_20261107T014236Z.json"},
    }
    ok, issues = v.validate_approval_artifact(cp)
    assert ok is False