"""
Phase 31: Production Telemetry for Crypto Options Vol Surface Arbitrage + Orderflow.

Metrics, traces, and logs for options vol arb + orderflow.
Production-grade, deterministic, finite numerics. PAPER-ONLY by default.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p31tel|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p31_{tag}_{h}"


def _assert_finite(obj: Any, label: str = "obj") -> None:
    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool):
            if not math.isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class TelemetryConfig:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    max_metric_points: int = 10000
    max_traces: int = 1000
    max_logs: int = 5000
    enforce_gates: bool = True


@dataclass(frozen=True)
class MetricPoint:
    name: str
    value: float
    tags: Dict[str, str]
    timestamp: str


@dataclass(frozen=True)
class TraceSpan:
    trace_id: str
    span_id: str
    operation: str
    start_ms: float
    end_ms: float
    duration_ms: float
    venue: str
    status: str


@dataclass(frozen=True)
class LogEntry:
    level: str  # "debug", "info", "warn", "error", "critical"
    message: str
    fields: Dict[str, Any]
    timestamp: str


@dataclass(frozen=True)
class TelemetrySnapshot:
    timestamp: str
    metric_count: int
    trace_count: int
    log_count: int
    alerts: int
    paper_only: bool


class ProductionTelemetry:
    def __init__(self, config: Optional[TelemetryConfig] = None, seed: int = 42) -> None:
        self.config = config or TelemetryConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "ProductionTelemetry: paper_only must remain True (live path hard-gated)"
            )
        self.config = TelemetryConfig(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            max_metric_points=int(self.config.max_metric_points),
            max_traces=int(self.config.max_traces),
            max_logs=int(self.config.max_logs),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.metrics: List[MetricPoint] = []
        self.traces: List[TraceSpan] = []
        self.logs: List[LogEntry] = []
        self._trace_counter = 0

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def record_metric(self, name: str, value: float, tags: Optional[Dict[str, str]] = None) -> MetricPoint:
        name = str(name)
        value = float(value)
        if not math.isfinite(value):
            raise ValueError(f"non-finite metric value for {name}")
        tags = dict(tags or {})
        mp = MetricPoint(
            name=name,
            value=value,
            tags=tags,
            timestamp=_utc_now(),
        )
        _assert_finite(asdict(mp), f"metric_{name}")
        self.metrics.append(mp)
        if len(self.metrics) > self.config.max_metric_points:
            self.metrics = self.metrics[-self.config.max_metric_points:]
        return mp

    def start_trace(self, operation: str, venue: str) -> str:
        self._trace_counter += 1
        trace_id = _make_id(self.seed, "trace", self._trace_counter)
        span_id = _make_id(self.seed, "span", self._trace_counter)
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            operation=str(operation),
            start_ms=0.0,
            end_ms=0.0,
            duration_ms=0.0,
            venue=str(venue),
            status="open",
        )
        _assert_finite(asdict(span), f"trace_{trace_id}")
        self.traces.append(span)
        if len(self.traces) > self.config.max_traces:
            self.traces = self.traces[-self.config.max_traces:]
        return trace_id

    def end_trace(self, trace_id: str, status: str = "ok", end_ms: Optional[float] = None) -> Optional[TraceSpan]:
        status = str(status)
        end_ms = float(end_ms if end_ms is not None else 0.0)
        for i, span in enumerate(self.traces):
            if span.trace_id == trace_id:
                end_ms_f = float(end_ms)
                updated = TraceSpan(
                    trace_id=span.trace_id,
                    span_id=span.span_id,
                    operation=span.operation,
                    start_ms=span.start_ms,
                    end_ms=end_ms_f,
                    duration_ms=end_ms_f - span.start_ms,
                    venue=span.venue,
                    status=status,
                )
                _assert_finite(asdict(updated), f"trace_end_{trace_id}")
                self.traces[i] = updated
                return updated
        return None

    def log(self, level: str, message: str, fields: Optional[Dict[str, Any]] = None) -> LogEntry:
        level = str(level).lower()
        message = str(message)
        fields = dict(fields or {})
        le = LogEntry(
            level=level,
            message=message,
            fields=fields,
            timestamp=_utc_now(),
        )
        self.logs.append(le)
        if len(self.logs) > self.config.max_logs:
            self.logs = self.logs[-self.config.max_logs:]
        return le

    def snapshot(self) -> TelemetrySnapshot:
        snap = TelemetrySnapshot(
            timestamp=_utc_now(),
            metric_count=int(len(self.metrics)),
            trace_count=int(len(self.traces)),
            log_count=int(len(self.logs)),
            alerts=int(sum(1 for l in self.logs if l.level in ("error", "critical"))),
            paper_only=True,
        )
        return snap

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        from pathlib import Path

        Path(outdir).mkdir(parents=True, exist_ok=True)
        snap = self.snapshot()
        report = {
            "report": "PHASE31_PRODUCTION_TELEMETRY_REPORT",
            "timestamp": snap.timestamp,
            "seed": self.seed,
            "paper_only": True,
            "metric_count": snap.metric_count,
            "trace_count": snap.trace_count,
            "log_count": snap.log_count,
            "alerts": snap.alerts,
            "metrics": [asdict(m) for m in self.metrics[-200:]],
            "traces": [asdict(t) for t in self.traces[-100:]],
            "logs": [asdict(l) for l in self.logs[-200:]],
            "config": asdict(self.config),
        }
        _assert_finite(report, "phase31_production_telemetry_report")
        rep_json = Path(outdir) / "PHASE31_PRODUCTION_TELEMETRY_REPORT.json"
        rep_md = Path(outdir) / "PHASE31_PRODUCTION_TELEMETRY_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE31_PRODUCTION_TELEMETRY_REPORT\n\n"
            f"Timestamp: {snap.timestamp}\nPaper-only: {snap.paper_only}\n"
            f"Metrics: {snap.metric_count}\nTraces: {snap.trace_count}\nLogs: {snap.log_count}\n"
            f"Error/critical logs: {snap.alerts}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
        }


__all__ = [
    "ProductionTelemetry",
    "TelemetryConfig",
    "MetricPoint",
    "TraceSpan",
    "LogEntry",
    "TelemetrySnapshot",
]
