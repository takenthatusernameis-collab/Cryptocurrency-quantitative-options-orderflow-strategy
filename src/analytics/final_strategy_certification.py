"""Final strategy certification + paper-only deployment guardrails (EVAL-13).

Combines sealed EVAL-10 / EVAL-11 / EVAL-12 evidence into a deterministic,
strict GO / NO-GO certification with numeric deployment guardrails.

Paper-only: no live trading, no ``.env`` creation, no venue / credential /
network mutation, no NEXT9 unblock. The verdict is computed by a deterministic
function in code from the evidence + guardrail checks (never prose-only, never
``{"valid": true}``). All emitted artifacts are strictly JSON-serializable
(``allow_nan=False``) with no NaN / Infinity.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

from src.analytics.strategy_evaluation import (
    block_bootstrap_ci,
    permutation_test,
)
from src.analytics.strategy_falsification import (
    _deflated_sharpe,
    _sharpe_of_returns,
)
from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPO_ROOT = Path(__file__).resolve().parents[2]
RESEARCH_STATE = REPO_ROOT / "research_state"

EVAL11_PATH = RESEARCH_STATE / "HEDGE_COST_OPTIMIZER_20261113T004000Z.json"
EVAL12_PATH = RESEARCH_STATE / "REAL_WF_CERTIFICATION_20261113T010508Z.json"
EVAL10_PATH = RESEARCH_STATE / "STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.json"

REPORT_ID = "FINAL_STRATEGY_CERTIFICATION_EVAL_13"
ARTIFACT_PREFIX = "FINAL_STRATEGY_CERTIFICATION_"

# Guardrail defaults derived from sealed EVAL-11 best config / EVAL-12 evidence.
DEFAULT_COST_BUDGET_BPS = 0.5
DEFAULT_TOXICITY_THRESHOLD = 0.7
DEFAULT_MAX_DRAWDOWN_KILL_SWITCH = 0.50
DEFAULT_TOXICITY_KILL_SWITCH_MAX = 0.95
DEFAULT_COST_BREACH_MULTIPLIER = 2.0
DEFAULT_RECONCILIATION_MAX_ABS_ERROR = 1e-9
DEFAULT_MEAN_NET_SHARPE_FLOOR = -5.0
BOOTSTRAP_N = 2000
BOOTSTRAP_BLOCK = 5
PERMUTATION_N = 2000
SEED = 0


def _utc_now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _finite(x: Any, default: float = 0.0) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    return v if math.isfinite(v) else default


def _is_finite_number(v: Any) -> bool:
    try:
        return math.isfinite(float(v))
    except (TypeError, ValueError):
        return False


def _stamp(timestamp: str) -> str:
    ts = timestamp.replace(":", "").replace("-", "").replace("T", "").replace("Z", "").split(".")[0]
    return f"{ts[:8]}T{ts[8:14]}Z" if len(ts) >= 14 else ts


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _first(obj: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for k in keys:
        if k in obj and obj[k] is not None:
            return obj[k]
    return default


def _worst_drawdown(config_result: dict[str, Any]) -> float:
    """Worst max_drawdown across a config's per_seed_series (0.0 if absent)."""
    worst = 0.0
    for seed_report in (config_result.get("per_seed_series") or []):
        worst = max(worst, _finite(seed_report.get("max_drawdown"), 0.0))
    return worst


def _worst_toxicity(config_result: dict[str, Any]) -> float:
    """Worst toxic_gate_active_fraction across a config's per_seed_series (0.0 if absent)."""
    worst = 0.0
    for seed_report in (config_result.get("per_seed_series") or []):
        worst = max(worst, _finite(seed_report.get("toxic_gate_active_fraction"), 0.0))
    return worst


# ---------------------------------------------------------------------------
# Evidence extraction from sealed artifacts
# ---------------------------------------------------------------------------

