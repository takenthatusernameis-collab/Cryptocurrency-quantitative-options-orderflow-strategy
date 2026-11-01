"""SLO/SLI tracking and burn-rate alerts for crypto options + orderflow.

SLO definitions (latency/error rate/uptime/reconciliation freshness),
SLI computation, burn-rate alerts, status page model. Strict allow_nan=False
serialization on all artifacts. Deterministic in tests.
"""

from __future__ import annotations

import math
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Callable, Deque, Dict, List, Optional

from ..telemetry import serialize_metrics_strict
from ..telemetry.observability import observability_logger, redact
from .health import HealthStatus


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_ts() -> float:
    return time.time()


class SLIType(str):
    LATENCY = "latency"
    ERROR_RATE = "error_rate"
    UPTIME = "uptime"
    RECONCILIATION_FRESHNESS = "reconciliation_freshness"
    FILL_RATE = "fill_rate"


@dataclass
class SLIMeasurement:
    """A single SLI measurement point."""

    sli_type: str
    value: float
    timestamp: str
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "sli_type": self.sli_type,
            "value": float(self.value) if isfinite(float(self.value)) else 0.0,
            "timestamp": self.timestamp,
            "labels": dict(self.labels),
        })


@dataclass
class SLODefinition:
    """Service Level Objective definition."""

    slo_id: str
    name: str
    sli_type: str
    target: float  # e.g. 0.999 for 99.9%
    comparison: str  # "gte" or "lte"
    window_sec: float
    labels: Dict[str, str] = field(default_factory=dict)
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "slo_id": self.slo_id,
            "name": self.name,
            "sli_type": self.sli_type,
            "target": float(self.target) if isfinite(float(self.target)) else 0.0,
            "comparison": self.comparison,
            "window_sec": float(self.window_sec) if isfinite(float(self.window_sec)) else 0.0,
            "labels": dict(self.labels),
            "enabled": bool(self.enabled),
        })


@dataclass
class SLOEvaluation:
    """Result of evaluating an SLO over its window."""

    slo_id: str
    name: str
    sli_type: str
    target: float
    current_value: float
    met: bool
    error_budget_remaining: float  # 0.0 to 1.0
    window_sec: float
    num_measurements: int
    evaluated_at: str
    labels: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "slo_id": self.slo_id,
            "name": self.name,
            "sli_type": self.sli_type,
            "target": float(self.target) if isfinite(float(self.target)) else 0.0,
            "current_value": float(self.current_value) if isfinite(float(self.current_value)) else 0.0,
            "met": bool(self.met),
            "error_budget_remaining": float(self.error_budget_remaining) if isfinite(float(self.error_budget_remaining)) else 0.0,
            "window_sec": float(self.window_sec) if isfinite(float(self.window_sec)) else 0.0,
            "num_measurements": int(self.num_measurements),
            "evaluated_at": self.evaluated_at,
            "labels": dict(self.labels),
        })


@dataclass
class BurnRateAlert:
    """Burn-rate alert for an SLO."""

    alert_id: str
    slo_id: str
    burn_rate: float  # multiple of expected burn
    window_sec: float
    severity: str
    message: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "alert_id": self.alert_id,
            "slo_id": self.slo_id,
            "burn_rate": float(self.burn_rate) if isfinite(float(self.burn_rate)) else 0.0,
            "window_sec": float(self.window_sec) if isfinite(float(self.window_sec)) else 0.0,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp,
        })


@dataclass
class StatusPage:
    """Aggregated status page model."""

    overall_status: str
    services: List[Dict[str, Any]] = field(default_factory=list)
    slo_evaluations: List[Dict[str, Any]] = field(default_factory=list)
    generated_at: str = field(default_factory=_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "overall_status": self.overall_status,
            "services": self.services,
            "slo_evaluations": self.slo_evaluations,
            "generated_at": self.generated_at,
        })


class SLIRecorder:
    """Records SLI measurements over time windows."""

    def __init__(self, max_points: int = 10000):
        self.max_points = int(max_points)
        self._lock = threading.RLock()
        self._measurements: Dict[str, Deque[SLIMeasurement]] = {}

    def record(self, sli_type: str, value: float,
               labels: Optional[Dict[str, str]] = None) -> None:
        v = float(value) if isfinite(float(value)) else float("nan")
        if not isfinite(v):
            return
        m = SLIMeasurement(
            sli_type=str(sli_type),
            value=v,
            timestamp=_now_iso(),
            labels=dict(labels or {}),
        )
        with self._lock:
            dq = self._measurements.setdefault(str(sli_type), deque(maxlen=self.max_points))
            dq.append(m)

    def get_measurements(self, sli_type: str,
                         since_ts: Optional[float] = None) -> List[SLIMeasurement]:
        with self._lock:
            dq = self._measurements.get(str(sli_type), deque())
            items = list(dq)
        if since_ts is None:
            return items
        return [m for m in items
                if _parse_ts(m.timestamp) >= since_ts]

    def clear(self) -> None:
        with self._lock:
            self._measurements.clear()


