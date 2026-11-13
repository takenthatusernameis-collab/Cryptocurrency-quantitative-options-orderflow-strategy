"""Numeric-invariant tests for src/analytics/integrated_options_orderflow_evaluation.py (EVAL-18).

Covers: real options chain loading (30 quotes, EVAL-16 data), real orderflow loading
(1000 trades, EVAL-17 data), causal bar construction, per-bar causal signals from both
pillars (options reconstructed surface + orderflow net_aggression), strict no-lookahead
assertion (future-injected tape does not change any earlier bar's features), information
coefficient + decay across horizons 1/5/20 for all three signals, block-bootstrap CI on
mean IC, paired permutation test (combined vs best single pillar), VPIN toxicity measured
(not identically 0 or 1, gate engagement), deterministic position fusion (both pillars
agree + toxicity gate), net-of-cost integrated walk-forward vs three controls (flat,
options-only, orderflow-only), capacity-aware cost model applied, DSR/PBO/BH-FDR
statistical defensibility, deterministic verdict with 7 explicit checks, strict
serialization (allow_nan=False, never {"valid": true}), and CLI artifact emission.
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
from src.analytics.integrated_options_orderflow_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
    DEFAULT_SIGNAL_LOOKBACK_SECONDS,
    DEFAULT_SIGNAL_THRESHOLD,
    DEFAULT_TOXICITY_THRESHOLD,
    DEFAULT_TOXICITY_WINDOW_TRADES,
    GUARDRAIL_COST_BUDGET_BPS,
    GUARDRAIL_DELTA_BAND_USD,
    GUARDRAIL_KILL_SWITCH_COST_BPS,
    GUARDRAIL_KILL_SWITCH_DD,
    GUARDRAIL_KILL_SWITCH_TOXICITY,
    GUARDRAIL_MAX_DAILY_LOSS_USD,
    GUARDRAIL_MAX_NOTIONAL_USD,
    GUARDRAIL_TARGET_DELTA_USD,
    GUARDRAIL_TOXICITY_GATE,
    HORIZONS,
    IC_EXISTS_EPSILON,
    PERM_ALPHA,
    TSTAT_CRITICAL,
    _all_finite_numbers,
    _build_bars,
    _causal_options_signal_series,
    _causal_signal_series,
    _deflated_sharpe,
    _finite,
    _fuse_positions,
    _pearson,
    _p95,
    _signal_positions,
    _stamp_for_filename,
    _tstat_from_ics,
    _toxicities_per_bar,
    _utc_now_iso,
    compute_alpha_metrics,
    compute_integrated_verdict,
    compute_toxicity_metrics,
    evaluate_integrated_options_orderflow,
    load_btc_options_chain,
    load_btc_orderflow,
)
from src.analytics.strategy_evaluation import permutation_test
from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.campaign.integrated import DEFAULT_SPOT
from src.data.schemas import OrderflowSnapshot, Trade

REPO_ROOT = Path(__file__).resolve().parents[1]
SPOT = float(DEFAULT_SPOT["BTC"])


def _report():
    return evaluate_integrated_options_orderflow(write=False, timestamp="2026-11-13T08:10:00Z")


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
    assert _stamp_for_filename("2026-11-13T08:10:00Z") == "20261113T081000Z"
    assert _stamp_for_filename("2026-11-13T08:10:00.123456Z") == "20261113T081000Z"
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
# 2. Real data loading (options chain + orderflow)
# --------------------------------------------------------------------------- #

def test_load_real_options_chain():
    chain = load_btc_options_chain("BTC", spot=SPOT)
    assert chain.underlying == "BTC"
    assert chain.venue == "synthetic"
    assert len(chain.quotes) == 30
    for q in chain.quotes:
        assert q.contract.strike > 0.0
        assert q.contract.option_type in ("call", "put")
        assert q.mark_iv is not None and q.mark_iv > 0.0


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
# 4. Causal per-bar signals (options + orderflow, no lookahead)
# --------------------------------------------------------------------------- #

def test_causal_orderflow_signal_finite_and_bounded():
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


def test_options_signal_components_from_reconstructed_surface():
    chain = load_btc_options_chain("BTC", spot=SPOT)
    now = datetime(2026, 10, 31, 0, 0, 0, tzinfo=timezone.utc)
    from src.analytics.integrated_options_orderflow_evaluation import _options_signal_components
    comps = _options_signal_components(chain, SPOT, now, seed=42)
    assert comps["surface_points"] > 0
    assert comps["surface_expiries"] > 0
    assert math.isfinite(comps["calib_residual_max_abs"])
    assert math.isfinite(comps["gamma_flip_level"])
    assert math.isfinite(comps["gex_signal"])
    assert -1.0 <= comps["gex_signal"] <= 1.0
    assert -1.0 <= comps["skew_signal"] <= 1.0
    assert -1.0 <= comps["calib_signal"] <= 1.0
    assert -1.0 <= comps["options_signal_raw"] <= 1.0


def test_causal_options_signal_broadcast():
    chain = load_btc_options_chain("BTC", spot=SPOT)
    now = datetime(2026, 10, 31, 0, 0, 0, tzinfo=timezone.utc)
    from src.analytics.integrated_options_orderflow_evaluation import _options_signal_components
    comps = _options_signal_components(chain, SPOT, now, seed=42)
    n_bars = 240
    sig = _causal_options_signal_series(n_bars, comps)
    assert len(sig) == n_bars
    assert all(math.isfinite(s) for s in sig)
    assert all(-1.0 <= s <= 1.0 for s in sig)
    # Static broadcast: every bar identical (deterministic, no lookahead).
    assert all(s == sig[0] for s in sig)


def test_no_lookahead_future_injection_does_not_change_early_bars():
    snap = load_btc_orderflow("BTC", "synthetic")
    bars = _build_bars(snap, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    base = _causal_signal_series(
        snap, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )["signals"]
    future = _make_trade("future_injected", "buy", 5.0, 70000.0, seconds_offset=10 ** 6)
    modified = _snapshot(list(snap.trades) + [future])
    altered = _causal_signal_series(
        modified, bars["bar_ends_dt"], bars["bar_closes"],
        lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS,
        engine=OrderflowAlphaEngine(seed=42),
    )["signals"]
    assert altered == base, "future-injected trade changed a causal bar feature (lookahead)"


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
    h = int(HORIZONS[-1])
    n = len(bars["bar_closes"])
    pairs = n - h
    fwd = [
        (bars["bar_closes"][t + h] - bars["bar_closes"][t]) / bars["bar_closes"][t]
        for t in range(pairs) if bars["bar_closes"][t] > 0
    ]
    sig = series["signals"][: len(fwd)]
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
    assert metrics["min_toxicity"] != metrics["max_toxicity"] or metrics["mean_toxicity"] not in (0.0, 1.0)
    assert isinstance(metrics["gate_engages"], bool)
    assert isinstance(metrics["toxicity_measured"], bool)


def test_p95_bounds():
    assert _p95([0.1, 0.2, 0.3, 0.4, 0.5]) == 0.5
    assert _p95([]) == 0.0


# --------------------------------------------------------------------------- #
# 8. Position fusion (deterministic rule + toxicity gate)
# --------------------------------------------------------------------------- #

def test_fusion_positions_deterministic_and_gated():
    n = 100
    options_signal = [0.5] * n  # all long
    orderflow_signal = [0.5] * n  # all long
    toxicity_low = [0.1] * n  # below gate
    toxicity_high = [0.9] * n  # above gate
    combined_low = _fuse_positions(options_signal, orderflow_signal, toxicity_low)
    combined_high = _fuse_positions(options_signal, orderflow_signal, toxicity_high)
    assert all(p == 1 for p in combined_low), "both pillars agree long + no toxicity -> long"
    assert all(p == 0 for p in combined_high), "toxicity gate engaged -> flat"
    # Disagreement -> flat.
    orderflow_short = [-0.5] * n
    combined_disagree = _fuse_positions(options_signal, orderflow_short, toxicity_low)
    assert all(p == 0 for p in combined_disagree), "pillars disagree -> flat"


def test_signal_positions_thresholding():
    sig = [0.2, 0.05, -0.2, -0.05, 0.0]
    pos = _signal_positions(sig, threshold=DEFAULT_SIGNAL_THRESHOLD)
    assert pos == [1, 0, -1, 0, 0]


# --------------------------------------------------------------------------- #
# 9. Net-of-cost walk-forward vs 3 controls
# --------------------------------------------------------------------------- #

def test_walkforward_finite_and_cost_applied():
    r = _report()
    for key in ("combined_wf", "options_only_wf", "orderflow_only_wf", "flat_wf"):
        wf = r[key]
        assert math.isfinite(wf["oos_return"])
        assert math.isfinite(wf["oos_sharpe"])
        assert math.isfinite(wf["oos_max_drawdown"])
        assert int(wf["num_windows"]) > 0
        assert float(wf["total_cost_usd"]) >= 0.0
        assert float(wf["spread_bps"]) == DEFAULT_SPREAD_BPS
        assert float(wf["impact_coeff"]) > 0.0


# --------------------------------------------------------------------------- #
# 10. Statistical defensibility (DSR, PBO, BH-FDR)
# --------------------------------------------------------------------------- #

def test_dsr_pbo_bh_fdr_finite():
    r = _report()
    for name, val in r["dsr"].items():
        assert math.isfinite(val), f"DSR non-finite for {name}"
    assert math.isfinite(r["pbo"]["overall_pbo"])
    assert 0.0 <= r["pbo"]["overall_pbo"] <= 1.0
    assert isinstance(r["bh_fdr"]["rejected"], list)
    assert isinstance(r["bh_fdr"]["thresholds"], dict)
    assert math.isfinite(r["bh_fdr"]["alpha"])
    for k, v in r["perm_pairs"].items():
        assert 0.0 < v <= 1.0, f"perm p non-valid for {k}"


# --------------------------------------------------------------------------- #
# 11. Verdict
# --------------------------------------------------------------------------- #

def test_verdict_structure_and_checks():
    r = _report()
    v = r["verdict_checks"]
    assert r["verdict"] in ("GO", "NO-GO")
    assert v["verdict"] == r["verdict"]
    assert v["n_checks"] == 7
    assert v["n_passed"] + len(v["failed_checks"]) == v["n_checks"]
    assert v["all_checks_pass"] == (r["verdict"] == "GO")
    required = {
        "options_signal_exists",
        "orderflow_signal_exists",
        "combined_ic_significant",
        "combined_net_of_cost_superior",
        "toxicity_gate_measured",
        "no_lookahead_asserted",
        "guardrails_consistent_with_eval13_14_15",
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
    verdict = compute_integrated_verdict(
        options_alpha=alpha,
        orderflow_alpha=alpha,
        combined_alpha=alpha,
        toxicity=toxicity,
        combined_wf={"oos_return": 0.0, "oos_sharpe": 0.0, "oos_max_drawdown": 0.0,
                     "total_cost_usd": 0.0, "num_windows": 1},
        options_only_wf={"oos_return": 0.0, "oos_sharpe": 0.0, "oos_max_drawdown": 0.0,
                         "total_cost_usd": 0.0, "num_windows": 1},
        orderflow_only_wf={"oos_return": 0.0, "oos_sharpe": 0.0, "oos_max_drawdown": 0.0,
                           "total_cost_usd": 0.0, "num_windows": 1},
        flat_wf={"oos_return": 0.0, "oos_sharpe": 0.0, "oos_max_drawdown": 0.0,
                 "total_cost_usd": 0.0, "num_windows": 1},
        permutation={"p_value": 0.5},
        dsr={"combined": 0.0, "options_only": 0.0, "orderflow_only": 0.0, "flat": 0.0},
        pbo={"overall_pbo": 0.0, "n_configs": 4, "pbo_per_config": {}},
        bh_fdr={"rejected": [], "thresholds": {}, "alpha": 0.10, "m_tests": 0, "method": "Benjamini-Hochberg"},
        no_lookahead_asserted=True,
    )
    assert verdict["verdict"] in ("GO", "NO-GO")
    assert verdict["verdict"] == ("GO" if verdict["all_checks_pass"] else "NO-GO")
    assert verdict["n_passed"] == sum(1 for c in verdict["checks"] if c["pass"])


# --------------------------------------------------------------------------- #
# 12. Guardrail constants
# --------------------------------------------------------------------------- #

def test_guardrail_constants_finite_and_sane():
    assert GUARDRAIL_DELTA_BAND_USD > 0.0
    assert GUARDRAIL_TARGET_DELTA_USD < 0.0
    assert GUARDRAIL_TOXICITY_GATE == DEFAULT_TOXICITY_THRESHOLD
    assert GUARDRAIL_COST_BUDGET_BPS > 0.0
    assert 0.0 < GUARDRAIL_KILL_SWITCH_DD < 1.0
    assert 0.0 < GUARDRAIL_KILL_SWITCH_TOXICITY < 1.0
    assert GUARDRAIL_KILL_SWITCH_COST_BPS > 0.0
    assert GUARDRAIL_MAX_NOTIONAL_USD > 0.0
    assert GUARDRAIL_MAX_DAILY_LOSS_USD > 0.0


# --------------------------------------------------------------------------- #
# 13. Report-level invariants
# --------------------------------------------------------------------------- #

def test_report_never_valid_true_and_strict_serializable():
    r = _report()
    assert r["never_valid_true"] is True
    assert "valid" not in r or r.get("valid") is not True
    assert r["report_id"] == "INTEGRATED_OPTIONS_ORDERFLOW_EVAL_18"
    assert r["trading_mode"] == "paper"
    assert r["live_trading_enabled"] is False
    text = json.dumps(r, allow_nan=False, sort_keys=True)
    assert "NaN" not in text and "Infinity" not in text
    assert _all_finite_numbers(r)


def test_report_evidence_matrix_real_data():
    r = _report()
    em = r["evidence_matrix"]
    assert em["options_chain_loaded"] is True
    assert em["n_options_quotes"] == 30
    assert em["orderflow_loaded"] is True
    assert em["n_trades"] == 1000
    assert em["n_liquidations"] == 20
    assert em["n_funding_rates"] == 8
    assert em["symbol"] == "BTC"
    assert em["venue"] == "synthetic"
    assert em["bars_constructed"] is True
    assert em["causal_orderflow_signal_computed"] is True
    assert em["causal_options_signal_computed"] is True
    assert em["combined_signal_computed"] is True
    assert em["ic_computed"] is True
    assert em["permutation_computed"] is True
    assert em["toxicity_measured"] is True
    assert em["integrated_walkforward_run"] is True
    assert em["paper_only"] is True
    assert em["live_trading_enabled"] is False
    assert em["options_signal_from_reconstructed_surface"] is True
    assert em["toxicity_gate_applied_to_all_pillars"] is True


# --------------------------------------------------------------------------- #
# 14. CLI writes both artifacts
# --------------------------------------------------------------------------- #

def test_cli_writes_artifacts(tmp_path):
    code = subprocess.run(
        [
            sys.executable,
            "-m", "src.analytics.integrated_options_orderflow_evaluation",
            "--out", str(tmp_path),
            "--timestamp", "2026-11-13T08:10:00Z",
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
