#!/usr/bin/env python3
"""Deterministic paper-ops readiness snapshot for crypto options + orderflow.

Reads repo guardrails and latest additive artifacts (CV, paper campaign, NEXT8,
continuity). Emits a timestamped JSON artifact to research_state/ and prints a
summary. Paper-only; never enables live trading.

Usage:
  PYTHONPATH=. python scripts/check_paper_ops_readiness.py [--strict] [--max-cv-age-hours 2]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
CP = RS / "campaign_checkpoints"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import validate_next9_approval_artifact  # noqa: E402


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _utc_str(dt: Optional[datetime] = None) -> str:
    return (dt or _utc_now()).strftime("%Y%m%dT%H%M%SZ")


def _parse_iso(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        s = ts.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _parse_compact(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    m = re.search(r"(\d{8}T\d{6}Z)", ts)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _git_tracked_diff_names(repo: Path) -> List[str]:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(repo), "diff", "--name-only", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        return []


def check_live_guardrails(repo: Path = REPO) -> Dict[str, Any]:
    secrets = (repo / "src/config/secrets.py").read_text(encoding="utf-8")
    env_example = (repo / ".env.example").read_text(encoding="utf-8")
    default_false = bool(
        re.search(r"""LIVE_TRADING_ENABLED["']\s*,\s*["']false["']""", secrets)
    )
    env_false = "LIVE_TRADING_ENABLED=false" in env_example and "LIVE_TRADING_ENABLED=true" not in env_example
    tracked = _git_tracked_diff_names(repo)
    live_enabling = [
        f for f in tracked
        if f in {"src/config/secrets.py", ".env.example"} or "live_trading" in f.lower()
    ]
    return {
        "live_trading_default_false": default_false,
        "env_example_live_trading_false": env_false,
        "tracked_diff_files": tracked,
        "tracked_live_enabling_changes": live_enabling,
        "tracked_worktree_clean_of_live_enabling_changes": len(live_enabling) == 0,
        "paper_only_required": True,
        "passed": default_false and env_false and len(live_enabling) == 0,
    }


def check_cv(repo: Path = REPO, max_age_hours: float = 2.0) -> Dict[str, Any]:
    cp_path = repo / "research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json"
    d = _load_json(cp_path)
    if not d:
        return {"exists": False, "passed": False, "details": "missing CV checkpoint"}
    ts = _parse_iso(d.get("timestamp")) or _parse_compact(cp_path.name)
    age_h = None
    fresh = None
    if ts:
        age_h = (_utc_now() - ts).total_seconds() / 3600.0
        fresh = age_h <= float(max_age_hours)
    g = d.get("gates") or {}
    rf = d.get("reconciliation_freshness") or {}
    measurements = rf.get("measurements_per_iteration") or []
    passed = bool(
        d.get("paper_only") is True
        and d.get("live_trading_enabled") is False
        and g.get("all_critical_passed") is True
        and g.get("iterations_5_5") is True
        and g.get("reconciliation_freshness_gte_0_99_met_with_measurements") is True
        and rf.get("met") is True
        and rf.get("all_iterations_have_measurements") is True
        and len(measurements) >= 1
        and all(float(m) > 0 for m in measurements)
    )
    return {
        "exists": True,
        "path": str(cp_path.relative_to(repo)),
        "timestamp": d.get("timestamp"),
        "age_hours": round(age_h, 4) if age_h is not None else None,
        "fresh_within_max_age_hours": fresh,
        "max_age_hours": float(max_age_hours),
        "paper_only": d.get("paper_only"),
        "live_trading_enabled": d.get("live_trading_enabled"),
        "gates": {
            "all_critical_passed": g.get("all_critical_passed"),
            "iterations_5_5": g.get("iterations_5_5"),
            "reconciliation_freshness_met": g.get("reconciliation_freshness_gte_0_99_met_with_measurements"),
        },
        "reconciliation_freshness": {
            "met": rf.get("met"),
            "measurements_per_iteration": measurements,
        },
        "passed": passed,
    }


def check_paper_campaign(repo: Path = REPO) -> Dict[str, Any]:
    # Prefer latest PAPER_TRADING_CAMPAIGN_*.json by filename timestamp.
    cands = sorted((repo / "research_state").glob("PAPER_TRADING_CAMPAIGN_*.json"))
    if not cands:
        return {"exists": False, "passed": False}
    path = cands[-1]
    d = _load_json(path)
    if not d:
        return {"exists": False, "path": str(path.relative_to(repo)), "passed": False}
    s = d.get("summary") or {}
    # R1 schema nuance: use summary fields.
    all_ok = s.get("all_critical_passed") is True and int(s.get("failed", 1)) == 0
    return {
        "exists": True,
        "path": str(path.relative_to(repo)),
        "timestamp": d.get("timestamp"),
        "summary": {
            "total_gates": s.get("total_gates"),
            "passed": s.get("passed"),
            "failed": s.get("failed"),
            "all_critical_passed": s.get("all_critical_passed"),
        },
        "passed": bool(all_ok),
    }


def check_next8(repo: Path = REPO) -> Dict[str, Any]:
    cp = repo / "research_state/campaign_checkpoints/LIVE_ENABLEMENT_PROPOSAL_REVIEW_ONLY_latest.json"
    d = _load_json(cp)
    if not d:
        return {"exists": False, "next9_unblocked": False, "a1_a7_all_approved": False}
    proposal_path = (d.get("artifacts") or {}).get("proposal_json")
    checklist_ok = False
    a1_a7_approved = False
    approval_issues: List[str] = []
    if proposal_path:
        prop = _load_json(repo / proposal_path)
        if prop:
            checklist = prop.get("human_approval_checklist") or []
            if isinstance(checklist, list) and checklist:
                checklist_ok = True
                # Strict A1-A7 field validation (shared invariant). A bare
                # `approved: true` with empty approver/scope/limits must NOT
                # unblock NEXT9 — only a full, non-empty approval record does.
                ok, approval_issues = validate_next9_approval_artifact.validate_approval_artifact(prop)
                a1_a7_approved = bool(ok)
    decision = d.get("live_enablement_decision")
    # Block invariant: NEXT9 unblocks only when A1-A7 are fully approved AND the
    # checkpoint decision is not an explicit NO_GO.
    next9_unblocked = bool(
        a1_a7_approved
        and decision != "NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL"
    )
    return {
        "exists": True,
        "path": str(cp.relative_to(repo)),
        "decision": decision,
        "live_trading_enabled": d.get("live_trading_enabled"),
        "paper_only": d.get("paper_only"),
        "checklist_found": checklist_ok,
        "a1_a7_all_approved": bool(a1_a7_approved),
        "a1_a7_approval_issues": approval_issues,
        "next9_unblocked": next9_unblocked,
        "passed_block_invariant": decision == "NO_GO_PENDING_EXPLICIT_HUMAN_APPROVAL" and not a1_a7_approved,
    }


def build_snapshot(repo: Path = REPO, max_cv_age_hours: float = 2.0) -> Dict[str, Any]:
    guardrails = check_live_guardrails(repo)
    cv = check_cv(repo, max_age_hours=max_cv_age_hours)
    paper = check_paper_campaign(repo)
    next8 = check_next8(repo)
    all_paper_ops_ready = bool(guardrails["passed"] and cv["passed"] and paper["passed"])
    cv_fresh_enough = cv.get("fresh_within_max_age_hours") is True
    return {
        "artifact_type": "PAPER_OPS_READINESS_SNAPSHOT",
        "timestamp": _utc_now().isoformat().replace("+00:00", "Z"),
        "paper_only": True,
        "live_trading_enabled": False,
        "guardrails": guardrails,
        "cv": cv,
        "paper_campaign": paper,
        "next8_live_enablement": next8,
        "gates": {
            "paper_ops_ready": all_paper_ops_ready,
            "cv_fresh_for_material_decisions": cv_fresh_enough,
            "next9_blocked_until_explicit_human_approval_recorded": not next8.get("next9_unblocked", False),
            "no_live_capital": True,
        },
        "action_required": [
            *(["rerun_strict_cv_before_material_decisions"] if not cv_fresh_enough else []),
            *(["record_a1_a7_human_approvals_before_next9"] if not next8.get("a1_a7_all_approved") else []),
            *(["fix_live_guardrails"] if not guardrails["passed"] else []),
        ],
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Paper-ops readiness snapshot (paper-only)")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero if paper ops not ready")
    ap.add_argument("--max-cv-age-hours", type=float, default=2.0)
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    snap = build_snapshot(REPO, max_cv_age_hours=args.max_cv_age_hours)
    ts = _utc_str()
    out = RS / f"PAPER_OPS_READINESS_SNAPSHOT_{ts}.json"
    if not args.no_write:
        RS.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(snap, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        snap["artifact_path"] = str(out.relative_to(REPO))
    print(json.dumps(snap, indent=2, allow_nan=False))
    if args.strict and not snap["gates"]["paper_ops_ready"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
