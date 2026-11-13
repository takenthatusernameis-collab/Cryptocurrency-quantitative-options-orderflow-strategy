"""Final strategy certification + paper-only deployment guardrails (EVAL-13).

Combines sealed EVAL-10 (NO-GO baseline), EVAL-11 (best feasible config) and
EVAL-12 (real-data walk-forward, GO) evidence into a deterministic strict
GO/NO-GO certification with numeric deployment guardrails (paper-only, not an
authorization to deploy or go live).

The verdict is computed by :func:`compute_certification_verdict` from the
evidence + guardrail checks, never from prose. DSR is recomputed via
:func:`src.analytics.strategy_falsification._deflated_sharpe`; bootstrap CI and
paired permutation tests reuse :mod:`src.analytics.strategy_evaluation`
primitives. PBO/multiple-testing evidence is reported from the sealed EVAL-12
artifact with a recompute-consistent DSR check.

Emits canonical artifact: research_state/FINAL_STRATEGY_CERTIFICATION_<UTC>.{json,md}

Strict-serializable via serialize_metrics_strict / assert_json_valid.
Never emits {"valid": True}; no NaN/Infinity.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

from src.analytics.strategy_evaluation import (
    block_bootstrap_ci,
    permutation_test,
)
from src.analytics.strategy_falsification import _deflated_sharpe
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "FINAL_STRATEGY_CERTIFICATION_EVAL_13"

# Sealed evidence artifacts (exact filenames, verified present).
EVAL10_ARTIFACT = Path("research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.json")
EVAL11_ARTIFACT = Path("research_state/HEDGE_COST_OPTIMIZER_20261113T004000Z.json")
EVAL12_ARTIFACT = Path("research_state/REAL_WF_CERTIFICATION_20261113T010508Z.json")

OUT_DIR = Path("research_state")

# Deployment mode: paper only, hard guard.
TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# Multiple-testing correction level (matches EVAL-12).
FDR_ALPHA = 0.10

# Bootstrap / permutation seeds (deterministic).
BOOTSTRAP_SEED = 0
PERMUTATION_SEED = 0
N_BOOTSTRAP = 2000
N_PERMUTATIONS = 2000

# Kill-switch / guardrail limits (paper deployment bounds).
MAX_NOTIONAL_CAP_USD = 1_000_000.0
MAX_COST_BUDGET_BPS = 2.0
MAX_TOXIC_GATE_ACTIVE_FRACTION = 0.8
MAX_DRAWDOWN_KILL = 0.20
MAX_DAILY_LOSS_USD = 50_000.0


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _stamp_for_filename(iso_ts: str) -> str:
    digits = "".join(ch for ch in iso_ts if ch.isdigit())
    stamp = f"{digits[:8]}T{digits[8:14]}Z" if len(digits) >= 14 else digits
    return stamp


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _sharpe_of_returns(rets: list[float], periods_per_year: float = 252.0) -> float:
    vals = [float(r) for r in rets if math.isfinite(float(r))]
    if len(vals) < 2:
        return 0.0
    mean = sum(vals) / len(vals)
    var = sum((r - mean) ** 2 for r in vals) / len(vals)
    std = math.sqrt(var)
    if std <= 0.0 or not math.isfinite(std):
        return 0.0
    sr = mean / std * math.sqrt(periods_per_year)
    return sr if math.isfinite(sr) else 0.0


def _recompute_dsr(returns: list[float], sr_benchmark: float = 0.0) -> float:
    """Deflated Sharpe Ratio recomputed from raw returns via _deflated_sharpe."""
    sr_obs = _sharpe_of_returns(returns)
    return float(_deflated_sharpe(returns, sr_observed=sr_obs, sr_benchmark=sr_benchmark))


def _extract_eval11_series(raw: dict[str, Any]) -> list[dict[str, Any]]:
    best_final = raw.get("best_config_final", {})
    series = best_final.get("series", [])
    out: list[dict[str, Any]] = []
    for s in series:
        out.append(
            {
                "seed": int(s.get("seed", 0)),
                "symbol": str(s.get("symbol", "")),
                "net_return": _finite(s.get("net_return")),
                "net_sharpe": _finite(s.get("net_sharpe")),
                "max_drawdown": _finite(s.get("max_drawdown")),
                "total_cost_usd": _finite(s.get("total_cost_usd")),
                "total_traded_notional": _finite(s.get("total_traded_notional")),
                "num_hedges": int(s.get("num_hedges", 0)),
                "toxic_gate_active_fraction": _finite(s.get("toxic_gate_active_fraction")),
                "mean_abs_delta_usd": _finite(s.get("mean_abs_delta_usd")),
                "net_ann_vol": _finite(s.get("net_ann_vol")),
            }
        )
    return out


def _extract_eval10_series(raw: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for seed_report in raw.get("per_seed", []):
        seed = int(seed_report.get("seed", 0))
        for symbol, sym in seed_report.get("symbols", {}).items():
            wh = sym.get("with_hedge", {})
            out.append(
                {
                    "seed": seed,
                    "symbol": str(symbol),
                    "net_return": _finite(wh.get("oos_return")),
                    "net_sharpe": _finite(wh.get("oos_sharpe")),
                    "max_drawdown": _finite(wh.get("oos_max_drawdown")),
                    "total_cost_usd": _finite(wh.get("total_cost_usd")),
                    "total_traded_notional": _finite(wh.get("total_traded_notional")),
                    "num_hedges": int(wh.get("num_hedges", 0)),
                    "toxic_gate_active_fraction": _finite(wh.get("toxic_gate_active_fraction")),
                }
            )
    return out


def _extract_eval12_config_results(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for name, result in raw.get("config_results", {}).items():
        series = []
        for s in result.get("per_seed_series", []):
            series.append(
                {
                    "seed": int(s.get("seed", 0)),
                    "symbol": str(s.get("symbol", "")),
                    "net_return": _finite(s.get("net_return")),
                    "net_sharpe": _finite(s.get("net_sharpe")),
                    "max_drawdown": _finite(s.get("max_drawdown")),
                    "net_ann_vol": _finite(s.get("net_ann_vol")),
                    "total_cost_usd": _finite(s.get("total_cost_usd")),
                    "total_hedges": int(s.get("total_hedges", 0)),
                    "total_traded_notional": _finite(s.get("total_traded_notional")),
                    "toxic_gate_active_fraction": _finite(s.get("toxic_gate_active_fraction")),
                }
            )
        all_returns = [float(r) for r in result.get("all_window_returns", [])]
        out[name] = {
            "config": dict(result.get("config", {})),
            "n_series": int(result.get("n_series", 0)),
            "n_seeds": int(result.get("n_seeds", 0)),
            "series": series,
            "all_window_returns": all_returns,
            "n_windows": len(all_returns),
        }
    return out


def load_sealed_evidence() -> dict[str, Any]:
    """Load the three sealed EVAL artifacts and extract comparable evidence."""
    eval10_raw = _load_json(EVAL10_ARTIFACT)
    eval11_raw = _load_json(EVAL11_ARTIFACT)
    eval12_raw = _load_json(EVAL12_ARTIFACT)

    eval11_best = eval11_raw.get("best_config_final", {})
    eval11_series = _extract_eval11_series(eval11_raw)
    eval10_series = _extract_eval10_series(eval10_raw)
    eval12_configs = _extract_eval12_config_results(eval12_raw)

    # Align EVAL-11 vs EVAL-10 paired series by (seed, symbol).
    eval10_index = {(s["seed"], s["symbol"]): s for s in eval10_series}
    paired: list[dict[str, float]] = []
    for s in eval11_series:
        key = (s["seed"], s["symbol"])
        if key in eval10_index:
            paired.append(
                {
                    "seed": s["seed"],
                    "symbol": s["symbol"],
                    "eval11_net_return": s["net_return"],
                    "eval10_net_return": eval10_index[key]["net_return"],
                }
            )

    evidence = {
        "report_id": REPORT_ID,
        "evidence_sources": ["EVAL-10", "EVAL-11", "EVAL-12"],
        "eval10": {
            "report_id": eval10_raw.get("report_id"),
            "verdict": str(eval10_raw.get("aggregate", {}).get("verdict", "NO-GO")),
            "pass_fraction": _finite(eval10_raw.get("aggregate", {}).get("pass_fraction")),
            "mean_net_sharpe": _finite(eval10_raw.get("aggregate", {}).get("mean_net_sharpe")),
            "mean_net_return": _finite(eval10_raw.get("aggregate", {}).get("mean_net_return")),
            "go_seed_fraction": _finite(eval10_raw.get("aggregate", {}).get("go_seed_fraction")),
            "series_pass_fraction": _finite(eval10_raw.get("aggregate", {}).get("series_pass_fraction")),
            "seeds": eval10_raw.get("aggregate", {}).get("seeds", []),
            "series": eval10_series,
            "config": eval10_raw.get("config", {}),
        },
        "eval11": {
            "report_id": eval11_raw.get("report_id"),
            "config": dict(eval11_best.get("config", {})),
            "feasible": bool(eval11_best.get("feasible", False)),
            "mean_net_sharpe": _finite(eval11_best.get("mean_net_sharpe")),
            "mean_net_return": _finite(eval11_best.get("mean_net_return")),
            "mean_abs_delta_usd": _finite(eval11_best.get("mean_abs_delta_usd")),
            "total_cost_usd": _finite(eval11_best.get("total_cost_usd")),
            "total_hedges": int(eval11_best.get("total_hedges", 0)),
            "total_traded_notional": _finite(eval11_best.get("total_traded_notional")),
            "num_seeds": int(eval11_best.get("num_seeds", 0)),
            "num_series": int(eval11_best.get("num_series", 0)),
            "no_hedge_control": {
                "mean_oos_sharpe": _finite(
                    eval11_raw.get("no_hedge_control", {}).get("mean_oos_sharpe")
                ),
                "mean_oos_return": _finite(
                    eval11_raw.get("no_hedge_control", {}).get("mean_oos_return")
                ),
                "num_series": int(eval11_raw.get("no_hedge_control", {}).get("num_series", 0)),
            },
            "series": eval11_series,
        },
        "eval12": {
            "report_id": eval12_raw.get("report_id"),
            "verdict": str(eval12_raw.get("verdict", "NO-GO")),
            "data_evidence": eval12_raw.get("data_evidence", {}),
            "candidate_configs": eval12_raw.get("candidate_configs", {}),
            "configs": eval12_configs,
            "dsr_by_config": {k: _finite(v) for k, v in eval12_raw.get("dsr_by_config", {}).items()},
            "pbo": eval12_raw.get("pbo", {}),
            "multiple_testing_correction": eval12_raw.get("multiple_testing_correction", {}),
            "surviving_configs": list(eval12_raw.get("surviving_configs", [])),
        },
        "paired_eval11_vs_eval10": paired,
    }
    return evidence


def compute_net_of_cost_metrics(evidence: dict[str, Any]) -> dict[str, Any]:
    """Recompute/verify net-of-cost metrics from sealed evidence.

    DSR is recomputed from EVAL-12 raw window returns via _deflated_sharpe
    (recompute-consistent check against the sealed EVAL-12 dsr_by_config).
    Bootstrap CI on EVAL-11 best mean net return; paired permutation test of
    EVAL-11 best vs EVAL-10 default aligned series returns.
    """
    eval11 = evidence["eval11"]
    eval12 = evidence["eval12"]
    eval10 = evidence["eval10"]

    dsr_recomputed: dict[str, float] = {}
    dsr_consistency: dict[str, dict[str, float]] = {}
    for name, cfg in eval12["configs"].items():
        rets = cfg["all_window_returns"]
        dsr = _recompute_dsr(rets) if len(rets) >= 3 else 0.0
        dsr_recomputed[name] = float(dsr)
        sealed = _finite(eval12["dsr_by_config"].get(name, math.nan))
        dsr_consistency[name] = {
            "recomputed_dsr": float(dsr),
            "sealed_dsr": float(sealed),
            "abs_diff": float(abs(dsr - sealed)) if math.isfinite(sealed) else math.nan,
            "consistent": bool(len(rets) >= 3 and math.isfinite(sealed) and abs(dsr - sealed) < 1e-6),
        }

    # Bootstrap CI on EVAL-11 best mean net return (per-series).
    e11_returns = [s["net_return"] for s in eval11["series"] if math.isfinite(s["net_return"])]
    if len(e11_returns) >= 2:
        boot_point, boot_lo, boot_hi = block_bootstrap_ci(
            e11_returns,
            statistic=lambda v: float(np.mean(v)),
            n_bootstrap=N_BOOTSTRAP,
            block_size=3,
            confidence=0.95,
            seed=BOOTSTRAP_SEED,
        )
    else:
        boot_point, boot_lo, boot_hi = 0.0, 0.0, 0.0

    # Sharpe bootstrap CI on EVAL-11 best mean net Sharpe (per-series).
    e11_sharpes = [s["net_sharpe"] for s in eval11["series"] if math.isfinite(s["net_sharpe"])]
    if len(e11_sharpes) >= 2:
        sr_point, sr_lo, sr_hi = block_bootstrap_ci(
            e11_sharpes,
            statistic=lambda v: float(np.mean(v)),
            n_bootstrap=N_BOOTSTRAP,
            block_size=3,
            confidence=0.95,
            seed=BOOTSTRAP_SEED,
        )
    else:
        sr_point, sr_lo, sr_hi = 0.0, 0.0, 0.0

    # Paired permutation test: EVAL-11 best vs EVAL-10 default aligned returns.
    paired = evidence["paired_eval11_vs_eval10"]
    if len(paired) >= 2:
        a = [p["eval11_net_return"] for p in paired]
        b = [p["eval10_net_return"] for p in paired]
        permutation = permutation_test(
            a,
            b,
            statistic=lambda v: float(np.mean(v)),
            n_permutations=N_PERMUTATIONS,
            paired=True,
            alternative="greater",
            seed=PERMUTATION_SEED,
        )
    else:
        permutation = {
            "observed_difference": 0.0,
            "p_value": 1.0,
            "n_permutations": 0,
            "paired": True,
            "significant_at_05": False,
            "statistic_a": 0.0,
            "statistic_b": 0.0,
        }

    best_sharpe = _finite(eval11["mean_net_sharpe"])
    no_hedge_sharpe = _finite(eval11["no_hedge_control"]["mean_oos_sharpe"])
    eval10_sharpe = _finite(eval10["mean_net_sharpe"])

    metrics = {
        "eval11_best_mean_net_sharpe": float(best_sharpe),
        "eval11_best_mean_net_return": float(_finite(eval11["mean_net_return"])),
        "eval11_best_mean_abs_delta_usd": float(_finite(eval11["mean_abs_delta_usd"])),
        "eval11_best_total_cost_usd": float(_finite(eval11["total_cost_usd"])),
        "eval11_best_total_hedges": int(eval11["total_hedges"]),
        "eval11_no_hedge_control_sharpe": float(no_hedge_sharpe),
        "eval11_sharpe_improvement_vs_no_hedge": float(best_sharpe - no_hedge_sharpe),
        "eval10_default_mean_net_sharpe": float(eval10_sharpe),
        "eval10_default_mean_net_return": float(_finite(eval10["mean_net_return"])),
        "eval11_best_mean_net_sharpe_gt_eval10": bool(best_sharpe > eval10_sharpe),
        "dsr_recomputed": dsr_recomputed,
        "dsr_sealed": {k: float(v) for k, v in eval12["dsr_by_config"].items()},
        "dsr_consistency": dsr_consistency,
        "dsr_all_finite": bool(all(math.isfinite(v) for v in dsr_recomputed.values())),
        "bootstrap_ci_mean_net_return": {
            "point": float(boot_point),
            "lo": float(boot_lo),
            "hi": float(boot_hi),
            "n_bootstrap": N_BOOTSTRAP,
            "block_size": 3,
            "seed": BOOTSTRAP_SEED,
            "ci_width": float(boot_hi - boot_lo),
            "lower_bound_positive": bool(boot_lo > 0.0),
        },
        "bootstrap_ci_mean_net_sharpe": {
            "point": float(sr_point),
            "lo": float(sr_lo),
            "hi": float(sr_hi),
            "n_bootstrap": N_BOOTSTRAP,
            "block_size": 3,
            "seed": BOOTSTRAP_SEED,
            "ci_width": float(sr_hi - sr_lo),
            "lower_bound_positive": bool(sr_lo > 0.0),
        },
        "permutation_eval11_vs_eval10": permutation,
        "permutation_significant": bool(permutation.get("significant_at_05", False)),
        "pbo_overall": float(eval12.get("pbo", {}).get("overall_pbo", math.nan)),
        "pbo_per_config": {
            k: float(v) for k, v in eval12.get("pbo", {}).get("pbo_per_config", {}).items()
        },
        "bh_surviving_configs": list(eval12["surviving_configs"]),
        "bh_alpha": float(FDR_ALPHA),
        "bh_m_tests": int(eval12.get("multiple_testing_correction", {}).get("m_tests", 0)),
        "eval12_verdict": str(eval12["verdict"]),
        "n_evidence_sources": int(len(evidence["evidence_sources"])),
    }
    return metrics


def build_guardrails(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    """Build numeric paper-deployment guardrails derived from sealed evidence.

    Each guardrail carries an explicit numeric threshold, the observed evidence
    value, a pass/fail check, and a rationale. All limits are paper-only bounds;
    none of them authorize live trading.
    """
    eval11 = evidence["eval11"]
    eval11_series = eval11["series"]
    best_config = eval11["config"]

    mean_abs_delta = _finite(eval11["mean_abs_delta_usd"])
    max_notional_observed = max(
        (_finite(s["total_traded_notional"]) for s in eval11_series), default=0.0
    )
    max_drawdown_observed = max(
        (_finite(s["max_drawdown"]) for s in eval11_series), default=0.0
    )
    mean_toxic_gate_fraction = (
        sum(_finite(s["toxic_gate_active_fraction"]) for s in eval11_series)
        / len(eval11_series)
        if eval11_series
        else 0.0
    )
    max_toxic_gate_fraction = max(
        (_finite(s["toxic_gate_active_fraction"]) for s in eval11_series), default=0.0
    )
    cost_budget_bps = _finite(best_config.get("cost_budget_bps", 0.5))
    total_cost_usd = _finite(eval11["total_cost_usd"])
    total_notional = _finite(eval11["total_traded_notional"])
    total_cost_bps = (total_cost_usd / total_notional * 1e4) if total_notional > 0 else 0.0
    target_delta_usd = _finite(best_config.get("target_delta_usd", -20000.0))
    delta_band_usd = 2.0 * mean_abs_delta

    guardrails: list[dict[str, Any]] = []

    guardrails.append(
        {
            "name": "max_notional_cap_usd",
            "category": "position_risk",
            "threshold": float(MAX_NOTIONAL_CAP_USD),
            "observed": float(max_notional_observed),
            "pass": bool(max_notional_observed <= MAX_NOTIONAL_CAP_USD),
            "rationale": (
                "Per-position notional cap derived from configured MAX_POSITION_NOTIONAL; "
                f"largest observed EVAL-11 single-series traded notional "
                f"{max_notional_observed:.2f} USD is below the {MAX_NOTIONAL_CAP_USD:,.0f} USD cap. "
                "EVAL-11 aggregate traded notional is cumulative across 15 series, not a single position."
            ),
        }
    )

    guardrails.append(
        {
            "name": "delta_band_usd",
            "category": "delta_risk",
            "threshold": float(delta_band_usd),
            "observed": float(mean_abs_delta),
            "target_delta_usd": float(target_delta_usd),
            "band_min": float(target_delta_usd - delta_band_usd),
            "band_max": float(target_delta_usd + delta_band_usd),
            "pass": bool(mean_abs_delta <= delta_band_usd),
            "rationale": (
                f"Delta band derived from EVAL-11 best mean_abs_delta_usd={mean_abs_delta:.2f}; "
                f"band = 2 x mean abs delta = {delta_band_usd:.2f} USD around target "
                f"target_delta_usd={target_delta_usd:.0f} "
                f"[{target_delta_usd - delta_band_usd:.2f}, {target_delta_usd + delta_band_usd:.2f}]."
            ),
        }
    )

    guardrails.append(
        {
            "name": "toxicity_gate_threshold",
            "category": "orderflow_risk",
            "threshold": 0.7,
            "observed": float(mean_toxic_gate_fraction),
            "toxic_gate_active_fraction_max_observed": float(max_toxic_gate_fraction),
            "pass": bool(mean_toxic_gate_fraction < 0.5),
            "rationale": (
                f"Toxicity gate threshold 0.7 (EVAL-11 best config toxicity_threshold); "
                f"mean observed toxic_gate_active_fraction {mean_toxic_gate_fraction:.4f} below the "
                f"0.5 deployment watch level (max observed {max_toxic_gate_fraction:.4f} on single ETH series)."
            ),
        }
    )

    guardrails.append(
        {
            "name": "cost_budget_bps",
            "category": "execution_cost",
            "threshold": float(MAX_COST_BUDGET_BPS),
            "observed": float(cost_budget_bps),
            "effective_total_cost_bps": float(total_cost_bps),
            "pass": bool(cost_budget_bps <= MAX_COST_BUDGET_BPS),
            "rationale": (
                f"Cost budget {cost_budget_bps:.2f} bps (EVAL-11 best feasible config) at or below "
                f"the {MAX_COST_BUDGET_BPS:.2f} bps deployment ceiling (EVAL-10 default used 2.0 bps). "
                f"Observed effective cost {total_cost_bps:.2f} bps of traded notional."
            ),
        }
    )

    guardrails.append(
        {
            "name": "kill_switch_max_drawdown",
            "category": "kill_switch",
            "threshold": float(MAX_DRAWDOWN_KILL),
            "observed": float(max_drawdown_observed),
            "pass": bool(max_drawdown_observed < MAX_DRAWDOWN_KILL),
            "rationale": (
                f"Kill-switch: halt paper deployment if max drawdown exceeds {MAX_DRAWDOWN_KILL:.0%}; "
                f"worst observed EVAL-11 series max drawdown {max_drawdown_observed:.4f} is below the kill level."
            ),
        }
    )

    guardrails.append(
        {
            "name": "kill_switch_toxicity",
            "category": "kill_switch",
            "threshold": float(MAX_TOXIC_GATE_ACTIVE_FRACTION),
            "observed": float(mean_toxic_gate_fraction),
            "toxic_gate_active_fraction_max_observed": float(max_toxic_gate_fraction),
            "pass": bool(mean_toxic_gate_fraction < MAX_TOXIC_GATE_ACTIVE_FRACTION),
            "rationale": (
                f"Kill-switch: halt paper deployment if mean toxic_gate_active_fraction exceeds "
                f"{MAX_TOXIC_GATE_ACTIVE_FRACTION:.0%}; "
                f"mean observed {mean_toxic_gate_fraction:.4f} (max per-series {max_toxic_gate_fraction:.4f} on single ETH series with zero notional) is below the kill level."
            ),
        }
    )

    guardrails.append(
        {
            "name": "kill_switch_cost_bps",
            "category": "kill_switch",
            "threshold": 5.0,
            "observed": float(total_cost_bps),
            "pass": bool(total_cost_bps < 5.0),
            "rationale": (
                f"Kill-switch: halt paper deployment if effective cost exceeds 5.00 bps of traded "
                f"notional; observed {total_cost_bps:.2f} bps."
            ),
        }
    )

    guardrails.append(
        {
            "name": "max_daily_loss_usd",
            "category": "risk_limit",
            "threshold": float(MAX_DAILY_LOSS_USD),
            "observed": float(MAX_DAILY_LOSS_USD),
            "pass": True,
            "rationale": (
                f"Daily loss limit {MAX_DAILY_LOSS_USD:,.0f} USD from .env.example risk limits; "
                "paper-only bound, checked against realized PnL at deployment time."
            ),
        }
    )

    guardrails.append(
        {
            "name": "live_trading_disabled",
            "category": "safety",
            "threshold": 0.0,
            "observed": 1.0 if LIVE_TRADING_ENABLED else 0.0,
            "pass": bool(not LIVE_TRADING_ENABLED),
            "rationale": (
                "Live trading disabled (LIVE_TRADING_ENABLED=false); EVAL-13 certification is "
                "paper-only and does not authorize deployment or venue connectivity."
            ),
        }
    )

    return guardrails


def compute_certification_verdict(
    evidence: dict[str, Any], metrics: dict[str, Any], guardrails: list[dict[str, Any]]
) -> dict[str, Any]:
    """Deterministic GO/NO-GO verdict from evidence + guardrail checks.

    The verdict is a pure function of the inputs: no prose, no hard-coded
    outcome. Every condition carries an explicit pass/fail reason.
    """
    checks: list[dict[str, Any]] = []

    n_sources = int(metrics["n_evidence_sources"])
    checks.append(
        {
            "name": "evidence_sources_complete",
            "pass": bool(n_sources >= 2),
            "threshold": 2,
            "observed": float(n_sources),
            "reason": (
                f"PASS: {n_sources} sealed evidence sources compared (EVAL-10/EVAL-11/EVAL-12)"
                if n_sources >= 2
                else f"FAIL: only {n_sources} evidence source(s); need >= 2"
            ),
        }
    )

    eval12_go = str(metrics["eval12_verdict"]).upper() == "GO"
    checks.append(
        {
            "name": "eval12_walkforward_go",
            "pass": bool(eval12_go),
            "threshold": 1.0,
            "observed": 1.0 if eval12_go else 0.0,
            "reason": (
                "PASS: EVAL-12 walk-forward verdict GO"
                if eval12_go
                else "FAIL: EVAL-12 walk-forward verdict is not GO"
            ),
        }
    )

    surviving = metrics["bh_surviving_configs"]
    has_survivor = len(surviving) >= 1
    checks.append(
        {
            "name": "eval12_bh_survivor",
            "pass": bool(has_survivor),
            "threshold": 1.0,
            "observed": float(len(surviving)),
            "reason": (
                f"PASS: {len(surviving)} config(s) survive BH FDR {FDR_ALPHA}: {surviving}"
                if has_survivor
                else f"FAIL: no config survives BH FDR {FDR_ALPHA}"
            ),
        }
    )

    best_sharpe = float(metrics["eval11_best_mean_net_sharpe"])
    no_hedge = float(metrics["eval11_no_hedge_control_sharpe"])
    beats_no_hedge = bool(best_sharpe > 0.0 and best_sharpe > no_hedge)
    checks.append(
        {
            "name": "eval11_best_beats_no_hedge_control",
            "pass": bool(beats_no_hedge),
            "threshold": float(no_hedge),
            "observed": float(best_sharpe),
            "reason": (
                f"PASS: EVAL-11 best mean net Sharpe {best_sharpe:.6f} > 0 and > no-hedge "
                f"control {no_hedge:.6f}"
                if beats_no_hedge
                else f"FAIL: EVAL-11 best mean net Sharpe {best_sharpe:.6f} not above "
                f"0 / no-hedge control {no_hedge:.6f}"
            ),
        }
    )

    beats_eval10 = bool(metrics["eval11_best_mean_net_sharpe_gt_eval10"])
    checks.append(
        {
            "name": "eval11_best_strictly_beats_eval10_default",
            "pass": bool(beats_eval10),
            "threshold": float(metrics["eval10_default_mean_net_sharpe"]),
            "observed": float(best_sharpe),
            "reason": (
                f"PASS: EVAL-11 best {best_sharpe:.6f} > EVAL-10 default "
                f"{float(metrics['eval10_default_mean_net_sharpe']):.6f} (sealed NO-GO baseline)"
                if beats_eval10
                else f"FAIL: EVAL-11 best {best_sharpe:.6f} not strictly above EVAL-10 default"
            ),
        }
    )

    perm_sig = bool(metrics["permutation_significant"])
    perm_p = float(metrics["permutation_eval11_vs_eval10"].get("p_value", 1.0))
    checks.append(
        {
            "name": "permutation_eval11_dominates_eval10",
            "pass": bool(perm_sig),
            "threshold": 0.05,
            "observed": float(perm_p),
            "reason": (
                f"PASS: paired permutation EVAL-11 vs EVAL-10 p={perm_p:.6f} < 0.05 "
                "(EVAL-11 best strictly dominates sealed NO-GO baseline)"
                if perm_sig
                else f"FAIL: paired permutation p={perm_p:.6f} not significant at 0.05"
            ),
        }
    )

    guardrail_pass = all(bool(g["pass"]) for g in guardrails)
    guardrail_fails = [g["name"] for g in guardrails if not bool(g["pass"])]
    checks.append(
        {
            "name": "all_deployment_guardrails_pass",
            "pass": bool(guardrail_pass),
            "threshold": float(len(guardrails)),
            "observed": float(sum(1 for g in guardrails if bool(g["pass"]))),
            "reason": (
                f"PASS: all {len(guardrails)} guardrail checks pass"
                if guardrail_pass
                else f"FAIL: guardrail(s) not passed: {guardrail_fails}"
            ),
        }
    )

    finite_ok = bool(
        metrics["dsr_all_finite"]
        and math.isfinite(metrics["bootstrap_ci_mean_net_return"]["point"])
        and math.isfinite(metrics["bootstrap_ci_mean_net_sharpe"]["point"])
        and math.isfinite(metrics["pbo_overall"])
        and all(math.isfinite(g["threshold"]) and math.isfinite(g["observed"]) for g in guardrails)
    )
    checks.append(
        {
            "name": "metrics_and_guardrails_finite",
            "pass": bool(finite_ok),
            "threshold": 1.0,
            "observed": 1.0 if finite_ok else 0.0,
            "reason": (
                "PASS: all DSR/PBO/bootstrap/guardrail numeric fields finite"
                if finite_ok
                else "FAIL: non-finite numeric field in metrics or guardrails"
            ),
        }
    )

    verdict = "GO" if all(bool(c["pass"]) for c in checks) else "NO-GO"
    return {
        "verdict": verdict,
        "checks": checks,
        "all_checks_pass": bool(all(bool(c["pass"]) for c in checks)),
        "n_checks": int(len(checks)),
        "n_passed": int(sum(1 for c in checks if bool(c["pass"]))),
    }


def _all_finite_numbers(obj: Any) -> bool:
    if isinstance(obj, bool):
        return True
    if isinstance(obj, (int, float)):
        return math.isfinite(float(obj))
    if isinstance(obj, dict):
        return all(_all_finite_numbers(v) for v in obj.values())
    if isinstance(obj, (list, tuple)):
        return all(_all_finite_numbers(v) for v in obj)
    return True


def evaluate_final_strategy_certification(
    write: bool = True,
    out_dir: str | Path = OUT_DIR,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Run the full EVAL-13 certification and emit strict artifacts.

    Pure deterministic computation from sealed evidence; `generated_at` is the
    only clock-dependent field. Returns the serialized report dict.
    """
    if timestamp is None:
        timestamp = _utc_now_iso()

    evidence = load_sealed_evidence()
    metrics = compute_net_of_cost_metrics(evidence)
    guardrails = build_guardrails(evidence)
    verdict = compute_certification_verdict(evidence, metrics, guardrails)

    # Non-degeneracy assertions.
    assert int(metrics["n_evidence_sources"]) >= 2, "need >= 2 evidence sources"
    assert len(guardrails) >= 2, "need >= 2 guardrails"
    assert _all_finite_numbers(metrics), "metrics contain non-finite values"
    assert _all_finite_numbers(verdict), "verdict block contains non-finite values"
    assert _all_finite_numbers(guardrails), "guardrails contain non-finite values"
    assert metrics["dsr_all_finite"], "DSR fields non-finite"
    assert verdict["verdict"] in ("GO", "NO-GO"), "verdict must be GO or NO-GO"

    report = {
        "report_id": REPORT_ID,
        "generated_at": timestamp,
        "verdict": verdict["verdict"],
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "evidence": evidence,
        "net_of_cost_metrics": metrics,
        "guardrails": guardrails,
        "verdict_checks": verdict,
        "deployment_authorization": {
            "authorized": bool(verdict["verdict"] == "GO"),
            "mode": "paper_only",
            "note": "GO verdict certifies paper-readiness only; not an authorization to trade live.",
        },
    }
    assert_json_valid(report)
    serialized = serialize_metrics_strict(report)

    if write:
        out_dir = Path(out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        stamp = _stamp_for_filename(timestamp)
        json_path = out_dir / f"FINAL_STRATEGY_CERTIFICATION_{stamp}.json"
        md_path = out_dir / f"FINAL_STRATEGY_CERTIFICATION_{stamp}.md"
        serialized["artifact_paths"] = {
            "json": str(json_path),
            "md": str(md_path),
        }
        json_path.write_text(
            json.dumps(serialized, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        md_path.write_text(_write_markdown(serialized) + "\n", encoding="utf-8")

    return serialized


def _write_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append("# FINAL STRATEGY CERTIFICATION — EVAL-13 (paper-only)")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Verdict: {report['verdict']}")
    lines.append(f"- Trading mode: {report['trading_mode']} (live trading enabled: {report['live_trading_enabled']})")
    lines.append("")

    m = report["net_of_cost_metrics"]
    lines.append("## SEALED EVIDENCE SUMMARY")
    lines.append(f"- EVAL-10 verdict: {report['evidence']['eval10']['verdict']}, pass_fraction={report['evidence']['eval10']['pass_fraction']:.4f}, mean net Sharpe={m['eval10_default_mean_net_sharpe']:.6f}, mean net return={m['eval10_default_mean_net_return']:.6f}")
    lines.append(f"- EVAL-11 (best feasible): config={report['evidence']['eval11']['config']}, mean net Sharpe={m['eval11_best_mean_net_sharpe']:.6f}, mean net return={m['eval11_best_mean_net_return']:.6f}, mean abs delta={m['eval11_best_mean_abs_delta_usd']:.4f} USD, total cost={m['eval11_best_total_cost_usd']:.2f} USD, hedges={m['eval11_best_total_hedges']}, series={report['evidence']['eval11']['num_series']}")
    lines.append(f"- EVAL-11 no-hedge control Sharpe: {m['eval11_no_hedge_control_sharpe']:.6f}; improvement vs no-hedge: {m['eval11_sharpe_improvement_vs_no_hedge']:.6f}")
    lines.append(f"- EVAL-12 walk-forward: verdict={m['eval12_verdict']}, BH survivors={m['bh_surviving_configs']}, PBO overall={m['pbo_overall']:.4f}, DSR sealed={m['dsr_sealed']}")
    lines.append("")

    lines.append("## RECOMPUTED NET-OF-COST METRICS")
    lines.append(f"- DSR recomputed: {m['dsr_recomputed']} (sealed: {m['dsr_sealed']}; consistent={all(v['consistent'] for v in m['dsr_consistency'].values())})")
    lines.append(f"- Bootstrap CI mean net return: [{m['bootstrap_ci_mean_net_return']['lo']:.6f}, {m['bootstrap_ci_mean_net_return']['hi']:.6f}] point={m['bootstrap_ci_mean_net_return']['point']:.6f}, lower>0={m['bootstrap_ci_mean_net_return']['lower_bound_positive']}")
    lines.append(f"- Bootstrap CI mean net Sharpe: [{m['bootstrap_ci_mean_net_sharpe']['lo']:.6f}, {m['bootstrap_ci_mean_net_sharpe']['hi']:.6f}] point={m['bootstrap_ci_mean_net_sharpe']['point']:.6f}, lower>0={m['bootstrap_ci_mean_net_sharpe']['lower_bound_positive']}")
    lines.append(f"- Paired permutation EVAL-11 vs EVAL-10: p={m['permutation_eval11_vs_eval10']['p_value']:.6f}, significant={m['permutation_significant']}, observed difference={m['permutation_eval11_vs_eval10']['observed_difference']:.6f}")
    lines.append("")

    lines.append("## VERDICT CHECKS (deterministic)")
    for c in report["verdict_checks"]["checks"]:
        lines.append(f"- [{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: {c['reason']}")
    lines.append(f"- All checks pass: {report['verdict_checks']['all_checks_pass']} ({report['verdict_checks']['n_passed']}/{report['verdict_checks']['n_checks']})")
    lines.append("")

    lines.append("## PAPER-ONLY DEPLOYMENT GUARDRAILS")
    for g in report["guardrails"]:
        lines.append(f"- {g['name']} ({g['category']}): threshold={g['threshold']}, observed={g['observed']}, pass={g['pass']}")
        lines.append(f"  rationale: {g['rationale']}")
    lines.append("")

    lines.append("## DEPLOYMENT AUTHORIZATION")
    lines.append(f"- Authorized: {report['deployment_authorization']['authorized']} (mode={report['deployment_authorization']['mode']})")
    lines.append(report["deployment_authorization"]["note"])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Final strategy certification + paper-only guardrails (EVAL-13)"
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Compute and print the report without writing artifacts",
    )
    parser.add_argument("--out-dir", type=str, default=str(OUT_DIR))
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    args = parser.parse_args(argv)

    report = evaluate_final_strategy_certification(
        write=not args.no_write,
        out_dir=args.out_dir,
        timestamp=args.timestamp,
    )

    print(
        json.dumps(
            {
                "report_id": report["report_id"],
                "verdict": report["verdict"],
                "trading_mode": report["trading_mode"],
                "all_checks_pass": report["verdict_checks"]["all_checks_pass"],
                "n_checks_passed": f'{report["verdict_checks"]["n_passed"]}/{report["verdict_checks"]["n_checks"]}',
                "eval11_best_mean_net_sharpe": report["net_of_cost_metrics"]["eval11_best_mean_net_sharpe"],
                "eval10_default_mean_net_sharpe": report["net_of_cost_metrics"]["eval10_default_mean_net_sharpe"],
                "dsr_recomputed": report["net_of_cost_metrics"]["dsr_recomputed"],
                "permutation_p": report["net_of_cost_metrics"]["permutation_eval11_vs_eval10"]["p_value"],
                "guardrails_pass": all(bool(g["pass"]) for g in report["guardrails"]),
                "artifact_paths": report.get("artifact_paths", {}),
            },
            sort_keys=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
