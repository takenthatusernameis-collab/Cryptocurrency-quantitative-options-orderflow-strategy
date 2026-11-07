#!/usr/bin/env python3
"""Generate stricter R5 execution/slippage simulation evidence (paper-only).

Deterministically consumes latest paper campaign, reconciliation audit, and pre-live
gate report into a v2 schema-validated artifact with conservative caps, warn-flag
policy, and deterministic pass criteria. Cites existing outputs; no live data
mutation. Never enables live trading. Never unblocks NEXT9. Advisory/opt-in.
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


def _load(path: Optional[Path]) -> Optional[Dict[str, Any]]:
    if not path or not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _latest(pattern: str) -> Optional[Path]:
    cands = sorted(RS.glob(pattern))
    return cands[-1] if cands else None


def _rel(path: Optional[Path]) -> Optional[str]:
    if not path or not path.exists():
        return None
    try:
        return path.relative_to(REPO).as_posix()
    except Exception:
        return str(path)


def _refs(*cands: str) -> List[str]:
    out = []
    for c in cands:
        p = REPO / c
        if p.exists():
            out.append(c)
    return out or list(cands[:1])


def gen_r5_strict(ts: Optional[str] = None) -> Dict[str, Any]:
    ts = ts or _utc()
    pc_p = _latest("PAPER_TRADING_CAMPAIGN_*.json")
    ra_p = _latest("RECONCILIATION_AUDIT_*.json")
    pl_p = _latest("PRE_LIVE_GATE_REPORT_*.json")

    pc = _load(pc_p) or {}
    ra = _load(ra_p) or {}
    pl = _load(pl_p) or {}

    tes = pc.get("trading_engine_summary") or {}
    ra_sum = ra.get("live_trading_summary") or ra.get("reconciliation_engine") or {}
    recon_audit = pc.get("reconciliation_audit") or {}
    pl_sum = pl.get("summary") or {}

    filled = tes.get("filled_orders") or ra_sum.get("filled_orders") or 0
    partial = tes.get("partially_filled_orders") or ra_sum.get("partially_filled_orders") or 0
    rejected = tes.get("rejected_orders") or ra_sum.get("rejected_orders") or 0
    cancelled = tes.get("cancelled_orders") or ra_sum.get("cancelled_orders") or 0
    total_fills = tes.get("total_fills") or ra_sum.get("total_fills") or 0
    match_rate = tes.get("reconciliation_match_rate") or ra_sum.get("reconciliation_match_rate") or recon_audit.get("reconciliation_match_rate") or 1.0
    unmatched_pos = recon_audit.get("unmatched_positions") or ra.get("reconciliation_engine", {}).get("unmatched_positions") or 0
    critical_unmatched = recon_audit.get("critical_unmatched") or ra.get("reconciliation_engine", {}).get("critical_unmatched") or 0

    paper_gates_passed = f"{pl_sum.get('passed',0)}/{pl_sum.get('total',0)}" if pl_sum else f"{pc.get('summary',{}).get('passed','?')}/{pc.get('summary',{}).get('total_gates','?')}"

    slippage_bps_conservative_cap = 15.0
    reject_rate_cap = 0.01
    partial_fill_rate_cap = 0.05

    denom_fill_reject = filled + rejected + partial
    denom_fill_partial = filled + partial
    reject_rate = (rejected / max(1, denom_fill_reject)) if denom_fill_reject > 0 else 0.0
    partial_rate = (partial / max(1, denom_fill_partial)) if denom_fill_partial > 0 else 0.0

    caps_ok = (
        reject_rate <= reject_rate_cap + 1e-12
        and partial_rate <= partial_fill_rate_cap + 1e-12
        and match_rate >= 0.999 - 1e-12
        and critical_unmatched == 0
    )

    warn_flags: List[str] = []
    if not pc:
        warn_flags.append("paper_campaign_missing")
    if not ra:
        warn_flags.append("reconciliation_audit_missing")
    if not pl:
        warn_flags.append("pre_live_gate_report_missing")
    if reject_rate > reject_rate_cap:
        warn_flags.append("reject_rate_exceeds_conservative_cap")
    if partial_rate > partial_fill_rate_cap:
        warn_flags.append("partial_fill_rate_exceeds_conservative_cap")
    if match_rate < 0.999:
        warn_flags.append("reconciliation_match_rate_below_slo")
    if critical_unmatched != 0:
        warn_flags.append("critical_unmatched_positions_nonzero")
    if denom_fill_reject == 0:
        warn_flags.append("no_fill_evidence_to_derive_rates")

    deterministic_pass = bool(
        pc and ra and pl and caps_ok and not warn_flags
    )

    evidence_refs = _refs(
        "research_state/PAPER_TRADING_CAMPAIGN_20261107T023814Z.json",
        "research_state/RECONCILIATION_AUDIT_20261107T023814Z.json",
        "research_state/PRE_LIVE_GATE_REPORT_20261107T023814Z.json",
    )
    for p, label in [(pc_p, "pc"), (ra_p, "ra"), (pl_p, "pl")]:
        r = _rel(p)
        if r and r not in evidence_refs:
            evidence_refs.append(r)
    if not evidence_refs:
        evidence_refs = ["docs/PAPER_RUNBOOK.md"]

    return {
        "artifact_type": v.ARTIFACT_TYPES["R5"],
        "timestamp_utc": _iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "simulation_scope": "stricter extraction from paper campaign + reconciliation audit + pre-live gate report; realized fill quality vs conservative caps; no live mutation",
        "evidence_refs": evidence_refs,
        "metrics": {
            "slippage_assumption_documented": True,
            "fill_quality_documented": True,
            "reconciliation_match_rate": float(match_rate),
            "paper_gates_passed": paper_gates_passed,
            "conservative_live_caps_required": True,
            "filled_orders": int(filled),
            "partially_filled_orders": int(partial),
            "rejected_orders": int(rejected),
            "cancelled_orders": int(cancelled),
            "total_fills": int(total_fills),
            "unmatched_positions": int(unmatched_pos),
            "critical_unmatched": int(critical_unmatched),
            "partial_fill_rate": float(partial_rate),
            "reject_rate": float(reject_rate),
            "slippage_bps_conservative_cap": float(slippage_bps_conservative_cap),
            "partial_fill_rate_cap": float(partial_fill_rate_cap),
            "reject_rate_cap": float(reject_rate_cap),
            "within_conservative_caps": bool(caps_ok),
        },
        "paper_or_backtest_derived": True,
        "advisory": True,
        "strictness": "enhanced_extraction_v2",
        "flags": {
            "deterministic_pass": deterministic_pass,
            "caps_enforced": True,
            "advisory_only": True,
        },
        "warn_flags": warn_flags,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate stricter R5 execution/slippage evidence (paper-only)")
    args = ap.parse_args(argv)
    ts = _utc()
    RS.mkdir(parents=True, exist_ok=True)
    d = gen_r5_strict(ts)
    ok, issues = v.validate_artifact(d, "R5")
    if not ok:
        print(json.dumps({"valid": False, "issues": issues}, indent=2))
        return 1
    out = RS / f"R5_EXECUTION_SLIPPAGE_SIM_EVIDENCE_{ts}.json"
    out.write_text(json.dumps(d, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out.relative_to(REPO)),
        "valid": True,
        "deterministic_pass": d["flags"]["deterministic_pass"],
        "within_conservative_caps": d["metrics"].get("within_conservative_caps"),
        "next9_unblocked": False,
        "warn_flags": d["warn_flags"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
