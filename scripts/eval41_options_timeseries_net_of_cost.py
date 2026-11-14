#!/usr/bin/env python3
"""EVAL-41 Track B: dense real options time-series net-of-cost decisive test.

This is the mandatory heavy work for the options pillar. It answers the binary
strategic question: can a genuinely time-varying options signal carry ANY
net-of-cost alpha on the available real BTC/OKX data?

Inputs (already acquired and verified; never re-acquired here):
  - ``data/raw/options_candles/`` — 101 real OKX option-candle snapshots
    (5-min bars, 2026-11-14T11:35:00Z -> 19:55:00Z, 26 distinct signal levels).
  - ``data/raw/eval41/orderflow_okx_BTC-USD-SWAP.json`` — fresh no-cursor tape
    (13:22:33.993Z -> 19:50:29.020Z), fully covered by the snapshots.
  - ``data/raw/orderflow_okx_BTC-USD-SWAP.json`` — disjoint robustness tape
    (09:05:22.330Z -> 15:33:56.432Z), partially covered (598 flat bars first).

Method (pre-declared, no curve fitting):
  For each window: load the tape, build 15 s bars, align the per-snapshot
  options signal causally (newest snapshot with timestamp <= bar end), build the
  orderflow signal and per-bar toxicities. On the FULL tape (the aligned signal
  saturates at a constant value in the tail, so a fixed tail slice would be
  degenerate) run the pre-declared options-only grid: direction in {long, short}
  x threshold in {0.01, 0.02, 0.05, 0.1, 0.2, 0.5}, toxicity gate on. Compare
  every variant against orderflow-only and flat controls on the identical slice.

Pre-declared GO bar (all four required, on BOTH windows):
  (a) OOS Sharpe > max(orderflow-only, flat);
  (b) paired permutation p < 0.05 vs that control;
  (c) block-bootstrap 95% CI excludes 0;
  (d) >=2 distinct time-varying levels with |IC| > 1e-9.
Otherwise REPLICATION/NO-GO: the options pillar is definitively closed as
non-persistent on the available real data.

Seal ``EVAL_41_TIMESERIES_NET_OF_COST_<UTC>.{json,md}``.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.alpha.orderflow_alpha import OrderflowAlphaEngine
from src.analytics.capacity_aware_tca import (
    CapacityAwareSizer,
    DEFAULT_COST_BUDGET_BPS,
    DEFAULT_IMPACT_COEFF,
    DEFAULT_MAX_PARTICIPATION,
    DEFAULT_SPREAD_BPS,
)
from src.analytics.integrated_options_orderflow_evaluation import (
    DEFAULT_BAR_DURATION_SECONDS,
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
    HORIZONS,
    _build_bars,
    _causal_signal_series,
    _run_walkforward,
    _toxicities_per_bar,
)
from src.analytics.options_time_varying_signal import (
    align_options_signal_to_bars,
    load_snapshot_signals,
    measure_time_varying_signal,
)
from src.analytics.real_walkforward_certification import _benjamini_hochberg, _cscv_pbo
from src.analytics.strategy_evaluation import block_bootstrap_ci, permutation_test
from src.campaign.integrated import IntegratedConfig, load_real_orderflow
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

OUT_DIR = Path("research_state")
REPORT_ID = "EVAL_41_TIMESERIES_NET_OF_COST"
OPTIONS_DIR = Path("data/raw/options_candles")

# Pre-declared windows (name -> tape path). Both overlap the snapshot window.
WINDOWS: Tuple[Dict[str, str], ...] = (
    {"name": "41d_fresh", "path": "data/raw/eval41/orderflow_okx_BTC-USD-SWAP.json"},
    {"name": "midday_robustness", "path": "data/raw/orderflow_okx_BTC-USD-SWAP.json"},
)

# Pre-declared grid.
GRID_DIRECTIONS: Tuple[str, ...] = ("long", "short")
GRID_THRESHOLDS: Tuple[float, ...] = (0.01, 0.02, 0.05, 0.1, 0.2, 0.5)

# Evaluate the FULL tape. The aligned options signal is time-varying only in the
# first hours (it saturates at one value after ~16:40Z), so a fixed tail slice is
# degenerate; the full tape is required for a valid time-variation test.
HELD_OUT_BARS: int | None = None

PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
PBO_K_FOLDS = 4
PBO_N_COMBINATIONS = 16
SEED = 42
MIN_DISTINCT_LEVELS = 2
MIN_ABS_IC = 1e-9


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _stamp_for_filename(iso_ts: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
        return dt.strftime("%Y%m%dT%H%M%SZ")
    except Exception:
        return iso_ts.replace("-", "").replace(":", "").replace(".", "")


def _all_finite(obj: Any) -> bool:
    if isinstance(obj, bool):
        return True
    if isinstance(obj, (int, float)):
        return math.isfinite(float(obj))
    if isinstance(obj, dict):
        return all(_all_finite(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(_all_finite(v) for v in obj)
    return True


def _mean(vals: Sequence[float]) -> float:
    clean = [float(v) for v in vals if math.isfinite(float(v))]
    return float(sum(clean) / len(clean)) if clean else 0.0


def _sharpe_of_returns(rets: Sequence[float], periods_per_year: float = 252.0) -> float:
    vals = [float(r) for r in rets if math.isfinite(float(r))]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    std = math.sqrt(sum((r - mean) ** 2 for r in vals) / len(vals))
    if std <= 0.0:
        return 0.0
    sr = mean / std * math.sqrt(periods_per_year)
    return float(sr) if math.isfinite(sr) else 0.0


def positions_for(
    signals: Sequence[float],
    toxicities: Sequence[float],
    *,
    direction: str,
    threshold: float,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
) -> List[int]:
    """Pure position builder for the options-only grid (toxicity gate on)."""
    out: List[int] = []
    n = min(len(signals), len(toxicities))
    for i in range(n):
        sig = float(signals[i])
        tox = float(toxicities[i])
        if tox >= toxicity_threshold:
            out.append(0)
        elif direction == "long" and sig > threshold:
            out.append(1)
        elif direction == "short" and sig < -threshold:
            out.append(-1)
        else:
            out.append(0)
    return out


def orderflow_positions(
    signals: Sequence[float],
    toxicities: Sequence[float],
    *,
    threshold: float = DEFAULT_SIGNAL_THRESHOLD,
    toxicity_threshold: float = DEFAULT_TOXICITY_THRESHOLD,
) -> List[int]:
    out: List[int] = []
    n = min(len(signals), len(toxicities))
    for i in range(n):
        sig = float(signals[i])
        tox = float(toxicities[i])
        if tox >= toxicity_threshold:
            out.append(0)
        elif sig > threshold:
            out.append(1)
        elif sig < -threshold:
            out.append(-1)
        else:
            out.append(0)
    return out


def _variant_window_pass(
    *,
    oos_sharpe: float,
    num_trades: int,
    control_sharpe: float,
    permutation_p: float,
    ci_lo: float,
    ci_hi: float,
    distinct_levels: int,
    abs_ic: float,
) -> Dict[str, Any]:
    superior = bool(oos_sharpe > control_sharpe and num_trades > 0)
    perm_pass = bool(permutation_p < 0.05)
    ci_excludes_zero = bool(ci_lo > 0.0 or ci_hi < 0.0)
    non_degenerate = bool(distinct_levels >= MIN_DISTINCT_LEVELS and abs_ic > MIN_ABS_IC)
    return {
        "oos_sharpe": float(oos_sharpe),
        "num_trades": int(num_trades),
        "control_sharpe": float(control_sharpe),
        "superior_to_best_control": superior,
        "permutation_p": float(permutation_p),
        "perm_pass": perm_pass,
        "bootstrap_ci": [float(oos_sharpe), float(ci_lo), float(ci_hi)],
        "ci_excludes_zero": ci_excludes_zero,
        "distinct_levels": int(distinct_levels),
        "abs_ic": float(abs_ic),
        "non_degenerate": non_degenerate,
        "window_pass": bool(superior and perm_pass and ci_excludes_zero and non_degenerate),
    }


def _evaluate_variant(
    *,
    name: str,
    direction: str,
    threshold: float,
    per_window: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Aggregate a single grid variant across windows; GO needs all 4 on both."""
    all_pass = bool(per_window) and all(w["window_pass"] for w in per_window)
    return {
        "variant": name,
        "direction": direction,
        "threshold": float(threshold),
        "per_window": per_window,
        "passed_all_windows": all_pass,
        "mean_oos_sharpe": _mean([w["oos_sharpe"] for w in per_window]),
    }


