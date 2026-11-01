"""Production observability core for crypto options + orderflow.

Structured JSON logging with trace/correlation IDs, log levels, PII/secret
redaction integration, metrics registry (counters/gauges/histograms), and
exporter interfaces (Prometheus/OpenTelemetry compatible). Deterministic
in tests: fixed seeds, no wall-clock dependence where avoidable, strict
allow_nan=False serialization on all emitted artifacts.
"""

from __future__ import annotations

import hashlib
import json
import math
import threading
import time
from collections import OrderedDict, deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Set, Union

from ..errors import SerializationError, get_logger
from .serialization import serialize_metrics_strict

_logger = get_logger(__name__)

# Secret-like keys to redact in structured logs.
REDACT_KEYS: Set[str] = {
    "api_key", "api_secret", "secret", "passphrase", "password", "token",
    "private_key", "access_token", "refresh_token", "authorization",
    "deribit_api_key", "deribit_api_secret", "okx_api_key", "okx_api_secret",
    "okx_passphrase", "binance_api_key", "binance_api_secret",
}

REDACT_VALUE = "[REDACTED]"


def _redact_value(key: str, value: Any) -> Any:
    if isinstance(key, str) and key.lower() in REDACT_KEYS:
        return REDACT_VALUE
    if isinstance(value, dict):
        return {k: _redact_value(k, v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(_redact_value("item", v) for v in value)
    return value


def redact(obj: Any) -> Any:
    """Redact secret-like keys from ``obj`` recursively."""
    return _redact_value("root", obj)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_trace_id() -> str:
    payload = f"{time.time_ns()}|{threading.get_ident()}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"trace_{digest}"


def _make_correlation_id() -> str:
    payload = f"corr|{time.time_ns()}|{threading.get_ident()}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"corr_{digest}"


class LogLevel(str):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    _RANK = {DEBUG: 10, INFO: 20, WARNING: 30, ERROR: 40, CRITICAL: 50}

    @classmethod
    def rank(cls, level: str) -> int:
        return cls._RANK.get(level, 20)


@dataclass
class LogEntry:
    """A single structured log entry, deterministic and serializable."""

    level: str
    message: str
    timestamp: str
    logger: str
    trace_id: Optional[str] = None
    correlation_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "ts": self.timestamp,
            "level": self.level,
            "logger": self.logger,
            "msg": self.message,
            "trace_id": self.trace_id,
            "correlation_id": self.correlation_id,
            "context": redact(self.context),
        })


class StructuredLogger:
    """JSON-line structured logger with trace/correlation ID support.

    Wraps the project StructuredLogger (errors.get_logger) and adds
    trace/correlation propagation plus deterministic redaction.
    """

    def __init__(self, name: str):
        self.name = name
        self._base = get_logger(name)
        self._trace_id: Optional[str] = None
        self._correlation_id: Optional[str] = None
        self._lock = threading.Lock()
        self.entries: List[LogEntry] = []

    # ------------------------------------------------------------------ scope
    def set_trace_id(self, trace_id: Optional[str]) -> None:
        self._trace_id = trace_id

    def set_correlation_id(self, correlation_id: Optional[str]) -> None:
        self._correlation_id = correlation_id

    def new_trace(self) -> str:
        tid = _make_trace_id()
        self._trace_id = tid
        return tid

    def new_correlation(self) -> str:
        cid = _make_correlation_id()
        self._correlation_id = cid
        return cid

    def clear_scope(self) -> None:
        self._trace_id = None
        self._correlation_id = None

    # ------------------------------------------------------------------ emit
    def _emit(self, level: str, msg: str, **ctx: Any) -> None:
        with self._lock:
            entry = LogEntry(
                level=level,
                message=msg,
                timestamp=_now_iso(),
                logger=self.name,
                trace_id=self._trace_id,
                correlation_id=self._correlation_id,
                context=dict(ctx),
            )
            self.entries.append(entry)
        redacted_ctx = redact(ctx)
        self._base._emit(level, msg, **redacted_ctx)

    def debug(self, msg: str, **ctx: Any) -> None:
        self._emit(LogLevel.DEBUG, msg, **ctx)

    def info(self, msg: str, **ctx: Any) -> None:
        self._emit(LogLevel.INFO, msg, **ctx)

    def warning(self, msg: str, **ctx: Any) -> None:
        self._emit(LogLevel.WARNING, msg, **ctx)

    def error(self, msg: str, **ctx: Any) -> None:
        self._emit(LogLevel.ERROR, msg, **ctx)

    def critical(self, msg: str, **ctx: Any) -> None:
        self._emit(LogLevel.CRITICAL, msg, **ctx)

    def exception(self, msg: str, exc: BaseException, **ctx: Any) -> None:
        self._emit(LogLevel.ERROR, msg, exc=exc, **ctx)

    # ------------------------------------------------------------------ export
    def get_entries(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [e.to_dict() for e in self.entries]

    def clear_entries(self) -> None:
        with self._lock:
            self.entries.clear()

    def export_report(self) -> Dict[str, Any]:
        with self._lock:
            entries = [e.to_dict() for e in self.entries]
        return serialize_metrics_strict({
            "logger": self.name,
            "num_entries": len(entries),
            "entries": entries,
            "trace_id": self._trace_id,
            "correlation_id": self._correlation_id,
        })


# Module-level default observability logger.
observability_logger = StructuredLogger("observability")


# --------------------------------------------------------------------------- Metrics

class MetricType(str):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class Counter:
    """Monotonically increasing counter."""

    name: str
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)

    def inc(self, amount: float = 1.0) -> None:
        amount = float(amount)
        if not isfinite(amount):
            return
        self.value += amount

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "type": MetricType.COUNTER,
            "name": self.name,
            "value": float(self.value) if isfinite(float(self.value)) else 0.0,
            "labels": dict(self.labels),
        })


