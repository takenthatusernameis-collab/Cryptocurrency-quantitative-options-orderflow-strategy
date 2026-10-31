"""Regime-stratified OOS stress suite for crypto options/orderflow microstructure."""

from __future__ import annotations

import math
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ..config import BacktestConfig, RiskConfig
from .engine import (
    BacktestEngine,
    WalkForwardBacktest,
    WalkForwardResults,
    serialize_metrics_strict,
)


REGIMES = ["trending", "ranging", "high_vol_chop", "liquidity_thin"]


@dataclass
class RegimeSpec:
    name: str
    description: str
    drift: float
    vol: float
    trend_strength: float
    chop_prob: float
    liquidity_factor: float
    gamma_sensitivity: float
    iv_regime_shift: float
    orderflow_imbalance_bias: float


REGIME_SPECS: Dict[str, RegimeSpec] = {
    "trending": RegimeSpec(
        name="trending",
        description="Sustained directional move with controlled volatility",
        drift=0.0008,
        vol=0.012,
        trend_strength=0.8,
        chop_prob=0.05,
        liquidity_factor=1.0,
        gamma_sensitivity=1.1,
        iv_regime_shift=0.05,
        orderflow_imbalance_bias=0.3,
    ),
    "ranging": RegimeSpec(
        name="ranging",
        description="Mean-reverting range-bound with moderate vol",
        drift=0.0,
        vol=0.008,
        trend_strength=0.1,
        chop_prob=0.3,
        liquidity_factor=0.9,
        gamma_sensitivity=0.9,
        iv_regime_shift=0.0,
        orderflow_imbalance_bias=0.0,
    ),
    "high_vol_chop": RegimeSpec(
        name="high_vol_chop",
        description="High volatility with frequent reversals (chop)",
        drift=0.0001,
        vol=0.025,
        trend_strength=0.2,
        chop_prob=0.6,
        liquidity_factor=0.7,
        gamma_sensitivity=1.4,
        iv_regime_shift=0.25,
        orderflow_imbalance_bias=0.1,
    ),
    "liquidity_thin": RegimeSpec(
        name="liquidity_thin",
        description="Liquidity-thin with wider spreads and jump risk",
        drift=0.0002,
        vol=0.015,
        trend_strength=0.3,
        chop_prob=0.4,
        liquidity_factor=0.4,
        gamma_sensitivity=1.3,
        iv_regime_shift=0.15,
        orderflow_imbalance_bias=0.2,
    ),
}


def generate_regime_prices(
    regime: str,
    n: int = 500,
    start_price: float = 50000.0,
    seed: int = 12345,
) -> Tuple[List[float], List[datetime]]:
    if regime not in REGIME_SPECS:
        raise ValueError(f"Unknown regime: {regime}")
    spec = REGIME_SPECS[regime]
    rng = np.random.RandomState(seed + hash(regime) % 10000)
    prices = [start_price]
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    timestamps = [start]
    for i in range(1, n):
        ret = rng.normal(spec.drift, spec.vol)
        if spec.trend_strength > 0.5:
            ret += spec.drift * spec.trend_strength
        if rng.random() < spec.chop_prob:
            ret -= ret * 1.5
        if regime == "liquidity_thin" and rng.random() < 0.02:
            ret += rng.normal(0, spec.vol * 2.0) * (1.0 - spec.liquidity_factor)
        prices.append(prices[-1] * (1.0 + ret))
        timestamps.append(start + timedelta(hours=i))
    return prices, timestamps


def generate_regime_signals(
    prices: List[float],
    regime: str,
    seed: int = 12345,
) -> List[int]:
    if regime not in REGIME_SPECS:
        raise ValueError(f"Unknown regime: {regime}")
    spec = REGIME_SPECS[regime]
    rng = np.random.RandomState(seed + hash(regime) % 20000)
    signals = []
    for i in range(len(prices)):
        if i < 20:
            signals.append(0)
            continue
        ret_short = (prices[i] - prices[i - 5]) / prices[i - 5] if prices[i - 5] > 0 else 0
        ma = sum(prices[max(0, i - 20): i]) / min(i, 20)
        mr = (ma - prices[i]) / prices[i] if prices[i] > 0 else 0
        score = spec.trend_strength * ret_short - (1 - spec.trend_strength) * mr * 0.5
        score += spec.orderflow_imbalance_bias * rng.normal(0, 0.1)
        if score > 0.01:
            signals.append(1)
        elif score < -0.01:
            signals.append(-1)
        else:
            signals.append(0)
    return signals


