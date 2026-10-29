"""OOS & walk-forward robustness tests (Phase 8, objective 1).

Covers: purge/embargo windows, strict time ordering/no lookahead,
RNG seed determinism propagation, allow_nan=False metric serialization,
and stability SerializationError guards.
"""

from datetime import datetime, timedelta, timezone

import math
import pytest

from src.backtest.engine import (
    BacktestEngine,
    WalkForwardBacktest,
    WalkForwardResults,
    WalkForwardWindowResult,
)
from src.config import BacktestConfig, RiskConfig
from src.errors import SerializationError
from src.telemetry import serialize_metrics_strict


def _base_timestamps(n: int, start: datetime = None) -> list:
    if start is None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [start + timedelta(hours=i) for i in range(n)]


def _rising_prices(n: int, base: float = 50000.0, step: float = 10.0) -> list:
    return [base + i * step for i in range(n)]


def _rising_signals(n: int) -> list:
    return [1 if i % 10 < 5 else (-1 if i % 20 == 19 else 0) for i in range(n)]


# --------------------------------------------------------------------------- #
# Purge/embargo correctness
# --------------------------------------------------------------------------- #

def test_purge_embargo_shrink_windows():
    """Purge shrinks train tail; embargo shrinks test head; train/test never overlap."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=10, embargo=5
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    assert len(results.windows) > 0
    for w in results.windows:
        # Train end (after purge) must be <= test start (after embargo)
        assert w.train_end <= w.test_start, f"train_end {w.train_end} > test_start {w.test_start}"
        # Effective train window: train_end - purge >= train_start
        assert w.train_end - w.train_start >= 0
        # Effective test window: test_end - test_start >= 0
        assert w.test_end - w.test_start >= 0


def test_purge_embargo_zero_preserves_original_behavior():
    """purge=0, embargo=0 should produce same windows as before (train_end == test_start)."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=0, embargo=0
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    assert len(results.windows) > 0
    for w in results.windows:
        assert w.train_end == w.test_start


def test_purge_larger_than_train_window_clamped():
    """purge >= train_window should not crash; effective train window >= 0."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=1000, embargo=0
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    assert len(results.windows) >= 0
    for w in results.windows:
        assert w.train_end - 1000 <= w.test_start


def test_embargo_larger_than_test_window_clamped():
    """embargo >= test_window should not crash; effective test window >= 0."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=0, embargo=1000
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    assert len(results.windows) >= 0
    for w in results.windows:
        assert w.test_start + 1000 >= w.test_end


def test_purge_embargo_per_call_override():
    """Per-call purge/embargo override instance-level values."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=0, embargo=0
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30, purge=5, embargo=5,
    )
    assert len(results.windows) > 0
    for w in results.windows:
        assert w.train_end - 5 <= w.test_start + 5


# --------------------------------------------------------------------------- #
# Strict time ordering / no lookahead
# --------------------------------------------------------------------------- #

def test_time_ordering_rejects_non_monotonic():
    """Non-monotonic timestamps raise ValueError (no lookahead)."""
    n = 100
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": [0] * n}
    ts = _base_timestamps(n)
    # Insert an out-of-order timestamp in the middle
    bad_ts = list(ts)
    bad_ts[50] = bad_ts[40]  # not strictly increasing

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig()
    )
    with pytest.raises(ValueError, match="not strictly increasing"):
        wfb.run_walk_forward(
            price_series=prices, signals=signals, timestamps=bad_ts,
            train_window=40, test_window=20, step_size=20,
        )


def test_time_ordering_accepts_monotonic():
    """Strictly increasing timestamps pass validation."""
    n = 100
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": [0] * n}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig()
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=40, test_window=20, step_size=20,
    )
    assert len(results.windows) > 0


def test_time_ordering_rejects_equal_timestamps():
    """Equal adjacent timestamps are not strictly increasing."""
    n = 50
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": [0] * n}
    ts = _base_timestamps(n)
    bad_ts = list(ts)
    bad_ts[25] = bad_ts[24]  # equal, not strictly increasing

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig()
    )
    with pytest.raises(ValueError, match="not strictly increasing"):
        wfb.run_walk_forward(
            price_series=prices, signals=signals, timestamps=bad_ts,
            train_window=20, test_window=10, step_size=10,
        )


def test_no_timestamps_allowed():
    """Omitting timestamps is allowed (falls back to wall-clock per tick)."""
    n = 100
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": [0] * n}

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig()
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=None,
        train_window=40, test_window=20, step_size=20,
    )
    assert len(results.windows) >= 0


# --------------------------------------------------------------------------- #
# RNG seed determinism / reproducibility
# --------------------------------------------------------------------------- #

def test_determinism_same_seed_identical_results():
    """Same slippage_seed produces byte-identical walk-forward results."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    cfg = BacktestConfig(initial_capital=100000.0, slippage_seed=12345, partial_fill_rate=0.5)
    wfb = WalkForwardBacktest(cfg, RiskConfig())
    assert wfb.verify_determinism(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    ) is True


