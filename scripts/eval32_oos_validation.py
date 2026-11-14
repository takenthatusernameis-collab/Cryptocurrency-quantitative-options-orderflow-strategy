#!/usr/bin/env python3
"""EVAL-32: rigorous out-of-sample validation of the marginal EVAL-31 GO.

This is mandatory heavy work, not discovery. It validates EVAL-31's Rule A fusion
(options sign as causal regime filter + causal orderflow direction/magnitude +
toxicity gate) on the STRICTLY HELD-OUT last 30% of the real 1553-bar series.

Pre-declared, no curve-fitting, no fitted parameters:
  - Split: chronological 70/30. Train bars [0, 1086] (through 2026-11-14T08:37:05Z),
    held-out test bars [1087, 1552] (from 2026-11-14T08:37:20Z).
  - Compute all four position series on the FULL 1553-bar series with the sealed
    causal functions (they are causal at every bar and preserve valid pre-segment
    history), then slice [1087:] for the held-out walk-forward.
  - Four configs: combined (Rule A), options-only, orderflow-only, flat (control).
  - Walk-forward uses the sealed CapacityAwareSizer + IntegratedConfig(seed=42,
    train_window=120, test_window=40, step_size=40, purge=10, embargo=5). On the
    466-bar held-out slice this yields exactly 9 windows.
  - Statistics on held-out walk-forward window returns:
      * permutation test vs best single-pillar control (1000 perms, paired, seed=42)
      * deflated Sharpe ratio at benchmarks 0.0 / 0.5 / 1.0
      * block bootstrap 95% CI on combined Sharpe (1000 resamples, block size=2)
      * PBO (CSCV) across the 4 configs, k_folds=4 (k_folds=8 is INVALID on this
        sample: valid_combinations==0 -> FAIL, not a 0.0 PASS)
      * BH-FDR over all permutation p-values
  - Pre-declared validation-GO criteria (ALL four must pass):
      (a) held-out combined OOS Sharpe > best control AND combined trades > 0
      (b) permutation p < 0.05 vs best control
      (c) bootstrap 95% CI for combined Sharpe excludes 0
      (d) PBO combined < 0.5 with valid_combinations > 0

A trustworthy NO-GO on validation is a full success. Fabricated GO, synthetic data
relabeled as real, or no new sealed measurement artifact = FAILED session.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

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
    _signal_positions,
    _toxicities_per_bar,
)
from src.analytics.options_time_varying_signal import (
    align_options_signal_to_bars,
    load_snapshot_signals,
    measure_time_varying_signal,
)
from src.analytics.real_walkforward_certification import _benjamini_hochberg, _cscv_pbo
from src.analytics.strategy_evaluation import block_bootstrap_ci, permutation_test
from src.analytics.strategy_falsification import _deflated_sharpe
from src.campaign.integrated import IntegratedConfig, load_real_orderflow
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

OUT_DIR = Path("research_state")
REPORT_ID = "EVAL_32_OOS_VALIDATION"
FUSION_RULE = "A_options_regime_filter_orderflow_direction"

# Fixed, pre-declared split (do not tune).
SPLIT_INDEX = 1087
HELD_OUT_START = SPLIT_INDEX
PERMUTATION_PERMS = 1000
BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_BLOCK = 2
PBO_K_FOLDS = 4
PBO_N_COMBINATIONS = 16
DSR_BENCHMARKS = (0.0, 0.5, 1.0)


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


def fuse_rule_a(options_series: Sequence[float], orderflow_series: Sequence[float],
                toxicities: Sequence[float], threshold: float = DEFAULT_SIGNAL_THRESHOLD,
                tox_threshold: float = DEFAULT_TOXICITY_THRESHOLD) -> List[int]:
    """Rule A (identical to EVAL-31): sign(orderflow) gated flat if toxicity>=tox
    threshold or options_signal>=0 (risk-off filter)."""
    of_pos = _signal_positions(orderflow_series, threshold=threshold)
    out: List[int] = []
    for i in range(len(of_pos)):
        tox = float(toxicities[i]) if i < len(toxicities) else 0.0
        opt = float(options_series[i]) if i < len(options_series) else 0.0
        if tox >= tox_threshold:
            out.append(0)
        elif opt >= 0.0:
            out.append(0)
        else:
            out.append(int(of_pos[i]))
    return out


def gated_single_pillar(series: Sequence[float], toxicities: Sequence[float],
                        threshold: float = DEFAULT_SIGNAL_THRESHOLD,
                        tox_threshold: float = DEFAULT_TOXICITY_THRESHOLD) -> List[int]:
    pos = _signal_positions(series, threshold=threshold)
    return [0 if float(toxicities[i]) >= tox_threshold else int(pos[i]) for i in range(len(pos))]


def wf_summary(wf: Dict[str, Any]) -> Dict[str, Any]:
    keys = ("oos_sharpe", "oos_return", "oos_max_drawdown", "num_trades",
            "total_cost_usd", "total_traded_notional", "num_windows")
    return {k: wf.get(k) for k in keys}


def _dsr_at_benchmarks(window_returns: Sequence[float]) -> Dict[str, float]:
    rets = [float(r) for r in window_returns if math.isfinite(float(r))]
    if len(rets) < 3:
        return {str(b): 0.0 for b in DSR_BENCHMARKS}
    sr_obs = _sharpe_of_returns(rets)
    out: Dict[str, float] = {}
    for b in DSR_BENCHMARKS:
        try:
            out[str(b)] = float(_deflated_sharpe(rets, sr_observed=sr_obs, sr_benchmark=float(b)))
        except Exception:
            out[str(b)] = 0.0
    return out


def evaluate_criteria(
    combined_sharpe: float,
    combined_trades: int,
    best_control_sharpe: float,
    perm_p: float,
    bootstrap_ci: Sequence[float],
    pbo_combined: float,
    pbo_valid_combinations: int,
) -> Dict[str, Any]:
    """Apply the four pre-declared validation-GO criteria (ALL must pass)."""
    lo, hi = float(bootstrap_ci[1]), float(bootstrap_ci[2])
    c_a = bool(combined_sharpe > best_control_sharpe and combined_trades > 0)
    c_b = bool(perm_p < 0.05)
    c_c = bool(lo > 0.0 or hi < 0.0)  # CI excludes 0
    c_d = bool(pbo_valid_combinations > 0 and pbo_combined < 0.5)
    passed = c_a and c_b and c_c and c_d
    return {
        "criteria": {
            "a_combined_superior_and_trades": c_a,
            "b_permutation_p_lt_0_05": c_b,
            "c_bootstrap_ci_excludes_zero": c_c,
            "d_pbo_combined_lt_0_5_valid": c_d,
        },
        "all_pass": passed,
        "validation_verdict": "GO" if passed else "NO-GO",
        "detail": {
            "combined_sharpe": float(combined_sharpe),
            "combined_trades": int(combined_trades),
            "best_control_sharpe": float(best_control_sharpe),
            "permutation_p": float(perm_p),
            "bootstrap_ci": [float(bootstrap_ci[0]), float(lo), float(hi)],
            "pbo_combined": float(pbo_combined),
            "pbo_valid_combinations": int(pbo_valid_combinations),
        },
    }


def run_eval32(write: bool = True) -> Dict[str, Any]:
    generated_at = _utc_now_iso()

    snapshot = load_real_orderflow("BTC")
    bars = _build_bars(snapshot)
    n_bars = len(bars["bar_closes"])
    signals = load_snapshot_signals("BTC")
    m30 = measure_time_varying_signal(signals, bars["bar_ends_dt"], bars["bar_closes"], horizons=HORIZONS)
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

    # Full-series causal positions (preserve valid pre-segment history), then slice.
    combined_pos_full = fuse_rule_a(opt_series, of_sig, toxicities)
    options_pos_full = gated_single_pillar(opt_series, toxicities)
    orderflow_pos_full = gated_single_pillar(of_sig, toxicities)
    flat_pos_full = [0] * n_bars

    s = HELD_OUT_START
    prices = bars["bar_closes"]
    timestamps = bars["bar_ends_dt"]

    def slice_positions(pos: Sequence[int]) -> List[int]:
        return [int(p) for p in pos[s:]]

    combined_pos = slice_positions(combined_pos_full)
    options_pos = slice_positions(options_pos_full)
    orderflow_pos = slice_positions(orderflow_pos_full)
    flat_pos = slice_positions(flat_pos_full)

    cfg = IntegratedConfig(
        seed=42, train_window=DEFAULT_TRAIN_WINDOW, test_window=DEFAULT_TEST_WINDOW,
        step_size=DEFAULT_STEP_SIZE, purge=DEFAULT_PURGE, embargo=DEFAULT_EMBARGO,
    )
    sizer = CapacityAwareSizer(
        DEFAULT_SPREAD_BPS, DEFAULT_IMPACT_COEFF, DEFAULT_MAX_PARTICIPATION,
        DEFAULT_COST_BUDGET_BPS, seed=42,
    )

    wf_args = dict(symbol="BTC", prices=prices[s:], timestamps=timestamps[s:],
                   sizer=sizer, cfg=cfg, n_points=DEFAULT_N_POINTS, seed=42,
                   max_position_pct=DEFAULT_MAX_POSITION_PCT)
    combined_wf = _run_walkforward(positions=combined_pos, **wf_args)
    options_wf = _run_walkforward(positions=options_pos, **wf_args)
    orderflow_wf = _run_walkforward(positions=orderflow_pos, **wf_args)
    flat_wf = _run_walkforward(positions=flat_pos, **wf_args)

    # --- Superiority on held-out ---
    control_map = {
        "options_only": options_wf,
        "orderflow_only": orderflow_wf,
        "flat": flat_wf,
    }
    best_name = max(control_map.keys(), key=lambda k: float(control_map[k]["oos_sharpe"]))
    best_control_sharpe = float(control_map[best_name]["oos_sharpe"])
    combined_sharpe = float(combined_wf["oos_sharpe"])
    combined_trades = int(combined_wf["num_trades"])

    comb_rets = [float(r) for r in combined_wf.get("window_returns", [])]
    ctrl_rets = [float(r) for r in control_map[best_name].get("window_returns", [])]

    # --- Permutation test vs best single-pillar control ---
    try:
        perm = permutation_test(
            comb_rets,
            ctrl_rets,
            statistic=_mean,
            n_permutations=PERMUTATION_PERMS,
            paired=True,
            seed=42,
        )
        perm_p = float(perm.get("p_value", 1.0))
    except Exception as e:
        perm = {"error": str(e), "p_value": 1.0}
        perm_p = 1.0

    # --- DSR at multiple benchmarks (combined) ---
    dsr_by_bench = _dsr_at_benchmarks(comb_rets)

    # --- Block bootstrap 95% CI on combined Sharpe ---
    try:
        boot = block_bootstrap_ci(
            comb_rets,
            statistic=_sharpe_of_returns,
            n_bootstrap=BOOTSTRAP_RESAMPLES,
            block_size=BOOTSTRAP_BLOCK,
            seed=42,
        )
        bootstrap_ci = [float(boot[0]), float(boot[1]), float(boot[2])]
    except Exception as e:
        bootstrap_ci = [0.0, 0.0, 0.0]
        bootstrap_ci_error = str(e)

    # --- PBO (CSCV) across the 4 configs, k_folds=4 ---
    returns_by_config = {
        "combined": comb_rets,
        "options_only": [float(r) for r in options_wf.get("window_returns", [])],
        "orderflow_only": [float(r) for r in orderflow_wf.get("window_returns", [])],
        "flat": [float(r) for r in flat_wf.get("window_returns", [])],
    }
    clean_cfgs = {k: v for k, v in returns_by_config.items()
                  if any(math.isfinite(x) for x in v) and len(v) >= PBO_K_FOLDS * 2}
    pbo_valid = _cscv_pbo(clean_cfgs, n_combinations=PBO_N_COMBINATIONS, k_folds=PBO_K_FOLDS)
    pbo_invalid = _cscv_pbo(clean_cfgs, n_combinations=PBO_N_COMBINATIONS, k_folds=8)
    pbo_combined = float(pbo_valid.get("pbo_per_config", {}).get("combined", 0.0))
    pbo_combined_valid_combos = int(
        pbo_valid.get("config_details", {}).get("combined", {}).get("valid_combinations", 0)
    )

    # --- BH-FDR over permutation p-values ---
    pvals = {"combined_vs_best_control": float(perm_p)}
    try:
        bh = _benjamini_hochberg(pvals, alpha=0.1)
    except Exception as e:
        bh = {"error": str(e), "input": pvals}

    # --- Pre-declared criteria ---
    criteria = evaluate_criteria(
        combined_sharpe=combined_sharpe,
        combined_trades=combined_trades,
        best_control_sharpe=best_control_sharpe,
        perm_p=perm_p,
        bootstrap_ci=bootstrap_ci,
        pbo_combined=pbo_combined,
        pbo_valid_combinations=pbo_combined_valid_combos,
    )

    # Toxicity/opt gating fractions on held-out
    held_tox = [float(t) for t in toxicities[s:]]
    held_opt = [float(v) for v in opt_series[s:]]
    tox_gate_frac = float(sum(1 for t in held_tox if t >= DEFAULT_TOXICITY_THRESHOLD) / len(held_tox)) if held_tox else 0.0
    opt_risk_off_frac = float(sum(1 for v in held_opt if v < 0.0) / len(held_opt)) if held_opt else 0.0

    split = {
        "n_bars_total": int(n_bars),
        "split_index": int(SPLIT_INDEX),
        "train_indices": [0, SPLIT_INDEX - 1],
        "train_n_bars": int(SPLIT_INDEX),
        "train_end_utc": bars["bar_ends_dt"][SPLIT_INDEX - 1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "held_out_indices": [HELD_OUT_START, n_bars - 1],
        "held_out_n_bars": int(n_bars - HELD_OUT_START),
        "held_out_start_utc": bars["bar_ends_dt"][HELD_OUT_START].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "held_out_end_utc": bars["bar_ends_dt"][-1].strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "chronological": True,
        "no_lookahead": True,
        "slice_mechanism": "positions computed on full 1553-bar causal series, then sliced [1087:]",
    }

    report = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "task_id": "INIT-2026-11-14T12:38:04Z-EVAL-32-OOS-VALIDATION-MARGINAL-GO",
        "trading_mode": "paper",
        "live_trading_enabled": False,
        "never_valid_true": True,
        "authenticity_verified": False,
        "data_provenance": "real_public_exchange_export",
        "symbol": "BTC",
        "venue": "okx",
        "provenance_caveats": [
            "Public read-only OKX exports; no signed venue attestation.",
            "Inverse BTC-USD-SWAP orderflow tape vs spot option snapshots.",
            "Paper-only; no live trading; .env absent.",
        ],
        "fusion": {
            "fusion_rule": FUSION_RULE,
            "constants": {
                "signal_threshold": DEFAULT_SIGNAL_THRESHOLD,
                "toxicity_threshold": DEFAULT_TOXICITY_THRESHOLD,
                "toxicity_window_trades": DEFAULT_TOXICITY_WINDOW_TRADES,
                "signal_lookback_seconds": DEFAULT_SIGNAL_LOOKBACK_SECONDS,
                "train_window": DEFAULT_TRAIN_WINDOW,
                "test_window": DEFAULT_TEST_WINDOW,
                "step_size": DEFAULT_STEP_SIZE,
                "purge": DEFAULT_PURGE,
                "embargo": DEFAULT_EMBARGO,
                "n_points": DEFAULT_N_POINTS,
                "max_position_pct": DEFAULT_MAX_POSITION_PCT,
                "seed": 42,
            },
            "fitted_parameters": None,
            "toxicity_gate_fraction_held_out": tox_gate_frac,
            "options_risk_off_fraction_held_out": opt_risk_off_frac,
            "n_combined_nonflat_held_out": int(sum(1 for p in combined_pos if p != 0)),
            "n_options_nonflat_held_out": int(sum(1 for p in options_pos if p != 0)),
            "n_orderflow_nonflat_held_out": int(sum(1 for p in orderflow_pos if p != 0)),
        },
        "eval30_reproduction": {
            "n_bars": m30["n_bars"],
            "n_snapshots": m30["n_snapshots"],
            "per_snapshot_signals": [s.options_signal_raw for s in signals],
            "mean_signal": m30["mean_signal"],
            "ic_mean": m30["ic_mean"],
            "non_constant": m30["non_constant"],
            "ic_present": m30["ic_present"],
            "matches_sealed_eval30": bool(
                m30["n_bars"] == 1553 and m30["n_snapshots"] == 3
                and m30["step_changes"] == 2 and m30["n_flat_bars"] == 1300
                and m30["distinct_signal_values"] == 3
            ),
        },
        "split": split,
        "walkforward_held_out": {
            "combined": wf_summary(combined_wf),
            "options_only": wf_summary(options_wf),
            "orderflow_only": wf_summary(orderflow_wf),
            "flat": wf_summary(flat_wf),
            "num_windows_by_config": {
                "combined": int(combined_wf["num_windows"]),
                "options_only": int(options_wf["num_windows"]),
                "orderflow_only": int(orderflow_wf["num_windows"]),
                "flat": int(flat_wf["num_windows"]),
            },
            "window_returns": {
                "combined": comb_rets,
                "options_only": [float(r) for r in options_wf.get("window_returns", [])],
                "orderflow_only": [float(r) for r in orderflow_wf.get("window_returns", [])],
                "flat": [float(r) for r in flat_wf.get("window_returns", [])],
            },
        },
        "statistical_defensibility": {
            "permutation_vs_best_control": {"best_control": best_name, **perm},
            "dsr_window_returns_by_benchmark": dsr_by_bench,
            "bootstrap_ci_combined_sharpe": {
                "n_bootstrap": BOOTSTRAP_RESAMPLES,
                "block_size": BOOTSTRAP_BLOCK,
                "ci": bootstrap_ci,
                "excludes_zero": bool(bootstrap_ci[1] > 0.0 or bootstrap_ci[2] < 0.0),
            },
            "pbo_cscv_k4": {
                "overall_pbo": pbo_valid.get("overall_pbo"),
                "pbo_per_config": pbo_valid.get("pbo_per_config"),
                "config_valid_combinations": {
                    k: int(v.get("valid_combinations", 0))
                    for k, v in pbo_valid.get("config_details", {}).items()
                },
                "k_folds": PBO_K_FOLDS,
            },
            "pbo_cscv_k8_invalid": {
                "note": "k_folds=8 on 466-bar held-out yields valid_combinations=0 -> INVALID; not a pass.",
                "config_valid_combinations": {
                    k: int(v.get("valid_combinations", 0))
                    for k, v in pbo_invalid.get("config_details", {}).items()
                },
                "k_folds": 8,
            },
            "bh_fdr": bh,
        },
        "validation_criteria": criteria,
        "verdict": criteria["validation_verdict"],
        "verdict_reason": (
            f"Held-out validation {'GO' if criteria['all_pass'] else 'NO-GO'}: "
            f"combined Sharpe {combined_sharpe:.6f} vs best control {best_control_sharpe:.6f} "
            f"({best_name}), trades {combined_trades}, perm p={perm_p:.4f}, "
            f"bootstrap CI [{bootstrap_ci[1]:.4f},{bootstrap_ci[2]:.4f}], "
            f"PBO combined={pbo_combined:.4f} (valid_combos={pbo_combined_valid_combos})."
        ),
        "code_paths": [
            "src/analytics/options_time_varying_signal.py",
            "src/analytics/integrated_options_orderflow_evaluation.py",
            "src/analytics/real_walkforward_certification.py",
            "src/analytics/strategy_evaluation.py",
            "src/analytics/strategy_falsification.py",
            "scripts/eval31_amended_fusion.py",
            "scripts/eval32_oos_validation.py",
            "tests/test_eval32_oos_validation.py",
        ],
        "commands": [
            "python3 -m py_compile src/analytics/options_time_varying_signal.py scripts/eval31_amended_fusion.py scripts/eval32_oos_validation.py tests/test_eval32_oos_validation.py",
            "python3 -m pytest -q tests/test_eval32_oos_validation.py",
            "python3 scripts/eval32_oos_validation.py",
        ],
    }

    assert _all_finite(report), "non-finite values in report"
    serialized = serialize_metrics_strict(report)
    assert_json_valid(serialized)

    artifact_paths = {}
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
    lines = []
    lines.append(f"# {r['report_id']} — OOS validation of marginal EVAL-31 GO (held-out 30%)")
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
    sp = r["split"]
    lines.append("## Split (chronological, no lookahead)")
    lines.append(f"- Total bars: {sp['n_bars_total']}; split index {sp['split_index']}.")
    lines.append(f"- Train: bars {sp['train_indices'][0]}..{sp['train_indices'][1]} ({sp['train_n_bars']} bars, through {sp['train_end_utc']}).")
    lines.append(f"- Held-out: bars {sp['held_out_indices'][0]}..{sp['held_out_indices'][1]} ({sp['held_out_n_bars']} bars, {sp['held_out_start_utc']} → {sp['held_out_end_utc']}).")
    lines.append(f"- Mechanism: {sp['slice_mechanism']}.")
    lines.append("")
    f = r["fusion"]
    lines.append("## Fusion (pre-declared, no fitted parameters)")
    lines.append(f"- fusion_rule: `{f['fusion_rule']}`")
    lines.append(f"- constants: {json.dumps(f['constants'], sort_keys=True)}")
    lines.append(f"- held-out nonflat bars: combined={f['n_combined_nonflat_held_out']}, options_only={f['n_options_nonflat_held_out']}, orderflow_only={f['n_orderflow_nonflat_held_out']}")
    lines.append(f"- toxicity gate fraction (held-out): {f['toxicity_gate_fraction_held_out']}; options risk-off fraction: {f['options_risk_off_fraction_held_out']}")
    lines.append("")
    wf = r["walkforward_held_out"]
    lines.append("## Held-out walk-forward (net-of-cost, seed=42)")
    lines.append(f"- num_windows by config: {json.dumps(wf['num_windows_by_config'], sort_keys=True)}")
    for name in ("combined", "options_only", "orderflow_only", "flat"):
        w = wf[name]
        lines.append(f"- **{name}**: Sharpe {w['oos_sharpe']}, return {w['oos_return']}, maxDD {w['oos_max_drawdown']}, trades {w['num_trades']}, cost ${w['total_cost_usd']}, notional ${w['total_traded_notional']}")
    lines.append("")
    sd = r["statistical_defensibility"]
    lines.append("## Statistical defensibility (pre-declared)")
    lines.append(f"- permutation vs {sd['permutation_vs_best_control']['best_control']}: {json.dumps(sd['permutation_vs_best_control'], sort_keys=True)}")
    lines.append(f"- DSR by benchmark: {json.dumps(sd['dsr_window_returns_by_benchmark'], sort_keys=True)}")
    lines.append(f"- bootstrap CI: {json.dumps(sd['bootstrap_ci_combined_sharpe'], sort_keys=True)}")
    lines.append(f"- PBO (k_folds=4): {json.dumps(sd['pbo_cscv_k4'], sort_keys=True)}")
    lines.append(f"- PBO (k_folds=8, invalid): {json.dumps(sd['pbo_cscv_k8_invalid'], sort_keys=True)}")
    lines.append(f"- BH-FDR: {json.dumps(sd['bh_fdr'], sort_keys=True)}")
    lines.append("")
    vc = r["validation_criteria"]
    lines.append("## Pre-declared validation criteria (ALL must pass)")
    for k, v in vc["criteria"].items():
        lines.append(f"- {k}: {v}")
    lines.append(f"- **all_pass: {vc['all_pass']}**")
    lines.append("")
    lines.append("## Verdict")
    lines.append(f"- **{r['verdict']}** — {r['verdict_reason']}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    report = run_eval32(write=not args.no_write)
    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "verdict_reason": report["verdict_reason"],
        "walkforward_held_out": report["walkforward_held_out"]["combined"],
        "num_windows_by_config": report["walkforward_held_out"]["num_windows_by_config"],
        "validation_criteria": report["validation_criteria"]["criteria"],
        "artifact_paths": report.get("artifact_paths", {}),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())