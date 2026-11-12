"""Numeric-invariant tests for src/analytics/strategy_falsification.py (EVAL-06).

Asserts real mathematical properties: determinism, nonzero windows/trades/return,
bootstrap CI containment, p-value range, deflated-Sharpe finiteness, net =
gross minus cost within tolerance, monotonic cost grid, and the engine invariant
that nonzero trades cannot yield a 0.0 aggregate OOS return unless every window
truly had 0.0 return. Never asserts ``valid=true``.
"""

from __future__ import annotations

import math

import pytest

from src.analytics.strategy_falsification import (
    COST_GRID_BPS,
    evaluate_strategy_falsification,
)
from src.backtest.engine import BacktestConfig, RiskConfig, WalkForwardBacktest


def _base_timestamps(n: int, start=None):
    from datetime import datetime, timedelta, timezone

    if start is None:
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return [start + timedelta(hours=i) for i in range(n)]


def _rising_prices(n: int, base: float = 50000.0, step: float = 5.0) -> list:
    return [base + i * step for i in range(n)]


def _trade_signals(n: int) -> list:
    return [1 if i % 10 < 5 else (-1 if i % 20 == 19 else 0) for i in range(n)]


def _evaluate(seeds, n_points=240, train_window=60, test_window=20, step_size=20, permutations=25):
    return evaluate_strategy_falsification(
        seeds=seeds,
        n_points=n_points,
        train_window=train_window,
        test_window=test_window,
        step_size=step_size,
        purge=0,
        embargo=0,
        n_permutations=permutations,
    )


def test_falsification_is_deterministic_across_runs():
    """Two evaluations with identical inputs must produce byte-identical reports."""
    r1 = _evaluate(seeds=[3, 4], permutations=25)
    r2 = _evaluate(seeds=[3, 4], permutations=25)
    r1.pop("generated_at", None)
    r2.pop("generated_at", None)
    assert r1 == r2
    assert r1["verdict"] in ("GO", "NO-GO")
    assert r1["never_valid_true"] is True
    assert "valid" not in r1 or r1.get("valid") is not True


def test_falsification_numeric_invariants_per_seed():
    """Per-seed numeric invariants required by the EVAL-06 exit gate."""
    report = _evaluate(seeds=[5, 6], permutations=25)
    bps_values = [int(b) for b in COST_GRID_BPS]
    for r in report["per_seed"]:
        assert r["track_record"]["admissible"] is True
        assert r["track_record"]["num_windows"] > 0
        # Nonzero OOS return for every symbol at the net baseline.
        for sym, sres in r["symbols"].items():
            assert sres["num_windows"] > 0
            assert sres["oos_trade_count"] > 0, f"seed {r['seed']} symbol {sym} has zero trades"
            assert sres["oos_return"] != 0.0, f"seed {r['seed']} symbol {sym} has zero net return"
            assert math.isfinite(sres["oos_sharpe"])
            assert math.isfinite(sres["oos_max_drawdown"])
        net = r["net"]
        gross = r["gross"]
        assert net["num_windows"] > 0
        assert net["oos_trade_count"] > 0
        assert math.isfinite(net["oos_return"])
        assert math.isfinite(net["oos_sharpe"])
        assert math.isfinite(r["deflated_sharpe"])
        # p-value in [0, 1]
        pv = r["permutation"]["p_value_return"]
        assert 0.0 <= pv <= 1.0
        pv_s = r["permutation"]["p_value_sharpe"]
        assert 0.0 <= pv_s <= 1.0
        # Bootstrap CI contains the point estimate.
        ci_ret = r["bootstrap_ci"]["mean_net_return"]
        assert ci_ret["lo"] <= ci_ret["point"] <= ci_ret["hi"]
        ci_sh = r["bootstrap_ci"]["net_sharpe"]
        assert ci_sh["lo"] <= ci_sh["point"] <= ci_sh["hi"]
        # Cost grid monotonicity: net return does not increase with bps.
        grid_returns = []
        for b in bps_values:
            grid_returns.append((b, r["cost_grid"][str(b)]["oos_return"]))
        for i in range(len(grid_returns) - 1):
            assert grid_returns[i][1] >= grid_returns[i + 1][1] - 1e-12
        # Net return at 0 bps equals gross return exactly.
        assert abs(r["cost_grid"]["0"]["oos_return"] - gross["oos_return"]) < 1e-12
        # Net return = gross - cost within tolerance for bps > 0.
        for b in bps_values[1:]:
            net_bps = r["cost_grid"][str(b)]["oos_return"]
            # Per-symbol traded notional at this cost level.
            total_notional = 0.0
            total_trades = 0
            for sym in ("BTC", "ETH", "SOL"):
                sres = r["symbols"][sym]
                total_notional += sres["traded_notional"]
                total_trades += sres["oos_trade_count"]
            capital = 100000.0
            est_cost = (b / 10000.0) * total_notional / capital
            diff = gross["oos_return"] - net_bps
            assert diff >= -1e-9, f"cost increased return at {b} bps: {diff}"
            assert diff <= est_cost + 0.01 + 1e-6, (
                f"cost gap too large at {b} bps: diff={diff}, est_cost={est_cost}"
            )