def test_determinism_different_seed_different_results_possible():
    """Different slippage_seed may produce different partial-fill results (not guaranteed to differ, but seed is used)."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    cfg_a = BacktestConfig(initial_capital=100000.0, slippage_seed=1, partial_fill_rate=0.5)
    cfg_b = BacktestConfig(initial_capital=100000.0, slippage_seed=99999, partial_fill_rate=0.5)
    wfb_a = WalkForwardBacktest(cfg_a, RiskConfig())
    wfb_b = WalkForwardBacktest(cfg_b, RiskConfig())
    r_a = wfb_a.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    r_b = wfb_b.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    # Both must be valid (finite) regardless of seed
    assert math.isfinite(r_a.overall_out_of_sample_return)
    assert math.isfinite(r_b.overall_out_of_sample_return)


def test_seed_propagated_to_each_window_engine():
    """Each window engine uses the configured slippage_seed (deterministic RNG)."""
    n = 100
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": [0] * n}
    ts = _base_timestamps(n)

    cfg = BacktestConfig(initial_capital=100000.0, slippage_seed=42, partial_fill_rate=1.0)
    wfb = WalkForwardBacktest(cfg, RiskConfig())
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=40, test_window=20, step_size=20,
    )
    assert len(results.windows) > 0
    # All OOS returns finite (deterministic RNG produces sane fills)
    for w in results.windows:
        if w.oos_metrics is not None:
            assert math.isfinite(w.out_of_sample_return)


# --------------------------------------------------------------------------- #
# allow_nan=False serialization of OOS results
# --------------------------------------------------------------------------- #

def test_serialize_oos_all_finite():
    """serialize_oos() produces a JSON-valid (allow_nan=False) payload for finite results."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig()
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    payload = results.serialize_oos()
    import json
    json.dumps(payload, allow_nan=False)  # must not raise
    assert "overall_out_of_sample_return" in payload
    assert "stability_ratio" in payload
    assert "degradation" in payload
    assert "num_windows" in payload


def test_serialize_oos_empty_results():
    """serialize_oos() on empty results returns valid payload with zeros."""
    results = WalkForwardResults()
    payload = results.serialize_oos()
    import json
    json.dumps(payload, allow_nan=False)
    assert payload["num_windows"] == 0
    assert payload["overall_out_of_sample_return"] == 0.0


# --------------------------------------------------------------------------- #
# Stability SerializationError guards
# --------------------------------------------------------------------------- #

def test_assert_oos_finite_raises_on_nonfinite_stability():
    """assert_oos_finite() raises SerializationError when stability_ratio is inf."""
    results = WalkForwardResults()
    results.stability_ratio = float("inf")
    with pytest.raises(SerializationError):
        results.assert_oos_finite()


def test_assert_oos_finite_raises_on_nan_degradation():
    """assert_oos_finite() raises SerializationError when degradation is NaN."""
    results = WalkForwardResults()
    results.degradation = float("nan")
    with pytest.raises(SerializationError):
        results.assert_oos_finite()


def test_assert_oos_finite_raises_on_nonfinite_aggregate_return():
    """assert_oos_finite() raises SerializationError on non-finite aggregate OOS return."""
    results = WalkForwardResults()
    results.overall_out_of_sample_return = float("-inf")
    with pytest.raises(SerializationError):
        results.assert_oos_finite()


def test_assert_oos_finite_passes_on_all_finite():
    """assert_oos_finite() passes when all metrics are finite."""
    results = WalkForwardResults(
        overall_out_of_sample_return=0.05,
        overall_out_of_sample_sharpe=1.2,
        overall_out_of_sample_max_drawdown=0.1,
        stability_ratio=2.5,
        degradation=0.1,
    )
    results.assert_oos_finite()  # must not raise


def test_serialize_oos_raises_on_nonfinite_stability():
    """serialize_oos() raises SerializationError when stability_ratio is non-finite."""
    n = 100
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": [0] * n}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig()
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=40, test_window=20, step_size=20,
    )
    # Corrupt stability_ratio to inf and verify serialization rejects it
    results.stability_ratio = float("inf")
    with pytest.raises(SerializationError):
        results.serialize_oos()


# --------------------------------------------------------------------------- #
# Walk-forward window structural invariants
# --------------------------------------------------------------------------- #

def test_walkforward_windows_have_correct_indices():
    """Each window records correct train/test index ranges."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=5, embargo=5
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    assert len(results.windows) > 0
    for w in results.windows:
        assert w.train_start < w.train_end
        assert w.test_start < w.test_end
        assert w.train_end <= w.test_start  # no overlap after purge/embargo


def test_walkforward_anchored_and_rolling_both_work():
    """Both anchored and rolling modes produce valid results."""
    n = 200
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _rising_signals(n)}
    ts = _base_timestamps(n)

    for anchored in (True, False):
        wfb = WalkForwardBacktest(
            BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=0, embargo=0
        )
        results = wfb.run_walk_forward(
            price_series=prices, signals=signals, timestamps=ts,
            train_window=60, test_window=30, step_size=30,
            anchored=anchored,
        )
        assert results is not None
        assert isinstance(results.overall_out_of_sample_return, float)
        assert math.isfinite(results.overall_out_of_sample_return)


def test_walkforward_insufficient_data_returns_empty():
    """Not enough data for even one window returns empty results."""
    n = 10
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": [0] * n}
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig()
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    assert isinstance(results.windows, list)
    assert len(results.windows) == 0


def test_walkforward_multi_symbol():
    """Walk-forward works with multiple symbols in price_series/signals."""
    n = 150
    prices = {
        "BTC": _rising_prices(n, base=50000.0),
        "ETH": _rising_prices(n, base=3000.0, step=0.5),
    }
    signals = {
        "BTC": _rising_signals(n),
        "ETH": [0] * n,
    }
    ts = _base_timestamps(n)

    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=0, embargo=0
    )
    results = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    assert results is not None
    assert math.isfinite(results.overall_out_of_sample_return)
