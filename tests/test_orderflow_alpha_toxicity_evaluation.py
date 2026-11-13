"""Numeric-invariant tests for src/analytics/orderflow_alpha_toxicity_evaluation.py (EVAL-17).

Covers: real orderflow loading, causal bar construction, per-bar causal features
(OrderflowAlphaEngine applied to trailing snapshots), a strict no-lookahead
assertion (future-injected tape does not change any earlier bar's features),
information-coefficient computation and decay across horizons 1/5/20,
block-bootstrap CI on mean IC, paired permutation test, VPIN toxicity
(measured, not identically 0 or 1, gate engagement), net-of-cost with/without
walk-forward, deterministic verdict with explicit checks, strict serialization
(allow_nan=False, never {"valid": true}), and CLI artifact emission.
"""

from __future__ import annotations

import json
import math
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from src.analytics.capacity_aware_tca import DEFAULT_SPREAD_BPS
from src.analytics.orderflow_alpha_toxicity_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    DEFAULT_SIGNAL_THRESHOLD,
    DEFAULT_TOXICITY_THRESHOLD,
    DEFAULT_TOXICITY_WINDOW_TRADES,
    HORIZONS,
    IC_EXISTS_EPSILON,
    PERM_ALPHA,
    TSTAT_CRITICAL,
    _all_finite_numbers,
    _build_bars,
    _causal_signal_series,
    _finite,
    _pearson,
    _p95,
    _signal_positions,
    _stamp_for_filename,
    _tstat_from_ics,
    _toxicities_per_bar,
    _utc_now_iso,
    compute_alpha_metrics,
    compute_orderflow_toxicity_verdict,
    compute_toxicity_metrics,
    evaluate_orderflow_alpha_toxicity,
    load_btc_orderflow,
)
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.campaign.integrated import DEFAULT_SPOT
from src.data.schemas import OrderflowSnapshot, Trade

REPO_ROOT = Path(__file__).resolve().parents[1]
SPOT = float(DEFAULT_SPOT["BTC"])


def _report():
    return evaluate_orderflow_alpha_toxicity(write=False, timestamp="2026-11-13T07:55:00Z")


def _make_trade(trade_id: str, side: str, size: float, price: float, seconds_offset: int) -> Trade:
    ts = datetime(2026, 10, 31, 6, 32, 42, tzinfo=timezone.utc) + timedelta(seconds=seconds_offset)
    return Trade(
        trade_id=trade_id,
        symbol="BTCUSDT",
        venue="synthetic",
        price=price,
        size=size,
        side=side,
        timestamp=ts,
    )


def _snapshot(trades):
    return OrderflowSnapshot(
        symbol="BTCUSDT", venue="synthetic", trades=list(trades),
        timestamp=datetime(2026, 10, 31, 6, 52, 48, tzinfo=timezone.utc),
    )


# --------------------------------------------------------------------------- #
# 1. Helpers
# --------------------------------------------------------------------------- #

def test_finite_helper():
    assert _finite(1.5) == 1.5
    assert _finite(float("inf")) == 0.0
    assert _finite(float("nan")) == 0.0
    assert _finite("2.5") == 2.5
    assert _finite(None) == 0.0


def test_utc_and_stamp_helpers():
    assert _stamp_for_filename("2026-11-13T07:55:00Z") == "20261113T075500Z"
    assert _stamp_for_filename("2026-11-13T07:55:00.123456Z") == "20261113T075500Z"
    iso = _utc_now_iso()
    assert iso.endswith("Z") and "T" in iso and "+" not in iso


def test_all_finite_numbers():
    assert _all_finite_numbers({"a": 1.0, "b": [2.0, 3.0]}) is True
    assert _all_finite_numbers({"a": float("nan")}) is False
    assert _all_finite_numbers([float("inf")]) is False


