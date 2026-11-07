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
        for f in v.REQUIRED_FIELDS[aid]:
            if f not in item:
                item[f] = "ok" if f != "limits" else {"max_notional": 1}
        checklist.append(item)
    ok, issues = v.validate_approval_artifact({"paper_only": True, "live_trading_enabled": False, "human_approval_checklist": checklist})
    assert ok is True
    assert issues == []


def test_partial_approval_blocked():
    checklist = [{"id": "A1", "approved": True, "approver_identity": "x", "timestamp_utc": "t", "scope": "s"}]
    ok, issues = v.validate_approval_artifact({"human_approval_checklist": checklist})
    assert ok is False
    assert "missing_A2" in issues