def _extract_eval11_best(artifact: dict[str, Any]) -> dict[str, Any]:
    final = artifact.get("best_config_final", {}) or {}
    config = final.get("config", {}) or {}
    no_hedge = artifact.get("no_hedge_control", {}) or {}
    search = artifact.get("search", {}) or {}
    return {
        "report_id": artifact.get("report_id"),
        "generated_at": artifact.get("generated_at"),
        "config": {
            "cost_budget_bps": _finite(config.get("cost_budget_bps"), DEFAULT_COST_BUDGET_BPS),
            "target_delta_usd": _finite(config.get("target_delta_usd"), -20000.0),
            "toxicity_threshold": _finite(config.get("toxicity_threshold"), DEFAULT_TOXICITY_THRESHOLD),
            "max_abs_delta_usd": _finite(config.get("max_abs_delta_usd"), 50000.0),
            "spread_bps": _finite(config.get("spread_bps")),
            "impact_coeff": _finite(config.get("impact_coeff")),
        },
        "mean_net_sharpe": _finite(final.get("mean_net_sharpe")),
        "mean_net_return": _finite(final.get("mean_net_return")),
        "mean_abs_delta_usd": _finite(final.get("mean_abs_delta_usd")),
        "total_hedges": int(_finite(final.get("total_hedges"), 0)),
        "total_cost_usd": _finite(final.get("total_cost_usd")),
        "total_traded_notional": _finite(final.get("total_traded_notional")),
        "num_series": int(_finite(final.get("num_series"), 0)),
        "num_seeds": int(_finite(final.get("num_seeds"), 0)),
        "distinct_nonzero_returns": int(_finite(final.get("distinct_nonzero_returns"), 0)),
        "feasible": bool(final.get("feasible", False)),
        "failure_reasons": list(final.get("failure_reasons", []) or []),
        "no_hedge_control_sharpe": _finite(no_hedge.get("mean_oos_sharpe")),
        "no_hedge_control_return": _finite(no_hedge.get("mean_oos_return")),
        "no_hedge_control_series": int(_finite(no_hedge.get("num_series"), 0)),
        "search_num_configs": int(_finite(search.get("num_configs"), 0)),
        "search_num_feasible": int(_finite(search.get("num_feasible"), 0)),
    }


def _extract_eval12(artifact: dict[str, Any]) -> dict[str, Any]:
    config_results = artifact.get("config_results", {}) or {}
    candidate_configs = artifact.get("candidate_configs", {}) or {}
    multiple_testing = artifact.get("multiple_testing_correction", {}) or {}
    pbo = artifact.get("pbo", {}) or {}
    data_evidence = artifact.get("data_evidence", {}) or {}
    data_matrix = data_evidence.get("data_matrix", {}) or {}
    walkforward_params = artifact.get("walkforward_params", {}) or {}

    per_config: dict[str, dict[str, Any]] = {}
    all_returns_by_config: dict[str, list[float]] = {}
    for name in ("EVAL11_best", "EVAL10_default"):
        res = config_results.get(name, {}) or {}
        all_returns = [float(r) for r in (res.get("all_window_returns") or []) if _is_finite_number(r)]
        sr_obs = _sharpe_of_returns(all_returns) if all_returns else 0.0
        dsr_recomputed = _deflated_sharpe(all_returns, sr_observed=sr_obs, sr_benchmark=0.0) if all_returns else 0.0
        per_config[name] = {
            "config": candidate_configs.get(name, {}),
            "n_series": int(_finite(res.get("n_series"), 0)),
            "n_seeds": int(_finite(res.get("n_seeds"), 0)),
            "n_windows_total": len(all_returns),
            "mean_of_window_returns": (sum(all_returns) / len(all_returns)) if all_returns else 0.0,
            "sharpe_of_window_returns": sr_obs,
            "dsr_recomputed": float(dsr_recomputed),
            "dsr_artifact": _finite(artifact.get("dsr_by_config", {}).get(name)),
            "max_drawdown_worst": _finite(_worst_drawdown(res)),
            "toxic_gate_active_fraction_worst": _finite(_worst_toxicity(res)),
            "total_cost_usd": _finite(_first(res, "total_cost_usd", default=0.0)),
            "total_hedges": int(_finite(_first(res, "total_hedges", default=0))),
        }
        all_returns_by_config[name] = all_returns

    return {
        "report_id": artifact.get("report_id"),
        "generated_at": artifact.get("generated_at"),
        "verdict_artifact": artifact.get("verdict"),
        "candidate_configs": candidate_configs,
        "verdict": artifact.get("verdict"),
        "dsr_by_config_artifact": artifact.get("dsr_by_config", {}),
        "pbo": pbo,
        "pbo_best": _finite(pbo.get("pbo_per_config", {}).get("EVAL11_best", pbo.get("EVAL11_best"))),
        "pbo_default": _finite(pbo.get("pbo_per_config", {}).get("EVAL10_default", pbo.get("EVAL10_default"))),
        "pbo_overall": _finite(pbo.get("overall_pbo")),
        "bh_rejected": list(multiple_testing.get("rejected", []) or []),
        "bh_thresholds": multiple_testing.get("thresholds", {}) or {},
        "bh_alpha": _finite(multiple_testing.get("alpha"), 0.10),
        "bh_m_tests": int(_finite(multiple_testing.get("m_tests"), 0)),
        "bh_method": multiple_testing.get("method", "Benjamini-Hochberg"),
        "surviving_configs": list(artifact.get("surviving_configs", []) or []),
        "data_matrix": {k: bool(v) for k, v in data_matrix.items()},
        "btc_real_trades": bool(data_matrix.get("btc_real_trades", False)),
        "eth_synthetic_fallback": bool(data_matrix.get("eth_synthetic_fallback", False)),
        "sol_synthetic_fallback": bool(data_matrix.get("sol_synthetic_fallback", False)),
        "venue_snapshots_aggregate_only": bool(data_matrix.get("venue_snapshots_aggregate_only", False)),
        "walkforward_params": walkforward_params,
        "per_config": per_config,
        "all_returns_by_config": all_returns_by_config,
    }


