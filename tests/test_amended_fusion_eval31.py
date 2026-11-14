"""Tests for EVAL-31 amended fusion (time-varying options + causal orderflow)."""
import math
from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.analytics.capacity_aware_tca import (
    CapacityAwareSizer,
    DEFAULT_COST_BUDGET_BPS,
    DEFAULT_IMPACT_COEFF,
    DEFAULT_MAX_PARTICIPATION,
    DEFAULT_SPREAD_BPS,
)
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
from src.campaign.integrated import IntegratedConfig, load_real_orderflow

from scripts.eval31_amended_fusion import fuse_rule_a, gated_single_pillar


def test_fuse_rule_a_matches_declared_mechanism():
    # options negative -> allow orderflow direction; options >=0 -> flat; tox gate -> flat
    options = [-0.05, -0.02, 0.01, -0.03, -0.03]
    orderflow = [0.5, -0.5, 0.5, 0.5, -0.5]  # signs +1,-1,+1,+1,-1 at threshold 0.1
    tox = [0.1, 0.1, 0.1, 0.8, 0.1]
    pos = fuse_rule_a(options, orderflow, tox, threshold=0.1, tox_threshold=0.7)
    # i=0: opt<0,tox ok -> +1; i=1: -1; i=2: opt>=0 -> 0; i=3: tox>=0.7 -> 0; i=4: -1
    assert pos == [1, -1, 0, 0, -1]


def test_causality_no_lookahead_bar_uses_snapshot_le_bar_end():
    signals = load_snapshot_signals("BTC")
    snapshot = load_real_orderflow("BTC")
    bars = _build_bars(snapshot)
    aligned = align_options_signal_to_bars(signals, bars["bar_ends_dt"])
    series = aligned["signals"]
    # Parse snapshot times
    stamps = [datetime.fromisoformat(s.snapshot_timestamp.replace("Z", "+00:00")) for s in signals]
    sigvals = [float(s.options_signal_raw) for s in signals]
    # For a sample of bars, verify value equals newest snapshot <= bar_end (or 0)
    for i in [0, 100, 500, 1000, len(series)-1]:
        end = bars["bar_ends_dt"][i]
        chosen = 0.0
        for idx in range(len(stamps)-1, -1, -1):
            if stamps[idx] <= end:
                chosen = sigvals[idx]
                break
        assert abs(series[i] - chosen) < 1e-12, (i, series[i], chosen)
    # Must have step changes (time-varying, not future-peeking constant broadcast artifact)
    assert aligned["step_changes"] == 2
    assert aligned["n_flat_bars"] == 1300  # bars before first snapshot


def test_toxicity_gate_forces_flat_at_threshold():
    options = [-0.05] * 5
    orderflow = [0.5] * 5
    tox = [0.0, 0.69, 0.7, 0.99, 1.0]
    pos = fuse_rule_a(options, orderflow, tox, threshold=0.1, tox_threshold=0.7)
    assert pos == [1, 1, 0, 0, 0]


def test_run_walkforward_deterministic_fixture_returns_required_keys():
    snapshot = load_real_orderflow("BTC")
    bars = _build_bars(snapshot)
    # short deterministic fixture: use last 300 bars subset logic via positions same length
    prices = bars["bar_closes"]
    ts = bars["bar_ends_dt"]
    # deterministic alternating positions
    pos = [1 if i % 20 < 10 else -1 for i in range(len(prices))]
    cfg = IntegratedConfig(seed=42, train_window=DEFAULT_TRAIN_WINDOW, test_window=DEFAULT_TEST_WINDOW,
                           step_size=DEFAULT_STEP_SIZE, purge=DEFAULT_PURGE, embargo=DEFAULT_EMBARGO)
    sizer = CapacityAwareSizer(DEFAULT_SPREAD_BPS, DEFAULT_IMPACT_COEFF, DEFAULT_MAX_PARTICIPATION,
                               DEFAULT_COST_BUDGET_BPS, seed=42)
    wf = _run_walkforward("BTC", prices, pos, ts, sizer, cfg, DEFAULT_N_POINTS, 42,
                          max_position_pct=DEFAULT_MAX_POSITION_PCT)
    for k in ("oos_sharpe", "oos_return", "oos_max_drawdown", "num_trades", "total_cost_usd",
              "total_traded_notional", "num_windows", "window_returns"):
        assert k in wf
    assert wf["num_windows"] == 36
    assert all(math.isfinite(float(x)) for x in wf["window_returns"])


def test_component_parity_gated_single_pillar_deterministic():
    snapshot = load_real_orderflow("BTC")
    bars = _build_bars(snapshot)
    engine = OrderflowAlphaEngine(seed=42)
    of_series = _causal_signal_series(snapshot, bars["bar_ends_dt"], bars["bar_closes"],
                                      lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS, engine=engine)
    of_sig = [float(s) for s in of_series["signals"]]
    toxicities = _toxicities_per_bar(snapshot, bars["bar_ends_dt"], window_trades=DEFAULT_TOXICITY_WINDOW_TRADES)
    pos = gated_single_pillar(of_sig, toxicities)
    # Manual parity check
    raw = _signal_positions(of_sig, threshold=DEFAULT_SIGNAL_THRESHOLD)
    manual = [0 if float(toxicities[i]) >= DEFAULT_TOXICITY_THRESHOLD else int(raw[i]) for i in range(len(raw))]
    assert pos == manual
    assert sum(1 for p in pos if p != 0) > 0  # not degenerate on this data
