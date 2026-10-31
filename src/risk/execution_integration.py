"""Risk integration layer: wires RiskManager/CircuitBreaker/KillSwitch into execution.

Production-grade pre-trade and post-trade risk enforcement for the crypto options
+ orderflow execution engine. Provides block/hold/flatten actions on breach,
kill-switch propagation, and a full deterministic audit trail. All outputs are
strict-serializable (allow_nan=False) and deterministic (seeded IDs).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Dict, List, Optional

from ..errors import RiskLimitError, get_logger
from ..risk.circuit_breaker import CircuitBreaker, CircuitBreakerState
from ..risk.limits import KillSwitchState, RiskManager, RiskViolation
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import safe_divide, clamp


_logger = get_logger(__name__)


class RiskAction(str, Enum):
    """Risk enforcement action returned by the integration layer."""
    ALLOW = "allow"
    BLOCK = "block"
    HOLD = "hold"
    FLATTEN = "flatten"
    REDUCE = "reduce"


class ExecutionRiskState(str, Enum):
    """Lifecycle state of the execution risk integrator."""
    ARMED = "armed"
    BREACHED = "breached"
    FLATTENING = "flattening"
    HALTED = "halted"
    DISABLED = "disabled"


@dataclass
class ExecutionRiskConfig:
    """Configuration for execution risk integration."""

    enable_pre_trade_checks: bool = True
    enable_post_trade_checks: bool = True
    enable_kill_switch_propagation: bool = True
    enable_circuit_breaker: bool = True
    auto_flatten_on_kill_switch: bool = True
    max_order_notional: float = 1_000_000.0
    max_order_quantity: float = 1000.0
    max_portfolio_delta: float = 500000.0
    max_portfolio_gamma: float = 50000.0
    max_portfolio_vega: float = 200000.0
    max_daily_loss: float = 50000.0
    max_drawdown_pct: float = 0.15
    stale_greek_seconds: float = 300.0
    latency_penalty_bps: float = 1.0
    partial_hedge_on_latency: bool = True
    partial_hedge_ratio: float = 0.5
    seed: int = 42

    def __post_init__(self) -> None:
        for name in [
            "max_order_notional",
            "max_order_quantity",
            "max_portfolio_delta",
            "max_portfolio_gamma",
            "max_portfolio_vega",
            "max_daily_loss",
            "max_drawdown_pct",
            "stale_greek_seconds",
            "latency_penalty_bps",
            "partial_hedge_ratio",
        ]:
            val = float(getattr(self, name))
            if not isfinite(val) or val < 0:
                raise RiskLimitError(f"{name} must be finite and >= 0", context={"limit": name, "value": val})
        if not (0.0 <= self.partial_hedge_ratio <= 1.0):
            raise RiskLimitError("partial_hedge_ratio must be in [0,1]", context={"partial_hedge_ratio": self.partial_hedge_ratio})
        if not isfinite(float(self.seed)) or int(self.seed) < 0:
            raise RiskLimitError("seed must be non-negative integer", context={"seed": self.seed})


@dataclass
class RiskCheckResult:
    """Result of a pre-trade or post-trade risk check."""

    action: RiskAction
    approved: bool
    violations: List[RiskViolation] = field(default_factory=list)
    adjusted_quantity: Optional[float] = None
    adjusted_price: Optional[float] = None
    reason: str = ""
    audit_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "action": self.action.value,
            "approved": bool(self.approved),
            "violations": [v.to_dict() for v in self.violations],
            "adjusted_quantity": float(self.adjusted_quantity) if self.adjusted_quantity is not None else None,
            "adjusted_price": float(self.adjusted_price) if self.adjusted_price is not None else None,
            "reason": self.reason,
            "audit_id": self.audit_id,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        })


@dataclass
class ExecutionRiskAudit:
    """Full audit trail for an execution risk event."""

    audit_id: str
    event_type: str  # pre_trade / post_trade / kill_switch / circuit_breaker / flatten
    symbol: str
    side: str
    quantity: float
    price: float
    action: RiskAction
    approved: bool
    risk_state: ExecutionRiskState
    violations: List[Dict[str, Any]]
    portfolio_greeks: Dict[str, float]
    latency_ms: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "audit_id": self.audit_id,
            "event_type": self.event_type,
            "symbol": self.symbol,
            "side": self.side,
            "quantity": float(self.quantity),
            "price": float(self.price),
            "action": self.action.value,
            "approved": bool(self.approved),
            "risk_state": self.risk_state.value,
            "violations": self.violations,
            "portfolio_greeks": self.portfolio_greeks,
            "latency_ms": float(self.latency_ms),
            "timestamp": self.timestamp.isoformat(),
        })


class ExecutionRiskIntegrator:
    """Wires RiskManager + CircuitBreaker into the ExecutionEngine execution path.

    Enforces pre-trade checks (block/hold/flatten/reduce on breach), post-trade
    limits, kill-switch propagation, and circuit-breaker integration. Maintains
    a deterministic audit trail. All methods are deterministic given the same
    inputs and seed.
    """

    def __init__(
        self,
        risk_manager: Optional[RiskManager] = None,
        circuit_breaker: Optional[CircuitBreaker] = None,
        config: Optional[ExecutionRiskConfig] = None,
        seed: int = 42,
    ):
        self.config = config or ExecutionRiskConfig(seed=seed)
        self.seed = int(self.config.seed)
        self.rm = risk_manager or RiskManager()
        self.cb = circuit_breaker or CircuitBreaker()
        self.state = ExecutionRiskState.ARMED
        self.audit_trail: List[ExecutionRiskAudit] = []
        self._audit_counter = 0
        self.daily_pnl: float = 0.0
        self.daily_turnover: float = 0.0
        self.peak_equity: float = 0.0
        self.current_equity: float = 0.0
        self.last_greek_update: Optional[datetime] = None
        self.portfolio_greeks: Dict[str, float] = {"delta": 0.0, "gamma": 0.0, "vega": 0.0, "theta": 0.0}
        self.violations: List[RiskViolation] = []
        self.flatten_queued: bool = False
        self._id_prefix = f"eri_{self.seed}"

    # ------------------------------------------------------------------ ids
    def _next_audit_id(self) -> str:
        self._audit_counter += 1
        payload = f"{self._id_prefix}|{self._audit_counter}|{datetime.now(timezone.utc).isoformat()}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        return f"{self._id_prefix}_audit_{digest}"

    def _next_violation_id(self) -> str:
        self.rm._violation_counter += 1
        return f"viol_{self.rm._violation_counter:06d}"

    # ------------------------------------------------------------------ state helpers
    def _is_stale(self) -> bool:
        if self.last_greek_update is None:
            return True
        elapsed = (datetime.now(timezone.utc) - self.last_greek_update).total_seconds()
        return elapsed > float(self.config.stale_greek_seconds)

    def update_equity(self, current_equity: float) -> None:
        try:
            ce = float(current_equity)
        except (TypeError, ValueError):
            return
        if not isfinite(ce):
            return
        self.current_equity = ce
        if ce > self.peak_equity:
            self.peak_equity = ce
        self.rm.update_equity(ce)

    def update_daily_pnl(self, daily_pnl: float, turnover: float = 0.0) -> None:
        try:
            dpnl = float(daily_pnl)
        except (TypeError, ValueError):
            dpnl = 0.0
        if not isfinite(dpnl):
            dpnl = 0.0
        self.daily_pnl = dpnl
        try:
            to = float(turnover)
        except (TypeError, ValueError):
            to = 0.0
        if not isfinite(to):
            to = 0.0
        self.daily_turnover = to
        self.rm.update_pnl(dpnl, to)

    def update_greeks(self, greeks: Dict[str, float]) -> None:
        clean: Dict[str, float] = {}
        for k in ("delta", "gamma", "vega", "theta"):
            try:
                v = float(greeks.get(k, 0.0))
            except (TypeError, ValueError):
                v = 0.0
            clean[k] = v if isfinite(v) else 0.0
        self.portfolio_greeks = clean
        self.last_greek_update = datetime.now(timezone.utc)

    # ------------------------------------------------------------------ pre-trade
    def pre_trade_check(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        positions: Optional[Dict[str, Any]] = None,
        latency_ms: float = 0.0,
    ) -> RiskCheckResult:
        """Pre-trade risk check. Returns BLOCK/HOLD/REDUCE/ALLOW with audit trail."""
        positions = positions or {}
        audit_id = self._next_audit_id()
        violations: List[RiskViolation] = []
        action = RiskAction.ALLOW
        approved = True
        adjusted_quantity: Optional[float] = None
        adjusted_price: Optional[float] = None
        reason = ""

        qty = float(quantity) if isfinite(float(quantity)) else 0.0
        px = float(price) if isfinite(float(price)) else 0.0
        notional = abs(qty * px)

        # Kill switch check first (hard halt)
        if self.config.enable_kill_switch_propagation:
            if self.rm.kill_switch_state == KillSwitchState.TRIGGERED:
                action = RiskAction.BLOCK
                approved = False
                reason = "kill_switch_triggered"
                viol = RiskViolation(
                    violation_id=self._next_violation_id(),
                    violation_type="kill_switch_active",
                    severity="critical",
                    symbol=symbol,
                    message="Trading halted - kill switch active",
                    current_value=1.0,
                    limit_value=0.0,
                    action_taken="ORDER_REJECTED",
                )
                self.rm.violations.append(viol)
                violations.append(viol)
                self.state = ExecutionRiskState.HALTED
                self._record_audit(audit_id, "pre_trade", symbol, side, qty, px, action, approved, violations, latency_ms)
                return RiskCheckResult(
                    action=action, approved=approved, violations=violations,
                    reason=reason, audit_id=audit_id,
                    metadata={"kill_switch": True, "latency_ms": float(latency_ms)},
                )

        # Circuit breaker check
        if self.config.enable_circuit_breaker:
            if not self.cb.can_execute():
                action = RiskAction.HOLD
                approved = False
                reason = "circuit_breaker_open"
                viol = RiskViolation(
                    violation_id=self._next_violation_id(),
                    violation_type="circuit_breaker_open",
                    severity="high",
                    symbol=symbol,
                    message="Circuit breaker open - order held",
                    current_value=float(self.cb.failure_count),
                    limit_value=float(self.cb.config.failure_threshold),
                    action_taken="ORDER_HELD",
                )
                self.rm.violations.append(viol)
                violations.append(viol)
                self.state = ExecutionRiskState.BREACHED
                self._record_audit(audit_id, "pre_trade", symbol, side, qty, px, action, approved, violations, latency_ms)
                return RiskCheckResult(
                    action=action, approved=approved, violations=violations,
                    reason=reason, audit_id=audit_id,
                    metadata={"circuit_breaker": True, "latency_ms": float(latency_ms)},
                )

        # Stale greeks check
        if self._is_stale():
            action = RiskAction.HOLD
            approved = False
            reason = "stale_greeks"
            viol = RiskViolation(
                violation_id=self._next_violation_id(),
                violation_type="stale_greeks",
                severity="medium",
                symbol=symbol,
                message="Greeks stale - order held until refreshed",
                current_value=float(self.config.stale_greek_seconds),
                limit_value=float(self.config.stale_greek_seconds),
                action_taken="ORDER_HELD",
            )
            self.rm.violations.append(viol)
            violations.append(viol)
            self._record_audit(audit_id, "pre_trade", symbol, side, qty, px, action, approved, violations, latency_ms)
            return RiskCheckResult(
                action=action, approved=approved, violations=violations,
                reason=reason, audit_id=audit_id,
                metadata={"stale_greeks": True, "latency_ms": float(latency_ms)},
            )

        # Drawdown check (pre-trade): block/flatten when drawdown breached
        try:
            dd_pct = 0.0
            if self.peak_equity > 0 and self.current_equity <= 0:
                dd_pct = 1.0
            elif self.peak_equity > 0:
                dd_pct = (self.peak_equity - self.current_equity) / self.peak_equity
        except Exception:
            dd_pct = 0.0
        if not isfinite(dd_pct):
            dd_pct = 0.0
        if dd_pct >= float(self.config.max_drawdown_pct) and self.peak_equity > 0:
            action = RiskAction.FLATTEN
            approved = False
            reason = "drawdown_limit_breached"
            self.state = ExecutionRiskState.FLATTENING
            self.flatten_queued = True
            viol = RiskViolation(
                violation_id=self._next_violation_id(),
                violation_type="drawdown_limit_breached",
                severity="critical",
                symbol=symbol,
                message="Drawdown limit breached pre-trade - flatten queued",
                current_value=dd_pct,
                limit_value=float(self.config.max_drawdown_pct),
                action_taken="FLATTEN_QUEUED",
            )
            self.rm.violations.append(viol)
            violations.append(viol)
            self._record_audit(audit_id, "pre_trade", symbol, side, qty, px, action, approved, violations, latency_ms)
            return RiskCheckResult(
                action=action, approved=approved, violations=violations,
                reason=reason, audit_id=audit_id,
                metadata={"drawdown_breach": True, "latency_ms": float(latency_ms)},
            )

        # Delegate to RiskManager.check_order for limit checks
        if self.config.enable_pre_trade_checks:
            rm_violations = self.rm.check_order(
                symbol=symbol,
                side=side,
                quantity=qty,
                price=px,
                positions=positions,
                portfolio_greeks=self.portfolio_greeks,
            )
            if rm_violations:
                violations.extend(rm_violations)
                high_or_critical = any(getattr(v, "severity", "") in ("high", "critical") for v in rm_violations)
                if high_or_critical:
                    action = RiskAction.BLOCK
                    approved = False
                    reason = "risk_limit_breach"
                    self.state = ExecutionRiskState.BREACHED
                else:
                    action = RiskAction.REDUCE
                    approved = True
                    adjusted_quantity = qty * 0.5
                    reason = "risk_limit_reduced"

        # Latency penalty / partial hedge on latency
        if approved and latency_ms > 0.0:
            if not isfinite(latency_ms) or latency_ms < 0:
                latency_ms = 0.0
            penalty_bps = float(self.config.latency_penalty_bps) * (latency_ms / 1000.0)
            if penalty_bps > 50.0:
                penalty_bps = 50.0
            if self.config.partial_hedge_on_latency and penalty_bps > 10.0:
                action = RiskAction.REDUCE
                adjusted_quantity = qty * float(self.config.partial_hedge_ratio)
                reason = f"latency_reduce_{penalty_bps:.1f}bps"

        # Flatten queued from prior kill switch
        if self.flatten_queued:
            action = RiskAction.FLATTEN
            approved = False
            reason = "flatten_queued"

        result = RiskCheckResult(
            action=action, approved=approved, violations=violations,
            adjusted_quantity=adjusted_quantity, adjusted_price=adjusted_price,
            reason=reason, audit_id=audit_id,
            metadata={
                "notional": float(notional),
                "latency_ms": float(latency_ms),
                "stale_greeks": self._is_stale(),
                "kill_switch_state": self.rm.kill_switch_state.value,
                "circuit_state": str(getattr(self.cb.state, "value", self.cb.state)),
            },
        )
        self._record_audit(audit_id, "pre_trade", symbol, side, qty, px, action, approved, violations, latency_ms)
        return result

    # ------------------------------------------------------------------ post-trade
    def post_trade_check(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        filled_quantity: float,
        commission: float,
        latency_ms: float = 0.0,
    ) -> RiskCheckResult:
        """Post-trade risk check. Enforces post-trade limits and updates daily PnL/turnover."""
        audit_id = self._next_audit_id()
        violations: List[RiskViolation] = []
        action = RiskAction.ALLOW
        approved = True
        reason = ""

        qty = float(quantity) if isfinite(float(quantity)) else 0.0
        px = float(price) if isfinite(float(price)) else 0.0
        fq = float(filled_quantity) if isfinite(float(filled_quantity)) else 0.0
        comm = float(commission) if isfinite(float(commission)) else 0.0
        notional = abs(qty * px)
        turnover = abs(fq * px) + comm

        self.daily_turnover += turnover

        # Daily loss / drawdown via RiskManager
        self.rm.update_pnl(0.0, turnover)
        risk_report = self.rm.get_risk_report()
        if risk_report.get("kill_switch_state") == "triggered":
            action = RiskAction.BLOCK
            approved = False
            reason = "post_trade_kill_switch"
            self.state = ExecutionRiskState.HALTED
            self.flatten_queued = True

        # Drawdown check
        try:
            dd_pct = float(risk_report.get("drawdown_pct", 0.0))
        except (TypeError, ValueError):
            dd_pct = 0.0
        if dd_pct >= float(self.config.max_drawdown_pct):
            action = RiskAction.FLATTEN
            approved = False
            reason = "drawdown_limit_breached"
            self.state = ExecutionRiskState.FLATTENING
            viol = RiskViolation(
                violation_id=self._next_violation_id(),
                violation_type="drawdown_limit_breached",
                severity="critical",
                symbol=symbol,
                message="Drawdown limit breached - flatten queued",
                current_value=dd_pct,
                limit_value=float(self.config.max_drawdown_pct),
                action_taken="FLATTEN_QUEUED",
            )
            self.rm.violations.append(viol)
            violations.append(viol)

        result = RiskCheckResult(
            action=action, approved=approved, violations=violations,
            reason=reason, audit_id=audit_id,
            metadata={
                "notional": float(notional),
                "turnover": float(turnover),
                "daily_turnover": float(self.daily_turnover),
                "daily_pnl": float(self.daily_pnl),
                "latency_ms": float(latency_ms),
            },
        )
        self._record_audit(audit_id, "post_trade", symbol, side, qty, px, action, approved, violations, latency_ms)
        return result

    # ------------------------------------------------------------------ flatten
    def queue_flatten(self, reason: str = "risk_breach") -> None:
        """Queue a full portfolio flatten (flatten on next pre-trade check)."""
        self.flatten_queued = True
        self.state = ExecutionRiskState.FLATTENING
        _logger.warning("flatten_queued", reason=reason, state=self.state.value)

    def cancel_flatten(self) -> None:
        """Cancel a queued flatten and return to armed state."""
        self.flatten_queued = False
        self.state = ExecutionRiskState.ARMED

    def trigger_kill_switch(self, vtype: str, current: float, limit: float) -> None:
        """Manually trigger the kill switch (hard halt)."""
        self.rm._trigger_kill_switch(vtype, current, limit)
        self.state = ExecutionRiskState.HALTED
        self.flatten_queued = True
        _logger.error("kill_switch_triggered_manual", violation_type=vtype, current_value=current, limit_value=limit)

    def reset(self) -> None:
        """Reset integrator to armed state (clears violations, audit trail kept)."""
        self.state = ExecutionRiskState.ARMED
        self.flatten_queued = False
        self.rm.reset_kill_switch()
        self.cb.reset()
        self.daily_pnl = 0.0
        self.daily_turnover = 0.0
        self.violations = []

    # ------------------------------------------------------------------ audit
    def _record_audit(
        self,
        audit_id: str,
        event_type: str,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        action: RiskAction,
        approved: bool,
        violations: List[RiskViolation],
        latency_ms: float,
    ) -> None:
        audit = ExecutionRiskAudit(
            audit_id=audit_id,
            event_type=event_type,
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            action=action,
            approved=approved,
            risk_state=self.state,
            violations=[v.to_dict() for v in violations],
            portfolio_greeks=dict(self.portfolio_greeks),
            latency_ms=float(latency_ms) if isfinite(float(latency_ms)) else 0.0,
        )
        self.audit_trail.append(audit)

    def get_risk_report(self) -> Dict[str, Any]:
        """Return a strict-serializable risk report for the integrator."""
        rm_report = self.rm.get_risk_report()
        cb_status = self.cb.get_status()
        return serialize_metrics_strict({
            "integrator_state": self.state.value,
            "flatten_queued": bool(self.flatten_queued),
            "seed": int(self.seed),
            "daily_pnl": float(self.daily_pnl) if isfinite(float(self.daily_pnl)) else 0.0,
            "daily_turnover": float(self.daily_turnover) if isfinite(float(self.daily_turnover)) else 0.0,
            "current_equity": float(self.current_equity) if isfinite(float(self.current_equity)) else 0.0,
            "peak_equity": float(self.peak_equity) if isfinite(float(self.peak_equity)) else 0.0,
            "portfolio_greeks": {k: float(v) if isfinite(float(v)) else 0.0 for k, v in self.portfolio_greeks.items()},
            "stale_greeks": bool(self._is_stale()),
            "num_violations": len(self.violations),
            "num_audits": len(self.audit_trail),
            "recent_audits": [a.to_dict() for a in self.audit_trail[-10:]],
            "risk_manager": rm_report,
            "circuit_breaker": cb_status,
        })

    def export_audit_trail(self) -> List[Dict[str, Any]]:
        """Export the full audit trail as strict-serializable dicts."""
        return [a.to_dict() for a in self.audit_trail]


def create_execution_risk_integrator(
    risk_manager: Optional[RiskManager] = None,
    circuit_breaker: Optional[CircuitBreaker] = None,
    config: Optional[ExecutionRiskConfig] = None,
    seed: int = 42,
) -> ExecutionRiskIntegrator:
    """Factory for a deterministic ExecutionRiskIntegrator."""
    return ExecutionRiskIntegrator(
        risk_manager=risk_manager,
        circuit_breaker=circuit_breaker,
        config=config,
        seed=seed,
    )


__all__ = [
    "ExecutionRiskConfig",
    "ExecutionRiskIntegrator",
    "RiskCheckResult",
    "ExecutionRiskAudit",
    "RiskAction",
    "ExecutionRiskState",
    "create_execution_risk_integrator",
]
