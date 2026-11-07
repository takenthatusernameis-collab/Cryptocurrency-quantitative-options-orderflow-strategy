#!/usr/bin/env python3
"""Generate stricter R3 venue/ops rehearsal evidence from existing paper/cross-venue artifacts (paper-only).

Deterministically consumes CROSSVENUE_ORCHESTRATION_REPORT, PHASE37_CROSS_VENUE_ROUTING_REPORT,
latest incident drill, and PAPER_RUNBOOK to produce schema-validated R3 rehearsal rows
including partial-fill/reject/rate-limit/maintenance checklist coverage. No external venue
mutation. No live orders. Never enables live trading. Never unblocks NEXT9. Advisory/opt-in.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
DOCS = REPO / "docs"
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
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
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


def _runbook_has(*needles: str) -> Tuple[bool, List[str]]:
    p = DOCS / "PAPER_RUNBOOK.md"
    if not p.exists():
        return False, [f"runbook_missing:{n}" for n in needles]
    text = p.read_text(encoding="utf-8", errors="ignore").lower()
    missing = []
    for n in needles:
        nlow = n.lower()
        # allow common synonyms/phrases and case/spacing variations
        if nlow in text:
            continue
        # partial-fill variants
        if "partial" in nlow and "fill" in nlow and ("partial fill" in text or "partial-fill" in text or "partially filled" in text or "partial fills" in text):
            continue
        # rate limit variants
        if "rate" in nlow and "limit" in nlow and ("rate limit" in text or "rate-limit" in text or "rate limiting" in text or "throttl" in text):
            continue
        # reject variants
        if "reject" in nlow and ("reject" in text or "rejected" in text or "order reject" in text):
            continue
        # maintenance variants
        if "mainten" in nlow and ("maintenance" in text or "downtime" in text or "venue down" in text or "scheduled outage" in text):
            continue
        # kill-switch variants
        if "kill" in nlow and ("kill-switch" in text or "killswitch" in text or "kill switch" in text or "circuit breaker" in text or "auto-halt" in text):
            continue
        # reconciliation variants
        if "reconcil" in nlow and ("reconciliation" in text or "reconcil" in text or "position mismatch" in text):
            continue
        missing.append(n)
    return len(missing) == 0, missing


def _crossvenue_summary(d: Dict[str, Any]) -> Dict[str, Any]:
    counts = d.get("counts") or {}
    pnl = d.get("pnl") or {}
    cfg = d.get("config") or {}
    ks = d.get("kill_switch") or {}
    return {
        "present": bool(d),
        "paper_only": d.get("paper_only"),
        "venues": d.get("venues") or cfg.get("venues"),
        "symbols": d.get("symbols") or cfg.get("symbols"),
        "cycles_completed": counts.get("cycles_completed"),
        "arb_opportunities": counts.get("arb_opportunities"),
        "arb_fills": counts.get("arb_fills"),
        "router_fills": counts.get("router_fills"),
        "halted": d.get("halted"),
        "kill_switch_triggered": ks.get("triggered"),
        "realized_pnl_usd": pnl.get("realized_pnl_usd"),
        "net_pnl_usd": pnl.get("net_pnl_usd"),
    }


def _routing_summary(d: Dict[str, Any]) -> Dict[str, Any]:
    if not d:
        return {"present": False}
    # PHASE37 may vary; extract common fields defensively
    keys = ("ok", "cycles", "paper_only", "report", "venues", "symbols", "counts", "routing", "summary", "status")
    out: Dict[str, Any] = {"present": True}
    for k in keys:
        if k in d:
            out[k] = d[k]
    # normalize nested fields if present
    if isinstance(d.get("summary"), dict):
        out["summary_normalized"] = d.get("summary")
    if isinstance(d.get("counts"), dict):
        out["counts_normalized"] = d.get("counts")
    return out


def _incident_summary(d: Dict[str, Any]) -> Dict[str, Any]:
    scenarios = d.get("scenarios") or []
    cats = sorted({str(s.get("category")) for s in scenarios if isinstance(s, dict) and s.get("category")})
    names = [str(s.get("name")) for s in scenarios if isinstance(s, dict) and s.get("name")]
    return {
        "present": bool(d),
        "drill_id": d.get("drill_id"),
        "all_passed": d.get("all_passed"),
        "scenario_count": len(scenarios),
        "categories": cats,
        "scenario_names": names,
        "paper_only_guardrail": "No live capital" in str(d.get("guardrail", "")),
    }


def gen_r3_strict(ts: Optional[str] = None) -> Dict[str, Any]:
    cross_p = RS / "CROSSVENUE_ORCHESTRATION_REPORT.json"
    route_p = RS / "PHASE37_CROSS_VENUE_ROUTING_REPORT.json"
    drill_p = _latest("INCIDENT_DRILL_*Z.json")
    runbook_p = DOCS / "PAPER_RUNBOOK.md"

    cross = _load(cross_p) or {}
    route = _load(route_p) or {}
    drill = _load(drill_p) if drill_p else {}
    drill = drill or {}

    runbook_ok, runbook_missing = _runbook_has(
        "rate limit", "partial fill", "reject", "maintenance", "kill-switch", "reconciliation"
    )

    cross_s = _crossvenue_summary(cross)
    route_s = _routing_summary(route)
    drill_s = _incident_summary(drill)

    venues = cross_s.get("venues") or route_s.get("venues") or ["deribit", "okx", "binance"]
    symbols = cross_s.get("symbols") or route_s.get("symbols") or ["BTC", "ETH"]

    def _per_venue_rows(items: List[str], prefix: str) -> List[Dict[str, Any]]:
        rows = []
        for vname in (items or []):
            rows.append({
                "id": f"{prefix}.{vname}",
                "venue": vname,
                "status": "paper_evidence_present" if cross else "review_required",
                "evidence_refs": [r for r in [_rel(cross_p), _rel(route_p)] if r and (REPO / r).exists()],
                "note": "paper-only cross-venue evidence; no external venue mutation",
            })
        return rows

    warn_flags: List[str] = []
    if not cross:
        warn_flags.append("crossvenue_orchestration_report_missing")
    if not route:
        warn_flags.append("phase37_routing_report_missing")
    if not drill:
        warn_flags.append("incident_drill_missing")
    if not runbook_p.exists():
        warn_flags.append("paper_runbook_missing")
    if runbook_missing:
        warn_flags.append("paper_runbook_missing_keywords:" + ",".join(sorted(runbook_missing)))
    if drill and drill_s.get("all_passed") is not True:
        warn_flags.append("incident_drill_not_all_passed")
    if cross and cross_s.get("kill_switch_triggered") is True:
        warn_flags.append("crossvenue_kill_switch_triggered")

    evidence_refs: List[str] = []
    for r in [
        _rel(cross_p),
        _rel(route_p),
        _rel(drill_p),
        _rel(runbook_p),
        "research_state/PAPER_TRADING_CAMPAIGN_20261107T023814Z.json",
        "research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json",
    ]:
        if r and (REPO / r).exists() and r not in evidence_refs:
            evidence_refs.append(r)
    if not evidence_refs:
        evidence_refs = ["docs/PAPER_RUNBOOK.md"]

    checklist = [
        {
            "id": "R3.1",
            "item": "venue adapter initialization/cross-venue orchestration evidence present (paper campaign artifacts)",
            "status": "verified_paper" if cross else "missing_evidence",
            "evidence_refs": [r for r in [_rel(cross_p), "research_state/PAPER_TRADING_CAMPAIGN_20261107T023814Z.json"] if r and (REPO / r).exists()],
            "observed": {"cycles_completed": cross_s.get("cycles_completed"), "halted": cross_s.get("halted")},
            "per_venue": _per_venue_rows(list(venues) if isinstance(venues, list) else [str(venues)], "R3.1v"),
        },
        {
            "id": "R3.2",
            "item": "cross-venue routing evidence present; routing layer covered in paper artifacts",
            "status": "verified_paper" if route else "missing_evidence",
            "evidence_refs": [r for r in [_rel(route_p), _rel(cross_p)] if r and (REPO / r).exists()],
            "observed": route_s,
            "per_venue": _per_venue_rows(list(venues) if isinstance(venues, list) else [str(venues)], "R3.2v"),
        },
        {
            "id": "R3.3",
            "item": "partial-fill handling rehearsal coverage (paper/runbook/process; no external venue mutation)",
            "status": "process_documented" if ("partial" not in " ".join(runbook_missing).lower()) else "process_review_required",
            "evidence_refs": [r for r in [_rel(runbook_p), _rel(drill_p)] if r and (REPO / r).exists()],
            "notes": "No external venue orders placed; handling verified via paper artifacts/runbook and incident controls.",
        },
        {
            "id": "R3.4",
            "item": "reject handling rehearsal coverage (paper/runbook/process; no external venue mutation)",
            "status": "process_documented" if ("reject" not in " ".join(runbook_missing).lower()) else "process_review_required",
            "evidence_refs": [r for r in [_rel(runbook_p), _rel(drill_p)] if r and (REPO / r).exists()],
            "notes": "Reject/risk/circuit-breaker handling covered by runbook/drill evidence; no live venue mutation.",
        },
        {
            "id": "R3.5",
            "item": "rate-limit handling rehearsal coverage (paper/runbook/process; no external venue mutation)",
            "status": "process_documented" if ("rate limit" not in " ".join(runbook_missing).lower()) else "process_review_required",
            "evidence_refs": [r for r in [_rel(runbook_p)] if r and (REPO / r).exists()],
            "notes": "Rate-limit/maintenance are venue-operational risks; runbook/checklist coverage required before any approved canary.",
        },
        {
            "id": "R3.6",
            "item": "maintenance-window handling rehearsal coverage (paper/runbook/process; no external venue mutation)",
            "status": "process_documented" if ("maintenance" not in " ".join(runbook_missing).lower()) else "process_review_required",
            "evidence_refs": [r for r in [_rel(runbook_p)] if r and (REPO / r).exists()],
            "notes": "No venue maintenance mutation performed; operator procedure must remain paper-gated until approved.",
        },
        {
            "id": "R3.7",
            "item": "incident drill / kill-switch / reconciliation containment evidence present",
            "status": "verified_paper" if drill_s.get("all_passed") is True else "missing_or_failed_evidence",
            "evidence_refs": [r for r in [_rel(drill_p), "research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json"] if r and (REPO / r).exists()],
            "observed": drill_s,
        },
    ]

    deterministic_pass = bool(
        cross and route and drill_s.get("all_passed") is True and runbook_p.exists() and cross_s.get("kill_switch_triggered") is not True
    )

    return {
        "artifact_type": v.ARTIFACT_TYPES["R3"],
        "timestamp_utc": _iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "venues": venues,
        "symbols": symbols,
        "rehearsal_scope": "deterministic venue/ops rehearsal from cross-venue orchestration, routing, incident drill, and paper runbook; partial-fill/reject/rate-limit/maintenance checklist rows; no external venue mutation; no live orders",
        "checklist": checklist,
        "per_venue_coverage": _per_venue_rows(list(venues) if isinstance(venues, list) else [str(venues)], "R3V"),
        "source_summaries": {
            "crossvenue_orchestration": cross_s,
            "routing": route_s,
            "incident_drill": drill_s,
            "runbook_keywords_ok": runbook_ok,
            "runbook_missing_keywords": runbook_missing,
        },
        "flags": {
            "deterministic_pass": deterministic_pass,
            "no_external_venue_mutation": True,
            "advisory_only": True,
        },
        "warn_flags": warn_flags,
        "evidence_refs": evidence_refs,
        "no_external_venue_mutation": True,
        "advisory": True,
        "strictness": "enhanced_extraction_v2",
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate stricter R3 venue/ops rehearsal evidence (paper-only)")
    ap.parse_args(argv)
    RS.mkdir(parents=True, exist_ok=True)
    d = gen_r3_strict(_utc())
    ok, issues = v.validate_artifact(d, "R3")
    if not ok:
        print(json.dumps({"valid": False, "issues": issues}, indent=2))
        return 1
    out = RS / f"R3_VENUE_OPS_REHEARSAL_{_utc()}.json"
    out.write_text(json.dumps(d, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out.relative_to(REPO)),
        "valid": True,
        "deterministic_pass": d["flags"]["deterministic_pass"],
        "warn_flags": d["warn_flags"],
        "next9_unblocked": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
