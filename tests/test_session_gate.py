"""Deterministic session gate tests (targeted, paper-only).

Covers the session gate invariant: a session cannot proceed unless P0 readiness
is green, CV is fresh, NEXT9 stays blocked (A1-A7 unapproved), and no live
capital is enabled. Emits a single additive artifact per run.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
sys.path.insert(0, str(REPO / "scripts"))

import run_session_gate as g  # noqa: E402
import check_paper_ops_readiness as c  # noqa: E402
import validate_next9_approval_artifact as v  # noqa: E402


def _green_snapshot():
    return {
        "gates": {
            "paper_ops_ready": True,
            "cv_fresh_for_material_decisions": True,
            "next9_blocked_until_explicit_human_approval_recorded": True,
            "no_live_capital": True,
        },
        "action_required": [],
    }


def test_session_gate_green_on_current_repo():
    result = g.run_gate(REPO)
    assert result["paper_only"] is True
    assert result["live_trading_enabled"] is False
    assert result["gate_passed"] is True
    assert result["block_agreement"] is True
    gt = result["gates"]
    assert gt["paper_ops_ready"] is True
    assert gt["cv_fresh_for_material_decisions"] is True
    assert gt["next9_blocked_until_explicit_human_approval_recorded"] is True
    assert gt["no_live_capital"] is True
    assert gt["next9_not_unblocked"] is True
    assert result["next9"]["next9_unblocked"] is False
    assert result["next9"]["checkpoint_decision"] == "NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL"


def test_session_gate_artifact_type():
    result = g.run_gate(REPO)
    assert result["artifact_type"] == "PAPER_OPS_SESSION_GATE"
    # run_gate() itself does not write; readiness path is absent until main() writes.
    ap = result["readiness"]["artifact_path"]
    assert ap is None or ap.startswith("research_state/PAPER_OPS_READINESS_SNAPSHOT_")


def test_session_gate_blocks_when_readiness_not_ready(monkeypatch):
    snap = _green_snapshot()
    snap["gates"]["paper_ops_ready"] = False
    snap["gates"]["cv_fresh_for_material_decisions"] = False
    snap["gates"]["no_live_capital"] = False
    monkeypatch.setattr(c, "build_snapshot", lambda repo, max_cv_age_hours=2.0: snap)
    result = g.run_gate(REPO)
    assert result["gate_passed"] is False
    assert result["gates"]["paper_ops_ready"] is False


def test_session_gate_blocks_when_next9_unblocked(monkeypatch):
    def fake_check_current(repo=REPO):
        return {
            "next9_unblocked": True,
            "checkpoint_decision": "APPROVED",
            "issues": [],
            "paper_only": True,
            "live_trading_enabled": False,
        }

    monkeypatch.setattr(v, "check_current", fake_check_current)
    result = g.run_gate(REPO)
    assert result["gate_passed"] is False
    assert result["gates"]["next9_not_unblocked"] is False
    assert result["block_agreement"] is False


def test_session_gate_strict_exits_nonzero_when_not_green(monkeypatch):
    snap = _green_snapshot()
    snap["gates"]["next9_blocked_until_explicit_human_approval_recorded"] = False
    monkeypatch.setattr(c, "build_snapshot", lambda repo, max_cv_age_hours=2.0: snap)
    code = g.main(["--strict"])
    assert code == 1


def test_session_gate_writes_additive_artifact(tmp_path, monkeypatch):
    monkeypatch.setattr(g, "RS", tmp_path)
    code = g.main([])
    assert code == 0
    written = list(tmp_path.glob("PAPER_OPS_SESSION_GATE_*.json"))
    assert len(written) == 1
    d = json.loads(written[0].read_text(encoding="utf-8"))
    assert d["artifact_type"] == "PAPER_OPS_SESSION_GATE"
    assert d["paper_only"] is True
    assert d["gate_passed"] is True
    assert d["readiness"]["artifact_path"] == str(written[0])
