"""Risk limits, kill switches, and portfolio risk controls."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from math import isfinite
from typing import Any, Dict, List, Optional

from ..errors import RiskLimitError, get_logger
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import clamp


_logger = get_logger(__name__)


class KillSwitchState(str, Enum):
    ARMED = "armed"
    TRIGGERED = "triggered"
    DISABLED = "disabled"


@dataclass
class RiskLimits:
    """Per-symbol and portfolio-level risk limits."""

    # Per symbol
    max_delta: float = 100000.0
    max_gamma: float = 10000.0
    max_vega: float = 50000.0
    max_theta: float = 10000.0
    max_notional_per_symbol: float = 1000000.0
    max_position_qty_per_symbol: float = 1000.0

    # Portfolio level
    max_portfolio_delta: float = 500000.0
    max_portfolio_gamma: float = 50000.0
    max_portfolio_vega: float = 200000.0
    max_portfolio_notional: float = 5000000.0
    max_leverage: float = 3.0

    # PnL / drawdown
    max_daily_loss: float = 50000.0
    max_drawdown_pct: float = 0.15
    max_drawdown_absolute: float = 150000.0

    # Turnover
    max_turnover_daily: float = 10000000.0
    max_turnover_pct: float = 2.0

    # Concentration
    max_single_symbol_pct: float = 0.25
    max_correlation_exposure: float = 0.7

    def __post_init__(self) -> None:
        for name in [
            "max_delta",
            "max_gamma",
            "max_vega",
            "max_theta",
            "max_notional_per_symbol",
            "max_position_qty_per_symbol",
            "max_portfolio_delta",
            "max_portfolio_gamma",
            "max_portfolio_vega",
            "max_portfolio_notional",
            "max_leverage",
            "max_daily_loss",
            "max_drawdown_pct",
            "max_drawdown_absolute",
            "max_turnover_daily",
            "max_turnover_pct",
            "max_single_symbol_pct",
            "max_correlation_exposure",
        ]:
            val = getattr(self, name)
            if not isfinite(float(val)) or float(val) < 0:
                raise RiskLimitError(f"{name} must be finite and >= 0", context={"limit": name, "value": val})
        if self.max_leverage <= 0:
            raise RiskLimitError("max_leverage must be > 0", context={"max_leverage": self.max_leverage})
        if self.max_drawdown_pct <= 0 or self.max_drawdown_pct > 1.0:
            raise RiskLimitError("max_drawdown_pct must be in (0,1]", context={"max_drawdown_pct": self.max_drawdown_pct})
        if self.max_single_symbol_pct <= 0 or self.max_single_symbol_pct > 1.0:
            raise RiskLimitError("max_single_symbol_pct must be in (0,1]", context={"max_single_symbol_pct": self.max_single_symbol_pct})

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "max_delta": float(self.max_delta),
            "max_gamma": float(self.max_gamma),
            "max_vega": float(self.max_vega),
            "max_theta": float(self.max_theta),
            "max_notional_per_symbol": float(self.max_notional_per_symbol),
            "max_position_qty_per_symbol": float(self.max_position_qty_per_symbol),
            "max_portfolio_delta": float(self.max_portfolio_delta),
            "max_portfolio_gamma": float(self.max_portfolio_gamma),
            "max_portfolio_vega": float(self.max_portfolio_vega),
            "max_portfolio_notional": float(self.max_portfolio_notional),
            "max_leverage": float(self.max_leverage),
            "max_daily_loss": float(self.max_daily_loss),
            "max_drawdown_pct": float(self.max_drawdown_pct),
            "max_drawdown_absolute": float(self.max_drawdown_absolute),
            "max_turnover_daily": float(self.max_turnover_daily),
            "max_turnover_pct": float(self.max_turnover_pct),
            "max_single_symbol_pct": float(self.max_single_symbol_pct),
            "max_correlation_exposure": float(self.max_correlation_exposure),
        })


@dataclass
class RiskViolation:
    """Risk limit violation record."""

    violation_id: str
    violation_type: str
    severity: str  # low/medium/high/critical
    symbol: Optional[str]
    message: str
    current_value: float
    limit_value: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    action_taken: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "violation_id": self.violation_id,
            "violation_type": self.violation_type,
            "severity": self.severity,
            "symbol": self.symbol,
            "message": self.message,
            "current_value": float(self.current_value),
            "limit_value": float(self.limit_value),
            "timestamp": self.timestamp.isoformat(),
            "action_taken": self.action_taken,
        })


class RiskManager:
    """Portfolio risk manager with kill switches."""

    def __init__(self, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()
        self.kill_switch_state = KillSwitchState.ARMED
        self.violations: List[RiskViolation] = []
        self.daily_pnl: float = 0.0
        self.daily_turnover: float = 0.0
        self.peak_equity: float = 0.0
        self.current_equity: float = 0.0
        self.last_reset: datetime = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        self._violation_counter = 0

    def _generate_violation_id(self) -> str:
        self._violation_counter += 1
        return f"viol_{self._violation_counter:06d}"

    def reset_daily_if_needed(self) -> None:
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if today_start > self.last_reset:
            self.daily_pnl = 0.0
            self.daily_turnover = 0.0
            self.last_reset = today_start

    def check_kill_switch(self) -> bool:
        """Check if kill switch should trigger. Returns True if triggered."""
        if self.kill_switch_state == KillSwitchState.DISABLED:
            return False
        self.reset_daily_if_needed()
        # Check daily loss
        if self.daily_pnl < -abs(self.limits.max_daily_loss):
            self._trigger_kill_switch("daily_loss_limit_breached", abs(self.daily_pnl), self.limits.max_daily_loss)
            return True
        # Check drawdown
        if self.peak_equity > 0 and self.current_equity > 0:
            dd_pct = (self.peak_equity - self.current_equity) / self.peak_equity
            if dd_pct >= self.limits.max_drawdown_pct:
                self._trigger_kill_switch("drawdown_pct_limit_breached", dd_pct, self.limits.max_drawdown_pct)
                return True
            dd_abs = self.peak_equity - self.current_equity
            if dd_abs >= self.limits.max_drawdown_absolute:
                self._trigger_kill_switch("drawdown_absolute_limit_breached", dd_abs, self.limits.max_drawdown_absolute)
                return True
        return self.kill_switch_state == KillSwitchState.TRIGGERED

    def _trigger_kill_switch(self, vtype: str, current: float, limit: float) -> None:
        if self.kill_switch_state == KillSwitchState.TRIGGERED:
            return
        self.kill_switch_state = KillSwitchState.TRIGGERED
        # Neutralize non-finite values so the violation record itself stays
        # serializable through serialize_metrics_strict (allow_nan=False).
        cur_f = float(current) if isfinite(float(current)) else 0.0
        lim_f = float(limit) if isfinite(float(limit)) else 0.0
        viol = RiskViolation(
            violation_id=self._generate_violation_id(),
            violation_type=vtype,
            severity="critical",
            symbol=None,
            message=f"Kill switch triggered: {vtype}",
            current_value=cur_f,
            limit_value=lim_f,
            action_taken="KILL_SWITCH_ACTIVATED",
        )
        self.violations.append(viol)
        _logger.error("kill_switch_triggered", violation_type=vtype, current_value=cur_f, limit_value=lim_f)

    def check_order(self, symbol: str, side: str, quantity: float, price: float, positions: Dict[str, Any],
                    portfolio_greeks: Optional[Dict[str, float]] = None) -> List[RiskViolation]:
        """Pre-trade risk checks."""
        violations = []
        if self.kill_switch_state == KillSwitchState.TRIGGERED:
            viol = RiskViolation(
                violation_id=self._generate_violation_id(),
                violation_type="kill_switch_active",
                severity="critical",
                symbol=symbol,
                message="Trading halted - kill switch active",
                current_value=1.0,
                limit_value=0.0,
                action_taken="ORDER_REJECTED",
            )
            self.violations.append(viol)
            violations.append(viol)
            return violations

        if not isfinite(quantity) or quantity <= 0:
            viol = RiskViolation(
                violation_id=self._generate_violation_id(),
                violation_type="invalid_quantity",
                severity="high",
                symbol=symbol,
                message="Order quantity must be positive and finite",
                current_value=float(quantity),
                limit_value=0.0,
                action_taken="ORDER_REJECTED",
            )
            self.violations.append(viol)
            violations.append(viol)
            return violations
        if not isfinite(price) or price <= 0:
            viol = RiskViolation(
                violation_id=self._generate_violation_id(),
                violation_type="invalid_price",
                severity="high",
                symbol=symbol,
                message="Order price must be positive and finite",
                current_value=float(price),
                limit_value=0.0,
                action_taken="ORDER_REJECTED",
            )
            self.violations.append(viol)
            violations.append(viol)
            return violations

        qty = float(quantity)
        px = float(price)
        try:
            notional = qty * px
        except Exception:
            notional = 0.0
        if not isfinite(notional):
            notional = 0.0
        if abs(notional) > 1e18:
            notional = 1e18 if notional > 0 else -1e18

        # Per-symbol notional
        if notional > self.limits.max_notional_per_symbol:
            viol = RiskViolation(
                violation_id=self._generate_violation_id(),
                violation_type="notional_per_symbol",
                severity="high",
                symbol=symbol,
                message="Order notional exceeds per-symbol limit",
                current_value=float(notional),
                limit_value=float(self.limits.max_notional_per_symbol),
                action_taken="ORDER_REDUCED_OR_REJECTED",
            )
            self.violations.append(viol)
            violations.append(viol)

        # Position quantity
        if qty > self.limits.max_position_qty_per_symbol:
            viol = RiskViolation(
                violation_id=self._generate_violation_id(),
                violation_type="position_qty_per_symbol",
                severity="high",
                symbol=symbol,
                message="Order quantity exceeds per-symbol limit",
                current_value=float(qty),
                limit_value=float(self.limits.max_position_qty_per_symbol),
                action_taken="ORDER_REDUCED_OR_REJECTED",
            )
            self.violations.append(viol)
            violations.append(viol)

        # Portfolio notional
        if self.current_equity > 0:
            try:
                existing_notional = sum(getattr(p, "market_value_abs", 0) for p in positions.values())
            except Exception:
                existing_notional = 0.0
            if not isfinite(existing_notional):
                existing_notional = 0.0
            total_notional = existing_notional + notional
            if not isfinite(total_notional):
                total_notional = 0.0
            if total_notional > self.limits.max_portfolio_notional:
                viol = RiskViolation(
                    violation_id=self._generate_violation_id(),
                    violation_type="portfolio_notional",
                    severity="high",
                    symbol=symbol,
                    message="Portfolio notional exceeds limit",
                    current_value=float(total_notional),
                    limit_value=float(self.limits.max_portfolio_notional),
                    action_taken="ORDER_REDUCED_OR_REJECTED",
                )
                self.violations.append(viol)
                violations.append(viol)
            # Concentration
            if total_notional > 0 and notional / total_notional > self.limits.max_single_symbol_pct:
                viol = RiskViolation(
                    violation_id=self._generate_violation_id(),
                    violation_type="concentration",
                    severity="medium",
                    symbol=symbol,
                    message="Single symbol concentration exceeds limit",
                    current_value=float(notional / total_notional),
                    limit_value=float(self.limits.max_single_symbol_pct),
                    action_taken="ORDER_REDUCED_OR_REJECTED",
                )
                self.violations.append(viol)
                violations.append(viol)

        # Greeks checks if provided
        if portfolio_greeks:
            for greek, val in [("delta", portfolio_greeks.get("delta", 0)), ("gamma", portfolio_greeks.get("gamma", 0)), ("vega", portfolio_greeks.get("vega", 0))]:
                if greek == "delta" and abs(val) > self.limits.max_portfolio_delta:
                    viol = RiskViolation(
                        violation_id=self._generate_violation_id(),
                        violation_type="portfolio_delta",
                        severity="high",
                        symbol=None,
                        message=f"Portfolio {greek} exceeds limit",
                        current_value=float(val),
                        limit_value=float(self.limits.max_portfolio_delta),
                        action_taken="ORDER_REDUCED_OR_REJECTED",
                    )
                    self.violations.append(viol)
                    violations.append(viol)
                elif greek == "gamma" and abs(val) > self.limits.max_portfolio_gamma:
                    viol = RiskViolation(
                        violation_id=self._generate_violation_id(),
                        violation_type="portfolio_gamma",
                        severity="high",
                        symbol=None,
                        message=f"Portfolio {greek} exceeds limit",
                        current_value=float(val),
                        limit_value=float(self.limits.max_portfolio_gamma),
                        action_taken="ORDER_REDUCED_OR_REJECTED",
                    )
                    self.violations.append(viol)
                    violations.append(viol)
                elif greek == "vega" and abs(val) > self.limits.max_portfolio_vega:
                    viol = RiskViolation(
                        violation_id=self._generate_violation_id(),
                        violation_type="portfolio_vega",
                        severity="high",
                        symbol=None,
                        message=f"Portfolio {greek} exceeds limit",
                        current_value=float(val),
                        limit_value=float(self.limits.max_portfolio_vega),
                        action_taken="ORDER_REDUCED_OR_REJECTED",
                    )
                    self.violations.append(viol)
                    violations.append(viol)

        return violations

    def update_pnl(self, daily_pnl: float, turnover: float) -> None:
        self.reset_daily_if_needed()
        if isfinite(daily_pnl):
            self.daily_pnl += float(daily_pnl)
        if isfinite(turnover):
            self.daily_turnover += float(turnover)

    def update_equity(self, current_equity: float):
        if not isfinite(current_equity):
            return
        self.current_equity = float(current_equity)
        if self.current_equity > self.peak_equity:
            self.peak_equity = self.current_equity

    def arm_kill_switch(self) -> None:
        if self.kill_switch_state != KillSwitchState.DISABLED:
            self.kill_switch_state = KillSwitchState.ARMED

    def disable_kill_switch(self) -> None:
        self.kill_switch_state = KillSwitchState.DISABLED

    def reset_kill_switch(self) -> None:
        self.kill_switch_state = KillSwitchState.ARMED
        self.daily_pnl = 0.0
        self.daily_turnover = 0.0

    def get_risk_report(self) -> Dict[str, Any]:
        dd_pct = 0.0
        if self.peak_equity > 0 and self.current_equity > 0:
            dd_pct = (self.peak_equity - self.current_equity) / self.peak_equity
        return serialize_metrics_strict({
            "kill_switch_state": self.kill_switch_state.value,
            "limits": self.limits.to_dict(),
            "daily_pnl": float(self.daily_pnl),
            "daily_turnover": float(self.daily_turnover),
            "current_equity": float(self.current_equity),
            "peak_equity": float(self.peak_equity),
            "drawdown_pct": float(dd_pct),
            "num_violations": len(self.violations),
            "recent_violations": [v.to_dict() for v in self.violations[-10:]],
        })
