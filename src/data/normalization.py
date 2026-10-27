"""Data normalization utilities across venues."""

from datetime import datetime
from typing import List

import numpy as np

from .schemas import OptionsChain, OrderflowSnapshot, Trade


def normalize_symbol(symbol: str, venue: str) -> str:
    """Normalize symbol format across venues."""
    # Basic normalization - can be extended per venue
    s = symbol.upper().replace("-", "").replace("_", "")
    return s


def calculate_moneyness(spot: float, strike: float) -> float:
    """Calculate moneyness as strike/spot."""
    if spot <= 0:
        return 0.0
    return strike / spot


def calculate_cumulative_delta(trades: List[Trade]) -> float:
    """Calculate cumulative delta from trade flow."""
    delta = 0.0
    for trade in trades:
        if trade.side.lower() == "buy":
            delta += trade.size
        elif trade.side.lower() == "sell":
            delta -= trade.size
    return delta


def compute_vwap(trades: List[Trade]) -> float:
    """Compute volume-weighted average price."""
    if not trades:
        return 0.0
    total_volume = sum(t.size for t in trades)
    if total_volume == 0:
        return 0.0
    vwap = sum(t.price * t.size for t in trades) / total_volume
    return vwap
