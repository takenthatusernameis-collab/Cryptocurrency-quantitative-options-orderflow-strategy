"""Production telemetry & monitoring for crypto options + orderflow execution.

Real-time-style metrics (PnL, drawdown, greeks, gamma exposure, VaR/ES, heat,
limits utilization), alerts, structured logging, and strict-serializable
artifact emission. All numeric outputs pass through allow_nan=False serialization.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Callable, Dict, List, Optional

from ..errors import SerializationError, get_logger
from ..risk.execution_integration import ExecutionRiskIntegrator, RiskAction
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import clamp, safe_divide


_logger = get_logger(__name__)


@dataclass
class Alert:
    """A telemetry alert."""

    alert_id: str
    severity: str  # info/warning/error/critical
    message: str
    metric: str
    current_value: float
    threshold: float
    timestamp: str
    acknowledged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "alert_id": self.alert_id,
            "severity": self.severity,
            "message": self.message,
            "metric": self.metric,
            "current_value": float(self.current_value) if isfinite(float(self.current_value)) else 0.0,
            "threshold": float(self.threshold) if isfinite(float(self.threshold)) else 0.0,
            "timestamp": self.timestamp,
            "acknowledged": bool(self.acknowledged),
        })


@dataclass
class TelemetrySnapshot:
    """A point-in-time telemetry snapshot, strict-serializable."""

    timestamp: str
    run_id: str
    pnl: float
    daily_pnl: float
    drawdown_pct: float
    drawdown_absolute: float
    current_equity: float
    peak_equity: float
    total_return_pct: float
    sharpe_estimate: float
    max_delta: float
    max_gamma: float
    max_vega: float
    portfolio_delta: float
    portfolio_gamma: float
    portfolio_vega: float
    gamma_exposure: float
    var_95: float
    expected_shortfall_95: float
    heat: float
    limits_utilization: Dict[str, float]
    num_violations: int
    kill_switch_state: str
    circuit_state: str
    num_orders: int
    num_fills: int
    total_commission: float
    total_execution_cost: float
    alerts: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "timestamp": self.timestamp,
            "run_id": self.run_id,
            "pnl": float(self.pnl) if isfinite(float(self.pnl)) else 0.0,
            "daily_pnl": float(self.daily_pnl) if isfinite(float(self.daily_pnl)) else 0.0,
            "drawdown_pct": float(self.drawdown_pct) if isfinite(float(self.drawdown_pct)) else 0.0,
            "drawdown_absolute": float(self.drawdown_absolute) if isfinite(float(self.drawdown_absolute)) else 0.0,
            "current_equity": float(self.current_equity) if isfinite(float(self.current_equity)) else 0.0,
            "peak_equity": float(self.peak_equity) if isfinite(float(self.peak_equity)) else 0.0,
            "total_return_pct": float(self.total_return_pct) if isfinite(float(self.total_return_pct)) else 0.0,
            "sharpe_estimate": float(self.sharpe_estimate) if isfinite(float(self.sharpe_estimate)) else 0.0,
            "max_delta": float(self.max_delta) if isfinite(float(self.max_delta)) else 0.0,
            "max_gamma": float(self.max_gamma) if isfinite(float(self.max_gamma)) else 0.0,
            "max_vega": float(self.max_vega) if isfinite(float(self.max_vega)) else 0.0,
            "portfolio_delta": float(self.portfolio_delta) if isfinite(float(self.portfolio_delta)) else 0.0,
            "portfolio_gamma": float(self.portfolio_gamma) if isfinite(float(self.portfolio_gamma)) else 0.0,
            "portfolio_vega": float(self.portfolio_vega) if isfinite(float(self.portfolio_vega)) else 0.0,
            "gamma_exposure": float(self.gamma_exposure) if isfinite(float(self.gamma_exposure)) else 0.0,
            "var_95": float(self.var_95) if isfinite(float(self.var_95)) else 0.0,
            "expected_shortfall_95": float(self.expected_shortfall_95) if isfinite(float(self.expected_shortfall_95)) else 0.0,
            "heat": float(self.heat) if isfinite(float(self.heat)) else 0.0,
            "limits_utilization": {k: float(v) if isfinite(float(v)) else 0.0 for k, v in self.limits_utilization.items()},
            "num_violations": int(self.num_violations),
            "kill_switch_state": self.kill_switch_state,
            "circuit_state": self.circuit_state,
            "num_orders": int(self.num_orders),
            "num_fills": int(self.num_fills),
            "total_commission": float(self.total_commission) if isfinite(float(self.total_commission)) else 0.0,
            "total_execution_cost": float(self.total_execution_cost) if isfinite(float(self.total_execution_cost)) else 0.0,
            "alerts": self.alerts,
            "metadata": self.metadata,
        })


class ProductionTelemetryMonitor:
    """Production telemetry monitor with alerting and artifact emission.

    Tracks PnL, drawdown, greeks, gamma exposure, VaR/ES, heat, and limits
    utilization. Emits strict-serializable snapshots and alerts. Deterministic
    given fixed seed. Thread-safe-ish (single-threaded campaign usage).
    """

    def __init__(
        self,
        run_id: Optional[str] = None,
        seed: int = 42,
        risk_integrator: Optional[ExecutionRiskIntegrator] = None,
        var_confidence: float = 0.95,
        alert_webhook: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        self.seed = int(seed)
        self.run_id = run_id or f"run_{self.seed}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        self.risk_integrator = risk_integrator
        self.var_confidence = float(var_confidence) if isfinite(float(var_confidence)) else 0.95
        if not 0.5 < self.var_confidence < 0.999:
            self.var_confidence = 0.95
        self.alert_webhook = alert_webhook
        self.snapshots: List[TelemetrySnapshot] = []
        self.alerts: List[Alert] = []
        self._alert_counter = 0
        self._pnl_history: List[float] = []
        self._return_history: List[float] = []
        self._equity_history: List[float] = []
        self.start_equity: Optional[float] = None
        self._id_prefix = f"tel_{self.seed}"

    # ------------------------------------------------------------------ id / time
    def _next_alert_id(self) -> str:
        self._alert_counter += 1
        payload = f"{self._id_prefix}|{self._alert_counter}|{datetime.now(timezone.utc).isoformat()}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        return f"{self._id_prefix}_alert_{digest}"

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------ update
    def update(
        self,
        pnl: float,
        daily_pnl: float,
        current_equity: float,
        peak_equity: float,
        portfolio_greeks: Optional[Dict[str, float]] = None,
        gamma_exposure: float = 0.0,
        num_orders: int = 0,
        num_fills: int = 0,
        total_commission: float = 0.0,
        total_execution_cost: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> TelemetrySnapshot:
        """Record a telemetry update and return a strict-serializable snapshot."""
        pnl = float(pnl) if isfinite(float(pnl)) else 0.0
        daily_pnl = float(daily_pnl) if isfinite(float(daily_pnl)) else 0.0
        current_equity = float(current_equity) if isfinite(float(current_equity)) else 0.0
        peak_equity = float(peak_equity) if isfinite(float(peak_equity)) else 0.0
        gamma_exposure = float(gamma_exposure) if isfinite(float(gamma_exposure)) else 0.0
        total_commission = float(total_commission) if isfinite(float(total_commission)) else 0.0
        total_execution_cost = float(total_execution_cost) if isfinite(float(total_execution_cost)) else 0.0

        if self.start_equity is None:
            self.start_equity = current_equity if current_equity > 0 else 100000.0
        start_eq = float(self.start_equity) if float(self.start_equity) > 0 else 100000.0

        self._pnl_history.append(pnl)
        self._equity_history.append(current_equity)
        if len(self._pnl_history) > 1:
            prev_eq = self._equity_history[-2] if len(self._equity_history) >= 2 else start_eq
            if prev_eq > 0:
                self._return_history.append((current_equity - prev_eq) / prev_eq)

        # Drawdown
        if peak_equity > 0:
            drawdown_pct = (peak_equity - current_equity) / peak_equity
            drawdown_absolute = peak_equity - current_equity
        else:
            drawdown_pct = 0.0
            drawdown_absolute = 0.0
        drawdown_pct = float(clamp(drawdown_pct, 0.0, 1.0))
        drawdown_absolute = float(max(0.0, drawdown_absolute))

        # Total return
        total_return_pct = float(clamp((current_equity - start_eq) / start_eq, -1.0, 10.0))

        # Sharpe estimate (annualized-ish, simple)
        sharpe_estimate = 0.0
        if len(self._return_history) >= 2:
            rets = [r for r in self._return_history if isfinite(r)]
            if len(rets) >= 2:
                mean_ret = sum(rets) / len(rets)
                var_ret = sum((r - mean_ret) ** 2 for r in rets) / len(rets)
                std_ret = math.sqrt(var_ret) if var_ret > 0 else 0.0
                if std_ret > 0:
                    sharpe_estimate = mean_ret / std_ret * math.sqrt(252.0)
        sharpe_estimate = float(clamp(sharpe_estimate, -50.0, 50.0))

        # VaR / Expected Shortfall (historical, per confidence)
        var_95 = 0.0
        es_95 = 0.0
        if len(self._return_history) >= 10:
            sorted_rets = sorted(self._return_history)
            idx = max(0, int(math.ceil((1.0 - self.var_confidence) * len(sorted_rets))) - 1)
            var_95 = abs(sorted_rets[idx]) if sorted_rets else 0.0
            tail = sorted_rets[: max(1, idx + 1)]
            es_95 = abs(sum(tail) / len(tail)) if tail else 0.0
        var_95 = float(clamp(var_95, 0.0, 1.0))
        es_95 = float(clamp(es_95, 0.0, 1.0))

        # Heat: drawdown + volatility proxy, normalized [0,1]
        recent_vol = 0.0
        if len(self._return_history) >= 5:
            recent = self._return_history[-20:]
            mean_r = sum(recent) / len(recent)
            recent_vol = math.sqrt(sum((r - mean_r) ** 2 for r in recent) / len(recent))
        heat = float(clamp(drawdown_pct + min(recent_vol * 10.0, 1.0), 0.0, 1.0))

        # Limits utilization from risk integrator
        limits_utilization: Dict[str, float] = {}
        kill_switch_state = "armed"
        circuit_state = "closed"
        num_violations = 0
        portfolio_delta = 0.0
        portfolio_gamma = 0.0
        portfolio_vega = 0.0
        if self.risk_integrator is not None:
            report = self.risk_integrator.get_risk_report()
            kill_switch_state = str(report.get("kill_switch_state", "armed"))
            circuit_state = str(report.get("circuit_breaker", {}).get("state", "closed"))
            num_violations = int(report.get("num_violations", 0))
            greeks = report.get("portfolio_greeks", {})
            portfolio_delta = float(greeks.get("delta", 0.0)) if isfinite(float(greeks.get("delta", 0.0))) else 0.0
            portfolio_gamma = float(greeks.get("gamma", 0.0)) if isfinite(float(greeks.get("gamma", 0.0))) else 0.0
            portfolio_vega = float(greeks.get("vega", 0.0)) if isfinite(float(greeks.get("vega", 0.0))) else 0.0
            rm_report = report.get("risk_manager", {})
            lim = rm_report.get("limits", {})
            limits_utilization = {
                "delta_utilization": float(clamp(abs(portfolio_delta) / max(1.0, float(lim.get("max_portfolio_delta", 1.0))), 0.0, 1.0)),
                "gamma_utilization": float(clamp(abs(portfolio_gamma) / max(1.0, float(lim.get("max_portfolio_gamma", 1.0))), 0.0, 1.0)),
                "vega_utilization": float(clamp(abs(portfolio_vega) / max(1.0, float(lim.get("max_portfolio_vega", 1.0))), 0.0, 1.0)),
                "drawdown_utilization": float(clamp(drawdown_pct / max(1e-9, float(lim.get("max_drawdown_pct", 0.15))), 0.0, 1.0)),
                "daily_loss_utilization": float(clamp(abs(daily_pnl) / max(1.0, float(lim.get("max_daily_loss", 1.0))), 0.0, 1.0)),
            }

        greeks = portfolio_greeks or {}
        port_delta = float(greeks.get("delta", portfolio_delta)) if isfinite(float(greeks.get("delta", portfolio_delta))) else 0.0
        port_gamma = float(greeks.get("gamma", portfolio_gamma)) if isfinite(float(greeks.get("gamma", portfolio_gamma))) else 0.0
        port_vega = float(greeks.get("vega", portfolio_vega)) if isfinite(float(greeks.get("vega", portfolio_vega))) else 0.0

        snapshot = TelemetrySnapshot(
            timestamp=self._now_iso(),
            run_id=self.run_id,
            pnl=pnl,
            daily_pnl=daily_pnl,
            drawdown_pct=drawdown_pct,
            drawdown_absolute=drawdown_absolute,
            current_equity=current_equity,
            peak_equity=peak_equity,
            total_return_pct=total_return_pct,
            sharpe_estimate=sharpe_estimate,
            max_delta=float(clamp(abs(port_delta), 0.0, 1e9)),
            max_gamma=float(clamp(abs(port_gamma), 0.0, 1e9)),
            max_vega=float(clamp(abs(port_vega), 0.0, 1e9)),
            portfolio_delta=port_delta,
            portfolio_gamma=port_gamma,
            portfolio_vega=port_vega,
            gamma_exposure=gamma_exposure,
            var_95=var_95,
            expected_shortfall_95=es_95,
            heat=heat,
            limits_utilization=limits_utilization,
            num_violations=num_violations,
            kill_switch_state=kill_switch_state,
            circuit_state=circuit_state,
            num_orders=int(num_orders),
            num_fills=int(num_fills),
            total_commission=total_commission,
            total_execution_cost=total_execution_cost,
            alerts=[],
            metadata=metadata or {},
        )

        # Evaluate alerts
        new_alerts: List[Dict[str, Any]] = []
        alert_thresholds = [
            ("drawdown_pct", drawdown_pct, 0.10, "warning", 0.15, "critical"),
            ("daily_loss", abs(daily_pnl), 25000.0, "warning", 50000.0, "critical"),
            ("heat", heat, 0.6, "warning", 0.8, "critical"),
            ("delta_utilization", limits_utilization.get("delta_utilization", 0.0), 0.8, "warning", 0.95, "critical"),
            ("gamma_utilization", limits_utilization.get("gamma_utilization", 0.0), 0.8, "warning", 0.95, "critical"),
            ("vega_utilization", limits_utilization.get("vega_utilization", 0.0), 0.8, "warning", 0.95, "critical"),
        ]
        for metric, cur, warn_thr, warn_sev, crit_thr, crit_sev in alert_thresholds:
            if cur >= crit_thr:
                alert = self._raise_alert(crit_sev, f"{metric} breached critical threshold",
                                          metric, cur, crit_thr)
                new_alerts.append(alert.to_dict())
            elif cur >= warn_thr:
                alert = self._raise_alert(warn_sev, f"{metric} approaching threshold",
                                          metric, cur, warn_thr)
                new_alerts.append(alert.to_dict())

        snapshot.alerts = new_alerts
        self.snapshots.append(snapshot)
        return snapshot

    def _raise_alert(self, severity: str, message: str, metric: str,
                     current_value: float, threshold: float) -> Alert:
        alert = Alert(
            alert_id=self._next_alert_id(),
            severity=severity,
            message=message,
            metric=metric,
            current_value=current_value,
            threshold=threshold,
            timestamp=self._now_iso(),
            acknowledged=False,
        )
        self.alerts.append(alert)
        if self.alert_webhook is not None:
            try:
                self.alert_webhook(alert.to_dict())
            except Exception:
                pass
        _logger.warning("telemetry_alert", severity=severity, metric=metric,
                        current_value=current_value, threshold=threshold)
        return alert

    # ------------------------------------------------------------------ export
    def get_latest_snapshot(self) -> Optional[TelemetrySnapshot]:
        return self.snapshots[-1] if self.snapshots else None

    def get_snapshots(self) -> List[Dict[str, Any]]:
        return [s.to_dict() for s in self.snapshots]

    def get_alerts(self) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self.alerts]

    def acknowledge_alert(self, alert_id: str) -> bool:
        for a in self.alerts:
            if a.alert_id == alert_id:
                a.acknowledged = True
                return True
        return False

    def export_report(self) -> Dict[str, Any]:
        """Export a full strict-serializable telemetry report."""
        latest = self.get_latest_snapshot()
        return serialize_metrics_strict({
            "run_id": self.run_id,
            "seed": int(self.seed),
            "num_snapshots": len(self.snapshots),
            "num_alerts": len(self.alerts),
            "num_unacknowledged_alerts": sum(1 for a in self.alerts if not a.acknowledged),
            "var_confidence": float(self.var_confidence),
            "latest_snapshot": latest.to_dict() if latest else {},
            "snapshots": self.get_snapshots(),
            "alerts": self.get_alerts(),
            "summary": {
                "total_pnl": float(latest.pnl) if latest else 0.0,
                "daily_pnl": float(latest.daily_pnl) if latest else 0.0,
                "drawdown_pct": float(latest.drawdown_pct) if latest else 0.0,
                "total_return_pct": float(latest.total_return_pct) if latest else 0.0,
                "sharpe_estimate": float(latest.sharpe_estimate) if latest else 0.0,
                "var_95": float(latest.var_95) if latest else 0.0,
                "expected_shortfall_95": float(latest.expected_shortfall_95) if latest else 0.0,
                "heat": float(latest.heat) if latest else 0.0,
                "gamma_exposure": float(latest.gamma_exposure) if latest else 0.0,
                "kill_switch_state": latest.kill_switch_state if latest else "armed",
                "circuit_state": latest.circuit_state if latest else "closed",
                "num_orders": latest.num_orders if latest else 0,
                "num_fills": latest.num_fills if latest else 0,
                "total_commission": float(latest.total_commission) if latest else 0.0,
                "total_execution_cost": float(latest.total_execution_cost) if latest else 0.0,
            },
        })

    def write_artifact(self, path: str) -> str:
        """Write the telemetry report to ``path`` as strict JSON. Returns path."""
        report = self.export_report()
        payload = json.dumps(report, allow_nan=False, indent=2)
        with open(path, "w", encoding="utf-8") as f:
            f.write(payload)
        _logger.info("telemetry_artifact_written", path=path, run_id=self.run_id)
        return path


__all__ = [
    "Alert",
    "TelemetrySnapshot",
    "ProductionTelemetryMonitor",
]
