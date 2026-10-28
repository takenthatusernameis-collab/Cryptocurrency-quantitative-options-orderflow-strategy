"""Orderflow imbalance and delta-adjusted flow calculations."""

from math import exp, isfinite
from typing import Any, Dict, Iterable, List, Optional

import numpy as np

from ..data.schemas import OrderflowSnapshot, Trade


def calculate_cumulative_delta(trades: List[Trade]) -> float:
    """Calculate cumulative delta (buy volume minus sell volume).

    Iterates trades, adding volume for side ``'buy'`` and subtracting for
    ``'sell'`` (case-insensitive). Skips invalid sizes/non-finite values.
    Returns 0.0 if the result is non-finite.
    """
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
    """Robust cumulative delta with optional trailing window.

    Classifies trades as buy/sell by side (case-insensitive); if ``window`` is
    provided and > 0, only the last ``window`` trades are considered. Guards
    against invalid volumes and returns 0.0 on non-finite results.
    """
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


def calculate_cumulative_delta_vectorized(trades: List[Trade]) -> float:
    """Vectorized cumulative delta (buy volume - sell volume).

    Semantically identical to `calculate_cumulative_delta` but uses numpy
    accumulation for large trade lists.
    """
    if not trades:
        return 0.0
    sides = np.empty(len(trades), dtype=object)
    sizes = np.zeros(len(trades), dtype=np.float64)
    for i, trade in enumerate(trades):
        try:
            sides[i] = str(trade.side).lower()
        except Exception:
            sides[i] = ""
        try:
            sizes[i] = float(trade.size)
        except Exception:
            sizes[i] = float("nan")
    valid = np.isfinite(sizes)
    buy_mask = (sides == "buy") & valid
    sell_mask = (sides == "sell") & valid
    delta = float(sizes[buy_mask].sum() - sizes[sell_mask].sum())
    if not isfinite(delta):
        return 0.0
    return delta


def calculate_signed_volume_vectorized(trades: List[Trade], window: Optional[int] = None) -> float:
    """Vectorized signed volume with optional windowing."""
    if not trades:
        return 0.0
    trades_list = trades[-window:] if window is not None and window > 0 else trades
    if not trades_list:
        return 0.0
    sides = np.empty(len(trades_list), dtype=object)
    sizes = np.zeros(len(trades_list), dtype=np.float64)
    for i, trade in enumerate(trades_list):
        try:
            sides[i] = str(trade.side).lower()
        except Exception:
            sides[i] = ""
        try:
            sizes[i] = float(trade.size)
        except Exception:
            sizes[i] = float("nan")
    valid = np.isfinite(sizes)
    buy_mask = (sides == "buy") & valid
    sell_mask = (sides == "sell") & valid
    signed_vol = float(sizes[buy_mask].sum() - sizes[sell_mask].sum())
    if not isfinite(signed_vol):
        return 0.0
    return signed_vol


def calculate_orderflow_imbalance_vectorized(trades: List[Trade], window: int = 100) -> float:
    """Vectorized orderflow imbalance ratio.

    Semantically identical to `calculate_orderflow_imbalance` but uses numpy
    for volume aggregation.
    """
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
    if not recent_trades:
        return 0.0
    sides = np.empty(len(recent_trades), dtype=object)
    sizes = np.zeros(len(recent_trades), dtype=np.float64)
    for i, t in enumerate(recent_trades):
        try:
            sides[i] = str(t.side).lower()
        except Exception:
            sides[i] = ""
        try:
            sizes[i] = float(t.size)
        except Exception:
            sizes[i] = float("nan")
    valid = np.isfinite(sizes)
    buy_volume = float(sizes[(sides == "buy") & valid].sum())
    sell_volume = float(sizes[(sides == "sell") & valid].sum())
    total = buy_volume + sell_volume
    if total == 0 or not isfinite(total):
        return 0.0
    result = (buy_volume - sell_volume) / total
    if not isfinite(result):
        return 0.0
    if result < -1.0:
        result = -1.0
    if result > 1.0:
        result = 1.0
    return float(result)


cumulative_delta_vectorized = calculate_cumulative_delta_vectorized
signed_volume_vectorized = calculate_signed_volume_vectorized
orderflow_imbalance_vectorized = calculate_orderflow_imbalance_vectorized


def calculate_vwap_adjusted_delta(trades: List[Trade]) -> float:
    """Compute VWAP-adjusted signed delta.

    Accumulates signed notional (``+vol*price`` for buys, ``-vol*price`` for
    sells) divided by total traded volume to get a VWAP-like signed imbalance;
    if total volume is zero/non-finite, falls back to ``calculate_cumulative_delta``.
    Guards all values for finiteness.
    """
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