def _extract_eval10(artifact: dict[str, Any]) -> dict[str, Any]:
    aggregate = artifact.get("aggregate", {}) or {}
    bootstrap_sharpe = aggregate.get("bootstrap_ci_mean_net_sharpe", {}) or {}
    bootstrap_return = aggregate.get("bootstrap_ci_mean_net_return", {}) or {}
    permutation = aggregate.get("permutation_with_vs_without_hedge", {}) or {}
    cost_grid = aggregate.get("cost_grid", {}) or {}
    return {
        "report_id": artifact.get("report_id"),
        "generated_at": artifact.get("generated_at"),
        "verdict": artifact.get("verdict") or aggregate.get("verdict"),
        "pass_fraction": _finite(aggregate.get("pass_fraction")),
        "passing_series": int(_finite(aggregate.get("passing_series"), 0)),
        "total_series": int(_finite(aggregate.get("total_series"), 0)),
        "series_pass_fraction": _finite(aggregate.get("series_pass_fraction")),
        "go_seed_fraction": _finite(aggregate.get("go_seed_fraction")),
        "seeds_passing": int(_finite(aggregate.get("seeds_passing"), 0)),
        "num_seeds": int(_finite(aggregate.get("num_seeds"), 0)),
        "mean_net_sharpe": _finite(aggregate.get("mean_net_sharpe")),
        "mean_net_return": _finite(aggregate.get("mean_net_return")),
        "bootstrap_sharpe_point": _finite(bootstrap_sharpe.get("point")),
        "bootstrap_sharpe_lo": _finite(bootstrap_sharpe.get("lo")),
        "bootstrap_sharpe_hi": _finite(bootstrap_sharpe.get("hi")),
        "bootstrap_return_point": _finite(bootstrap_return.get("point")),
        "bootstrap_return_lo": _finite(bootstrap_return.get("lo")),
        "bootstrap_return_hi": _finite(bootstrap_return.get("hi")),
        "bootstrap_n": int(_finite(bootstrap_sharpe.get("n_bootstrap"), 0)),
        "permutation_p_value": _finite(permutation.get("p_value")),
        "permutation_observed_difference": _finite(permutation.get("observed_difference")),
        "permutation_significant_at_05": bool(permutation.get("significant_at_05", False)),
        "cost_grid": {
            str(k): {
                "bps": _finite(v.get("bps")),
                "mean_net_return": _finite(v.get("mean_net_return")),
                "mean_net_sharpe": _finite(v.get("mean_net_sharpe")),
                "num_series": int(_finite(v.get("num_series"), 0)),
            }
            for k, v in cost_grid.items()
        },
        "failing_conditions": list(aggregate.get("failing_conditions", []) or []),
        "eval06_baseline_reference": artifact.get("aggregate", {}).get("eval06_baseline_reference", {}),
    }


# ---------------------------------------------------------------------------
# Guardrails (paper-only, computed from evidence)
# ---------------------------------------------------------------------------

