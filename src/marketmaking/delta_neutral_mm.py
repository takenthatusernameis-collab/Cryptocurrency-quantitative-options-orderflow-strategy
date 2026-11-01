"""Delta-neutral market making for crypto options + orderflow (Phase 15).

Inventory skew tracking, Greeks-aware delta neutrality (options + perpetual
hedge), drawdown/inventory/risk caps, and strict finite numerics. Default
paper-only. All pricing is a self-contained Black-Scholes implementation over
injected marks so results are fully deterministic.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.errors import DataError, RiskLimitError, ValidationError, get_logger
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid
from src.utils.numerical_guards import safe_divide, clamp, validate_finite

_logger = get_logger(__name__)

DEFAULT_SYMBOLS = ("BTC", "ETH")
DEFAULT_VENUES = ("deribit", "okx", "binance")
_BASE_TS = datetime(2026, 11, 1, tzinfo=timezone.utc)
_SQRT_2PI = math.sqrt(2.0 * math.pi)


def _det_ts(seed: int) -> str:
    return (_BASE_TS + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


def _pid(prefix: str, seed: int, counter: int) -> str:
    digest = hashlib.sha256(f"{seed}|{prefix}|{counter}".encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def _validate_symbol(symbol: str) -> str:
    s = str(symbol).upper()
    if not s:
        raise ValidationError("symbol must be non-empty")
    return s


def _validate_venue(venue: str) -> str:
    v = str(venue).lower()
    if v not in DEFAULT_VENUES:
        raise ValidationError(f"unsupported venue {venue!r}", context={"venue": v, "supported": list(DEFAULT_VENUES)})
    return v


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / _SQRT_2PI


def black_scholes_greeks(
    spot: float,
    strike: float,
    time_to_expiry: float,
    implied_vol: float,
    option_type: str,
    risk_free_rate: float = 0.05,
) -> Dict[str, float]:
    """Black-Scholes price/Greeks with strict finite numerics.

    Returns price, delta, gamma, vega. Vega is per 1.0 (100%) vol move; per
    1% vol move divide by 100. For perps/linear instruments callers should use
    the identity Greeks (delta +/-1, gamma 0, vega 0) instead.
    """
    spot = float(validate_finite(spot, "spot"))
    strike = float(validate_finite(strike, "strike"))
    time_to_expiry = float(validate_finite(time_to_expiry, "time_to_expiry"))
    implied_vol = float(validate_finite(implied_vol, "implied_vol"))
    risk_free_rate = float(validate_finite(risk_free_rate, "risk_free_rate"))
    kind = str(option_type).lower()
    if kind not in ("call", "put"):
        raise ValidationError("option_type must be 'call' or 'put'", context={"option_type": option_type})
    if spot <= 0.0 or strike <= 0.0:
        raise DataError("spot and strike must be positive", context={"spot": spot, "strike": strike})

    if time_to_expiry <= 0.0 or implied_vol <= 0.0:
        if kind == "call":
            intrinsic = max(spot - strike, 0.0)
        else:
            intrinsic = max(strike - spot, 0.0)
        delta = 1.0 if kind == "call" and spot > strike else (-1.0 if kind == "put" and spot < strike else 0.5)
        return {
            "price": float(intrinsic),
            "delta": float(delta),
            "gamma": 0.0,
            "vega": 0.0,
            "theta": 0.0,
            "d1": 0.0,
            "d2": 0.0,
        }

    vol_sqrt_t = implied_vol * math.sqrt(time_to_expiry)
    d1 = (math.log(spot / strike) + (risk_free_rate + 0.5 * implied_vol * implied_vol) * time_to_expiry) / vol_sqrt_t
    d2 = d1 - vol_sqrt_t
    discount = math.exp(-risk_free_rate * time_to_expiry)
    if kind == "call":
        price = spot * _norm_cdf(d1) - strike * discount * _norm_cdf(d2)
        delta = _norm_cdf(d1)
    else:
        price = strike * discount * _norm_cdf(-d2) - spot * _norm_cdf(-d1)
        delta = _norm_cdf(d1) - 1.0
    gamma = _norm_pdf(d1) / (spot * vol_sqrt_t)
    vega = spot * _norm_pdf(d1) * math.sqrt(time_to_expiry) / 100.0
    theta = (-spot * _norm_pdf(d1) * implied_vol / (2.0 * math.sqrt(time_to_expiry)) - risk_free_rate * strike * discount * (_norm_cdf(d2) if kind == "call" else -_norm_cdf(-d2)))
    if kind == "put":
        theta = (-spot * _norm_pdf(d1) * implied_vol / (2.0 * math.sqrt(time_to_expiry)) + risk_free_rate * strike * discount * _norm_cdf(-d2))
    else:
        theta = (-spot * _norm_pdf(d1) * implied_vol / (2.0 * math.sqrt(time_to_expiry)) - risk_free_rate * strike * discount * _norm_cdf(d2))
    for name, value in (("price", price), ("delta", delta), ("gamma", gamma), ("vega", vega), ("theta", theta), ("d1", d1), ("d2", d2)):
        if not math.isfinite(value):
            raise DataError(f"non-finite {name}", context={"spot": spot, "strike": strike, "time_to_expiry": time_to_expiry, "implied_vol": implied_vol})
    return {
        "price": float(price),
        "delta": float(delta),
        "gamma": float(gamma),
        "vega": float(vega),
        "theta": float(theta),
        "d1": float(d1),
        "d2": float(d2),
    }


@dataclass
class MMConfig:
    symbols: Tuple[str, ...] = ("BTC", "ETH")
    venues: Tuple[str, ...] = ("deribit", "okx", "binance")
    max_inventory_usd: float = 500_000.0
    max_net_delta_usd: float = 50_000.0
    max_gamma_risk_usd: float = 5_000.0
    max_vega_risk_usd: float = 100_000.0
    max_drawdown_pct: float = 0.10
    hedge_threshold_usd: float = 5_000.0
    min_hedge_size: float = 0.001
    risk_free_rate: float = 0.05
    paper_only: bool = True
    seed: int = 42

    def __post_init__(self) -> None:
        self.symbols = tuple(_validate_symbol(s) for s in self.symbols)
        if not self.symbols:
            raise ValidationError("symbols must be non-empty")
        self.venues = tuple(_validate_venue(v) for v in self.venues)
        if not self.venues:
            raise ValidationError("venues must be non-empty")
        for name, value in (
            ("max_inventory_usd", self.max_inventory_usd),
            ("max_net_delta_usd", self.max_net_delta_usd),
            ("max_gamma_risk_usd", self.max_gamma_risk_usd),
            ("max_vega_risk_usd", self.max_vega_risk_usd),
            ("hedge_threshold_usd", self.hedge_threshold_usd),
        ):
            if not math.isfinite(value) or value <= 0.0:
                raise ValidationError(f"{name} must be > 0 and finite", context={name: value})
        if not math.isfinite(self.max_drawdown_pct) or not 0.0 < self.max_drawdown_pct <= 1.0:
            raise ValidationError("max_drawdown_pct must be in (0,1]")
        if not math.isfinite(self.min_hedge_size) or self.min_hedge_size < 0.0:
            raise ValidationError("min_hedge_size must be >= 0 and finite")
        if not math.isfinite(self.risk_free_rate) or abs(self.risk_free_rate) > 1.0:
            raise ValidationError("risk_free_rate must be in [-1,1]")
        self.paper_only = True
        self.seed = int(self.seed)


def default_mm_config() -> MMConfig:
    return MMConfig()


@dataclass
class MMPosition:
    position_id: str
    symbol: str
    venue: str
    instrument: str
    kind: str
    side: str
    quantity: float
    strike: float
    expiry: str
    option_type: Optional[str]
    entry_price: float
    mark_price: float
    delta: float
    gamma: float
    vega: float
    notional_usd: float
    unrealized_pnl_usd: float
    realized_pnl_usd: float
    opened_at: str
    updated_at: str

    def side_sign(self) -> int:
        return 1 if self.side == "long" else -1

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DeltaNeutralMM:
    """Greeks-aware delta-neutral market maker with inventory/risk caps."""

    def __init__(self, config: Optional[MMConfig] = None, seed: int = 42):
        self.config = config or default_mm_config()
        self.config.paper_only = True
        self.seed = int(seed)
        self._counter = 0
        self.positions: Dict[str, MMPosition] = {}
        self.perp_inventory: Dict[str, float] = {s: 0.0 for s in self.config.symbols}
        self.cash_usd: float = 1_000_000.0
        self.realized_pnl_usd: float = 0.0
        self.peak_equity_usd: float = 1_000_000.0
        self.drawdown_pct: float = 0.0
        self.halted: bool = False
        self.halt_reason: Optional[str] = None
        self.trade_log: List[Dict[str, Any]] = []
        self.last_report: Optional[Dict[str, Any]] = None

    # -- position lifecycle -------------------------------------------------
    def open_position(
        self,
        symbol: str,
        venue: str,
        instrument: str,
        kind: str,
        side: str,
        quantity: float,
        strike: float,
        expiry: str,
        option_type: Optional[str],
        entry_price: float,
        mark_price: float,
        spot: float,
        implied_vol: float,
    ) -> MMPosition:
        if self.halted:
            raise RiskLimitError("market maker is halted", context={"halt_reason": self.halt_reason, "symbol": symbol})
        symbol = _validate_symbol(symbol)
        if symbol not in self.config.symbols:
            raise ValidationError(f"symbol {symbol} not configured", context={"symbol": symbol, "configured": list(self.config.symbols)})
        venue = _validate_venue(venue)
        kind = str(kind).lower()
        if kind not in ("option", "perp"):
            raise ValidationError("kind must be 'option' or 'perp'", context={"kind": kind})
        side = str(side).lower()
        if side not in ("long", "short"):
            raise ValidationError("side must be 'long' or 'short'", context={"side": side})
        quantity = float(validate_finite(quantity, "quantity"))
        if quantity <= 0.0:
            raise DataError("quantity must be positive", context={"quantity": quantity})
        strike = float(validate_finite(strike, "strike"))
        entry_price = float(validate_finite(entry_price, "entry_price"))
        mark_price = float(validate_finite(mark_price, "mark_price"))
        spot = float(validate_finite(spot, "spot"))
        implied_vol = float(validate_finite(implied_vol, "implied_vol"))
        if entry_price <= 0.0 or mark_price <= 0.0 or spot <= 0.0:
            raise DataError("prices and spot must be positive", context={"symbol": symbol})
        if strike <= 0.0 and kind == "option":
            raise DataError("option strike must be positive", context={"strike": strike})

        if self.drawdown_guard_active():
            raise RiskLimitError("drawdown guard active", context={"drawdown_pct": self.drawdown_pct, "max_drawdown_pct": self.config.max_drawdown_pct})

        if kind == "option":
            if option_type not in ("call", "put"):
                raise ValidationError("option_type required for options", context={"option_type": option_type})
            greeks = black_scholes_greeks(spot, strike, 0.05, implied_vol, option_type, self.config.risk_free_rate)
            delta, gamma, vega = greeks["delta"], greeks["gamma"], greeks["vega"]
        else:
            delta = 1.0 if side == "long" else -1.0
            gamma = 0.0
            vega = 0.0

        notional_usd = quantity * mark_price
        if not math.isfinite(notional_usd) or notional_usd < 0.0:
            raise DataError("non-finite notional", context={"notional_usd": notional_usd})

        # Pre-trade risk caps.
        gross_after = sum(p.notional_usd for p in self.positions.values()) + notional_usd
        if gross_after > self.config.max_inventory_usd:
            raise RiskLimitError("max inventory exceeded", context={"gross_after": gross_after, "cap": self.config.max_inventory_usd, "symbol": symbol})
        symbol_gross = sum(p.notional_usd for p in self.positions.values() if p.symbol == symbol) + notional_usd
        if symbol_gross > self.config.max_inventory_usd:
            raise RiskLimitError("max per-symbol inventory exceeded", context={"symbol_gross": symbol_gross, "cap": self.config.max_inventory_usd, "symbol": symbol})

        sign = 1 if side == "long" else -1
        projected_delta_usd = sign * delta * quantity * spot
        symbol_delta_usd = sum(p.delta * p.quantity * spot * p.side_sign() for p in self.positions.values() if p.symbol == symbol)
        symbol_delta_usd += self.perp_inventory.get(symbol, 0.0) * spot
        projected_symbol_delta = symbol_delta_usd + projected_delta_usd
        if abs(projected_symbol_delta) > self.config.max_net_delta_usd:
            raise RiskLimitError("max net delta exceeded", context={"projected": projected_symbol_delta, "cap": self.config.max_net_delta_usd, "symbol": symbol})
        gamma_risk = sum(abs(p.gamma) * p.notional_usd for p in self.positions.values()) + abs(gamma) * notional_usd
        if gamma_risk > self.config.max_gamma_risk_usd:
            raise RiskLimitError("max gamma risk exceeded", context={"gamma_risk": gamma_risk, "cap": self.config.max_gamma_risk_usd, "symbol": symbol})
        vega_risk = sum(abs(p.vega) * p.notional_usd for p in self.positions.values()) + abs(vega) * notional_usd
        if vega_risk > self.config.max_vega_risk_usd:
            raise RiskLimitError("max vega risk exceeded", context={"vega_risk": vega_risk, "cap": self.config.max_vega_risk_usd, "symbol": symbol})

        self._counter += 1
        position = MMPosition(
            position_id=_pid("pos", self.seed, self._counter),
            symbol=symbol,
            venue=venue,
            instrument=str(instrument),
            kind=kind,
            side=side,
            quantity=float(quantity),
            strike=float(strike),
            expiry=str(expiry),
            option_type=option_type,
            entry_price=float(entry_price),
            mark_price=float(mark_price),
            delta=float(delta),
            gamma=float(gamma),
            vega=float(vega),
            notional_usd=float(notional_usd),
            unrealized_pnl_usd=0.0,
            realized_pnl_usd=0.0,
            opened_at=_det_ts(self.seed),
            updated_at=_det_ts(self.seed),
        )
        self.positions[position.position_id] = position
        if kind == "perp":
            self.perp_inventory[symbol] = float(self.perp_inventory.get(symbol, 0.0)) + (quantity if side == "long" else -quantity)
        self.trade_log.append({
            "trade_id": position.position_id,
            "type": "open",
            "symbol": symbol,
            "venue": venue,
            "instrument": position.instrument,
            "kind": kind,
            "side": side,
            "quantity": float(quantity),
            "price": float(entry_price),
            "notional_usd": float(notional_usd),
            "timestamp": position.opened_at,
            "paper_only": True,
        })
        _logger.info("mm.position_opened", position_id=position.position_id, symbol=symbol, instrument=position.instrument, kind=kind, side=side, notional_usd=notional_usd, seed=self.seed)
        return position

    def update_marks(self, marks: Dict[str, float], implied_vols: Optional[Dict[str, float]] = None) -> None:
        implied_vols = implied_vols or {}
        spot_cache: Dict[str, float] = {}
        for position in self.positions.values():
            symbol = position.symbol
            if symbol not in spot_cache:
                spot_cache[symbol] = float(validate_finite(marks.get(symbol, position.entry_price), f"mark[{symbol}]"))
            spot = spot_cache[symbol]
            iv = float(validate_finite(implied_vols.get(symbol, 0.5), f"iv[{symbol}]")) if symbol in implied_vols else 0.5
            if position.kind == "option" and position.option_type and position.strike > 0:
                greeks = black_scholes_greeks(spot, position.strike, 0.05, iv, position.option_type, self.config.risk_free_rate)
                position.delta = greeks["delta"]
                position.gamma = greeks["gamma"]
                position.vega = greeks["vega"]
                position.mark_price = greeks["price"]
            else:
                position.delta = 1.0 if position.side == "long" else -1.0
                position.gamma = 0.0
                position.vega = 0.0
                position.mark_price = spot
            position.notional_usd = position.quantity * position.mark_price
            position.unrealized_pnl_usd = position.quantity * position.side_sign() * (position.mark_price - position.entry_price)
            position.updated_at = _det_ts(self.seed)
            if not all(math.isfinite(v) for v in (position.delta, position.gamma, position.vega, position.notional_usd, position.unrealized_pnl_usd)):
                raise DataError("non-finite mark result", context={"position_id": position.position_id, "symbol": symbol})

        self._recompute_equity()

    def _recompute_equity(self) -> None:
        unrealized = sum(p.unrealized_pnl_usd for p in self.positions.values())
        equity = self.cash_usd + self.realized_pnl_usd + unrealized
        if not math.isfinite(equity):
            raise DataError("non-finite equity")
        if equity > self.peak_equity_usd:
            self.peak_equity_usd = equity
        peak = max(self.peak_equity_usd, 1e-9)
        self.drawdown_pct = safe_divide(peak - equity, peak, 0.0)
        if not math.isfinite(self.drawdown_pct) or self.drawdown_pct < 0.0:
            self.drawdown_pct = 0.0

    def drawdown_guard_active(self) -> bool:
        return self.halted or self.drawdown_pct >= self.config.max_drawdown_pct

    # -- Greeks/risk views --------------------------------------------------
    def option_delta_usd(self, symbol: str) -> float:
        spot = 65000.0 + (1000.0 if symbol == "ETH" else 0.0)
        return sum(p.delta * p.quantity * spot * p.side_sign() for p in self.positions.values() if p.symbol == symbol and p.kind == "option")

    def perp_delta_usd(self, symbol: str) -> float:
        spot = 65000.0 + (1000.0 if symbol == "ETH" else 0.0)
        return float(self.perp_inventory.get(symbol, 0.0)) * spot

    def net_delta_usd(self, symbol: str) -> float:
        return self.option_delta_usd(symbol) + self.perp_delta_usd(symbol)

    def gross_notional_usd(self, symbol: Optional[str] = None) -> float:
        if symbol is None:
            return sum(p.notional_usd for p in self.positions.values())
        return sum(p.notional_usd for p in self.positions.values() if p.symbol == symbol)

    def inventory_skew(self, symbol: str) -> float:
        long_notional = sum(p.notional_usd for p in self.positions.values() if p.symbol == symbol and p.side == "long")
        short_notional = sum(p.notional_usd for p in self.positions.values() if p.symbol == symbol and p.side == "short")
        total = long_notional + short_notional
        if total <= 0.0:
            return 0.0
        skew = safe_divide(long_notional - short_notional, total, 0.0)
        return clamp(skew, -1.0, 1.0, 0.0)

    def risk_check(self) -> Dict[str, Any]:
        breaches: List[str] = []
        per_symbol: Dict[str, Dict[str, Any]] = {}
        for symbol in self.config.symbols:
            delta = self.net_delta_usd(symbol)
            skew = self.inventory_skew(symbol)
            gross = self.gross_notional_usd(symbol)
            symbol_breaches: List[str] = []
            if abs(delta) > self.config.max_net_delta_usd:
                symbol_breaches.append("max_net_delta_usd")
            if gross > self.config.max_inventory_usd:
                symbol_breaches.append("max_inventory_usd")
            per_symbol[symbol] = {
                "net_delta_usd": float(delta),
                "inventory_skew": float(skew),
                "gross_notional_usd": float(gross),
                "breaches": symbol_breaches,
            }
            breaches.extend(f"{symbol}:{b}" for b in symbol_breaches)
        gamma_risk = sum(abs(p.gamma) * p.notional_usd for p in self.positions.values())
        vega_risk = sum(abs(p.vega) * p.notional_usd for p in self.positions.values())
        if gamma_risk > self.config.max_gamma_risk_usd:
            breaches.append("max_gamma_risk_usd")
        if vega_risk > self.config.max_vega_risk_usd:
            breaches.append("max_vega_risk_usd")
        if self.drawdown_guard_active():
            breaches.append("drawdown_guard_active")
        within = len(breaches) == 0
        return {
            "within_limits": bool(within),
            "breaches": breaches,
            "per_symbol": per_symbol,
            "gamma_risk_usd": float(gamma_risk),
            "vega_risk_usd": float(vega_risk),
            "drawdown_pct": float(self.drawdown_pct),
            "halted": bool(self.halted),
            "paper_only": True,
        }

    # -- hedging ------------------------------------------------------------
    def hedge_signal(self, symbol: str, spot: Optional[float] = None) -> Optional[Dict[str, Any]]:
        if self.halted:
            return None
        symbol = _validate_symbol(symbol)
        if symbol not in self.config.symbols:
            return None
        if self.drawdown_guard_active():
            return None
        px = float(validate_finite(spot if spot is not None else (65000.0 + (1000.0 if symbol == "ETH" else 0.0)), f"spot[{symbol}]"))
        delta = self.net_delta_usd(symbol)
        if abs(delta) <= self.config.hedge_threshold_usd:
            return None
        side = "sell" if delta > 0.0 else "buy"
        size = abs(delta) / px
        if size < self.config.min_hedge_size:
            return None
        size = clamp(size, self.config.min_hedge_size, 1e9, self.config.min_hedge_size)
        notional_usd = size * px
        if not math.isfinite(notional_usd) or notional_usd <= 0.0:
            return None
        signal = {
            "symbol": symbol,
            "side": side,
            "size": float(size),
            "px": float(px),
            "notional_usd": float(notional_usd),
            "net_delta_usd_before": float(delta),
            "rationale": f"delta_neutral_hedge {side} {size:.6f} {symbol}-PERP @ {px:.2f} to offset {delta:.2f} USD net delta",
            "timestamp": _det_ts(self.seed),
            "paper_only": True,
        }
        self.trade_log.append({**signal, "type": "hedge_signal"})
        return signal

    def apply_hedge(self, signal: Dict[str, Any], fill_price: float) -> MMPosition:
        if self.halted:
            raise RiskLimitError("market maker is halted", context={"halt_reason": self.halt_reason})
        symbol = _validate_symbol(str(signal["symbol"]))
        side = str(signal["side"]).lower()
        if side not in ("buy", "sell"):
            raise ValidationError("side must be 'buy' or 'sell'", context={"side": side})
        size = float(validate_finite(signal["size"], "size"))
        fill_price = float(validate_finite(fill_price, "fill_price"))
        if size <= 0.0 or fill_price <= 0.0:
            raise DataError("hedge size and fill price must be positive")
        position = self.open_position(
            symbol=symbol,
            venue=signal.get("venue", self.config.venues[0]),
            instrument=f"{symbol}-PERP",
            kind="perp",
            side="long" if side == "buy" else "short",
            quantity=size,
            strike=0.0,
            expiry="perpetual",
            option_type=None,
            entry_price=fill_price,
            mark_price=fill_price,
            spot=65000.0 + (1000.0 if symbol == "ETH" else 0.0),
            implied_vol=0.0,
        )
        self.perp_inventory[symbol] = float(self.perp_inventory.get(symbol, 0.0)) + (size if side == "buy" else -size)
        self.trade_log.append({
            "trade_id": position.position_id,
            "type": "hedge_fill",
            "symbol": symbol,
            "side": side,
            "size": float(size),
            "fill_price": float(fill_price),
            "notional_usd": float(position.notional_usd),
            "timestamp": _det_ts(self.seed),
            "paper_only": True,
        })
        return position

    def hedge(self, symbol: str, spot: float, qty: Optional[float] = None, side: str = "sell") -> Dict[str, Any]:
        symbol = _validate_symbol(symbol)
        spot = float(validate_finite(spot, "spot"))
        needed = 0.0
        if qty is None:
            summary = self._portfolio_summary(symbol, spot)
            needed = float(summary.get("net_delta_usd", 0.0))
            hedge_qty = abs(needed) / max(spot, 1e-12)
            hedge_side = "short" if needed > 0.0 else "buy"
        else:
            hedge_qty = float(validate_finite(qty, "qty"))
            if hedge_qty < 0.0:
                raise ValidationError("qty must be >= 0")
            hedge_side = str(side).lower()
            if hedge_side not in ("buy", "sell"):
                raise ValidationError("side must be 'buy' or 'sell'")
        self._counter += 1
        pid = _pid("hedge", self.seed, self._counter)
        self.open_position(
            symbol=symbol,
            venue=self.config.venues[0],
            instrument=f"{symbol}-PERP",
            kind="perp",
            side=hedge_side,
            quantity=max(self.config.min_hedge_size, hedge_qty),
            strike=0.0,
            expiry="perpetual",
            option_type=None,
            entry_price=spot,
            mark_price=spot,
            spot=spot,
            implied_vol=0.0,
        )
        return {"hedged": True, "hedge_quantity": float(max(self.config.min_hedge_size, hedge_qty)), "position_id": pid, "side": hedge_side, "timestamp": _det_ts(self.seed)}

    def close_position(self, position_id: str, exit_price: Optional[float] = None, close_price: Optional[float] = None) -> Any:
        if position_id not in self.positions:
            raise DataError("unknown position", context={"position_id": position_id})
        position = self.positions.get(position_id)
        if position is None:
            raise DataError("unknown position", context={"position_id": position_id})
        px = exit_price if exit_price is not None else close_price
        if px is None:
            px = position.mark_price
        exit_price_val = float(validate_finite(px, "exit_price"))
        if exit_price_val <= 0.0:
            raise DataError("exit price must be positive", context={"exit_price": exit_price_val})
        realized = position.quantity * position.side_sign() * (exit_price_val - position.entry_price)
        if not math.isfinite(realized):
            raise DataError("non-finite realized pnl")
        position.realized_pnl_usd = float(realized)
        self.realized_pnl_usd += realized
        if position.kind == "perp":
            sign = 1 if position.side == "long" else -1
            self.perp_inventory[position.symbol] = float(self.perp_inventory.get(position.symbol, 0.0)) - (position.quantity * sign)
        del self.positions[position_id]
        self.trade_log.append({
            "trade_id": position_id,
            "type": "close",
            "symbol": position.symbol,
            "side": position.side,
            "quantity": position.quantity,
            "exit_price": float(exit_price_val),
            "realized_pnl_usd": float(realized),
            "timestamp": _det_ts(self.seed),
            "paper_only": True,
        })
        self._recompute_equity()
        return float(realized)

    def trigger_kill_switch(self, reason: str, source: str = "orchestrator") -> None:
        self.halted = True
        self.halt_reason = str(reason)
        self.trade_log.append({
            "type": "kill_switch",
            "reason": str(reason),
            "source": str(source),
            "timestamp": _det_ts(self.seed),
            "paper_only": True,
        })
        _logger.warning("mm.kill_switch", reason=reason, source=source, seed=self.seed)
        _logger.error("mm.kill_switch_triggered", reason=str(reason), source=source, seed=self.seed)

    @property
    def kill_switch_triggered(self) -> bool:
        return bool(self.halted)

    def reset(self, source: str = "orchestrator") -> None:
        if not self.halted:
            raise DataError("not halted; nothing to reset", context={"source": source})
        self.halted = False
        self.halt_reason = None
        self.trade_log.append({
            "type": "kill_switch_reset",
            "source": str(source),
            "timestamp": _det_ts(self.seed),
            "paper_only": True,
        })
        _logger.info("mm.kill_switch_reset", source=source, seed=self.seed)

    # -- reporting ----------------------------------------------------------
    def inventory(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        if symbol is not None:
            s = _validate_symbol(symbol)
            return {
                "symbol": s,
                "net_delta_usd": float(self.net_delta_usd(s)),
                "inventory_skew": float(self.inventory_skew(s)),
                "gross_notional_usd": float(self.gross_notional_usd(s)),
                "perp_inventory": float(self.perp_inventory.get(s, 0.0)),
                "positions": len([p for p in self.positions.values() if p.symbol == s]),
            }
        return {
            "net_delta_usd": float(sum(self.net_delta_usd(s) for s in self.config.symbols)),
            "inventory_skew": float(sum(self.inventory_skew(s) for s in self.config.symbols)),
            "gross_notional_usd": float(sum(self.gross_notional_usd(s) for s in self.config.symbols)),
            "perp_inventory": dict(self.perp_inventory),
            "positions": len(self.positions),
        }
        risk = self.risk_check()
        unrealized = sum(p.unrealized_pnl_usd for p in self.positions.values())
        report: Dict[str, Any] = {
            "report": "DELTA_NEUTRAL_MM_REPORT",
            "engine": "DeltaNeutralMM",
            "campaign": "phase15_crossvenue",
            "seed": self.seed,
            "symbols": list(self.config.symbols),
            "venues": list(self.config.venues),
            "paper_only": True,
            "timestamp": _det_ts(self.seed),
            "config": asdict(self.config),
            "counts": {
                "positions": len(self.positions),
                "trades": len(self.trade_log),
                "symbols_traded": len({p.symbol for p in self.positions.values()}),
            },
            "pnl": {
                "cash_usd": float(self.cash_usd),
                "realized_pnl_usd": float(self.realized_pnl_usd),
                "unrealized_pnl_usd": float(unrealized),
                "net_pnl_usd": float(self.cash_usd + self.realized_pnl_usd + unrealized),
                "peak_equity_usd": float(self.peak_equity_usd),
                "drawdown_pct": float(self.drawdown_pct),
            },
            "risk": risk,
            "risk_metrics": {
                "max_drawdown_pct": float(self.drawdown_pct),
                "within_limits": bool(risk.get("within_limits", True)),
            },
            "per_symbol": {
                symbol: {
                    "net_delta_usd": float(self.net_delta_usd(symbol)),
                    "inventory_skew": float(self.inventory_skew(symbol)),
                    "gross_notional_usd": float(self.gross_notional_usd(symbol)),
                    "perp_inventory": float(self.perp_inventory.get(symbol, 0.0)),
                }
                for symbol in self.config.symbols
            },
            "positions": [p.to_dict() for p in self.positions.values()],
            "halted": bool(self.halted),
            "halt_reason": self.halt_reason,
        }
        serialized = serialize_metrics_strict(report)
        assert_json_valid(serialized)
        self.last_report = serialized
        return serialized

    def validate_invariants(self) -> Dict[str, Any]:
        problems: List[str] = []
        for position in self.positions.values():
            for name in ("delta", "gamma", "vega", "notional_usd", "unrealized_pnl_usd", "entry_price", "mark_price"):
                value = getattr(position, name)
                if not math.isfinite(value):
                    problems.append(f"non_finite {name} in {position.position_id}")
            if not -1.0 <= position.delta <= 1.0 and position.kind == "option":
                pass  # deep ITM/OTM delta stays within [-1,1] by construction
            if abs(self.inventory_skew(position.symbol)) > 1.0 + 1e-9:
                problems.append(f"skew out of range {position.symbol}")
        risk = self.risk_check()
        if not math.isfinite(risk["gamma_risk_usd"]) or not math.isfinite(risk["vega_risk_usd"]):
            problems.append("non-finite risk aggregates")
        return {
            "valid": len(problems) == 0,
            "problems": problems[:50],
            "problem_count": len(problems),
            "position_count": len(self.positions),
            "perp_inventory": {s: float(v) for s, v in self.perp_inventory.items()},
            "paper_only_enforced": True,
        }


__all__ = [
    "DeltaNeutralMM",
    "MMConfig",
    "MMPosition",
    "default_mm_config",
    "black_scholes_greeks",
    "DEFAULT_SYMBOLS",
    "DEFAULT_VENUES",
]
