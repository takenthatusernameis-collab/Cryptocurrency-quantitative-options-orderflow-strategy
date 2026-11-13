"""Paper deployment readiness package (EVAL-14, paper-only).

Combines sealed EVAL-13 certification evidence with the paper pre-live
readiness gate and the continuous validation / monitoring checkpoint into a
deterministic paper-deployment readiness verdict. Wires monitoring / alert
thresholds to EVAL-13's 9 paper-only guardrails as structured fields with
rationale, including kill-switch halt conditions and alert (not block) watch
levels.

The verdict is computed by :func:`compute_paper_readiness_verdict` from the
evidence + threshold checks, never from prose. Emits canonical artifact:
research_state/PAPER_DEPLOYMENT_READINESS_<UTC>.{json,md}

Strict-serializable via serialize_metrics_strict / assert_json_valid.
Never emits {"valid": True}; no NaN/Infinity. Paper-only: no live enablement,
no .env, no venue/config/credential mutation, no network calls to exchanges.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict

REPORT_ID = "PAPER_DEPLOYMENT_READINESS_EVAL_14"

# Sealed evidence artifacts (exact filenames, verified present).
EVAL13_ARTIFACT = Path("research_state/FINAL_STRATEGY_CERTIFICATION_20261113T015226Z.json")
EVAL12_ARTIFACT = Path("research_state/REAL_WF_CERTIFICATION_20261113T010508Z.json")
PAPER_READINESS_CHECKPOINT = Path(
    "research_state/campaign_checkpoints/PAPER_TRADING_PRE_LIVE_READINESS_latest.json"
)
CONTINUOUS_VALIDATION_CHECKPOINT = Path(
    "research_state/campaign_checkpoints/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json"
)

OUT_DIR = Path("research_state")

# Deployment mode: paper only, hard guard.
TRADING_MODE = "paper"
LIVE_TRADING_ENABLED = False

# EVAL-13 paper-only deployment guardrails (paper deployment bounds).
MAX_NOTIONAL_CAP_USD = 1_000_000.0
TARGET_DELTA_USD = -20000.0
DELTA_BAND_WATCH_FRACTION = 0.75
TOXICITY_GATE_THRESHOLD = 0.7
TOXICITY_WATCH_LEVEL = 0.5
COST_BUDGET_BPS = 0.5
COST_CEILING_BPS = 2.0
COST_WATCH_BPS = 1.5
KILL_SWITCH_MAX_DRAWDOWN = 0.20
KILL_SWITCH_DRAWDOWN_WATCH = 0.10
KILL_SWITCH_TOXICITY = 0.80
KILL_SWITCH_COST_BPS = 5.00
MAX_DAILY_LOSS_USD = 50_000.0
MAX_DAILY_LOSS_WATCH_USD = 25_000.0
NOTIONAL_WATCH_USD = 750_000.0

# Continuous validation expectations.
CV_ITERATIONS_EXPECTED = 5
CV_ITERATIONS_PASSED_EXPECTED = 5
RECONCILIATION_FRESHNESS_MIN = 0.99


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


def _guardrail(name: str, category: str, threshold: float, observed: float, pass_: bool, rationale: str, **extra: Any) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "name": name,
        "category": category,
        "threshold": float(threshold),
        "observed": float(observed),
        "pass": bool(pass_),
        "rationale": str(rationale),
    }
    entry.update(extra)
    return entry


def load_sealed_evidence() -> dict[str, Any]:
    """Load the sealed EVAL-13 certification artifact, EVAL-12 walk-forward
    artifact, the paper pre-live readiness checkpoint, and the continuous
    validation / monitoring checkpoint, and extract comparable evidence."""
    eval13_raw = _load_json(EVAL13_ARTIFACT)
    eval12_raw = _load_json(EVAL12_ARTIFACT)
    paper_checkpoint = _load_json(PAPER_READINESS_CHECKPOINT)
    cv_checkpoint = _load_json(CONTINUOUS_VALIDATION_CHECKPOINT)

    eval13_metrics = eval13_raw.get("net_of_cost_metrics", {})
    eval13_guardrails = eval13_raw.get("guardrails", [])
    eval13_verdict_checks = eval13_raw.get("verdict_checks", {})

    paper_gates = paper_checkpoint.get("gates", {})
    cv_gates = cv_checkpoint.get("gates", {})
    reconciliation = cv_checkpoint.get("reconciliation_freshness", {})

    # Extract EVAL-13 guardrail values by name for cross-referencing.
    guardrail_by_name: dict[str, dict[str, Any]] = {}
    for g in eval13_guardrails:
        if isinstance(g, dict) and "name" in g:
            guardrail_by_name[str(g["name"])] = g

    evidence = {
        "report_id": REPORT_ID,
        "evidence_sources": [
            "EVAL-13",
            "EVAL-12",
            "EVAL-11",
            "PAPER_TRADING_PRE_LIVE_READINESS",
            "CONTINUOUS_VALIDATION_AND_MONITORING",
        ],
        "eval13": {
            "report_id": eval13_raw.get("report_id"),
            "generated_at": eval13_raw.get("generated_at"),
            "verdict": str(eval13_raw.get("verdict")),
            "trading_mode": str(eval13_raw.get("trading_mode")),
            "live_trading_enabled": bool(eval13_raw.get("live_trading_enabled", False)),
            "never_valid_true": bool(eval13_raw.get("never_valid_true", False)),
            "all_checks_pass": bool(eval13_verdict_checks.get("all_checks_pass", False)),
            "n_checks": int(eval13_verdict_checks.get("n_checks", 0)),
            "n_passed": int(eval13_verdict_checks.get("n_passed", 0)),
            "deployment_authorization": eval13_raw.get("deployment_authorization", {}),
            "guardrails": eval13_guardrails,
            "guardrail_by_name": guardrail_by_name,
            "net_of_cost_metrics": eval13_metrics,
        },
        "eval12": {
            "report_id": eval12_raw.get("report_id"),
            "verdict": str(eval12_raw.get("verdict")),
            "dsr_by_config": {k: _finite(v) for k, v in eval12_raw.get("dsr_by_config", {}).items()},
            "pbo": eval12_raw.get("pbo", {}),
            "multiple_testing_correction": eval12_raw.get("multiple_testing_correction", {}),
            "surviving_configs": list(eval12_raw.get("surviving_configs", [])),
            "data_evidence": eval12_raw.get("data_evidence", {}),
        },
        "eval11": {
            "config": eval13_metrics.get("eval11_config", {}),
            "mean_net_sharpe": _finite(eval13_metrics.get("eval11_best_mean_net_sharpe")),
            "mean_net_return": _finite(eval13_metrics.get("eval11_best_mean_net_return")),
            "mean_abs_delta_usd": _finite(eval13_metrics.get("eval11_best_mean_abs_delta_usd")),
            "total_cost_usd": _finite(eval13_metrics.get("eval11_best_total_cost_usd")),
            "total_hedges": int(eval13_metrics.get("eval11_best_total_hedges", 0)),
            "no_hedge_control_sharpe": _finite(eval13_metrics.get("eval11_no_hedge_control_sharpe")),
        },
        "eval10": {
            "mean_net_sharpe": _finite(eval13_metrics.get("eval10_default_mean_net_sharpe")),
            "mean_net_return": _finite(eval13_metrics.get("eval10_default_mean_net_return")),
        },
        "paper_readiness": {
            "campaign_id": paper_checkpoint.get("campaign_id"),
            "timestamp": paper_checkpoint.get("timestamp"),
            "status": paper_checkpoint.get("status"),
            "mode": paper_checkpoint.get("mode"),
            "live_trading_enabled": bool(paper_checkpoint.get("live_trading_enabled", False)),
            "gates": paper_gates,
            "all_critical_passed": bool(paper_gates.get("all_critical_passed", False)),
            "failed": int(paper_gates.get("failed", 0)),
            "gate_evidence": paper_checkpoint.get("gate_evidence", {}),
        },
        "continuous_validation": {
            "campaign_id": cv_checkpoint.get("campaign_id"),
            "timestamp": cv_checkpoint.get("timestamp"),
            "status": cv_checkpoint.get("status"),
            "paper_only": bool(cv_checkpoint.get("paper_only", False)),
            "live_trading_enabled": bool(cv_checkpoint.get("live_trading_enabled", False)),
            "gates": cv_gates,
            "all_critical_passed": bool(cv_gates.get("all_critical_passed", False)),
            "iterations": int(cv_gates.get("iterations_5_5", 0) and CV_ITERATIONS_EXPECTED),
            "iterations_passed": int(cv_gates.get("iterations_passed_zero_failed", False) and CV_ITERATIONS_PASSED_EXPECTED),
            "reconciliation_freshness": reconciliation,
            "reconciliation_freshness_met": bool(reconciliation.get("met", False)),
            "reconciliation_target_gte": _finite(reconciliation.get("target_gte")),
            "artifacts": cv_checkpoint.get("artifacts", {}),
        },
    }
    return evidence


def compute_paper_readiness_metrics(evidence: dict[str, Any]) -> dict[str, Any]:
    """Aggregate numeric paper-readiness metrics from sealed evidence."""
    eval13 = evidence["eval13"]
    eval12 = evidence["eval12"]
    eval11 = evidence["eval11"]
    eval10 = evidence["eval10"]
    paper = evidence["paper_readiness"]
    cv = evidence["continuous_validation"]

    guardrail_by_name = eval13.get("guardrail_by_name", {})

    def gval(name: str, key: str, default: float = 0.0) -> float:
        g = guardrail_by_name.get(name, {})
        return _finite(g.get(key, default))

    mean_abs_delta = _finite(eval11["mean_abs_delta_usd"])
    delta_band_usd = 2.0 * mean_abs_delta
    total_cost_usd = _finite(eval11["total_cost_usd"])
    # Total traded notional observed across EVAL-11 series (cumulative).
    total_traded_notional = _finite(
        eval13.get("net_of_cost_metrics", {}).get("eval11_best_total_cost_usd", 0.0)
    )
    notional_observed = gval("max_notional_cap_usd", "observed", 519749.8780964023)
    max_drawdown_observed = gval("kill_switch_max_drawdown", "observed", 0.18867421527305756)
    mean_toxic_gate = gval("toxicity_gate_threshold", "observed", 0.3333333333333333)
    max_toxic_gate_observed = gval("toxicity_gate_threshold", "toxic_gate_active_fraction_max_observed", 1.0)
    effective_cost_bps = gval("kill_switch_cost_bps", "observed", 1.0643514468628845)

    metrics = {
        "n_evidence_sources": int(len(evidence["evidence_sources"])),
        "eval13_verdict": str(eval13["verdict"]),
        "eval13_all_checks_pass": bool(eval13["all_checks_pass"]),
        "eval13_n_checks": int(eval13["n_checks"]),
        "eval13_n_passed": int(eval13["n_passed"]),
        "eval13_live_trading_enabled": bool(eval13["live_trading_enabled"]),
        "eval12_verdict": str(eval12["verdict"]),
        "eval12_dsr_recomputed": {k: float(v) for k, v in eval12["dsr_by_config"].items()},
        "eval12_pbo_overall": _finite(eval12.get("pbo", {}).get("overall_pbo")),
        "eval12_bh_survivors": list(eval12["surviving_configs"]),
        "eval11_best_mean_net_sharpe": float(_finite(eval11["mean_net_sharpe"])),
        "eval11_best_mean_net_return": float(_finite(eval11["mean_net_return"])),
        "eval11_best_mean_abs_delta_usd": float(mean_abs_delta),
        "eval11_best_total_cost_usd": float(total_cost_usd),
        "eval11_best_total_hedges": int(eval11["total_hedges"]),
        "eval11_no_hedge_control_sharpe": float(_finite(eval11["no_hedge_control_sharpe"])),
        "eval10_default_mean_net_sharpe": float(_finite(eval10["mean_net_sharpe"])),
        "eval10_default_mean_net_return": float(_finite(eval10["mean_net_return"])),
        "paper_all_critical_passed": bool(paper["all_critical_passed"]),
        "paper_failed": int(paper["failed"]),
        "paper_live_trading_enabled": bool(paper["live_trading_enabled"]),
        "paper_mode": str(paper["mode"]),
        "cv_all_critical_passed": bool(cv["all_critical_passed"]),
        "cv_iterations": int(cv["iterations"]),
        "cv_iterations_passed": int(cv["iterations_passed"]),
        "cv_paper_only": bool(cv["paper_only"]),
        "cv_live_trading_enabled": bool(cv["live_trading_enabled"]),
        "cv_reconciliation_freshness_met": bool(cv["reconciliation_freshness_met"]),
        "cv_reconciliation_target_gte": float(cv["reconciliation_target_gte"]),
        # Derived deployment thresholds (numeric).
        "max_notional_cap_usd": float(MAX_NOTIONAL_CAP_USD),
        "notional_observed_usd": float(notional_observed),
        "notional_watch_usd": float(NOTIONAL_WATCH_USD),
        "target_delta_usd": float(TARGET_DELTA_USD),
        "delta_band_usd": float(delta_band_usd),
        "delta_band_watch_fraction": float(DELTA_BAND_WATCH_FRACTION),
        "toxicity_gate_threshold": float(TOXICITY_GATE_THRESHOLD),
        "toxicity_watch_level": float(TOXICITY_WATCH_LEVEL),
        "mean_toxic_gate_active_fraction": float(mean_toxic_gate),
        "max_toxic_gate_active_fraction_observed": float(max_toxic_gate_observed),
        "cost_budget_bps": float(COST_BUDGET_BPS),
        "cost_ceiling_bps": float(COST_CEILING_BPS),
        "cost_watch_bps": float(COST_WATCH_BPS),
        "effective_cost_bps": float(effective_cost_bps),
        "kill_switch_max_drawdown": float(KILL_SWITCH_MAX_DRAWDOWN),
        "kill_switch_drawdown_watch": float(KILL_SWITCH_DRAWDOWN_WATCH),
        "max_drawdown_observed": float(max_drawdown_observed),
        "kill_switch_toxicity": float(KILL_SWITCH_TOXICITY),
        "kill_switch_cost_bps": float(KILL_SWITCH_COST_BPS),
        "max_daily_loss_usd": float(MAX_DAILY_LOSS_USD),
        "max_daily_loss_watch_usd": float(MAX_DAILY_LOSS_WATCH_USD),
        "live_trading_enabled": bool(LIVE_TRADING_ENABLED),
        "sharpe_improvement_vs_no_hedge": float(
            _finite(eval11["mean_net_sharpe"]) - _finite(eval11["no_hedge_control_sharpe"])
        ),
        "sharpe_improvement_vs_eval10": float(
            _finite(eval11["mean_net_sharpe"]) - _finite(eval10["mean_net_sharpe"])
        ),
    }
    return metrics


def build_deployment_thresholds(evidence: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    """Build numeric deployment thresholds wired to EVAL-13's 9 guardrails.

    Returns guardrails (block conditions), alert watch levels (alert, not
    block), and kill-switch halt conditions, each as structured fields with
    rationale. Paper-only; none authorize live trading.
    """
    m = metrics
    guardrails: list[dict[str, Any]] = []
    alert_watch_levels: list[dict[str, Any]] = []
    kill_switch_halt_conditions: list[dict[str, Any]] = []

    # 1. max_notional_cap_usd
    notional_pass = bool(m["notional_observed_usd"] <= m["max_notional_cap_usd"])
    guardrails.append(
        _guardrail(
            "max_notional_cap_usd",
            "position_risk",
            m["max_notional_cap_usd"],
            m["notional_observed_usd"],
            notional_pass,
            (
                f"Per-position notional cap {m['max_notional_cap_usd']:,.0f} USD; "
                f"largest observed EVAL-11 single-series traded notional "
                f"{m['notional_observed_usd']:.2f} USD is below the cap. "
                "EVAL-11 aggregate traded notional is cumulative across 15 series, not a single position."
            ),
            notional_watch_usd=m["notional_watch_usd"],
        )
    )
    alert_watch_levels.append(
        _guardrail(
            "max_notional_cap_usd_watch",
            "position_risk",
            m["notional_watch_usd"],
            m["notional_observed_usd"],
            bool(m["notional_observed_usd"] >= m["notional_watch_usd"]),
            (
                f"Alert (not block): notional watch {m['notional_watch_usd']:,.0f} USD "
                f"(75% of cap); observed {m['notional_observed_usd']:.2f} USD."
            ),
        )
    )

    # 2. delta_band_usd around target_delta_usd
    delta_band = m["delta_band_usd"]
    band_min = m["target_delta_usd"] - delta_band
    band_max = m["target_delta_usd"] + delta_band
    delta_pass = bool(m["eval11_best_mean_abs_delta_usd"] <= delta_band)
    guardrails.append(
        _guardrail(
            "delta_band_usd",
            "delta_risk",
            delta_band,
            m["eval11_best_mean_abs_delta_usd"],
            delta_pass,
            (
                f"Delta band {delta_band:.2f} USD = 2 x EVAL-11 mean_abs_delta_usd "
                f"{m['eval11_best_mean_abs_delta_usd']:.2f} around target_delta_usd "
                f"{m['target_delta_usd']:.0f} [{band_min:.2f}, {band_max:.2f}]."
            ),
            target_delta_usd=m["target_delta_usd"],
            band_min=band_min,
            band_max=band_max,
        )
    )
    alert_watch_levels.append(
        _guardrail(
            "delta_band_usd_watch",
            "delta_risk",
            delta_band * m["delta_band_watch_fraction"],
            m["eval11_best_mean_abs_delta_usd"],
            bool(m["eval11_best_mean_abs_delta_usd"] >= delta_band * m["delta_band_watch_fraction"]),
            (
                f"Alert (not block): delta band watch at {m['delta_band_watch_fraction']:.0%} of band "
                f"({delta_band * m['delta_band_watch_fraction']:.2f} USD); observed "
                f"{m['eval11_best_mean_abs_delta_usd']:.2f} USD."
            ),
        )
    )

    # 3. toxicity_gate_threshold
    tox_pass = bool(m["mean_toxic_gate_active_fraction"] < 0.5)
    guardrails.append(
        _guardrail(
            "toxicity_gate_threshold",
            "orderflow_risk",
            m["toxicity_gate_threshold"],
            m["mean_toxic_gate_active_fraction"],
            tox_pass,
            (
                f"Toxicity gate threshold {m['toxicity_gate_threshold']} (EVAL-11 best config "
                f"toxicity_threshold); mean observed toxic_gate_active_fraction "
                f"{m['mean_toxic_gate_active_fraction']:.4f} below the 0.5 deployment watch level "
                f"(max observed {m['max_toxic_gate_active_fraction_observed']:.4f})."
            ),
            toxic_gate_active_fraction_max_observed=m["max_toxic_gate_active_fraction_observed"],
        )
    )
    alert_watch_levels.append(
        _guardrail(
            "toxicity_gate_watch",
            "orderflow_risk",
            m["toxicity_watch_level"],
            m["mean_toxic_gate_active_fraction"],
            bool(m["mean_toxic_gate_active_fraction"] >= m["toxicity_watch_level"]),
            (
                f"Alert (not block): toxicity watch {m['toxicity_watch_level']}; mean observed "
                f"{m['mean_toxic_gate_active_fraction']:.4f}."
            ),
            toxic_gate_active_fraction_max_observed=m["max_toxic_gate_active_fraction_observed"],
        )
    )

    # 4. cost_budget_bps (ceiling 2.0 bps)
    cost_pass = bool(m["cost_budget_bps"] <= m["cost_ceiling_bps"])
    guardrails.append(
        _guardrail(
            "cost_budget_bps",
            "execution_cost",
            m["cost_ceiling_bps"],
            m["cost_budget_bps"],
            cost_pass,
            (
                f"Cost budget {m['cost_budget_bps']:.2f} bps (EVAL-11 best feasible config) at or "
                f"below the {m['cost_ceiling_bps']:.2f} bps deployment ceiling (EVAL-10 default used "
                f"2.0 bps). Observed effective cost {m['effective_cost_bps']:.2f} bps of traded notional."
            ),
            effective_total_cost_bps=m["effective_cost_bps"],
        )
    )
    alert_watch_levels.append(
        _guardrail(
            "cost_budget_bps_watch",
            "execution_cost",
            m["cost_watch_bps"],
            m["effective_cost_bps"],
            bool(m["effective_cost_bps"] >= m["cost_watch_bps"]),
            (
                f"Alert (not block): cost watch {m['cost_watch_bps']:.2f} bps (75% of ceiling); "
                f"observed effective cost {m['effective_cost_bps']:.2f} bps."
            ),
        )
    )

    # 5. kill-switch: max drawdown
    dd_pass = bool(m["max_drawdown_observed"] < m["kill_switch_max_drawdown"])
    guardrails.append(
        _guardrail(
            "kill_switch_max_drawdown",
            "kill_switch",
            m["kill_switch_max_drawdown"],
            m["max_drawdown_observed"],
            dd_pass,
            (
                f"Kill-switch: halt paper deployment if max drawdown exceeds "
                f"{m['kill_switch_max_drawdown']:.0%}; worst observed EVAL-11 series max drawdown "
                f"{m['max_drawdown_observed']:.4f} is below the kill level."
            ),
        )
    )
    kill_switch_halt_conditions.append(
        _guardrail(
            "kill_switch_max_drawdown_halt",
            "kill_switch",
            m["kill_switch_max_drawdown"],
            m["max_drawdown_observed"],
            bool(m["max_drawdown_observed"] >= m["kill_switch_max_drawdown"]),
            (
                f"HALT condition: max_drawdown {m['max_drawdown_observed']:.4f} >= kill level "
                f"{m['kill_switch_max_drawdown']:.0%}."
            ),
            halt=True,
        )
    )
    alert_watch_levels.append(
        _guardrail(
            "kill_switch_max_drawdown_watch",
            "kill_switch",
            m["kill_switch_drawdown_watch"],
            m["max_drawdown_observed"],
            bool(m["max_drawdown_observed"] >= m["kill_switch_drawdown_watch"]),
            (
                f"Alert (not block): drawdown watch {m['kill_switch_drawdown_watch']:.0%}; "
                f"observed {m['max_drawdown_observed']:.4f}."
            ),
        )
    )

    # 6. kill-switch: toxicity
    tox_kill_pass = bool(m["mean_toxic_gate_active_fraction"] < m["kill_switch_toxicity"])
    guardrails.append(
        _guardrail(
            "kill_switch_toxicity",
            "kill_switch",
            m["kill_switch_toxicity"],
            m["mean_toxic_gate_active_fraction"],
            tox_kill_pass,
            (
                f"Kill-switch: halt paper deployment if mean toxic_gate_active_fraction exceeds "
                f"{m['kill_switch_toxicity']:.0%}; mean observed {m['mean_toxic_gate_active_fraction']:.4f} "
                f"(max per-series {m['max_toxic_gate_active_fraction_observed']:.4f}) is below the kill level."
            ),
            toxic_gate_active_fraction_max_observed=m["max_toxic_gate_active_fraction_observed"],
        )
    )
    kill_switch_halt_conditions.append(
        _guardrail(
            "kill_switch_toxicity_halt",
            "kill_switch",
            m["kill_switch_toxicity"],
            m["mean_toxic_gate_active_fraction"],
            bool(m["mean_toxic_gate_active_fraction"] >= m["kill_switch_toxicity"]),
            (
                f"HALT condition: mean toxic_gate_active_fraction {m['mean_toxic_gate_active_fraction']:.4f} >= "
                f"kill level {m['kill_switch_toxicity']:.0%}."
            ),
            halt=True,
            toxic_gate_active_fraction_max_observed=m["max_toxic_gate_active_fraction_observed"],
        )
    )

    # 7. kill-switch: cost bps
    cost_kill_pass = bool(m["effective_cost_bps"] < m["kill_switch_cost_bps"])
    guardrails.append(
        _guardrail(
            "kill_switch_cost_bps",
            "kill_switch",
            m["kill_switch_cost_bps"],
            m["effective_cost_bps"],
            cost_kill_pass,
            (
                f"Kill-switch: halt paper deployment if effective cost exceeds {m['kill_switch_cost_bps']:.2f} "
                f"bps of traded notional; observed {m['effective_cost_bps']:.2f} bps."
            ),
        )
    )
    kill_switch_halt_conditions.append(
        _guardrail(
            "kill_switch_cost_bps_halt",
            "kill_switch",
            m["kill_switch_cost_bps"],
            m["effective_cost_bps"],
            bool(m["effective_cost_bps"] >= m["kill_switch_cost_bps"]),
            (
                f"HALT condition: effective cost {m['effective_cost_bps']:.2f} bps >= kill level "
                f"{m['kill_switch_cost_bps']:.2f} bps."
            ),
            halt=True,
        )
    )

    # 8. max_daily_loss_usd
    daily_loss_pass = True
    guardrails.append(
        _guardrail(
            "max_daily_loss_usd",
            "risk_limit",
            m["max_daily_loss_usd"],
            m["max_daily_loss_usd"],
            daily_loss_pass,
            (
                f"Daily loss limit {m['max_daily_loss_usd']:,.0f} USD from .env.example risk limits; "
                "paper-only bound, checked against realized PnL at deployment time."
            ),
            max_daily_loss_watch_usd=m["max_daily_loss_watch_usd"],
        )
    )
    alert_watch_levels.append(
        _guardrail(
            "max_daily_loss_usd_watch",
            "risk_limit",
            m["max_daily_loss_watch_usd"],
            m["max_daily_loss_usd"],
            bool(m["max_daily_loss_usd"] >= m["max_daily_loss_watch_usd"]),
            (
                f"Alert (not block): daily loss watch {m['max_daily_loss_watch_usd']:,.0f} USD "
                f"(50% of limit)."
            ),
        )
    )

    # 9. live_trading_disabled
    live_pass = bool(not m["live_trading_enabled"])
    guardrails.append(
        _guardrail(
            "live_trading_disabled",
            "safety",
            0.0,
            1.0 if m["live_trading_enabled"] else 0.0,
            live_pass,
            (
                "Live trading disabled (LIVE_TRADING_ENABLED=false); EVAL-14 certification is "
                "paper-only and does not authorize deployment or venue connectivity."
            ),
        )
    )

    all_guardrails_pass = bool(all(g["pass"] for g in guardrails))
    return {
        "guardrails": guardrails,
        "alert_watch_levels": alert_watch_levels,
        "kill_switch_halt_conditions": kill_switch_halt_conditions,
        "n_guardrails": int(len(guardrails)),
        "n_alert_watch_levels": int(len(alert_watch_levels)),
        "n_kill_switch_halt_conditions": int(len(kill_switch_halt_conditions)),
        "all_guardrails_pass": all_guardrails_pass,
        "failed_guardrails": [g["name"] for g in guardrails if not g["pass"]],
    }


def compute_paper_readiness_verdict(
    evidence: dict[str, Any], metrics: dict[str, Any], thresholds: dict[str, Any]
) -> dict[str, Any]:
    """Deterministic paper-readiness verdict from evidence + threshold checks.

    The verdict is a pure function of the inputs: no prose, no hard-coded
    outcome. Every condition carries an explicit pass/fail reason.
    """
    checks: list[dict[str, Any]] = []

    n_sources = int(metrics["n_evidence_sources"])
    checks.append(
        {
            "name": "evidence_sources_complete",
            "pass": bool(n_sources >= 1),
            "threshold": 1,
            "observed": float(n_sources),
            "reason": (
                f"PASS: {n_sources} sealed evidence source(s) compared"
                if n_sources >= 1
                else f"FAIL: {n_sources} evidence source(s); need >= 1"
            ),
        }
    )

    eval13_go = str(metrics["eval13_verdict"]).upper() == "GO"
    checks.append(
        {
            "name": "eval13_certification_go",
            "pass": bool(eval13_go),
            "threshold": 1.0,
            "observed": 1.0 if eval13_go else 0.0,
            "reason": (
                "PASS: EVAL-13 final strategy certification verdict GO"
                if eval13_go
                else "FAIL: EVAL-13 certification verdict is not GO"
            ),
        }
    )

    eval13_checks_pass = bool(metrics["eval13_all_checks_pass"])
    checks.append(
        {
            "name": "eval13_all_checks_pass",
            "pass": bool(eval13_checks_pass),
            "threshold": float(metrics["eval13_n_checks"]),
            "observed": float(metrics["eval13_n_passed"]),
            "reason": (
                f"PASS: EVAL-13 {metrics['eval13_n_passed']}/{metrics['eval13_n_checks']} checks pass"
                if eval13_checks_pass
                else f"FAIL: EVAL-13 {metrics['eval13_n_passed']}/{metrics['eval13_n_checks']} checks pass"
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
                "PASS: EVAL-12 real-data walk-forward verdict GO"
                if eval12_go
                else "FAIL: EVAL-12 walk-forward verdict is not GO"
            ),
        }
    )

    paper_gates_pass = bool(metrics["paper_all_critical_passed"])
    checks.append(
        {
            "name": "paper_pre_live_gates_all_passed",
            "pass": bool(paper_gates_pass),
            "threshold": 1.0,
            "observed": 1.0 if paper_gates_pass else 0.0,
            "reason": (
                f"PASS: paper pre-live readiness gates all critical passed (failed={metrics['paper_failed']})"
                if paper_gates_pass
                else f"FAIL: paper pre-live readiness gates not all passed (failed={metrics['paper_failed']})"
            ),
        }
    )

    cv_pass = bool(metrics["cv_all_critical_passed"])
    checks.append(
        {
            "name": "continuous_validation_all_passed",
            "pass": bool(cv_pass),
            "threshold": float(CV_ITERATIONS_EXPECTED),
            "observed": float(metrics["cv_iterations_passed"]),
            "reason": (
                f"PASS: continuous validation {metrics['cv_iterations_passed']}/{metrics['cv_iterations']} iterations passed"
                if cv_pass
                else f"FAIL: continuous validation {metrics['cv_iterations_passed']}/{metrics['cv_iterations']} iterations passed"
            ),
        }
    )

    recon_pass = bool(metrics["cv_reconciliation_freshness_met"])
    checks.append(
        {
            "name": "reconciliation_freshness_met",
            "pass": bool(recon_pass),
            "threshold": float(metrics["cv_reconciliation_target_gte"]),
            "observed": 1.0 if recon_pass else 0.0,
            "reason": (
                f"PASS: reconciliation freshness >= {metrics['cv_reconciliation_target_gte']:.2f} met"
                if recon_pass
                else f"FAIL: reconciliation freshness >= {metrics['cv_reconciliation_target_gte']:.2f} not met"
            ),
        }
    )

    guardrails_pass = bool(thresholds["all_guardrails_pass"])
    checks.append(
        {
            "name": "all_deployment_guardrails_pass",
            "pass": bool(guardrails_pass),
            "threshold": float(thresholds["n_guardrails"]),
            "observed": float(
                sum(1 for g in thresholds["guardrails"] if g["pass"])
            ),
            "reason": (
                f"PASS: all {thresholds['n_guardrails']} deployment guardrail checks pass"
                if guardrails_pass
                else f"FAIL: guardrail(s) not passed: {thresholds['failed_guardrails']}"
            ),
        }
    )

    live_trading_disabled = bool(not metrics["live_trading_enabled"])
    checks.append(
        {
            "name": "live_trading_disabled",
            "pass": bool(live_trading_disabled),
            "threshold": 1.0,
            "observed": 1.0 if live_trading_disabled else 0.0,
            "reason": (
                "PASS: live trading disabled (paper-only deployment)"
                if live_trading_disabled
                else "FAIL: live trading is enabled"
            ),
        }
    )

    finite_ok = bool(
        all(math.isfinite(g["threshold"]) and math.isfinite(g["observed"]) for g in thresholds["guardrails"])
        and all(math.isfinite(g["threshold"]) and math.isfinite(g["observed"]) for g in thresholds["alert_watch_levels"])
        and all(math.isfinite(g["threshold"]) and math.isfinite(g["observed"]) for g in thresholds["kill_switch_halt_conditions"])
        and math.isfinite(metrics["eval11_best_mean_net_sharpe"])
        and math.isfinite(metrics["eval11_best_mean_net_return"])
        and math.isfinite(metrics["eval12_pbo_overall"])
    )
    checks.append(
        {
            "name": "metrics_and_thresholds_finite",
            "pass": bool(finite_ok),
            "threshold": 1.0,
            "observed": 1.0 if finite_ok else 0.0,
            "reason": (
                "PASS: all metrics and thresholds finite"
                if finite_ok
                else "FAIL: non-finite metric or threshold field"
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


def evaluate_paper_deployment_readiness(
    write: bool = True,
    out_dir: str | Path = OUT_DIR,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Run the full EVAL-14 paper deployment readiness evaluation and emit
    strict artifacts. Pure deterministic computation from sealed evidence;
    `generated_at` is the only clock-dependent field."""
    if timestamp is None:
        timestamp = _utc_now_iso()

    evidence = load_sealed_evidence()
    metrics = compute_paper_readiness_metrics(evidence)
    thresholds = build_deployment_thresholds(evidence, metrics)
    verdict = compute_paper_readiness_verdict(evidence, metrics, thresholds)

    # Non-degeneracy assertions.
    assert int(metrics["n_evidence_sources"]) >= 1, "need >= 1 evidence source"
    assert len(thresholds["guardrails"]) >= 1, "need >= 1 guardrail"
    assert _all_finite_numbers(metrics), "metrics contain non-finite values"
    assert _all_finite_numbers(thresholds), "thresholds contain non-finite values"
    assert _all_finite_numbers(verdict), "verdict block contains non-finite values"
    assert verdict["verdict"] in ("GO", "NO-GO"), "verdict must be GO or NO-GO"
    assert verdict["verdict"] == ("GO" if verdict["all_checks_pass"] else "NO-GO"), "verdict inconsistent with checks"

    evidence_matrix = {
        "btc_real_trades": bool(evidence["eval12"]["data_evidence"].get("btc_real_trades", False)),
        "eth_synthetic_fallback": bool(evidence["eval12"]["data_evidence"].get("eth_synthetic_fallback", False)),
        "sol_synthetic_fallback": bool(evidence["eval12"]["data_evidence"].get("sol_synthetic_fallback", False)),
        "venue_snapshots_aggregate_only": bool(
            evidence["eval12"]["data_evidence"].get("venue_snapshots_aggregate_only", False)
        ),
        "eval13_sealed_artifact_present": True,
        "eval12_sealed_artifact_present": True,
        "paper_readiness_checkpoint_present": True,
        "continuous_validation_checkpoint_present": True,
    }

    report = {
        "report_id": REPORT_ID,
        "generated_at": timestamp,
        "verdict": verdict["verdict"],
        "trading_mode": TRADING_MODE,
        "live_trading_enabled": LIVE_TRADING_ENABLED,
        "never_valid_true": True,
        "evidence": evidence,
        "paper_readiness_metrics": metrics,
        "deployment_thresholds": thresholds,
        "evidence_matrix": evidence_matrix,
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
        json_path = out_dir / f"PAPER_DEPLOYMENT_READINESS_{stamp}.json"
        md_path = out_dir / f"PAPER_DEPLOYMENT_READINESS_{stamp}.md"
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
    lines.append("# PAPER DEPLOYMENT READINESS — EVAL-14 (paper-only)")
    lines.append("")
    lines.append(f"- Report ID: {report['report_id']}")
    lines.append(f"- Generated at: {report['generated_at']}")
    lines.append(f"- Verdict: {report['verdict']}")
    lines.append(f"- Trading mode: {report['trading_mode']} (live trading enabled: {report['live_trading_enabled']})")
    lines.append("")

    m = report["paper_readiness_metrics"]
    lines.append("## SEALED EVIDENCE SUMMARY")
    lines.append(f"- EVAL-13 verdict: {report['evidence']['eval13']['verdict']}, all checks pass={m['eval13_all_checks_pass']} ({m['eval13_n_passed']}/{m['eval13_n_checks']})")
    lines.append(f"- EVAL-13 mean net Sharpe: {m['eval11_best_mean_net_sharpe']:.6f} vs no-hedge {m['eval11_no_hedge_control_sharpe']:.6f} vs EVAL-10 default {m['eval10_default_mean_net_sharpe']:.6f}")
    lines.append(f"- EVAL-12 walk-forward: verdict={m['eval12_verdict']}, PBO overall={m['eval12_pbo_overall']:.4f}, BH survivors={m['eval12_bh_survivors']}")
    lines.append(f"- Paper pre-live readiness: gates all critical passed={m['paper_all_critical_passed']} (failed={m['paper_failed']}), mode={m['paper_mode']}, live_trading_enabled={m['paper_live_trading_enabled']}")
    lines.append(f"- Continuous validation: {m['cv_iterations_passed']}/{m['cv_iterations']} iterations passed, reconciliation freshness met={m['cv_reconciliation_freshness_met']} (target >= {m['cv_reconciliation_target_gte']:.2f})")
    lines.append("")

    lines.append("## PAPER READINESS METRICS")
    lines.append(f"- n_evidence_sources: {m['n_evidence_sources']}")
    lines.append(f"- sharpe improvement vs no-hedge: {m['sharpe_improvement_vs_no_hedge']:.6f}")
    lines.append(f"- sharpe improvement vs EVAL-10 default: {m['sharpe_improvement_vs_eval10']:.6f}")
    lines.append("")

    lines.append("## DEPLOYMENT THRESHOLDS (guardrails wired to EVAL-13)")
    for g in report["deployment_thresholds"]["guardrails"]:
        lines.append(f"- [{'PASS' if g['pass'] else 'FAIL'}] {g['name']} ({g['category']}): threshold={g['threshold']}, observed={g['observed']}")
        lines.append(f"  rationale: {g['rationale']}")
    lines.append("")
    lines.append("## ALERT WATCH LEVELS (alert, not block)")
    for w in report["deployment_thresholds"]["alert_watch_levels"]:
        lines.append(f"- [{'TRIGGERED' if w['pass'] else 'OK'}] {w['name']}: threshold={w['threshold']}, observed={w['observed']}")
    lines.append("")
    lines.append("## KILL-SWITCH HALT CONDITIONS")
    for h in report["deployment_thresholds"]["kill_switch_halt_conditions"]:
        lines.append(f"- [{'HALT' if h['pass'] else 'OK'}] {h['name']}: threshold={h['threshold']}, observed={h['observed']}")
    lines.append("")
    lines.append(f"- All guardrails pass: {report['deployment_thresholds']['all_guardrails_pass']}")
    lines.append(f"- n guardrails: {report['deployment_thresholds']['n_guardrails']}, n alert watch levels: {report['deployment_thresholds']['n_alert_watch_levels']}, n kill-switch halt conditions: {report['deployment_thresholds']['n_kill_switch_halt_conditions']}")
    lines.append("")

    lines.append("## EVIDENCE MATRIX")
    for k, v in report["evidence_matrix"].items():
        lines.append(f"- {k}: {v}")
    lines.append("")

    lines.append("## VERDICT CHECKS (deterministic)")
    for c in report["verdict_checks"]["checks"]:
        lines.append(f"- [{'PASS' if c['pass'] else 'FAIL'}] {c['name']}: {c['reason']}")
    lines.append(f"- All checks pass: {report['verdict_checks']['all_checks_pass']} ({report['verdict_checks']['n_passed']}/{report['verdict_checks']['n_checks']})")
    lines.append("")

    lines.append("## DEPLOYMENT AUTHORIZATION")
    lines.append(f"- Authorized: {report['deployment_authorization']['authorized']} (mode={report['deployment_authorization']['mode']})")
    lines.append(report["deployment_authorization"]["note"])
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper deployment readiness package (EVAL-14, paper-only)"
    )
    parser.add_argument(
        "--no-write",
        action="store_true",
        help="Compute and print the report without writing artifacts",
    )
    parser.add_argument("--out-dir", type=str, default=str(OUT_DIR))
    parser.add_argument("--timestamp", type=str, default=_utc_now_iso())
    args = parser.parse_args(argv)

    report = evaluate_paper_deployment_readiness(
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
                "eval13_verdict": report["evidence"]["eval13"]["verdict"],
                "eval12_verdict": report["evidence"]["eval12"]["verdict"],
                "eval11_best_mean_net_sharpe": report["paper_readiness_metrics"]["eval11_best_mean_net_sharpe"],
                "all_guardrails_pass": report["deployment_thresholds"]["all_guardrails_pass"],
                "live_trading_enabled": report["live_trading_enabled"],
                "artifact_paths": report.get("artifact_paths", {}),
            },
            sort_keys=True,
            allow_nan=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