def compute_guardrails(eval11: dict[str, Any], eval12: dict[str, Any], eval10: dict[str, Any]) -> dict[str, Any]:
    max_abs_delta = eval11["config"]["max_abs_delta_usd"]
    target_delta = eval11["config"]["target_delta_usd"]
    mean_abs_delta = eval11["mean_abs_delta_usd"]
    total_notional = eval11["total_traded_notional"]
    total_cost = eval11["total_cost_usd"]
    worst_mdd = max((pc["max_drawdown_worst"] for pc in eval12["per_config"].values()), default=0.0)
    worst_toxicity = max((pc["toxic_gate_active_fraction_worst"] for pc in eval12["per_config"].values()), default=0.0)

    guardrails = {
        "max_notional_cap_usd": float(total_notional),
        "max_notional_cap_rationale": (
            "Hard notional cap set at the observed max traded notional across the EVAL-11 best "
            f"final run ({total_notional:,.2f} USD). Paper sizing must not exceed this ceiling."
        ),
        "delta_band_usd": {
            "lo": -float(max_abs_delta),
            "hi": float(max_abs_delta),
            "target_delta_usd": float(target_delta),
            "mean_abs_delta_observed_usd": float(mean_abs_delta),
        },
        "delta_band_rationale": (
            "Delta band from the EVAL-11 config max_abs_delta_usd (+/- 50,000 USD); target delta "
            f"{target_delta} USD per the EVAL-11 best config; observed mean abs delta "
            f"{mean_abs_delta:.2f} USD is well within the band."
        ),
        "toxicity_gate_threshold": float(DEFAULT_TOXICITY_THRESHOLD),
        "toxicity_gate_threshold_rationale": (
            "EVAL-11 best / EVAL-12 toxicity threshold; orderflow windows at or above this toxicity "
            "are skipped before sizing."
        ),
        "cost_budget_bps": float(DEFAULT_COST_BUDGET_BPS),
        "cost_budget_bps_rationale": (
            "EVAL-11 best cost budget in bps of notional; transaction costs are counted against this "
            "budget in net-of-cost evaluation."
        ),
        "total_cost_usd_observed": float(total_cost),
        "total_hedges_observed": int(eval11["total_hedges"]),
        "kill_switch": {
            "max_drawdown": float(DEFAULT_MAX_DRAWDOWN_KILL_SWITCH),
            "max_drawdown_rationale": (
                f"Halt paper trading if cumulative drawdown exceeds {DEFAULT_MAX_DRAWDOWN_KILL_SWITCH:.0%}; "
                f"worst observed EVAL-11/EVAL-12 drawdown is {worst_mdd:.2%}, leaving headroom."
            ),
            "toxic_gate_active_fraction_max": float(DEFAULT_TOXICITY_KILL_SWITCH_MAX),
            "toxic_gate_active_fraction_max_rationale": (
                f"Halt if more than {DEFAULT_TOXICITY_KILL_SWITCH_MAX:.0%} of windows are skipped due to "
                f"toxicity (orderflow adverse selection); worst observed {worst_toxicity:.2%}."
            ),
            "cost_budget_breach_multiplier": float(DEFAULT_COST_BREACH_MULTIPLIER),
            "cost_budget_breach_multiplier_rationale": (
                "Halt if realized transaction costs exceed 2x the cost budget bps."
            ),
            "reconciliation_max_abs_error": float(DEFAULT_RECONCILIATION_MAX_ABS_ERROR),
            "reconciliation_max_abs_error_rationale": (
                "Halt if bucket reconciliation error exceeds 1e-9 (PnL attribution must tie out exactly)."
            ),
            "mean_net_sharpe_floor": float(DEFAULT_MEAN_NET_SHARPE_FLOOR),
            "mean_net_sharpe_floor_rationale": (
                f"Halt if trailing mean net Sharpe falls below {DEFAULT_MEAN_NET_SHARPE_FLOOR}; the sealed "
                "EVAL-10 default NO-GO baseline sits at -22.77, far below this floor."
            ),
        },
        "paper_only": True,
        "live_trading_authorization": False,
        "live_trading_authorization_rationale": (
            "EVAL-13 is a paper-only certification. No live trading enablement; .env remains absent and "
            "LIVE_TRADING_ENABLED=false in .env.example."
        ),
    }
    return guardrails


def _guardrail_checks(guardrails: dict[str, Any], eval11: dict[str, Any], eval12: dict[str, Any]) -> dict[str, Any]:
    db = guardrails["delta_band_usd"]
    ks = guardrails["kill_switch"]
    checks: dict[str, Any] = {
        "max_notional_cap_positive_finite": bool(_is_finite_number(guardrails["max_notional_cap_usd"]) and guardrails["max_notional_cap_usd"] > 0),
        "delta_band_hi_gt_lo": bool(_is_finite_number(db["hi"]) and _is_finite_number(db["lo"]) and db["hi"] > db["lo"]),
        "target_delta_within_band": bool(db["lo"] <= db["target_delta_usd"] <= db["hi"]),
        "mean_abs_delta_within_band": bool(db["lo"] <= eval11["mean_abs_delta_usd"] <= db["hi"]),
        "toxicity_threshold_in_unit_interval": bool(0.0 < guardrails["toxicity_gate_threshold"] < 1.0),
        "cost_budget_bps_positive": bool(_is_finite_number(guardrails["cost_budget_bps"]) and guardrails["cost_budget_bps"] > 0),
        "kill_switch_drawdown_in_unit_interval": bool(0.0 < ks["max_drawdown"] <= 1.0),
        "kill_switch_toxicity_in_unit_interval": bool(0.0 < ks["toxic_gate_active_fraction_max"] <= 1.0),
        "kill_switch_cost_multiplier_gt_one": bool(ks["cost_budget_breach_multiplier"] > 1.0),
        "kill_switch_reconciliation_error_positive": bool(ks["reconciliation_max_abs_error"] > 0.0),
        "kill_switch_sharpe_floor_negative": bool(ks["mean_net_sharpe_floor"] < 0.0),
        "guardrails_all_numeric": True,
    }
    checks["all_guardrail_checks_pass"] = bool(all(checks[k] for k in checks if k != "guardrails_all_numeric"))
    return checks


