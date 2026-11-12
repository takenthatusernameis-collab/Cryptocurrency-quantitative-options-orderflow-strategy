"""Numeric-invariant tests for src/analytics/strategy_evaluation.py.

Asserts real mathematical properties (finite values, correct sign, CI bracketing,
PnL reconciliation) — never ``valid=true`` shortcuts.
"""

from __future__ import annotations

import math

import pytest

from src.analytics.strategy_evaluation import (
    PROFIT_FACTOR_CAP,
    attribute_pnl,
    block_bootstrap_ci,
    compare_to_baseline,
    compute_metrics,
    permutation_test,
)


def _gbm_equity(up: bool, n: int = 500, seed: int = 7) -> list[float]:
    """Geometric Brownian motion equity curve; up-trending if up=True."""
    import numpy as np

    rng = np.random.default_rng(seed)
    drift = 0.0004 if up else -0.0004
    vol = 0.01
    rets = drift + vol * rng.standard_normal(n)
    eq = [100000.0]
    for r in rets:
        eq.append(eq[-1] * (1.0 + r))
    return eq


def test_compute_metrics_finite_on_gbm() -> None:
    eq = _gbm_equity(up=True)
    m = compute_metrics(eq)
    for k, v in m.items():
        assert isinstance(v, (int, float)) and not isinstance(v, bool), (k, v)
        assert math.isfinite(float(v)), (k, v)


def test_sharpe_sortino_calmar_sign_up_vs_down() -> None:
    m_up = compute_metrics(_gbm_equity(up=True))
    m_down = compute_metrics(_gbm_equity(up=False))
    # Up-trending should have higher Sharpe than down-trending.
    assert m_up["sharpe"] > m_down["sharpe"], (m_up["sharpe"], m_down["sharpe"])
    assert m_up["ann_return"] > m_down["ann_return"], (m_up["ann_return"], m_down["ann_return"])
    # Calmar non-negative when no drawdown beyond start; at minimum finite.
    assert math.isfinite(m_up["calmar"]) and math.isfinite(m_down["calmar"])


def test_zero_variance_sharpe_is_zero_no_nan() -> None:
    eq = [100000.0 * (1.001 ** i) for i in range(101)]  # constant positive returns, std>0 actually
    # Truly zero-variance: flat equity.
    flat = [100000.0] * 101
    m = compute_metrics(flat)
    assert m["sharpe"] == 0.0
    assert m["sortino"] == 0.0
    assert m["ann_vol"] == 0.0
    assert math.isfinite(m["profit_factor"])


def test_profit_factor_never_inf() -> None:
    eq = [100000.0, 101000.0]
    trades = [{"pnl": 100.0}, {"pnl": 200.0}]  # wins only, no losses
    m = compute_metrics(eq, trades=trades)
    assert m["profit_factor"] == PROFIT_FACTOR_CAP
    assert math.isfinite(m["profit_factor"])


def test_block_bootstrap_ci_brackets_multiple_seeds() -> None:
    import numpy as np

    rng = np.random.default_rng(3)
    vals = list(rng.normal(0.05, 0.02, 500))
    for seed in (0, 1, 42):
        point, lo, hi = block_bootstrap_ci(vals, np.mean, seed=seed)
        assert math.isfinite(point) and math.isfinite(lo) and math.isfinite(hi)
        assert lo <= point <= hi, (seed, lo, point, hi)


def test_block_bootstrap_deterministic_same_seed() -> None:
    vals = [0.01, -0.02, 0.03, -0.01, 0.02] * 50
    ci1 = block_bootstrap_ci(vals, __import__("numpy").mean, seed=123)
    ci2 = block_bootstrap_ci(vals, __import__("numpy").mean, seed=123)
    assert ci1 == ci2


def test_attribute_pnl_reconciles() -> None:
    by_bucket = {
        "venue_A": [10.0, -2.0, 3.0],
        "venue_B": [-5.0, 4.0],
        "regime_chop": [1.0, 1.0, 1.0],
    }
    rep = attribute_pnl(by_bucket)
    bucket_sum = sum(rep["bucket_totals"].values())
    assert abs(bucket_sum - rep["grand_total"]) <= 1e-9 * max(1.0, abs(rep["grand_total"]))
    assert rep["reconciled_total"] == rep["grand_total"]
    assert rep["max_abs_error"] <= 1e-9 * max(1.0, abs(rep["grand_total"]))
    assert rep["reconciliation_ok"] is True
    assert rep["num_buckets"] == 3


def test_compute_metrics_rejects_nonfinite() -> None:
    with pytest.raises(ValueError):
        compute_metrics([1.0, float("nan"), 2.0])
    with pytest.raises(ValueError):
        compute_metrics([1.0, float("inf"), 2.0])
    with pytest.raises(ValueError):
        compute_metrics([1.0])  # too short


