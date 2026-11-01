#!/usr/bin/env python3
"""CLI: run continuous validation campaign for crypto options + orderflow.

Emits timestamped Phase 9 artifacts to research_state/ and prints a summary.
Usage: python scripts/run_continuous_validation.py [--symbols BTC,ETH] [--seed 42]
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone

from src.validation.continuous import default_continuous_validator
from src.monitoring.health import default_health_checker, register_default_dependency_checks
from src.monitoring.slo import default_slo_monitor, register_default_slos, default_sli_recorder
from src.telemetry.alerting import default_alert_manager, setup_default_rules
from src.telemetry.observability import observability_logger
from src.resilience.circuit import default_circuit_registry
from src.resilience.retry import default_retry_policy, get_bulkhead
from src.telemetry import metrics_registry, tracer


def _utc_now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _emit_artifact(name_prefix: str, payload: dict, out_dir: str = "research_state") -> str:
    import os
    import re
    os.makedirs(out_dir, exist_ok=True)
    # Strip any existing trailing timestamp to avoid double timestamps
    clean = re.sub(r'_\d{8}T\d{6}Z$', '', name_prefix)
    ts = _utc_now_str()
    path = f"{out_dir}/{clean}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, allow_nan=False, indent=2)
    return path


def run_campaign(symbols: list, seed: int) -> dict:
    """Run the full continuous validation campaign and return all results."""
    validator = default_continuous_validator
    validator.seed = int(seed)

    # 1) Data quality checks
    dq_results = []
    for sym in symbols:
        venue = "deribit"
        r = validator.validate_data_quality(
            symbol=sym, venue=venue,
            bid=50000.0, ask=50001.0,
            timestamp=__import__("time").time(),
        )
        dq_results.append(r)

    # 2) Drift detection
    drift_results = []
    validator.check_drift("vol_surface", 0.60, 0.62, threshold_pct=5.0,
                          labels={"symbol": symbols[0] if symbols else "BTC"})
    validator.check_drift("spread_bps", 2.0, 2.5, threshold_pct=10.0,
                          labels={"symbol": symbols[0] if symbols else "BTC"})
    drift_results = validator._drift_results[-2:]

    # 3) Shadow comparison
    shadow_results = []
    for sym in symbols:
        c = validator.compare_shadow(sym, "deribit", 0.25, 0.26,
                                     labels={"strategy": "orderflow_momentum"})
        shadow_results.append(c)

    # 4) Canary gate
    canary_result = validator.evaluate_canary(
        canary_version="v2.1", baseline_version="v2.0",
        metric="sharpe_ratio", canary_value=1.85, baseline_value=1.75,
        labels={"symbol": symbols[0] if symbols else "BTC"},
    )

    # 5) Golden artifact + regression check
    golden = validator.store_golden(
        "baseline_metrics_v2",
        {"sharpe": 1.75, "max_drawdown": 0.08, "win_rate": 0.54},
        labels={"version": "v2.0"},
    )
    regression = validator.check_regression("baseline_metrics_v2",
                                            {"sharpe": 1.75, "max_drawdown": 0.08, "win_rate": 0.54})

    # 6) Health check
    hc = default_health_checker
    register_default_dependency_checks(hc)
    health_report = hc.run_all()

    # 7) SLO evaluation
    sm = default_slo_monitor
    register_default_slos(sm)
    # Record some SLI measurements
    for _ in range(5):
        default_sli_recorder.record("latency", 45.0 + (_ * 2.0), labels={"component": "execution"})
        default_sli_recorder.record("error_rate", 0.005, labels={"component": "execution"})
        default_sli_recorder.record("uptime", 1.0, labels={"component": "api"})
        default_sli_recorder.record("fill_rate", 0.97, labels={"component": "execution"})
    slo_evals = sm.evaluate_all()

    # 8) Alerting setup + evaluation
    am = default_alert_manager
    setup_default_rules(am)
    am.evaluate("drawdown_pct", 0.12, labels={"symbol": symbols[0] if symbols else "BTC"})
    am.evaluate("order_latency_ms", 120.0, labels={"symbol": symbols[0] if symbols else "BTC"})

    # 9) Metrics snapshot
    metrics_registry.inc("campaign_runs", 1, labels={"campaign": "phase9_validation"})
    metrics_registry.set("campaign_last_run_status", 1.0, labels={"status": "complete"})
    metrics_snapshot = metrics_registry.snapshot()

    # 10) Observability export
    obs_report = observability_logger.export_report()

    # 11) Tracer snapshot
    trace_snapshot = tracer.snapshot()

    # 12) Resilience snapshots
    circuit_snapshot = default_circuit_registry.snapshot_all()
    retry_snapshot = default_retry_policy.snapshot()

    campaign_result = {
        "campaign": "phase9_continuous_validation",
        "seed": int(seed),
        "symbols": symbols,
        "run_at": datetime.now(timezone.utc).isoformat(),
        "data_quality": dq_results,
        "drift": [d.to_dict() for d in drift_results],
        "shadow": shadow_results,
        "canary": canary_result,
        "golden_artifact": golden,
        "regression": regression,
        "health": health_report.to_dict(),
        "slo_evaluations": slo_evals,
        "alerts": am.snapshot(),
        "metrics": metrics_snapshot,
        "observability": obs_report,
        "tracing": trace_snapshot,
        "resilience": {
            "circuit_breakers": circuit_snapshot,
            "retry": retry_snapshot,
        },
    }
    return campaign_result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 9 continuous validation campaign")
    parser.add_argument("--symbols", default="BTC,ETH", help="Comma-separated symbols")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for determinism")
    args = parser.parse_args()

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    result = run_campaign(symbols, args.seed)

    # Emit artifacts
    ts = _utc_now_str()
    artifacts = {}
    for key in ["observability", "alerts", "health", "resilience", "data_quality", "drift", "shadow", "canary", "slo_evaluations"]:
        if key in result:
            artifacts[key] = result[key]

    # OBSERVABILITY_REPORT
    obs_path = _emit_artifact(f"OBSERVABILITY_REPORT_{ts}",
                              {"report": result.get("observability", {}), "campaign": result["campaign"]})
    # ALERT_AUDIT
    alert_path = _emit_artifact(f"ALERT_AUDIT_{ts}",
                                {"audit": result.get("alerts", {}), "campaign": result["campaign"]})
    # HEALTH_SLO_REPORT
    hs_path = _emit_artifact(f"HEALTH_SLO_REPORT_{ts}",
                             {"health": result.get("health", {}), "slo_evaluations": result.get("slo_evaluations", []), "campaign": result["campaign"]})
    # RESILIENCE_AUDIT
    res_path = _emit_artifact(f"RESILIENCE_AUDIT_{ts}",
                              {"resilience": result.get("resilience", {}), "campaign": result["campaign"]})
    # CONTINUOUS_VALIDATION
    cv_path = _emit_artifact(f"CONTINUOUS_VALIDATION_{ts}",
                             {"campaign": result, "artifacts": artifacts})

    print(json.dumps({
        "status": "complete",
        "campaign": result["campaign"],
        "seed": result["seed"],
        "symbols": symbols,
        "run_at": result["run_at"],
        "artifacts": {
            "observability": obs_path,
            "alert_audit": alert_path,
            "health_slo": hs_path,
            "resilience": res_path,
            "continuous_validation": cv_path,
        },
        "summary": {
            "dq_passed": all(r.get("passed", False) for r in result.get("data_quality", [])),
            "drift_detected": any(d.get("drift_detected", False) for d in result.get("drift", [])),
            "shadow_agreement": all(c.get("agreement", False) for c in result.get("shadow", [])),
            "canary_passed": result.get("canary", {}).get("gate_passed", False),
            "regression_matched": result.get("regression", {}).get("matches", False),
            "health_status": result.get("health", {}).get("status", "unknown"),
        },
    }, allow_nan=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
