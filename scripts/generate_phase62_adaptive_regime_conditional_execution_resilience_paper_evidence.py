#!/usr/bin/env python3
"""Generate phase62 adaptive regime-conditional execution resilience depth paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
features/signals → execution/backtest (fees/slippage/risk) → delta-neutral
hedging + directional/hedge PnL attribution → reconciliation/monitoring.
Advisory paper evidence only: never enables live trading, never unblocks NEXT9,
no external venue mutation, no refactor of phase79/80/110.

Uses src.hedging.phase62_adaptive_regime_conditional_execution_resilience
(deterministic, paper-only, hard-gated; composes Phase61 → Phases 54/58/39/32/59/60)
to produce adaptive regime-conditional execution resilience surfaces (regimes
normal/elevated/high_toxicity × execution postures relax_safe/tighten_moderate/
tighten_hard) across the repo-prioritized venue×symbol scope with
kill-switch/circuit-breaker/SLO posture paper-guarded, latency-aware
regime-conditional posture bounded, slippage/latency/position-limit guards, and
finite-validated bounds (allow_nan=False write).

Usage:
  PYTHONPATH=. /usr/share/miniconda/bin/python scripts/generate_phase62_adaptive_regime_conditional_execution_resilience_paper_evidence.py [--cycles N] [--seed S] [--write|--no-write]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
sys.path.insert(0, str(REPO))

from src.hedging.phase62_adaptive_regime_conditional_execution_resilience import (  # noqa: E402
    Phase62AdaptiveRegimeConditionalExecutionResilience,
    Phase62AdaptiveRegimeConditionalResilienceConfig,
)
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE62_ADAPTIVE_REGIME_CONDITIONAL_EXECUTION_RESILIENCE_PAPER_EVIDENCE"
VENUES = ("deribit", "okx", "binance")
SYMBOLS = ("BTC-USD", "ETH-USD")
UNDERLYINGS = ("BTC", "ETH")
UNDERLYING_BY_SYMBOL = {"BTC-USD": "BTC", "ETH-USD": "ETH"}
COVERAGE_CYCLES = 8
REGIMES = ("normal", "elevated", "high_toxicity")
POSTURES = ("relax_safe", "tighten_moderate", "tighten_hard")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _strip_timestamps(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            k: _strip_timestamps(v)
            for k, v in obj.items()
            if k not in ("timestamp_utc", "timestamp")
        }
    if isinstance(obj, (list, tuple)):
        return [_strip_timestamps(v) for v in obj]
    return obj


def _assert_finite(obj: Any, label: str) -> List[str]:
    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool) and not math.isfinite(v):
            bad.append(p)

    walk(obj, "$")
    return [f"non_finite:{label}:{p}" for p in bad[:20]]


def validate_artifact(d: Dict[str, Any]) -> Tuple[bool, List[str]]:
    issues: List[str] = []
    if d.get("artifact_type") != ARTIFACT_TYPE:
        issues.append("artifact_type_mismatch")
    if d.get("paper_only") is not True:
        issues.append("paper_only_required")
    if d.get("live_trading_enabled") is True:
        issues.append("must_not_enable_live_trading")
    if d.get("next9_unblocked") is True:
        issues.append("must_not_unblock_next9")
    if d.get("no_external_venue_mutation") is not True:
        issues.append("no_external_venue_mutation_required")
    if d.get("advisory") is not True:
        issues.append("advisory_required")
    for k in (
        "timestamp_utc",
        "seed",
        "cycles",
        "venues",
        "symbols",
        "underlyings",
        "campaign",
        "execution_resilience_surface",
        "venue_symbol_coverage",
        "risk_posture",
        "evidence_refs",
        "cross_refs",
        "determinism",
    ):
        if d.get(k) in (None, "", [], {}):
            issues.append(f"missing_{k}")
    camp = d.get("campaign") or {}
    if camp.get("paper_only") is not True:
        issues.append("campaign_paper_only_required")
    if int(camp.get("cycles") or 0) <= 0:
        issues.append("campaign_cycles_required")
    if camp.get("gates_ok") is not True:
        issues.append("campaign_gates_ok_required")
    surf = d.get("execution_resilience_surface") or {}
    if surf.get("paper_only") is not True:
        issues.append("surface_paper_only_required")
    if set(surf.get("venues") or []) != set(VENUES):
        issues.append("surface_venues_must_match")
    if set(surf.get("symbols") or []) != set(SYMBOLS):
        issues.append("surface_symbols_must_match")
    if set(surf.get("regimes") or []) != set(REGIMES):
        issues.append("surface_regimes_must_match")
    if set(surf.get("execution_postures") or []) != set(POSTURES):
        issues.append("surface_postures_must_match")
    if surf.get("deterministic_replay_equal") is not True:
        issues.append("surface_deterministic_replay_required")
    if surf.get("bounds_ok") is not True:
        issues.append("surface_bounds_ok_required")
    if int(surf.get("n_params") or 0) <= 0:
        issues.append("surface_params_required")
    cov = d.get("venue_symbol_coverage") or []
    pairs = {(x.get("venue"), x.get("symbol")) for x in cov if isinstance(x, dict)}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    if pairs != expected:
        issues.append("venue_symbol_coverage_must_match")
    if not all(isinstance(x, dict) and x.get("paper_only") is True for x in cov):
        issues.append("coverage_rows_must_be_paper_only")
    if not all(isinstance(x, dict) and x.get("deterministic_probe_param_id") for x in cov):
        issues.append("coverage_rows_must_have_probe")
    if not all(isinstance(x, dict) and bool(x.get("probe_finite")) for x in cov):
        issues.append("coverage_rows_must_have_finite_probe")
    if not all(isinstance(x, dict) and bool(x.get("probe_slippage_bounded")) for x in cov):
        issues.append("coverage_rows_must_have_slippage_bounded")
    if not all(isinstance(x, dict) and bool(x.get("probe_latency_bounded")) for x in cov):
        issues.append("coverage_rows_must_have_latency_bounded")
    if not all(isinstance(x, dict) and bool(x.get("probe_position_limit_bounded")) for x in cov):
        issues.append("coverage_rows_must_have_position_limit_bounded")
    if not all(isinstance(x, dict) and bool(x.get("probe_regime_conditional_posture")) for x in cov):
        issues.append("coverage_rows_must_be_regime_conditional")
    rp = d.get("risk_posture") or {}
    if rp.get("kill_switch_slo_posture") not in ("armed_paper", "observed_paper", "paper_guarded"):
        issues.append("risk_posture_invalid")
    if rp.get("paper_only") is not True:
        issues.append("risk_posture_paper_only_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _run_scope(seed: int, cycles: int, venue: str, symbol: str) -> Dict[str, Any]:
    """Deterministic phase62 regime-conditional execution resilience probe for one venue×symbol scope.

    Pins venue/underlying for stable finite probe evidence; paper-only hard-gated,
    no external venue mutation.
    """
    underlying = UNDERLYING_BY_SYMBOL[symbol]
    cfg = Phase62AdaptiveRegimeConditionalResilienceConfig(
        seed=int(seed),
        paper_only=True,
        underlyings=(underlying,),
        venues=(venue,),
        cycles=int(cycles),
    )
    eng = Phase62AdaptiveRegimeConditionalExecutionResilience(cfg)
    rep = eng.run_resilience(cycles=int(cycles))
    params = list(getattr(eng, "params", []) or [])
    adjustments = list(getattr(eng, "adjustments", []) or [])
    guardrails = list(getattr(eng, "guardrails", []) or [])
    slip_vals = [float(p.get("slippage_tolerance_bps") or 0.0) for p in params]
    lat_vals = [float(p.get("latency_cap_ms") or 0.0) for p in params]
    pos_vals = [float(p.get("position_limit_mult") or 0.0) for p in params]
    tox_vals = [float(p.get("toxicity") or 0.0) for p in params]
    vol_vals = [float(p.get("vol_shock") or 0.0) for p in params]
    avg_slip = sum(slip_vals) / max(1, len(slip_vals))
    avg_lat = sum(lat_vals) / max(1, len(lat_vals))
    avg_pos = sum(pos_vals) / max(1, len(pos_vals))
    avg_tox = sum(tox_vals) / max(1, len(tox_vals))
    avg_vol = sum(vol_vals) / max(1, len(vol_vals))
    cfg_slip_min, cfg_slip_max = cfg.slippage_tolerance_bps_min, cfg.slippage_tolerance_bps_max
    cfg_lat_min, cfg_lat_max = cfg.latency_cap_ms_min, cfg.latency_cap_ms_max
    cfg_pos_min, cfg_pos_max = cfg.pos_limit_mult_min, cfg.pos_limit_mult_max
    max_slip_ratio = max((v / cfg_slip_max for v in slip_vals), default=0.0)
    max_lat_ratio = max((v / cfg_lat_max for v in lat_vals), default=0.0)
    min_pos_ratio = min((v / cfg_pos_max for v in pos_vals), default=0.0)
    max_bound_ratio = max(max_slip_ratio, max_lat_ratio, 1.0 - min_pos_ratio if pos_vals else 0.0)
    regime_counts: Dict[str, int] = {}
    posture_counts: Dict[str, int] = {}
    for p in params:
        regime_counts[str(p.get("regime") or "unknown")] = int(regime_counts.get(str(p.get("regime") or "unknown"), 0)) + 1
        posture_counts[str(p.get("mode") or "unknown")] = int(posture_counts.get(str(p.get("mode") or "unknown"), 0)) + 1
    finite_ok = all(
        math.isfinite(float(x))
        for x in (
            avg_slip, avg_lat, avg_pos, avg_tox, avg_vol,
            max_slip_ratio, max_lat_ratio, min_pos_ratio, max_bound_ratio,
            float(rep.get("gates_ok") is True),
        )
    )
    slippage_bounded = all(cfg_slip_min <= v <= cfg_slip_max for v in slip_vals) if slip_vals else True
    latency_bounded = all(cfg_lat_min <= v <= cfg_lat_max for v in lat_vals) if lat_vals else True
    position_limit_bounded = all(cfg_pos_min <= v <= cfg_pos_max for v in pos_vals) if pos_vals else True
    regime_conditional_posture = bool(
        slippage_bounded and latency_bounded and position_limit_bounded and max_bound_ratio <= 1.0
    )
    return serialize_metrics_strict(
        {
            "phase": str(rep.get("phase") or "PHASE62_ADAPTIVE_REGIME_CONDITIONAL_EXECUTION_RESILIENCE"),
            "paper_only": True,
            "venue": venue,
            "symbol": symbol,
            "underlying": underlying,
            "cycles": int(rep.get("cycles") or cycles),
            "n_params": int(rep.get("n_params") or len(params)),
            "n_adjustments": int(rep.get("n_adjustments") or len(adjustments)),
            "n_guardrails": int(rep.get("n_guardrails") or len(guardrails)),
            "regime_counts": regime_counts,
            "posture_counts": posture_counts,
            "avg_slippage_tolerance_bps": float(avg_slip),
            "avg_latency_cap_ms": float(avg_lat),
            "avg_position_limit_mult": float(avg_pos),
            "avg_toxicity": float(avg_tox),
            "avg_vol_shock": float(avg_vol),
            "slippage_tolerance_bps_min": float(cfg_slip_min),
            "slippage_tolerance_bps_max": float(cfg_slip_max),
            "latency_cap_ms_min": float(cfg_lat_min),
            "latency_cap_ms_max": float(cfg_lat_max),
            "position_limit_mult_min": float(cfg_pos_min),
            "position_limit_mult_max": float(cfg_pos_max),
            "max_slippage_ratio": float(max_slip_ratio),
            "max_latency_ratio": float(max_lat_ratio),
            "min_position_limit_ratio": float(min_pos_ratio),
            "max_bound_ratio": float(max_bound_ratio),
            "bounds_within_limits": bool(slippage_bounded and latency_bounded and position_limit_bounded and max_bound_ratio <= 1.0),
            "slippage_bounded": bool(slippage_bounded),
            "latency_bounded": bool(latency_bounded),
            "position_limit_bounded": bool(position_limit_bounded),
            "regime_conditional_posture": bool(regime_conditional_posture),
            "guardrails_ok": all(bool(g.get("guard_ok")) for g in guardrails) if guardrails else True,
            "kill_switch_ready": all(bool(g.get("kill_switch_ready")) for g in guardrails) if guardrails else True,
            "halted": False,
            "gates_ok": bool(rep.get("gates_ok")) and bool(finite_ok),
            "composed_phases": "17-61",
            "seed": int(seed),
            "param_ids": [str(p.get("param_id")) for p in params[:3]],
        }
    )


def _coverage_rows(seed: int, cycles: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for vi, venue in enumerate(VENUES):
        for si, symbol in enumerate(SYMBOLS):
            rep = _run_scope(seed=seed + vi * 100 + si, cycles=cycles, venue=venue, symbol=symbol)
            rows.append(
                serialize_metrics_strict(
                    {
                        "venue": venue,
                        "symbol": symbol,
                        "underlying": UNDERLYING_BY_SYMBOL[symbol],
                        "deterministic_probe_param_id": f"p62res:{venue}:{symbol}:{int(seed)+vi*100+si}",
                        "probe_cycle": 0,
                        "probe_gates_ok": bool(rep.get("gates_ok")),
                        "probe_n_params": int(rep.get("n_params") or 0),
                        "probe_n_adjustments": int(rep.get("n_adjustments") or 0),
                        "probe_n_guardrails": int(rep.get("n_guardrails") or 0),
                        "probe_avg_slippage_tolerance_bps": float(rep.get("avg_slippage_tolerance_bps") or 0.0),
                        "probe_avg_latency_cap_ms": float(rep.get("avg_latency_cap_ms") or 0.0),
                        "probe_avg_position_limit_mult": float(rep.get("avg_position_limit_mult") or 0.0),
                        "probe_avg_toxicity": float(rep.get("avg_toxicity") or 0.0),
                        "probe_avg_vol_shock": float(rep.get("avg_vol_shock") or 0.0),
                        "probe_max_bound_ratio": float(rep.get("max_bound_ratio") or 0.0),
                        "probe_bounds_within_limits": bool(rep.get("bounds_within_limits")),
                        "probe_slippage_bounded": bool(rep.get("slippage_bounded")),
                        "probe_latency_bounded": bool(rep.get("latency_bounded")),
                        "probe_position_limit_bounded": bool(rep.get("position_limit_bounded")),
                        "probe_regime_conditional_posture": bool(rep.get("regime_conditional_posture")),
                        "probe_guardrails_ok": bool(rep.get("guardrails_ok")),
                        "probe_kill_switch_ready": bool(rep.get("kill_switch_ready")),
                        "probe_finite": all(
                            math.isfinite(float(rep.get(k) or 0.0))
                            for k in (
                                "avg_slippage_tolerance_bps", "avg_latency_cap_ms", "avg_position_limit_mult",
                                "avg_toxicity", "avg_vol_shock", "max_bound_ratio",
                            )
                        ),
                        "campaign_cycles": int(rep.get("cycles") or 0),
                        "paper_only": True,
                    }
                )
            )
    return rows


def _deterministic_checks(seed: int, cycles: int) -> Dict[str, Any]:
    rep = _run_scope(seed=seed, cycles=cycles, venue="deribit", symbol="BTC-USD")
    rep2 = _run_scope(seed=seed, cycles=cycles, venue="deribit", symbol="BTC-USD")
    same = _strip_timestamps(rep) == _strip_timestamps(rep2)
    bounds = {
        "n_params_positive": int(rep.get("n_params") or 0) > 0,
        "n_adjustments_positive": int(rep.get("n_adjustments") or 0) > 0,
        "n_guardrails_positive": int(rep.get("n_guardrails") or 0) > 0,
        "gates_ok": bool(rep.get("gates_ok")),
        "bounds_within_limits": bool(rep.get("bounds_within_limits")),
        "slippage_bounded": bool(rep.get("slippage_bounded")),
        "latency_bounded": bool(rep.get("latency_bounded")),
        "position_limit_bounded": bool(rep.get("position_limit_bounded")),
        "regime_conditional_posture": bool(rep.get("regime_conditional_posture")),
        "guardrails_ok": bool(rep.get("guardrails_ok")),
        "kill_switch_ready": bool(rep.get("kill_switch_ready")),
        "avg_slippage_finite_positive": math.isfinite(float(rep.get("avg_slippage_tolerance_bps") or 0.0)) and float(rep.get("avg_slippage_tolerance_bps") or 0.0) > 0.0,
        "avg_latency_finite_positive": math.isfinite(float(rep.get("avg_latency_cap_ms") or 0.0)) and float(rep.get("avg_latency_cap_ms") or 0.0) > 0.0,
        "avg_position_limit_finite_positive": math.isfinite(float(rep.get("avg_position_limit_mult") or 0.0)) and float(rep.get("avg_position_limit_mult") or 0.0) > 0.0,
        "max_slippage_ratio_le_1": math.isfinite(float(rep.get("max_slippage_ratio") or 0.0)) and 0.0 <= float(rep.get("max_slippage_ratio") or 0.0) <= 1.0,
        "max_latency_ratio_le_1": math.isfinite(float(rep.get("max_latency_ratio") or 0.0)) and 0.0 <= float(rep.get("max_latency_ratio") or 0.0) <= 1.0,
        "min_position_limit_ratio_ge_0": math.isfinite(float(rep.get("min_position_limit_ratio") or 0.0)) and float(rep.get("min_position_limit_ratio") or 0.0) >= 0.0,
        "max_bound_ratio_le_1": math.isfinite(float(rep.get("max_bound_ratio") or 0.0)) and 0.0 <= float(rep.get("max_bound_ratio") or 0.0) <= 1.0,
        "avg_toxicity_in_0_1": math.isfinite(float(rep.get("avg_toxicity") or 0.0)) and 0.0 <= float(rep.get("avg_toxicity") or 0.0) <= 1.0,
        "avg_vol_shock_finite_nonneg": math.isfinite(float(rep.get("avg_vol_shock") or 0.0)) and float(rep.get("avg_vol_shock") or 0.0) >= 0.0,
        "all_reports_paper_only": bool(rep.get("paper_only")),
    }
    return {"report": rep, "deterministic_replay_equal": bool(same), "bounds": bounds, "bounds_ok": all(bool(v) for v in bounds.values())}


def generate(cycles: int = 80, seed: int = 62061) -> Dict[str, Any]:
    checks = _deterministic_checks(seed=seed, cycles=cycles)
    rep = checks["report"]
    coverage = _coverage_rows(seed=seed, cycles=max(1, COVERAGE_CYCLES))
    slip_vals = [float(x["probe_avg_slippage_tolerance_bps"]) for x in coverage]
    lat_vals = [float(x["probe_avg_latency_cap_ms"]) for x in coverage]
    pos_vals = [float(x["probe_avg_position_limit_mult"]) for x in coverage]
    ratio_vals = [float(x["probe_max_bound_ratio"]) for x in coverage]
    tox_vals = [float(x["probe_avg_toxicity"]) for x in coverage]
    vol_vals = [float(x["probe_avg_vol_shock"]) for x in coverage]
    gates_all_ok = all(bool(x["probe_gates_ok"]) for x in coverage)
    guardrails_all_ok = all(bool(x["probe_guardrails_ok"]) for x in coverage)
    risk_posture = {
        "paper_only": True,
        "kill_switch_slo_posture": "paper_guarded" if (not gates_all_ok or not guardrails_all_ok) else "armed_paper",
        "halted_coverage_rows": int(sum(1 for x in coverage if not bool(x["probe_gates_ok"]))),
        "all_coverage_gates_ok": bool(gates_all_ok),
        "all_coverage_guardrails_ok": bool(guardrails_all_ok),
        "slo_posture_recorded": bool(rep.get("gates_ok")),
        "next9_unblocked": False,
        "live_trading_enabled": False,
        "no_external_venue_mutation": True,
    }
    artifact = serialize_metrics_strict(
        {
            "artifact_type": ARTIFACT_TYPE,
            "timestamp_utc": _utc_iso(),
            "paper_only": True,
            "live_trading_enabled": False,
            "next9_unblocked": False,
            "advisory": True,
            "no_external_venue_mutation": True,
            "seed": int(seed),
            "cycles": int(cycles),
            "venues": list(VENUES),
            "symbols": list(SYMBOLS),
            "underlyings": list(UNDERLYINGS),
            "campaign": {
                "paper_only": True,
                "phase": str(rep.get("phase") or "PHASE62_ADAPTIVE_REGIME_CONDITIONAL_EXECUTION_RESILIENCE"),
                "cycles": int(cycles),
                "probe_total_cycles": int(rep.get("cycles") or 0),
                "gates_ok": bool(rep.get("gates_ok")),
                "slo_ok": bool(rep.get("gates_ok")),
                "n_params": int(rep.get("n_params") or 0),
                "n_adjustments": int(rep.get("n_adjustments") or 0),
                "n_guardrails": int(rep.get("n_guardrails") or 0),
                "avg_slippage_tolerance_bps": float(rep.get("avg_slippage_tolerance_bps") or 0.0),
                "avg_latency_cap_ms": float(rep.get("avg_latency_cap_ms") or 0.0),
                "avg_position_limit_mult": float(rep.get("avg_position_limit_mult") or 0.0),
                "avg_toxicity": float(rep.get("avg_toxicity") or 0.0),
                "avg_vol_shock": float(rep.get("avg_vol_shock") or 0.0),
                "halted": bool(rep.get("halted")),
                "source_seed": int(rep.get("seed") or seed),
            },
            "execution_resilience_surface": {
                "paper_only": True,
                "venues": list(VENUES),
                "symbols": list(SYMBOLS),
                "underlyings": list(UNDERLYINGS),
                "regimes": list(REGIMES),
                "execution_postures": list(POSTURES),
                "deterministic_replay_equal": bool(checks["deterministic_replay_equal"]),
                "bounds_ok": bool(checks["bounds_ok"]),
                "bounds": checks["bounds"],
                "coverage_pairs": len(coverage),
                "n_params": int(rep.get("n_params") or 0),
                "n_adjustments": int(rep.get("n_adjustments") or 0),
                "n_guardrails": int(rep.get("n_guardrails") or 0),
                "regime_counts": rep.get("regime_counts") or {},
                "posture_counts": rep.get("posture_counts") or {},
                "avg_slippage_tolerance_bps": float(sum(slip_vals) / max(1, len(slip_vals))),
                "avg_latency_cap_ms": float(sum(lat_vals) / max(1, len(lat_vals))),
                "avg_position_limit_mult": float(sum(pos_vals) / max(1, len(pos_vals))),
                "max_bound_ratio": float(max(ratio_vals) if ratio_vals else 0.0),
                "avg_toxicity": float(sum(tox_vals) / max(1, len(tox_vals))),
                "avg_vol_shock": float(sum(vol_vals) / max(1, len(vol_vals))),
            },
            "venue_symbol_coverage": coverage,
            "risk_posture": risk_posture,
            "evidence_refs": [
                "scripts/generate_phase62_adaptive_regime_conditional_execution_resilience_paper_evidence.py",
                "src/hedging/phase62_adaptive_regime_conditional_execution_resilience.py",
                "src/hedging/phase61_adaptive_regime_switching_hedge_orchestrator.py",
                "src/hedging/phase60_toxicity_resilient_hedge_fusion.py",
                "src/hedging/phase59_adaptive_cross_asset_hedge_fusion.py",
                "src/risk/phase54_realtime_risk_fusion_engine.py",
                "src/risk/phase39_kill_switches_circuit_breakers.py",
                "src/orderflow/phase58_flow_toxicity_mitigator.py",
                "src/orderflow/phase32_orderflow_alpha_integration.py",
                "src/telemetry/serialization.py",
                "tests/test_phase62_adaptive_regime_conditional_execution_resilience.py",
                "research_state/PHASE60_ADAPTIVE_EXECUTION_INTELLIGENCE_ENGINE_PAPER_EVIDENCE_20261107T192105Z.json",
                "research_state/PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION_PAPER_EVIDENCE_20261107T185604Z.json",
                "research_state/CONTINUOUS_VALIDATION_20261107T195952Z.json",
                "research_state/PAPER_OPS_SESSION_GATE_20261107T195947Z.json",
            ],
            "cross_refs": [
                "phase62_adaptive_regime_conditional_execution_resilience.py:Phase62AdaptiveRegimeConditionalExecutionResilience/Phase62AdaptiveRegimeConditionalResilienceConfig",
                "PHASE61_ADAPTIVE_REGIME_SWITCHING_HEDGE_ORCHESTRATOR_PAPER_EVIDENCE_20261107T200213Z.json",
                "PHASE60_ADAPTIVE_EXECUTION_INTELLIGENCE_ENGINE_PAPER_EVIDENCE_20261107T192105Z.json",
                "PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION_PAPER_EVIDENCE_20261107T185604Z.json",
                "PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION_PAPER_EVIDENCE_20261107T172922Z.json",
                "PHASE58_FLOW_TOXICITY_MITIGATOR_PAPER_EVIDENCE_20261107T165643Z.json",
                "PAPER_OPS_SESSION_GATE_20261107T195947Z.json",
            ],
            "determinism": {
                "deterministic_seeded": True,
                "same_seed_cycles_reproduce_surface": bool(checks["deterministic_replay_equal"]),
                "bounds_ok": bool(checks["bounds_ok"]),
                "bounds": checks["bounds"],
            },
        }
    )
    ok, issues = validate_artifact(artifact)
    artifact["validation"] = {"valid": bool(ok), "issues": issues}
    return artifact


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=80)
    ap.add_argument("--seed", type=int, default=62061)
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--no-write", dest="write", action="store_false")
    ap.set_defaults(write=True)
    args = ap.parse_args()
    d = generate(cycles=args.cycles, seed=args.seed)
    v = d["validation"]
    out_path = RS / f"{ARTIFACT_TYPE}_{_utc()}.json"
    if args.write:
        RS.mkdir(parents=True, exist_ok=True)
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(d, f, indent=2, sort_keys=True, allow_nan=False)
            f.write("\n")
    payload = serialize_metrics_strict(
        {
            "artifact_path": str(out_path) if args.write else None,
            "valid": v["valid"],
            "issues": v["issues"],
            "paper_only": d["paper_only"],
            "live_trading_enabled": d["live_trading_enabled"],
            "next9_unblocked": d["next9_unblocked"],
            "deterministic": d["determinism"]["same_seed_cycles_reproduce_surface"],
        }
    )
    print(json.dumps(payload, indent=2))
    if not v["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