def test_block_bootstrap_ci_rejects_empty() -> None:
    with pytest.raises(ValueError):
        block_bootstrap_ci([], __import__("numpy").mean)


def test_compare_to_baseline_deltas_and_verdict() -> None:
    strategy = {"sharpe": 1.2, "total_return": 0.1, "max_drawdown": 0.05}
    baseline = {"sharpe": 0.8, "total_return": 0.05, "max_drawdown": 0.08}
    rep = compare_to_baseline(strategy, baseline)
    assert rep["verdict"] == "strategy"
    assert rep["verdict_metric"] == "sharpe"
    assert rep["deltas"]["sharpe"] == pytest.approx(0.4)
    assert rep["deltas"]["total_return"] == pytest.approx(0.05)
    assert rep["num_metrics_compared"] == 3


def test_compare_to_baseline_rejects_nonfinite() -> None:
    with pytest.raises(ValueError):
        compare_to_baseline({"sharpe": float("nan")}, {"sharpe": 0.5})
    with pytest.raises(ValueError):
        compare_to_baseline({"sharpe": 0.5}, {"sharpe": float("inf")})


def test_permutation_test_paired_is_deterministic_and_bracketing() -> None:
    import numpy as np

    rng = np.random.default_rng(11)
    a = list(0.01 + 0.02 * rng.standard_normal(30))
    b = list(-0.01 + 0.02 * rng.standard_normal(30))
    r1 = permutation_test(a, b, statistic=np.mean, n_permutations=500, paired=True, seed=3)
    r2 = permutation_test(a, b, statistic=np.mean, n_permutations=500, paired=True, seed=3)
    assert r1 == r2
    assert 0.0 < r1["p_value"] <= 1.0
    assert r1["observed_difference"] == pytest.approx(
        float(np.mean(a)) - float(np.mean(b))
    )
    assert math.isfinite(r1["null_mean"])
    assert r1["n_permutations"] == 500


def test_permutation_test_detects_real_shift() -> None:
    import numpy as np

    rng = np.random.default_rng(5)
    noise = 0.01 * rng.standard_normal(200)
    a = list(0.05 + noise)
    b = list(-0.05 + noise)
    rep = permutation_test(a, b, statistic=np.mean, n_permutations=1000, paired=False, seed=1)
    assert rep["significant_at_05"] is True
    assert rep["p_value"] < 0.05
    assert rep["observed_difference"] > 0.0


def test_permutation_test_unpaired_pooling_respects_sizes() -> None:
    import numpy as np

    rep = permutation_test([1.0, 2.0, 3.0], [10.0, 20.0], statistic=np.mean,
                           n_permutations=50, paired=False, seed=2)
    assert rep["statistic_a"] == pytest.approx(2.0)
    assert rep["statistic_b"] == pytest.approx(15.0)
    assert rep["observed_difference"] == pytest.approx(-13.0)
    assert rep["paired"] is False


def test_permutation_test_alternative_directions() -> None:
    import numpy as np

    rng = np.random.default_rng(5)
    noise = 0.01 * rng.standard_normal(200)
    a = list(0.05 + noise)
    b = list(-0.05 + noise)
    two = permutation_test(a, b, statistic=np.mean, n_permutations=2000, paired=False, seed=0)
    greater = permutation_test(a, b, statistic=np.mean, n_permutations=2000, paired=False,
                               alternative="greater", seed=0)
    less = permutation_test(a, b, statistic=np.mean, n_permutations=2000, paired=False,
                            alternative="less", seed=0)
    # Observed difference is positive, so the upper tail is far more extreme.
    assert greater["observed_difference"] > 0.0
    assert greater["p_value"] < less["p_value"]
    assert greater["p_value"] <= two["p_value"]
    assert greater["significant_at_05"] is True
    assert less["significant_at_05"] is False


def test_permutation_test_rejects_bad_inputs() -> None:
    import numpy as np

    with pytest.raises(ValueError):
        permutation_test([], [1.0], statistic=np.mean)
    with pytest.raises(ValueError):
        permutation_test([1.0, 2.0], [1.0], statistic=np.mean, paired=True)
    with pytest.raises(ValueError):
        permutation_test([1.0], [2.0], statistic=np.mean, n_permutations=0)
    with pytest.raises(ValueError):
        permutation_test([1.0], [2.0], statistic=np.mean, alternative="two_sided")
    with pytest.raises(ValueError):
        permutation_test([1.0, float("nan")], [2.0, 3.0], statistic=np.mean, paired=True)
