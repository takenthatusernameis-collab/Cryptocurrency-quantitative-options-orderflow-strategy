"""Numeric-invariant tests for src/analytics/regime_sizing.py (EVAL-03).

Asserts real mathematical properties (finite metrics, nonzero windows/trades,
correct sizing direction, strict-serializable output) — never ``valid=true``.
"""

from __future__ import annotations

import json
import math

import pytest

from src.analytics.regime_sizing import (
    RegimeSizingConfig,
    RegimeSizingEngine,
    evaluate_regime_sizing,
    generate_price_path,
    momentum_signal,
    run_walk_forward_mode,
)
from src.backtest.engine import BacktestConfig, RiskConfig


def test_momentum_signal_is_time_varying_and_correct() -> None:
    prices, _ = generate_price_path(seed=11, n_points=120)
    sig = momentum_signal(prices, lookback=10)
    assert len(sig) == len(prices)
    assert set(sig).issubset({-1, 0, 1})
    # A genuinely time-varying series must not be constant.
    assert len(set(sig)) > 1
    # Spot-check the definition at a late index.
    i = 90
    expected = 1 if prices[i] > prices[i - 10] else (-1 if prices[i] < prices[i - 10] else 0)
    assert sig[i] == expected


def test_generate_price_path_deterministic_and_wellformed() -> None:
    p1, t1 = generate_price_path(seed=5, n_points=80)
    p2, t2 = generate_price_path(seed=5, n_points=80)
    assert p1 == p2 and t1 == t2
    assert len(p1) == 80
    assert all(math.isfinite(x) and x > 0 for x in p1)
    assert all(t2[i] < t2[i + 1] for i in range(len(t2) - 1))


def test_config_rejects_bad_multipliers_and_thresholds() -> None:
    with pytest.raises(ValueError):
        RegimeSizingConfig(position_size_multipliers={"low_vol": 0.0})
    with pytest.raises(ValueError):
        RegimeSizingConfig(position_size_multipliers={"low_vol": float("nan")})
    with pytest.raises(ValueError):
        RegimeSizingConfig(vol_thresholds=(0.01, 0.02))  # type: ignore[arg-type]


def test_regime_multiplier_scales_position_size_down() -> None:
    cfg = BacktestConfig(initial_capital=100000.0, slippage_seed=1)
    risk = RiskConfig(max_position_pct=0.1, stop_loss_pct=0.02)
    base = RegimeSizingEngine(cfg, risk, position_size_multiplier=1.0)
    scaled = RegimeSizingEngine(cfg, risk, position_size_multiplier=0.4)
    q_base = base.calculate_position_size(50000.0, side="long")
    q_scaled = scaled.calculate_position_size(50000.0, side="long")
    assert q_base > 0 and math.isfinite(q_base)
    assert math.isclose(q_scaled, q_base * 0.4, rel_tol=1e-12)


def test_walk_forward_mode_flat_and_regime_nonzero() -> None:
    cfg = RegimeSizingConfig()
    prices, timestamps = generate_price_path(seed=3, n_points=220)
    signals = momentum_signal(prices, lookback=15)
    flat = run_walk_forward_mode(
        "flat", prices, signals, timestamps, cfg, seed=3,
        train_window=80, test_window=20, step_size=20,
    )
    regime = run_walk_forward_mode(
        "regime", prices, signals, timestamps, cfg, seed=3,
        train_window=80, test_window=20, step_size=20,
    )
    for res in (flat, regime):
        assert res.num_windows > 0
        assert res.oos_trade_count > 0
        assert math.isfinite(res.oos_return) and res.oos_return != 0.0
        assert math.isfinite(res.oos_sharpe)
        assert math.isfinite(res.oos_max_drawdown)
        assert res.bootstrap_ci["n_returns"] > 0


def test_evaluate_regime_sizing_numeric_invariants() -> None:
    res = evaluate_regime_sizing(
        seeds=[1, 2], n_points=220, train_window=80, test_window=20, step_size=20
    )
    total_windows = sum(int(p["num_windows"]) for p in res.per_seed)
    total_trades = sum(int(p["oos_trade_count"]) for p in res.per_seed)
    assert total_windows > 0
    assert total_trades > 0
    assert math.isfinite(res.regime_avg["oos_return"])
    assert math.isfinite(res.regime_avg["oos_sharpe"])
    assert res.regime_avg["oos_return"] != 0.0
    # Delta must reconcile to the difference of the reported averages.
    assert math.isclose(
        res.delta["oos_sharpe_delta"],
        res.regime_avg["oos_sharpe"] - res.flat_avg["oos_sharpe"],
        rel_tol=1e-12,
        abs_tol=1e-12,
    )
    # Nonzero/finite gates are hard invariants; the "beats flat" gate is empirical.
    for hard_gate in (
        "nonzero_windows",
        "nonzero_trades",
        "nonzero_regime_oos_return",
        "finite_regime_metrics",
    ):
        assert res.gates[hard_gate]["pass"] is True, hard_gate
    assert res.verdict == ("GO" if all(g["pass"] for g in res.gates.values()) else "NO-GO")


def test_serialize_is_strict_json() -> None:
    res = evaluate_regime_sizing(
        seeds=[1], n_points=200, train_window=80, test_window=20, step_size=20
    )
    payload = res.serialize()
    text = json.dumps(payload, allow_nan=False)
    assert "NaN" not in text and "Infinity" not in text
    assert payload["verdict"] in {"GO", "NO-GO"}
    assert payload["gates"]["nonzero_windows"]["pass"] is True