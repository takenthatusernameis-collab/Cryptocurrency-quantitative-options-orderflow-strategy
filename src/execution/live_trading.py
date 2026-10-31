"""Live/Paper Trading Engine with order lifecycle management."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Dict, List, Optional

from ..errors import OrderError, RiskLimitError, get_logger
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import clamp
from .engine import ExecutionEngine
from .orders import Order, OrderSide, OrderStatus, OrderType, TimeInForce

_logger = get_logger(__name__)


class OrderStateMachine(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    REPLACED = "replaced"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class LiveOrder:
    """Live trading order with full lifecycle tracking."""
    order_id: str
    client_order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    state: OrderStateMachine = OrderStateMachine.PENDING
    filled_quantity: float = 0.0
    remaining_quantity: float = 0.0
    avg_fill_price: float = 0.0
    commission: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    fills: List[Dict[str, Any]] = field(default_factory=list)
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    idempotency_key: str = ""

    def __post_init__(self):
        if not self.remaining_quantity:
            self.remaining_quantity = float(self.quantity)
        if not self.idempotency_key:
            payload = f"{self.client_order_id}|{self.symbol}|{self.side.value}|{self.quantity}"
            self.idempotency_key = hashlib.sha256(payload.encode()).hexdigest()[:16]


@dataclass
class OrderReconciliation:
    """Reconciliation result between local and exchange state."""
    order_id: str
    local_state: OrderStateMachine
    exchange_state: str
    matched: bool
    discrepancy: List[str] = field(default_factory=list)
    fills_matched: bool = True
    quantity_match: bool = True
    price_match: bool = True
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "order_id": self.order_id,
            "local_state": self.local_state.value,
            "exchange_state": self.exchange_state,
            "matched": bool(self.matched),
            "discrepancy": self.discrepancy,
            "fills_matched": bool(self.fills_matched),
            "quantity_match": bool(self.quantity_match),
            "price_match": bool(self.price_match),
            "timestamp": self.timestamp.isoformat(),
        })


class LiveTradingEngine:
    """Production-grade live/paper trading engine."""

    def __init__(self, execution_engine: Optional[ExecutionEngine] = None,
                 risk_integrator: Optional[Any] = None,
                 paper_mode: bool = True, seed: int = 42):
        self.execution_engine = execution_engine or ExecutionEngine(seed=seed)
        self.risk_integrator = risk_integrator
        self.paper_mode = bool(paper_mode)
        self.seed = int(seed)
        self.orders: Dict[str, LiveOrder] = {}
        self.client_order_map: Dict[str, str] = {}
        self.fills: List[Dict[str, Any]] = []
        self.reconciliations: List[OrderReconciliation] = []
        self._order_counter = 0
        self._fill_counter = 0
        self.halted = False
        self.halt_reason = ""

    def _generate_order_id(self) -> str:
        self._order_counter += 1
        payload = f"{self.seed}|live|{self._order_counter}|{time.time()}"
        digest = hashlib.sha256(payload.encode()).hexdigest()[:16]
        return f"live_{digest}"

    def _generate_client_order_id(self, prefix: str = "cli") -> str:
        self._order_counter += 1
        payload = f"{self.seed}|{prefix}|{self._order_counter}"
        digest = hashlib.sha256(payload.encode()).hexdigest()[:12]
        return f"{prefix}_{digest}"

    def submit_order(self, symbol: str, side: OrderSide, quantity: float,
                     order_type: OrderType = OrderType.MARKET,
                     price: Optional[float] = None,
                     time_in_force: TimeInForce = TimeInForce.GTC,
                     tags: Optional[Dict[str, str]] = None) -> LiveOrder:
        if self.halted:
            raise OrderError(f"Trading halted: {self.halt_reason}", context={"halt_reason": self.halt_reason})

        if not isfinite(quantity) or quantity <= 0:
            raise OrderError("quantity must be positive and finite", context={"quantity": quantity})

        # Risk check if integrator available
        if self.risk_integrator is not None:
            try:
                risk_result = self.risk_integrator.pre_trade_check(
                    symbol, side.value, quantity, price or 0.0, {}, latency_ms=1.0
                )
                if not risk_result.approved or risk_result.action.value in ("block", "halt"):
                    raise RiskLimitError(f"Order blocked by risk: {risk_result.reason}",
                                       context={"action": risk_result.action.value, "reason": risk_result.reason})
                if risk_result.adjusted_quantity is not None:
                    quantity = float(risk_result.adjusted_quantity)
            except (RiskLimitError, OrderError):
                raise
            except Exception as e:
                _logger.warning("risk_check_error", error=str(e))

        order_id = self._generate_order_id()
        client_order_id = self._generate_client_order_id()

        live_order = LiveOrder(
            order_id=order_id,
            client_order_id=client_order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=float(quantity),
            price=float(price) if price is not None else None,
            time_in_force=time_in_force,
            state=OrderStateMachine.SUBMITTED,
            remaining_quantity=float(quantity),
            tags=tags or {},
        )
        live_order.updated_at = datetime.now(timezone.utc)

        self.orders[order_id] = live_order
        self.client_order_map[client_order_id] = order_id

        _logger.info("order_submitted", order_id=order_id, symbol=symbol, side=side.value, quantity=quantity)
        return live_order

    def replace_order(self, order_id: str, quantity: Optional[float] = None,
                      price: Optional[float] = None) -> LiveOrder:
        if order_id not in self.orders:
            raise OrderError(f"Order {order_id} not found", context={"order_id": order_id})

        order = self.orders[order_id]
        if order.state in (OrderStateMachine.FILLED, OrderStateMachine.CANCELLED, OrderStateMachine.REJECTED):
            raise OrderError(f"Cannot replace order in state {order.state.value}",
                           context={"order_id": order_id, "state": order.state.value})

        if quantity is not None:
            if not isfinite(quantity) or quantity <= 0:
                raise OrderError("quantity must be positive and finite", context={"quantity": quantity})
            order.quantity = float(quantity)
            order.remaining_quantity = float(quantity) - order.filled_quantity
        if price is not None:
            order.price = float(price)

        order.state = OrderStateMachine.REPLACED
        order.updated_at = datetime.now(timezone.utc)
        _logger.info("order_replaced", order_id=order_id)
        return order

    def cancel_order(self, order_id: str) -> LiveOrder:
        if order_id not in self.orders:
            raise OrderError(f"Order {order_id} not found", context={"order_id": order_id})

        order = self.orders[order_id]
        if order.state == OrderStateMachine.FILLED:
            raise OrderError("Cannot cancel filled order", context={"order_id": order_id})

        order.state = OrderStateMachine.CANCELLED
        order.updated_at = datetime.now(timezone.utc)
        order.remaining_quantity = 0.0
        _logger.info("order_cancelled", order_id=order_id)
        return order

    def process_fill(self, order_id: str, fill_quantity: float, fill_price: float,
                     commission: float = 0.0) -> Dict[str, Any]:
        if order_id not in self.orders:
            raise OrderError(f"Order {order_id} not found", context={"order_id": order_id})

        order = self.orders[order_id]
        if not isfinite(fill_quantity) or fill_quantity <= 0:
            raise OrderError("fill_quantity must be positive and finite", context={"fill_quantity": fill_quantity})
        if not isfinite(fill_price) or fill_price <= 0:
            raise OrderError("fill_price must be positive and finite", context={"fill_price": fill_price})

        fill_qty = min(float(fill_quantity), order.remaining_quantity)
        self._fill_counter += 1
        fill = {
            "fill_id": f"fill_{self._fill_counter:08d}",
            "order_id": order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": fill_qty,
            "price": float(fill_price),
            "commission": float(commission) if isfinite(commission) else 0.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.fills.append(fill)
        order.fills.append(fill)
        order.filled_quantity += fill_qty
        order.remaining_quantity = max(0.0, order.quantity - order.filled_quantity)
        order.commission += fill["commission"]

        # Update avg fill price
        total_notional = order.avg_fill_price * (order.filled_quantity - fill_qty) + fill_price * fill_qty
        if order.filled_quantity > 0:
            order.avg_fill_price = total_notional / order.filled_quantity

        if order.remaining_quantity <= 1e-18:
            order.state = OrderStateMachine.FILLED
        elif order.filled_quantity > 0:
            order.state = OrderStateMachine.PARTIALLY_FILLED

        order.updated_at = datetime.now(timezone.utc)
        _logger.info("order_filled", order_id=order_id, fill_qty=fill_qty, fill_price=fill_price)
        return fill

    def reconcile_order(self, order_id: str, exchange_state: str,
                        exchange_filled_qty: float = 0.0,
                        exchange_avg_price: float = 0.0) -> OrderReconciliation:
        if order_id not in self.orders:
            raise OrderError(f"Order {order_id} not found", context={"order_id": order_id})

        order = self.orders[order_id]
        discrepancies = []
        fills_matched = True
        quantity_match = abs(order.filled_quantity - float(exchange_filled_qty)) < 1e-9
        price_match = abs(order.avg_fill_price - float(exchange_avg_price)) < 1e-6 if exchange_avg_price > 0 else True

        if not quantity_match:
            discrepancies.append(f"quantity_mismatch: local={order.filled_quantity} exchange={exchange_filled_qty}")
        if not price_match:
            discrepancies.append(f"price_mismatch: local={order.avg_fill_price} exchange={exchange_avg_price}")

        # Check state consistency
        expected_exchange_states = {
            OrderStateMachine.FILLED: ["filled", "FILLED"],
            OrderStateMachine.PARTIALLY_FILLED: ["partially_filled", "PARTIALLY_FILLED", "partial"],
            OrderStateMachine.CANCELLED: ["cancelled", "CANCELLED", "canceled"],
            OrderStateMachine.REJECTED: ["rejected", "REJECTED"],
        }
        state_ok = True
        if order.state in expected_exchange_states:
            if exchange_state not in expected_exchange_states[order.state]:
                # Allow some flexibility
                state_ok = False
                discrepancies.append(f"state_mismatch: local={order.state.value} exchange={exchange_state}")

        reconciliation = OrderReconciliation(
            order_id=order_id,
            local_state=order.state,
            exchange_state=str(exchange_state),
            matched=(len(discrepancies) == 0),
            discrepancy=discrepancies,
            fills_matched=fills_matched,
            quantity_match=quantity_match,
            price_match=price_match,
        )
        self.reconciliations.append(reconciliation)
        return reconciliation

    def halt_trading(self, reason: str) -> None:
        self.halted = True
        self.halt_reason = str(reason)
        _logger.critical("trading_halted", reason=reason)

    def resume_trading(self) -> None:
        self.halted = False
        self.halt_reason = ""
        _logger.info("trading_resumed")

    def get_order_status(self, order_id: str) -> Dict[str, Any]:
        if order_id not in self.orders:
            raise OrderError(f"Order {order_id} not found", context={"order_id": order_id})
        order = self.orders[order_id]
        return serialize_metrics_strict({
            "order_id": order.order_id,
            "client_order_id": order.client_order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "order_type": order.order_type.value,
            "quantity": float(order.quantity),
            "price": float(order.price) if order.price is not None else None,
            "state": order.state.value,
            "filled_quantity": float(order.filled_quantity),
            "remaining_quantity": float(order.remaining_quantity),
            "avg_fill_price": float(order.avg_fill_price),
            "commission": float(order.commission),
            "created_at": order.created_at.isoformat(),
            "updated_at": order.updated_at.isoformat(),
            "num_fills": len(order.fills),
            "idempotency_key": order.idempotency_key,
        })

    def get_trading_summary(self) -> Dict[str, Any]:
        filled_orders = sum(1 for o in self.orders.values() if o.state == OrderStateMachine.FILLED)
        partial_orders = sum(1 for o in self.orders.values() if o.state == OrderStateMachine.PARTIALLY_FILLED)
        cancelled_orders = sum(1 for o in self.orders.values() if o.state == OrderStateMachine.CANCELLED)
        rejected_orders = sum(1 for o in self.orders.values() if o.state == OrderStateMachine.REJECTED)
        matched_recons = sum(1 for r in self.reconciliations if r.matched)

        return serialize_metrics_strict({
            "paper_mode": bool(self.paper_mode),
            "halted": bool(self.halted),
            "halt_reason": self.halt_reason,
            "total_orders": len(self.orders),
            "filled_orders": filled_orders,
            "partially_filled_orders": partial_orders,
            "cancelled_orders": cancelled_orders,
            "rejected_orders": rejected_orders,
            "total_fills": len(self.fills),
            "total_reconciliations": len(self.reconciliations),
            "matched_reconciliations": matched_recons,
            "reconciliation_match_rate": float(matched_recons / len(self.reconciliations)) if self.reconciliations else 1.0,
        })
