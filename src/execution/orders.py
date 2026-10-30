"""Order representation, lifecycle, fills, and position state."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Dict, List, Optional

from ..errors import OrderError, get_logger
from ..telemetry import serialize_metrics_strict


_logger = get_logger(__name__)


class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"
    ICEBERG = "iceberg"


class OrderStatus(str, Enum):
    PENDING = "pending"
    SUBMITTED = "submitted"
    PARTIALLY_FILLED = "partially_filled"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    EXPIRED = "expired"


class TimeInForce(str, Enum):
    GTC = "GTC"
    IOC = "IOC"
    FOK = "FOK"
    DAY = "DAY"


@dataclass
class OrderFill:
    """A single fill event for an order."""

    fill_id: str
    order_id: str
    symbol: str
    quantity: float
    price: float
    commission: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    liquidity: str = "taker"  # maker/taker/unknown

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "fill_id": self.fill_id,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "quantity": float(self.quantity),
            "price": float(self.price),
            "commission": float(self.commission),
            "timestamp": self.timestamp.isoformat(),
            "liquidity": self.liquidity,
        })


@dataclass
class Order:
    """Order representation with lifecycle tracking."""

    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None
    stop_price: Optional[float] = None
    time_in_force: TimeInForce = TimeInForce.GTC
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    fills: List[OrderFill] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: Optional[datetime] = None
    filled_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    client_order_id: Optional[str] = None
    parent_order_id: Optional[str] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Validate numerics
        if not isfinite(float(self.quantity)) or float(self.quantity) <= 0:
            raise OrderError(
                "Order quantity must be positive and finite",
                context={"order_id": self.order_id, "quantity": self.quantity},
            )
        if self.price is not None:
            if not isfinite(float(self.price)) or float(self.price) <= 0:
                raise OrderError(
                    "Order price must be positive and finite",
                    context={"order_id": self.order_id, "price": self.price},
                )
        if self.stop_price is not None:
            if not isfinite(float(self.stop_price)) or float(self.stop_price) <= 0:
                raise OrderError(
                    "Stop price must be positive and finite",
                    context={"order_id": self.order_id, "stop_price": self.stop_price},
                )
        self.quantity = float(self.quantity)
        self.filled_quantity = float(self.filled_quantity)
        self.avg_fill_price = float(self.avg_fill_price)

    @property
    def remaining_quantity(self) -> float:
        rem = self.quantity - self.filled_quantity
        if rem < 0:
            rem = 0.0
        return float(rem)

    @property
    def is_active(self) -> bool:
        return self.status in (OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIALLY_FILLED)

    @property
    def is_complete(self) -> bool:
        return self.status in (OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED)

    def add_fill(self, fill: OrderFill) -> None:
        if not isinstance(fill, OrderFill):
            raise OrderError("fill must be OrderFill instance", context={"order_id": self.order_id})
        if fill.quantity <= 0 or not isfinite(fill.quantity):
            raise OrderError("fill quantity must be positive and finite", context={"order_id": self.order_id})
        if fill.price <= 0 or not isfinite(fill.price):
            raise OrderError("fill price must be positive and finite", context={"order_id": self.order_id})

        self.fills.append(fill)
        new_filled = self.filled_quantity + float(fill.quantity)
        if new_filled > self.quantity + 1e-18:  # allow tiny numerical drift guard
            raise OrderError(
                "Fill quantity would exceed order quantity",
                context={"order_id": self.order_id, "filled": new_filled, "quantity": self.quantity},
            )
        # Update avg fill price (volume weighted)
        total_notional = self.avg_fill_price * self.filled_quantity + float(fill.price) * float(fill.quantity)
        self.filled_quantity = new_filled
        if self.filled_quantity > 0:
            self.avg_fill_price = total_notional / self.filled_quantity
        else:
            self.avg_fill_price = float(fill.price)
        self.updated_at = datetime.now(timezone.utc)

        if abs(self.filled_quantity - self.quantity) < 1e-12 or self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
            self.filled_quantity = self.quantity  # cap
            if self.filled_at is None:
                self.filled_at = datetime.now(timezone.utc)
        elif self.filled_quantity > 0:
            self.status = OrderStatus.PARTIALLY_FILLED

    def cancel(self) -> None:
        if self.is_complete:
            return  # already complete
        self.status = OrderStatus.CANCELLED
        self.cancelled_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    def reject(self, reason: str = "") -> None:
        if self.is_complete:
            return
        self.status = OrderStatus.REJECTED
        self.updated_at = datetime.now(timezone.utc)
        if reason:
            self.metadata["reject_reason"] = reason

    def submit(self) -> None:
        if self.status == OrderStatus.PENDING:
            self.status = OrderStatus.SUBMITTED
            self.submitted_at = datetime.now(timezone.utc)
            self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "order_id": self.order_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "order_type": self.order_type.value,
            "quantity": float(self.quantity),
            "price": float(self.price) if self.price is not None else None,
            "stop_price": float(self.stop_price) if self.stop_price is not None else None,
            "time_in_force": self.time_in_force.value,
            "status": self.status.value,
            "filled_quantity": float(self.filled_quantity),
            "avg_fill_price": float(self.avg_fill_price),
            "remaining_quantity": float(self.remaining_quantity),
            "fills": [f.to_dict() for f in self.fills],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "submitted_at": self.submitted_at.isoformat() if self.submitted_at else None,
            "filled_at": self.filled_at.isoformat() if self.filled_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "client_order_id": self.client_order_id,
            "parent_order_id": self.parent_order_id,
            "tags": self.tags,
            "metadata": self.metadata,
        })


@dataclass
class PositionState:
    """Current position state for a symbol."""

    symbol: str
    quantity: float = 0.0  # positive = long, negative = short
    avg_entry_price: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_commission: float = 0.0
    last_update: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def side(self) -> str:
        if self.quantity > 1e-18:
            return "long"
        elif self.quantity < -1e-18:
            return "short"
        return "flat"

    @property
    def market_value_abs(self) -> float:
        return abs(float(self.quantity)) * float(self.avg_entry_price)

    def update_fill(self, side: OrderSide, quantity: float, price: float, commission: float = 0.0) -> None:
        if quantity <= 0 or not isfinite(quantity):
            raise OrderError("fill quantity must be positive", context={"symbol": self.symbol})
        if price <= 0 or not isfinite(price):
            raise OrderError("fill price must be positive", context={"symbol": self.symbol})
        qty = float(quantity)
        px = float(price)
        comm = float(commission)
        self.total_commission += comm

        if side == OrderSide.BUY:
            if self.quantity >= -1e-18:  # going long or covering
                if self.quantity < 0:  # covering short
                    cover_qty = min(qty, abs(self.quantity))
                    # realize PnL on cover
                    self.realized_pnl += (self.avg_entry_price - px) * cover_qty - comm * (cover_qty / qty) if qty > 0 else (self.avg_entry_price - px) * cover_qty
                    self.quantity += qty
                    if self.quantity >= 0:
                        if abs(self.quantity) < 1e-12:
                            self.quantity = 0.0
                            self.avg_entry_price = 0.0
                        else:
                            # flipped to long, new avg is px for remaining
                            self.avg_entry_price = px
                else:
                    # adding to long
                    total_cost = self.avg_entry_price * self.quantity + px * qty
                    self.quantity += qty
                    if self.quantity > 0:
                        self.avg_entry_price = total_cost / self.quantity
            else:
                self.quantity += qty
                self.avg_entry_price = px
        else:  # SELL
            if self.quantity <= 1e-18:  # going short or closing long
                if self.quantity > 0:  # closing long
                    close_qty = min(qty, self.quantity)
                    self.realized_pnl += (px - self.avg_entry_price) * close_qty - comm * (close_qty / qty) if qty > 0 else (px - self.avg_entry_price) * close_qty
                    self.quantity -= qty
                    if self.quantity <= 0:
                        if abs(self.quantity) < 1e-12:
                            self.quantity = 0.0
                            self.avg_entry_price = 0.0
                        else:
                            self.avg_entry_price = px
                else:
                    # adding to short
                    total_cost = abs(self.avg_entry_price) * abs(self.quantity) + px * qty  # avg entry for short is price
                    self.quantity -= qty  # more negative
                    if self.quantity < 0:
                        self.avg_entry_price = total_cost / abs(self.quantity)
            else:
                self.quantity -= qty
                self.avg_entry_price = px

        self.last_update = datetime.now(timezone.utc)

    def mark_to_market(self, current_price: float) -> float:
        if not isfinite(current_price) or current_price <= 0:
            return float(self.unrealized_pnl)
        px = float(current_price)
        if abs(self.quantity) < 1e-18 or self.avg_entry_price == 0:
            self.unrealized_pnl = 0.0
            return 0.0
        if self.quantity > 0:  # long
            self.unrealized_pnl = (px - self.avg_entry_price) * self.quantity
        else:  # short
            self.unrealized_pnl = (self.avg_entry_price - px) * abs(self.quantity)
        self.last_update = datetime.now(timezone.utc)
        return float(self.unrealized_pnl)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "symbol": self.symbol,
            "quantity": float(self.quantity),
            "side": self.side,
            "avg_entry_price": float(self.avg_entry_price),
            "realized_pnl": float(self.realized_pnl),
            "unrealized_pnl": float(self.unrealized_pnl),
            "total_commission": float(self.total_commission),
            "market_value_abs": float(self.market_value_abs),
            "last_update": self.last_update.isoformat(),
        })


@dataclass
class ExecutionReport:
    """Execution report for order/fill events."""

    report_id: str
    order_id: str
    symbol: str
    status: OrderStatus
    filled_quantity: float
    remaining_quantity: float
    avg_fill_price: float
    commission: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    message: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "report_id": self.report_id,
            "order_id": self.order_id,
            "symbol": self.symbol,
            "status": self.status.value,
            "filled_quantity": float(self.filled_quantity),
            "remaining_quantity": float(self.remaining_quantity),
            "avg_fill_price": float(self.avg_fill_price),
            "commission": float(self.commission),
            "timestamp": self.timestamp.isoformat(),
            "message": self.message,
        })
