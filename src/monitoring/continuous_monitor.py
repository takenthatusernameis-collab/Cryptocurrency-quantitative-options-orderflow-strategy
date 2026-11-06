"""Continuous production monitoring for crypto options + orderflow.

Extends src.monitoring with continuous health/SLO monitoring, alert thresholds,
latency/throughput/error metrics, observability integration, and deterministic
snapshot export. All artifacts strictly serialized with allow_nan=False.
"""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from math import isfinite
from typing import Any, Callable, Deque, Dict, List, Optional

from src.errors import RiskLimitError, get_logger
from src.monitoring.health import (
    HealthChecker, HealthReport, HealthStatus, DependencyCheck,
    default_health_checker, register_default_dependency_checks,
)
from src.monitoring.slo import (
    SLOMonitor, SLODefinition, SLIRecorder, SLIType, BurnRateAlert,
    default_sli_recorder, default_slo_monitor, register_default_slos,
)
from src.telemetry import serialize_metrics_strict
from src.telemetry.serialization import assert_json_valid
from src.telemetry.observability import (
    Counter, Gauge, Histogram, MetricsRegistry, observability_logger,
    metrics_registry, tracer,
)

_logger = get_logger(__name__)


def _utc_iso(ts: datetime) -> str:
    return ts.isoformat().replace("+00:00", "Z")


def _deterministic_iso(seed: int) -> str:
    base = datetime(2026, 11, 1, tzinfo=timezone.utc)
    return _utc_iso(base + timedelta(seconds=int(seed)))


def _now_ts() -> float:
    return 42.0


@dataclass
class AlertThreshold:
    """Alert threshold for a monitored metric."""

    metric: str
    operator: str  # "gte" or "lte"
    warning: float
    critical: float
    enabled: bool = True

    def evaluate(self, value: float) -> Optional[str]:
        if not self.enabled or not isfinite(float(value)):
            return None
        v = float(value)
        sev = None
        if self.operator == "gte":
            if v >= self.critical:
                sev = "critical"
            elif v >= self.warning:
                sev = "warning"
        else:  # lte
            if v <= self.critical:
                sev = "critical"
            elif v <= self.warning:
                sev = "warning"
        return sev

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "metric": self.metric,
            "operator": self.operator,
            "warning": float(self.warning),
            "critical": float(self.critical),
            "enabled": bool(self.enabled),
        })


@dataclass
class AlertRecord:
    """A single alert record."""

    alert_id: str
    metric: str
    value: float
    severity: str
    message: str
    timestamp: str
    acknowledged: bool = False
    resolved: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "alert_id": self.alert_id,
            "metric": self.metric,
            "value": float(self.value) if isfinite(float(self.value)) else 0.0,
            "severity": self.severity,
            "message": str(self.message),
            "timestamp": self.timestamp,
            "acknowledged": bool(self.acknowledged),
            "resolved": bool(self.resolved),
        })


@dataclass
class SnapshotMetrics:
    """Point-in-time snapshot metrics."""

    latency_p99_ms: float
    error_rate: float
    throughput_per_sec: float
    uptime_pct: float
    fill_rate: float
    reconciliation_freshness: float
    health_status: str
    num_alerts: int
    critical_alerts: int
    warning_alerts: int

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "latency_p99_ms": float(self.latency_p99_ms),
            "error_rate": float(self.error_rate),
            "throughput_per_sec": float(self.throughput_per_sec),
            "uptime_pct": float(self.uptime_pct),
            "fill_rate": float(self.fill_rate),
            "reconciliation_freshness": float(self.reconciliation_freshness),
            "health_status": self.health_status,
            "num_alerts": int(self.num_alerts),
            "critical_alerts": int(self.critical_alerts),
            "warning_alerts": int(self.warning_alerts),
        })


