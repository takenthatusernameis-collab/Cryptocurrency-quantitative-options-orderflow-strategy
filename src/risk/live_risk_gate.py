"""Live Risk Gatekeeper for Phase 11."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class LiveRiskGatekeeper:
    def __init__(self, max_delta: float = 0.2, max_vega: float = 0.15, max_gamma: float = 0.08,
                 max_drawdown_pct: float = 0.15, min_liquidity: float = 0.1, min_dte: int = 1, max_dte: int = 90,
                 max_concentration: float = 0.25):
        self.max_delta = float(max_delta)
        self.max_vega = float(max_vega)
        self.max_gamma = float(max_gamma)
        self.max_drawdown_pct = float(max_drawdown_pct)
        self.min_liquidity = float(min_liquidity)
        self.min_dte = int(min_dte)
        self.max_dte = int(max_dte)
        self.max_concentration = float(max_concentration)
        self.kill_switch = False

    def check(self, intent: Any, portfolio_state: Dict[str, float]) -> Dict[str, Any]:
        if self.kill_switch:
            raise RuntimeError("kill_switch_triggered")
        dd = float(portfolio_state.get("drawdown_pct", 0.0))
        if dd > self.max_drawdown_pct:
            self.kill_switch = True
            raise RuntimeError("drawdown_kill_switch")
        delta = abs(float(getattr(intent, "delta_est", 0.0)))
        vega = abs(float(getattr(intent, "vega_est", 0.0)))
        gamma = abs(float(getattr(intent, "gamma_est", 0.0)))
        liq = float(getattr(intent, "liquidity_score", 1.0))
        dte = int(getattr(intent, "dte", 30))
        conc = float(portfolio_state.get("max_concentration", 0.0))
        if delta > self.max_delta + 1e-12:
            raise RuntimeError("delta_breach")
        if vega > self.max_vega + 1e-12:
            raise RuntimeError("vega_breach")
        if gamma > self.max_gamma + 1e-12:
            raise RuntimeError("gamma_breach")
        if liq < self.min_liquidity - 1e-12:
            raise RuntimeError("liquidity_breach")
        if dte < self.min_dte or dte > self.max_dte:
            raise RuntimeError("dte_breach")
        if conc > self.max_concentration + 1e-12:
            raise RuntimeError("concentration_breach")
        res = {"approved": True, "timestamp": _utc_now()}
        return serialize_metrics_strict(res)

    def generate_report(self) -> Dict[str, Any]:
        rep = {
            "timestamp": _utc_now(),
            "limits": {
                "max_delta": self.max_delta, "max_vega": self.max_vega, "max_gamma": self.max_gamma,
                "max_drawdown_pct": self.max_drawdown_pct, "min_liquidity": self.min_liquidity,
                "min_dte": self.min_dte, "max_dte": self.max_dte, "max_concentration": self.max_concentration,
            },
            "kill_switch": bool(self.kill_switch),
        }
        return serialize_metrics_strict(rep)
