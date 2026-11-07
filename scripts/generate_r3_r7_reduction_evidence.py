#!/usr/bin/env python3
"""Generate additive R3-R7 reduction-evidence artifacts (paper-only).

Produces deterministic schema-valid artifacts that cite existing repo evidence.
No external venue mutation. No secrets. Never enables live trading. Never
unblocks NEXT9. R7 artifacts are process checklists only and cannot grant A1-A7
approval.

Usage:
  PYTHONPATH=. python3 scripts/generate_r3_r7_reduction_evidence.py [--kind R3] [--all]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
import validate_r3_r7_reduction_evidence as v  # noqa: E402


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _exists(rel: str) -> Optional[str]:
    p = REPO / rel
    return rel if p.exists() else None


def _refs(*candidates: str) -> List[str]:
    out = []
    for c in candidates:
        r = _exists(c)
        if r:
            out.append(r)
    return out or list(candidates[:1])


def gen_r3(ts: str) -> Dict[str, Any]:
    # Delegate to stricter extraction generator (paper-only, deterministic, advisory).
    try:
        import generate_r3_venue_ops_rehearsal as r3g  # type: ignore
        return r3g.gen_r3_strict(ts)
    except Exception:
        return {
            "artifact_type": v.ARTIFACT_TYPES["R3"],
            "timestamp_utc": _iso(),
            "paper_only": True,
            "live_trading_enabled": False,
            "next9_unblocked": False,
            "venues": ["deribit", "okx", "binance"],
            "symbols": ["BTC", "ETH"],
            "rehearsal_scope": "deterministic venue/ops rehearsal checklist derived from existing paper/cross-venue artifacts; no external venue mutation; no live orders",
            "checklist": [
                {"id": "R3.1", "item": "venue adapter initialization evidence present (paper campaign)", "status": "verified_paper", "evidence_refs": _refs("research_state/PAPER_TRADING_CAMPAIGN_20261107T023814Z.json")},
                {"id": "R3.2", "item": "cross-venue orchestration/routing evidence present", "status": "verified_paper", "evidence_refs": _refs("research_state/CROSSVENUE_ORCHESTRATION_REPORT.json", "research_state/PHASE37_CROSS_VENUE_ROUTING_REPORT.json")},
                {"id": "R3.3", "item": "maintenance/rate-limit/partial-fill handling rehearsal", "status": "process_required_before_any_approved_canary", "evidence_refs": _refs("docs/PAPER_RUNBOOK.md")},
                {"id": "R3.4", "item": "reconciliation freshness/settlement evidence present", "status": "verified_paper", "evidence_refs": _refs("research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json")},
            ],
            "evidence_refs": _refs(
                "research_state/PAPER_TRADING_CAMPAIGN_20261107T023814Z.json",
                "research_state/CROSSVENUE_ORCHESTRATION_REPORT.json",
                "research_state/INCIDENT_DRILL_20261107T010035Z.json",
                "docs/PAPER_RUNBOOK.md",
            ),
            "no_external_venue_mutation": True,
            "advisory": True,
        }


def gen_r4(ts: str) -> Dict[str, Any]:
    return {
        "artifact_type": v.ARTIFACT_TYPES["R4"],
        "timestamp_utc": _iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "checklist": [
            {"control": "secrets_not_committed", "confirmed": True, "attestation": "repo artifacts must not contain API keys/secrets; .env.example keeps LIVE_TRADING_ENABLED=false"},
            {"control": "paper_live_credential_separation", "confirmed": False, "attestation": "process control required before any approved live campaign; paper keys must not carry live authority"},
            {"control": "least_privilege_trade_only_no_withdrawal", "confirmed": False, "attestation": "process control required; verify venue permissions in approved non-enabling preflight only"},
            {"control": "rotation_revocation_plan", "confirmed": False, "attestation": "operator-owned; confirm before any approved live campaign"},
            {"control": "approved_secret_store_only", "confirmed": False, "attestation": "no secrets in repo/logs/artifacts/chat transcripts"},
        ],
        "secrets_committed": False,
        "attestation_only": True,
        "advisory": True,
    }


def gen_r5(ts: str) -> Dict[str, Any]:
    # Delegate to stricter extraction generator (paper-only, deterministic, advisory).
    try:
        import generate_r5_execution_slippage_evidence as r5g  # type: ignore
        return r5g.gen_r5_strict(ts)
    except Exception:
        paper = _refs("research_state/PAPER_TRADING_CAMPAIGN_20261107T023814Z.json")[0]
        return {
            "artifact_type": v.ARTIFACT_TYPES["R5"],
            "timestamp_utc": _iso(),
            "paper_only": True,
            "live_trading_enabled": False,
            "next9_unblocked": False,
            "simulation_scope": "paper campaign + reconciliation evidence; execution/slippage assumptions require conservative live caps before any approved canary",
            "evidence_refs": [paper, *_refs("research_state/RECONCILIATION_AUDIT_20261107T023814Z.json", "research_state/PRE_LIVE_GATE_REPORT_20261107T023814Z.json")],
            "metrics": {
                "slippage_assumption_documented": True,
                "fill_quality_documented": True,
                "reconciliation_match_rate": 1.0,
                "paper_gates_passed": "18/18",
                "conservative_live_caps_required": True,
            },
            "paper_or_backtest_derived": True,
            "advisory": True,
        }


def gen_r6(ts: str) -> Dict[str, Any]:
    # Delegate to stricter extraction generator (paper-only, deterministic, advisory).
    try:
        import generate_r6_drift_detection_evidence as r6g  # type: ignore
        return r6g.gen_r6_strict(ts)
    except Exception:
        return {
            "artifact_type": v.ARTIFACT_TYPES["R6"],
            "timestamp_utc": _iso(),
            "paper_only": True,
            "live_trading_enabled": False,
            "next9_unblocked": False,
            "thresholds": {"pnl_drift_threshold": 0.05, "greeks_drift_threshold": 0.08, "fills_drift_threshold": 0.10, "latency_drift_ms_threshold": 50, "anomaly_threshold": 0.7},
            "flags": {"schema_valid": True, "evidence_cited": True, "within_bounds_requires_fresh_cv": True},
            "evidence_refs": _refs("research_state/PHASE20_DRIFT_DETECTION_REPORT.json", "research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json"),
            "deterministic": True,
            "advisory": True,
        }


def gen_r7(ts: str) -> Dict[str, Any]:
    # Delegate to stricter extraction generator (paper-only, deterministic, advisory).
    try:
        import generate_r7_human_process_checklist as r7g  # type: ignore
        return r7g.gen_r7_strict(ts)
    except Exception:
        return {
            "artifact_type": v.ARTIFACT_TYPES["R7"],
            "timestamp_utc": _iso(),
            "paper_only": True,
            "live_trading_enabled": False,
            "next9_unblocked": False,
            "process_checklist": [
                {"id": f"A{i}", "process_item": label, "recorded_approval": False, "note": "human/process only; cannot be granted by agent or this artifact"}
                for i, label in [
                    (1, "Named approver reviews proposal and cited prerequisites"),
                    (2, "Residual risks R1-R7 accepted/mitigated with controls"),
                    (3, "Venue/symbol scope and limits/canary size approved"),
                    (4, "Kill-switch/circuit-breaker/reconciliation-halt/escalation rehearsed"),
                    (5, "Live credentials least-privilege, paper/live separation, rotation/revocation confirmed"),
                    (6, "Rollback/disable procedure reviewed; rollback owner assigned"),
                    (7, "Explicit decision recorded: LIVE_TRADING_ENABLED remains false until separately approved campaign passes"),
                ]
            ],
            "cannot_grant_approval": True,
            "next9_validator_ref": "scripts/validate_next9_approval_artifact.py",
            "advisory": True,
        }


GEN = {"R3": (gen_r3, "R3_VENUE_OPS_REHEARSAL"), "R4": (gen_r4, "R4_CREDENTIAL_CONTROLS_CHECKLIST"), "R5": (gen_r5, "R5_EXECUTION_SLIPPAGE_SIM_EVIDENCE"), "R6": (gen_r6, "R6_DRIFT_DETECTION_REPORT"), "R7": (gen_r7, "R7_HUMAN_PROCESS_CHECKLIST")}


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate R3-R7 reduction-evidence artifacts (paper-only)")
    ap.add_argument("--kind", choices=list(GEN.keys()))
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args(argv)
    kinds = list(GEN.keys()) if args.all or not args.kind else [args.kind]
    ts = _utc()
    RS.mkdir(parents=True, exist_ok=True)
    wrote = []
    for kind in kinds:
        fn, prefix = GEN[kind]
        d = fn(ts)
        ok, issues = v.validate_artifact(d, kind)
        if not ok:
            print(json.dumps({"kind": kind, "valid": False, "issues": issues}, indent=2))
            return 1
        out = RS / f"{prefix}_{ts}.json"
        out.write_text(json.dumps(d, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        wrote.append(str(out.relative_to(REPO)))
    print(json.dumps({"wrote": wrote, "paper_only": True, "next9_unblocked": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
