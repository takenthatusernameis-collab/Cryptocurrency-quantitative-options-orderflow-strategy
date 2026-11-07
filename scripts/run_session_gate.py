#!/usr/bin/env python3
"""Deterministic session gate for crypto options orderflow paper ops.

Runs the P0 paper-ops readiness snapshot, the NEXT9/A1-A7 approval validation,
and the continuous-validation freshness check in one deterministic pass, then
emits a single additive timestamped artifact to research_state/.

Paper-only; never enables live trading. Exit non-zero (strict) when the gate
is not green so no session can skip the heavy P0 work.

Usage:
  PYTHONPATH=. python scripts/run_session_gate.py [--strict] [--max-cv-age-hours 2] [--no-write]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import check_paper_ops_readiness as c  # noqa: E402
import validate_next9_approval_artifact as v  # noqa: E402


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def run_gate(repo: Path = REPO, max_cv_age_hours: float = 2.0, include_r3_r7_evidence: bool = False) -> Dict[str, Any]:
    snap = c.build_snapshot(repo, max_cv_age_hours=max_cv_age_hours, include_r3_r7_evidence=include_r3_r7_evidence)
    next9 = v.check_current(repo)

    gates = snap.get("gates") or {}
    next9_unblocked = bool(next9.get("next9_unblocked", False))
    gate_passed = bool(
        gates.get("paper_ops_ready") is True
        and gates.get("cv_fresh_for_material_decisions") is True
        and gates.get("next9_blocked_until_explicit_human_approval_recorded") is True
        and gates.get("no_live_capital") is True
        and next9_unblocked is False
    )
    # Cross-invariant: readiness next9_blocked must agree with NEXT9 validation.
    block_agreement = bool(
        gates.get("next9_blocked_until_explicit_human_approval_recorded") is True
        and next9_unblocked is False
    )

    result: Dict[str, Any] = {
        "artifact_type": "PAPER_OPS_SESSION_GATE",
        "timestamp": _utc_iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "gate_passed": gate_passed,
        "block_agreement": block_agreement,
        "gates": {
            "paper_ops_ready": bool(gates.get("paper_ops_ready") is True),
            "cv_fresh_for_material_decisions": bool(gates.get("cv_fresh_for_material_decisions") is True),
            "next9_blocked_until_explicit_human_approval_recorded": bool(gates.get("next9_blocked_until_explicit_human_approval_recorded") is True),
            "no_live_capital": bool(gates.get("no_live_capital") is True),
            "next9_not_unblocked": next9_unblocked is False,
        },
        "readiness": {
            "artifact_path": snap.get("artifact_path"),
            "action_required": snap.get("action_required") or [],
        },
        "next9": {
            "next9_unblocked": next9_unblocked,
            "checkpoint_decision": next9.get("checkpoint_decision"),
            "issues": next9.get("issues") or [],
        },
        "action_required": [
            *(["rerun_strict_cv_before_material_decisions"] if not gates.get("cv_fresh_for_material_decisions") else []),
            *(["record_a1_a7_human_approvals_before_next9"] if next9_unblocked else []),
            *(["fix_live_guardrails"] if not gates.get("paper_ops_ready") else []),
            *(snap.get("action_required") or []),
        ],
    }
    if "r3_r7_reduction_evidence" in snap:
        result["r3_r7_reduction_evidence_advisory"] = snap["r3_r7_reduction_evidence"]
    return result


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(description="Deterministic paper-ops session gate")
    ap.add_argument("--strict", action="store_true", help="Exit non-zero if the session gate is not green")
    ap.add_argument("--max-cv-age-hours", type=float, default=2.0)
    ap.add_argument("--no-write", action="store_true")
    ap.add_argument("--include-r3-r7-evidence", action="store_true", help="Advisory: include R3-R7 reduction-evidence report (never blocks gate)")
    args = ap.parse_args(argv)

    result = run_gate(REPO, max_cv_age_hours=args.max_cv_age_hours, include_r3_r7_evidence=bool(args.include_r3_r7_evidence))
    ts = _utc()
    if not args.no_write:
        RS.mkdir(parents=True, exist_ok=True)
        out = RS / f"PAPER_OPS_SESSION_GATE_{ts}.json"
        try:
            rel = str(out.relative_to(REPO))
        except ValueError:
            rel = str(out)
        result["artifact_path"] = rel
        result["readiness"]["artifact_path"] = rel
        out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=False))
    if args.strict and not result["gate_passed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
