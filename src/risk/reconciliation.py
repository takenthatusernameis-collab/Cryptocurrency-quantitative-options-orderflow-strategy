"""Position, PnL and margin reconciliation with auto-halt."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Dict, List, Optional

from ..errors import RiskLimitError, get_logger
from ..telemetry import serialize_metrics_strict

_logger = get_logger(__name__)


class DiscrepancySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class PositionReconciliation:
    symbol: str
    local_quantity: float
    exchange_quantity: float
    local_notional: float
    exchange_notional: float
    quantity_diff: float
    notional_diff: float
    matched: bool
    severity: DiscrepancySeverity = DiscrepancySeverity.LOW
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "symbol": self.symbol,
            "local_quantity": float(self.local_quantity),
            "exchange_quantity": float(self.exchange_quantity),
            "local_notional": float(self.local_notional),
            "exchange_notional": float(self.exchange_notional),
            "quantity_diff": float(self.quantity_diff),
            "notional_diff": float(self.notional_diff),
            "matched": bool(self.matched),
            "severity": self.severity.value,
            "timestamp": self.timestamp.isoformat(),
        })


@dataclass
class MarginCheckResult:
    required_margin: float
    available_margin: float
    margin_ratio: float
    sufficient: bool
    warning_threshold: float = 1.5
    critical_threshold: float = 1.2
    action: str = "ok"  # ok/warn/reduce/halt
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "required_margin": float(self.required_margin),
            "available_margin": float(self.available_margin),
            "margin_ratio": float(self.margin_ratio),
            "sufficient": bool(self.sufficient),
            "warning_threshold": float(self.warning_threshold),
            "critical_threshold": float(self.critical_threshold),
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
        })


class ReconciliationEngine:
    """Reconciles positions, PnL and margin with auto-halt on critical mismatch."""

    def __init__(self, auto_halt_on_critical: bool = True,
                 quantity_tolerance: float = 1e-9,
                 notional_tolerance: float = 1.0):
        self.auto_halt_on_critical = bool(auto_halt_on_critical)
        self.quantity_tolerance = float(quantity_tolerance)
        self.notional_tolerance = float(notional_tolerance)
        self.position_reconciliations: List[PositionReconciliation] = []
        self.margin_checks: List[MarginCheckResult] = []
        self.halted = False
        self.halt_reason = ""
        self.discrepancy_alerts: List[Dict[str, Any]] = []

    def reconcile_positions(self, local_positions: Dict[str, Dict[str, float]],
                           exchange_positions: Dict[str, Dict[str, float]]) -> List[PositionReconciliation]:
        results = []
        all_symbols = set(local_positions.keys()) | set(exchange_positions.keys())

        for symbol in all_symbols:
            local = local_positions.get(symbol, {"quantity": 0.0, "notional": 0.0})
            exchange = exchange_positions.get(symbol, {"quantity": 0.0, "notional": 0.0})

            local_qty = float(local.get("quantity", 0.0))
            exchange_qty = float(exchange.get("quantity", 0.0))
            local_not = float(local.get("notional", 0.0))
            exchange_not = float(exchange.get("notional", 0.0))

            qty_diff = abs(local_qty - exchange_qty)
            not_diff = abs(local_not - exchange_not)
            matched = qty_diff < self.quantity_tolerance and not_diff < self.notional_tolerance

            severity = DiscrepancySeverity.LOW
            if not matched:
                if qty_diff > 1.0 or not_diff > 10000.0:
                    severity = DiscrepancySeverity.CRITICAL
                elif qty_diff > 0.1 or not_diff > 1000.0:
                    severity = DiscrepancySeverity.HIGH
                elif qty_diff > 0.01 or not_diff > 100.0:
                    severity = DiscrepancySeverity.MEDIUM

            rec = PositionReconciliation(
                symbol=symbol,
                local_quantity=local_qty,
                exchange_quantity=exchange_qty,
                local_notional=local_not,
                exchange_notional=exchange_not,
                quantity_diff=qty_diff,
                notional_diff=not_diff,
                matched=matched,
                severity=severity,
            )
            results.append(rec)
            self.position_reconciliations.append(rec)

            if not matched:
                alert = {
                    "type": "position_discrepancy",
                    "symbol": symbol,
                    "severity": severity.value,
                    "quantity_diff": qty_diff,
                    "notional_diff": not_diff,
                    "timestamp": rec.timestamp.isoformat(),
                }
                self.discrepancy_alerts.append(alert)
                _logger.warning("position_discrepancy", **alert)

                if severity == DiscrepancySeverity.CRITICAL and self.auto_halt_on_critical:
                    self.halt_trading(f"Critical position discrepancy on {symbol}: qty_diff={qty_diff}")

        return results

    def check_margin(self, required_margin: float, available_margin: float,
                     warning_threshold: float = 1.5, critical_threshold: float = 1.2) -> MarginCheckResult:
        if not isfinite(required_margin) or required_margin <= 0:
            required_margin = 0.0
        if not isfinite(available_margin) or available_margin <= 0:
            available_margin = 0.0

        if required_margin > 0:
            margin_ratio = available_margin / required_margin
        else:
            margin_ratio = float('inf')

        sufficient = margin_ratio >= critical_threshold

        action = "ok"
        if margin_ratio < critical_threshold:
            action = "halt"
            if self.auto_halt_on_critical:
                self.halt_trading(f"Insufficient margin: ratio={margin_ratio:.4f}")
        elif margin_ratio < warning_threshold:
            action = "reduce"
            _logger.warning("margin_warning", margin_ratio=margin_ratio, action=action)

        result = MarginCheckResult(
            required_margin=required_margin,
            available_margin=available_margin,
            margin_ratio=margin_ratio,
            sufficient=sufficient,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold,
            action=action,
        )
        self.margin_checks.append(result)
        return result

    def reconcile_pnl(self, local_pnl: float, exchange_pnl: float, tolerance: float = 1.0) -> Dict[str, Any]:
        local_pnl_f = float(local_pnl) if isfinite(local_pnl) else 0.0
        exchange_pnl_f = float(exchange_pnl) if isfinite(exchange_pnl) else 0.0
        diff = abs(local_pnl_f - exchange_pnl_f)
        matched = diff < tolerance

        result = {
            "local_pnl": local_pnl_f,
            "exchange_pnl": exchange_pnl_f,
            "difference": diff,
            "matched": bool(matched),
            "tolerance": float(tolerance),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if not matched:
            alert = {"type": "pnl_discrepancy", "severity": "high" if diff > 100 else "medium", **result}
            self.discrepancy_alerts.append(alert)
            _logger.warning("pnl_discrepancy", **result)
            if diff > 10000 and self.auto_halt_on_critical:
                self.halt_trading(f"Critical PnL discrepancy: diff={diff}")

        return serialize_metrics_strict(result)

    def halt_trading(self, reason: str) -> None:
        self.halted = True
        self.halt_reason = str(reason)
        _logger.critical("reconciliation_halt", reason=reason)

    def resume_trading(self) -> None:
        self.halted = False
        self.halt_reason = ""
        _logger.info("reconciliation_resumed")

    def get_audit_report(self) -> Dict[str, Any]:
        unmatched_positions = sum(1 for r in self.position_reconciliations if not r.matched)
        critical_unmatched = sum(1 for r in self.position_reconciliations if not r.matched and r.severity == DiscrepancySeverity.CRITICAL)

        return serialize_metrics_strict({
            "halted": bool(self.halted),
            "halt_reason": self.halt_reason,
            "total_position_reconciliations": len(self.position_reconciliations),
            "unmatched_positions": unmatched_positions,
            "critical_unmatched": critical_unmatched,
            "total_margin_checks": len(self.margin_checks),
            "total_alerts": len(self.discrepancy_alerts),
            "alerts": self.discrepancy_alerts[-20:],  # Last 20 alerts
            "recent_position_recons": [r.to_dict() for r in self.position_reconciliations[-10:]],
            "recent_margin_checks": [m.to_dict() for m in self.margin_checks[-10:]],
        })