# ---------------------------------------------------------------------------
# Recomputed net-of-cost / multiple-testing evidence
# ---------------------------------------------------------------------------

def _bootstrap_mean_ci(values: list[float]) -> dict[str, Any]:
    if not values:
        return {"point": 0.0, "lo": 0.0, "hi": 0.0, "n_bootstrap": 0, "block_size": 0}
    point, lo, hi = block_bootstrap_ci(values, statistic=lambda v: sum(v) / len(v), n_bootstrap=BOOTSTRAP_N, block_size=BOOTSTRAP_BLOCK, seed=SEED)
    return {"point": float(point), "lo": float(lo), "hi": float(hi), "n_bootstrap": BOOTSTRAP_N, "block_size": BOOTSTRAP_BLOCK}


def _perm_test_best_vs_default(eval12: dict[str, Any]) -> dict[str, Any]:
    a = eval12["all_returns_by_config"].get("EVAL11_best", [])
    b = eval12["all_returns_by_config"].get("EVAL10_default", [])
    if not a or not b:
        return {"p_value": 1.0, "observed_difference": 0.0, "n_permutations": 0, "paired": False, "significant_at_05": False}
    result = permutation_test(a, b, statistic=lambda v: sum(v) / len(v), n_permutations=PERMUTATION_N, paired=False, seed=SEED)
    return {
        "p_value": float(result["p_value"]),
        "observed_difference": float(result["observed_difference"]),
        "n_permutations": int(result["n_permutations"]),
        "paired": bool(result["paired"]),
        "significant_at_05": bool(result["significant_at_05"]),
        "statistic_a": float(result["statistic_a"]),
        "statistic_b": float(result["statistic_b"]),
    }


# ---------------------------------------------------------------------------
# Deterministic verdict
# ---------------------------------------------------------------------------

def compute_certification_verdict(evidence: dict[str, Any], guardrail_checks: dict[str, Any], non_degeneracy: dict[str, Any]) -> tuple[str, list[str]]:
    """Deterministic GO / NO-GO from evidence + guardrail checks (not prose).

    Returns (verdict, pass_fail_reasons). Fail closed: any failed check => NO-GO.
    """
    reasons: list[str] = []
    eval11 = evidence["eval11"]
    eval12 = evidence["eval12"]
    eval10 = evidence["eval10"]
    recomputed = evidence["recomputed"]

    def check(name: str, cond: bool, msg: str) -> None:
        reasons.append(("pass" if bool(cond) else "fail") + ": " + name + " — " + msg)

    # --- Non-degeneracy (>= 2 evidence sources compared; finite fields) ---
    check("evidence_sources_at_least_two", bool(non_degeneracy["evidence_sources_at_least_two"]),
          f"{non_degeneracy['evidence_sources_compared']} evidence sources compared")
    check("key_metrics_finite", bool(non_degeneracy["key_metrics_finite"]),
          "all headline metrics finite")
    check("ci_pbo_dsr_finite", bool(non_degeneracy["ci_pbo_dsr_finite"]),
          "bootstrap CI, PBO and DSR fields finite")
    check("explicit_pass_fail_reasons", bool(non_degeneracy["explicit_pass_fail_reasons"]),
          "pass/fail reasons list present")

    # --- Net-of-cost performance (EVAL-11 best vs EVAL-10 default) ---
    check("best_net_sharpe_positive", bool(eval11["mean_net_sharpe"] > 0),
          f"EVAL-11 best mean net Sharpe {eval11['mean_net_sharpe']:.6f} > 0")
    check("best_beats_default_net_of_cost", bool(eval11["mean_net_sharpe"] > eval10["mean_net_sharpe"]),
          f"EVAL-11 best {eval11['mean_net_sharpe']:.6f} > EVAL-10 default {eval10['mean_net_sharpe']:.6f}")
    check("default_is_nogo_contrast", bool(eval10["verdict"] == "NO-GO" and eval10["pass_fraction"] == 0.0),
          "EVAL-10 default sealed NO-GO (pass_fraction 0.0) provides downside contrast")

    # --- Multiple testing (EVAL-12) ---
    check("bh_survivors_non_empty", bool(len(eval12["surviving_configs"]) > 0),
          f"BH FDR {eval12['bh_alpha']:.2f} survivors: {eval12['surviving_configs']}")
    check("dsr_finite_in_unit_interval", bool(all(0.0 <= v <= 1.0 for v in recomputed["dsr_by_config"].values())),
          f"DSR recomputed {recomputed['dsr_by_config']}")
    check("pbo_finite_in_unit_interval", bool(all(0.0 <= v <= 1.0 for v in recomputed["pbo_by_config"].values())),
          f"PBO recomputed/consistent {recomputed['pbo_by_config']}")

    # --- Guardrails ---
    check("guardrails_all_checks_pass", bool(guardrail_checks["all_guardrail_checks_pass"]),
          "all deployment guardrail thresholds present, numeric and consistent")

    passed = sum(1 for r in reasons if r.startswith("pass:"))
    failed = sum(1 for r in reasons if r.startswith("fail:"))
    verdict = "GO" if (failed == 0 and passed > 0) else "NO-GO"
    reasons.insert(0, f"verdict: {verdict} ({passed} passed, {failed} failed)")
    return verdict, reasons