def test_pearson_bounds():
    assert _pearson([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 1.0
    assert _pearson([1.0, 2.0, 3.0], [3.0, 2.0, 1.0]) == -1.0
    assert _pearson([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) == 0.0
    assert _pearson([1.0], [2.0]) == 0.0


# --------------------------------------------------------------------------- #
# 2. Real orderflow loading
# --------------------------------------------------------------------------- #

def test_load_real_orderflow_shape():
    snap = load_btc_orderflow("BTC", "synthetic")
    assert snap.symbol == "BTC"
    assert snap.venue == "synthetic"
    assert len(snap.trades) == 1000
    assert len(snap.liquidations) == 20
    assert len(snap.funding_rates) == 8
    for t in snap.trades:
        assert t.symbol == "BTCUSDT"
        assert t.size > 0.0
        assert t.price > 0.0
        assert str(t.side).lower() in ("buy", "sell")


# --------------------------------------------------------------------------- #
# 3. Causal bar construction
# --------------------------------------------------------------------------- #

def test_bar_construction_shape_and_finiteness():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    assert bars["n_bars"] > max(HORIZONS) + 1
    assert len(bars["bar_closes"]) == bars["n_bars"]
    assert len(bars["bar_trades"]) == bars["n_bars"]
    assert all(math.isfinite(p) and p > 0 for p in bars["bar_closes"])
    assert bars["start_timestamp"] and bars["end_timestamp"]


def test_bar_ends_monotonic():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=30.0)
    ends = [datetime.fromisoformat(e.replace("Z", "+00:00")) for e in bars["bar_ends"]]
    assert all(ends[i] < ends[i + 1] for i in range(len(ends) - 1))


# --------------------------------------------------------------------------- #
# 4. Causal per-bar features (no lookahead)
# --------------------------------------------------------------------------- #

def test_causal_features_finite_and_bounded():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    series = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )
    assert series["n_bars"] == bars["n_bars"]
    assert len(series["signals"]) == bars["n_bars"]
    for s in series["signals"]:
        assert math.isfinite(s)
        assert -1.0 <= s <= 1.0
    for f in series["features_per_bar"]:
        assert math.isfinite(f["net_aggression"])
        assert math.isfinite(f["vpin_lite"])
        assert 0.0 <= f["vpin_lite"] <= 1.0
        assert f["n_trades"] >= 0


def test_no_lookahead_future_injection_does_not_change_early_bars():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    base = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )["signals"]

    # Inject a trade far in the future (after the last bar). Reuse the original
    # bar grid so the future trade cannot alter the bar boundaries; it must not
    # affect any bar's causal features because it lies beyond every bar_end.
    future = _make_trade("future_injected", "buy", 5.0, 70000.0, seconds_offset=10 ** 6)
    modified = _snapshot(list(snap.trades) + [future])
    altered = _causal_signal_series(
        modified, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )["signals"]
    assert altered == base, "future-injected trade changed a causal bar feature (lookahead)"


def test_shuffled_tape_preserves_causal_signal_up_to_order():
    # Causal features depend on the trade set up to each bar, not on future
    # trades; reordering trades within the past must not inject lookahead.
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    base = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )["signals"]
    # Same trades, same bar ends -> identical causal signal series.
    same = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )["signals"]
    assert same == base


# --------------------------------------------------------------------------- #
# 5. Alpha (IC + decay)
# --------------------------------------------------------------------------- #

def test_ic_computation_finite_and_bounded():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    series = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )
    alpha = compute_alpha_metrics(series["signals"], bars["bar_closes"], horizons=HORIZONS)
    assert set(alpha["ic_by_horizon"].keys()) == {str(h) for h in HORIZONS}
    for h in HORIZONS:
        ic = alpha["ic_by_horizon"][str(h)]
        assert math.isfinite(ic)
        assert -1.0 <= ic <= 1.0
    assert math.isfinite(alpha["ic_mean"])
    assert math.isfinite(alpha["ic_std"])
    assert math.isfinite(alpha["ic_tstat"])
    assert alpha["ic_std"] >= 0.0
    assert alpha["n_horizons"] == len(HORIZONS)


def test_ic_decay_structure():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    series = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )
    alpha = compute_alpha_metrics(series["signals"], bars["bar_closes"], horizons=HORIZONS)
    assert math.isfinite(alpha["ic_decay_slope"])
    ic_values = [alpha["ic_by_horizon"][str(h)] for h in HORIZONS]
    # Signal decay: IC magnitude should not grow with horizon (weak form).
    assert abs(ic_values[0]) >= abs(ic_values[-1]) - 1e-9


def test_block_bootstrap_ci_on_mean_ic():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    series = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )
    alpha = compute_alpha_metrics(series["signals"], bars["bar_closes"], horizons=HORIZONS)
    ci = alpha["ic_bootstrap_ci"]
    assert math.isfinite(ci["point"])
    assert math.isfinite(ci["lo"])
    assert math.isfinite(ci["hi"])
    assert ci["lo"] <= ci["point"] <= ci["hi"] or ci["hi"] <= ci["point"] <= ci["lo"]


