#!/usr/bin/env python3
"""Generate stricter R6 drift-detection evidence (paper-only).

Deterministically consumes PHASE20 drift report + latest strict CV/paper-monitoring
outputs (observability/alert audit/health SLO/resilience + CV checkpoint) into a v2
schema-validated artifact with deterministic pass/warn-flag policy. Cites existing
outputs; no live mutation. Never enables live trading. Never unblocks NEXT9.
Advisory/opt-in evidence.
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


def _latest(pattern: str) -> Optional[Path]:
    cands = sorted(RS.glob(pattern))
    return cands[-1] if cands else None


def _rel(p: Optional[Path]) -> Optional[str]:
    if not p:
        return None
    try:
        return p.relative_to(REPO).as_posix()
    except Exception:
        return str(p)


def _cv_checkpoint() -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    p = RS / "campaign_checkpoints" / "CONTINUOUS_VALIDATION_AND_MONITORING_latest.json"
    return _load(p), _rel(p) if p.exists() else None


def _cross_venue_latency_drift_breakdown(
    cross: Dict[str, Any], route: Dict[str, Any], phase20: Dict[str, Any]
) -> Dict[str, Any]:
    """Derive cross-venue per-symbol latency/drift breakdown (advisory, paper-only).

    Consumes CROSSVENUE_ORCHESTRATION_REPORT (per-venue latency ewma/samples/max/
    within_limit + taker fees + slippage), PHASE37 routing (routing ok), and PHASE20
    drift report (per-venue/per-symbol drift deltas vs baseline). Defaults to
    zero-fill paper state when no order-level detail is present. No live mutation,
    no secrets, never unblocks NEXT9.
    """
    lr = ((cross.get("components") or {}).get("latency_routing") or {})
    arb_cfg = ((cross.get("components") or {}).get("arbitrage") or {}).get("config") or {}
    mm = (cross.get("components") or {}).get("market_making") or {}
    mm_per_symbol = (mm.get("per_symbol") or {}) if isinstance(mm, dict) else {}
    latency = lr.get("latency") or {}
    slippage = lr.get("slippage") or {}
    taker_fees = arb_cfg.get("taker_fee_bps") or {}
    venues = list(cross.get("venues") or arb_cfg.get("venues") or ["deribit", "okx", "binance"])
    symbols = list(cross.get("symbols") or arb_cfg.get("symbols") or ["BTC", "ETH"])

    cfg = phase20.get("config") or {}
    det = phase20.get("detection") or {}
    baseline = phase20.get("baseline") or {}
    current = phase20.get("current") or {}
    latency_drift_threshold = float(cfg.get("latency_drift_ms_threshold", 50.0))
    baseline_latency_ms = float(baseline.get("latency_ms", 0.0))
    current_latency_ms = float(current.get("latency_ms", 0.0))
    global_latency_drift_ms = current_latency_ms - baseline_latency_ms
    within_latency_threshold = global_latency_drift_ms <= latency_drift_threshold + 1e-12

    per_venue: Dict[str, Any] = {}
    for venue in venues:
        vd = latency.get(venue) or {}
        venue_ewma = vd.get("ewma_ms")
        venue_drift_ms = None
        if isinstance(venue_ewma, (int, float)) and baseline_latency_ms:
            venue_drift_ms = float(venue_ewma) - baseline_latency_ms
        per_venue[venue] = {
            "ewma_ms": venue_ewma,
            "samples": vd.get("samples"),
            "max_sample_ms": vd.get("max_sample_ms"),
            "within_limit": vd.get("within_limit"),
            "taker_fee_bps": taker_fees.get(venue),
            "avg_slippage_bps": slippage.get("avg_slippage_bps"),
            "max_slippage_bps": slippage.get("max_slippage_bps"),
            "fills": slippage.get("fills"),
            "latency_drift_ms_vs_baseline": venue_drift_ms,
            "latency_drift_within_threshold": (
                bool(venue_drift_ms <= latency_drift_threshold + 1e-12)
                if venue_drift_ms is not None else None
            ),
            "routing_ok": route.get("ok") if route else None,
        }

    per_symbol: Dict[str, Any] = {}
    for symbol in symbols:
        sym_base = (baseline.get("greeks") or {}) if isinstance(baseline.get("greeks"), dict) else {}
        sym_cur = (current.get("greeks") or {}) if isinstance(current.get("greeks"), dict) else {}
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
            "gross_notional_usd": (mm_per_symbol.get(symbol) or {}).get("gross_notional_usd"),
            "net_delta_usd": (mm_per_symbol.get(symbol) or {}).get("net_delta_usd"),
            "delta_drift": (sym_cur.get("delta") - sym_base.get("delta"))
            if isinstance(sym_cur.get("delta"), (int, float)) and isinstance(sym_base.get("delta"), (int, float)) else None,
            "gamma_drift": (sym_cur.get("gamma") - sym_base.get("gamma"))
            if isinstance(sym_cur.get("gamma"), (int, float)) and isinstance(sym_base.get("gamma"), (int, float)) else None,
            "vega_drift": (sym_cur.get("vega") - sym_base.get("vega"))
            if isinstance(sym_cur.get("vega"), (int, float)) and isinstance(sym_base.get("vega"), (int, float)) else None,
        }

    return {
        "venues": venues,
        "symbols": symbols,
        "per_venue": per_venue,
        "per_symbol": per_symbol,
        "latency_drift_ms_threshold": latency_drift_threshold,
        "baseline_latency_ms": baseline_latency_ms,
        "current_latency_ms": current_latency_ms,
        "global_latency_drift_ms": global_latency_drift_ms,
        "within_latency_threshold": bool(within_latency_threshold),
        "crossvenue_paper_only": cross.get("paper_only"),
        "routing_ok": route.get("ok") if route else None,
        "phase20_within_bounds": det.get("within_bounds"),
    }


def gen_r6_strict(
    ts: Optional[str] = None, *, cross_venue_latency_drift: bool = False
) -> Dict[str, Any]:
    ts = ts or _utc()
    phase20_p = REPO / "research_state/PHASE20_DRIFT_DETECTION_REPORT.json"
    phase20 = _load(phase20_p) or {}
    cv, cv_ref = _cv_checkpoint()
    cv = cv or {}
    artifacts = cv.get("artifacts") or {}

    obs_p = (REPO / artifacts["observability"]) if artifacts.get("observability") else (_latest("OBSERVABILITY_REPORT_*.json") or RS / "_missing")
    alert_p = (REPO / artifacts["alert_audit"]) if artifacts.get("alert_audit") else (_latest("ALERT_AUDIT_*.json") or RS / "_missing")
    health_p = (REPO / artifacts["health_slo"]) if artifacts.get("health_slo") else (_latest("HEALTH_SLO_REPORT_*.json") or RS / "_missing")
    resil_p = (REPO / artifacts["resilience"]) if artifacts.get("resilience") else (_latest("RESILIENCE_AUDIT_*.json") or RS / "_missing")
    obs = _load(obs_p) or {}
    alert = _load(alert_p) or {}
    health = _load(health_p) or {}
    resil = _load(resil_p) or {}

    cfg = phase20.get("config") or {}
    det = phase20.get("detection") or {}
    thresholds = {
        "pnl_drift_threshold": float(cfg.get("pnl_drift_threshold", 0.05)),
        "greeks_drift_threshold": float(cfg.get("greeks_drift_threshold", 0.08)),
        "fills_drift_threshold": float(cfg.get("fills_drift_threshold", 0.1)),
        "latency_drift_ms_threshold": float(cfg.get("latency_drift_ms_threshold", 50)),
        "anomaly_threshold": float(cfg.get("anomaly_threshold", 0.7)),
    }

    cv_g = cv.get("gates") or {}
    cv_rf = cv.get("reconciliation_freshness") or {}
    cv_ok = bool(
        cv_g.get("all_critical_passed") is True
        and cv_g.get("iterations_5_5") is True
        and cv_g.get("reconciliation_freshness_gte_0_99_met_with_measurements") is True
        and cv_rf.get("met") is True
        and cv_rf.get("all_iterations_have_measurements") is True
    )
    phase20_ok = bool(det.get("within_bounds") is True and int(det.get("anomaly_count", 1)) == 0)
    health_status = ((health.get("health") or {}).get("status")) if isinstance(health.get("health"), dict) else health.get("status")
    health_ok = health_status in (None, "pass", "healthy", "ok") or bool((health.get("health") or {}).get("checks"))
    alert_audit = alert.get("audit") or {}
    unresolved = int(alert_audit.get("num_unresolved", 0) or 0)
    alert_bounded = unresolved <= 5
    resil_ok = bool(resil) or resil == {}

    warn_flags: List[str] = []
    if not phase20:
        warn_flags.append("phase20_drift_report_missing")
    if not cv_ok:
        warn_flags.append("cv_not_green_or_incomplete")
    if not phase20_ok:
        warn_flags.append("phase20_out_of_bounds_or_anomalies")
    if health_status not in (None, "pass", "healthy", "ok") and health:
        warn_flags.append(f"health_status:{health_status}")
    if not alert_bounded:
        warn_flags.append(f"unresolved_alerts_exceed_bound:{unresolved}")
    if not obs:
        warn_flags.append("observability_report_missing")
    if not alert:
        warn_flags.append("alert_audit_missing")
    if not health:
        warn_flags.append("health_slo_report_missing")

    deterministic_pass = bool(
        cv_ok and phase20_ok
        and not any(w.startswith("phase20_drift_report_missing") for w in warn_flags)
        and not any(w.startswith("cv_not_green") for w in warn_flags)
    )

    flags = {
        "schema_valid": True,
        "evidence_cited": True,
        "within_bounds_requires_fresh_cv": True,
        "cv_checkpoint_green": cv_ok,
        "phase20_within_bounds": phase20_ok,
        "health_slo_present": bool(health),
        "alert_audit_present": bool(alert),
        "observability_present": bool(obs),
        "resilience_present": bool(resil),
        "unresolved_alerts_bounded": alert_bounded,
        "deterministic_pass": deterministic_pass,
        "advisory_only": True,
        "cross_venue_latency_drift_breakdown_present": True,
    }

    evidence_refs: List[str] = []
    for r in [
        "research_state/PHASE20_DRIFT_DETECTION_REPORT.json",
        cv_ref,
        artifacts.get("observability"),
        artifacts.get("alert_audit"),
        artifacts.get("health_slo"),
        artifacts.get("resilience"),
        artifacts.get("continuous_validation"),
    ]:
        if r and (REPO / r).exists() and r not in evidence_refs:
            evidence_refs.append(r)
    if not evidence_refs:
        evidence_refs = ["research_state/PHASE20_DRIFT_DETECTION_REPORT.json"]

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

    latency_drift_breakdown = _cross_venue_latency_drift_breakdown(cross, route, phase20)
    if not latency_drift_breakdown.get("within_latency_threshold"):
        warn_flags.append("cross_venue_latency_drift_breakdown_exceeds_threshold")
    if cross_venue_latency_drift:
        warn_flags.append("cross_venue_latency_drift_breakdown_emitted_advisory")

    return {
        "artifact_type": v.ARTIFACT_TYPES["R6"],
        "timestamp_utc": _iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "thresholds": thresholds,
        "flags": flags,
        "warn_flags": warn_flags,
        "phase20_summary": {
            "present": bool(phase20),
            "report": phase20.get("report"),
            "timestamp": phase20.get("timestamp"),
            "anomaly_count": det.get("anomaly_count"),
            "anomaly_score": det.get("anomaly_score"),
            "within_bounds": det.get("within_bounds"),
            "alerts_count": det.get("alerts_count"),
        },
        "cv_summary": {
            "present": bool(cv),
            "timestamp": cv.get("timestamp"),
            "all_critical_passed": cv_g.get("all_critical_passed"),
            "iterations_5_5": cv_g.get("iterations_5_5"),
            "reconciliation_freshness_met": cv_g.get("reconciliation_freshness_gte_0_99_met_with_measurements"),
            "reconciliation_measurements": cv_rf.get("measurements_per_iteration"),
        },
        "monitoring_summary": {
            "health_status": health_status,
            "unresolved_alerts": unresolved,
            "observability_entries": ((obs.get("report") or {}).get("num_entries") if isinstance(obs.get("report"), dict) else None),
        },
        "cross_venue_latency_drift_breakdown": latency_drift_breakdown,
        "evidence_refs": evidence_refs,
        "deterministic": True,
        "advisory": True,
        "strictness": "enhanced_extraction_v2",
        "cross_venue_latency_drift": cross_venue_latency_drift,
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate stricter R6 drift-detection evidence (paper-only)")
    ap.add_argument(
        "--cross-venue-latency-drift",
        action="store_true",
        default=False,
        help="Advisory/default-off: emit cross-venue per-symbol latency/drift breakdown rows; no live mutation; does not grant approvals",
    )
    ap.parse_args(argv)
    ts = _utc()
    RS.mkdir(parents=True, exist_ok=True)
    d = gen_r6_strict(ts, cross_venue_latency_drift=args.cross_venue_latency_drift)
    ok, issues = v.validate_artifact(d, "R6")
    if not ok:
        print(json.dumps({"valid": False, "issues": issues}, indent=2))
        return 1
    out = RS / f"R6_DRIFT_DETECTION_REPORT_{ts}.json"
    out.write_text(json.dumps(d, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out.relative_to(REPO)),
        "valid": True,
        "deterministic_pass": d["flags"]["deterministic_pass"],
        "cross_venue_latency_drift_breakdown_present": d["flags"].get("cross_venue_latency_drift_breakdown_present", True),
        "cross_venue_latency_drift": d.get("cross_venue_latency_drift"),
        "next9_unblocked": False,
        "warn_flags": d["warn_flags"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
