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
    monkeypatch.setattr(c, "build_snapshot", lambda repo, max_cv_age_hours=2.0, include_r3_r7_evidence=False, require_r3_r7_evidence=False: snap)
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
    monkeypatch.setattr(c, "build_snapshot", lambda repo, max_cv_age_hours=2.0, include_r3_r7_evidence=False, require_r3_r7_evidence=False: snap)
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


def _all_valid_r3_r7_report():
    kinds = {k: {"present": True, "valid": True, "issues": [], "path": f"research_state/{k}_X.json"} for k in ("R3", "R4", "R5", "R6", "R7")}
    return {
        "artifact_type": "R3_R7_REDUCTION_EVIDENCE_REPORT",
        "timestamp_utc": "2026-11-07T00:00:00Z",
        "advisory": False,
        "required": True,
        "mode": "required",
        "available": True,
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "kinds": kinds,
        "all_present_and_valid": True,
        "action_required": [],
    }


def _missing_r3_r7_report():
    kinds = {k: {"present": False, "valid": False, "issues": [f"missing_{k}"], "path": None} for k in ("R3", "R4", "R5", "R6", "R7")}
    return {
        "artifact_type": "R3_R7_REDUCTION_EVIDENCE_REPORT",
        "timestamp_utc": "2026-11-07T00:00:00Z",
        "advisory": False,
        "required": True,
        "mode": "required",
        "available": True,
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "kinds": kinds,
        "all_present_and_valid": False,
        "action_required": ["fix_or_generate_missing_r3_r7_evidence"],
    }


def test_session_gate_default_off_does_not_require_r3_r7(monkeypatch):
    # Default behavior: require flag is off, so a missing R3-R7 set must NOT
    # affect the gate (advisory semantics preserved). Simulate by ensuring the
    # readiness snapshot is the normal green one (no r3_r7 key) — gate stays green.
    monkeypatch.setattr(c, "build_snapshot", lambda repo, max_cv_age_hours=2.0, include_r3_r7_evidence=False, require_r3_r7_evidence=False: _green_snapshot())
    result = g.run_gate(REPO)
    assert result["gate_passed"] is True
    assert result["gates"]["r3_r7_evidence_required"] is False
    # never loosens NEXT9 / live guards
    assert result["next9"]["next9_unblocked"] is False
    assert result["live_trading_enabled"] is False


def test_session_gate_require_r3_r7_passes_when_all_valid(monkeypatch):
    monkeypatch.setattr(c, "check_r3_r7_evidence", lambda repo, required=False: _all_valid_r3_r7_report())
    result = g.run_gate(REPO, require_r3_r7_evidence=True)
    assert result["gate_passed"] is True
    assert result["gates"]["r3_r7_evidence_required"] is True
    assert result["gates"]["r3_r7_evidence_ready"] is True
    assert "r3_r7_reduction_evidence" in result
    assert result["r3_r7_reduction_evidence"]["all_present_and_valid"] is True
    # strict tightening must never unblock NEXT9 or enable live trading
    assert result["next9"]["next9_unblocked"] is False
    assert result["live_trading_enabled"] is False
    assert result["paper_only"] is True


def test_session_gate_require_r3_r7_blocks_when_missing(monkeypatch):
    monkeypatch.setattr(c, "check_r3_r7_evidence", lambda repo, required=False: _missing_r3_r7_report())
    result = g.run_gate(REPO, require_r3_r7_evidence=True)
    assert result["gate_passed"] is False
    assert result["gates"]["r3_r7_evidence_required"] is True
    assert result["gates"]["r3_r7_evidence_ready"] is False
    assert "satisfy_r3_r7_reduction_evidence" in result["action_required"]
    # tightened gate still must NOT unblock NEXT9 or enable live trading
    assert result["next9"]["next9_unblocked"] is False
    assert result["gates"]["next9_not_unblocked"] is True
    assert result["live_trading_enabled"] is False


def test_session_gate_require_r3_r7_strict_exits_nonzero_when_missing(monkeypatch):
    monkeypatch.setattr(c, "check_r3_r7_evidence", lambda repo, required=False: _missing_r3_r7_report())
    code = g.main(["--strict", "--require-r3-r7-evidence", "--no-write"])
    assert code == 1