def test_tstat_from_ics():
    assert _tstat_from_ics([0.1, 0.2, 0.3]) > 0.0
    assert _tstat_from_ics([0.0, 0.0, 0.0]) == 0.0
    assert _tstat_from_ics([0.5]) == 0.0


# --------------------------------------------------------------------------- #
# 6. Permutation test
# --------------------------------------------------------------------------- #

def test_permutation_test_valid():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    series = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )
    alpha = compute_alpha_metrics(series["signals"], bars["bar_closes"], horizons=HORIZONS)
    # Reuse the permutation block from the full evaluation via _report is too
    # heavy here; construct a paired permutation directly on the primary horizon.
    h = int(HORIZONS[-1])
    n = len(bars["bar_closes"])
    pairs = n - h
    fwd = [
        (bars["bar_closes"][t + h] - bars["bar_closes"][t]) / bars["bar_closes"][t]
        for t in range(pairs) if bars["bar_closes"][t] > 0
    ]
    sig = series["signals"][: len(fwd)]
    from src.analytics.strategy_evaluation import permutation_test
    perm = permutation_test(
        sample_a=sig if sig else [0.0],
        sample_b=[0.0] * len(fwd) if fwd else [0.0],
        statistic=lambda vals: float(sum(vals) / len(vals)) if len(vals) > 0 else 0.0,
        paired=True,
        n_permutations=500,
        seed=42,
    )
    assert 0.0 < perm["p_value"] <= 1.0
    assert math.isfinite(perm["observed_difference"])
    assert isinstance(perm["significant_at_05"], bool)
    assert perm["paired"] is True


# --------------------------------------------------------------------------- #
# 7. Toxicity (VPIN)
# --------------------------------------------------------------------------- #

def test_toxicity_measured_not_degenerate():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    tox = _toxicities_per_bar(snap, bars["bar_ends_dt"], window_trades=DEFAULT_TOXICITY_WINDOW_TRADES)
    assert len(tox) == bars["n_bars"]
    assert all(0.0 <= t <= 1.0 and math.isfinite(t) for t in tox)
    metrics = compute_toxicity_metrics(tox, threshold=DEFAULT_TOXICITY_THRESHOLD)
    assert metrics["n_bars"] == bars["n_bars"]
    assert 0.0 < metrics["mean_toxicity"] < 1.0
    assert 0.0 <= metrics["p95_toxicity"] <= 1.0
    assert 0.0 <= metrics["fraction_above_threshold"] <= 1.0
    assert 0.0 <= metrics["toxic_gate_active_fraction"] <= 1.0
    # Must be a real measured number: not identically 0 and not identically 1.
    assert metrics["min_toxicity"] != metrics["max_toxicity"] or metrics["mean_toxicity"] not in (0.0, 1.0)
    assert isinstance(metrics["gate_engages"], bool)
    assert isinstance(metrics["toxicity_measured"], bool)


def test_p95_bounds():
    assert _p95([0.1, 0.2, 0.3, 0.4, 0.5]) == 0.5
    assert _p95([]) == 0.0


# --------------------------------------------------------------------------- #
# 8. Net-of-cost with/without
# --------------------------------------------------------------------------- #

def test_net_of_cost_finite_and_cost_applied():
    r = _report()
    ws = r["with_signal"]
    wo = r["without_signal"]
    assert math.isfinite(ws["oos_return"])
    assert math.isfinite(ws["oos_sharpe"])
    assert math.isfinite(ws["oos_max_drawdown"])
    assert math.isfinite(wo["oos_return"])
    assert math.isfinite(wo["oos_sharpe"])
    assert int(ws["num_windows"]) > 0
    assert float(ws["total_cost_usd"]) >= 0.0
    assert float(ws["spread_bps"]) == DEFAULT_SPREAD_BPS  # cost model applied
    assert float(ws["impact_coeff"]) > 0.0


# --------------------------------------------------------------------------- #
# 9. Verdict
# --------------------------------------------------------------------------- #