@dataclass
class Gauge:
    """Point-in-time gauge value."""

    name: str
    value: float = 0.0
    labels: Dict[str, str] = field(default_factory=dict)

    def set(self, value: float) -> None:
        v = float(value)
        if isfinite(v):
            self.value = v

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "type": MetricType.GAUGE,
            "name": self.name,
            "value": float(self.value) if isfinite(float(self.value)) else 0.0,
            "labels": dict(self.labels),
        })


@dataclass
class Histogram:
    """Distribution histogram with fixed buckets."""

    name: str
    buckets: List[float] = field(default_factory=list)
    counts: List[int] = field(default_factory=list)
    sum: float = 0.0
    count: int = 0
    labels: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.buckets:
            self.buckets = [0.001, 0.01, 0.1, 1.0, 10.0, 100.0, 1000.0]
        if not self.counts:
            self.counts = [0] * (len(self.buckets) + 1)

    def observe(self, value: float) -> None:
        v = float(value)
        if not isfinite(v):
            return
        self.sum += v
        self.count += 1
        idx = 0
        while idx < len(self.buckets) and v > self.buckets[idx]:
            idx += 1
        self.counts[idx] += 1

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "type": MetricType.HISTOGRAM,
            "name": self.name,
            "buckets": [float(b) for b in self.buckets],
            "counts": [int(c) for c in self.counts],
            "sum": float(self.sum) if isfinite(float(self.sum)) else 0.0,
            "count": int(self.count),
            "labels": dict(self.labels),
        })