def _parse_ts(ts: str) -> float:
    try:
        from datetime import datetime as _dt
        return _dt.fromisoformat(ts).timestamp()
    except Exception:
        return 0.0


class SLOMonitor:
    """Evaluates SLOs over sliding windows and emits burn-rate alerts."""

    def __init__(self, sli_recorder: Optional[SLIRecorder] = None):
        self._lock = threading.RLock()
        self._slo_recorder = sli_recorder or SLIRecorder()
        self._slo_defs: Dict[str, SLODefinition] = {}
        self._evaluations: List[SLOEvaluation] = []
        self._burn_alerts: List[BurnRateAlert] = []
        self._burn_alert_index: Dict[str, BurnRateAlert] = {}

    def add_slo(self, slo: SLODefinition) -> None:
        with self._lock:
            self._slo_defs[slo.slo_id] = slo
        observability_logger.debug("slo_added", slo_id=slo.slo_id, name=slo.name,
                                   sli_type=slo.sli_type, target=slo.target)

    def remove_slo(self, slo_id: str) -> bool:
        with self._lock:
            if slo_id in self._slo_defs:
                del self._slo_defs[slo_id]
                return True
        return False

    def record_sli(self, sli_type: str, value: float,
                   labels: Optional[Dict[str, str]] = None) -> None:
        self._slo_recorder.record(sli_type, value, labels)

    def evaluate_slo(self, slo_id: str) -> Optional[SLOEvaluation]:
        with self._lock:
            slo = self._slo_defs.get(slo_id)
        if slo is None or not slo.enabled:
            return None
        window_start_ts = _now_ts() - slo.window_sec
        measurements = self._slo_recorder.get_measurements(slo.sli_type, since_ts=window_start_ts)
        if not measurements:
            eval_result = SLOEvaluation(
                slo_id=slo.slo_id, name=slo.name, sli_type=slo.sli_type,
                target=slo.target, current_value=0.0, met=False,
                error_budget_remaining=1.0, window_sec=slo.window_sec,
                num_measurements=0, evaluated_at=_now_iso(), labels=dict(slo.labels),
            )
        else:
            values = [m.value for m in measurements]
            if slo.sli_type in (SLIType.LATENCY, SLIType.ERROR_RATE):
                current_value = sum(values) / len(values)
            elif slo.sli_type == SLIType.UPTIME:
                good = sum(1 for v in values if v >= 0.999)
                current_value = good / len(values)
            elif slo.sli_type == SLIType.RECONCILIATION_FRESHNESS:
                current_value = sum(values) / len(values)
            elif slo.sli_type == SLIType.FILL_RATE:
                current_value = sum(values) / len(values)
            else:
                current_value = sum(values) / len(values)
            if not isfinite(current_value):
                current_value = 0.0
            if slo.comparison == "gte":
                met = current_value >= slo.target
            else:
                met = current_value <= slo.target
            error_budget = max(0.0, min(1.0, 1.0 - (current_value / slo.target))) if slo.target > 0 else 1.0
            if met:
                error_budget = max(error_budget, 0.5)
            eval_result = SLOEvaluation(
                slo_id=slo.slo_id, name=slo.name, sli_type=slo.sli_type,
                target=slo.target, current_value=float(current_value),
                met=bool(met), error_budget_remaining=float(error_budget),
                window_sec=slo.window_sec, num_measurements=len(measurements),
                evaluated_at=_now_iso(), labels=dict(slo.labels),
            )
        with self._lock:
            self._evaluations.append(eval_result)
        observability_logger.info("slo_evaluated", slo_id=slo.slo_id, name=slo.name,
                                  met=eval_result.met,
                                  current_value=eval_result.current_value,
                                  error_budget=eval_result.error_budget_remaining)
        return eval_result

    def evaluate_all(self) -> List[Dict[str, Any]]:
        with self._lock:
            slo_ids = list(self._slo_defs.keys())
        results = []
        for sid in slo_ids:
            ev = self.evaluate_slo(sid)
            if ev is not None:
                results.append(ev.to_dict())
        return results

    def check_burn_rate(self, slo_id: str,
                        expected_burn_per_sec: float,
                        alert_threshold_multiplier: float = 2.0) -> Optional[BurnRateAlert]:
        """Check if error budget is burning faster than expected."""
        ev = self.evaluate_slo(slo_id)
        if ev is None or ev.error_budget_remaining <= 0:
            return None
        elapsed = ev.window_sec
        if elapsed <= 0:
            return None
        expected_remaining = 1.0 - (expected_burn_per_sec * elapsed)
        expected_remaining = max(0.0, min(1.0, expected_remaining))
        if expected_remaining <= 0:
            return None
        burn_rate = (expected_remaining - ev.error_budget_remaining) / expected_remaining if expected_remaining > 0 else 0.0
        if burn_rate <= 0:
            return None
        severity = "info"
        if burn_rate >= alert_threshold_multiplier * 10:
            severity = "critical"
        elif burn_rate >= alert_threshold_multiplier * 5:
            severity = "error"
        elif burn_rate >= alert_threshold_multiplier * 2:
            severity = "warning"
        if severity == "info":
            return None
        alert = BurnRateAlert(
            alert_id=f"burn_{slo_id}_{int(_now_ts())}",
            slo_id=slo.slo_id,
            burn_rate=float(burn_rate) if isfinite(float(burn_rate)) else 0.0,
            window_sec=ev.window_sec,
            severity=severity,
            message=f"SLO {slo.name} error budget burning at {burn_rate:.2f}x expected rate",
            timestamp=_now_iso(),
        )
        with self._lock:
            self._burn_alerts.append(alert)
            self._burn_alert_index[alert.alert_id] = alert
        observability_logger.warning("burn_rate_alert", slo_id=slo.slo_id,
                                     burn_rate=burn_rate, severity=severity)
        return alert

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            evals = [e.to_dict() for e in self._evaluations]
            burns = [b.to_dict() for b in self._burn_alerts]
            defs = [s.to_dict() for s in self._slo_defs.values()]
        return serialize_metrics_strict({
            "num_slos": len(self._slo_defs),
            "num_evaluations": len(evals),
            "num_burn_alerts": len(burns),
            "slo_definitions": defs,
            "evaluations": evals,
            "burn_alerts": burns,
            "timestamp": _now_iso(),
        })

    def clear(self) -> None:
        with self._lock:
            self._evaluations.clear()
            self._burn_alerts.clear()
            self._burn_alert_index.clear()
            self._slo_defs.clear()


