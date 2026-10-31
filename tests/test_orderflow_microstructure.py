"""Orderflow microstructure hardening tests (Phase 7).

Covers signed volume, footprint imbalance, gamma wall proximity, liquidity
sweep score, OFI/toxicity, trade aggressor, absorption ratio, regime detection,
regime-aware normalization, adversarial inputs (NaN/Inf, empty, extreme sizes,
invalid sides), lookahead-freeness, determinism, and strict serialization
(allow_nan=False).
"""

import json
import math
from datetime import datetime, timezone

from math import isfinite

import pytest

from src.data.schemas import Liquidation, OrderflowSnapshot, Trade
from src.features.orderflow_microstructure import (
    compute_absorption_ratio,
    compute_footprint_imbalance,
    compute_gamma_wall_proximity,
    compute_liquidity_sweep_score,
    compute_microstructure_features_dict,
    compute_oft_score,
    compute_signed_volume,
    compute_trade_aggressor_score,
    detect_regime,
    normalize_for_regime,
)
from src.errors import NonFiniteResultError
from src.telemetry import serialize_metrics_strict


def _trade(symbol: str, price: float, size: float, side: str, tid: str,
           ts: datetime | None = None) -> Trade:
    if ts is None:
        ts = datetime.now(timezone.utc)
    return Trade(trade_id=tid, symbol=symbol, venue="v", price=price, size=size,
                 side=side, timestamp=ts)


def _snapshot(symbol: str, trades: list, liquidations: list | None = None,
              ts: datetime | None = None) -> OrderflowSnapshot:
    if ts is None:
        ts = datetime.now(timezone.utc)
    return OrderflowSnapshot(symbol=symbol, venue="v", trades=list(trades),
                             liquidations=list(liquidations or []), funding_rates=[],
                             timestamp=ts)


# --------------------------------------------------------------------------- signed volume


def test_signed_volume_basic():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", "t1"),
              _trade("BTCUSDT", 100.0, 2.0, "sell", "t2")]
    assert compute_signed_volume(trades) == -1.0


def test_signed_volume_empty_returns_zero():
    assert compute_signed_volume([]) == 0.0
    assert compute_signed_volume(None) == 0.0


def test_signed_volume_window():
    trades = [_trade("BTCUSDT", 100.0, float(i), "buy", f"t{i}") for i in range(1, 6)]
    assert compute_signed_volume(trades, window=2) == 9.0  # last two: 4+5


def test_signed_volume_non_finite_size_skipped():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", "t1"),
              _trade("BTCUSDT", float("nan"), 1.0, "sell", "t2")]
    v = compute_signed_volume(trades)
    assert math.isfinite(v)
    assert v == 1.0


def test_signed_volume_invalid_side_skipped():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", "t1"),
              _trade("BTCUSDT", 100.0, 1.0, "unknown", "t2")]
    assert compute_signed_volume(trades) == 1.0


# --------------------------------------------------------------------------- footprint imbalance


def test_footprint_imbalance_bounded():
    trades = [_trade("BTCUSDT", 100.0, 10.0, "buy", "t1"),
              _trade("BTCUSDT", 100.0, 2.0, "sell", "t2")]
    imb = compute_footprint_imbalance(trades)
    assert -1.0 <= imb <= 1.0
    assert imb > 0  # more buy volume


def test_footprint_imbalance_empty():
    assert compute_footprint_imbalance([]) == 0.0


def test_footprint_imbalance_all_buy_is_one():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", f"t{i}") for i in range(3)]
    assert compute_footprint_imbalance(trades) == 1.0


def test_footprint_imbalance_all_sell_is_neg_one():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "sell", f"t{i}") for i in range(3)]
    assert compute_footprint_imbalance(trades) == -1.0


# --------------------------------------------------------------------------- gamma wall proximity


def test_gamma_wall_proximity_at_wall_is_one():
    assert compute_gamma_wall_proximity(100000.0, gamma_walls={100000.0: 1e6}) == 1.0


def test_gamma_wall_proximity_far_is_zero():
    assert compute_gamma_wall_proximity(100000.0, gamma_walls={200000.0: 1e6}) == 0.0


