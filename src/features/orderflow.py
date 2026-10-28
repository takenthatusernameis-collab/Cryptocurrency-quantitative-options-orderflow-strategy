"""Orderflow imbalance and delta-adjusted flow calculations."""

from math import isfinite
from typing import List, Optional

import numpy as np

from ..data.schemas import OrderflowSnapshot, Trade


def calculate_cumulative_delta(trades: List[Trade]) -> float:
    """Calculate cumulative delta (buy volume - sell volume)."""
    delta = 0.0
    for trade in trades:
        try:
            vol = float(trade.size)
        except Exception:
            continue
        if not isfinite(vol):
            continue
        try:
            side = str(trade.side).lower()
        except Exception:
            continue
        if side == "buy":
            delta += vol
        elif side == "sell":
            delta -= vol
    if not isfinite(delta):
        return 0.0
    return float(delta)


def calculate_cumulative_delta_robust(trades: List[Trade], window: Optional[int] = None) -> float:
    """Robust cumulative delta with trade classification; optional windowing."""
    if not trades:
        return 0.0
    trades_list = trades[-window:] if window is not None and window > 0 else trades
    delta = 0.0
    for trade in trades_list:
        try:
            vol = float(trade.size)
        except Exception:
            continue
        if not isfinite(vol):
            continue
        try:
            side = str(trade.side).lower()
        except Exception:
            continue
        if side == "buy":
            delta += vol
        elif side == "sell":
            delta -= vol
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

    try:
        w = int(window)
    except Exception:
        w = 100
    if w <= 0:
        recent_trades = trades
    else:
        recent_trades = trades[-w:] if len(trades) > w else trades
    buy_volume = 0.0
    sell_volume = 0.0
    for t in recent_trades:
        try:
            vol = float(t.size)
        except Exception:
            continue
        if not isfinite(vol):
            continue
        try:
            side = str(t.side).lower()
        except Exception:
            continue
        if side == "buy":
            buy_volume += vol
        elif side == "sell":
            sell_volume += vol
    total = buy_volume + sell_volume
    if total == 0 or not isfinite(total):
        return 0.0

    result = (buy_volume - sell_volume) / total
    if not isfinite(result):
        return 0.0
    # clamp to [-1,1] for numerical safety
    if result < -1.0:
        result = -1.0
    if result > 1.0:
        result = 1.0
    return float(result)


def orderflow_imbalance_multi_horizon(
    trades: List[Trade], horizons: List[int] = None, decay: float = 0.3
) -> dict:
    """Orderflow imbalance at multiple horizons with decay weighting."""
    if trades is None:
        trades = []
    if horizons is None:
        horizons = [1, 10, 50, 100]
    # Normalize horizons - ensure list of positive ints
    try:
        norm_horizons = []
        for h in horizons:
            try:
                hh = int(h)
            except Exception:
                continue
            if hh > 0:
                norm_horizons.append(hh)
        horizons = norm_horizons
    except Exception:
        horizons = [1, 10, 50, 100]

    result = {}
    for h in horizons:
        try:
            imb = calculate_orderflow_imbalance(trades, window=h)
        except Exception:
            imb = 0.0
        if not isfinite(imb):
            imb = 0.0
        # clamp for safety
        if imb < -1.0:
            imb = -1.0
        if imb > 1.0:
            imb = 1.0
        result[f"imb_{h}"] = float(imb)
        # aliases for flexibility
        result[f"orderflow_imbalance_{h}"] = float(imb)

    # Decay-weighted aggregate
    if result and horizons:
        agg = 0.0
        total_w = 0.0
        try:
            d = float(decay)
        except Exception:
            d = 0.3
        if d < 0.0:
            d = 0.0
        if not isfinite(d):
            d = 0.3
        for i, h in enumerate(horizons):
            w = float(np.exp(-i * d))  # decay
            if not isfinite(w) or w < 0:
                w = 0.0
            agg += result.get(f"imb_{h}", 0.0) * w
            total_w += w
        if total_w > 0 and isfinite(agg):
            out = agg / total_w
            if not isfinite(out):
                out = 0.0
            if out < -1.0:
                out = -1.0
            if out > 1.0:
                out = 1.0
            result["imb_decay_weighted"] = float(out)
            result["orderflow_imbalance_decay_weighted"] = float(out)
            result["imbalance_decay_weighted"] = float(out)
        else:
            result["imb_decay_weighted"] = 0.0
            result["orderflow_imbalance_decay_weighted"] = 0.0
            result["imbalance_decay_weighted"] = 0.0
    else:
        result["imb_decay_weighted"] = 0.0
        result["orderflow_imbalance_decay_weighted"] = 0.0
        result["imbalance_decay_weighted"] = 0.0

    # Cross-consistency helper: also provide mean/simple aggregate
    try:
        vals = []
        for h in horizons:
            v = result.get(f"imb_{h}")
            if v is not None and isfinite(v):
                vals.append(float(v))
        if vals:
            m = sum(vals) / len(vals)
            if not isfinite(m):
                m = 0.0
            if m < -1.0:
                m = -1.0
            if m > 1.0:
                m = 1.0
            result["imb_mean"] = float(m)
            result["orderflow_imbalance_mean"] = float(m)
        else:
            result["imb_mean"] = 0.0
            result["orderflow_imbalance_mean"] = 0.0
    except Exception:
        result["imb_mean"] = 0.0
        result["orderflow_imbalance_mean"] = 0.0

    return result


imbalance_multi_horizon = orderflow_imbalance_multi_horizon
orderflow_imbalance_multihorizon = orderflow_imbalance_multi_horizon
multi_horizon_orderflow_imbalance = orderflow_imbalance_multi_horizon


def calculate_signed_volume(trades: List[Trade], window: Optional[int] = None) -> float:
    """Signed volume with trade classification robustness."""
    if not trades:
        return 0.0
    trades_list = trades[-window:] if window is not None and window > 0 else trades
    signed_vol = 0.0
    for trade in trades_list:
        try:
            vol = float(trade.size)
        except Exception:
            continue
        if not isfinite(vol):
            continue
        try:
            side = str(trade.side).lower()
        except Exception:
            continue
        if side == "buy":
            signed_vol += vol
        elif side == "sell":
            signed_vol -= vol
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


def detect_aggressive_flow(trades: List[Trade], window: int = 50) -> float:
    """Detect aggressive orderflow: fraction of trades that are large and in the same direction."""
    if not trades or len(trades) < 2:
        return 0.0
    trades_list = trades[-window:] if window is not None and window > 0 else trades
    sizes = [t.size for t in trades_list]
    avg_size = sum(sizes) / len(sizes)
    if avg_size == 0 or not isfinite(avg_size):
        return 0.0
    buy_aggressive = sum(1 for t in trades_list if t.side.lower() == "buy" and t.size > 2.0 * avg_size)
    sell_aggressive = sum(1 for t in trades_list if t.side.lower() == "sell" and t.size > 2.0 * avg_size)
    total = len(trades_list)
    aggressive_ratio = (buy_aggressive - sell_aggressive) / total if total > 0 else 0.0
    if not isfinite(aggressive_ratio):
        return 0.0
    if aggressive_ratio < -1.0:
        aggressive_ratio = -1.0
    if aggressive_ratio > 1.0:
        aggressive_ratio = 1.0
    return float(aggressive_ratio)


vpin_toxicity = vpin_style_toxicity
trade_intensity = detect_aggressive_flow
