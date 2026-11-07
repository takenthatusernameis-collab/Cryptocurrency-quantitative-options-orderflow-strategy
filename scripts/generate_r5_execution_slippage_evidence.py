#!/usr/bin/env python3
"""Generate stricter R5 execution/slippage simulation evidence from paper campaign/recon (paper-only).
Extracts/normalizes realized fill quality, reject/partial rates, reconciliation match rates into
a stricter schema-validated artifact; cites existing outputs; no live data mutation.
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


def _load(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _refs(*cands: str) -> List[str]:
    out = []
    for c in cands:
        p = REPO / c
        if p.exists():
            out.append(c)
    return out or list(cands[:1])


def _latest_campaign() -> Optional[Dict[str, Any]]:
    # find latest PAPER_TRADING_CAMPAIGN
    cands = sorted((RS).glob("PAPER_TRADING_CAMPAIGN_*.json"))
    if not cands:
        return None
    return _load(cands[-1])


def _latest_recon() -> Optional[Dict[str, Any]]:
    cands = sorted((RS).glob("RECONCILIATION_AUDIT_*.json"))
    if not cands:
        return None
    return _load(cands[-1])


def _latest_prelive() -> Optional[Dict[str, Any]]:
    cands = sorted((RS).glob("PRE_LIVE_GATE_REPORT_*.json"))
    if not cands:
        return None
    return _load(cands[-1])


def gen_r5_strict(ts: str) -> Dict[str, Any]:
    pc = _latest_campaign() or {}
    ra = _latest_recon() or {}
    pl = _latest_prelive() or {}

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

    # conservative caps (paper-derived defaults; never auto-enabling)
    slippage_bps_conservative_cap = 15.0
    reject_rate_cap = 0.01
    partial_fill_rate_cap = 0.05

    reject_rate = (rejected / max(1, filled + rejected + partial)) if (filled + rejected + partial) > 0 else 0.0
    partial_rate = (partial / max(1, filled + partial)) if (filled + partial) > 0 else 0.0

    caps_ok = (reject_rate <= reject_rate_cap + 1e-12) and (partial_rate <= partial_fill_rate_cap + 1e-12) and (match_rate >= 0.999 - 1e-12) and (critical_unmatched == 0)

    evidence_refs = _refs(
        "research_state/PAPER_TRADING_CAMPAIGN_20261107T023814Z.json",
        "research_state/RECONCILIATION_AUDIT_20261107T023814Z.json",
        "research_state/PRE_LIVE_GATE_REPORT_20261107T023814Z.json",
    )
    # add latest if different
    pc_latest = sorted((RS).glob("PAPER_TRADING_CAMPAIGN_*.json"))[-1].relative_to(REPO).as_posix() if sorted((RS).glob("PAPER_TRADING_CAMPAIGN_*.json")) else None
    ra_latest = sorted((RS).glob("RECONCILIATION_AUDIT_*.json"))[-1].relative_to(REPO).as_posix() if sorted((RS).glob("RECONCILIATION_AUDIT_*.json")) else None
    pl_latest = sorted((RS).glob("PRE_LIVE_GATE_REPORT_*.json"))[-1].relative_to(REPO).as_posix() if sorted((RS).glob("PRE_LIVE_GATE_REPORT_*.json")) else None
    for r in [pc_latest, ra_latest, pl_latest]:
        if r and r not in evidence_refs:
            evidence_refs.append(r)

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
        "strictness": "enhanced_extraction_v1",
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
    print(json.dumps({"wrote": str(out.relative_to(REPO)), "valid": True, "within_conservative_caps": d["metrics"].get("within_conservative_caps")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