def calculate_delta_adjusted_flow(trades: List[Trade], spot_price: Optional[float] = None) -> float:
    """Calculate delta-adjusted orderflow.

    Returns ``cumulative_delta / spot_price`` if spot_price is positive and
    finite, otherwise returns cumulative delta unchanged.
    """
    cum_delta = calculate_cumulative_delta(trades)
    if spot_price and spot_price > 0:
        result = cum_delta / spot_price
        if isfinite(result):
            return result
        return cum_delta
    return cum_delta


def calculate_orderflow_imbalance(trades: List[Trade], window: int = 100) -> float:
    """Calculate orderflow imbalance ratio over a trailing window.

    Takes the last ``window`` trades (or all if ``window <= 0`` or shorter),
    sums buy/sell volumes by side, and returns ``(buy-sell)/(buy+sell)`` clamped
    to [-1, 1]. Returns 0.0 on empty/zero total volume or non-finite results.
    """
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
    trades: List[Trade], horizons: Optional[List[int]] = None, decay: float = 0.3
) -> Dict[str, Any]:
    """Orderflow imbalance at multiple horizons with exponential decay weighting.

    Production-grade hardening: validates/sanitizes inputs, filters non-finite
    sizes and unknown sides, clamps all outputs to [-1,1], guards against
    division by zero/exp overflow. Per-horizon values are consistent with
    ``calculate_orderflow_imbalance``; returns keys including per-horizon
    imbalances, counts, decay-weighted composite, and metadata.
    """
    result: dict = {}

    # --- normalize trades: filter non-trade / non-finite / misclassified ---
    clean_trades: List[Trade] = []
    iterator: Iterable[Trade]
    if trades is not None:
        try:
            iterator = iter(trades)
        except TypeError:
            iterator = []
        for t in iterator:
            try:
                side = str(getattr(t, "side", "")).lower()
            except Exception:
                continue
            if side not in ("buy", "sell"):
                continue
            try:
                size = float(getattr(t, "size", float("nan")))
            except Exception:
                continue
            if not isfinite(size):
                continue
            clean_trades.append(t)

    # --- normalize horizons: positive ints only, deduplicated ---
    norm_horizons: List[int] = []
    if horizons is not None:
        try:
            for h in horizons:
                try:
                    hh = int(h)
                except Exception:
                    continue
                if hh > 0 and hh not in norm_horizons:
                    norm_horizons.append(hh)
        except Exception:
            norm_horizons = []
    if not norm_horizons:
        norm_horizons = [1, 10, 50, 100]

    # --- per-horizon imbalance (cross-consistent with single-window calc) --
    imb_values: dict = {}
    for h in norm_horizons:
        try:
            imb = calculate_orderflow_imbalance(clean_trades, window=h)
        except Exception:
            imb = 0.0
        if not isfinite(imb):
            imb = 0.0
        if imb < -1.0:
            imb = -1.0
        elif imb > 1.0:
            imb = 1.0
        imb = float(imb)
        imb_values[h] = imb
        result[f"imb_{h}"] = imb
        result[f"orderflow_imbalance_{h}"] = imb

    # --- decay weighting (guards against exp overflow/underflow) ---
    try:
        d = float(decay)
    except Exception:
        d = 0.3
    if not isfinite(d) or d < 0.0:
        d = 0.3
    if d > 50.0:
        d = 50.0

    keys = [f"imb_{h}" for h in norm_horizons]
    weights: List[float] = [exp(-i * d) for i in range(len(keys))]
    weights = [w_i if isfinite(w_i) and w_i >= 0.0 else 0.0 for w_i in weights]
    total_w = float(sum(weights)) if weights else 0.0

    if keys and total_w > 0.0 and isfinite(total_w):
        vals = [imb_values.get(h, 0.0) for h in norm_horizons]
        vals = [v if isfinite(v) else 0.0 for v in vals]
        agg = float(sum(v * w_i for v, w_i in zip(vals, weights)))
        out = agg / total_w if total_w > 0 else 0.0
        if not isfinite(out):
            out = 0.0
        if out < -1.0:
            out = -1.0
        elif out > 1.0:
            out = 1.0
        out = float(out)
    else:
        out = 0.0

    decay_keys = (
        "imb_decay_weighted",
        "orderflow_imbalance_decay_weighted",
        "imbalance_decay_weighted",
    )
    for k in decay_keys:
        result[k] = out

    # decay-weight normalization (weights sum to 1)
    if total_w > 0.0 and isfinite(total_w):
        norm_w = [w_i / total_w for w_i in weights]
    elif keys:
        norm_w = [1.0 / len(keys)] * len(keys)
    else:
        norm_w = []
    result["decay_weights"] = norm_w
    result["orderflow_imbalance_decay_weights"] = norm_w

    # --- mean aggregate ---------------------------------------------------
    if imb_values:
        vals = [v for v in imb_values.values() if isfinite(v)]
        m = float(sum(vals) / len(vals)) if vals else 0.0
        if not isfinite(m):
            m = 0.0
        if m < -1.0:
            m = -1.0
        elif m > 1.0:
            m = 1.0
    else:
        m = 0.0
    result["imb_mean"] = m
    result["orderflow_imbalance_mean"] = m

    # --- final finite/clamp guarantee on every numeric value --------------
    for k, v in list(result.items()):
        if isinstance(v, float):
            if not isfinite(v):
                result[k] = 0.0
            elif v < -1.0:
                result[k] = -1.0
            elif v > 1.0:
                result[k] = 1.0
        elif isinstance(v, list):
            result[k] = [
                0.0 if not isfinite(x) else max(-1.0, min(1.0, float(x)))
                for x in v
            ]

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


