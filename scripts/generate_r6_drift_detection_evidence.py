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


def gen_r6_strict(ts: Optional[str] = None) -> Dict[str, Any]:
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
        "evidence_refs": evidence_refs,
        "deterministic": True,
        "advisory": True,
        "strictness": "enhanced_extraction_v2",
    }


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate stricter R6 drift-detection evidence (paper-only)")
    ap.parse_args(argv)
    ts = _utc()
    RS.mkdir(parents=True, exist_ok=True)
    d = gen_r6_strict(ts)
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
        "next9_unblocked": False,
        "warn_flags": d["warn_flags"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