def test_gamma_wall_proximity_no_walls_zero():
    assert compute_gamma_wall_proximity(100000.0) == 0.0


def test_gamma_wall_proximity_invalid_spot_zero():
    assert compute_gamma_wall_proximity(0.0, gamma_walls={100000.0: 1e6}) == 0.0


# --------------------------------------------------------------------------- liquidity sweep


def test_liquidity_sweep_score_bounded():
    trades = [_trade("BTCUSDT", 100.0, float(i), "buy", f"t{i}") for i in range(1, 21)]
    score = compute_liquidity_sweep_score(trades)
    assert 0.0 <= score <= 1.0


def test_liquidity_sweep_empty():
    assert compute_liquidity_sweep_score([]) == 0.0


def test_liquidity_sweep_with_liquidations():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", f"t{i}") for i in range(10)]
    liqs = [Liquidation(liquidation_id=f"l{i}", symbol="BTCUSDT", venue="v",
                        price=100.0, size=10.0, side="long",
                        timestamp=datetime.now(timezone.utc)) for i in range(5)]
    score = compute_liquidity_sweep_score(trades, liquidations=liqs)
    assert 0.0 <= score <= 1.0


# --------------------------------------------------------------------------- OFI / toxicity


def test_oft_score_bounded():
    trades = [_trade("BTCUSDT", 100.0, float(i), "buy" if i % 2 == 0 else "sell", f"t{i}")
              for i in range(20)]
    score = compute_oft_score(trades)
    assert 0.0 <= score <= 1.0


def test_oft_score_empty():
    assert compute_oft_score([]) == 0.0


# --------------------------------------------------------------------------- trade aggressor


def test_trade_aggressor_bounded():
    trades = [_trade("BTCUSDT", 100.0, 10.0, "buy", f"t{i}") for i in range(5)] + \
             [_trade("BTCUSDT", 100.0, 1.0, "sell", f"s{i}") for i in range(5)]
    score = compute_trade_aggressor_score(trades)
    assert -1.0 <= score <= 1.0
    assert score > 0  # buy-dominant


def test_trade_aggressor_empty():
    assert compute_trade_aggressor_score([]) == 0.0


# --------------------------------------------------------------------------- absorption


def test_absorption_ratio_bounded():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", f"t{i}") for i in range(10)] + \
             [_trade("BTCUSDT", 100.0, 100.0, "buy", "big")]
    ratio = compute_absorption_ratio(trades)
    assert 0.0 <= ratio <= 1.0


def test_absorption_ratio_insufficient_trades():
    assert compute_absorption_ratio([_trade("BTCUSDT", 100.0, 1.0, "buy", "t1")]) == 0.0


# --------------------------------------------------------------------------- regime


def test_detect_regime_quiet():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", f"t{i}") for i in range(3)]
    assert detect_regime(trades, oft_score=0.1, liquidity_sweep_score=0.1) == "quiet"


def test_detect_regime_trending():
    trades = [_trade("BTCUSDT", 100.0, 10.0, "buy", f"t{i}") for i in range(10)]
    reg = detect_regime(trades, oft_score=0.2, liquidity_sweep_score=0.1)
    assert reg == "trending"


def test_detect_regime_high_vol_chop():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", f"t{i}") for i in range(10)]
    reg = detect_regime(trades, oft_score=0.8, liquidity_sweep_score=0.1, volatility=0.15)
    assert reg == "high_vol_chop"


def test_detect_regime_liquidity_thin():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", f"t{i}") for i in range(10)]
    reg = detect_regime(trades, oft_score=0.3, liquidity_sweep_score=0.8)
    assert reg == "liquidity_thin"


# --------------------------------------------------------------------------- regime normalization


def test_normalize_for_regime_bounded():
    assert 0.0 <= normalize_for_regime(0.5, "ranging") <= 1.0
    assert 0.0 <= normalize_for_regime(-5.0, "trending") <= 1.0
    assert 0.0 <= normalize_for_regime(5.0, "high_vol_chop") <= 1.0


