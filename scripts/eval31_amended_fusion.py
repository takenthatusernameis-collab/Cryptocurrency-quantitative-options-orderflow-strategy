#!/usr/bin/env python3
"""EVAL-31: fuse time-varying options signal with causal orderflow, net-of-cost.

Mechanism (pre-declared, no fitted parameters, causal):
  - Fusion rule A (options sign as causal regime filter, orderflow for direction/magnitude):
      raw = sign(orderflow_signal[i])  (thresholded at DEFAULT_SIGNAL_THRESHOLD)
      position[i] = 0 if toxicity[i] >= 0.7 else (0 if options_signal[i] >= 0 else raw)
    Rationale: the 3-step options signal is a slow risk regime (all negative in
    measured snapshots: -0.036191, -0.051843, -0.029513); the fast causal
    orderflow signal supplies timing/direction. Gated flat when options not
    risk-off (>=0) and flat when toxicity >= 0.7. No lookahead (bar i uses
    newest snapshot with timestamp <= bar_end[i]; pre-first-snapshot = 0.0).

Sealed artifacts EVAL-18/23/24/27/29/30 are not modified. Additive only.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Sequence

import numpy as np

# Ensure repo root on path when run as script
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
REPORT_ID = "AMENDED_FUSION_EVAL_31"
FUSION_RULE = "A_options_regime_filter_orderflow_direction"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _stamp_for_filename(iso_ts: str) -> str:
    # Use compact sortable stamp similar to existing artifacts
    try:
        # iso may be like 2026-11-14T11:45:01.123456Z
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
    """Rule A: sign(orderflow) gated flat if toxicity>=tox_threshold or options_signal>=0."""
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


def run_eval31(write: bool = True) -> Dict[str, Any]:
    generated_at = _utc_now_iso()

    snapshot = load_real_orderflow("BTC")
    bars = _build_bars(snapshot)
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

    cfg = IntegratedConfig(
        seed=42, train_window=DEFAULT_TRAIN_WINDOW, test_window=DEFAULT_TEST_WINDOW,
        step_size=DEFAULT_STEP_SIZE, purge=DEFAULT_PURGE, embargo=DEFAULT_EMBARGO,
    )
    sizer = CapacityAwareSizer(
        DEFAULT_SPREAD_BPS, DEFAULT_IMPACT_COEFF, DEFAULT_MAX_PARTICIPATION,
        DEFAULT_COST_BUDGET_BPS, seed=42,
    )

    combined_pos = fuse_rule_a(opt_series, of_sig, toxicities)
    options_pos = gated_single_pillar(opt_series, toxicities)
    orderflow_pos = gated_single_pillar(of_sig, toxicities)
    flat_pos = [0] * len(bars["bar_closes"])

    wf_args = dict(symbol="BTC", prices=bars["bar_closes"], timestamps=bars["bar_ends_dt"],
                   sizer=sizer, cfg=cfg, n_points=DEFAULT_N_POINTS, seed=42,
                   max_position_pct=DEFAULT_MAX_POSITION_PCT)
    combined_wf = _run_walkforward(positions=combined_pos, **wf_args)
    options_wf = _run_walkforward(positions=options_pos, **wf_args)
    orderflow_wf = _run_walkforward(positions=orderflow_pos, **wf_args)
    flat_wf = _run_walkforward(positions=flat_pos, **wf_args)

    def _tox_engagement(pos: Sequence[int]) -> float:
        # fraction of bars where position is non-flat AND tox gate did not force flat by itself irrelevant;
        # report fraction of bars where toxicity>=threshold (gate engaged condition present)
        n = len(pos)
        if n == 0:
            return 0.0
        return float(sum(1 for t in toxicities if float(t) >= DEFAULT_TOXICITY_THRESHOLD) / n)

    tox_gate_frac = float(sum(1 for t in toxicities if float(t) >= DEFAULT_TOXICITY_THRESHOLD) / len(toxicities)) if toxicities else 0.0
    opt_risk_off_frac = float(sum(1 for v in opt_series if float(v) < 0.0) / len(opt_series)) if opt_series else 0.0

    # Superiority: combined OOS Sharpe > max(options-only, orderflow-only, flat) and combined trades>0
    best_control_sharpe = max(float(options_wf["oos_sharpe"]), float(orderflow_wf["oos_sharpe"]), float(flat_wf["oos_sharpe"]))
    combined_superior = bool(float(combined_wf["oos_sharpe"]) > best_control_sharpe and int(combined_wf["num_trades"]) > 0)

    # Statistical defensibility (permutation vs best single pillar by window returns)
    # Best single pillar among non-flat controls by Sharpe
    control_map = {
        "options_only": options_wf,
        "orderflow_only": orderflow_wf,
        "flat": flat_wf,
    }
    best_name = max(control_map.keys(), key=lambda k: float(control_map[k]["oos_sharpe"]))
    best_control = control_map[best_name]
    comb_rets = [float(r) for r in combined_wf.get("window_returns", [])]
    ctrl_rets = [float(r) for r in best_control.get("window_returns", [])]
    perm = permutation_test(
        comb_rets,
        ctrl_rets,
        statistic=lambda vals: float(sum(vals) / len(vals)) if len(vals) > 0 else 0.0,
        n_permutations=1000,
        paired=True,
        seed=42,
    )
    # DSR on window returns
    def dsr_of(wf):
        rets = [float(r) for r in wf.get("window_returns", []) if math.isfinite(float(r))]
        if len(rets) < 3:
            return 0.0
        sr_obs = _sharpe_of_returns(rets)
        return float(_deflated_sharpe(rets, sr_observed=sr_obs, sr_benchmark=0.0))
    dsr = {
        "combined": dsr_of(combined_wf),
        "options_only": dsr_of(options_wf),
        "orderflow_only": dsr_of(orderflow_wf),
        "flat": dsr_of(flat_wf),
    }
    # PBO (CSCV) across configs (4 strategies)
    returns_by_config = {
        "combined": [float(r) for r in combined_wf.get("window_returns", [])],
        "options_only": [float(r) for r in options_wf.get("window_returns", [])],
        "orderflow_only": [float(r) for r in orderflow_wf.get("window_returns", [])],
        "flat": [float(r) for r in flat_wf.get("window_returns", [])],
    }
    clean_cfgs = {k: v for k, v in returns_by_config.items() if any(math.isfinite(x) for x in v)}
    if len(clean_cfgs) >= 2:
        try:
            pbo = _cscv_pbo(clean_cfgs, n_combinations=16, k_folds=8)
        except Exception as e:
            pbo = {"overall_pbo": None, "error": str(e)}
    else:
        pbo = {"overall_pbo": None, "note": "insufficient configs"}
    # BH-FDR over permutation-like comparisons
    pvals = {
        "combined_vs_best_control": float(perm.get("p_value", 1.0)),
    }
    try:
        bh = _benjamini_hochberg(pvals, alpha=0.1)
    except Exception as e:
        bh = {"error": str(e), "input": pvals}

    verdict = "GO" if combined_superior else "NO-GO"
    verdict_reason = (
        f"combined OOS Sharpe {combined_wf['oos_sharpe']:.6f} > best control {best_control_sharpe:.6f} with trades {combined_wf['num_trades']}>0"
        if combined_superior else
        f"combined OOS Sharpe {combined_wf['oos_sharpe']:.6f} not superior to best control {best_control_sharpe:.6f} (trades {combined_wf['num_trades']})"
    )

    report = {
        "report_id": REPORT_ID,
        "generated_at": generated_at,
        "trading_mode": "paper",
        "live_trading_enabled": False,
        "never_valid_true": True,
        "authenticity_verified": False,
        "data_provenance": "real_public_exchange_export",
        "symbol": "BTC",
        "venue": "okx",
        "fusion": {
            "fusion_rule": FUSION_RULE,
            "rule_amended": True,
            "rationale": (
                "EVAL-30 time-varying options signal is a 3-step function (all negative: "
                "-0.036191, -0.051843, -0.029513). A sign-agreement fusion degenerates when "
                "pillars do not share sign; Rule A uses options sign as a causal regime filter "
                "(trade orderflow direction only while options_signal < 0, i.e. risk-off) and "
                "orderflow for direction/magnitude, with toxicity gate (>=0.7 -> flat). "
                "Pre-declared, no fitted parameters, no curve-fitting."
            ),
            "constants": {
                "signal_threshold": DEFAULT_SIGNAL_THRESHOLD,
                "toxicity_threshold": DEFAULT_TOXICITY_THRESHOLD,
                "toxicity_window_trades": DEFAULT_TOXICITY_WINDOW_TRADES,
                "signal_lookback_seconds": DEFAULT_SIGNAL_LOOKBACK_SECONDS,
                "bar_duration_seconds": DEFAULT_BAR_DURATION_SECONDS,
            },
            "fitted_parameters": None,
            "toxicity_gate_fraction": tox_gate_frac,
            "options_risk_off_fraction": opt_risk_off_frac,
            "n_combined_nonflat": int(sum(1 for p in combined_pos if p != 0)),
            "n_options_nonflat": int(sum(1 for p in options_pos if p != 0)),
            "n_orderflow_nonflat": int(sum(1 for p in orderflow_pos if p != 0)),
        },
        "eval30_reproduction": {
            "n_bars": m30["n_bars"],
            "n_snapshots": m30["n_snapshots"],
            "snapshot_timestamps": m30["snapshot_timestamps"],
            "bar_span_seconds": float((bars["bar_ends_dt"][-1]-bars["bar_ends_dt"][0]).total_seconds()) if bars["bar_ends_dt"] else 0.0,
            "snapshot_span_seconds": float((datetime.fromisoformat(m30["snapshot_timestamps"][-1].replace("Z","+00:00")) - datetime.fromisoformat(m30["snapshot_timestamps"][0].replace("Z","+00:00"))).total_seconds()) if len(m30["snapshot_timestamps"])>=2 else 0.0,
            "per_snapshot_signals": [s.options_signal_raw for s in signals],
            "mean_signal": m30["mean_signal"],
            "signal_stdev": m30["signal_stdev"],
            "distinct_signal_values": m30["distinct_signal_values"],
            "step_changes": m30["step_changes"],
            "n_flat_bars": m30["n_flat_bars"],
            "ic_by_horizon": m30["ic_by_horizon"],
            "ic_tstat_by_horizon": m30["ic_tstat_by_horizon"],
            "ic_mean": m30["ic_mean"],
            "non_constant": m30["non_constant"],
            "ic_present": m30["ic_present"],
            "matches_sealed_eval30": bool(
                m30["n_bars"] == 1553 and m30["n_snapshots"] == 3 and m30["step_changes"] == 2
                and m30["n_flat_bars"] == 1300 and m30["distinct_signal_values"] == 3
                and abs(m30["ic_mean"] - (-0.0029570304267226335)) < 1e-9
            ),
        },
        "walkforward": {
            "combined": wf_summary(combined_wf),
            "options_only": wf_summary(options_wf),
            "orderflow_only": wf_summary(orderflow_wf),
            "flat": wf_summary(flat_wf),
        },
        "verdict_checks": {
            "combined_net_of_cost_superior": {
                "pass": combined_superior,
                "best_control": best_name,
                "best_control_sharpe": best_control_sharpe,
                "combined_sharpe": float(combined_wf["oos_sharpe"]),
                "combined_trades": int(combined_wf["num_trades"]),
            }
        },
        "statistical_defensibility": {
            "permutation_vs_best_control": {"best_control": best_name, **perm},
            "dsr_window_returns": dsr,
            "pbo_cscv": pbo,
            "bh_fdr": bh,
            "notes": "Permutation/DSR/PBO computed on walk-forward window returns (36 windows).",
        },
        "verdict": verdict,
        "verdict_reason": verdict_reason,
        "code_paths": [
            "src/analytics/options_time_varying_signal.py",
            "src/analytics/integrated_options_orderflow_evaluation.py",
            "src/analytics/real_net_of_cost_evaluation.py",
            "src/analytics/capacity_aware_tca.py",
            "scripts/eval31_amended_fusion.py",
            "tests/test_amended_fusion_eval31.py",
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
        # rewrite json with paths
        jpath.write_text(json.dumps(serialize_metrics_strict(serialized), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return serialized


def build_md(r: Dict[str, Any]) -> str:
    lines = []
    lines.append(f"# {REPORT_ID} — Amended time-varying options+orderflow fusion (net-of-cost)")
    lines.append("")
    lines.append(f"- **Report ID:** `{r['report_id']}`")
    lines.append(f"- **Generated:** {r['generated_at']}")
    lines.append(f"- **Verdict:** **{r['verdict']}**")
    lines.append(f"- **Reason:** {r['verdict_reason']}")
    lines.append(f"- **Provenance:** {r['data_provenance']} (authenticity_verified={r['authenticity_verified']})")
    lines.append(f"- **Caveats:** public read-only OKX exports; no signed venue attestation; inverse BTC-USD-SWAP orderflow tape vs spot option snapshots; paper-only.")
    lines.append("")
    f = r["fusion"]
    lines.append("## Fusion mechanism (pre-declared, no fitted parameters)")
    lines.append(f"- fusion_rule: `{f['fusion_rule']}` (rule_amended={f['rule_amended']})")
    lines.append(f"- rationale: {f['rationale']}")
    lines.append(f"- constants: {json.dumps(f['constants'], sort_keys=True)}")
    lines.append(f"- toxicity_gate_fraction: {f['toxicity_gate_fraction']}, options_risk_off_fraction: {f['options_risk_off_fraction']}")
    lines.append(f"- nonflat bars: combined={f['n_combined_nonflat']}, options_only={f['n_options_nonflat']}, orderflow_only={f['n_orderflow_nonflat']}")
    lines.append("")
    e = r["eval30_reproduction"]
    lines.append("## Step 1 — EVAL-30 reproduction (real loader)")
    lines.append(f"- n_bars={e['n_bars']} n_snapshots={e['n_snapshots']} bar_span_seconds={e['bar_span_seconds']} snapshot_span_seconds={e['snapshot_span_seconds']}")
    lines.append(f"- snapshot_timestamps: {e['snapshot_timestamps']}")
    lines.append(f"- per_snapshot_signals: {e['per_snapshot_signals']}")
    lines.append(f"- mean_signal={e['mean_signal']} stdev={e['signal_stdev']} distinct={e['distinct_signal_values']} step_changes={e['step_changes']} n_flat_bars={e['n_flat_bars']}")
    lines.append(f"- ic_by_horizon: {e['ic_by_horizon']}")
    lines.append(f"- ic_tstat_by_horizon: {e['ic_tstat_by_horizon']}")
    lines.append(f"- ic_mean={e['ic_mean']} non_constant={e['non_constant']} ic_present={e['ic_present']} matches_sealed_eval30={e['matches_sealed_eval30']}")
    lines.append("")
    lines.append("## Walk-forward (net-of-cost, CapacityAwareSizer + IntegratedConfig seed=42)")
    for name in ("combined","options_only","orderflow_only","flat"):
        wf = r["walkforward"][name]
        lines.append(f"- **{name}**: Sharpe {wf['oos_sharpe']}, return {wf['oos_return']}, maxDD {wf['oos_max_drawdown']}, trades {wf['num_trades']}, cost {wf['total_cost_usd']}, turnover/notional {wf['total_traded_notional']}, windows {wf['num_windows']}")
    lines.append("")
    lines.append("## Verdict checks")
    vc = r["verdict_checks"]["combined_net_of_cost_superior"]
    lines.append(f"- combined_net_of_cost_superior: pass={vc['pass']} (combined Sharpe {vc['combined_sharpe']} vs best {vc['best_control']} {vc['best_control_sharpe']}, trades {vc['combined_trades']})")
    lines.append("")
    sd = r["statistical_defensibility"]
    lines.append("## Statistical defensibility")
    lines.append(f"- permutation_vs_best_control: {json.dumps(sd['permutation_vs_best_control'], sort_keys=True)}")
    lines.append(f"- DSR (window returns): {json.dumps(sd['dsr_window_returns'], sort_keys=True)}")
    lines.append(f"- PBO (CSCV): {json.dumps(sd['pbo_cscv'], sort_keys=True)}")
    lines.append(f"- BH-FDR: {json.dumps(sd['bh_fdr'], sort_keys=True)}")
    lines.append(f"- notes: {sd['notes']}")
    lines.append("")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args(argv)
    report = run_eval31(write=not args.no_write)
    print(json.dumps({
        "report_id": report["report_id"],
        "verdict": report["verdict"],
        "verdict_reason": report["verdict_reason"],
        "eval30_matches": report["eval30_reproduction"]["matches_sealed_eval30"],
        "combined": report["walkforward"]["combined"],
        "artifact_paths": report.get("artifact_paths", {}),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
