"""Tests for EVAL-32 OOS validation of the marginal EVAL-31 GO."""
import math

import pytest

from src.analytics.integrated_options_orderflow_evaluation import (
    DEFAULT_MAX_POSITION_PCT,
    DEFAULT_N_POINTS,
    DEFAULT_PURGE,
    DEFAULT_EMBARGO,
    DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    DEFAULT_SIGNAL_THRESHOLD,
    DEFAULT_STEP_SIZE,
    DEFAULT_TEST_WINDOW,
    DEFAULT_TOXICITY_THRESHOLD,
    DEFAULT_TOXICITY_WINDOW_TRADES,
    DEFAULT_TRAIN_WINDOW,
    _build_bars,
    _causal_signal_series,
    _run_walkforward,
    _signal_positions,
    _toxicities_per_bar,
)
from src.analytics.options_time_varying_signal import align_options_signal_to_bars, load_snapshot_signals
from src.analytics.real_walkforward_certification import _cscv_pbo
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.analytics.capacity_aware_tca import (
    CapacityAwareSizer,
    DEFAULT_COST_BUDGET_BPS,
    DEFAULT_IMPACT_COEFF,
    DEFAULT_MAX_PARTICIPATION,
    DEFAULT_SPREAD_BPS,
)
from src.campaign.integrated import IntegratedConfig, load_real_orderflow

from scripts.eval32_oos_validation import (
    SPLIT_INDEX,
    evaluate_criteria,
    fuse_rule_a,
    gated_single_pillar,
    run_eval32,
)


def _full_series():
    snapshot = load_real_orderflow("BTC")
    bars = _build_bars(snapshot)
    signals = load_snapshot_signals("BTC")
    aligned = align_options_signal_to_bars(signals, bars["bar_ends_dt"])
    opt_series = [float(v) for v in aligned["signals"]]
    engine = OrderflowAlphaEngine(seed=42)
    of_series = _causal_signal_series(
        snapshot, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS, engine=engine,
    )
    of_sig = [float(s) for s in of_series["signals"]]
    toxicities = _toxicities_per_bar(
        snapshot, bars["bar_ends_dt"], window_trades=DEFAULT_TOXICITY_WINDOW_TRADES
    )
    return snapshot, bars, opt_series, of_sig, toxicities


def test_held_out_split_is_chronological_no_future_in_train():
    snapshot = load_real_orderflow("BTC")
    bars = _build_bars(snapshot)
    n = len(bars["bar_closes"])
    assert n == 1553
    # Train end must be strictly before held-out start in time.
    train_end = bars["bar_ends_dt"][SPLIT_INDEX - 1]
    held_out_start = bars["bar_ends_dt"][SPLIT_INDEX]
    assert train_end < held_out_start
    # Chronological ordering of the full bar series (no unsorted timestamps).
    ts = bars["bar_ends_dt"]
    assert all(ts[i] < ts[i + 1] for i in range(len(ts) - 1))
    # Held-out count matches handoff.
    assert n - SPLIT_INDEX == 466


def test_combined_positions_match_full_series_rule_a_sliced():
    _, bars, opt_series, of_sig, toxicities = _full_series()
    n = len(bars["bar_closes"])
    combined_full = fuse_rule_a(opt_series, of_sig, toxicities)
    sliced = combined_full[SPLIT_INDEX:]
    assert len(sliced) == n - SPLIT_INDEX
    # Slicing is exactly the tail of the full-series positions.
    assert sliced == [int(p) for p in combined_full[SPLIT_INDEX:]]
    # Rule A parity against an independent manual recomputation on the held-out tail.
    of_pos = _signal_positions(of_sig, threshold=DEFAULT_SIGNAL_THRESHOLD)
    manual = []
    for i in range(SPLIT_INDEX, n):
        tox = float(toxicities[i])
        opt = float(opt_series[i])
        if tox >= DEFAULT_TOXICITY_THRESHOLD or opt >= 0.0:
            manual.append(0)
        else:
            manual.append(int(of_pos[i]))
    assert manual == sliced


def test_walkforward_on_held_out_returns_keys_and_nine_windows():
    snapshot = load_real_orderflow("BTC")
    bars = _build_bars(snapshot)
    n = len(bars["bar_closes"])
    # deterministic alternating positions on the held-out slice
    pos = [1 if i % 20 < 10 else -1 for i in range(n - SPLIT_INDEX)]
    cfg = IntegratedConfig(seed=42, train_window=DEFAULT_TRAIN_WINDOW, test_window=DEFAULT_TEST_WINDOW,
                           step_size=DEFAULT_STEP_SIZE, purge=DEFAULT_PURGE, embargo=DEFAULT_EMBARGO)
    sizer = CapacityAwareSizer(DEFAULT_SPREAD_BPS, DEFAULT_IMPACT_COEFF, DEFAULT_MAX_PARTICIPATION,
                               DEFAULT_COST_BUDGET_BPS, seed=42)
    wf = _run_walkforward("BTC", bars["bar_closes"][SPLIT_INDEX:], pos,
                          bars["bar_ends_dt"][SPLIT_INDEX:], sizer, cfg, DEFAULT_N_POINTS, 42,
                          max_position_pct=DEFAULT_MAX_POSITION_PCT)
    for k in ("oos_sharpe", "oos_return", "oos_max_drawdown", "num_trades",
              "total_cost_usd", "total_traded_notional", "num_windows", "window_returns"):
        assert k in wf
    assert wf["num_windows"] == 9
    assert all(math.isfinite(float(x)) for x in wf["window_returns"])