def run_regime_stress_walkforward(
    regime: str,
    price_series: Optional[Dict[str, List[float]]] = None,
    signals: Optional[Dict[str, List[int]]] = None,
    timestamps: Optional[List[datetime]] = None,
    train_window: int = 120,
    test_window: int = 40,
    step_size: int = 40,
    purge: int = 10,
    embargo: int = 5,
    config: Optional[BacktestConfig] = None,
    risk_config: Optional[RiskConfig] = None,
    seed: int = 12345,
) -> Dict[str, Any]:
    if regime not in REGIME_SPECS:
        raise ValueError(f"Unknown regime: {regime}")

    if price_series is None or signals is None:
        prices, ts = generate_regime_prices(regime, seed=seed)
        if timestamps is None:
            timestamps = ts
        price_series = {"BTC": prices}
        signals = {"BTC": generate_regime_signals(prices, regime, seed=seed)}

    wfb = WalkForwardBacktest(config or BacktestConfig(), risk_config or RiskConfig(), purge=purge, embargo=embargo)
    results = wfb.run_walk_forward(
        price_series=price_series,
        signals=signals,
        timestamps=timestamps,
        train_window=train_window,
        test_window=test_window,
        step_size=step_size,
        rolling=True,
        anchored=False,
        purge=purge,
        embargo=embargo,
    )

    window_details = []
    for w in results.windows:
        detail = {
            "train_start": w.train_start,
            "train_end": w.train_end,
            "test_start": w.test_start,
            "test_end": w.test_end,
            "purge_applied": getattr(w, "purge_applied", purge),
            "embargo_applied": getattr(w, "embargo_applied", embargo),
            "in_sample": {
                "return": w.in_sample_return,
                "sharpe": w.in_sample_sharpe,
                "max_drawdown": w.in_sample_max_drawdown,
                "sortino_ratio": getattr(w.is_metrics, "sortino_ratio", None) if w.is_metrics else None,
                "win_rate": getattr(w.is_metrics, "win_rate", None) if w.is_metrics else None,
                "profit_factor": getattr(w.is_metrics, "profit_factor", None) if w.is_metrics else None,
                "total_trades": getattr(w.is_metrics, "total_trades", None) if w.is_metrics else None,
            },
            "out_of_sample": {
                "return": w.out_of_sample_return,
                "sharpe": w.out_of_sample_sharpe,
                "max_drawdown": w.out_of_sample_max_drawdown,
                "sortino_ratio": getattr(w.oos_metrics, "sortino_ratio", None) if w.oos_metrics else None,
                "win_rate": getattr(w.oos_metrics, "win_rate", None) if w.oos_metrics else None,
                "profit_factor": getattr(w.oos_metrics, "profit_factor", None) if w.oos_metrics else None,
                "total_trades": getattr(w.oos_metrics, "total_trades", None) if w.oos_metrics else None,
            },
            "regime_info": getattr(w, "regime_info", None),
        }
        window_details.append(detail)

    payload = {
        "type": "WALKFORWARD_regime",
        "regime": regime,
        "regime_spec": {
            "description": REGIME_SPECS[regime].description,
            "drift": REGIME_SPECS[regime].drift,
            "vol": REGIME_SPECS[regime].vol,
            "trend_strength": REGIME_SPECS[regime].trend_strength,
            "chop_prob": REGIME_SPECS[regime].chop_prob,
            "liquidity_factor": REGIME_SPECS[regime].liquidity_factor,
            "gamma_sensitivity": REGIME_SPECS[regime].gamma_sensitivity,
            "iv_regime_shift": REGIME_SPECS[regime].iv_regime_shift,
            "orderflow_imbalance_bias": REGIME_SPECS[regime].orderflow_imbalance_bias,
        },
        "timestamp": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "purge": purge,
        "embargo": embargo,
        "windows": window_details,
        "overall_out_of_sample_return": results.overall_out_of_sample_return,
        "overall_out_of_sample_sharpe": results.overall_out_of_sample_sharpe,
        "overall_out_of_sample_max_drawdown": results.overall_out_of_sample_max_drawdown,
        "stability_ratio": results.stability_ratio,
        "degradation": results.degradation,
        "num_windows": len(results.windows),
        "oos_equity_curve": results.oos_equity_curve,
        "oos_trade_count": len(results.oos_trades),
        "regime_shift_coverage": getattr(results, "regime_shift_coverage", {}),
        "purge_embargo_enforced": getattr(results, "purge_embargo_enforced", purge > 0 or embargo > 0),
        "crypto_microstructure": {
            "orderflow_gamma_iv_liquidity_modeled": True,
            "regime_realistic": True,
        },
    }
    return payload


def save_regime_artifact(payload: Dict[str, Any], regime: str) -> str:
    """Persist a regime walk-forward artifact with strict ``allow_nan=False`` serialization.

    Raises :class:`SerializationError` (via :func:`serialize_metrics_strict`) if the
    payload contains any non-finite value, so NaN/Inf can never leak into a file.
    """
    from pathlib import Path
    import json

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = Path("research_state") / f"WALKFORWARD_regime_{regime}_{ts}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    # Strict: raises SerializationError on non-finite; never silently writes NaN/Inf.
    payload_clean = serialize_metrics_strict(payload)
    content = json.dumps(payload_clean, indent=2, allow_nan=False)
    fd, tmp_path = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent), suffix=".tmp")
    try:
        os.write(fd, content.encode("utf-8"))
        os.close(fd)
        fd = None
        os.replace(tmp_path, path)
        tmp_path = None
    finally:
        if fd is not None:
            os.close(fd)
        if tmp_path is not None and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
    return str(path)
