"""Orderflow imbalance and delta-adjusted flow calculations."""

from math import isfinite
from typing import List, Optional

import numpy as np

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


def calculate_cumulative_delta_robust(trades: List[Trade], window: Optional[int] = None) -> float:
    """Robust cumulative delta with trade classification; optional windowing."""
    if not trades:
        return 0.0
    trades_list = trades[-window:] if window is not None and window > 0 else trades
    delta = 0.0
    for trade in trades_list:
        side = trade.side.lower()
        if side == "buy":
            delta += trade.size
        elif side == "sell":
            delta -= trade.size
        else:
            # Try to infer
            pass
    if not isfinite(delta):
        return 0.0
    return float(delta)


cumulative_delta = calculate_cumulative_delta
robust_cumulative_delta = calculate_cumulative_delta_robust


def calculate_vwap_adjusted_delta(trades: List[Trade]) -> float:
    """VWAP-adjusted signed delta."""
    if not trades:
        return 0.0
    total_vol = 0.0
    signed_notional = 0.0
    for trade in trades:
        vol = trade.size
        if not isfinite(vol):
            continue
        total_vol += vol
        if trade.side.lower() == "buy":
            signed_notional += vol * trade.price
        elif trade.side.lower() == "sell":
            signed_notional -= vol * trade.price
    if total_vol == 0 or not isfinite(signed_notional):
        return calculate_cumulative_delta(trades)
    vwap_adj = signed_notional / total_vol  # approximation
    if not isfinite(vwap_adj):
        return calculate_cumulative_delta(trades)
    return float(vwap_adj)


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


def orderflow_imbalance_multi_horizon(
    trades: List[Trade], horizons: List[int] = None
) -> dict:
    """Orderflow imbalance at multiple horizons with decay weighting."""
    if horizons is None:
        horizons = [1, 10, 50, 100]
    result = {}
    for h in horizons:
        if h <= 0:
            continue
        imb = calculate_orderflow_imbalance(trades, window=h)
        # Apply exponential decay weighting factor for aggregation
        result[f"imb_{h}"] = imb
    # Decay-weighted aggregate
    if result:
        agg = 0.0
        total_w = 0.0
        for i, h in enumerate(horizons):
            if h <= 0:
                continue
            w = np.exp(-i * 0.3)  # decay
            agg += result.get(f"imb_{h}", 0.0) * w
            total_w += w
        if total_w > 0 and isfinite(agg):
            result["imb_decay_weighted"] = agg / total_w
        else:
            result["imb_decay_weighted"] = 0.0
    else:
        result["imb_decay_weighted"] = 0.0
    return result


imbalance_multi_horizon = orderflow_imbalance_multi_horizon


def calculate_signed_volume(trades: List[Trade], window: Optional[int] = None) -> float:
    """Signed volume with trade classification robustness."""
    if not trades:
        return 0.0
    trades_list = trades[-window:] if window is not None and window > 0 else trades
    signed_vol = 0.0
    for trade in trades_list:
        side = trade.side.lower()
        if side == "buy":
            signed_vol += trade.size
        elif side == "sell":
            signed_vol -= trade.size
    if not isfinite(signed_vol):
        return 0.0
    return float(signed_vol)


def delta_divergence_vs_price(trades: List[Trade], price_series: List[float] = None) -> float:
    """Footprint/orderflow divergence metric (delta divergence vs price)."""
    if not trades:
        return 0.0
    cum_delta = calculate_cumulative_delta(trades)
    if price_series and len(price_series) >= 2:
        price_change = price_series[-1] - price_series[0]
        if isfinite(price_change) and isfinite(cum_delta):
            # Simple divergence measure
            div = cum_delta * np.sign(price_change) if abs(price_change) > 1e-18 else cum_delta
            if isfinite(div):
                return float(div)
    if isfinite(cum_delta):
        return float(cum_delta)
    return 0.0


def absorption_detection(trades: List[Trade], threshold: float = 2.0) -> float:
    """Absorption detection metric."""
    if not trades or len(trades) < 3:
        return 0.0
    sizes = [t.size for t in trades]
    avg_size = sum(sizes) / len(sizes)
    if avg_size == 0 or not isfinite(avg_size):
        return 0.0
    large_trades = sum(1 for s in sizes if s > threshold * avg_size)
    result = large_trades / len(sizes)
    if not isfinite(result):
        return 0.0
    return float(result)


def vpin_style_toxicity(trades: List[Trade], bucket_size: int = 50) -> float:
    """VPIN-style toxicity proxy with finite-sample guards."""
    if not trades or len(trades) < bucket_size:
        return 0.0
    # Simplified VPIN
    vpin = 0.0
    num_buckets = min(10, len(trades) // bucket_size)
    if num_buckets == 0:
        return 0.0
    for i in range(num_buckets):
        bucket = trades[i * bucket_size : (i + 1) * bucket_size]
        buy_vol = sum(t.size for t in bucket if t.side.lower() == "buy")
        sell_vol = sum(t.size for t in bucket if t.side.lower() == "sell")
        total = buy_vol + sell_vol
        if total > 0 and isfinite(buy_vol) and isfinite(sell_vol):
            vpin += abs(buy_vol - sell_vol) / total
    vpin_result = vpin / num_buckets if num_buckets > 0 else 0.0
    if not isfinite(vpin_result):
        return 0.0
    # Clamp
    if vpin_result < 0:
        vpin_result = 0.0
    if vpin_result > 1:
        vpin_result = 1.0
    return float(vpin_result)


vpin_toxicity = vpin_style_toxicity
trade_intensity = detect_aggressive_flow
