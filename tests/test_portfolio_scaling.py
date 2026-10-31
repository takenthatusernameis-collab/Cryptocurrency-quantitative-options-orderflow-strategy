"""Tests for portfolio scaling with constraints (turnover cap, vol-target / risk-parity).

Covers: turnover cap enforcement (breach scaled/rejected, finite), vol-target and
risk-parity weights finite and (respectively) sum <= 1 / sum == 1, allocation
stability across regimes, no-lookahead (weights derived only from the train
window), strict serialization allow_nan=False, and determinism (run twice
identical). All allocation math is computed on in-sample/train data only and
applied out-of-sample.
"""

import json
import math
import random
from datetime import datetime, timedelta, timezone

import pytest

from src.backtest.engine import (
    PortfolioWalkForwardBacktest,
    PortfolioWalkForwardResults,
    run_portfolio_walk_forward,
)
from src.telemetry.serialization import serialize_metrics_strict


def _make_prices(n: int = 300, seed: int = 7) -> dict:
    random.seed(seed)
    factors = [100.0]
    for i in range(1, n):
        factors.append(factors[-1] * (1.0 + random.gauss(0.0002, 0.012)))
    prices = {}
    for sym, b, beta in [("BTC", 100.0, 0.4), ("ETH", 50.0, 0.7), ("SOL", 20.0, 0.9)]:
        series = [b]
        for i in range(1, n):
            ret = beta * (factors[i] / factors[i - 1] - 1.0) + (1.0 - beta) * random.gauss(0.0002, 0.015)
            series.append(series[-1] * (1.0 + ret))
        prices[sym] = series
    return prices


def _make_signals(price_series: dict, every: int = 20) -> dict:
    n = len(next(iter(price_series.values())))
    signals = {s: [0] * n for s in price_series}
    for i in range(60, n - 30, every):
        for s in signals:
            signals[s][i] = 1
    return signals


_BASE = dict(train_window=70, test_window=30, step_size=30, purge=3, embargo=2, correlation_constraint=True)


def _run(mode: str, **kw):
    pwfb = PortfolioWalkForwardBacktest(allocation_mode=mode, **kw)
    res = pwfb.run_portfolio_walk_forward(_make_prices(), signals=_make_signals(_make_prices()), **_BASE)
    res.assert_oos_finite()
    serialize_metrics_strict(res.serialize_oos())
    return res


def test_risk_parity_weights_sum_to_one_and_finite():
    res = _run("risk_parity")
    assert len(res.windows) >= 1
    for w in res.windows:
        assert w.allocation_weights is not None
        wsum = sum(w.allocation_weights.values())
        assert abs(wsum - 1.0) < 1e-9, wsum
        for s, v in w.allocation_weights.items():
            assert math.isfinite(v) and v >= 0.0, (s, v)
        assert w.allocation_mode == "risk_parity"


def test_equal_weight_weights_sum_to_one_and_finite():
    res = _run("equal_weight")
    for w in res.windows:
        assert w.allocation_weights is not None
        assert abs(sum(w.allocation_weights.values()) - 1.0) < 1e-9
        for v in w.allocation_weights.values():
            assert math.isfinite(v) and v >= 0.0


def test_vol_target_weights_finite_sum_le_one_cash_buffer():
    res = _run("vol_target", vol_target=0.001)  # tiny target forces heavy de-risking
    for w in res.windows:
        assert w.allocation_weights is not None
        wsum = sum(w.allocation_weights.values())
        assert 0.0 < wsum <= 1.0 + 1e-9, wsum  # cash buffer allowed, no leverage
        for v in w.allocation_weights.values():
            assert math.isfinite(v) and v >= 0.0, v


def test_turnover_cap_enforcement_breach_scaled_to_cap():
    # Natural turnover exceeds 0.02 -> must be scaled down to the cap.
    res = _run("risk_parity", turnover_cap=0.02)
    for w in res.windows:
        assert w.turnover <= 0.020001, (w.turnover, "turnover cap breached")
        assert math.isfinite(w.turnover)
        assert abs(sum(w.allocation_weights.values()) - 1.0) < 1e-9


def test_turnover_cap_under_cap_unchanged():
    # Natural turnover below 0.5 -> cap not binding, weights still sum to 1.
    res = _run("risk_parity", turnover_cap=0.5)
    for w in res.windows:
        assert w.turnover <= 0.5 + 1e-9
        assert math.isfinite(w.turnover)
        assert abs(sum(w.allocation_weights.values()) - 1.0) < 1e-9