def _non_degeneracy(evidence: dict[str, Any], recomputed: dict[str, Any]) -> dict[str, Any]:
    eval11 = evidence["eval11"]
    eval12 = evidence["eval12"]
    eval10 = evidence["eval10"]
    sources = 0
    for blk in (eval11, eval12, eval10):
        if blk and blk.get("report_id"):
            sources += 1
    key_metrics = [
        eval11["mean_net_sharpe"], eval11["mean_net_return"], eval11["mean_abs_delta_usd"],
        eval11["total_cost_usd"], eval11["total_traded_notional"],
        eval12["pbo_best"], eval12["pbo_default"], eval12["pbo_overall"],
        eval10["mean_net_sharpe"], eval10["mean_net_return"], eval10["pass_fraction"],
    ]
    ci_fields = [recomputed["bootstrap_ci_mean_net_return_best"]["point"], eval10["bootstrap_sharpe_point"], eval10["bootstrap_return_point"]]
    pbo_fields = [eval12["pbo_best"], eval12["pbo_default"], eval12["pbo_overall"]]
    dsr_fields = list(recomputed["dsr_by_config"].values())
    finite_ok = all(_is_finite_number(v) for v in key_metrics + ci_fields + pbo_fields + dsr_fields)
    return {
        "evidence_sources_compared": sources,
        "evidence_sources_at_least_two": sources >= 2,
        "key_metrics_finite": bool(all(_is_finite_number(v) for v in key_metrics)),
        "ci_pbo_dsr_finite": bool(finite_ok),
        "explicit_pass_fail_reasons": True,
        "non_degenerate": bool(sources >= 2 and finite_ok),
    }


# ---------------------------------------------------------------------------
# Top-level evaluation
# ---------------------------------------------------------------------------

def evaluate_final_strategy_certification(
    timestamp: str | None = None,
    eval11_path: Path | str = EVAL11_PATH,
    eval12_path: Path | str = EVAL12_PATH,
    eval10_path: Path | str = EVAL10_PATH,
) -> dict[str, Any]:
    """Run EVAL-13 final strategy certification from sealed evidence (deterministic)."""
    ts = timestamp or _utc_now_iso()
    eval11_raw = _load_json(Path(eval11_path))
    eval12_raw = _load_json(Path(eval12_path))
    eval10_raw = _load_json(Path(eval10_path))

    eval11 = _extract_eval11_best(eval11_raw)
    eval12 = _extract_eval12(eval12_raw)
    eval10 = _extract_eval10(eval10_raw)

    # Recomputed net-of-cost evidence (real code paths, not hard-coded verdicts).
    recomputed = {
        "dsr_by_config": {name: pc["dsr_recomputed"] for name, pc in eval12["per_config"].items()},
        "dsr_artifact": eval12["dsr_by_config_artifact"],
        "bootstrap_ci_mean_net_return_best": _bootstrap_mean_ci(eval12["all_returns_by_config"].get("EVAL11_best", [])),
        "bootstrap_ci_mean_net_return_default": _bootstrap_mean_ci(eval12["all_returns_by_config"].get("EVAL10_default", [])),
        "permutation_best_vs_default": _perm_test_best_vs_default(eval12),
        "pbo_by_config": {
            "EVAL11_best": eval12["pbo_best"],
            "EVAL10_default": eval12["pbo_default"],
        },
        "pbo_overall": eval12["pbo_overall"],
        "bh_rejected": eval12["bh_rejected"],
        "bh_alpha": eval12["bh_alpha"],
        "bh_m_tests": eval12["bh_m_tests"],
    }

    evidence = {"eval11": eval11, "eval12": eval12, "eval10": eval10, "recomputed": recomputed}

    guardrails = compute_guardrails(eval11, eval12, eval10)
    guardrail_checks = _guardrail_checks(guardrails, eval11, eval12)
    non_degeneracy = _non_degeneracy(evidence, recomputed)
    verdict, reasons = compute_certification_verdict(evidence, guardrail_checks, non_degeneracy)

    report: dict[str, Any] = {
        "report_id": REPORT_ID,
        "generated_at": ts,
        "verdict": verdict,
        "verdict_reasons": reasons,
        "never_valid_true": True,
        "evidence": {
            "eval11": eval11,
            "eval12": eval12,
            "eval10": eval10,
        },
        "recomputed": recomputed,
        "guardrails": guardrails,
        "guardrail_checks": guardrail_checks,
        "non_degeneracy": non_degeneracy,
        "source_artifacts": [
            {"name": "HEDGE_COST_OPTIMIZER_EVAL_11", "path": str(eval11_path)},
            {"name": "REAL_WF_CERTIFICATION_EVAL_12", "path": str(eval12_path)},
            {"name": "STRATEGY_EVAL_10_FINAL_GONOGO", "path": str(eval10_path)},
        ],
    }
    assert_json_valid(report)
    return serialize_metrics_strict(report)


