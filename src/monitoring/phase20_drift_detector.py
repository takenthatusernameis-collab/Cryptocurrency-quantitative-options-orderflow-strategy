"""Phase 20 DriftDetector: PnL/Greeks/fills/latency drift, anomaly scoring, alert hooks."""
from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from src.telemetry.serialization import serialize_metrics_strict


_BASE_DAY = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _det_ts(seed: int) -> str:
    return (_BASE_DAY + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


@dataclass
class Phase20DriftConfig:
    pnl_drift_threshold: float = 0.05
    greeks_drift_threshold: float = 0.08
    fills_drift_threshold: float = 0.10
    latency_drift_ms_threshold: float = 50.0
    anomaly_threshold: float = 0.7
    paper_only: bool = True


class Phase20DriftDetector:
    def __init__(self, config: Optional[Phase20DriftConfig] = None, seed: int = 42):
        self.config = config or Phase20DriftConfig()
        if self.config.paper_only is False:
            raise ValueError("Phase20DriftDetector: paper_only must remain True by default")
        self.config.paper_only = True
        self.seed = int(seed)
        self.alerts: List[Dict[str, Any]] = []

    def detect(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        baseline = baseline or {}
        current = current or {}
        anomalies: List[Dict[str, Any]] = []
        scores: List[float] = []

        def rel_drift(b, c):
            b_f = float(b)
            c_f = float(c)
            if not math.isfinite(b_f) or not math.isfinite(c_f):
                return 0.0
            if abs(b_f) < 1e-12:
                return abs(c_f - b_f)
            return abs(c_f - b_f) / abs(b_f)

        pnl_d = rel_drift(baseline.get("pnl", 0.0), current.get("pnl", 0.0))
        if pnl_d > self.config.pnl_drift_threshold:
            anomalies.append({"metric": "pnl", "drift": pnl_d, "threshold": self.config.pnl_drift_threshold})
            scores.append(min(1.0, pnl_d / self.config.pnl_drift_threshold))
            self.alerts.append({"type": "pnl_drift", "drift": pnl_d, "timestamp": _utc_now()})

        g_b = baseline.get("greeks", {}) or {}
        g_c = current.get("greeks", {}) or {}
        max_gd = 0.0
        for k in set(g_b) | set(g_c):
            gd = rel_drift(g_b.get(k, 0.0), g_c.get(k, 0.0))
            if gd > max_gd:
                max_gd = gd
        if max_gd > self.config.greeks_drift_threshold:
            anomalies.append({"metric": "greeks", "max_drift": max_gd, "threshold": self.config.greeks_drift_threshold})
            scores.append(min(1.0, max_gd / self.config.greeks_drift_threshold))
            self.alerts.append({"type": "greeks_drift", "max_drift": max_gd, "timestamp": _utc_now()})

        f_b = float(baseline.get("fills_rate", 1.0))
        f_c = float(current.get("fills_rate", 1.0))
        f_d = rel_drift(f_b, f_c)
        if f_d > self.config.fills_drift_threshold:
            anomalies.append({"metric": "fills_rate", "drift": f_d, "threshold": self.config.fills_drift_threshold})
            scores.append(min(1.0, f_d / self.config.fills_drift_threshold))

        l_b = float(baseline.get("latency_ms", 10.0))
        l_c = float(current.get("latency_ms", 10.0))
        l_d = abs(l_c - l_b)
        if l_d > self.config.latency_drift_ms_threshold:
            anomalies.append({"metric": "latency_ms", "delta": l_d, "threshold": self.config.latency_drift_ms_threshold})
            scores.append(min(1.0, l_d / self.config.latency_drift_ms_threshold))

        anomaly_score = float(max(scores) if scores else 0.0)
        within_bounds = anomaly_score < self.config.anomaly_threshold
        res = {
            "timestamp": _utc_now(),
            "seed": self.seed,
            "anomalies": anomalies,
            "anomaly_count": len(anomalies),
            "anomaly_score": anomaly_score,
            "within_bounds": bool(within_bounds),
            "alerts_triggered": len([a for a in self.alerts if a["timestamp"].startswith(_utc_now()[:10])]) >= 0,
            "alerts_count": len(self.alerts),
            "paper_only": True,
        }
        return serialize_metrics_strict(res)

    def generate_report(self, baseline: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
        det = self.detect(baseline, current)
        rep = {
            "report": "PHASE20_DRIFT_DETECTION_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "baseline": baseline,
            "current": current,
            "detection": det,
            "alerts": self.alerts,
            "paper_only": True,
        }
        return serialize_metrics_strict(rep)