def _run_window(
    *,
    name: str,
    tape_path: str,
    signals: Sequence[Any],
    cfg: IntegratedConfig,
    sizer: CapacityAwareSizer,
) -> Dict[str, Any]:
    snapshot = load_real_orderflow("BTC", orderflow_path=tape_path)
    bars = _build_bars(snapshot, bar_duration_seconds=DEFAULT_BAR_DURATION_SECONDS)
    n_bars = int(bars["n_bars"])
    prices = bars["bar_closes"]
    timestamps = bars["bar_ends_dt"]
    bar_ends = bars["bar_ends_dt"]

    aligned = align_options_signal_to_bars(signals, bar_ends)
    opt_full = [float(v) for v in aligned["signals"]]
    tox_full = [
        float(v)
        for v in _toxicities_per_bar(
            snapshot, bar_ends, window_trades=DEFAULT_TOXICITY_WINDOW_TRADES
        )
    ]
    engine = OrderflowAlphaEngine(seed=SEED)
    of_full = [
        float(v)
        for v in _causal_signal_series(
            snapshot, bar_ends, prices,
            lookback_seconds=DEFAULT_SIGNAL_LOOKBACK_SECONDS, engine=engine,
        )["signals"]
    ]

    # Full tape by default; a fixed tail slice would be degenerate because the
    # aligned options signal saturates at a constant value in the last hours.
    start = 0 if HELD_OUT_BARS is None else max(0, n_bars - int(HELD_OUT_BARS))
    sl_prices = prices[start:]
    sl_ts = timestamps[start:]
    sl_opt = opt_full[start:]
    sl_tox = tox_full[start:]
    sl_of = of_full[start:]

    measurement = measure_time_varying_signal(
        signals, sl_ts, sl_prices, horizons=HORIZONS
    )
    distinct_levels = int(measurement["distinct_signal_values"])
    abs_ic = abs(float(measurement["ic_mean"]))

    wf_args = dict(
        symbol="BTC", sizer=sizer, cfg=cfg, n_points=DEFAULT_N_POINTS, seed=SEED,
        max_position_pct=DEFAULT_MAX_POSITION_PCT,
    )

    flat_pos = [0] * len(sl_prices)
    of_pos = orderflow_positions(sl_of, sl_tox)
    flat_wf = _run_walkforward(positions=flat_pos, prices=sl_prices, timestamps=sl_ts, **wf_args)
    of_wf = _run_walkforward(positions=of_pos, prices=sl_prices, timestamps=sl_ts, **wf_args)

    control_sharpe = max(float(of_wf["oos_sharpe"]), float(flat_wf["oos_sharpe"]))
    control_name = (
        "orderflow_only"
        if float(of_wf["oos_sharpe"]) >= float(flat_wf["oos_sharpe"])
        else "flat"
    )
    control_rets = [
        float(r)
        for r in (of_wf if control_name == "orderflow_only" else flat_wf).get("window_returns", [])
    ]

    variants: List[Dict[str, Any]] = []
    for direction in GRID_DIRECTIONS:
        for threshold in GRID_THRESHOLDS:
            pos = positions_for(sl_opt, sl_tox, direction=direction, threshold=threshold)
            wf = _run_walkforward(positions=pos, prices=sl_prices, timestamps=sl_ts, **wf_args)
            vrets = [float(r) for r in wf.get("window_returns", [])]

            perm_p = 1.0
            if vrets and control_rets and len(vrets) == len(control_rets):
                try:
                    perm = permutation_test(
                        vrets, control_rets, statistic=_mean,
                        n_permutations=PERMUTATION_PERMS, paired=True, seed=SEED,
                    )
                    perm_p = float(perm.get("p_value", 1.0))
                except Exception:
                    perm_p = 1.0

            try:
                boot = block_bootstrap_ci(
                    vrets, statistic=_sharpe_of_returns,
                    n_bootstrap=BOOTSTRAP_RESAMPLES, block_size=BOOTSTRAP_BLOCK, seed=SEED,
                )
                ci_lo, ci_hi = float(boot[1]), float(boot[2])
            except Exception:
                ci_lo, ci_hi = 0.0, 0.0

            pw = _variant_window_pass(
                oos_sharpe=float(wf["oos_sharpe"]),
                num_trades=int(wf["num_trades"]),
                control_sharpe=control_sharpe,
                permutation_p=perm_p,
                ci_lo=ci_lo,
                ci_hi=ci_hi,
                distinct_levels=distinct_levels,
                abs_ic=abs_ic,
            )
            pw.update({
                "name": f"options_only_{direction}_thresh{threshold}",
                "direction": direction,
                "threshold": float(threshold),
                "oos_return": float(wf["oos_return"]),
                "oos_max_drawdown": float(wf["oos_max_drawdown"]),
                "total_cost_usd": float(wf["total_cost_usd"]),
                "total_traded_notional": float(wf["total_traded_notional"]),
                "num_windows": int(wf["num_windows"]),
                "window_returns": vrets,
            })
            variants.append(pw)

    return {
        "window": name,
        "tape_path": tape_path,
        "n_bars_total": n_bars,
        "bar_duration_seconds": float(bars["bar_duration_seconds"]),
        "tape_start_utc": bars["start_timestamp"],
        "tape_end_utc": bars["end_timestamp"],
        "held_out_start_index": int(start),
        "held_out_n_bars": int(len(sl_prices)),
        "held_out_start_utc": bar_ends[start].isoformat().replace("+00:00", "Z"),
        "held_out_end_utc": bar_ends[-1].isoformat().replace("+00:00", "Z"),
        "n_snapshots_used": int(aligned["n_snapshots_used"]),
        "n_flat_bars_full_tape": int(aligned["n_flat_bars"]),
        "step_changes_full_tape": int(aligned["step_changes"]),
        "measurement": {
            "n_bars": int(measurement["n_bars"]),
            "distinct_signal_values": distinct_levels,
            "mean_signal": float(measurement["mean_signal"]),
            "signal_stdev": float(measurement["signal_stdev"]),
            "min_signal": float(measurement["min_signal"]),
            "max_signal": float(measurement["max_signal"]),
            "ic_by_horizon": measurement["ic_by_horizon"],
            "ic_tstat_by_horizon": measurement["ic_tstat_by_horizon"],
            "ic_mean": float(measurement["ic_mean"]),
            "ic_abs_mean": float(measurement["ic_abs_mean"]),
            "non_constant": bool(measurement["non_constant"]),
            "ic_present": bool(measurement["ic_present"]),
        },
        "controls": {
            "orderflow_only": {
                "oos_sharpe": float(of_wf["oos_sharpe"]),
                "oos_return": float(of_wf["oos_return"]),
                "oos_max_drawdown": float(of_wf["oos_max_drawdown"]),
                "num_trades": int(of_wf["num_trades"]),
                "total_cost_usd": float(of_wf["total_cost_usd"]),
                "total_traded_notional": float(of_wf["total_traded_notional"]),
                "num_windows": int(of_wf["num_windows"]),
                "window_returns": [float(r) for r in of_wf.get("window_returns", [])],
            },
            "flat": {
                "oos_sharpe": float(flat_wf["oos_sharpe"]),
                "oos_return": float(flat_wf["oos_return"]),
                "oos_max_drawdown": float(flat_wf["oos_max_drawdown"]),
                "num_trades": int(flat_wf["num_trades"]),
                "total_cost_usd": float(flat_wf["total_cost_usd"]),
                "total_traded_notional": float(flat_wf["total_traded_notional"]),
                "num_windows": int(flat_wf["num_windows"]),
                "window_returns": [float(r) for r in flat_wf.get("window_returns", [])],
            },
            "best_control": control_name,
            "best_control_sharpe": control_sharpe,
        },
        "variants": variants,
    }


