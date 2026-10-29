"""Data normalization utilities across venues."""

import math
from datetime import datetime, timezone
from typing import List, Optional

import numpy as np

from ..errors import DataError, NonFiniteResultError
from ..telemetry.error_logging import log_error_with_context
from ..utils.numerical_guards import ensure_finite, safe_divide, validate_finite
from .schemas import OptionsChain, OrderflowSnapshot, Trade


def normalize_symbol(symbol: str, venue: str) -> str:
    """Normalize symbol format across venues."""
    if not symbol:
        return ""
    s = str(symbol).upper().strip()
    # Remove common separators
    s = s.replace("-", "").replace("_", "").replace("/", "")
    return s


def normalize_timestamp(ts: Optional[datetime]) -> datetime:
    if ts is None:
        return datetime.now(timezone.utc)
    if ts.tzinfo is None:
        return ts.replace(tzinfo=timezone.utc)
    return ts.astimezone(timezone.utc)


def calculate_moneyness(spot: float, strike: float) -> float:
    """Calculate moneyness as strike/spot with numerical guards."""
    try:
        spot_f = validate_finite(spot, "spot", context={"function": "calculate_moneyness"})
        strike_f = validate_finite(strike, "strike", context={"function": "calculate_moneyness"})
    except (NonFiniteResultError, Exception) as e:
        try:
            log_error_with_context(
                "calculate_moneyness: non-finite input",
                operation="calculate_moneyness",
                module="src.data.normalization",
                extra={"spot": spot, "strike": strike},
                exc=e,
            )
        except Exception:
            pass
        return 0.0
    if spot_f <= 0 or not math.isfinite(spot_f):
        try:
            log_error_with_context(
                "calculate_moneyness: invalid spot",
                operation="calculate_moneyness",
                module="src.data.normalization",
                extra={"spot": spot_f},
            )
        except Exception:
            pass
        return 0.0
    if not math.isfinite(strike_f):
        return 0.0
    moneyness = safe_divide(strike_f, spot_f, default=0.0, operation="calculate_moneyness")
    if not math.isfinite(moneyness):
        return 0.0
    return float(moneyness)


def calculate_cumulative_delta(trades: List[Trade]) -> float:
    """Calculate cumulative delta from trade flow with numerical guards."""
    delta = 0.0
    if not trades:
        return 0.0
    for trade in trades:
        try:
            side = str(getattr(trade, "side", "")).lower().strip()
            size = getattr(trade, "size", 0.0)
            size_f = validate_finite(size, "trade.size", context={"function": "calculate_cumulative_delta"})
        except (NonFiniteResultError, Exception) as e:
            try:
                log_error_with_context(
                    "calculate_cumulative_delta: skipping invalid trade",
                    operation="calculate_cumulative_delta",
                    module="src.data.normalization",
                    extra={"side": getattr(trade, "side", None), "size": getattr(trade, "size", None)},
                    exc=e,
                )
            except Exception:
                pass
            continue
        if not math.isfinite(size_f) or size_f < 0:
            continue
        if side == "buy":
            delta += float(size_f)
        elif side == "sell":
            delta -= float(size_f)
        else:
            continue
    if not math.isfinite(delta):
        try:
            log_error_with_context(
                "calculate_cumulative_delta: non-finite result",
                operation="calculate_cumulative_delta",
                module="src.data.normalization",
                extra={"delta": delta},
            )
        except Exception:
            pass
        return 0.0
    return float(delta)


def compute_vwap(trades: List[Trade]) -> float:
    """Compute volume-weighted average price with numerical guards."""
    if not trades:
        return 0.0
    total_volume = 0.0
    weighted_sum = 0.0
    for trade in trades:
        try:
            price = getattr(trade, "price", 0.0)
            size = getattr(trade, "size", 0.0)
            price_f = validate_finite(price, "trade.price", context={"function": "compute_vwap"})
            size_f = validate_finite(size, "trade.size", context={"function": "compute_vwap"})
        except (NonFiniteResultError, Exception) as e:
            try:
                log_error_with_context(
                    "compute_vwap: skipping invalid trade",
                    operation="compute_vwap",
                    module="src.data.normalization",
                    extra={"price": getattr(trade, "price", None), "size": getattr(trade, "size", None)},
                    exc=e,
                )
            except Exception:
                pass
            continue
        if not math.isfinite(price_f) or not math.isfinite(size_f):
            continue
        if size_f <= 0 or price_f < 0:
            continue
        weighted_sum += float(price_f) * float(size_f)
        total_volume += float(size_f)
    if total_volume == 0 or not math.isfinite(total_volume):
        return 0.0
    vwap = safe_divide(weighted_sum, total_volume, default=0.0, operation="compute_vwap")
    if not math.isfinite(vwap) or vwap < 0:
        try:
            log_error_with_context(
                "compute_vwap: non-finite result",
                operation="compute_vwap",
                module="src.data.normalization",
                extra={"weighted_sum": weighted_sum, "total_volume": total_volume},
            )
        except Exception:
            pass
        return 0.0
    return float(vwap)


def normalize_options_chain(chain: OptionsChain) -> OptionsChain:
    # Ensure timestamps normalized
    chain.timestamp = normalize_timestamp(chain.timestamp)
    for q in chain.quotes:
        q.timestamp = normalize_timestamp(q.timestamp)
    return chain


def normalize_orderflow(snapshot: OrderflowSnapshot) -> OrderflowSnapshot:
    snapshot.timestamp = normalize_timestamp(snapshot.timestamp)
    for t in snapshot.trades:
        t.timestamp = normalize_timestamp(t.timestamp)
    for l in getattr(snapshot, "liquidations", []):
        if hasattr(l, "timestamp"):
            l.timestamp = normalize_timestamp(l.timestamp)
    for f in getattr(snapshot, "funding_rates", []):
        if hasattr(f, "timestamp"):
            f.timestamp = normalize_timestamp(f.timestamp)
        if hasattr(f, "funding_time"):
            f.funding_time = normalize_timestamp(f.funding_time)
    return snapshot
