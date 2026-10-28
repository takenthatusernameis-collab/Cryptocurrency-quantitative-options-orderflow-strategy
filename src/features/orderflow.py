"""Orderflow imbalance and delta-adjusted flow calculations."""

from math import isfinite
from typing import List

from ..data.schemas import OrderflowSnapshot, Trade


def calculate_cumulative_delta(trades: List[Trade]) -> float:
    """Calculate cumulative delta (buy volume - sell volume)."""
    delta = 0.0
    for trade in trades:
        if trade.side.lower() == "buy":
            delta += trade.size
        elif trade.side.lower() == "sell":
            delta -= trade.size
    if not isfinite(delta):
        return 0.0
    return delta


def calculate_delta_adjusted_flow(trades: List[Trade], spot_price: float = None) -> float:
    """Calculate delta-adjusted orderflow."""
    cum_delta = calculate_cumulative_delta(trades)
    if spot_price and spot_price > 0:
        result = cum_delta / spot_price
        if isfinite(result):
            return result
        return cum_delta
    return cum_delta


def calculate_orderflow_imbalance(trades: List[Trade], window: int = 100) -> float:
    """Calculate orderflow imbalance ratio."""
    if not trades:
        return 0.0

    recent_trades = trades[-window:] if len(trades) > window else trades
    buy_volume = sum(t.size for t in recent_trades if t.side.lower() == "buy")
    sell_volume = sum(t.size for t in recent_trades if t.side.lower() == "sell")

    total = buy_volume + sell_volume
    if total == 0:
        return 0.0

    result = (buy_volume - sell_volume) / total
    if not isfinite(result):
        return 0.0
    return result


def detect_aggressive_flow(trades: List[Trade], threshold: float = 1.5) -> float:
    """Detect aggressive flow using size relative to average."""
    if not trades or len(trades) < 2:
        return 0.0

    sizes = [t.size for t in trades]
    avg_size = sum(sizes) / len(sizes)
    if avg_size == 0:
        return 0.0

    aggressive_count = sum(1 for s in sizes if s > threshold * avg_size)
    result = aggressive_count / len(sizes)
    if not isfinite(result):
        return 0.0
    return result