def test_statistical_tests_execute_on_deterministic_fixture():
    # Execute the real primitives the script uses, on a deterministic fixture.
    from src.analytics.strategy_evaluation import block_bootstrap_ci, permutation_test

    def _sharpe(rets, pp=252.0):
        vals = [float(r) for r in rets if math.isfinite(float(r))]
        if len(vals) < 2:
            return 0.0
        m = sum(vals) / len(vals)
        sd = math.sqrt(sum((r - m) ** 2 for r in vals) / len(vals))
        return float(m / sd * math.sqrt(pp)) if sd > 0 else 0.0

    a = [0.01, -0.02, 0.03, 0.00, 0.04, -0.01, 0.02, 0.01, -0.03, 0.05]
    b = [0.00] * len(a)
    perm = permutation_test(a, b, statistic=lambda v: float(sum(v) / len(v)) if len(v) > 0 else 0.0,
                            n_permutations=200, paired=True, seed=42)
    assert 0.0 < perm["p_value"] <= 1.0
    point, lo, hi = block_bootstrap_ci(a, statistic=_sharpe, n_bootstrap=200, block_size=2, seed=42)
    assert math.isfinite(point) and lo <= hi


def test_pbo_k8_rejected_when_valid_combinations_zero():
    # 9 window returns per config; k_folds=8 requires n >= 16 -> 0 valid combos.
    rets = {"combined": [0.01, -0.01, 0.02, 0.0, 0.03, -0.02, 0.01, 0.0, 0.02],
            "flat": [0.0] * 9}
    invalid = _cscv_pbo(rets, n_combinations=16, k_folds=8)
    for cfg, det in invalid.get("config_details", {}).items():
        assert int(det.get("valid_combinations", 0)) == 0
    # k_folds=4 on 9 points -> valid combinations exist.
    valid = _cscv_pbo(rets, n_combinations=16, k_folds=4)
    assert int(valid.get("config_details", {}).get("combined", {}).get("valid_combinations", 0)) > 0


def test_predeclared_criteria_evaluated_correctly():
    # All pass.
    r = evaluate_criteria(combined_sharpe=0.5, combined_trades=10, best_control_sharpe=0.2,
                          perm_p=0.01, bootstrap_ci=(0.5, 0.3, 0.7),
                          pbo_combined=0.3, pbo_valid_combinations=4)
    assert r["all_pass"] is True
    assert r["validation_verdict"] == "GO"
    # Fails (b): permutation p >= 0.05.
    r = evaluate_criteria(combined_sharpe=0.5, combined_trades=10, best_control_sharpe=0.2,
                          perm_p=0.5, bootstrap_ci=(0.5, 0.3, 0.7),
                          pbo_combined=0.3, pbo_valid_combinations=4)
    assert r["all_pass"] is False and r["validation_verdict"] == "NO-GO"
    # Fails (d): PBO valid_combinations == 0 -> FAIL regardless of pbo value.
    r = evaluate_criteria(combined_sharpe=0.5, combined_trades=10, best_control_sharpe=0.2,
                          perm_p=0.01, bootstrap_ci=(0.5, 0.3, 0.7),
                          pbo_combined=0.0, pbo_valid_combinations=0)
    assert r["criteria"]["d_pbo_combined_lt_0_5_valid"] is False
    assert r["all_pass"] is False
    # Fails (a): no trades.
    r = evaluate_criteria(combined_sharpe=0.5, combined_trades=0, best_control_sharpe=0.2,
                          perm_p=0.01, bootstrap_ci=(0.5, 0.3, 0.7),
                          pbo_combined=0.3, pbo_valid_combinations=4)
    assert r["criteria"]["a_combined_superior_and_trades"] is False
    # Fails (c): bootstrap CI includes zero.
    r = evaluate_criteria(combined_sharpe=0.05, combined_trades=10, best_control_sharpe=0.0,
                          perm_p=0.01, bootstrap_ci=(0.05, -0.1, 0.2),
                          pbo_combined=0.3, pbo_valid_combinations=4)
    assert r["criteria"]["c_bootstrap_ci_excludes_zero"] is False


def test_run_eval32_no_write_executes_and_returns_consistent_verdict():
    report = run_eval32(write=False)
    assert report["verdict"] in ("GO", "NO-GO")
    assert report["walkforward_held_out"]["num_windows_by_config"]["combined"] == 9
    assert report["split"]["n_bars_total"] == 1553
    assert report["split"]["held_out_n_bars"] == 466
    # verdict must equal all four criteria passing.
    assert (report["validation_criteria"]["all_pass"]) == (report["verdict"] == "GO")