def test_no_lookahead_weights_derived_from_train_only():
    prices = _make_prices()
    signals = _make_signals(prices)
    pwfb = PortfolioWalkForwardBacktest(allocation_mode="risk_parity")
    res = pwfb.run_portfolio_walk_forward(prices, signals=signals, **_BASE)
    # Recompute expected risk-parity weights for the first window from train data
    # only and confirm they match what was applied out-of-sample.
    first = res.windows[0]
    ts, te = first.train_start, first.train_end
    # The engine purges the tail of the train window adjacent to the test set
    # before computing allocation weights (no lookahead; train data only).
    purge = 3
    te_purged = max(ts, te - purge)
    seg = {s: prices[s][ts:te_purged] for s in prices}
    vols = {}
    for s, p in seg.items():
        rets = []
        for i in range(1, len(p)):
            p0, p1 = p[i - 1], p[i]
            if p0 != 0:
                r = (p1 / p0) - 1.0
                if math.isfinite(r):
                    rets.append(r)
        if len(rets) >= 2:
            m = sum(rets) / len(rets)
            var = sum((r - m) ** 2 for r in rets) / len(rets)
            vols[s] = math.sqrt(max(var, 0.0))
        else:
            vols[s] = 0.0
    inv = {s: (1.0 / v if v > 0 else 0.0) for s, v in vols.items()}
    tot = sum(inv.values())
    expected = {s: (inv[s] / tot if tot > 0 else 1.0 / len(prices)) for s in prices}
    for s, v in expected.items():
        assert math.isfinite(first.allocation_weights.get(s, 0.0))
        assert abs(first.allocation_weights.get(s, 0.0) - v) < 1e-9, (s, first.allocation_weights.get(s), v)


def test_allocation_stability_across_regimes():
    prices = _make_prices()
    signals = _make_signals(prices)
    # Same allocation inputs under different regime labels must produce identical
    # weights (regime label affects cost multiplier, not the allocation math).
    kw = dict(train_window=70, test_window=30, step_size=30, purge=3, embargo=2, correlation_constraint=True)
    res_normal = PortfolioWalkForwardBacktest(allocation_mode="risk_parity").run_portfolio_walk_forward(
        prices, signals=signals, regime="normal", **kw
    )
    res_stress = PortfolioWalkForwardBacktest(allocation_mode="risk_parity").run_portfolio_walk_forward(
        prices, signals=signals, regime="stress", **kw
    )
    assert len(res_normal.windows) == len(res_stress.windows)
    for wn, ws in zip(res_normal.windows, res_stress.windows):
        for s in prices:
            assert wn.allocation_weights.get(s) == ws.allocation_weights.get(s), s


def test_serialization_allow_nan_false_strict():
    res = _run("risk_parity")
    payload = serialize_metrics_strict(res.serialize_oos())
    out = json.dumps(payload, allow_nan=False)
    assert "NaN" not in out and "Infinity" not in out and "-Infinity" not in out


def test_determinism_run_twice_identical():
    prices = _make_prices()
    signals = _make_signals(prices)
    kw = dict(train_window=70, test_window=30, step_size=30, purge=3, embargo=2, correlation_constraint=True)
    pwfb = PortfolioWalkForwardBacktest(allocation_mode="vol_target", vol_target=0.1, turnover_cap=0.3)
    r1 = pwfb.run_portfolio_walk_forward(prices, signals=signals, **kw)
    r2 = pwfb.run_portfolio_walk_forward(prices, signals=signals, **kw)
    assert r1.serialize_oos() == r2.serialize_oos()
    assert len(r1.windows) == len(r2.windows)
    for w1, w2 in zip(r1.windows, r2.windows):
        assert w1.allocation_weights == w2.allocation_weights
        assert w1.turnover == w2.turnover
        assert w1.out_of_sample_return == w2.out_of_sample_return


def test_allocation_weights_applied_out_of_sample_and_finite():
    res = _run("risk_parity")
    for w in res.windows:
        assert w.allocation_weights is not None
        assert math.isfinite(w.out_of_sample_return)
        assert math.isfinite(w.out_of_sample_sharpe)
        assert math.isfinite(w.out_of_sample_max_drawdown)


def test_invalid_allocation_mode_falls_back_safe():
    prices = _make_prices()
    signals = _make_signals(prices)
    pwfb = PortfolioWalkForwardBacktest(allocation_mode="bogus_mode")
    res = pwfb.run_portfolio_walk_forward(prices, signals=signals, **_BASE)
    res.assert_oos_finite()
    for w in res.windows:
        assert abs(sum(w.allocation_weights.values()) - 1.0) < 1e-9


@pytest.mark.parametrize("mode", ["equal_weight", "risk_parity", "vol_target"])
def test_all_modes_green_and_serializable(mode):
    res = _run(mode) if mode != "vol_target" else _run("vol_target", vol_target=0.05)
    assert isinstance(res, PortfolioWalkForwardResults)
    res.assert_oos_finite()
    s = serialize_metrics_strict(res.serialize_oos())
    assert math.isfinite(s["overall_out_of_sample_return"])
    assert math.isfinite(s["overall_out_of_sample_sharpe"])