def run_eval41(write: bool = True) -> Dict[str, Any]:
    generated_at = _utc_now_iso()

    signals = load_snapshot_signals("BTC", OPTIONS_DIR)
    all_levels = len({round(float(s.options_signal_raw), 12) for s in signals})

    cfg = IntegratedConfig(
        seed=SEED, train_window=DEFAULT_TRAIN_WINDOW, test_window=DEFAULT_TEST_WINDOW,
        step_size=DEFAULT_STEP_SIZE, purge=DEFAULT_PURGE, embargo=DEFAULT_EMBARGO,
    )
    sizer = CapacityAwareSizer(
        DEFAULT_SPREAD_BPS, DEFAULT_IMPACT_COEFF, DEFAULT_MAX_PARTICIPATION,
        DEFAULT_COST_BUDGET_BPS, seed=SEED,
    )

    window_results = [
        _run_window(name=w["name"], tape_path=w["path"], signals=signals, cfg=cfg, sizer=sizer)
        for w in WINDOWS
    ]

    # Aggregate each grid variant across windows.
    aggregated: List[Dict[str, Any]] = []
    for direction in GRID_DIRECTIONS:
        for threshold in GRID_THRESHOLDS:
            vname = f"options_only_{direction}_thresh{threshold}"
            per_window = []
            for wr in window_results:
                match = next((v for v in wr["variants"] if v["name"] == vname), None)
                if match is None:
                    continue
                per_window.append({
                    "window": wr["window"],
                    "oos_sharpe": match["oos_sharpe"],
                    "num_trades": match["num_trades"],
                    "control_sharpe": match["control_sharpe"],
                    "superior_to_best_control": match["superior_to_best_control"],
                    "permutation_p": match["permutation_p"],
                    "perm_pass": match["perm_pass"],
                    "bootstrap_ci": match["bootstrap_ci"],
                    "ci_excludes_zero": match["ci_excludes_zero"],
                    "distinct_levels": match["distinct_levels"],
                    "abs_ic": match["abs_ic"],
                    "non_degenerate": match["non_degenerate"],
                    "window_pass": match["window_pass"],
                })
            aggregated.append(_evaluate_variant(
                name=vname, direction=direction, threshold=threshold, per_window=per_window
            ))

    any_pass = any(v["passed_all_windows"] for v in aggregated)
    verdict = "GO" if any_pass else "REPLICATION/NO-GO"
    passing = [v["variant"] for v in aggregated if v["passed_all_windows"]]
    best = max(aggregated, key=lambda v: v["mean_oos_sharpe"])
    verdict_reason = (
        f"Variant(s) {passing} passed all four pre-declared criteria on both windows."
        if any_pass
        else (
            f"No options-only variant passed all four criteria on both windows. "
            f"Best mean OOS Sharpe = {best['variant']} ({best['mean_oos_sharpe']:.6f}); "
            f"per-window details in the artifact."
        )
    )

    # Statistical defensibility on the best variant (per window).
    defensibility: Dict[str, Any] = {}
    pvals: Dict[str, float] = {}
    for wr in window_results:
        match = next((v for v in wr["variants"] if v["name"] == best["variant"]), None)
        if match is None:
            continue
        rets = [float(r) for r in match.get("window_returns", [])]
        cfg_returns = {
            best["variant"]: rets,
            "orderflow_only": [float(r) for r in wr["controls"]["orderflow_only"]["window_returns"]],
            "flat": [float(r) for r in wr["controls"]["flat"]["window_returns"]],
        }
        clean = {k: v for k, v in cfg_returns.items() if len(v) >= PBO_K_FOLDS * 2}
        try:
            pbo = _cscv_pbo(clean, n_combinations=PBO_N_COMBINATIONS, k_folds=PBO_K_FOLDS)
        except Exception as exc:  # pragma: no cover - defensive
            pbo = {"error": str(exc)}
        defensibility[wr["window"]] = {
            "pbo_cscv": {
                "overall_pbo": pbo.get("overall_pbo"),
                "pbo_per_config": pbo.get("pbo_per_config"),
                "k_folds": PBO_K_FOLDS,
            },
            "permutation_p_vs_best_control": match["permutation_p"],
            "bootstrap_ci": match["bootstrap_ci"],
        }
        pvals[f"{wr['window']}__{best['variant']}"] = float(match["permutation_p"])
    try:
        bh = _benjamini_hochberg(pvals, alpha=0.1)
    except Exception as exc:  # pragma: no cover - defensive
        bh = {"error": str(exc), "input": pvals}

    report: Dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task_id": f"INIT-{generated_at}-EVAL-41-TRACK-B-DECISIVE",
        "trading_mode": "paper",
        "live_trading_enabled": False,
        "never_valid_true": True,
        "authenticity_verified": False,
        "data_provenance": "real_public_exchange_export",
        "symbol": "BTC",
        "venue": "okx",
        "provenance_caveats": [
            "Public read-only OKX exports; no signed venue attestation.",
            "Options snapshots are OKX option candle closes with reconstructed "
            "bid/ask spreads (price_mode=candle_close_with_reconstructed_spread); "
            "mid-price parity is meaningful, the bid-ask bound test is not.",
            "Inverse BTC-USD-SWAP orderflow tape vs spot option snapshots.",
            "Paper-only; no live trading; .env absent.",
        ],
        "options_provenance": {
            "options_dir": str(OPTIONS_DIR),
            "n_snapshots": int(len(signals)),
            "distinct_signal_levels": int(all_levels),
            "first_snapshot_utc": signals[0].snapshot_timestamp if signals else None,
            "last_snapshot_utc": signals[-1].snapshot_timestamp if signals else None,
            "snapshot_sha256": [s.content_sha256 for s in signals],
        },
        "pre_declared": {
            "directions": list(GRID_DIRECTIONS),
            "thresholds": list(GRID_THRESHOLDS),
            "toxicity_gate": True,
            "toxicity_threshold": float(DEFAULT_TOXICITY_THRESHOLD),
            "held_out_bars": HELD_OUT_BARS,
            "slice_policy": "full_tape (the aligned signal saturates in the tail, so no fixed tail slice is used)",
            "expected_windows_per_slice": "n/a (full tape; reported per window)",
            "go_criteria": [
                "(a) OOS Sharpe > max(orderflow-only, flat) on both windows",
                "(b) paired permutation p < 0.05 vs that control on both windows",
                "(c) block-bootstrap 95% CI excludes 0 on both windows",
                "(d) >=2 distinct time-varying levels with |IC| > 1e-9 on both windows",
            ],
            "permutation_perms": PERMUTATION_PERMS,
            "bootstrap_resamples": BOOTSTRAP_RESAMPLES,
            "bootstrap_block": BOOTSTRAP_BLOCK,
            "pbo_k_folds": PBO_K_FOLDS,
            "seed": SEED,
        },
        "windows": window_results,
        "aggregated_variants": aggregated,
        "statistical_defensibility": {
            "best_variant": best["variant"],
            "best_mean_oos_sharpe": float(best["mean_oos_sharpe"]),
            "per_window": defensibility,
            "bh_fdr": bh,
        },
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "any_variant_passed_all_windows": bool(any_pass),
        "code_paths": [
            "src/analytics/options_time_varying_signal.py",
            "src/analytics/integrated_options_orderflow_evaluation.py",
            "src/analytics/capacity_aware_tca.py",
            "src/data/options_candle_backfill.py",
            "scripts/eval41_options_timeseries_net_of_cost.py",
            "tests/test_eval41_options_timeseries_net_of_cost.py",
        ],
        "commands": [
            "export PYTHONPATH=\"$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}\"",
            "python3 -m py_compile scripts/eval41_options_timeseries_net_of_cost.py tests/test_eval41_options_timeseries_net_of_cost.py",
            "python3 -m pytest -q tests/test_eval41_options_timeseries_net_of_cost.py",
            "python3 scripts/eval41_options_timeseries_net_of_cost.py",
        ],
    }

    assert _all_finite(report), "non-finite values in report"
    serialized = serialize_metrics_strict(report)
    assert_json_valid(serialized)

    artifact_paths: Dict[str, str] = {}
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = _stamp_for_filename(generated_at)
        jpath = OUT_DIR / f"{REPORT_ID}_{stamp}.json"
        mpath = OUT_DIR / f"{REPORT_ID}_{stamp}.md"
        jpath.write_text(json.dumps(serialized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        md = build_md(serialized)
        mpath.write_text(md + "\n", encoding="utf-8")
        artifact_paths = {"json": str(jpath), "md": str(mpath)}
        serialized["artifact_paths"] = artifact_paths
        jpath.write_text(json.dumps(serialize_metrics_strict(serialized), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return serialized


def build_md(r: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {r['report_id']} — Dense options time-series net-of-cost decisive test (EVAL-41 Track B)")
    lines.append("")
    lines.append(f"- **Report ID:** `{r['report_id']}`")
    lines.append(f"- **Generated:** {r['generated_at']}")
    lines.append(f"- **Task ID:** `{r['task_id']}`")
    lines.append(f"- **Verdict:** **{r['verdict']}**")
    lines.append(f"- **Reason:** {r['verdict_reason']}")
    lines.append(f"- **Provenance:** {r['data_provenance']} (authenticity_verified={r['authenticity_verified']})")
    for c in r["provenance_caveats"]:
        lines.append(f"- Caveat: {c}")
    lines.append("")
    op = r["options_provenance"]
    lines.append("## Options inputs")
    lines.append(f"- Snapshots: {op['n_snapshots']}; distinct signal levels: {op['distinct_signal_levels']}")
    lines.append(f"- Window: {op['first_snapshot_utc']} → {op['last_snapshot_utc']}")
    lines.append("")
    for wr in r["windows"]:
        lines.append(f"## Window: {wr['window']} (`{wr['tape_path']}`)")
        lines.append(f"- Tape: {wr['n_bars_total']} bars, {wr['tape_start_utc']} → {wr['tape_end_utc']}")
        lines.append(f"- Held-out slice: {wr['held_out_n_bars']} bars, {wr['held_out_start_utc']} → {wr['held_out_end_utc']}")
        m = wr["measurement"]
        lines.append(f"- Distinct levels in slice: {m['distinct_signal_values']}; signal stdev: {m['signal_stdev']:.6f}")
        lines.append(f"- IC by horizon: {json.dumps(m['ic_by_horizon'], sort_keys=True)}")
        lines.append(f"- IC mean: {m['ic_mean']:.6e}; non_constant={m['non_constant']}")
        ctl = wr["controls"]
        lines.append(f"- Controls: best={ctl['best_control']} (Sharpe {ctl['best_control_sharpe']:.6f}); "
                     f"orderflow_only Sharpe {ctl['orderflow_only']['oos_sharpe']:.6f} ({ctl['orderflow_only']['num_trades']} trades); "
                     f"flat Sharpe {ctl['flat']['oos_sharpe']:.6f}")
        lines.append("")
        lines.append("| variant | Sharpe | trades | cost $ | perm p | CI | pass |")
        lines.append("|---|---|---|---|---|---|---|")
        for v in wr["variants"]:
            ci = v["bootstrap_ci"]
            lines.append(
                f"| {v['name']} | {v['oos_sharpe']:.4f} | {v['num_trades']} | "
                f"{v['total_cost_usd']:.2f} | {v['permutation_p']:.4f} | "
                f"[{ci[1]:.4f},{ci[2]:.4f}] | {v['window_pass']} |"
            )
        lines.append("")
    lines.append("## Aggregated variants")
    lines.append("| variant | mean Sharpe | passed both windows |")
    lines.append("|---|---|---|")
    for v in r["aggregated_variants"]:
        lines.append(f"| {v['variant']} | {v['mean_oos_sharpe']:.4f} | {v['passed_all_windows']} |")
    lines.append("")
    sd = r["statistical_defensibility"]
    lines.append("## Statistical defensibility")
    lines.append(f"- Best variant: {sd['best_variant']} (mean Sharpe {sd['best_mean_oos_sharpe']:.6f})")
    lines.append(f"- Per-window PBO/CI: {json.dumps(sd['per_window'], sort_keys=True)}")
    lines.append(f"- BH-FDR: {json.dumps(sd['bh_fdr'], sort_keys=True)}")
    lines.append("")
    lines.append("## Commands")
    for cmd in r["commands"]:
        lines.append(f"```bash\n{cmd}\n```")
    return "\n".join(lines)


def main(argv: Any = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    report = run_eval41(write=not args.no_write)
    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "verdict_reason": report["verdict_reason"],
        "any_variant_passed_all_windows": report["any_variant_passed_all_windows"],
        "artifact_paths": report.get("artifact_paths", {}),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())