class MetricsRegistry:
    """Thread-safe metrics registry with counters/gauges/histograms.

    All metric values are finite-checked. Deterministic given fixed inputs.
    Supports labeled metrics and snapshot export for Prometheus-compatible
    text exposition or OpenTelemetry-compatible JSON.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._counters: Dict[str, Counter] = OrderedDict()
        self._gauges: Dict[str, Gauge] = OrderedDict()
        self._histograms: Dict[str, Histogram] = OrderedDict()

    def _key(self, name: str, labels: Dict[str, str]) -> str:
        if not labels:
            return name
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}"

    def counter(self, name: str, labels: Optional[Dict[str, str]] = None) -> Counter:
        labels = labels or {}
        key = self._key(name, labels)
        with self._lock:
            if key not in self._counters:
                self._counters[key] = Counter(name=name, labels=dict(labels))
            return self._counters[key]

    def gauge(self, name: str, labels: Optional[Dict[str, str]] = None) -> Gauge:
        labels = labels or {}
        key = self._key(name, labels)
        with self._lock:
            if key not in self._gauges:
                self._gauges[key] = Gauge(name=name, labels=dict(labels))
            return self._gauges[key]

    def histogram(self, name: str, buckets: Optional[List[float]] = None,
                  labels: Optional[Dict[str, str]] = None) -> Histogram:
        labels = labels or {}
        key = self._key(name, labels)
        with self._lock:
            if key not in self._histograms:
                self._histograms[key] = Histogram(name=name,
                                                  buckets=list(buckets) if buckets else None,
                                                  labels=dict(labels))
            return self._histograms[key]

    def inc(self, name: str, amount: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        self.counter(name, labels).inc(amount)

    def set(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        self.gauge(name, labels).set(value)

    def observe(self, name: str, value: float, labels: Optional[Dict[str, str]] = None) -> None:
        self.histogram(name, labels=labels).observe(value)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            counters = [c.to_dict() for c in self._counters.values()]
            gauges = [g.to_dict() for g in self._gauges.values()]
            histograms = [h.to_dict() for h in self._histograms.values()]
        return serialize_metrics_strict({
            "counters": counters,
            "gauges": gauges,
            "histograms": histograms,
            "timestamp": _now_iso(),
        })

    def clear(self) -> None:
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()

    def to_prometheus_text(self) -> str:
        """Prometheus-compatible text exposition format."""
        lines: List[str] = []
        with self._lock:
            for c in self._counters.values():
                labels = "".join(f'{k}="{v}"' for k, v in sorted(c.labels.items()))
                lines.append(f"{c.name}{{{labels}}} {c.value}")
            for g in self._gauges.values():
                labels = "".join(f'{k}="{v}"' for k, v in sorted(g.labels.items()))
                lines.append(f"{g.name}{{{labels}}} {g.value}")
            for h in self._histograms.values():
                labels = "".join(f'{k}="{v}"' for k, v in sorted(h.labels.items()))
                for i, (b, cnt) in enumerate(zip(h.buckets, h.counts)):
                    le = float("inf") if i >= len(h.buckets) else b
                    lines.append(f'{h.name}_bucket{{{labels},le="{le}"}} {cnt}')
                lines.append(f'{h.name}_sum{{{labels}}} {h.sum}')
                lines.append(f'{h.name}_count{{{labels}}} {h.count}')
        return "\n".join(lines) + ("\n" if lines else "")

    def to_opentelemetry_json(self) -> Dict[str, Any]:
        """OpenTelemetry-compatible JSON export."""
        with self._lock:
            metrics: List[Dict[str, Any]] = []
            for c in self._counters.values():
                metrics.append({
                    "name": c.name,
                    "type": "counter",
                    "unit": "1",
                    "data": {
                        "data_points": [{
                            "attributes": c.labels,
                            "value": float(c.value) if isfinite(float(c.value)) else 0.0,
                            "time_unix_nano": int(datetime.now(timezone.utc).timestamp() * 1e9),
                        }]
                    },
                })
            for g in self._gauges.values():
                metrics.append({
                    "name": g.name,
                    "type": "gauge",
                    "unit": "1",
                    "data": {
                        "data_points": [{
                            "attributes": g.labels,
                            "value": float(g.value) if isfinite(float(g.value)) else 0.0,
                            "time_unix_nano": int(datetime.now(timezone.utc).timestamp() * 1e9),
                        }]
                    },
                })
            for h in self._histograms.values():
                metrics.append({
                    "name": h.name,
                    "type": "histogram",
                    "unit": "1",
                    "data": {
                        "data_points": [{
                            "attributes": h.labels,
                            "bucket_counts": [int(c) for c in h.counts],
                            "explicit_bounds": [float(b) for b in h.buckets],
                            "sum": float(h.sum) if isfinite(float(h.sum)) else 0.0,
                            "count": int(h.count),
                            "time_unix_nano": int(datetime.now(timezone.utc).timestamp() * 1e9),
                        }]
                    },
                })
        return serialize_metrics_strict({
            "resource_metrics": [{
                "scope_metrics": [{"metrics": metrics}],
            }],
        })


# Module-level default metrics registry.
metrics_registry = MetricsRegistry()


# --------------------------------------------------------------------------- Exporters

class MetricsExporter:
    """Base exporter interface for metrics."""

    def export(self, snapshot: Dict[str, Any]) -> None:
        raise NotImplementedError


class LoggingExporter(MetricsExporter):
    """Export metrics snapshot via structured logger."""

    def export(self, snapshot: Dict[str, Any]) -> None:
        observability_logger.info("metrics_export", metrics=snapshot)


class PrometheusExporter(MetricsExporter):
    """Export metrics in Prometheus text format via structured logger."""

    def __init__(self, registry: MetricsRegistry):
        self.registry = registry

    def export(self, snapshot: Optional[Dict[str, Any]] = None) -> None:
        text = self.registry.to_prometheus_text()
        observability_logger.info("prometheus_metrics", payload=text)


class OpenTelemetryExporter(MetricsExporter):
    """Export metrics in OpenTelemetry JSON format via structured logger."""

    def __init__(self, registry: MetricsRegistry):
        self.registry = registry

    def export(self, snapshot: Optional[Dict[str, Any]] = None) -> None:
        otel = self.registry.to_opentelemetry_json()
        observability_logger.info("opentelemetry_metrics", otel=otel)


# --------------------------------------------------------------------------- Tracing

@dataclass
class TraceSpan:
    """A trace span with deterministic timing."""

    span_id: str
    trace_id: str
    operation: str
    start_time: str
    end_time: Optional[str] = None
    status: str = "ok"
    attributes: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "span_id": self.span_id,
            "trace_id": self.trace_id,
            "operation": self.operation,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "status": self.status,
            "attributes": redact(self.attributes),
        })


class Tracer:
    """Deterministic tracer for distributed traces across components."""

    def __init__(self):
        self._lock = threading.Lock()
        self._spans: Dict[str, TraceSpan] = OrderedDict()
        self._active: Dict[str, str] = {}  # thread_id -> span_id

    def start_span(self, operation: str, trace_id: Optional[str] = None,
                   parent_span_id: Optional[str] = None,
                   attributes: Optional[Dict[str, Any]] = None) -> TraceSpan:
        tid = trace_id or observability_logger.new_trace()
        sid = f"span_{hashlib.sha256(f'{tid}|{time.time_ns()}|{threading.get_ident()}'.encode()).hexdigest()[:12]}"
        span = TraceSpan(
            span_id=sid,
            trace_id=tid,
            operation=operation,
            start_time=_now_iso(),
            status="ok",
            attributes=dict(attributes or {}),
        )
        with self._lock:
            self._spans[sid] = span
            self._active[str(threading.get_ident())] = sid
        observability_logger.debug("span_started", span_id=sid, trace_id=tid,
                                   operation=operation, parent_span_id=parent_span_id)
        return span

    def end_span(self, span: TraceSpan, status: str = "ok") -> None:
        span.end_time = _now_iso()
        span.status = status
        with self._lock:
            tid = str(threading.get_ident())
            if self._active.get(tid) == span.span_id:
                del self._active[tid]
        observability_logger.debug("span_ended", span_id=span.span_id,
                                   trace_id=span.trace_id, status=status)

    def get_span(self, span_id: str) -> Optional[TraceSpan]:
        with self._lock:
            return self._spans.get(span_id)

    def get_trace_spans(self, trace_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            return [s.to_dict() for s in self._spans.values() if s.trace_id == trace_id]

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            spans = [s.to_dict() for s in self._spans.values()]
        return serialize_metrics_strict({
            "num_spans": len(spans),
            "spans": spans,
            "timestamp": _now_iso(),
        })

    def clear(self) -> None:
        with self._lock:
            self._spans.clear()
            self._active.clear()


# Module-level default tracer.
tracer = Tracer()


__all__ = [
    "LogLevel", "LogEntry", "StructuredLogger", "observability_logger",
    "redact", "REDACT_KEYS", "REDACT_VALUE",
    "Counter", "Gauge", "Histogram", "MetricsRegistry", "metrics_registry",
    "MetricsExporter", "LoggingExporter", "PrometheusExporter", "OpenTelemetryExporter",
    "TraceSpan", "Tracer", "tracer",
]
