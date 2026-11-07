"""Paper-ops readiness snapshot tests (targeted, paper-only).

Covers the false-green regression: `approved: true` alone must NOT unblock
NEXT9 — only a full A1-A7 approval record (non-empty approver/scope/limits
fields) does.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_paper_ops_readiness as c  # noqa: E402
import validate_next9_approval_artifact as v  # noqa: E402


def test_snapshot_blocks_next9_on_current_repo():
    snap = c.build_snapshot(REPO)
    assert snap["paper_only"] is True
    assert snap["live_trading_enabled"] is False
    assert snap["gates"]["next9_blocked_until_explicit_human_approval_recorded"] is True
    assert snap["gates"]["no_live_capital"] is True
    assert "record_a1_a7_human_approvals_before_next9" in snap["action_required"]


def _load_proposal_copy():
    prop = json.loads((REPO / "research_state/LIVE_ENABLEMENT_PROPOSAL_20261107T014236Z.json").read_text(encoding="utf-8"))
    return prop


def test_bare_approved_true_does_not_unblock_next8():
    # Regression: a checklist where every item is approved but fields are empty
    # must NOT unblock NEXT9. The shared validator is the single source of truth
    # used by check_next8, so exercise it directly (no on-disk mutation).
    prop = _load_proposal_copy()
    for item in prop["human_approval_checklist"]:
        item["approved"] = True
    ok, issues = v.validate_approval_artifact(prop)
    assert ok is False
    assert any("A1_missing_approver_identity" in i for i in issues)
    # `scope` resolves via the `item` alias to the descriptive text, so it is
    # present; the block comes from the missing approver identity.
    assert not any("A1_missing_scope" in i for i in issues)
    # And check_next8 must agree on the current (unmodified) repo artifact.
    res = c.check_next8(REPO)
    assert res["a1_a7_all_approved"] is False
    assert res["next9_unblocked"] is False
    assert res["passed_block_invariant"] is True


def test_full_approvals_unblock_next8_when_decision_not_no_go():
    prop = _load_proposal_copy()
    for item in prop["human_approval_checklist"]:
        item["approved"] = True
        item["approver"] = "human-approver"
        item["timestamp_utc"] = "2026-01-01T00:00:00Z"
    ok, issues = v.validate_approval_artifact(prop)
    assert ok is True
    assert issues == []


def test_guardrails_detect_tracked_live_enabling_change(tmp_path):
    # Simulate a tracked diff containing a live-enabling file.
    orig = c._git_tracked_diff_names
    c._git_tracked_diff_names = lambda repo: ["src/config/secrets.py"]
    try:
        g = c.check_live_guardrails(REPO)
        assert g["tracked_worktree_clean_of_live_enabling_changes"] is False
        assert g["passed"] is False
        assert "src/config/secrets.py" in g["tracked_live_enabling_changes"]
    finally:
        c._git_tracked_diff_names = orig


def test_cv_checkpoint_shape():
    cv = c.check_cv(REPO, max_age_hours=2.0)
    assert cv["exists"] is True
    assert cv["paper_only"] is True
    assert cv["live_trading_enabled"] is False
    assert cv["gates"]["all_critical_passed"] is True
    assert cv["gates"]["iterations_5_5"] is True
    assert cv["reconciliation_freshness"]["met"] is True
    assert cv["reconciliation_freshness"]["measurements_per_iteration"] == [1, 1, 1, 1, 1]


def test_paper_campaign_summary_r1():
    p = c.check_paper_campaign(REPO)
    assert p["exists"] is True
    assert p["passed"] is True
    assert p["summary"]["all_critical_passed"] is True
    assert p["summary"]["failed"] == 0
    assert p["summary"]["passed"] == p["summary"]["total_gates"]