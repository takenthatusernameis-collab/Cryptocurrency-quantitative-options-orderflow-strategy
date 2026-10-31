"""Multi-venue smart order routing with fill tracking and cost-aware execution."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Dict, List, Optional, Tuple

from ..errors import OrderError, RiskLimitError, get_logger
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import safe_divide, clamp
from .orders import Order, OrderSide, OrderType, OrderStatus, OrderFill, ExecutionReport
from .algorithms import SlippageModel


_logger = get_logger(__name__)


class VenueType(str, Enum):
    DERIBIT = "deribit"
    OKX = "okx"
    BINANCE = "binance"


@dataclass
class VenueConfig:
    """Venue-specific configuration for routing."""

    venue: VenueType
    enabled: bool = True
    taker_fee_bps: float = 5.0
    maker_fee_bps: float = -2.5  # negative means rebate
    min_order_size: float = 0.001
    max_order_size: float = 1000000.0
    liquidity_score: float = 1.0  # 0-1, higher is better
    latency_ms: float = 50.0
    slippage_multiplier: float = 1.0
    supports_options: bool = True
    supports_futures: bool = True

    def __post_init__(self) -> None:
        if not isfinite(self.taker_fee_bps) or self.taker_fee_bps < -100 or self.taker_fee_bps > 100:
            raise OrderError("taker_fee_bps out of range", context={"venue": self.venue.value})
        if not isfinite(self.maker_fee_bps) or self.maker_fee_bps < -100 or self.maker_fee_bps > 100:
            raise OrderError("maker_fee_bps out of range", context={"venue": self.venue.value})
        if not isfinite(self.min_order_size) or self.min_order_size < 0:
            raise OrderError("min_order_size must be >= 0", context={"venue": self.venue.value})
        if not isfinite(self.max_order_size) or self.max_order_size < self.min_order_size:
            raise OrderError("max_order_size must be >= min_order_size", context={"venue": self.venue.value})
        if not isfinite(self.liquidity_score) or self.liquidity_score < 0 or self.liquidity_score > 1:
            raise OrderError("liquidity_score must be in [0,1]", context={"venue": self.venue.value})
        if not isfinite(self.latency_ms) or self.latency_ms < 0:
            raise OrderError("latency_ms must be >= 0", context={"venue": self.venue.value})
        if not isfinite(self.slippage_multiplier) or self.slippage_multiplier < 0:
            raise OrderError("slippage_multiplier must be >= 0", context={"venue": self.venue.value})


@dataclass
class VenueQuote:
    """Quote from a specific venue."""

    venue: VenueType
    symbol: str
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not isfinite(self.bid) or self.bid <= 0 or not isfinite(self.ask) or self.ask <= 0:
            raise OrderError("bid/ask must be positive and finite", context={"venue": self.venue.value, "symbol": self.symbol})
        if self.ask < self.bid - 1e-12:
            raise OrderError("ask must be >= bid", context={"venue": self.venue.value, "symbol": self.symbol})
        if not isfinite(self.bid_size) or self.bid_size < 0 or not isfinite(self.ask_size) or self.ask_size < 0:
            raise OrderError("sizes must be non-negative and finite", context={"venue": self.venue.value, "symbol": self.symbol})
        self.bid = float(self.bid)
        self.ask = float(self.ask)
        self.bid_size = float(self.bid_size)
        self.ask_size = float(self.ask_size)

    @property
    def mid_price(self) -> float:
        return (self.bid + self.ask) / 2.0

    @property
    def spread(self) -> float:
        return self.ask - self.bid

    @property
    def spread_bps(self) -> float:
        return safe_divide(self.spread, self.mid_price, 0.0) * 10000.0


@dataclass
class RoutingDecision:
    """Routing decision for order splitting."""

    venue_allocations: Dict[VenueType, float]  # venue -> quantity
    rationale: str
    total_cost_bps: float
    estimated_slippage_bps: float
    participation_rate: float = 0.0

    def __post_init__(self) -> None:
        # Validate allocations
        total = sum(self.venue_allocations.values())
        if total < 0 or not isfinite(total):
            raise OrderError("venue allocations must be non-negative and finite")
        if not isfinite(self.total_cost_bps):
            raise OrderError("total_cost_bps must be finite")
        if not isfinite(self.estimated_slippage_bps):
            raise OrderError("estimated_slippage_bps must be finite")
        if not isfinite(self.participation_rate) or self.participation_rate < 0 or self.participation_rate > 1.0:
            raise OrderError("participation_rate must be in [0,1]", context={"participation_rate": self.participation_rate})


@dataclass
class FillTrackingRecord:
    """Fill tracking record for multi-venue execution."""

    tracking_id: str
    parent_order_id: str
    venue: VenueType
    child_order_id: str
    filled_quantity: float = 0.0
    avg_fill_price: float = 0.0
    total_commission: float = 0.0
    fills: List[OrderFill] = field(default_factory=list)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not isfinite(self.filled_quantity) or self.filled_quantity < 0:
            raise OrderError("filled_quantity must be non-negative and finite")
        if self.avg_fill_price < 0 or not isfinite(self.avg_fill_price):
            raise OrderError("avg_fill_price must be non-negative and finite")
        if self.total_commission < 0 or not isfinite(self.total_commission):
            raise OrderError("total_commission must be non-negative and finite")
        self.filled_quantity = float(self.filled_quantity)
        self.avg_fill_price = float(self.avg_fill_price)
        self.total_commission = float(self.total_commission)

    def add_fill(self, fill: OrderFill) -> None:
        if not isinstance(fill, OrderFill):
            raise OrderError("fill must be OrderFill instance")
        if fill.quantity <= 0 or not isfinite(fill.quantity):
            raise OrderError("fill quantity must be positive and finite")
        if fill.price <= 0 or not isfinite(fill.price):
            raise OrderError("fill price must be positive and finite")

        self.fills.append(fill)
        new_filled = self.filled_quantity + float(fill.quantity)
        if new_filled < 0 or not isfinite(new_filled):
            raise OrderError("invalid fill quantity accumulation")

        # VWAP update
        if new_filled > 0:
            total_notional = self.avg_fill_price * self.filled_quantity + float(fill.price) * float(fill.quantity)
            self.avg_fill_price = total_notional / new_filled
        else:
            self.avg_fill_price = float(fill.price)

        self.filled_quantity = new_filled
        self.total_commission += float(fill.commission)
        self.updated_at = datetime.now(timezone.utc)

        if self.filled_quantity > 0:
            self.status = OrderStatus.PARTIALLY_FILLED

    def complete_fill(self) -> None:
        self.status = OrderStatus.FILLED
        self.updated_at = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "tracking_id": self.tracking_id,
            "parent_order_id": self.parent_order_id,
            "venue": self.venue.value,
            "child_order_id": self.child_order_id,
            "filled_quantity": float(self.filled_quantity),
            "avg_fill_price": float(self.avg_fill_price),
            "total_commission": float(self.total_commission),
            "status": self.status.value,
            "num_fills": len(self.fills),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        })


class SmartOrderRouter:
    """Smart order router with multi-venue routing and fill tracking."""

    SUPPORTED_VENUES = [VenueType.DERIBIT, VenueType.OKX, VenueType.BINANCE]

    def __init__(
        self,
        venue_configs: Optional[Dict[VenueType, VenueConfig]] = None,
        slippage_model: Optional[SlippageModel] = None,
        max_participation_rate: float = 0.1,  # 10% of volume
        min_fill_rate_threshold: float = 0.95,
        seed: int = 42,
    ):
        if not isfinite(max_participation_rate) or max_participation_rate <= 0 or max_participation_rate > 1.0:
            raise OrderError("max_participation_rate must be in (0,1]", context={"max_participation_rate": max_participation_rate})
        if not isfinite(min_fill_rate_threshold) or min_fill_rate_threshold < 0 or min_fill_rate_threshold > 1.0:
            raise OrderError("min_fill_rate_threshold must be in [0,1]", context={"min_fill_rate_threshold": min_fill_rate_threshold})
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise OrderError("seed must be integer for determinism", context={"seed": seed})

        # Default venue configs
        if venue_configs is None:
            venue_configs = {
                VenueType.DERIBIT: VenueConfig(venue=VenueType.DERIBIT, taker_fee_bps=5.0, maker_fee_bps=-2.5, liquidity_score=0.95, latency_ms=40.0),
                VenueType.OKX: VenueConfig(venue=VenueType.OKX, taker_fee_bps=5.0, maker_fee_bps=-1.0, liquidity_score=0.90, latency_ms=45.0),
                VenueType.BINANCE: VenueConfig(venue=VenueType.BINANCE, taker_fee_bps=4.0, maker_fee_bps=-2.0, liquidity_score=0.93, latency_ms=35.0),
            }
        self.venue_configs = venue_configs
        self.slippage_model = slippage_model or SlippageModel()
        self.max_participation_rate = float(max_participation_rate)
        self.min_fill_rate_threshold = float(min_fill_rate_threshold)
        self.seed = int(seed)

        self.quotes: Dict[VenueType, VenueQuote] = {}
        self.routing_history: List[RoutingDecision] = []
        self.fill_tracking: Dict[str, FillTrackingRecord] = {}
        self._id_counter = 0

    def _generate_id(self, prefix: str = "route") -> str:
        self._id_counter += 1
        payload = f"{int(self.seed)}|{prefix}|{self._id_counter}"
        digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
        return f"{prefix}_{digest}"

    def update_quotes(self, quotes: List[VenueQuote]) -> None:
        for q in quotes:
            if not isinstance(q, VenueQuote):
                raise OrderError("quotes must be VenueQuote instances")
            if q.venue in self.venue_configs and self.venue_configs[q.venue].enabled:
                self.quotes[q.venue] = q

    def get_best_venue(self, order: Order) -> VenueType:
        """Select best venue based on liquidity, fees, and spread."""
        if not self.quotes:
            # Fallback to default preference
            for v in [VenueType.DERIBIT, VenueType.BINANCE, VenueType.OKX]:
                if v in self.venue_configs and self.venue_configs[v].enabled:
                    return v
            raise OrderError("No enabled venues available")

        best_venue = None
        best_score = -float("inf")

        for venue, quote in self.quotes.items():
            if venue not in self.venue_configs or not self.venue_configs[venue].enabled:
                continue
            cfg = self.venue_configs[venue]
            # Score based on liquidity, spread, fees, latency
            spread_cost_bps = quote.spread_bps
            fee_cost_bps = cfg.taker_fee_bps if order.order_type == OrderType.MARKET else cfg.maker_fee_bps
            total_cost_bps = spread_cost_bps / 2.0 + fee_cost_bps  # rough estimate
            # Higher liquidity and lower cost is better
            score = cfg.liquidity_score * 1000.0 - total_cost_bps - cfg.latency_ms * 0.1
            if score > best_score:
                best_score = score
                best_venue = venue

        if best_venue is None:
            raise OrderError("No valid venues for routing")
        return best_venue

    def route_order(
        self,
        order: Order,
        adv: float = 0.0,  # average daily volume
        participation_cap: Optional[float] = None,
        allow_splitting: bool = True,
    ) -> RoutingDecision:
        """Route order across venues with participation cap enforcement."""
        if not isinstance(order, Order):
            raise OrderError("order must be Order instance")
        if not isfinite(adv) or adv < 0:
            raise OrderError("adv must be non-negative and finite")
        if participation_cap is not None:
            if not isfinite(participation_cap) or participation_cap <= 0 or participation_cap > 1.0:
                raise OrderError("participation_cap must be in (0,1]", context={"participation_cap": participation_cap})
        else:
            participation_cap = self.max_participation_rate

        qty = float(order.quantity)
        if qty <= 0 or not isfinite(qty):
            raise OrderError("order quantity must be positive and finite")

        # Check participation cap
        if adv > 0:
            participation_rate = safe_divide(qty, adv, 0.0)
            if participation_rate > participation_cap + 1e-12:
                raise RiskLimitError(
                    "Order exceeds participation cap",
                    context={
                        "quantity": qty,
                        "adv": adv,
                        "participation_rate": participation_rate,
                        "participation_cap": participation_cap,
                    },
                )
        else:
            participation_rate = 0.0

        # Get available venues with quotes
        available_venues = []
        for venue, quote in self.quotes.items():
            if venue in self.venue_configs and self.venue_configs[venue].enabled:
                cfg = self.venue_configs[venue]
                if qty >= cfg.min_order_size:  # basic check
                    available_venues.append((venue, quote, cfg))

        if not available_venues:
            # Route to best single venue even without quotes
            best_venue = self.get_best_venue(order)
            decision = RoutingDecision(
                venue_allocations={best_venue: qty},
                rationale="Single venue routing (no quotes available)",
                total_cost_bps=5.0,
                estimated_slippage_bps=2.0,
                participation_rate=participation_rate,
            )
            self.routing_history.append(decision)
            return decision

        # Smart routing: can split across venues for large orders
        if allow_splitting and len(available_venues) > 1 and qty > 10.0:  # split threshold
            # Allocate based on liquidity score and inverse spread
            allocations = {}
            total_score = 0.0
            venue_scores = {}

            for venue, quote, cfg in available_venues:
                # Score: liquidity + inverse spread
                spread_inv = safe_divide(10000.0, max(quote.spread_bps, 0.1), 0.0)
                score = cfg.liquidity_score * 100.0 + spread_inv * 0.1 - cfg.latency_ms * 0.01
                if score > 0:
                    venue_scores[venue] = score
                    total_score += score

            if total_score > 0:
                for venue, score in venue_scores.items():
                    alloc = qty * (score / total_score)
                    cfg = self.venue_configs[venue]
                    # Respect venue limits
                    alloc = clamp(alloc, cfg.min_order_size, cfg.max_order_size)
                    if alloc > 1e-12:
                        allocations[venue] = alloc
            else:
                # Equal split as fallback
                per_venue = qty / len(available_venues)
                for venue, _, _ in available_venues:
                    allocations[venue] = per_venue
        else:
            # Single venue routing
            best_venue = self.get_best_venue(order)
            allocations = {best_venue: qty}

        # Normalize allocations to sum to qty (small numerical adjustment)
        total_alloc = sum(allocations.values())
        if total_alloc > 0 and abs(total_alloc - qty) > 1e-10:
            # Scale to match
            if not isfinite(total_alloc) or total_alloc <= 0:
                # Fallback to single best venue
                try:
                    best_venue = self.get_best_venue(order)
                    allocations = {best_venue: qty}
                except Exception:
                    allocations = {list(self.venue_configs.keys())[0]: qty} if self.venue_configs else {}
            else:
                scale = qty / total_alloc
                if not isfinite(scale):
                    scale = 1.0
                new_alloc = {}
                for v, a in allocations.items():
                    na = a * scale
                    if isfinite(na) and na > 1e-18:
                        new_alloc[v] = na
                allocations = new_alloc if new_alloc else allocations

        # Ensure all allocations are finite and positive
        clean_alloc = {}
        for v, a in allocations.items():
            fa = float(a)
            if isfinite(fa) and fa > 0:
                clean_alloc[v] = fa
        allocations = clean_alloc
        if not allocations:
            try:
                best_venue = self.get_best_venue(order)
                allocations = {best_venue: qty}
            except Exception:
                raise OrderError("Unable to compute finite venue allocations")

        # Calculate estimated costs
        total_cost_bps = 0.0
        total_slippage_bps = 0.0
        for venue, alloc_qty in allocations.items():
            if venue in self.quotes and venue in self.venue_configs:
                quote = self.quotes[venue]
                cfg = self.venue_configs[venue]
                fee_bps = cfg.taker_fee_bps if order.order_type == OrderType.MARKET else cfg.maker_fee_bps
                slip_bps = self.slippage_model.estimate_slippage_bps(order.side, alloc_qty, adv, 0.01) * cfg.slippage_multiplier
                weight = alloc_qty / qty if qty > 0 else 0
                total_cost_bps += (fee_bps + quote.spread_bps / 2.0) * weight
                total_slippage_bps += slip_bps * weight
            else:
                weight = alloc_qty / qty if qty > 0 else 0
                total_cost_bps += 5.0 * weight
                total_slippage_bps += 2.0 * weight

        decision = RoutingDecision(
            venue_allocations=allocations,
            rationale=f"Smart routed to {len(allocations)} venue(s) with participation cap {participation_cap:.2%}",
            total_cost_bps=float(total_cost_bps),
            estimated_slippage_bps=float(total_slippage_bps),
            participation_rate=participation_rate,
        )
        self.routing_history.append(decision)
        return decision

    def create_child_orders(self, parent_order: Order, routing_decision: RoutingDecision) -> Dict[VenueType, Order]:
        """Create child orders for each venue allocation."""
        if not isinstance(parent_order, Order):
            raise OrderError("parent_order must be Order instance")
        if not isinstance(routing_decision, RoutingDecision):
            raise OrderError("routing_decision must be RoutingDecision instance")

        child_orders = {}
        for venue, qty in routing_decision.venue_allocations.items():
            if qty < 1e-18:
                continue
            child_id = self._generate_id(f"child_{venue.value}")
            child_order = Order(
                order_id=child_id,
                symbol=parent_order.symbol,
                side=parent_order.side,
                order_type=parent_order.order_type,
                quantity=float(qty),
                price=parent_order.price,
                time_in_force=parent_order.time_in_force,
                parent_order_id=parent_order.order_id,
                tags={**parent_order.tags, "venue": venue.value, "routed": "true"},
                metadata={**parent_order.metadata, "routing_decision_id": self._generate_id("rdec")},
            )
            child_orders[venue] = child_order
            # Initialize tracking
            tracking_id = self._generate_id("track")
            self.fill_tracking[tracking_id] = FillTrackingRecord(
                tracking_id=tracking_id,
                parent_order_id=parent_order.order_id,
                venue=venue,
                child_order_id=child_id,
            )
        return child_orders

    def track_fill(self, venue: VenueType, child_order_id: str, fill: OrderFill) -> Optional[FillTrackingRecord]:
        """Track fill for a child order."""
        if not isinstance(venue, VenueType):
            raise OrderError("venue must be VenueType")
        if not isinstance(fill, OrderFill):
            raise OrderError("fill must be OrderFill instance")

        # Find tracking record
        for tracking in self.fill_tracking.values():
            if tracking.venue == venue and tracking.child_order_id == child_order_id:
                tracking.add_fill(fill)
                return tracking
        return None

    def get_fill_status(self, parent_order_id: str) -> Dict[str, Any]:
        """Get aggregated fill status across all venues for a parent order."""
        records = [r for r in self.fill_tracking.values() if r.parent_order_id == parent_order_id]
        if not records:
            return {
                "parent_order_id": parent_order_id,
                "total_filled": 0.0,
                "avg_fill_price": 0.0,
                "total_commission": 0.0,
                "venues": [],
                "all_filled": False,
            }

        total_filled = sum(r.filled_quantity for r in records)
        total_notional = sum(r.avg_fill_price * r.filled_quantity for r in records)
        total_commission = sum(r.total_commission for r in records)
        avg_price = safe_divide(total_notional, total_filled, 0.0)
        all_filled = all(r.status == OrderStatus.FILLED for r in records)

        return serialize_metrics_strict({
            "parent_order_id": parent_order_id,
            "total_filled": float(total_filled),
            "avg_fill_price": float(avg_price),
            "total_commission": float(total_commission),
            "venues": [r.to_dict() for r in records],
            "all_filled": bool(all_filled),
            "num_venues": len(records),
        })

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        if not self.routing_history:
            return {
                "total_routes": 0,
                "avg_venues_per_order": 0.0,
                "avg_cost_bps": 0.0,
                "avg_slippage_bps": 0.0,
            }

        total_routes = len(self.routing_history)
        venue_counts = [len(d.venue_allocations) for d in self.routing_history]
        costs = [d.total_cost_bps for d in self.routing_history]
        slippages = [d.estimated_slippage_bps for d in self.routing_history]

        avg_venues = sum(venue_counts) / total_routes if total_routes > 0 else 0.0
        avg_cost = sum(costs) / total_routes if total_routes > 0 else 0.0
        avg_slip = sum(slippages) / total_routes if total_routes > 0 else 0.0

        return serialize_metrics_strict({
            "total_routes": int(total_routes),
            "avg_venues_per_order": float(avg_venues),
            "avg_cost_bps": float(avg_cost),
            "avg_slippage_bps": float(avg_slip),
            "max_participation_rate": float(self.max_participation_rate),
        })
