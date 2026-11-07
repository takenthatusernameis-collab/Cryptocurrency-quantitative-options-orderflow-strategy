from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import check_paper_ops_readiness as por  # noqa: E402


def test_live_guardrails_pass_in_repo_state():
    r = por.check_live_guardrails(REPO)
    assert r["live_trading_default_false"] is True
    assert r["env_example_live_trading_false"] is True
    assert r["tracked_worktree_clean_of_live_enabling_changes"] is True
    assert r["passed"] is True


def test_cv_checkpoint_green_when_present():
    r = por.check_cv(REPO, max_age_hours=24.0)
    if not r.get("exists"):
        return
    assert r["passed"] is True
    assert r["paper_only"] is True
    assert r["live_trading_enabled"] is False
    assert r["gates"]["reconciliation_freshness_met"] is True


def test_paper_campaign_r1_summary():
    r = por.check_paper_campaign(REPO)
    if not r.get("exists"):
        return
    assert r["passed"] is True
    assert r["summary"]["all_critical_passed"] is True
    assert r["summary"]["failed"] == 0


def test_next9_blocked_invariant():
    r = por.check_next8(REPO)
    if not r.get("exists"):
        return
    assert r["a1_a7_all_approved"] is False
    assert r["next9_unblocked"] is False
    assert r["passed_block_invariant"] is True


def test_build_snapshot_shape_and_safety():
    s = por.build_snapshot(REPO, max_cv_age_hours=24.0)
    assert s["paper_only"] is True
    assert s["live_trading_enabled"] is False
    assert s["gates"]["no_live_capital"] is True
    assert s["gates"]["next9_blocked_until_explicit_human_approval_recorded"] is True
    assert "guardrails" in s and "cv" in s and "paper_campaign" in s
    # Snapshot must never claim NEXT9 unblocked without approvals.
    assert s["next8_live_enablement"]["next9_unblocked"] is False
