"""Latency-aware execution routing for crypto options + orderflow (Phase 15).

Venue latency models (EWMA), adaptive cost-latency routing, cancel/replace,
slippage tracking, and paper-only hard gates. Fully deterministic for a fixed
seed: no clocks, no network, no randomness outside the injected seed.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from ..errors import DataError, OrderError, RiskLimitError, ValidationError, get_logger
from ..telemetry.serialization import serialize_metrics_strict, assert_json_valid
from ..utils.numerical_guards import safe_divide, clamp, validate_finite

_logger = get_logger(__name__)

DEFAULT_VENUES = ("deribit", "okx", "binance")
DEFAULT_SYMBOLS = ("BTC", "ETH")
_BASE_TS = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _det_ts(seed: int) -> str:
    return (_BASE_TS + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


def _rid(prefix: str, seed: int, counter: int) -> str:
    digest = hashlib.sha256(f"{seed}|{prefix}|{counter}".encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _validate_venue(venue: str) -> str:
    v = str(venue).lower()
    if v not in DEFAULT_VENUES:
        raise ValidationError(f"unsupported venue {venue!r}", context={"venue": v, "supported": list(DEFAULT_VENUES)})
    return v


def _validate_symbol(symbol: str) -> str:
    s = str(symbol).upper()
    if not s:
        raise ValidationError("symbol must be non-empty")
    return s


@dataclass
class LatencyRouterConfig:
    venues: Tuple[str, ...] = ("deribit", "okx", "binance")
    symbols: Tuple[str, ...] = ("BTC", "ETH")
    paper_only: bool = True
    enable_live: bool = False
    max_latency_ms: float = 500.0
    latency_penalty_bps_per_ms: float = 0.5
    slippage_bps_per_1pct_participation: float = 2.0
    min_spread_bps: float = 0.1
    cancel_replace_enabled: bool = True
    max_cancel_replace_per_order: int = 3
    adv_usd: float = 1_000_000_000.0
    seed: int = 42

    def __post_init__(self) -> None:
        self.venues = tuple(_validate_venue(v) for v in self.venues)
        if not self.venues:
            raise ValidationError("venues must be non-empty")
        self.symbols = tuple(_validate_symbol(s) for s in self.symbols)
        if not self.symbols:
            raise ValidationError("symbols must be non-empty")
        for name, value, minimum in (
            ("max_latency_ms", self.max_latency_ms, 0.0),
            ("latency_penalty_bps_per_ms", self.latency_penalty_bps_per_ms, 0.0),
            ("slippage_bps_per_1pct_participation", self.slippage_bps_per_1pct_participation, 0.0),
            ("min_spread_bps", self.min_spread_bps, 0.0),
            ("adv_usd", self.adv_usd, 0.0),
        ):
            value = float(validate_finite(value, name))
            if value < minimum:
                raise ValidationError(f"{name} must be >= {minimum}", context={name: value})
            if name == "max_latency_ms":
                self.max_latency_ms = value
            elif name == "latency_penalty_bps_per_ms":
                self.latency_penalty_bps_per_ms = value
            elif name == "slippage_bps_per_1pct_participation":
                self.slippage_bps_per_1pct_participation = value
            elif name == "min_spread_bps":
                self.min_spread_bps = value
            else:
                self.adv_usd = value
        if not math.isfinite(self.max_cancel_replace_per_order) or self.max_cancel_replace_per_order < 0:
            raise ValidationError("max_cancel_replace_per_order must be >= 0")
        self.max_cancel_replace_per_order = int(self.max_cancel_replace_per_order)
        self.paper_only = True
        self.enable_live = False
        self.seed = int(self.seed)


def default_latency_router_config() -> LatencyRouterConfig:
    return LatencyRouterConfig()


@dataclass
class RouteResult:
    order_id: str
    venue: str
    symbol: str
    side: str
    quantity: float
    price: float
    latency_ms: float
    latency_penalty_bps: float
    slippage_bps: float
    total_cost_bps: float
    participation_rate: float
    status: str
    paper_only: bool
    timestamp: str
    rationale: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FillRecord:
    fill_id: str
    order_id: str
    venue: str
    symbol: str
    side: str
    fill_price: float
    mid_price: float
    slippage_bps: float
    quantity: float
    commission: float
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LatencyAwareRouter:
    """Latency-aware smart router with cancel/replace and slippage tracking."""

    def __init__(self, config: Optional[LatencyRouterConfig] = None, seed: int = 42):
        self.config = config or default_latency_router_config()
        self.config.paper_only = True
        self.config.enable_live = False
        self.seed = int(seed)
        self.paper_only = True
        self.enable_live = False
        self._counter = 0
        self.quotes: Dict[str, Dict[str, Any]] = {}  # venue -> symbol -> quote
        self.latency_ewma: Dict[str, float] = {v: 0.0 for v in self.config.venues}
        self.latency_samples: Dict[str, List[float]] = {v: [] for v in self.config.venues}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.cancel_history: List[Dict[str, Any]] = []
        self.replacement_history: List[Dict[str, Any]] = []
        self.cancel_replace_counts: Dict[str, int] = {}
        self.fills: List[FillRecord] = []
        self.last_report: Optional[Dict[str, Any]] = None

    # -- market data / latency ----------------------------------------------
    def update_quote(
        self,
        venue: str,
        symbol: str,
        bid: float,
        ask: float,
        bid_size: float,
        ask_size: float,
        timestamp: str,
    ) -> None:
        venue = _validate_venue(venue)
        symbol = _validate_symbol(symbol)
        bid = float(validate_finite(bid, "bid"))
        ask = float(validate_finite(ask, "ask"))
        bid_size = float(validate_finite(bid_size, "bid_size"))
        ask_size = float(validate_finite(ask_size, "ask_size"))
        if bid <= 0.0 or ask <= 0.0:
            raise DataError("bid/ask must be positive", context={"venue": venue, "symbol": symbol})
        if ask < bid - 1e-12:
            raise DataError("ask must be >= bid", context={"venue": venue, "symbol": symbol})
        if bid_size < 0.0 or ask_size < 0.0:
            raise DataError("sizes must be non-negative", context={"venue": venue, "symbol": symbol})
        self.quotes.setdefault(venue, {})[symbol] = {
            "venue": venue,
            "symbol": symbol,
            "bid": float(bid),
            "ask": float(ask),
            "bid_size": float(bid_size),
            "ask_size": float(ask_size),
            "timestamp": str(timestamp),
            "mid_price": (float(bid) + float(ask)) / 2.0,
            "spread_bps": safe_divide(float(ask) - float(bid), (float(bid) + float(ask)) / 2.0, 0.0) * 10000.0,
        }

    def record_latency(self, venue: str, latency_ms: float, symbol: Optional[str] = None) -> None:
        venue = _validate_venue(venue)
        latency_ms = float(validate_finite(latency_ms, "latency_ms"))
        if latency_ms < 0.0:
            raise DataError("latency must be non-negative", context={"venue": venue, "latency_ms": latency_ms})
        alpha = 0.3
        previous = self.latency_ewma.get(venue, 0.0)
        self.latency_ewma[venue] = alpha * latency_ms + (1.0 - alpha) * previous
        self.latency_samples.setdefault(venue, []).append(float(latency_ms))
        _logger.info("router.latency_recorded", venue=venue, latency_ms=latency_ms, ewma_ms=self.latency_ewma[venue], seed=self.seed)

    def venue_latency_ms(self, venue: str) -> float:
        venue = _validate_venue(venue)
        return float(self.latency_ewma.get(venue, 0.0))

    def _venue_score(self, venue: str, symbol: str, side: str) -> float:
        quote = self.quotes.get(venue, {}).get(symbol)
        if quote is None:
            return float("inf")
        latency = self.latency_ewma.get(venue, 0.0)
        if latency > self.config.max_latency_ms:
            return float("inf")
        spread_bps = quote["spread_bps"] if quote else self.config.min_spread_bps
        taker_fee_bps = 5.0
        side_cost = taker_fee_bps  # marketable orders pay taker
        score = (
            self.config.latency_penalty_bps_per_ms * latency
            + side_cost
            + spread_bps / 2.0
        )
        return float(score)

    # -- routing ------------------------------------------------------------
    def route_intent(
        self,
        intent: Dict[str, Any],
        spot: Optional[Dict[str, float]] = None,
    ) -> RouteResult:
        spot = spot or {}
        symbol = _validate_symbol(str(intent.get("symbol", "BTC")))
        side = str(intent.get("side", "buy")).lower()
        if side not in ("buy", "sell"):
            raise ValidationError("side must be 'buy' or 'sell'", context={"side": side})
        quantity = float(validate_finite(intent.get("quantity", intent.get("qty", 0.0)), "quantity"))
        if quantity <= 0.0:
            raise DataError("quantity must be positive", context={"quantity": quantity})
        price_raw = intent.get("price")
        price = float(validate_finite(price_raw, "price")) if price_raw is not None else None

        venues_ranked = sorted(self.config.venues, key=lambda v: self._venue_score(v, symbol, side))
        best_venue = venues_ranked[0] if venues_ranked else self.config.venues[0]
        best_score = self._venue_score(best_venue, symbol, side)
        quote = self.quotes.get(best_venue, {}).get(symbol)
        latency = self.latency_ewma.get(best_venue, 0.0)
        if quote is None or math.isinf(best_score):
            # Fall back to the lowest-latency venue when no usable quote exists.
            best_venue = min(self.config.venues, key=lambda v: self.latency_ewma.get(v, 0.0))
            quote = self.quotes.get(best_venue, {}).get(symbol)
            latency = self.latency_ewma.get(best_venue, 0.0)
            best_score = self._venue_score(best_venue, symbol, side) if quote is not None else float("inf")
            if math.isinf(best_score):
                # Degraded mode: every venue is over the latency limit; route to
                # the lowest-latency venue with its full (finite) latency penalty.
                best_score = self.config.latency_penalty_bps_per_ms * latency

        if quote is None:
            # No quote: fall back to lowest-latency venue with a deterministic price.
            px = float(price) if price is not None else float(spot.get(symbol, 65000.0))
            if px <= 0.0:
                px = 65000.0
            penalty = self.config.latency_penalty_bps_per_ms * latency
            slip = self._slippage_bps(side, quantity, symbol)
            total = penalty + slip
            self._counter += 1
            result = RouteResult(
                order_id=_rid("ord", self.seed, self._counter),
                venue=best_venue,
                symbol=symbol,
                side=side,
                quantity=float(quantity),
                price=float(px),
                latency_ms=float(latency),
                latency_penalty_bps=float(penalty),
                slippage_bps=float(slip),
                total_cost_bps=float(total),
                participation_rate=float(safe_divide(quantity * px, self.config.adv_usd, 0.0)),
                status="routed_paper_no_quote",
                paper_only=True,
                timestamp=_det_ts(self.seed),
                rationale=f"no quote for {best_venue}/{symbol}; fallback latency routing",
            )
            self.orders[result.order_id] = {**result.to_dict(), "filled": False, "cancelled": False, "replaces": 0}
            self.last_report = None
            return result

        px = float(price) if price is not None else quote["mid_price"]
        if px <= 0.0:
            px = quote["mid_price"]
        penalty = self.config.latency_penalty_bps_per_ms * latency
        slip = self._slippage_bps(side, quantity, symbol)
        spread_cost = quote["spread_bps"] / 2.0
        total = penalty + slip + spread_cost

        self._counter += 1
        result = RouteResult(
            order_id=_rid("ord", self.seed, self._counter),
            venue=best_venue,
            symbol=symbol,
            side=side,
            quantity=float(quantity),
            price=float(px),
            latency_ms=float(latency),
            latency_penalty_bps=float(penalty),
            slippage_bps=float(slip),
            total_cost_bps=float(total),
            participation_rate=float(safe_divide(quantity * px, self.config.adv_usd, 0.0)),
            status="routed_paper",
            paper_only=True,
            timestamp=_det_ts(self.seed),
            rationale=(
                f"adaptive route to {best_venue} (latency {latency:.1f} ms, "
                f"spread {quote['spread_bps']:.2f} bps, total cost {total:.2f} bps)"
            ),
        )
        self.orders[result.order_id] = {**result.to_dict(), "filled": False, "cancelled": False, "replaces": 0}
        self.last_report = None
        _logger.info("router.route_intent", order_id=result.order_id, venue=best_venue, symbol=symbol, side=side, qty=quantity, cost_bps=total, seed=self.seed)
        return result

    def _slippage_bps(self, side: str, quantity: float, symbol: str) -> float:
        px = 65000.0 + (1000.0 if symbol == "ETH" else 0.0)
        notional = quantity * px
        participation = safe_divide(notional, self.config.adv_usd, 0.0)
        return participation * 100.0 * self.config.slippage_bps_per_1pct_participation

    # -- cancel / replace ---------------------------------------------------
    def cancel(self, order_id: str) -> bool:
        order = self.orders.get(order_id)
        if order is None:
            return False
        if order.get("cancelled") or order.get("filled"):
            return False
        order["cancelled"] = True
        order["status"] = "cancelled"
        order["cancelled_at"] = _det_ts(self.seed)
        self.cancel_history.append({
            "order_id": order_id,
            "venue": order["venue"],
            "symbol": order["symbol"],
            "side": order["side"],
            "quantity": order["quantity"],
            "timestamp": order["cancelled_at"],
        })
        _logger.info("router.order_cancelled", order_id=order_id, venue=order["venue"], seed=self.seed)
        return True

    def replace(self, order_id: str, price: Optional[float] = None, quantity: Optional[float] = None) -> str:
        if not self.config.cancel_replace_enabled:
            raise OrderError("cancel_replace disabled", context={"order_id": order_id})
        order = self.orders.get(order_id)
        if order is None:
            raise OrderError("unknown order", context={"order_id": order_id})
        if order.get("cancelled") or order.get("filled"):
            raise OrderError("order not active", context={"order_id": order_id, "status": order.get("status")})
        count = self.cancel_replace_counts.get(order_id, 0)
        if count >= self.config.max_cancel_replace_per_order:
            raise OrderError("max cancel/replace exceeded", context={"order_id": order_id, "count": count, "max": self.config.max_cancel_replace_per_order})
        self.cancel(order_id)
        new_quantity = float(validate_finite(quantity if quantity is not None else order["quantity"], "quantity"))
        new_price_raw = price if price is not None else order["price"]
        new_price = float(validate_finite(new_price_raw, "price"))
        if new_quantity <= 0.0 or new_price <= 0.0:
            raise DataError("replacement price/quantity must be positive")
        self._counter += 1
        new_id = _rid("ord", self.seed, self._counter)
        replacement = {
            **order,
            "order_id": new_id,
            "quantity": new_quantity,
            "price": new_price,
            "status": "routed_paper",
            "cancelled": False,
            "filled": False,
            "replaces": order.get("replaces", 0) + 1,
            "replaced_from": order_id,
            "timestamp": _det_ts(self.seed),
        }
        self.orders[new_id] = replacement
        self.cancel_replace_counts[order_id] = count + 1
        self.replacement_history.append({
            "original_order_id": order_id,
            "replacement_order_id": new_id,
            "venue": order["venue"],
            "symbol": order["symbol"],
            "old_price": order["price"],
            "new_price": new_price,
            "old_quantity": order["quantity"],
            "new_quantity": new_quantity,
            "replace_number": count + 1,
            "timestamp": _det_ts(self.seed),
        })
        _logger.info("router.order_replaced", original=order_id, replacement=new_id, venue=order["venue"], seed=self.seed)
        return new_id

    # -- fills / slippage ---------------------------------------------------
    def track_fill(
        self,
        order_id: str,
        fill_price: float,
        quantity: Optional[float] = None,
        commission: float = 0.0,
        symbol: Optional[str] = None,
    ) -> FillRecord:
        order = self.orders.get(order_id)
        if order is None:
            raise OrderError("unknown order", context={"order_id": order_id})
        fill_price = float(validate_finite(fill_price, "fill_price"))
        if fill_price <= 0.0:
            raise DataError("fill price must be positive", context={"fill_price": fill_price})
        qty = float(validate_finite(quantity if quantity is not None else order["quantity"], "quantity"))
        commission = float(validate_finite(commission, "commission"))
        if qty <= 0.0 or commission < 0.0:
            raise DataError("invalid fill quantity/commission")
        venue = str(order["venue"])
        sym = str(symbol if symbol is not None else order["symbol"])
        side = str(order["side"])
        quote = self.quotes.get(venue, {}).get(sym)
        mid = quote["mid_price"] if quote else fill_price
        slippage_bps = safe_divide(abs(fill_price - mid), mid, 0.0) * 10000.0
        self._counter += 1
        record = FillRecord(
            fill_id=_rid("fill", self.seed, self._counter),
            order_id=order_id,
            venue=venue,
            symbol=sym,
            side=side,
            fill_price=float(fill_price),
            mid_price=float(mid),
            slippage_bps=float(slippage_bps),
            quantity=float(qty),
            commission=float(commission),
            timestamp=_det_ts(self.seed),
        )
        order["filled"] = True
        order["status"] = "filled"
        order["fill_price"] = float(fill_price)
        order["filled_quantity"] = float(qty)
        self.fills.append(record)
        self.last_report = None
        _logger.info("router.fill_tracked", order_id=order_id, fill_id=record.fill_id, slippage_bps=slippage_bps, seed=self.seed)
        return record

    # -- reporting ----------------------------------------------------------
    def slippage_report(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        records = [f for f in self.fills if symbol is None or f.symbol == symbol]
        if not records:
            return {"symbol": symbol, "fills": 0, "total_slippage_bps": 0.0, "avg_slippage_bps": 0.0, "max_slippage_bps": 0.0, "total_commission": 0.0}
        bps = [f.slippage_bps for f in records]
        return {
            "symbol": symbol,
            "fills": len(records),
            "total_slippage_bps": float(sum(bps)),
            "avg_slippage_bps": float(sum(bps) / len(bps)),
            "max_slippage_bps": float(max(bps)),
            "total_commission": float(sum(f.commission for f in records)),
            "paper_only": True,
        }

    def generate_report(self) -> Dict[str, Any]:
        route_costs = [o["total_cost_bps"] for o in self.orders.values()]
        route_latencies = [o["latency_ms"] for o in self.orders.values()]
        slips = [f.slippage_bps for f in self.fills]
        report: Dict[str, Any] = {
            "report": "LATENCY_ROUTING_REPORT",
            "router": "LatencyAwareRouter",
            "campaign": "phase15_crossvenue",
            "seed": self.seed,
            "symbols": list(self.config.symbols),
            "venues": list(self.config.venues),
            "paper_only": True,
            "enable_live": False,
            "timestamp": _det_ts(self.seed),
            "config": asdict(self.config),
            "counts": {
                "routes": len(self.orders),
                "fills": len(self.fills),
                "cancels": len(self.cancel_history),
                "replacements": len(self.replacement_history),
                "venues_tracked": len(self.latency_ewma),
            },
            "latency": {
                venue: {
                    "ewma_ms": float(self.latency_ewma.get(venue, 0.0)),
                    "samples": len(self.latency_samples.get(venue, [])),
                    "max_sample_ms": float(max(self.latency_samples.get(venue, [0.0]))) if self.latency_samples.get(venue) else 0.0,
                    "within_limit": bool(self.latency_ewma.get(venue, 0.0) <= self.config.max_latency_ms),
                }
                for venue in self.config.venues
            },
            "routing": {
                "total_routes": len(self.orders),
                "avg_cost_bps": float(sum(route_costs) / len(route_costs)) if route_costs else 0.0,
                "max_cost_bps": float(max(route_costs)) if route_costs else 0.0,
                "avg_latency_ms": float(sum(route_latencies) / len(route_latencies)) if route_latencies else 0.0,
                "paper_only": True,
            },
            "slippage": {
                "fills": len(self.fills),
                "total_slippage_bps": float(sum(slips)) if slips else 0.0,
                "avg_slippage_bps": float(sum(slips) / len(slips)) if slips else 0.0,
                "max_slippage_bps": float(max(slips)) if slips else 0.0,
                "total_commission": float(sum(f.commission for f in self.fills)),
            },
            "cancels": self.cancel_history,
            "replacements": self.replacement_history,
            "orders": [o for o in self.orders.values()],
        }
        serialized = serialize_metrics_strict(report)
        assert_json_valid(serialized)
        self.last_report = serialized
        return serialized

    def validate_invariants(self) -> Dict[str, Any]:
        problems: List[str] = []
        for order in self.orders.values():
            for name in ("quantity", "price", "latency_ms", "latency_penalty_bps", "slippage_bps", "total_cost_bps", "participation_rate"):
                if not math.isfinite(float(order[name])):
                    problems.append(f"non_finite {name} in {order['order_id']}")
            if order["participation_rate"] < 0.0 or order["participation_rate"] > 1.0:
                problems.append(f"participation out of range {order['order_id']}")
        for venue, ewma in self.latency_ewma.items():
            if not math.isfinite(ewma) or ewma < 0.0:
                problems.append(f"non-finite latency ewma {venue}")
        if self.enable_live:
            problems.append("live path enabled")
        if not self.paper_only:
            problems.append("paper_only not enforced")
        return {
            "valid": len(problems) == 0,
            "problems": problems[:50],
            "problem_count": len(problems),
            "order_count": len(self.orders),
            "fill_count": len(self.fills),
            "paper_only_enforced": bool(self.paper_only),
        }


__all__ = [
    "LatencyAwareRouter",
    "LatencyRouterConfig",
    "RouteResult",
    "FillRecord",
    "default_latency_router_config",
    "DEFAULT_VENUES",
    "DEFAULT_SYMBOLS",
]
