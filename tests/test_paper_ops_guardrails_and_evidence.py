"""Paper-ops guardrail and evidence invariants (targeted, paper-only)."""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
CP = RS / "campaign_checkpoints"


def test_live_trading_default_false_in_secrets():
    text = (REPO / "src/config/secrets.py").read_text(encoding="utf-8")
    assert 'LIVE_TRADING_ENABLED", "false"' in text or "LIVE_TRADING_ENABLED', 'false'" in text


def test_env_example_keeps_live_trading_false():
    text = (REPO / ".env.example").read_text(encoding="utf-8")
    assert "LIVE_TRADING_ENABLED=false" in text
    assert "LIVE_TRADING_ENABLED=true" not in text


def test_paper_campaign_summary_schema_r1():
    # R1: consume summary.all_critical_passed/failed; top-level fields may be absent.
    p = RS / "PAPER_TRADING_CAMPAIGN_20261107T023814Z.json"
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    s = d.get("summary") or {}
    assert s.get("all_critical_passed") is True
    assert s.get("failed") == 0
    assert s.get("passed") == s.get("total_gates")


def test_cv_checkpoint_gates_and_freshness():
    p = CP / "CONTINUOUS_VALIDATION_AND_MONITORING_latest.json"
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d.get("paper_only") is True
    assert d.get("live_trading_enabled") is False
    g = d.get("gates") or {}
    assert g.get("all_critical_passed") is True
    assert g.get("iterations_5_5") is True
    assert g.get("reconciliation_freshness_gte_0_99_met_with_measurements") is True
    rf = d.get("reconciliation_freshness") or {}
    assert rf.get("met") is True
    assert rf.get("all_iterations_have_measurements") is True
    assert all(m > 0 for m in (rf.get("measurements_per_iteration") or []))


def test_next9_blocked_a1_a7_unapproved():
    p = CP / "LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY_latest.json"
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d.get("live_trading_enabled") is False
    assert d.get("paper_only") is True
    assert d.get("live_enablement_decision") == "NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL"
    prop_path = d.get("artifacts", {}).get("proposal_json")
    if prop_path:
        prop = json.loads((REPO / prop_path).read_text(encoding="utf-8"))
        checklist = prop.get("human_approval_checklist") or []
        if checklist:
            assert all(not item.get("approved") for item in checklist), "A1-A7 must remain unapproved in repo artifacts"


def test_continuity_refresh_checkpoint_shape():
    p = CP / "PAPER_OPERATIONS_CONTINUITY_REFRESH_latest.json"
    if not p.exists():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d.get("paper_only") is True
    assert d.get("live_trading_enabled") is False
    assert d.get("next9_unblocked") is False
    g = d.get("gates") or {}
    assert g.get("a1_a7_all_approved") is False
    assert g.get("next9_blocked_until_explicit_human_approval_recorded") is True
