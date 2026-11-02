"""
Phase 38: Telemetry & Observability for Crypto Options + Orderflow.

Structured metrics/traces, counters/gauges/histograms, alerting hooks,
deterministic serialization. Extends Phases 17-37.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p38obs|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p38obs_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _assert_finite_dict(d: Dict[str, Any], label: str = "obj") -> None:
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

    walk(d, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class ObsConfig38:
    seed: int = 38039
    paper_only: bool = True
    metrics_interval_s: int = 60
    alert_threshold_breaches: int = 3
    export_formats: tuple = ("json", "md")


class Phase38TelemetryObservability:
    def __init__(self, config: Optional[ObsConfig38] = None, seed: int = 38039):
        self.config = config or ObsConfig38(seed=seed)
        if not isinstance(self.config.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.config.paper_only:
            raise ValueError("Phase38TelemetryObservability: paper_only must remain True")
        self.seed = int(self.config.seed)
        self._ctr = 0
        self.counters: Dict[str, float] = {}
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, List[float]] = {}
        self.traces: List[Dict[str, Any]] = []
        self.alerts: List[Dict[str, Any]] = []

    def _id(self, tag: str) -> str:
        self._ctr += 1
        return _make_id(self.seed, tag, self._ctr)

    def increment(self, key: str, val: float = 1.0) -> None:
        v = _finite(val)
        self.counters[key] = _finite(self.counters.get(key, 0.0)) + v

    def gauge(self, key: str, val: float) -> None:
        self.gauges[key] = _finite(val)

    def observe(self, key: str, val: float) -> None:
        v = _finite(val)
        self.histograms.setdefault(key, []).append(v)

    def trace(self, name: str, attrs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        attrs = attrs or {}
        t = {"trace_id": self._id("tr"), "name": name, "attrs": attrs, "ts": _utc_now()}
        _assert_finite_dict(t, "trace")
        self.traces.append(t)
        return t

    def alert(self, level: str, msg: str, ctx: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        a = {"alert_id": self._id("al"), "level": level, "msg": msg, "ctx": ctx or {}, "ts": _utc_now()}
        _assert_finite_dict(a, "alert")
        self.alerts.append(a)
        return a

    def export(self, outdir: str = "research_state") -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        report = {
            "phase": "PHASE38_OBSERVABILITY",
            "timestamp_utc": _utc_now(),
            "paper_only": True,
            "counters": {k: _finite(v) for k, v in self.counters.items()},
            "gauges": {k: _finite(v) for k, v in self.gauges.items()},
            "histograms": {k: [_finite(x) for x in vals] for k, vals in self.histograms.items()},
            "traces": self.traces,
            "alerts": self.alerts,
            "summary": {
                "n_traces": len(self.traces),
                "n_alerts": len(self.alerts),
                "n_counters": len(self.counters),
                "n_gauges": len(self.gauges),
            },
        }
        _assert_finite_dict(report, "obs_report")
        (out / "PHASE38_OBSERVABILITY_REPORT.json").write_text(json.dumps(report, indent=2))
        md = []
        md.append("# PHASE38 OBSERVABILITY REPORT")
        md.append(f"\nTimestamp: {report['timestamp_utc']}\n")
        md.append(f"Traces: {report['summary']['n_traces']}, Alerts: {report['summary']['n_alerts']}\n")
        md.append("\n## Counters\n")
        for k, v in report["counters"].items():
            md.append(f"- {k}: {v}\n")
        (out / "PHASE38_OBSERVABILITY_REPORT.md").write_text("".join(md))
        return report