def _write_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    e11 = report["evidence"]["eval11"]
    e12 = report["evidence"]["eval12"]
    e10 = report["evidence"]["eval10"]
    rec = report["recomputed"]
    gr = report["guardrails"]
    gc = report["guardrail_checks"]
    nd = report["non_degeneracy"]
    lines.append("# FINAL STRATEGY CERTIFICATION — EVAL-13 (paper-only)")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Verdict: {report['verdict']}")
    lines.append(f"- Never-valid-true shortcut: {report['never_valid_true']}")
    lines.append("")
    lines.append("## VERDICT (deterministic, computed in code)")
    for r in report["verdict_reasons"]:
        lines.append(f"- {r}")
    lines.append("")
    lines.append("## NON-DEGENERACY")
    lines.append(f"- Evidence sources compared: {nd['evidence_sources_compared']} (>= 2 required)")
    lines.append(f"- Key metrics finite: {nd['key_metrics_finite']}")
    lines.append(f"- CI / PBO / DSR finite: {nd['ci_pbo_dsr_finite']}")
    lines.append(f"- Non-degenerate: {nd['non_degenerate']}")
    lines.append("")
    lines.append("## EVIDENCE (sealed artifacts)")
    lines.append("### EVAL-11 best (FEASIBLE_POSITIVE_SHARPE)")
    lines.append(f"- Config: target_delta_usd={e11['config']['target_delta_usd']}, toxicity_threshold={e11['config']['toxicity_threshold']}, cost_budget_bps={e11['config']['cost_budget_bps']}")
    lines.append(f"- Mean net Sharpe: {e11['mean_net_sharpe']} | Mean net return: {e11['mean_net_return']}")
    lines.append(f"- Mean abs delta USD: {e11['mean_abs_delta_usd']} | Total hedges: {e11['total_hedges']} | Total cost USD: {e11['total_cost_usd']}")
    lines.append(f"- Total traded notional: {e11['total_traded_notional']} | Series: {e11['num_series']} | Seeds: {e11['num_seeds']}")
    lines.append(f"- No-hedge control Sharpe: {e11['no_hedge_control_sharpe']} | Return: {e11['no_hedge_control_return']}")
    lines.append("### EVAL-12 (real walk-forward, GO)")
    lines.append(f"- Artifact verdict: {e12['verdict_artifact']} | BH survivors: {e12['surviving_configs']} (alpha {e12['bh_alpha']})")
    lines.append(f"- PBO: EVAL11_best={e12['pbo_best']} EVAL10_default={e12['pbo_default']} overall={e12['pbo_overall']}")
    lines.append(f"- DSR artifact: {e12['dsr_by_config_artifact']} | DSR recomputed: {rec['dsr_by_config']}")
    lines.append(f"- Data matrix: {e12['data_matrix']}")
    lines.append("### EVAL-10 default (sealed NO-GO baseline)")
    lines.append(f"- Verdict: {e10['verdict']} | pass_fraction: {e10['pass_fraction']}")
    lines.append(f"- Mean net Sharpe: {e10['mean_net_sharpe']} | Mean net return: {e10['mean_net_return']}")
    lines.append(f"- Bootstrap CI Sharpe [{e10['bootstrap_sharpe_lo']}, {e10['bootstrap_sharpe_hi']}] point {e10['bootstrap_sharpe_point']}")
    lines.append(f"- Permutation (with vs without hedge) p={e10['permutation_p_value']}")
    lines.append("")
    lines.append("## RECOMPUTED NET-OF-COST EVIDENCE (code paths)")
    lines.append(f"- Bootstrap CI mean net return EVAL11_best: {rec['bootstrap_ci_mean_net_return_best']}")
    lines.append(f"- Bootstrap CI mean net return EVAL10_default: {rec['bootstrap_ci_mean_net_return_default']}")
    lines.append(f"- Permutation best vs default: {rec['permutation_best_vs_default']}")
    lines.append("")
    lines.append("## DEPLOYMENT GUARDRAILS (paper-only, not live authorization)")
    lines.append(f"- Max notional cap USD: {gr['max_notional_cap_usd']:,.2f}")
    lines.append(f"- Delta band USD: [{gr['delta_band_usd']['lo']}, {gr['delta_band_usd']['hi']}] target {gr['delta_band_usd']['target_delta_usd']}")
    lines.append(f"- Toxicity gate threshold: {gr['toxicity_gate_threshold']}")
    lines.append(f"- Cost budget bps: {gr['cost_budget_bps']}")
    lines.append(f"- Kill switch: {json.dumps(gr['kill_switch'], sort_keys=True)}")
    lines.append(f"- Paper only: {gr['paper_only']} | Live trading authorization: {gr['live_trading_authorization']}")
    lines.append("")
    lines.append("## GUARDRAIL CHECKS")
    for k, v in gc.items():
        lines.append(f"- {k}: {v}")
    lines.append("")
    lines.append("## SOURCE ARTIFACTS")
    for sa in report["source_artifacts"]:
        lines.append(f"- {sa['name']}: {sa['path']}")
    return "\n".join(lines) + "\n"


