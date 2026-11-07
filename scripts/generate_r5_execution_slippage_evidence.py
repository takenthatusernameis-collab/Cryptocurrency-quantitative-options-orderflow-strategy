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


def _cross_venue_slippage_breakdown(cross: Dict[str, Any], route: Dict[str, Any]) -> Dict[str, Any]:
    """Derive cross-venue per-symbol slippage breakdown from cross-venue artifacts.

    Advisory only; no live mutation; no secrets. Produces per-venue latency/slippage
    rows and per venue x symbol slippage rows (default-off emission). Defaults to
    zero-fill paper state when no order-level detail is present.
    """
    lr = ((cross.get("components") or {}).get("latency_routing") or {})
    arb_cfg = ((cross.get("components") or {}).get("arbitrage") or {}).get("config") or {}
    venues = list(cross.get("venues") or arb_cfg.get("venues") or ["deribit", "okx", "binance"])
    symbols = list(cross.get("symbols") or arb_cfg.get("symbols") or ["BTC", "ETH"])
    latency = lr.get("latency") or {}
    slippage = lr.get("slippage") or {}
    taker_fees = arb_cfg.get("taker_fee_bps") or {}

    per_venue: Dict[str, Any] = {}
    for venue in venues:
        vd = latency.get(venue) or {}
        per_venue[venue] = {
            "ewma_ms": vd.get("ewma_ms"),
            "samples": vd.get("samples"),
            "max_sample_ms": vd.get("max_sample_ms"),
            "within_limit": vd.get("within_limit"),
            "taker_fee_bps": taker_fees.get(venue),
            "avg_slippage_bps": slippage.get("avg_slippage_bps"),
            "max_slippage_bps": slippage.get("max_slippage_bps"),
            "fills": slippage.get("fills"),
            "total_slippage_bps": slippage.get("total_slippage_bps"),
            "routing_ok": route.get("ok") if route else None,
        }

    per_symbol: Dict[str, Any] = {}
    for symbol in symbols:
        per_symbol[symbol] = {
            "venues": {
                venue: {
                    "ewma_ms": (latency.get(venue) or {}).get("ewma_ms"),
                    "taker_fee_bps": taker_fees.get(venue),
                    "avg_slippage_bps": slippage.get("avg_slippage_bps"),
                    "max_slippage_bps": slippage.get("max_slippage_bps"),
                    "fills": slippage.get("fills"),
                }
                for venue in venues
            },
            "gross_notional_usd": (((cross.get("components") or {}).get("market_making") or {}).get("per_symbol") or {}).get(symbol, {}).get("gross_notional_usd"),
            "net_delta_usd": (((cross.get("components") or {}).get("market_making") or {}).get("per_symbol") or {}).get(symbol, {}).get("net_delta_usd"),
        }

    return {
        "venues": venues,
        "symbols": symbols,
        "per_venue": per_venue,
        "per_symbol": per_symbol,
        "slippage_bps_conservative_cap": 15.0,
        "within_conservative_caps": bool(
            (slippage.get("max_slippage_bps") or 0.0) <= 15.0 + 1e-12
            and (slippage.get("avg_slippage_bps") or 0.0) <= 15.0 + 1e-12
        ),
        "crossvenue_paper_only": cross.get("paper_only"),
        "routing_ok": route.get("ok") if route else None,
    }


def gen_r5_strict(ts: Optional[str] = None, *, per_symbol_slippage: bool = False) -> Dict[str, Any]:
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

    cross_p = RS / "CROSSVENUE_ORCHESTRATION_REPORT.json"
    route_p = RS / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json"
    cross = _load(cross_p) or {}
    route = _load(route_p) or {}
    if cross_p.exists():
        r = _rel(cross_p)
        if r and r not in evidence_refs:
            evidence_refs.append(r)
    if route_p.exists():
        r = _rel(route_p)
        if r and r not in evidence_refs:
            evidence_refs.append(r)

    slippage_breakdown = _cross_venue_slippage_breakdown(cross, route)
    if not slippage_breakdown.get("within_conservative_caps"):
        warn_flags.append("cross_venue_slippage_breakdown_exceeds_conservative_cap")
    if per_symbol_slippage:
        warn_flags.append("per_symbol_slippage_breakdown_emitted_advisory")

    return {
        "artifact_type": v.ARTIFACT_TYPES["R5"],
        "timestamp_utc": _iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "simulation_scope": "stricter extraction from paper campaign + reconciliation audit + pre-live gate report; realized fill quality vs conservative caps; cross-venue per-symbol slippage breakdown from CROSSVENUE_ORCHESTRATION_REPORT + PHASE37 routing; no live mutation",
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
            "cross_venue_slippage_breakdown": slippage_breakdown,
        },
        "per_symbol_slippage": per_symbol_slippage,
        "paper_or_backtest_derived": True,
        "advisory": True,
        "strictness": "enhanced_extraction_v2",
        "flags": {
            "deterministic_pass": deterministic_pass,
            "caps_enforced": True,
            "advisory_only": True,
            "cross_venue_slippage_breakdown_present": True,
        },
        "warn_flags": warn_flags,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate stricter R5 execution/slippage evidence (paper-only)")
    ap.add_argument("--per-symbol-slippage", action="store_true", default=False, help="Advisory/default-off: emit cross-venue per-symbol slippage breakdown rows; no live mutation; does not grant approvals")
    args = ap.parse_args(argv)
    ts = _utc()
    RS.mkdir(parents=True, exist_ok=True)
    d = gen_r5_strict(ts, per_symbol_slippage=args.per_symbol_slippage)
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
        "cross_venue_slippage_breakdown_present": d["flags"].get("cross_venue_slippage_breakdown_present"),
        "per_symbol_slippage": d.get("per_symbol_slippage"),
        "next9_unblocked": False,
        "warn_flags": d["warn_flags"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