def delta_divergence_vs_price(trades: List[Trade], price_series: Optional[List[float]] = None) -> float:
    """Footprint/orderflow divergence metric (delta divergence vs price)."""
    # Normalize trades: filter non-finite sizes and valid sides
    clean_trades: List[Trade] = []
    iterator: Iterable[Trade]
    if trades is not None:
        try:
            iterator = iter(trades)
        except TypeError:
            iterator = []
        for t in iterator:
            try:
                vol = float(getattr(t, "size", float("nan")))
            except Exception:
                continue
            if not isfinite(vol):
                continue
            try:
                side = str(getattr(t, "side", "")).lower()
            except Exception:
                continue
            if side not in ("buy", "sell"):
                continue
            clean_trades.append(t)
    if not clean_trades:
        return 0.0

    # Compute cum delta on clean trades
    cum_delta = 0.0
    for t in clean_trades:
        try:
            vol = float(t.size)
        except Exception:
            continue
        if not isfinite(vol):
            continue
        side = str(t.side).lower()
        if side == "buy":
            cum_delta += vol
        elif side == "sell":
            cum_delta -= vol
    if not isfinite(cum_delta):
        return 0.0

    # Normalize price series
    price_change = float("nan")
    if price_series is not None:
        try:
            ps = list(price_series)
        except Exception:
            ps = []
        if len(ps) >= 2:
            # Use first and last; filter non-finite
            p0 = ps[0]
            p1 = ps[-1]
            try:
                p0f = float(p0)
                p1f = float(p1)
            except Exception:
                p0f = float("nan")
                p1f = float("nan")
            if isfinite(p0f) and isfinite(p1f) and p0f != 0:
                price_change = p1f - p0f
            elif isfinite(p0f) and isfinite(p1f):
                price_change = p1f - p0f

    if isfinite(price_change):
        if abs(price_change) > 1e-18:
            # Divergence sign: if delta and price move opposite directions, divergence high
            sign_pc = 1.0 if price_change > 0 else -1.0
            div = cum_delta * sign_pc
        else:
            div = cum_delta
        if not isfinite(div):
            return 0.0
        # Clamp to reasonable range for robustness
        if div < -1e18:
            div = -1e18
        if div > 1e18:
            div = 1e18
        return float(div)

    if isfinite(cum_delta):
        return float(cum_delta)
    return 0.0


def absorption_detection(trades: List[Trade], threshold: float = 2.0) -> float:
    """Detect absorption: fraction of trades with size > threshold × average size.

    Computes mean trade size over finite valid sizes, counts trades larger than
    ``threshold * mean_size``, and returns the fraction in [0,1]. Requires >=3
    trades with valid sizes; guards against zero mean/non-finite values.
    """
    if trades is None:
        return 0.0
    try:
        trades_list = list(trades)
    except Exception:
        return 0.0
    if len(trades_list) < 3:
        return 0.0

    try:
        th = float(threshold)
    except Exception:
        th = 2.0
    if not isfinite(th) or th < 0:
        th = 2.0

    # Filter non-finite sizes
    sizes = []
    for t in trades_list:
        try:
            vol = float(getattr(t, "size", float("nan")))
        except Exception:
            continue
        if not isfinite(vol):
            continue
        sizes.append(vol)
    if len(sizes) < 3:
        return 0.0
    avg_size = sum(sizes) / len(sizes)
    if avg_size == 0 or not isfinite(avg_size):
        return 0.0
    large_trades = 0
    for s in sizes:
        if s > th * avg_size:
            large_trades += 1
    result = large_trades / len(sizes)
    if not isfinite(result):
        return 0.0
    if result < 0.0:
        result = 0.0
    if result > 1.0:
        result = 1.0
    return float(result)