class StatusPageModel:
    """Builds a status page from health checks and SLO evaluations."""

    def __init__(self, health_checker=None, slo_monitor=None):
        self.health_checker = health_checker
        self.slo_monitor = slo_monitor

    def generate(self) -> Dict[str, Any]:
        services: List[Dict[str, Any]] = []
        overall = HealthStatus.PASS  # type: ignore[attr-defined]
        if self.health_checker is not None:
            health = self.health_checker.run_all()
            services.append({
                "service": health.service,
                "status": health.status,
                "version": health.version,
                "uptime_sec": health.uptime_sec,
                "checked_at": health.checked_at,
                "checks": [c.to_dict() for c in health.checks],
            })
            overall = HealthStatus.aggregate([health.status])  # type: ignore[attr-defined]
        slo_evals: List[Dict[str, Any]] = []
        if self.slo_monitor is not None:
            slo_evals = self.slo_monitor.evaluate_all()
            for ev in slo_evals:
                if not ev.get("met", False):
                    overall = HealthStatus.WARN  # type: ignore[attr-defined]
        page = StatusPage(
            overall_status=overall,
            services=services,
            slo_evaluations=slo_evals,
        )
        return page.to_dict()


# Default SLO monitor with standard crypto options + orderflow SLOs.
default_sli_recorder = SLIRecorder()
default_slo_monitor = SLOMonitor(sli_recorder=default_sli_recorder)


def register_default_slos(monitor: Optional[SLOMonitor] = None) -> SLOMonitor:
    """Register standard SLOs for crypto options + orderflow trading."""
    m = monitor or default_slo_monitor
    slos = [
        SLODefinition("slo_latency_p99", "Order Latency p99", SLIType.LATENCY,
                      target=100.0, comparison="lte", window_sec=300.0,
                      labels={"component": "execution"}),
        SLODefinition("slo_error_rate", "Execution Error Rate", SLIType.ERROR_RATE,
                      target=0.01, comparison="lte", window_sec=300.0,
                      labels={"component": "execution"}),
        SLODefinition("slo_uptime", "Service Uptime", SLIType.UPTIME,
                      target=0.999, comparison="gte", window_sec=3600.0,
                      labels={"component": "api"}),
        SLODefinition("slo_reconciliation_freshness", "Reconciliation Freshness",
                      SLIType.RECONCILIATION_FRESHNESS, target=0.99,
                      comparison="gte", window_sec=60.0,
                      labels={"component": "reconciliation"}),
        SLODefinition("slo_fill_rate", "Order Fill Rate", SLIType.FILL_RATE,
                      target=0.95, comparison="gte", window_sec=300.0,
                      labels={"component": "execution"}),
    ]
    for slo in slos:
        m.add_slo(slo)
    return m


__all__ = [
    "SLIType", "SLIMeasurement", "SLODefinition", "SLOEvaluation",
    "BurnRateAlert", "StatusPage", "SLIRecorder", "SLOMonitor",
    "StatusPageModel", "default_sli_recorder", "default_slo_monitor",
    "register_default_slos",
]
