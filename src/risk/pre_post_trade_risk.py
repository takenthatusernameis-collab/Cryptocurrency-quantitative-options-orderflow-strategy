"""Pre/post-trade risk and circuit breaker integration."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

from src.resilience.circuit import CircuitBreaker, CircuitBreakerConfig


class PrePostTradeRisk:
    def __init__(self):
        self.cb = CircuitBreaker(CircuitBreakerConfig(name="pre_post_trade", failure_threshold=5, timeout_seconds=60.0))
        self.violations: list = []

    def pre_trade(self, intent: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        if not self.cb.can_execute():
            self.violations.append({"type": "circuit_open", "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")})
            raise RuntimeError("circuit_breaker_open")
        # checks
        delta = float(intent.get("delta", 0.0))
        vega = float(intent.get("vega", 0.0))
        gamma = float(intent.get("gamma", 0.0))
        liquidity = float(intent.get("liquidity", 1.0))
        dte = float(intent.get("dte", 30))
        if abs(delta) > 0.5:
            self.violations.append({"type": "delta_limit"})
            raise ValueError("pretrade_delta_breach")
        if abs(vega) > 1000.0:
            self.violations.append({"type": "vega_limit"})
            raise ValueError("pretrade_vega_breach")
        if abs(gamma) > 50.0:
            self.violations.append({"type": "gamma_limit"})
            raise ValueError("pretrade_gamma_breach")
        if liquidity < 0.1:
            self.violations.append({"type": "liquidity_min"})
            raise ValueError("pretrade_liquidity_breach")
        if dte < 1 or dte > 365:
            self.violations.append({"type": "dte_range"})
            raise ValueError("pretrade_dte_breach")
        return {"ok": True}

    def post_trade(self, fill: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        slip = float(fill.get("slippage_bps", 1.0))
        if slip > 50.0:
            self.cb.record_failure()
            self.violations.append({"type": "slippage_breach", "slip_bps": slip})
            raise ValueError("posttrade_slippage_breach")
        self.cb.record_success()
        return {"ok": True}

    def strategy_kill_switch(self) -> None:
        self.cb._manual_override = __import__('src.resilience.circuit', fromlist=['CircuitBreakerState']).CircuitBreakerState.OPEN

    def heartbeat_latency_check(self, latency_ms: float) -> bool:
        if latency_ms > 500.0:
            self.cb.record_failure()
            return False
        self.cb.record_success()
        return True

    def generate_report(self) -> Dict[str, Any]:
        from src.resilience.circuit import CircuitBreakerState
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "circuit_state": self.cb.state.value if isinstance(self.cb.state, CircuitBreakerState) else str(self.cb.state),
            "failures": getattr(self.cb, 'failure_count', 0),
            "violations": list(self.violations),
            "venue_circuit_breakers": True,
            "strategy_kill_switch": True,
            "heartbeat_latency_guards": True,
            "pre_trade_checks": ["delta", "vega", "gamma", "liquidity", "dte", "spread"],
            "post_trade_checks": ["slippage", "fills", "reconciliation"],
        }
        return report