def test_falsification_cost_grid_reports_all_levels():
    """Cost grid covers 0 / 1 / 5 / 10 bps with net Sharpe at each level."""
    report = _evaluate(seeds=[1], permutations=25)
    assert set(report["cost_grid"].keys()) == {str(b) for b in COST_GRID_BPS}
    for b in COST_GRID_BPS:
        entry = report["cost_grid"][str(b)]
        assert entry["bps"] == float(b)
        assert math.isfinite(entry["mean_net_sharpe"])
        assert math.isfinite(entry["mean_net_return"])


def test_falsification_has_regime_conditioned_performance():
    """Regime-conditioned performance is reported for path regimes."""
    report = _evaluate(seeds=[2], permutations=25)
    for r in report["per_seed"]:
        rc = r["regime_conditioned"]
        assert isinstance(rc, dict) and len(rc) > 0
        for regime, perf in rc.items():
            assert regime in ("trend", "range", "high_vol_chop", "thin")
            assert math.isfinite(perf["mean_return"])
            assert math.isfinite(perf["sharpe"])
            assert perf["num_windows"] > 0
        # Regime-dependent cost profile present.
        cp = r["regime_cost_profile"]
        assert isinstance(cp, dict) and len(cp) > 0
        for v in cp.values():
            assert math.isfinite(v["effective_cost_bps_net_baseline"])


def test_engine_aggregate_nonzero_trades_implies_nonzero_return():
    """Engine invariant: nonzero trades cannot produce a 0.0 aggregate return
    unless every window truly had 0.0 return."""
    n = 240
    prices = {"BTC": _rising_prices(n)}
    signals = {"BTC": _trade_signals(n)}
    ts = _base_timestamps(n)
    wfb = WalkForwardBacktest(
        BacktestConfig(initial_capital=100000.0), RiskConfig(), purge=0, embargo=0
    )
    res = wfb.run_walk_forward(
        price_series=prices, signals=signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    assert len(res.windows) > 0
    assert len(res.oos_trades) > 0
    assert res.overall_out_of_sample_return != 0.0
    # Chained aggregate equals compounding of per-window returns.
    compounded = 1.0
    for w in res.windows:
        compounded *= 1.0 + w.out_of_sample_return
    assert abs(res.overall_out_of_sample_return - (compounded - 1.0)) < 1e-12
    # Flat signals: trades may still occur on exit, but every window return 0.0
    # implies a 0.0 aggregate return.
    flat_signals = {"BTC": [0] * n}
    res_flat = wfb.run_walk_forward(
        price_series=prices, signals=flat_signals, timestamps=ts,
        train_window=60, test_window=30, step_size=30,
    )
    window_returns = [w.out_of_sample_return for w in res_flat.windows]
    assert all(r == 0.0 for r in window_returns)
    assert res_flat.overall_out_of_sample_return == 0.0


def test_falsification_cli_entry_point_runs():
    """The module CLI runs end-to-end on a small configuration."""
    from src.analytics.strategy_falsification import main

    code = main(["--seeds", "1", "2", "--n-points", "240", "--train-window", "60",
                 "--test-window", "20", "--step-size", "20", "--permutations", "25"])
    assert code == 0