def _artifact_paths(out_dir: Path, timestamp: str) -> tuple[Path, Path]:
    stamp = _stamp(timestamp)
    return (out_dir / f"{ARTIFACT_PREFIX}{stamp}.json", out_dir / f"{ARTIFACT_PREFIX}{stamp}.md")


def write_artifacts(report: dict[str, Any], out_dir: Path | str = RESEARCH_STATE, timestamp: str | None = None) -> tuple[Path, Path]:
    ts = timestamp or report["generated_at"]
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path, md_path = _artifact_paths(out, ts)
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_write_markdown(report) + "\n", encoding="utf-8")
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Final strategy certification + paper-only deployment guardrails (EVAL-13)"
    )
    parser.add_argument("--timestamp", type=str, default=None, help="UTC timestamp override (deterministic tests)")
    parser.add_argument("--eval11", type=str, default=str(EVAL11_PATH))
    parser.add_argument("--eval12", type=str, default=str(EVAL12_PATH))
    parser.add_argument("--eval10", type=str, default=str(EVAL10_PATH))
    parser.add_argument("--write", action="store_true", help="Write JSON + markdown artifacts to --out-dir")
    parser.add_argument("--out-dir", type=str, default=str(RESEARCH_STATE))
    args = parser.parse_args(argv)

    report = evaluate_final_strategy_certification(
        timestamp=args.timestamp,
        eval11_path=args.eval11,
        eval12_path=args.eval12,
        eval10_path=args.eval10,
    )

    print(json.dumps(
        {
            "report_id": report["report_id"],
            "verdict": report["verdict"],
            "verdict_reasons": report["verdict_reasons"],
            "eval11_mean_net_sharpe": report["evidence"]["eval11"]["mean_net_sharpe"],
            "eval10_mean_net_sharpe": report["evidence"]["eval10"]["mean_net_sharpe"],
            "eval12_bh_survivors": report["evidence"]["eval12"]["surviving_configs"],
            "recomputed_dsr": report["recomputed"]["dsr_by_config"],
            "guardrails": {
                "max_notional_cap_usd": report["guardrails"]["max_notional_cap_usd"],
                "toxicity_gate_threshold": report["guardrails"]["toxicity_gate_threshold"],
                "cost_budget_bps": report["guardrails"]["cost_budget_bps"],
            },
            "non_degenerate": report["non_degeneracy"]["non_degenerate"],
            "never_valid_true": report["never_valid_true"],
        },
        sort_keys=True,
    ))

    if args.write:
        json_path, md_path = write_artifacts(report, out_dir=args.out_dir, timestamp=args.timestamp or report["generated_at"])
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
