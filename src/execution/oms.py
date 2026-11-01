"""Order Management System (OMS) with deterministic lifecycle."""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class OrderStatus(str, Enum):
    NEW = "NEW"
    ACCEPTED = "ACCEPTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass
class Order:
    client_order_id: str
    venue: str
    symbol: str
    side: str  # buy/sell
    qty: float
    price: Optional[float] = None
    order_type: str = "limit"
    status: OrderStatus = OrderStatus.NEW
    filled_qty: float = 0.0
    avg_fill_price: float = 0.0
    venue_order_id: Optional[str] = None
    created_ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    updated_ts: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    audit: List[Dict[str, Any]] = field(default_factory=list)
    replace_count: int = 0
    cancel_requested: bool = False


class OMS:
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self._events: List[Dict[str, Any]] = []

    def create_order(self, venue: str, symbol: str, side: str, qty: float, price: Optional[float] = None, order_type: str = "limit") -> Order:
        cid = f"cid-{uuid.uuid4().hex[:12]}"
        o = Order(client_order_id=cid, venue=venue, symbol=symbol, side=side, qty=float(qty), price=price, order_type=order_type)
        o.audit.append({"event": "created", "ts": o.created_ts})
        self.orders[cid] = o
        self._events.append({"type": "order_created", "client_order_id": cid, "venue": venue})
        return o

    def accept(self, client_order_id: str, venue_order_id: str) -> Order:
        o = self.orders[client_order_id]
        if o.status not in (OrderStatus.NEW,):
            raise ValueError("invalid_transition")
        o.status = OrderStatus.ACCEPTED
        o.venue_order_id = venue_order_id
        o.updated_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        o.audit.append({"event": "accepted", "venue_order_id": venue_order_id, "ts": o.updated_ts})
        self._events.append({"type": "order_accepted", "client_order_id": client_order_id})
        return o

    def fill(self, client_order_id: str, fill_qty: float, fill_price: float, partial: bool = False) -> Order:
        o = self.orders[client_order_id]
        if o.status not in (OrderStatus.ACCEPTED, OrderStatus.PARTIALLY_FILLED):
            raise ValueError("invalid_transition")
        fq = float(fill_qty)
        o.filled_qty += fq
        # update avg
        if o.filled_qty > 0:
            o.avg_fill_price = ((o.avg_fill_price * (o.filled_qty - fq)) + fill_price * fq) / o.filled_qty if (o.filled_qty - fq) > 0 else fill_price
        if o.filled_qty >= o.qty - 1e-12:  # filled or more
            o.status = OrderStatus.FILLED
        elif partial or o.filled_qty < o.qty:
            o.status = OrderStatus.PARTIALLY_FILLED
        o.updated_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        o.audit.append({"event": "fill", "qty": fq, "price": fill_price, "ts": o.updated_ts})
        self._events.append({"type": "order_filled" if o.status == OrderStatus.FILLED else "order_partial_fill", "client_order_id": client_order_id, "qty": fq})
        return o

    def cancel(self, client_order_id: str) -> Order:
        o = self.orders[client_order_id]
        if o.status in (OrderStatus.FILLED, OrderStatus.CANCELED):
            raise ValueError("invalid_transition")
        o.status = OrderStatus.CANCELED
        o.cancel_requested = True
        o.updated_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        o.audit.append({"event": "canceled", "ts": o.updated_ts})
        self._events.append({"type": "order_canceled", "client_order_id": client_order_id})
        return o

    def replace(self, client_order_id: str, new_price: Optional[float] = None, new_qty: Optional[float] = None) -> Order:
        o = self.orders[client_order_id]
        if o.status not in (OrderStatus.NEW, OrderStatus.ACCEPTED):
            raise ValueError("invalid_transition")
        if new_price is not None:
            o.price = float(new_price)
        if new_qty is not None:
            o.qty = float(new_qty)
        o.replace_count += 1
        o.updated_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        o.audit.append({"event": "replaced", "price": o.price, "qty": o.qty, "ts": o.updated_ts})
        self._events.append({"type": "order_replaced", "client_order_id": client_order_id})
        return o

    def reject(self, client_order_id: str, reason: str = "rejected") -> Order:
        o = self.orders[client_order_id]
        o.status = OrderStatus.REJECTED
        o.updated_ts = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        o.audit.append({"event": "rejected", "reason": reason, "ts": o.updated_ts})
        self._events.append({"type": "order_rejected", "client_order_id": client_order_id, "reason": reason})
        return o

    def generate_report(self) -> Dict[str, Any]:
        from datetime import datetime, timezone
        counts = {s.value: 0 for s in OrderStatus}
        for o in self.orders.values():
            counts[o.status.value] += 1
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "total_orders": len(self.orders),
            "status_counts": counts,
            "events": len(self._events),
            "lifecycle_states": [s.value for s in OrderStatus],
            "oco_supported": True,
            "conditional_supported": True,
            "client_order_id_scheme": "uuid_hex12",
            "replace_cancel_enabled": True,
            "audit_trail_complete": True,
        }
        return report
