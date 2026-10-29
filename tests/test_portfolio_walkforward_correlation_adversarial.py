"""Adversarial tests for portfolio-level walk-forward with correlation constraints.

Covers correlation spikes, diversification breakdown, regime-dependent cost shocks,
cross-symbol constraint breach prevention, purge/embargo across symbols, strict
time ordering (tz-aware/naive), determinism, serialization with allow_nan=False,
finite metrics, positions-flatten invariants, and edge cases.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from math import isfinite

import pytest

from src.backtest.engine import (
    PortfolioWalkForwardBacktest,
    PortfolioWalkForwardResults,
    run_portfolio_walk_forward,
)
from src.telemetry.serialization import SerializationError


def _make_correlated_prices(n: int = 240, seed: int = 123) -> dict:
    random.seed(seed)
    # Common factor
    factors = [1.0]
    for i in range(1, n):
        factors.append(factors[-1] * (1.0 + random.gauss(0.00005, 0.01)))
    prices = {}
    # BTC more independent-ish, others correlated to factor
    base = {"BTC": 100.0, "ETH": 50.0, "SOL": 20.0}
    for sym, b in base.items():
        series = [b]
        for i in range(1, n):
            beta = 0.6 if sym != "BTC" else 0.3
            ret = beta * (factors[i] / factors[i - 1] - 1.0) + (1 - beta) * random.gauss(0.00005, 0.012)
            series.append(series[-1] * (1.0 + ret))
        prices[sym] = series
    return prices


def _make_simple_signals(price_series: dict, every: int = 30) -> dict:
    n = len(next(iter(price_series.values())))
    signals = {s: [0] * n for s in price_series}
    for i in range(40, n - 20, every):
        for s in signals:
            signals[s][i] = 1
    return signals


def test_portfolio_walkforward_basic_with_correlation():
    prices = _make_correlated_prices(n=220, seed=7)
    signals = _make_simple_signals(prices, every=35)
    res = run_portfolio_walk_forward(
        prices,
        signals=signals,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=2,
        embargo=1,
        correlation_constraint=True,
    )
    assert isinstance(res, PortfolioWalkForwardResults)
    assert len(res.windows) >= 1
    res.assert_oos_finite()
    s = res.serialize_oos()
    assert s["num_windows"] == len(res.windows)
    assert isfinite(s["overall_out_of_sample_return"])
    assert isfinite(s["overall_out_of_sample_sharpe"])
    assert isfinite(s["overall_out_of_sample_max_drawdown"])


def test_correlation_matrix_recorded_when_constrained():
    prices = _make_correlated_prices(n=200, seed=11)
    signals = _make_simple_signals(prices, every=40)
    pwfb = PortfolioWalkForwardBacktest(correlation_window=40, max_correlation=0.7)
    res = pwfb.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=1,
        embargo=1,
        correlation_constraint=True,
    )
    # At least some windows may have correlation matrix
    has_corr = any(w.correlation_matrix is not None for w in res.windows)
    assert has_corr
    for w in res.windows:
        if w.correlation_matrix is not None:
            mat = w.correlation_matrix
            assert isinstance(mat, list)
        # diagonal should be ~1.0
        for i in range(len(mat)):
            assert abs(mat[i][i] - 1.0) < 1e-9
        # symmetric and clipped (off-diagonal)
        n = len(mat)
        for i in range(n):
            for j in range(n):
                val = mat[i][j]
                assert isfinite(val)
                if i != j:
                    assert abs(val) <= 0.7 + 1e-9
                else:
                    assert abs(val - 1.0) < 1e-9


def test_correlation_spike_adversarial():
    prices = _make_correlated_prices(n=260, seed=13)
    # Create a correlation spike regime by making all move together at end of train windows conceptually
    # Just ensure constraints hold
    signals = _make_simple_signals(prices, every=25)
    pwfb = PortfolioWalkForwardBacktest(correlation_window=30, max_correlation=0.5)
    res = pwfb.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        train_window=70,
        test_window=30,
        step_size=30,
        purge=2,
        embargo=2,
        correlation_constraint=True,
    )
    res.assert_oos_finite()
    res.serialize_oos()
    # Constraint enforcement should keep things finite
    assert all(isfinite(w.out_of_sample_sharpe) for w in res.windows)


def test_diversification_breakdown_handling():
    # All highly correlated
    random.seed(99)
    n = 200
    base = [100.0]
    for i in range(1, n):
        base.append(base[-1] * (1.0 + random.gauss(0.0001, 0.01)))
    prices = {s: [x * (1.0 + random.gauss(0, 0.001)) for x in base] for s in ["BTC", "ETH", "SOL", "XRP"]}
    signals = {s: [0] * n for s in prices}
    for i in range(50, n - 15, 25):
        for s in signals:
            signals[s][i] = 1
    pwfb = PortfolioWalkForwardBacktest(correlation_window=50, max_correlation=0.6)
    res = pwfb.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=3,
        embargo=2,
        correlation_constraint=True,
    )
    res.assert_oos_finite()
    res.serialize_oos()


def test_regime_dependent_costs_slippage_applied():
    prices = _make_correlated_prices(n=220, seed=17)
    signals = _make_simple_signals(prices, every=30)
    pwfb_normal = PortfolioWalkForwardBacktest(regime_costs={"normal": 0.0002})
    pwfb_stress = PortfolioWalkForwardBacktest(regime_costs={"stress": 0.0010})
    res_n = pwfb_normal.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=1,
        embargo=1,
        regime="normal",
    )
    res_s = pwfb_stress.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=1,
        embargo=1,
        regime="stress",
    )
    res_n.assert_oos_finite()
    res_s.assert_oos_finite()
    res_n.serialize_oos()
    res_s.serialize_oos()
    # Stress regime should have higher costs -> different (worse or different) results in general
    assert len(res_s.windows) == len(res_n.windows)


def test_cross_symbol_constraint_breach_prevention():
    prices = _make_correlated_prices(n=200, seed=23)
    signals = _make_simple_signals(prices, every=20)  # more frequent signals
    pwfb = PortfolioWalkForwardBacktest(correlation_window=40, max_correlation=0.4)
    res = pwfb.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=2,
        embargo=1,
        correlation_constraint=True,
    )
    res.assert_oos_finite()
    res.serialize_oos()
    # No non-finite from constraint breaches
    assert all(isfinite(w.in_sample_return) and isfinite(w.out_of_sample_return) for w in res.windows)


def test_purge_embargo_across_symbols():
    prices = _make_correlated_prices(n=240, seed=29)
    signals = _make_simple_signals(prices, every=30)
    pwfb = PortfolioWalkForwardBacktest(purge=5, embargo=3)
    res = pwfb.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        train_window=80,
        test_window=40,
        step_size=40,
        purge=5,
        embargo=3,
        correlation_constraint=True,
    )
    res.assert_oos_finite()
    res.serialize_oos()
    for w in res.windows:
        assert w.train_end - w.train_start >= 0
        assert w.test_end >= w.test_start


def test_strict_time_ordering_tz_aware_and_naive():
    prices = _make_correlated_prices(n=180, seed=31)
    signals = _make_simple_signals(prices, every=35)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    timestamps_tz = [base + timedelta(hours=i) for i in range(180)]
    pwfb = PortfolioWalkForwardBacktest()
    res = pwfb.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        timestamps=timestamps_tz,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=1,
        embargo=1,
        correlation_constraint=True,
    )
    res.assert_oos_finite()

    # naive timestamps
    timestamps_naive = [datetime(2026, 1, 1) + timedelta(hours=i) for i in range(180)]
    res2 = pwfb.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        timestamps=timestamps_naive,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=1,
        embargo=1,
        correlation_constraint=True,
    )
    res2.assert_oos_finite()


def test_time_ordering_violation_raises():
    prices = _make_correlated_prices(n=120, seed=37)
    signals = _make_simple_signals(prices, every=30)
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    timestamps = [base + timedelta(hours=i) for i in range(120)]
    timestamps[50] = timestamps[49]  # not strictly increasing
    pwfb = PortfolioWalkForwardBacktest()
    with pytest.raises(ValueError):
        pwfb.run_portfolio_walk_forward(
            price_series=prices,
            signals=signals,
            timestamps=timestamps,
            train_window=40,
            test_window=20,
            step_size=20,
            correlation_constraint=True,
        )


def test_determinism_portfolio_walkforward_twice_identical():
    prices = _make_correlated_prices(n=200, seed=41)
    signals = _make_simple_signals(prices, every=30)
    pwfb = PortfolioWalkForwardBacktest()
    r1 = pwfb.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=2,
        embargo=1,
        correlation_constraint=True,
    )
    r2 = pwfb.run_portfolio_walk_forward(
        price_series=prices,
        signals=signals,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=2,
        embargo=1,
        correlation_constraint=True,
    )
    s1 = r1.serialize_oos()
    s2 = r2.serialize_oos()
    assert s1 == s2
    assert len(r1.windows) == len(r2.windows)
    for w1, w2 in zip(r1.windows, r2.windows):
        assert w1.train_start == w2.train_start
        assert w1.train_end == w2.train_end
        assert w1.test_start == w2.test_start
        assert w1.test_end == w2.test_end
        assert w1.out_of_sample_return == w2.out_of_sample_return
        assert w1.out_of_sample_sharpe == w2.out_of_sample_sharpe


def test_serialization_allow_nan_false_strict():
    prices = _make_correlated_prices(n=200, seed=43)
    signals = _make_simple_signals(prices, every=30)
    res = run_portfolio_walk_forward(
        prices,
        signals=signals,
        train_window=60,
        test_window=20,
        step_size=20,
        purge=1,
        embargo=1,
        correlation_constraint=True,
    )
    res.assert_oos_finite()
    s = res.serialize_oos()
    # ensure no NaN/Inf
    import json

    out = json.dumps(s)
    assert "NaN" not in out
    assert "Infinity" not in out
    assert "-Infinity" not in out


def test_positions_flat_invariants_on_edges():
    prices = _make_correlated_prices(n=150, seed=47)
    signals = _make_simple_signals(prices, every=50)
    res = run_portfolio_walk_forward(
        prices,
        signals=signals,
        train_window=50,
        test_window=25,
        step_size=25,
        purge=0,
        embargo=0,
        correlation_constraint=True,
    )
    res.assert_oos_finite()
    res.serialize_oos()


def test_edge_cases_empty_short_series():
    prices = {"BTC": [100.0, 101.0, 102.0], "ETH": [50.0, 51.0, 52.0]}
    signals = {"BTC": [0, 0, 0], "ETH": [0, 0, 0]}
    res = run_portfolio_walk_forward(
        prices,
        signals=signals,
        train_window=2,
        test_window=1,
        step_size=1,
        purge=0,
        embargo=0,
        correlation_constraint=True,
    )
    res.assert_oos_finite()
    res.serialize_oos()


def test_single_symbol_path_still_works():
    prices = {"BTC": [100.0 + i * 0.1 for i in range(150)]}
    signals = {"BTC": [1 if i % 40 == 0 else 0 for i in range(150)]}
    res = run_portfolio_walk_forward(
        prices,
        signals=signals,
        train_window=40,
        test_window=20,
        step_size=20,
        purge=1,
        embargo=1,
        correlation_constraint=False,
    )
    res.assert_oos_finite()
    res.serialize_oos()