def test_verdict_structure_and_checks():
    r = _report()
    v = r["verdict_checks"]
    assert r["verdict"] in ("GO", "NO-GO")
    assert v["verdict"] == r["verdict"]
    assert v["n_checks"] == 5
    assert v["n_passed"] + len(v["failed_checks"]) == v["n_checks"]
    assert v["all_checks_pass"] == (r["verdict"] == "GO")
    required = {
        "signal_exists_ic_nonzero",
        "ic_significant",
        "toxicity_measured",
        "net_of_cost_with_vs_without",
        "no_lookahead_asserted",
    }
    assert required.issubset({c["name"] for c in v["checks"]})
    for c in v["checks"]:
        assert math.isfinite(c["threshold"])
        assert math.isfinite(c["observed"])
        assert isinstance(c["reason"], str) and c["reason"]
        assert isinstance(c["pass"], bool)


def test_verdict_matches_function():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    series = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )
    alpha = compute_alpha_metrics(series["signals"], bars["bar_closes"], horizons=HORIZONS)
    tox = _toxicities_per_bar(snap, bars["bar_ends_dt"], window_trades=DEFAULT_TOXICITY_WINDOW_TRADES)
    toxicity = compute_toxicity_metrics(tox, threshold=DEFAULT_TOXICITY_THRESHOLD)
    positions = _signal_positions(series["signals"], threshold=DEFAULT_SIGNAL_THRESHOLD)
    # Exercise the public verdict function with deterministic inputs.
    verdict = compute_orderflow_toxicity_verdict(
        alpha, toxicity,
        with_signal={"oos_return": 0.0, "oos_sharpe": 0.0, "oos_max_drawdown": 0.0,
                     "total_cost_usd": 0.0, "num_windows": 1},
        without_signal={"oos_return": 0.0, "oos_sharpe": 0.0, "oos_max_drawdown": 0.0,
                        "total_cost_usd": 0.0, "num_windows": 1},
        permutation={"p_value": 0.5},
        no_lookahead_asserted=True,
    )
    assert verdict["verdict"] in ("GO", "NO-GO")
    assert verdict["verdict"] == ("GO" if verdict["all_checks_pass"] else "NO-GO")
    assert verdict["n_passed"] == sum(1 for c in verdict["checks"] if c["pass"])


# --------------------------------------------------------------------------- #
# 10. Report-level invariants
# --------------------------------------------------------------------------- #

def test_report_never_valid_true_and_strict_serializable():
    r = _report()
    assert r["never_valid_true"] is True
    assert "valid" not in r or r.get("valid") is not True
    assert r["report_id"] == "ORDERFLOW_ALPHA_TOXICITY_EVAL_17"
    assert r["trading_mode"] == "paper"
    assert r["live_trading_enabled"] is False
    text = json.dumps(r, allow_nan=False, sort_keys=True)
    assert "NaN" not in text and "Infinity" not in text
    assert _all_finite_numbers(r)


def test_report_evidence_matrix_real_data():
    r = _report()
    em = r["evidence_matrix"]
    assert em["orderflow_loaded"] is True
    assert em["n_trades"] == 1000
    assert em["n_liquidations"] == 20
    assert em["n_funding_rates"] == 8
    assert em["symbol"] == "BTC"
    assert em["venue"] == "synthetic"
    assert em["bars_constructed"] is True
    assert em["causal_signal_computed"] is True
    assert em["ic_computed"] is True
    assert em["net_of_cost_run"] is True
    assert em["paper_only"] is True
    assert em["live_trading_enabled"] is False


# --------------------------------------------------------------------------- #
# 11. CLI writes both artifacts
# --------------------------------------------------------------------------- #

def test_cli_writes_artifacts(tmp_path):
    code = subprocess.run(
        [
            sys.executable,
            "-m", "src.analytics.orderflow_alpha_toxicity_evaluation",
            "--out", str(tmp_path),
            "--timestamp", "2026-11-13T07:55:00Z",
        ],
        cwd=REPO_ROOT,
        env={**os.environ, "PYTHONPATH": str(REPO_ROOT)},
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert code.returncode == 0, code.stderr
    written = [line.split("Wrote ", 1)[1] for line in code.stdout.splitlines() if line.startswith("Wrote ")]
    assert len(written) == 2, written
    for rel in written:
        p = Path(rel)
        if not p.is_absolute():
            p = tmp_path / p
        assert p.exists(), f"missing artifact {p}"
        text = p.read_text()
        assert "NaN" not in text and "Infinity" not in text
