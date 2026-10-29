"""Adversarial stress tests for the backtesting engine (Phase 5).

Covers deterministic gap-down, sustained crash, volatility-spike whipsaw, and
liquidity-crunch (partial fills / round lots / slippage cap) scenarios with
strict no-lookahead, numerical stability, and allow_nan=False serialization
safety.
"""

from src.backtest.engine import (
    StressScenario,
    StressTestResult,
    all_stress_scenarios,
    crash_scenario,
    gap_down_scenario,
    liquidity_crunch_scenario,
    run_deterministic_stress_suite,
    run_stress_scenario,
    vol_spike_scenario,
)


def test_stress_suite_all_scenarios_pass():
    results = run_deterministic_stress_suite()
    assert len(results) == 4
    names = {r.name for r in results}
    assert names == {"crash", "gap_down", "vol_spike", "liquidity_crunch"}
    for r in results:
        assert r.passed, f"{r.name} failed: {r.violations}"
        assert r.finite, f"{r.name} non-finite: {r.violations}"
        assert r.serializable, f"{r.name} not serializable: {r.violations}"


def test_crash_bounds_drawdown_and_stays_finite():
    r = run_stress_scenario(crash_scenario())
    assert r.passed, r.violations
    assert r.max_drawdown <= 0.2 + 1e-9
    assert r.finite and r.serializable


def test_gap_down_closes_position_and_stays_finite():
    r = run_stress_scenario(gap_down_scenario())
    assert r.passed, r.violations
    assert r.positions_flat
    assert r.finite and r.serializable


def test_vol_spike_turnover_stable():
    r = run_stress_scenario(vol_spike_scenario())
    assert r.passed, r.violations
    assert r.total_trades > 0
    assert r.finite and r.serializable


def test_liquidity_crunch_partial_fills_and_round_lots():
    r = run_stress_scenario(liquidity_crunch_scenario())
    assert r.passed, r.violations
    assert r.finite and r.serializable


def test_stress_suite_deterministic_repeat_matches():
    first = run_deterministic_stress_suite()
    second = run_deterministic_stress_suite()
    assert len(first) == len(second)
    for a, b in zip(first, second):
        assert a.name == b.name
        assert a.passed == b.passed
        assert a.total_return == b.total_return
        assert a.max_drawdown == b.max_drawdown
        assert a.sharpe_ratio == b.sharpe_ratio
        assert a.total_trades == b.total_trades
        assert a.equity_final == b.equity_final
        assert a.violations == b.violations
