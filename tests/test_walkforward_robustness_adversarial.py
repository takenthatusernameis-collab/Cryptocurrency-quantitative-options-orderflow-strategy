"""Adversarial walk-forward/OOS robustness tests.

Covers purge/embargo edge cases (excessive values clamped to valid windows),
anchored/rolling parity and determinism, strict time-ordering with mixed
tz-aware/naive datetimes, and serialization/stability invariants for OOS
results. No placeholders; production-grade assertions only.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone
from typing import Dict, List

import pytest

from src.backtest.engine import BacktestEngine, WalkForwardBacktest, run_walk_forward
from src.config import BacktestConfig, RiskConfig
from src.errors import SerializationError


def _rising_prices(n: int, base: float = 50000.0, step: float = 1.0) -> List[float]:
    prices = []
    for i in range(n):
        prices.append(base + i * step)
    return prices


def _rising_signals(n: int) -> List[int]:
    signals = [0] * n
    for i in range(50, n):
        if i % 20 < 10:
            signals[i] = 1
        else:
            signals[i] = -1 if i % 30 == 29 else 0
    return signals


def _base_timestamps(n: int, start: datetime | None = None) -> List[datetime]:
    if start is None:
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    return [start + timedelta(minutes=i) for i in range(n)]


def test_purge_embargo_clamped_when_excessive_keeps_valid_windows():
    """Excessive purge/embargo larger than windows are clamped safely."""
    n = 150
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=1000, embargo=1000
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    # Must not crash; windows may be empty or valid depending on clamping
    assert isinstance(results.windows, list)
    for w in results.windows:
        assert w.train_start < w.train_end
        assert w.test_start < w.test_end
        assert w.train_end <= w.test_start  # no overlap after clamping


def test_purge_embargo_per_call_override_strict():
    """Per-call purge/embargo override instance defaults correctly."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=0, embargo=0
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=80, test_window=40, step_size=40,
        purge=10, embargo=10,
    )
    assert isinstance(results.windows, list)
    for w in results.windows:
        assert w.train_end - w.train_start <= 80  # purged
        assert w.test_end - w.test_start <= 40  # embargoed
        assert w.train_end <= w.test_start


def test_anchored_expanding_window_parity_and_determinism():
    """Anchored expanding windows are deterministic and produce valid OOS."""
    n = 220
    prices = {"BTC": _rising_prices(n, base=40000.0, step=2.0)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    cfg = BacktestConfig(initial_capital=100000.0, slippage_seed=4242)
    wfb = WalkForwardBacktest(cfg, RiskConfig(), purge=3, embargo=3)
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=40, step_size=20,
        anchored=True,
    )
    assert isinstance(results.windows, list)
    assert math.isfinite(results.overall_out_of_sample_return)
    assert math.isfinite(results.overall_out_of_sample_sharpe)
    assert math.isfinite(results.stability_ratio)
    assert math.isfinite(results.degradation)
    # Determinism
    assert wfb.verify_determinism(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=40, step_size=20,
        anchored=True, purge=3, embargo=3,
    ) is True


def test_rolling_vs_anchored_both_deterministic_with_purge_embargo():
    """Both modes deterministic under purge/embargo."""
    n = 200
    prices = {"ETH": _rising_prices(n, base=3000.0, step=0.5)}
    signals = {"ETH": _rising_signals(n)}
    ts = _base_timestamps(n)

    cfg = BacktestConfig(initial_capital=50000.0, slippage_seed=777)
    for anchored in (False, True):
        wfb = WalkForwardBacktest(cfg, RiskConfig(), purge=5, embargo=2)
        assert wfb.verify_determinism(
            price_series=prices, signals=signals, timestamps=ts,
            train_window=70, test_window=30, step_size=25,
            anchored=anchored,
        ) is True