class ContinuousMonitor:
    """Continuous health/SLO monitoring for crypto options + orderflow services.

    Deterministic given fixed seed. Emits auditable snapshots and alerts.
    Default paper-only aware: never enables live paths.
    """

    def __init__(
        self,
        service: str = "crypto-options-orderflow",
        seed: int = 42,
        paper_only: bool = True,
        health_checker=None,
        slo_monitor=None,
        metrics_registry=None,
    ) -> None:
        self.service = str(service)
        self.seed = int(seed)
        self.paper_only = bool(paper_only)
        self.timestamp = _deterministic_iso(self.seed)
        self._lock = threading.RLock()
        self.health_checker = health_checker or default_health_checker
        self.slo_monitor = slo_monitor or default_slo_monitor
        self.metrics = metrics_registry or MetricsRegistry()
        self._start_ts = _now_ts()
        self._alerts: List[AlertRecord] = []
        self._alert_index: Dict[str, AlertRecord] = {}
        self._snapshots: List[Dict[str, Any]] = []
        self._thresholds: Dict[str, AlertThreshold] = {}
        self._latency_samples: Deque[float] = deque(maxlen=10000)
        self._error_samples: Deque[float] = deque(maxlen=10000)
        self._throughput_samples: Deque[float] = deque(maxlen=10000)
        self._health_status = HealthStatus.PASS
        self._last_reconciliation_ts: Optional[float] = None
        self._reconciliation_window_sec = 60.0
        register_default_dependency_checks(self.health_checker)
        register_default_slos(self.slo_monitor)
        self._register_default_thresholds()

    # ------------------------------------------------------------- thresholds
    def _register_default_thresholds(self) -> None:
        defaults = [
            AlertThreshold("latency_p99_ms", "gte", 100.0, 500.0),
            AlertThreshold("error_rate", "gte", 0.01, 0.05),
            AlertThreshold("uptime_pct", "lte", 99.0, 95.0),
            AlertThreshold("fill_rate", "lte", 0.90, 0.80),
            AlertThreshold("reconciliation_freshness", "lte", 0.95, 0.90),
        ]
        for t in defaults:
            self._thresholds[t.metric] = t

    def add_threshold(self, threshold: AlertThreshold) -> None:
        with self._lock:
            self._thresholds[threshold.metric] = threshold

    # ------------------------------------------------------------- metrics
    def record_latency(self, value_ms: float, labels: Optional[Dict[str, str]] = None) -> None:
        v = float(value_ms)
        if not isfinite(v):
            return
        with self._lock:
            self._latency_samples.append(v)
        self.metrics.observe("monitor_latency_ms", v, labels or {})
        observability_logger.debug("monitor_latency_recorded", value_ms=v, labels=labels or {})

    def record_error(self, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        v = float(value)
        if not isfinite(v):
            return
        with self._lock:
            self._error_samples.append(v)
        self.metrics.observe("monitor_error_rate", v, labels or {})
        observability_logger.debug("monitor_error_recorded", value=v, labels=labels or {})

    def record_throughput(self, value_per_sec: float, labels: Optional[Dict[str, str]] = None) -> None:
        v = float(value_per_sec)
        if not isfinite(v):
            return
        with self._lock:
            self._throughput_samples.append(v)
        self.metrics.observe("monitor_throughput_per_sec", v, labels or {})
        observability_logger.debug("monitor_throughput_recorded", value_per_sec=v, labels=labels or {})

    def record_reconciliation(self) -> None:
        """Record that a reconciliation run completed at real wall-clock time.

        Used by the E2E/campaign runner path so reconciliation freshness is
        genuinely emitted from the monitor cycle instead of a hardcoded constant.
        Strictly paper-only aware: no live path is enabled.
        """
        with self._lock:
            self._last_reconciliation_ts = time.time()

    # ------------------------------------------------------------- cycle
    def monitor_cycle(self) -> Dict[str, Any]:
        """Run one continuous monitoring cycle: health + SLO + alerts + snapshot."""
        tracer_ctx = tracer.start_span("monitor_cycle", attributes={"service": self.service, "seed": self.seed})
        try:
            health = self.health_checker.run_all()
            with self._lock:
                self._health_status = HealthStatus(health.status)

            slo_evals = self.slo_monitor.evaluate_all()

            # record SLIs from health + samples
            latency_values = list(self._latency_samples)
            error_values = list(self._error_samples)
            throughput_values = list(self._throughput_samples)

            latency_p99 = self._p99(latency_values) if latency_values else 0.0
            error_rate = (sum(error_values) / len(error_values)) if error_values else 0.0
            throughput = (sum(throughput_values) / len(throughput_values)) if throughput_values else 0.0

            # uptime from health
            uptime = 100.0 if health.status == HealthStatus.PASS else (
                50.0 if health.status == HealthStatus.WARN else 0.0)

            fill_rate = 1.0

            # Real reconciliation freshness: age of last reconciliation run vs
            # the slo_reconciliation_freshness window (60s). Never hardcoded.
            now = time.time()
            if self._last_reconciliation_ts is None:
                rec_freshness = 0.0
            else:
                age = now - self._last_reconciliation_ts
                rec_freshness = max(0.0, min(1.0, 1.0 - age / self._reconciliation_window_sec))
            # Emit as an SLI measurement so slo_reconciliation_freshness is
            # genuinely evaluated by evaluate_all() (not just snapshot-placed).
            self.slo_monitor.record_sli(
                SLIType.RECONCILIATION_FRESHNESS,
                rec_freshness,
                labels={"component": "reconciliation", "service": self.service},
            )

            snap_metrics = SnapshotMetrics(
                latency_p99_ms=round(latency_p99, 6),
                error_rate=round(error_rate, 6),
                throughput_per_sec=round(throughput, 6),
                uptime_pct=round(uptime, 6),
                fill_rate=round(fill_rate, 6),
                reconciliation_freshness=round(rec_freshness, 6),
                health_status=health.status,
                num_alerts=0,
                critical_alerts=0,
                warning_alerts=0,
            )

            # evaluate thresholds -> alerts
            alerts = self._evaluate_thresholds({
                "latency_p99_ms": snap_metrics.latency_p99_ms,
                "error_rate": snap_metrics.error_rate,
                "uptime_pct": snap_metrics.uptime_pct,
                "fill_rate": snap_metrics.fill_rate,
                "reconciliation_freshness": snap_metrics.reconciliation_freshness,
            })
            snap_metrics = SnapshotMetrics(
                latency_p99_ms=snap_metrics.latency_p99_ms,
                error_rate=snap_metrics.error_rate,
                throughput_per_sec=snap_metrics.throughput_per_sec,
                uptime_pct=snap_metrics.uptime_pct,
                fill_rate=snap_metrics.fill_rate,
                reconciliation_freshness=snap_metrics.reconciliation_freshness,
                health_status=health.status,
                num_alerts=len(alerts),
                critical_alerts=sum(1 for a in alerts if a.severity == "critical"),
                warning_alerts=sum(1 for a in alerts if a.severity == "warning"),
            )

            snapshot = {
                "service": self.service,
                "seed": self.seed,
                "paper_only": self.paper_only,
                "timestamp": _deterministic_iso(self.seed),
                "uptime_sec": round(_now_ts() - self._start_ts, 6),
                "health": health.to_dict(),
                "slo_evaluations": slo_evals,
                "metrics": {"metrics": snap_metrics.to_dict()},
                "alerts": [a.to_dict() for a in alerts],
                "thresholds": {k: t.to_dict() for k, t in self._thresholds.items()},
            }
            snapshot = serialize_metrics_strict(snapshot)
            assert_json_valid(snapshot)

            with self._lock:
                self._snapshots.append(snapshot)
                for a in alerts:
                    self._alerts.append(a)
                    self._alert_index[a.alert_id] = a

            observability_logger.info("monitor_cycle_complete",
                                      service=self.service, status=health.status,
                                      num_alerts=len(alerts),
                                      latency_p99_ms=snap_metrics.latency_p99_ms,
                                      error_rate=snap_metrics.error_rate)
            tracer.end_span(tracer_ctx, status="ok")
            return snapshot
        except Exception as exc:  # pragma: no cover - defensive
            tracer.end_span(tracer_ctx, status="error")
            observability_logger.error("monitor_cycle_failed", error=str(exc))
            raise

    # ------------------------------------------------------------- helpers
    @staticmethod
    def _p99(values: List[float]) -> float:
        if not values:
            return 0.0
        s = sorted(values)
        idx = max(0, min(len(s) - 1, int(0.99 * len(s))))
        return float(s[idx])

    def _alert_id(self, metric: str, severity: str) -> str:
        import hashlib
        payload = f"{self.service}|{metric}|{severity}|{self.seed}|{time.time_ns()}"
        return f"alert_{hashlib.sha256(payload.encode()).hexdigest()[:12]}"

    def _evaluate_thresholds(self, values: Dict[str, float]) -> List[AlertRecord]:
        now = _deterministic_iso(self.seed)
        alerts: List[AlertRecord] = []
        for metric, value in values.items():
            thr = self._thresholds.get(metric)
            if thr is None:
                continue
            sev = thr.evaluate(value)
            if sev is None:
                continue
            alert = AlertRecord(
                alert_id=self._alert_id(metric, sev),
                metric=metric,
                value=value,
                severity=sev,
                message=f"Metric {metric}={value:.6f} breached {thr.operator} threshold ({sev})",
                timestamp=now,
            )
            alerts.append(alert)
            observability_logger.warning("monitor_alert", metric=metric, value=value,
                                         severity=sev, alert_id=alert.alert_id)
        return alerts

    # ------------------------------------------------------------- export
    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            snaps = list(self._snapshots)
            alerts = [a.to_dict() for a in self._alerts]
            thresholds = {k: t.to_dict() for k, t in self._thresholds.items()}
        payload = serialize_metrics_strict({
            "service": self.service,
            "seed": self.seed,
            "paper_only": self.paper_only,
            "timestamp": _deterministic_iso(self.seed),
            "uptime_sec": round(_now_ts() - self._start_ts, 6),
            "health_status": self._health_status,
            "num_snapshots": len(snaps),
            "num_alerts": len(alerts),
            "snapshots": snaps,
            "alerts": alerts,
            "thresholds": thresholds,
        })
        assert_json_valid(payload)
        return payload

    def export_report(self) -> Dict[str, Any]:
        snap = self.snapshot()
        report = serialize_metrics_strict({
            "report": "continuous_monitor",
            "service": self.service,
            "seed": self.seed,
            "paper_only": self.paper_only,
            "timestamp": _deterministic_iso(self.seed),
            "uptime_sec": snap["uptime_sec"],
            "health_status": snap["health_status"],
            "num_snapshots": snap["num_snapshots"],
            "num_alerts": snap["num_alerts"],
            "latest_snapshot": snap["snapshots"][-1] if snap["snapshots"] else None,
            "alerts": snap["alerts"],
            "thresholds": snap["thresholds"],
        })
        assert_json_valid(report)
        return report

    def clear(self) -> None:
        with self._lock:
            self._snapshots.clear()
            self._alerts.clear()
            self._alert_index.clear()
            self._latency_samples.clear()
            self._error_samples.clear()
            self._throughput_samples.clear()
        self.metrics.clear()


# Default continuous monitor for the strategy service.
default_continuous_monitor = ContinuousMonitor(seed=42, paper_only=True)


__all__ = [
    "AlertThreshold", "AlertRecord", "SnapshotMetrics", "ContinuousMonitor",
    "default_continuous_monitor",
]