def test_normalize_for_regime_custom_stats():
    stats = {"ranging": {"mean": 0.0, "std": 1.0, "min": -1.0, "max": 1.0}}
    assert 0.0 <= normalize_for_regime(0.0, "ranging", regime_stats=stats) <= 1.0


# --------------------------------------------------------------------------- full microstructure features


def test_compute_microstructure_features_dict_strict():
    trades = [_trade("BTCUSDT", 100.0 + i * 0.1, 1.0, "buy" if i % 2 == 0 else "sell", f"t{i}")
              for i in range(50)]
    liqs = [Liquidation(liquidation_id=f"l{i}", symbol="BTCUSDT", venue="v",
                        price=100.0, size=5.0, side="long",
                        timestamp=datetime.now(timezone.utc)) for i in range(5)]
    snap = _snapshot("BTCUSDT", trades, liquidations=liqs)
    out = compute_microstructure_features_dict(snap, gamma_walls={105.0: 1e6},
                                               spot=100.0, volatility=0.65, window=25)
    assert isfinite(out["signed_volume"])
    assert -1.0 <= out["footprint_imbalance"] <= 1.0
    assert 0.0 <= out["gamma_wall_proximity"] <= 1.0
    assert 0.0 <= out["liquidity_sweep_score"] <= 1.0
    assert 0.0 <= out["oft_score"] <= 1.0
    assert -1.0 <= out["trade_aggressor_score"] <= 1.0
    assert 0.0 <= out["absorption_ratio"] <= 1.0
    assert out["regime"] in ("quiet", "trending", "ranging", "high_vol_chop", "liquidity_thin")
    assert out["lookahead_free"] is True
    assert out["regime_normalized"] is True
    assert json.dumps(out, allow_nan=False) is not None


def test_compute_microstructure_features_empty_snapshot():
    snap = _snapshot("BTCUSDT", [])
    out = compute_microstructure_features_dict(snap, spot=100.0, volatility=0.65)
    assert out["signed_volume"] == 0.0
    assert out["footprint_imbalance"] == 0.0
    assert json.dumps(out, allow_nan=False) is not None


def test_microstructure_adversarial_nan_price():
    # Non-finite price trades are filtered, never crash
    trades = [_trade("BTCUSDT", float("nan"), 1.0, "buy", "t1"),
              _trade("BTCUSDT", 100.0, 1.0, "sell", "t2")]
    snap = _snapshot("BTCUSDT", trades)
    out = compute_microstructure_features_dict(snap, spot=100.0, volatility=0.65)
    assert isfinite(out["signed_volume"])
    assert json.dumps(out, allow_nan=False) is not None


def test_microstructure_adversarial_extreme_size():
    trades = [_trade("BTCUSDT", 100.0, 1e15, "buy", "t1")]
    snap = _snapshot("BTCUSDT", trades)
    out = compute_microstructure_features_dict(snap, spot=100.0, volatility=0.65)
    assert isfinite(out["signed_volume"])
    assert -1.0 <= out["footprint_imbalance"] <= 1.0


def test_microstructure_deterministic_rerun():
    trades = [_trade("BTCUSDT", 100.0 + i * 0.1, 1.0, "buy" if i % 2 == 0 else "sell", f"t{i}")
              for i in range(50)]
    snap = _snapshot("BTCUSDT", trades)
    o1 = compute_microstructure_features_dict(snap, gamma_walls={105.0: 1e6}, spot=100.0, volatility=0.65)
    o2 = compute_microstructure_features_dict(snap, gamma_walls={105.0: 1e6}, spot=100.0, volatility=0.65)
    assert o1 == o2


def test_microstructure_all_outputs_finite_and_serializable():
    trades = [_trade("BTCUSDT", 100.0, 1.0, "buy", f"t{i}") for i in range(20)]
    snap = _snapshot("BTCUSDT", trades)
    out = compute_microstructure_features_dict(snap, spot=100.0, volatility=0.65)
    for k, v in out.items():
        if isinstance(v, float):
            assert math.isfinite(v), f"{k} is non-finite: {v}"
    assert json.dumps(out, allow_nan=False) is not None
