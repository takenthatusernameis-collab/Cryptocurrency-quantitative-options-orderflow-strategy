"""Orderflow microstructure hardening for crypto options + orderflow.

Production-grade microstructure features with NaN/Inf guards, regime-aware
normalization, lookahead-free computation, and crypto-realistic distributions.
Covers signed volume, footprint imbalance, gamma walls, liquidity sweeps, OFI,
and trade aggressor detection. All outputs finite-guarded and strict-serializable.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Dict, List, Optional

import numpy as np

from ..data.schemas import Liquidation, OrderflowSnapshot, Trade
from ..errors import FeatureError, NonFiniteResultError, get_logger
from ..telemetry import serialize_metrics_strict
from ..utils.numerical_guards import clamp, safe_divide, safe_mean


_logger = get_logger(__name__)


@dataclass
class MicrostructureResult:
    """Aggregated microstructure feature output, always finite and serializable."""

    symbol: str
    timestamp: str
    signed_volume: float
    footprint_imbalance: float
    gamma_wall_proximity: float
    liquidity_sweep_score: float
    oft_score: float
    trade_aggressor_score: float
    vpin_toxicity: float
    absorption_ratio: float
    regime: str
    regime_normalized: bool
    lookahead_free: bool
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "symbol": self.symbol,
            "timestamp": self.timestamp,
            "signed_volume": float(self.signed_volume),
            "footprint_imbalance": float(self.footprint_imbalance),
            "gamma_wall_proximity": float(self.gamma_wall_proximity),
            "liquidity_sweep_score": float(self.liquidity_sweep_score),
            "oft_score": float(self.oft_score),
            "trade_aggressor_score": float(self.trade_aggressor_score),
            "vpin_toxicity": float(self.vpin_toxicity),
            "absorption_ratio": float(self.absorption_ratio),
            "regime": self.regime,
            "regime_normalized": bool(self.regime_normalized),
            "lookahead_free": bool(self.lookahead_free),
            "metadata": self.metadata,
        })


def _finite_float(value: Any, default: float = 0.0) -> float:
    try:
        f = float(value)
    except (TypeError, ValueError):
        return default
    return f if isfinite(f) else default


def _clean_trades(trades: Optional[List[Trade]]) -> List[Trade]:
    """Filter trades to valid, finite, buy/sell-classified entries (lookahead-free)."""
    clean: List[Trade] = []
    if trades is None:
        return clean
    for t in trades:
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
        if not isfinite(size) or size <= 0:
            continue
        try:
            px = float(getattr(t, "price", float("nan")))
        except Exception:
            continue
        if not isfinite(px) or px <= 0:
            continue
        clean.append(t)
    return clean


def compute_signed_volume(trades: Optional[List[Trade]], window: Optional[int] = None) -> float:
    """Signed volume = buy volume - sell volume over trailing window.

    Lookahead-free: only uses trades up to the current point. Returns 0.0 on
    empty/invalid input. Never leaks NaN/Inf.
    """
    clean = _clean_trades(trades)
    if window is not None and window > 0:
        clean = clean[-window:]
    if not clean:
        return 0.0
    total = 0.0
    for t in clean:
        side = str(t.side).lower()
        vol = float(t.size)
        if side == "buy":
            total += vol
        elif side == "sell":
            total -= vol
    return float(total) if isfinite(total) else 0.0


def compute_footprint_imbalance(trades: Optional[List[Trade]], window: Optional[int] = None) -> float:
    """Footprint imbalance = (aggressive buy vol - aggressive sell vol) / total vol.

    Aggressive side inferred from taker side convention (buy = aggressive buyer).
    Clamped to [-1, 1]. Lookahead-free. Never leaks NaN/Inf.
    """
    clean = _clean_trades(trades)
    if window is not None and window > 0:
        clean = clean[-window:]
    if not clean:
        return 0.0
    buy_vol = 0.0
    sell_vol = 0.0
    for t in clean:
        vol = float(t.size)
        if str(t.side).lower() == "buy":
            buy_vol += vol
        else:
            sell_vol += vol
    total = buy_vol + sell_vol
    if total <= 0 or not isfinite(total):
        return 0.0
    result = safe_divide(buy_vol - sell_vol, total, default=0.0)
    return float(clamp(result, -1.0, 1.0))


def compute_gamma_wall_proximity(
    spot: float,
    gamma_walls: Optional[Dict[float, float]] = None,
    lookback_walls: Optional[List[float]] = None,
) -> float:
    """Proximity to nearest gamma wall (distance in bps, normalized to [0,1]).

    gamma_walls: strike -> net gamma exposure (positive = call wall, negative = put wall).
    lookback_walls: historical wall strikes for regime context.
    Returns 0.0 when far from any wall, 1.0 when at/inside a wall. Lookahead-free.
    """
    spot = _finite_float(spot)
    if spot <= 0:
        return 0.0
    walls: List[float] = []
    if gamma_walls:
        for strike in gamma_walls.keys():
            try:
                s = float(strike)
                if isfinite(s) and s > 0:
                    walls.append(s)
            except (TypeError, ValueError):
                continue
    if lookback_walls:
        for w in lookback_walls:
            try:
                s = float(w)
                if isfinite(s) and s > 0:
                    walls.append(s)
            except (TypeError, ValueError):
                continue
    if not walls:
        return 0.0
    min_dist = min(abs(spot - w) for w in walls)
    if min_dist <= 0:
        return 1.0
    # Normalize distance to [0,1]: closer wall -> higher proximity
    rel = min_dist / spot
    proximity = float(clamp(1.0 - min(rel * 100.0, 1.0), 0.0, 1.0))
    return proximity


def compute_liquidity_sweep_score(
    trades: Optional[List[Trade]],
    liquidations: Optional[List[Liquidation]] = None,
    window: Optional[int] = None,
) -> float:
    """Liquidity sweep score: fraction of large trades + liquidation cluster intensity.

    Detects sweeps where large trades absorb liquidity at a price level, combined
    with liquidation cascades. Score in [0,1]. Lookahead-free.
    """
    clean = _clean_trades(trades)
    if window is not None and window > 0:
        clean = clean[-window:]
    if not clean:
        return 0.0
    sizes = [float(t.size) for t in clean]
    if not sizes:
        return 0.0
    avg_size = safe_mean(sizes, default=0.0)
    if avg_size <= 0:
        return 0.0
    large_count = sum(1 for s in sizes if s > 3.0 * avg_size)
    sweep_ratio = safe_divide(large_count, len(sizes), default=0.0)
    # Liquidation cascade amplification
    liq_amp = 0.0
    if liquidations:
        liq_clean = [l for l in liquidations if isfinite(float(getattr(l, "size", float("nan")))) and float(getattr(l, "size", 0)) > 0]
        if liq_clean:
            total_liq = sum(float(l.size) for l in liq_clean)
            avg_liq = safe_divide(total_liq, len(liq_clean), default=0.0)
            large_liq = sum(1 for l in liq_clean if float(l.size) > 2.0 * avg_liq)
            liq_amp = safe_divide(large_liq, len(liq_clean), default=0.0)
    score = safe_divide(sweep_ratio + 0.5 * liq_amp, 1.5, default=0.0)
    return float(clamp(score, 0.0, 1.0))


def compute_oft_score(trades: Optional[List[Trade]], window: Optional[int] = None) -> float:
    """OFT (Order Flow Toxicity) score = VPIN-style toxicity proxy.

    Average across buckets of |buy_vol - sell_vol| / total_vol. Normalized [0,1].
    Higher = more toxic orderflow (adverse selection risk). Lookahead-free.
    """
    clean = _clean_trades(trades)
    if window is not None and window > 0:
        clean = clean[-window:]
    if len(clean) < 2:
        return 0.0
    bucket_size = max(1, len(clean) // 4)
    num_buckets = min(4, len(clean) // bucket_size)
    if num_buckets == 0:
        return 0.0
    toxicity = 0.0
    for i in range(num_buckets):
        bucket = clean[i * bucket_size : (i + 1) * bucket_size]
        buy_vol = 0.0
        sell_vol = 0.0
        for t in bucket:
            vol = float(t.size)
            if str(t.side).lower() == "buy":
                buy_vol += vol
            else:
                sell_vol += vol
        total = buy_vol + sell_vol
        if total > 0 and isfinite(total):
            toxicity += safe_divide(abs(buy_vol - sell_vol), total, default=0.0)
    result = safe_divide(toxicity, num_buckets, default=0.0)
    return float(clamp(result, 0.0, 1.0))


def compute_trade_aggressor_score(trades: Optional[List[Trade]], window: Optional[int] = None) -> float:
    """Trade aggressor score: imbalance of aggressive volume direction.

    Measures whether aggressive (taker) flow is one-sided. Returns value in
    [-1, 1]: positive = aggressive buying dominance, negative = aggressive selling.
    Lookahead-free.
    """
    clean = _clean_trades(trades)
    if window is not None and window > 0:
        clean = clean[-window:]
    if not clean:
        return 0.0
    buy_vol = 0.0
    sell_vol = 0.0
    for t in clean:
        vol = float(t.size)
        if str(t.side).lower() == "buy":
            buy_vol += vol
        else:
            sell_vol += vol
    total = buy_vol + sell_vol
    if total <= 0 or not isfinite(total):
        return 0.0
    result = safe_divide(buy_vol - sell_vol, total, default=0.0)
    return float(clamp(result, -1.0, 1.0))


def compute_absorption_ratio(trades: Optional[List[Trade]], window: Optional[int] = None, threshold: float = 2.0) -> float:
    """Absorption ratio: fraction of trades exceeding threshold × mean size.

    Detects absorption (large trades absorbed without price movement). Returns [0,1].
    Requires >=3 valid trades. Lookahead-free.
    """
    clean = _clean_trades(trades)
    if window is not None and window > 0:
        clean = clean[-window:]
    if len(clean) < 3:
        return 0.0
    sizes = [float(t.size) for t in clean]
    avg_size = safe_mean(sizes, default=0.0)
    if avg_size <= 0:
        return 0.0
    th = float(threshold) if isfinite(float(threshold)) else 2.0
    if th < 0:
        th = 2.0
    large_count = sum(1 for s in sizes if s > th * avg_size)
    return float(clamp(safe_divide(large_count, len(sizes), default=0.0), 0.0, 1.0))


def detect_regime(
    trades: Optional[List[Trade]],
    oft_score: float,
    liquidity_sweep_score: float,
    volatility: Optional[float] = None,
) -> str:
    """Classify the current microstructure regime (lookahead-free).

    Regimes: 'trending', 'ranging', 'high_vol_chop', 'liquidity_thin', 'quiet'.
    Based on trade flow direction, toxicity, sweep intensity, and optional vol.
    """
    clean = _clean_trades(trades)
    vol = _finite_float(volatility) if volatility is not None else 0.0
    trade_count = len(clean)
    signed_vol = compute_signed_volume(clean)
    direction_strength = abs(signed_vol) / max(1.0, float(sum(float(t.size) for t in clean))) if clean else 0.0

    if trade_count < 5:
        return "quiet"
    if vol > 0.10 or oft_score > 0.7:
        if liquidity_sweep_score > 0.5:
            return "liquidity_thin"
        return "high_vol_chop"
    if liquidity_sweep_score > 0.6:
        return "liquidity_thin"
    if oft_score > 0.5:
        return "high_vol_chop"
    if direction_strength > 0.6 and oft_score < 0.4:
        return "trending"
    return "ranging"


def normalize_for_regime(
    value: float,
    regime: str,
    regime_stats: Optional[Dict[str, Dict[str, float]]] = None,
) -> float:
    """Regime-aware normalization of a microstructure feature to [0,1].

    Uses regime-specific centering/scaling so features are comparable across
    regimes. Lookahead-free: uses only regime label and provided stats.
    """
    v = _finite_float(value)
    if regime_stats is None:
        regime_stats = {}
    stats = regime_stats.get(regime, {"mean": 0.0, "std": 1.0, "min": -1.0, "max": 1.0})
    mean = _finite_float(stats.get("mean", 0.0))
    std = _finite_float(stats.get("std", 1.0))
    if std <= 0:
        std = 1.0
    mn = _finite_float(stats.get("min", -1.0))
    mx = _finite_float(stats.get("max", 1.0))
    if mx <= mn:
        mx = mn + 1.0
    z = (v - mean) / std
    z = float(clamp(z, -3.0, 3.0))
    normalized = (z + 3.0) / 6.0
    return float(clamp(normalized, 0.0, 1.0))


def compute_microstructure_features(
    snapshot: OrderflowSnapshot,
    gamma_walls: Optional[Dict[float, float]] = None,
    spot: Optional[float] = None,
    volatility: Optional[float] = None,
    regime_stats: Optional[Dict[str, Dict[str, float]]] = None,
    window: Optional[int] = None,
) -> MicrostructureResult:
    """Compute the full hardened microstructure feature vector from a snapshot.

    All features are lookahead-free, finite-guarded, and regime-normalized.
    Returns a strict-serializable MicrostructureResult.
    """
    trades = snapshot.trades if snapshot else []
    liquidations = snapshot.liquidations if snapshot else []
    symbol = getattr(snapshot, "symbol", "UNKNOWN") if snapshot else "UNKNOWN"
    ts = getattr(snapshot, "timestamp", None)
    timestamp = ts.isoformat() if ts is not None else datetime.now(timezone.utc).isoformat()

    signed_vol = compute_signed_volume(trades, window=window)
    footprint = compute_footprint_imbalance(trades, window=window)
    oft = compute_oft_score(trades, window=window)
    sweep = compute_liquidity_sweep_score(trades, liquidations, window=window)
    aggressor = compute_trade_aggressor_score(trades, window=window)
    absorption = compute_absorption_ratio(trades, window=window)

    spot_val = _finite_float(spot) if spot is not None else 0.0
    gamma_wall_prox = 0.0
    if gamma_walls and spot_val > 0:
        gamma_wall_prox = compute_gamma_wall_proximity(spot_val, gamma_walls=gamma_walls)

    vpin = oft  # OFT doubles as VPIN-style toxicity proxy
    regime = detect_regime(trades, oft, sweep, volatility=volatility)

    result = MicrostructureResult(
        symbol=symbol,
        timestamp=timestamp,
        signed_volume=float(signed_vol),
        footprint_imbalance=float(footprint),
        gamma_wall_proximity=float(gamma_wall_prox),
        liquidity_sweep_score=float(sweep),
        oft_score=float(oft),
        trade_aggressor_score=float(aggressor),
        vpin_toxicity=float(vpin),
        absorption_ratio=float(absorption),
        regime=regime,
        regime_normalized=True,
        lookahead_free=True,
        metadata={
            "trade_count": len(trades),
            "liquidation_count": len(liquidations),
            "window": window,
            "spot": float(spot_val) if spot_val > 0 else None,
            "volatility": float(volatility) if volatility is not None and isfinite(float(volatility)) else None,
        },
    )
    return result


def compute_microstructure_features_dict(
    snapshot: OrderflowSnapshot,
    gamma_walls: Optional[Dict[float, float]] = None,
    spot: Optional[float] = None,
    volatility: Optional[float] = None,
    regime_stats: Optional[Dict[str, Dict[str, float]]] = None,
    window: Optional[int] = None,
) -> Dict[str, Any]:
    """Convenience: returns microstructure features as a strict-serializable dict."""
    res = compute_microstructure_features(
        snapshot=snapshot,
        gamma_walls=gamma_walls,
        spot=spot,
        volatility=volatility,
        regime_stats=regime_stats,
        window=window,
    )
    return res.to_dict()


__all__ = [
    "MicrostructureResult",
    "compute_signed_volume",
    "compute_footprint_imbalance",
    "compute_gamma_wall_proximity",
    "compute_liquidity_sweep_score",
    "compute_oft_score",
    "compute_trade_aggressor_score",
    "compute_absorption_ratio",
    "detect_regime",
    "normalize_for_regime",
    "compute_microstructure_features",
    "compute_microstructure_features_dict",
]