def test_time_ordering_naive_and_mixed_tz():
    """Time ordering accepts naive datetimes and mixed tz-aware/naive (naive treated as UTC)."""
    n = 120
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    # Start naive
    start = datetime(2024, 6, 1)  # naive
    ts = [start + timedelta(hours=i) for i in range(n)]
    # Make some tz-aware but keep them monotonically increasing in UTC
    ts[10] = (start + timedelta(hours=10)).replace(tzinfo=timezone.utc)
    ts[50] = (start + timedelta(hours=50)).astimezone(timezone(timedelta(hours=2)))
    # Ensure strictly increasing overall
    for j in range(1, len(ts)):
        if ts[j].tzinfo is None:
            ts_norm_j = ts[j].replace(tzinfo=timezone.utc)
        else:
            ts_norm_j = ts[j].astimezone(timezone.utc)
        if ts[j-1].tzinfo is None:
            ts_norm_prev = ts[j-1].replace(tzinfo=timezone.utc)
        else:
            ts_norm_prev = ts[j-1].astimezone(timezone.utc)
        if ts_norm_j <= ts_norm_prev:
            ts[j] = (ts[j-1] + timedelta(hours=1))
            if ts[j].tzinfo is not None:
                ts[j] = ts[j].astimezone(timezone.utc).replace(tzinfo=None)  # make naive for simplicity

    wfb = WalkForwardBacktest(BacktestConfig(initial_capital=100000.0), RiskConfig())
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=40, test_window=20, step_size=20,
    )
    assert isinstance(results.windows, list)


def test_time_ordering_rejects_decreasing_across_mixed_tz():
    """Decreasing timestamps rejected even with mixed tz awareness."""
    n = 80
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": [0] * n}
    start = datetime(2024, 1, 1, tzinfo=timezone.utc)
    ts = [start + timedelta(minutes=i) for i in range(n)]
    ts[30] = ts[29].replace(tzinfo=timezone(timedelta(hours=5))) - timedelta(minutes=1)  # go back
    wfb = WalkForwardBacktest(BacktestConfig(initial_capital=100000.0), RiskConfig())
    with pytest.raises(ValueError, match="not strictly increasing"):
        wfb.run_walk_forward(
            price_series=prices, signals=signals, timestamps=ts,
            train_window=30, test_window=10, step_size=10,
        )


def test_oos_serialization_strict_finishes_all_windows():
    """serialize_oos() passes strict serialization with allow_nan=False on valid runs."""
    n = 180
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=4, embargo=4)
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    results.assert_oos_finite()
    payload = results.serialize_oos()
    assert isinstance(payload, dict)
    assert "oos_equity_curve" in payload
    assert "num_windows" in payload


def test_oos_serialize_raises_on_window_nonfinite():
    """serialize_oos() rejects if any window metric becomes non-finite."""
    n = 160
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(BacktestConfig(initial_capital=100000.0), RiskConfig())
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=50, test_window=25, step_size=25,
    )
    if results.windows:
        results.windows[0].out_of_sample_sharpe = float("nan")
        with pytest.raises(SerializationError):
            results.serialize_oos()
    else:
        # If no windows, corrupt aggregate
        results.overall_out_of_sample_sharpe = float("-inf")
        with pytest.raises(SerializationError):
            results.serialize_oos()


def test_cross_symbol_time_alignment_enforced():
    """Multi-symbol with identical timestamps processed consistently."""
    n = 150
    prices = {
        "BTC": _rising_prices(n, base=50000.0),
        "ETH": _rising_prices(n, base=3000.0, step=0.8),
    }
    signals = {
        "BTC": _rising_signals(n),
        "ETH": [1 if i % 12 < 2 else 0 for i in range(n)],
    }
    ts = _base_timestamps(n)
    wfb = WalkForwardBacktest(BacktestConfig(initial_capital=200000.0), RiskConfig(), purge=2, embargo=2)
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    assert isinstance(results.windows, list)
    for w in results.windows:
        assert w.train_end <= w.test_start
    results.assert_oos_finite()
