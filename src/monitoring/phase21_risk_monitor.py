#!/usr/bin/env python3
import hashlib
import math
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> str | None:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return str(sha)
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd="/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


def _det_ts(seed: int, idx: int = 0) -> str:
    h = hashlib.sha256(f"{seed}|p21mon|{idx}".encode()).hexdigest()[:12]
    return f"2026-11-01T14:{h[:2]}:{h[2:4]}Z"


def _assert_no_nan_inf(obj: Any, label: str) -> None:
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
        raise ValueError(f"Non-finite values detected in {label}: {bad[:10]}")


@dataclass(frozen=True)
class RiskMonitorConfig:
    seed: int = 42
    paper_only: bool = True
    alert_threshold_util: float = 0.8
    breach_escalation: bool = True
    drift_integration_enabled: bool = True


class Phase21RiskMonitor:
    def __init__(self, config: Optional[RiskMonitorConfig] = None, seed: int = 42):
        self.config = config or RiskMonitorConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("Phase21RiskMonitor: paper_only must remain True")
        self.config = RiskMonitorConfig(
            seed=int(self.config.seed),
            paper_only=True,
            alert_threshold_util=float(self.config.alert_threshold_util),
            breach_escalation=bool(self.config.breach_escalation),
            drift_integration_enabled=bool(self.config.drift_integration_enabled),
        )
        self.seed = int(self.config.seed)
        self.alerts: List[Dict[str, Any]] = []
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def monitor(
        self,
        agg_limits: Dict[str, Any],
        stress_summary: Optional[Dict[str, Any]] = None,
        pretrade_summary: Optional[Dict[str, Any]] = None,
        drift_summary: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._log("monitor", {})
        totals = agg_limits.get("totals", {})
        limits_rep = agg_limits
        alerts: List[Dict[str, Any]] = []
        # compute utilizations
        util = {}
        for k, lim in [("notional_usd", 5000000.0), ("delta", 2000.0), ("gamma", 500.0), ("vega", 50000.0)]:
            v = float(totals.get(k, 0.0))
            l = float(lim)
            if l > 0:
                u = abs(v) / l if k != "vega" or v >= 0 else v / l  # rough
                if k == "vega" and v < 0:
                    u = 0.0
                if k != "vega":
                    u = abs(v) / l
                else:
                    u = v / l if l > 0 else 0.0
                util[k] = float(u)
                if u >= self.config.alert_threshold_util:
                    alerts.append({"type": "limit_utilization_high", "metric": k, "utilization": u, "threshold": self.config.alert_threshold_util, "severity": "warn" if u < 1.0 else "critical"})

        if not agg_limits.get("passed", True):
            for b in agg_limits.get("breaches", []):
                alerts.append({"type": "aggregation_breach", "detail": b, "severity": b.get("severity", "block")})

        if stress_summary and stress_summary.get("breach_count", 0) > 0:
            alerts.append({"type": "stress_breaches", "count": stress_summary.get("breach_count"), "severity": "critical"})

        if pretrade_summary and pretrade_summary.get("blocked_count", 0) > 0:
            alerts.append({"type": "pretrade_blocks", "count": pretrade_summary.get("blocked_count"), "severity": "warn"})

        if drift_summary and not drift_summary.get("within_bounds", True):
            alerts.append({"type": "drift_out_of_bounds", "detail": drift_summary, "severity": "warn"})

        if self.config.breach_escalation and any(a.get("severity") == "critical" for a in alerts):
            alerts.append({"type": "escalation", "action": "engage_risk_escalation", "severity": "critical"})

        self.alerts.extend(alerts)
        rep = {
            "timestamp": _utc_now(),
            "utilization": util,
            "alerts": alerts,
            "alert_count": len(alerts),
            "critical_count": len([a for a in alerts if a.get("severity") == "critical"]),
            "warn_count": len([a for a in alerts if a.get("severity") == "warn"]),
            "drift_integration_enabled": self.config.drift_integration_enabled,
            "breach_escalation": self.config.breach_escalation,
            "healthy": len([a for a in alerts if a.get("severity") == "critical"]) == 0,
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p21_risk_monitor")
        return rep

    def generate_report(self, agg_limits: Dict[str, Any], **kwargs: Any) -> Dict[str, Any]:
        mon = self.monitor(agg_limits, **kwargs)
        rep = {
            "report": "PHASE21_RISK_MONITORING_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "monitoring": mon,
            "alerts_history": self.alerts,
            "audit": self.audit,
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p21_risk_monitor_report")
        return rep
