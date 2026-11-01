"""Cross-exchange arbitrage detection for crypto options + orderflow (Phase 15).

Deterministic cross-venue spread detection across Deribit/OKX/Binance with
fee-adjusted net edge, stale-quote filtering, volatility/spread sanity checks,
and strict finite numerics. Default paper-only. No live-market dependencies:
all inputs are injected quotes, making detection fully reproducible.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

from src.errors import DataError, ValidationError, get_logger
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid
from src.utils.numerical_guards import safe_divide, clamp, validate_finite

_logger = get_logger(__name__)

SUPPORTED_VENUES = ("deribit", "okx", "binance")
DEFAULT_SYMBOLS = ("BTC", "ETH")
_BASE_TS = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _det_ts(seed: int) -> str:
    return (_BASE_TS + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


def _did(prefix: str, seed: int, counter: int) -> str:
    digest = hashlib.sha256(f"{seed}|{prefix}|{counter}".encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _parse_iso(value: str) -> datetime:
    text = str(value)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def _validate_venue(venue: str) -> str:
    v = str(venue).lower()
    if v not in SUPPORTED_VENUES:
        raise ValidationError(
            f"Unsupported venue {venue!r}",
            context={"venue": v, "supported": list(SUPPORTED_VENUES)},
        )
    return v


def _validate_symbol(symbol: str) -> str:
    s = str(symbol).upper()
    if not s:
        raise ValidationError("Symbol must be non-empty")
    return s


@dataclass
class ArbitrageQuote:
    """A single venue quote for a symbol, with publish/receive timestamps."""

    venue: str
    symbol: str
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    timestamp: str
    received_at: str
    source: str = "orderflow"

    def __post_init__(self) -> None:
        self.venue = _validate_venue(self.venue)
        self.symbol = _validate_symbol(self.symbol)
        self.bid = float(validate_finite(self.bid, "bid"))
        self.ask = float(validate_finite(self.ask, "ask"))
        self.bid_size = float(validate_finite(self.bid_size, "bid_size"))
        self.ask_size = float(validate_finite(self.ask_size, "ask_size"))
        if self.bid <= 0.0:
            raise DataError("bid must be positive", context={"venue": self.venue, "symbol": self.symbol, "bid": self.bid})
        if self.ask <= 0.0:
            raise DataError("ask must be positive", context={"venue": self.venue, "symbol": self.symbol, "ask": self.ask})
        if self.ask < self.bid - 1e-12:
            raise DataError("ask must be >= bid", context={"venue": self.venue, "symbol": self.symbol, "bid": self.bid, "ask": self.ask})
        if self.bid_size < 0.0 or self.ask_size < 0.0:
            raise DataError("sizes must be non-negative", context={"venue": self.venue, "symbol": self.symbol})
        self.timestamp = str(self.timestamp)
        self.received_at = str(self.received_at)
        _parse_iso(self.timestamp)
        _parse_iso(self.received_at)
        self.source = str(self.source)

    @property
    def mid_price(self) -> float:
        return (self.bid + self.ask) / 2.0

    @property
    def spread_bps(self) -> float:
        return safe_divide(self.ask - self.bid, self.mid_price, 0.0) * 10000.0

    @property
    def age_sec(self) -> float:
        return (_parse_iso(self.received_at) - _parse_iso(self.timestamp)).total_seconds()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "venue": self.venue,
            "symbol": self.symbol,
            "bid": float(self.bid),
            "ask": float(self.ask),
            "bid_size": float(self.bid_size),
            "ask_size": float(self.ask_size),
            "timestamp": self.timestamp,
            "received_at": self.received_at,
            "source": self.source,
            "mid_price": float(self.mid_price),
            "spread_bps": float(self.spread_bps),
            "age_sec": float(self.age_sec),
        }


@dataclass
class ArbitrageConfig:
    venues: Tuple[str, ...] = ("deribit", "okx", "binance")
    symbols: Tuple[str, ...] = ("BTC", "ETH")
    min_edge_bps: float = 5.0
    taker_fee_bps: Dict[str, float] = field(default_factory=lambda: {"deribit": 5.0, "okx": 5.0, "binance": 4.0})
    max_spread_bps: float = 50.0
    max_implied_vol: float = 1.5
    stale_quote_sec: float = 5.0
    min_size_usd: float = 1_000.0
    max_notional_usd: float = 100_000.0
    paper_only: bool = True
    seed: int = 42

    def __post_init__(self) -> None:
        self.venues = tuple(_validate_venue(v) for v in self.venues)
        if not self.venues:
            raise ValidationError("venues must be non-empty")
        self.symbols = tuple(_validate_symbol(s) for s in self.symbols)
        if not self.symbols:
            raise ValidationError("symbols must be non-empty")
        for venue, fee in self.taker_fee_bps.items():
            _validate_venue(venue)
            f = float(validate_finite(fee, f"taker_fee_bps[{venue}]"))
            if f < 0.0 or f > 100.0:
                raise ValidationError("taker_fee_bps must be in [0,100]", context={"venue": venue, "fee": f})
            self.taker_fee_bps[venue] = f
        if not math.isfinite(self.min_edge_bps) or self.min_edge_bps < 0.0:
            raise ValidationError("min_edge_bps must be >= 0 and finite")
        if not math.isfinite(self.max_spread_bps) or self.max_spread_bps <= 0.0:
            raise ValidationError("max_spread_bps must be > 0 and finite")
        if not math.isfinite(self.max_implied_vol) or self.max_implied_vol <= 0.0:
            raise ValidationError("max_implied_vol must be > 0 and finite")
        if not math.isfinite(self.stale_quote_sec) or self.stale_quote_sec < 0.0:
            raise ValidationError("stale_quote_sec must be >= 0 and finite")
        if not math.isfinite(self.min_size_usd) or self.min_size_usd < 0.0:
            raise ValidationError("min_size_usd must be >= 0 and finite")
        if not math.isfinite(self.max_notional_usd) or self.max_notional_usd <= 0.0:
            raise ValidationError("max_notional_usd must be > 0 and finite")
        self.paper_only = True
        self.seed = int(self.seed)


def default_arbitrage_config() -> ArbitrageConfig:
    return ArbitrageConfig()


@dataclass
class ArbitrageOpportunity:
    """A detected cross-venue arbitrage opportunity with fee-adjusted net edge."""

    opportunity_id: str
    symbol: str
    buy_venue: str
    sell_venue: str
    ask_price: float
    bid_price: float
    spread_bps: float
    buy_fee_bps: float
    sell_fee_bps: float
    total_fee_bps: float
    net_edge_bps: float
    estimated_size: float
    estimated_notional_usd: float
    gross_edge_usd: float
    net_edge_usd: float
    buy_age_sec: float
    sell_age_sec: float
    timestamp: str
    qualified: bool
    rejection_reason: Optional[str]

    def __post_init__(self) -> None:
        for name in (
            "ask_price", "bid_price", "spread_bps", "buy_fee_bps", "sell_fee_bps",
            "total_fee_bps", "net_edge_bps", "estimated_size", "estimated_notional_usd",
            "gross_edge_usd", "net_edge_usd", "buy_age_sec", "sell_age_sec",
        ):
            value = getattr(self, name)
            validate_finite(value, name)
        if self.ask_price <= 0.0 or self.bid_price <= 0.0:
            raise DataError("prices must be positive", context={"symbol": self.symbol})
        if self.estimated_size < 0.0 or self.estimated_notional_usd < 0.0:
            raise DataError("size/notional must be non-negative", context={"symbol": self.symbol})
        self.buy_venue = _validate_venue(self.buy_venue)
        self.sell_venue = _validate_venue(self.sell_venue)
        self.symbol = _validate_symbol(self.symbol)
        self.timestamp = str(self.timestamp)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ArbitrageDetector:
    """Deterministic cross-venue arbitrage detector (paper-only by default)."""

    def __init__(self, config: Optional[ArbitrageConfig] = None, seed: int = 42):
        self.config = config or default_arbitrage_config()
        self.config.paper_only = True
        self.seed = int(seed)
        self._counter = 0
        self.quotes: List[ArbitrageQuote] = []
        self.rejections: List[Dict[str, Any]] = []
        self.last_opportunities: List[ArbitrageOpportunity] = []
        self.last_report: Optional[Dict[str, Any]] = None

    def submit_quotes(self, quotes: Iterable[ArbitrageQuote]) -> int:
        accepted = 0
        for quote in quotes:
            if not isinstance(quote, ArbitrageQuote):
                raise DataError("quote must be an ArbitrageQuote instance", context={"type": type(quote).__name__})
            if quote.venue not in self.config.venues:
                continue
            if quote.symbol not in self.config.symbols:
                continue
            self.quotes.append(quote)
            accepted += 1
        _logger.info("arbitrage.quotes_submitted", accepted=accepted, venue_count=len(self.config.venues), symbol_count=len(self.config.symbols), seed=self.seed)
        return accepted

    def clear_quotes(self) -> None:
        self.quotes = []
        self.rejections = []
        self.last_opportunities = []
        self.last_report = None

    def _freshest_per_venue(self, symbol: str) -> Dict[str, ArbitrageQuote]:
        freshest: Dict[str, ArbitrageQuote] = {}
        for quote in self.quotes:
            if quote.symbol != symbol:
                continue
            current = freshest.get(quote.venue)
            if current is None or _parse_iso(quote.received_at) >= _parse_iso(current.received_at):
                freshest[quote.venue] = quote
        return freshest

    def _reject(self, symbol: str, venue: str, reason: str, detail: Any) -> None:
        self.rejections.append({
            "symbol": symbol,
            "venue": venue,
            "reason": reason,
            "detail": float(detail) if isinstance(detail, (int, float)) else str(detail),
        })

    def detect(
        self,
        spot: Optional[Dict[str, float]] = None,
        implied_vol: Optional[Dict[str, float]] = None,
    ) -> List[ArbitrageOpportunity]:
        spots = {s: float(validate_finite(spot.get(s, 65000.0 + (1000.0 if s == "ETH" else 0.0)), f"spot[{s}]")) for s in self.config.symbols}
        vols: Dict[str, float] = {}
        if implied_vol is not None:
            for symbol in self.config.symbols:
                raw = implied_vol.get(symbol)
                vols[symbol] = float(validate_finite(raw, f"implied_vol[{symbol}]")) if raw is not None else 0.0

        opportunities: List[ArbitrageOpportunity] = []
        self.rejections = []

        for symbol in self.config.symbols:
            px = spots[symbol]
            iv = vols.get(symbol, 0.0)
            vol_halted = bool(implied_vol is not None and symbol in implied_vol and math.isfinite(iv) and iv > self.config.max_implied_vol)
            freshest = self._freshest_per_venue(symbol)

            for buy_venue in sorted(freshest):
                ask_q = freshest[buy_venue]
                if ask_q.age_sec > self.config.stale_quote_sec:
                    self._reject(symbol, buy_venue, "stale_quote", ask_q.age_sec)
                    continue
                if ask_q.ask_size <= 0.0:
                    self._reject(symbol, buy_venue, "zero_ask_size", ask_q.ask_size)
                    continue
                if ask_q.spread_bps > self.config.max_spread_bps:
                    self._reject(symbol, buy_venue, "wide_spread", ask_q.spread_bps)
                    continue

                for sell_venue in sorted(freshest):
                    if sell_venue == buy_venue:
                        continue
                    bid_q = freshest[sell_venue]
                    if bid_q.age_sec > self.config.stale_quote_sec:
                        self._reject(symbol, sell_venue, "stale_quote", bid_q.age_sec)
                        continue
                    if bid_q.bid_size <= 0.0:
                        self._reject(symbol, sell_venue, "zero_bid_size", bid_q.bid_size)
                        continue
                    if bid_q.spread_bps > self.config.max_spread_bps:
                        self._reject(symbol, sell_venue, "wide_spread", bid_q.spread_bps)
                        continue

                    cross_bid = float(bid_q.bid)
                    cross_ask = float(ask_q.ask)
                    if cross_bid <= cross_ask:
                        self._reject(symbol, f"{buy_venue}->{sell_venue}", "negative_spread", cross_bid - cross_ask)
                        continue

                    mid = (cross_bid + cross_ask) / 2.0
                    spread_bps = safe_divide(cross_bid - cross_ask, mid, 0.0) * 10000.0

                    buy_fee = float(self.config.taker_fee_bps.get(buy_venue, 0.0))
                    sell_fee = float(self.config.taker_fee_bps.get(sell_venue, 0.0))
                    total_fee_bps = buy_fee + sell_fee
                    net_edge_bps = spread_bps - total_fee_bps

                    size = min(ask_q.ask_size, bid_q.bid_size)
                    notional_usd = size * mid
                    if notional_usd < self.config.min_size_usd:
                        self._reject(symbol, f"{buy_venue}->{sell_venue}", "min_size", notional_usd)
                        continue
                    if notional_usd > self.config.max_notional_usd:
                        size = self.config.max_notional_usd / mid if mid > 0 else 0.0
                        notional_usd = self.config.max_notional_usd

                    gross_edge_usd = (spread_bps / 10000.0) * notional_usd
                    net_edge_usd = (net_edge_bps / 10000.0) * notional_usd

                    qualified = (
                        not vol_halted
                        and net_edge_bps >= self.config.min_edge_bps - 1e-12
                        and size > 0.0
                        and math.isfinite(net_edge_usd)
                    )

                    self._counter += 1
                    opportunities.append(
                        ArbitrageOpportunity(
                            opportunity_id=_did("arb", self.seed, self._counter),
                            symbol=symbol,
                            buy_venue=buy_venue,
                            sell_venue=sell_venue,
                            ask_price=float(cross_ask),
                            bid_price=float(cross_bid),
                            spread_bps=float(spread_bps),
                            buy_fee_bps=float(buy_fee),
                            sell_fee_bps=float(sell_fee),
                            total_fee_bps=float(total_fee_bps),
                            net_edge_bps=float(net_edge_bps),
                            estimated_size=float(size),
                            estimated_notional_usd=float(notional_usd),
                            gross_edge_usd=float(gross_edge_usd),
                            net_edge_usd=float(net_edge_usd),
                            buy_age_sec=float(ask_q.age_sec),
                            sell_age_sec=float(bid_q.age_sec),
                            timestamp=_det_ts(self.seed),
                            qualified=bool(qualified),
                            rejection_reason=None if qualified else ("volatility_sanity" if vol_halted else "below_min_edge"),
                        )
                    )

        opportunities.sort(key=lambda o: (-o.net_edge_bps, o.opportunity_id))
        self.last_opportunities = opportunities
        _logger.info("arbitrage.detect_complete", symbol_count=len(self.config.symbols), detected=len(opportunities), qualified=sum(1 for o in opportunities if o.qualified), rejections=len(self.rejections), seed=self.seed)
        return opportunities

    def generate_report(self, opportunities: Optional[List[ArbitrageOpportunity]] = None) -> Dict[str, Any]:
        if opportunities is None:
            opportunities = self.last_opportunities
        report: Dict[str, Any] = {
            "report": "ARBITRAGE_REPORT",
            "detector": "ArbitrageDetector",
            "campaign": "phase15_crossvenue",
            "seed": self.seed,
            "symbols": list(self.config.symbols),
            "venues": list(self.config.venues),
            "paper_only": True,
            "timestamp": _det_ts(self.seed),
            "config": asdict(self.config),
            "counts": {
                "quotes_submitted": len(self.quotes),
                "venues_seen": len({q.venue for q in self.quotes}),
                "symbols_seen": len({q.symbol for q in self.quotes}),
                "opportunities_detected": len(opportunities),
                "qualified": sum(1 for o in opportunities if o.qualified),
                "rejections": len(self.rejections),
            },
            "rejections": self.rejections,
            "opportunities": [o.to_dict() for o in opportunities],
        }
        serialized = serialize_metrics_strict(report)
        assert_json_valid(serialized)
        self.last_report = serialized
        return serialized

    def validate_invariants(self, opportunities: Optional[List[ArbitrageOpportunity]] = None) -> Dict[str, Any]:
        if opportunities is None:
            opportunities = self.last_opportunities
        problems: List[str] = []
        seen_ids: List[str] = []
        for opportunity in opportunities:
            for name in ("net_edge_bps", "spread_bps", "gross_edge_usd", "net_edge_usd", "estimated_notional_usd"):
                value = getattr(opportunity, name)
                if not math.isfinite(value):
                    problems.append(f"non_finite {name} in {opportunity.opportunity_id}")
            if opportunity.opportunity_id in seen_ids:
                problems.append(f"duplicate id {opportunity.opportunity_id}")
            seen_ids.append(opportunity.opportunity_id)
            if opportunity.qualified:
                if opportunity.net_edge_bps < self.config.min_edge_bps - 1e-9:
                    problems.append(f"qualified below min edge {opportunity.opportunity_id}")
                if opportunity.rejection_reason is not None:
                    problems.append(f"qualified with rejection reason {opportunity.opportunity_id}")
            expected_net = opportunity.spread_bps - opportunity.total_fee_bps
            if abs(opportunity.net_edge_bps - expected_net) > 1e-9:
                problems.append(f"fee math mismatch {opportunity.opportunity_id}")
            expected_spread = safe_divide(opportunity.bid_price - opportunity.ask_price, (opportunity.bid_price + opportunity.ask_price) / 2.0, 0.0) * 10000.0
            if abs(opportunity.spread_bps - expected_spread) > 1e-6:
                problems.append(f"spread math mismatch {opportunity.opportunity_id}")
        return {
            "valid": len(problems) == 0,
            "problems": problems[:50],
            "problem_count": len(problems),
            "opportunity_count": len(opportunities),
            "qualified_count": sum(1 for o in opportunities if o.qualified),
            "paper_only_enforced": True,
        }


__all__ = [
    "ArbitrageDetector",
    "ArbitrageConfig",
    "ArbitrageOpportunity",
    "ArbitrageQuote",
    "default_arbitrage_config",
    "SUPPORTED_VENUES",
    "DEFAULT_SYMBOLS",
]