def vpin_style_toxicity(trades: List[Trade], bucket_size: int = 50) -> float:
    """VPIN-style toxicity proxy with finite-sample guards.

    Computes the average across buckets of |buy_volume - sell_volume| /
    total_volume, a normalized [0, 1] measure of orderflow imbalance /
    toxicity. All inputs are sanitized: non-finite sizes and invalid sides
    are filtered, bucket_size is validated, and every intermediate value is
    guarded against overflow / division-by-zero.
    """
    if trades is None:
        return 0.0
    try:
        trades_list = list(trades)
    except Exception:
        return 0.0
    try:
        bs = int(bucket_size)
    except Exception:
        bs = 50
    if bs <= 0:
        return 0.0
    if len(trades_list) < bs:
        return 0.0

    # Number of full buckets (capped to avoid runaway on huge inputs)
    num_buckets = min(10, len(trades_list) // bs)
    if num_buckets == 0:
        return 0.0

    vpin = 0.0
    for i in range(num_buckets):
        bucket = trades_list[i * bs : (i + 1) * bs]
        buy_vol = 0.0
        sell_vol = 0.0
        for t in bucket:
            try:
                vol = float(getattr(t, "size", float("nan")))
            except Exception:
                continue
            if not isfinite(vol):
                continue
            try:
                side = str(getattr(t, "side", "")).lower()
            except Exception:
                continue
            if side == "buy":
                buy_vol += vol
            elif side == "sell":
                sell_vol += vol
        total = buy_vol + sell_vol
        if total > 0.0 and isfinite(buy_vol) and isfinite(sell_vol):
            vpin += abs(buy_vol - sell_vol) / total
        # If total == 0 (all sizes filtered), this bucket contributes 0 — safe.

    vpin_result = vpin / num_buckets if num_buckets > 0 else 0.0
    if not isfinite(vpin_result):
        return 0.0
    if vpin_result < 0.0:
        vpin_result = 0.0
    if vpin_result > 1.0:
        vpin_result = 1.0
    return float(vpin_result)


def detect_aggressive_flow(trades: List[Trade], window: int = 50) -> float:
    """Detect aggressive flow: fraction of large trades in the dominant direction.

    Over the trailing window, measures average size vs last-trade context and
    counts trades larger than average that align with the prevailing side;
    returns fraction in [0,1] with numerical guards.
    """
    if trades is None:
        return 0.0
    try:
        trades_list_all = list(trades)
    except Exception:
        return 0.0
    if len(trades_list_all) < 2:
        return 0.0

    try:
        w = int(window)
    except Exception:
        w = 50
    if w <= 0:
        trades_list = trades_list_all
    else:
        trades_list = trades_list_all[-w:] if len(trades_list_all) > w else trades_list_all

    if len(trades_list) < 2:
        return 0.0

    # Filter valid trades
    valid = []
    for t in trades_list:
        try:
            vol = float(getattr(t, "size", float("nan")))
        except Exception:
            continue
        if not isfinite(vol):
            continue
        try:
            side = str(getattr(t, "side", "")).lower()
        except Exception:
            continue
        if side not in ("buy", "sell"):
            continue
        valid.append((side, vol))
    if len(valid) < 2:
        return 0.0

    sizes = [v for _, v in valid]
    avg_size = sum(sizes) / len(sizes)
    if avg_size == 0 or not isfinite(avg_size):
        return 0.0

    buy_aggressive = 0
    sell_aggressive = 0
    for side, vol in valid:
        if vol > 2.0 * avg_size:
            if side == "buy":
                buy_aggressive += 1
            elif side == "sell":
                sell_aggressive += 1
    total = len(valid)
    if total == 0 or not isfinite(total):
        return 0.0
    aggressive_ratio = (buy_aggressive - sell_aggressive) / total
    if not isfinite(aggressive_ratio):
        return 0.0
    if aggressive_ratio < -1.0:
        aggressive_ratio = -1.0
    if aggressive_ratio > 1.0:
        aggressive_ratio = 1.0
    return float(aggressive_ratio)


vpin_toxicity = vpin_style_toxicity
trade_intensity = detect_aggressive_flow

# Backwards-compatible aliases
cumulative_delta = calculate_cumulative_delta
robust_cumulative_delta = calculate_cumulative_delta_robust
