"""Data normalization utilities across venues."""

from datetime import datetime, timezone
from typing import List, Optional

import numpy as np

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
    """Calculate moneyness as strike/spot."""
    if spot <= 0:
        return 0.0
    return strike / spot


def calculate_cumulative_delta(trades: List[Trade]) -> float:
    """Calculate cumulative delta from trade flow."""
    delta = 0.0
    for trade in trades:
        side = str(trade.side).lower()
        if side == "buy":
            delta += trade.size
        elif side == "sell":
            delta -= trade.size
    return delta


def compute_vwap(trades: List[Trade]) -> float:
    """Compute volume-weighted average price."""
    if not trades:
        return 0.0
    total_volume = sum(float(t.size) for t in trades)
    if total_volume == 0:
        return 0.0
    vwap = sum(float(t.price) * float(t.size) for t in trades) / total_volume
    return vwap


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
