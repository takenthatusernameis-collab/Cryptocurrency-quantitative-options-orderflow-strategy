#!/usr/bin/env python3
"""Generate phase60 toxicity-resilient hedge fusion depth paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
features/signals → execution/backtest (fees/slippage/risk) → delta-neutral
hedging + directional/hedge PnL attribution → reconciliation/monitoring.
Advisory paper evidence only: never enables live trading, never unblocks NEXT9,
no external venue mutation, no refactor of phase79/80/110.

Uses src.hedging.phase60_toxicity_resilient_hedge_fusion
(deterministic, paper-only, hard-gated; composes Phase54 risk fusion,
Phase58 flow toxicity, Phase39 kill-switches, Phase32 orderflow alpha)
to produce toxicity-resilient delta-vol-vega hedge-fusion surfaces across the
repo-prioritized venue×symbol scope with kill-switch/SLO posture and
finite-validated bounds.

Usage:
  PYTHONPATH=. /usr/share/miniconda/bin/python scripts/generate_phase60_toxicity_resilient_hedge_fusion_paper_evidence.py [--cycles N] [--seed S] [--write]
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

from src.hedging.phase60_toxicity_resilient_hedge_fusion import (  # noqa: E402
    Phase60ToxicityResilientHedgeFusion,
    Phase60ToxicityResilientHedgeConfig,
)
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION_PAPER_EVIDENCE"
VENUES = ("deribit", "okx", "binance")
SYMBOLS = ("BTC-USD", "ETH-USD")
UNDERLYINGS = ("BTC", "ETH")
UNDERLYING_BY_SYMBOL = {"BTC-USD": "BTC", "ETH-USD": "ETH"}
COVERAGE_CYCLES = 8


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
        "hedge_fusion_surface",
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
    surf = d.get("hedge_fusion_surface") or {}
    if surf.get("paper_only") is not True:
        issues.append("surface_paper_only_required")
    if set(surf.get("venues") or []) != set(VENUES):
        issues.append("surface_venues_must_match")
    if set(surf.get("symbols") or []) != set(SYMBOLS):
        issues.append("surface_symbols_must_match")
    if surf.get("deterministic_replay_equal") is not True:
        issues.append("surface_deterministic_replay_required")
    if surf.get("bounds_ok") is not True:
        issues.append("surface_bounds_ok_required")
    if int(surf.get("n_hedges") or 0) <= 0:
        issues.append("surface_hedges_required")
    cov = d.get("venue_symbol_coverage") or []
    pairs = {(x.get("venue"), x.get("symbol")) for x in cov if isinstance(x, dict)}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    if pairs != expected:
        issues.append("venue_symbol_coverage_must_match")
    if not all(isinstance(x, dict) and x.get("paper_only") is True for x in cov):
        issues.append("coverage_rows_must_be_paper_only")
    if not all(isinstance(x, dict) and x.get("deterministic_probe_hedge_id") for x in cov):
        issues.append("coverage_rows_must_have_probe")
    if not all(isinstance(x, dict) and bool(x.get("probe_finite")) for x in cov):
        issues.append("coverage_rows_must_have_finite_probe")
    rp = d.get("risk_posture") or {}
    if rp.get("kill_switch_slo_posture") not in ("armed_paper", "observed_paper", "paper_guarded"):
        issues.append("risk_posture_invalid")
    if rp.get("paper_only") is not True:
        issues.append("risk_posture_paper_only_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _run_scope(seed: int, cycles: int, venue: str, symbol: str) -> Dict[str, Any]:
    """Deterministic phase60 toxicity-resilient hedge-fusion probe for one venue×symbol scope.

    Pins venue/underlying for stable finite probe evidence; paper-only hard-gated,
    no external venue mutation.
    """
    underlying = UNDERLYING_BY_SYMBOL[symbol]
    cfg = Phase60ToxicityResilientHedgeConfig(
        seed=int(seed),
        paper_only=True,
        venues=(venue,),
        underlyings=(underlying,),
        cycles=int(cycles),
    )
    eng = Phase60ToxicityResilientHedgeFusion(cfg)
    rep = eng.run_hedge_fusion(cycles=int(cycles))
    hedges = list(getattr(eng, "hedges", []) or [])
    regimes = list(getattr(eng, "regimes", []) or [])
    clips = list(getattr(eng, "limit_clips", []) or [])
    delta_vals = [float(h.get("delta_notional_usd") or 0.0) for h in hedges]
    vega_vals = [float(h.get("vega_notional_usd") or 0.0) for h in hedges]
    gamma_vals = [float(h.get("gamma_notional_usd") or 0.0) for h in hedges]
    ratio_vals = [float(h.get("hedge_ratio") or 0.0) for h in hedges]
    tox_vals = [float(h.get("toxicity") or 0.0) for h in hedges]
    vol_vals = [float(h.get("vol_shock") or 0.0) for h in hedges]
    avg_delta = sum(delta_vals) / max(1, len(delta_vals))
    avg_vega = sum(vega_vals) / max(1, len(vega_vals))
    avg_gamma = sum(gamma_vals) / max(1, len(gamma_vals))
    avg_ratio = sum(ratio_vals) / max(1, len(ratio_vals))
    avg_tox = sum(tox_vals) / max(1, len(tox_vals))
    avg_vol = sum(vol_vals) / max(1, len(vol_vals))
    max_delta_ratio = max((v / cfg.max_delta_notional_usd for v in delta_vals), default=0.0)
    max_vega_ratio = max((v / cfg.max_vega_notional_usd for v in vega_vals), default=0.0)
    max_gamma_ratio = max((v / cfg.max_gamma_notional_usd for v in gamma_vals), default=0.0)
    max_bound_ratio = max(max_delta_ratio, max_vega_ratio, max_gamma_ratio)
    regime_counts: Dict[str, int] = {}
    for r in regimes:
        regime_counts[str(r.get("regime") or "unknown")] = int(regime_counts.get(str(r.get("regime") or "unknown"), 0)) + 1
    finite_ok = all(
        math.isfinite(float(x))
        for x in (
            avg_delta, avg_vega, avg_gamma, avg_ratio, avg_tox, avg_vol,
            max_delta_ratio, max_vega_ratio, max_gamma_ratio, max_bound_ratio,
            float(rep.get("avg_toxicity") or 0.0), float(rep.get("avg_vol_shock") or 0.0),
        )
    )
    # Delta-neutral posture: all notionals clipped within hard bounds; under kill-switch
    # halt (mult=0) the book is fully flat (delta-neutral). Hedge ratios bounded.
    delta_neutral_guarded = bool(
        max_bound_ratio <= 1.0
        and all(0.0 <= v for v in delta_vals)
        and all(0.0 <= v for v in vega_vals)
        and all(0.0 <= v for v in gamma_vals)
    )
    hedge_ratio_bounded = bool(
        all(cfg.hedge_ratio_min <= float(h.get("hedge_ratio") or 0.0) <= cfg.hedge_ratio_max for h in hedges)
    ) if hedges else True
    return serialize_metrics_strict(
        {
            "phase": str(rep.get("phase") or "PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION"),
            "paper_only": True,
            "venue": venue,
            "symbol": symbol,
            "underlying": underlying,
            "cycles": int(rep.get("cycles") or cycles),
            "n_hedges": int(rep.get("n_hedges") or len(hedges)),
            "n_adjustments": int(rep.get("n_adjustments") or 0),
            "n_limit_clips": int(rep.get("n_limit_clips") or len(clips)),
            "n_regime_high": int(rep.get("n_regime_high") or 0),
            "regime_counts": regime_counts,
            "avg_toxicity": float(rep.get("avg_toxicity") or 0.0),
            "avg_vol_shock": float(rep.get("avg_vol_shock") or 0.0),
            "avg_toxicity_per_hedge": float(avg_tox),
            "avg_vol_shock_per_hedge": float(avg_vol),
            "avg_hedge_ratio": float(avg_ratio),
            "avg_delta_notional_usd": float(avg_delta),
            "avg_vega_notional_usd": float(avg_vega),
            "avg_gamma_notional_usd": float(avg_gamma),
            "max_delta_notional_usd": float(cfg.max_delta_notional_usd),
            "max_vega_notional_usd": float(cfg.max_vega_notional_usd),
            "max_gamma_notional_usd": float(cfg.max_gamma_notional_usd),
            "max_delta_bound_ratio": float(max_delta_ratio),
            "max_vega_bound_ratio": float(max_vega_ratio),
            "max_gamma_bound_ratio": float(max_gamma_ratio),
            "max_bound_ratio": float(max_bound_ratio),
            "bounds_within_limits": bool(max_bound_ratio <= 1.0),
            "delta_neutral_guarded": bool(delta_neutral_guarded),
            "hedge_ratio_bounded": bool(hedge_ratio_bounded),
            "halted": bool(rep.get("halted")),
            "gates_ok": bool(rep.get("gates_ok")) and bool(finite_ok),
            "risk54_ok": bool(rep.get("risk54_ok")),
            "tox58_ok": bool(rep.get("tox58_ok")),
            "seed": int(seed),
            "hedge_ids": [str(h.get("hedge_id")) for h in hedges[:3]],
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
                        "deterministic_probe_hedge_id": f"p60toxhedgef:{venue}:{symbol}:{int(seed)+vi*100+si}",
                        "probe_cycle": 0,
                        "probe_gates_ok": bool(rep.get("gates_ok")),
                        "probe_halted": bool(rep.get("halted")),
                        "probe_n_hedges": int(rep.get("n_hedges") or 0),
                        "probe_n_adjustments": int(rep.get("n_adjustments") or 0),
                        "probe_n_limit_clips": int(rep.get("n_limit_clips") or 0),
                        "probe_avg_hedge_ratio": float(rep.get("avg_hedge_ratio") or 0.0),
                        "probe_avg_delta_notional_usd": float(rep.get("avg_delta_notional_usd") or 0.0),
                        "probe_avg_vega_notional_usd": float(rep.get("avg_vega_notional_usd") or 0.0),
                        "probe_avg_gamma_notional_usd": float(rep.get("avg_gamma_notional_usd") or 0.0),
                        "probe_max_bound_ratio": float(rep.get("max_bound_ratio") or 0.0),
                        "probe_bounds_within_limits": bool(rep.get("bounds_within_limits")),
                        "probe_delta_neutral_guarded": bool(rep.get("delta_neutral_guarded")),
                        "probe_hedge_ratio_bounded": bool(rep.get("hedge_ratio_bounded")),
                        "probe_avg_toxicity": float(rep.get("avg_toxicity_per_hedge") or 0.0),
                        "probe_avg_vol_shock": float(rep.get("avg_vol_shock_per_hedge") or 0.0),
                        "probe_finite": all(
                            math.isfinite(float(rep.get(k) or 0.0))
                            for k in (
                                "avg_delta_notional_usd", "avg_vega_notional_usd", "avg_gamma_notional_usd",
                                "avg_hedge_ratio", "max_bound_ratio", "avg_toxicity_per_hedge", "avg_vol_shock_per_hedge",
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
        "n_hedges_positive": int(rep.get("n_hedges") or 0) > 0,
        "gates_ok": bool(rep.get("gates_ok")),
        "bounds_within_limits": bool(rep.get("bounds_within_limits")),
        "delta_neutral_guarded": bool(rep.get("delta_neutral_guarded")),
        "hedge_ratio_bounded": bool(rep.get("hedge_ratio_bounded")),
        "avg_delta_finite_nonneg": math.isfinite(float(rep.get("avg_delta_notional_usd") or 0.0)) and float(rep.get("avg_delta_notional_usd") or 0.0) >= 0.0,
        "avg_vega_finite_nonneg": math.isfinite(float(rep.get("avg_vega_notional_usd") or 0.0)) and float(rep.get("avg_vega_notional_usd") or 0.0) >= 0.0,
        "avg_gamma_finite_nonneg": math.isfinite(float(rep.get("avg_gamma_notional_usd") or 0.0)) and float(rep.get("avg_gamma_notional_usd") or 0.0) >= 0.0,
        "max_bound_ratio_le_1": math.isfinite(float(rep.get("max_bound_ratio") or 0.0)) and 0.0 <= float(rep.get("max_bound_ratio") or 0.0) <= 1.0,
        "avg_hedge_ratio_finite_positive": math.isfinite(float(rep.get("avg_hedge_ratio") or 0.0)) and float(rep.get("avg_hedge_ratio") or 0.0) > 0.0,
        "avg_toxicity_in_0_1": math.isfinite(float(rep.get("avg_toxicity_per_hedge") or 0.0)) and 0.0 <= float(rep.get("avg_toxicity_per_hedge") or 0.0) <= 1.0,
        "avg_vol_shock_finite_nonneg": math.isfinite(float(rep.get("avg_vol_shock_per_hedge") or 0.0)) and float(rep.get("avg_vol_shock_per_hedge") or 0.0) >= 0.0,
        "all_reports_paper_only": bool(rep.get("paper_only")),
    }
    return {"report": rep, "deterministic_replay_equal": bool(same), "bounds": bounds, "bounds_ok": all(bool(v) for v in bounds.values())}


def generate(cycles: int = 80, seed: int = 60061) -> Dict[str, Any]:
    checks = _deterministic_checks(seed=seed, cycles=cycles)
    rep = checks["report"]
    coverage = _coverage_rows(seed=seed, cycles=max(1, COVERAGE_CYCLES))
    delta_vals = [float(x["probe_avg_delta_notional_usd"]) for x in coverage]
    vega_vals = [float(x["probe_avg_vega_notional_usd"]) for x in coverage]
    gamma_vals = [float(x["probe_avg_gamma_notional_usd"]) for x in coverage]
    ratio_vals = [float(x["probe_max_bound_ratio"]) for x in coverage]
    hedge_ratio_vals = [float(x["probe_avg_hedge_ratio"]) for x in coverage]
    tox_vals = [float(x["probe_avg_toxicity"]) for x in coverage]
    vol_vals = [float(x["probe_avg_vol_shock"]) for x in coverage]
    halted_cycles = sum(1 for x in coverage if bool(x["probe_halted"]))
    gates_all_ok = all(bool(x["probe_gates_ok"]) for x in coverage)
    risk_posture = {
        "paper_only": True,
        "kill_switch_slo_posture": "paper_guarded" if (halted_cycles or not gates_all_ok) else "armed_paper",
        "halted_coverage_rows": int(halted_cycles),
        "all_coverage_gates_ok": bool(gates_all_ok),
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
                "phase": str(rep.get("phase") or "PHASE60_TOXICITY_RESILIENT_HEDGE_FUSION"),
                "cycles": int(cycles),
                "probe_total_cycles": int(rep.get("cycles") or 0),
                "gates_ok": bool(rep.get("gates_ok")),
                "slo_ok": bool(rep.get("gates_ok")),
                "n_hedges": int(rep.get("n_hedges") or 0),
                "n_adjustments": int(rep.get("n_adjustments") or 0),
                "n_limit_clips": int(rep.get("n_limit_clips") or 0),
                "n_regime_high": int(rep.get("n_regime_high") or 0),
                "avg_hedge_ratio": float(rep.get("avg_hedge_ratio") or 0.0),
                "avg_delta_notional_usd": float(rep.get("avg_delta_notional_usd") or 0.0),
                "avg_vega_notional_usd": float(rep.get("avg_vega_notional_usd") or 0.0),
                "avg_gamma_notional_usd": float(rep.get("avg_gamma_notional_usd") or 0.0),
                "risk54_integration_ok": bool(rep.get("risk54_ok")),
                "tox58_integration_ok": bool(rep.get("tox58_ok")),
                "halted": bool(rep.get("halted")),
                "source_seed": int(rep.get("seed") or seed),
            },
            "hedge_fusion_surface": {
                "paper_only": True,
                "venues": list(VENUES),
                "symbols": list(SYMBOLS),
                "underlyings": list(UNDERLYINGS),
                "deterministic_replay_equal": bool(checks["deterministic_replay_equal"]),
                "bounds_ok": bool(checks["bounds_ok"]),
                "bounds": checks["bounds"],
                "coverage_pairs": len(coverage),
                "n_hedges": int(rep.get("n_hedges") or 0),
                "n_adjustments": int(rep.get("n_adjustments") or 0),
                "n_limit_clips": int(rep.get("n_limit_clips") or 0),
                "n_regime_high": int(rep.get("n_regime_high") or 0),
                "avg_hedge_ratio": float(sum(hedge_ratio_vals) / max(1, len(hedge_ratio_vals))),
                "avg_delta_notional_usd": float(sum(delta_vals) / max(1, len(delta_vals))),
                "avg_vega_notional_usd": float(sum(vega_vals) / max(1, len(vega_vals))),
                "avg_gamma_notional_usd": float(sum(gamma_vals) / max(1, len(gamma_vals))),
                "max_bound_ratio": float(max(ratio_vals) if ratio_vals else 0.0),
                "avg_toxicity": float(sum(tox_vals) / max(1, len(tox_vals))),
                "avg_vol_shock": float(sum(vol_vals) / max(1, len(vol_vals))),
            },
            "venue_symbol_coverage": coverage,
            "risk_posture": risk_posture,
            "evidence_refs": [
                "scripts/generate_phase60_toxicity_resilient_hedge_fusion_paper_evidence.py",
                "src/hedging/phase60_toxicity_resilient_hedge_fusion.py",
                "src/risk/phase54_realtime_risk_fusion_engine.py",
                "src/risk/phase39_kill_switches_circuit_breakers.py",
                "src/orderflow/phase58_flow_toxicity_mitigator.py",
                "src/orderflow/phase32_orderflow_alpha_integration.py",
                "src/telemetry/serialization.py",
                "research_state/PHASE59_AUTONOMOUS_EXECUTION_HARDENING_LOOP_PAPER_EVIDENCE_20261107T175942Z.json",
                "research_state/PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION_PAPER_EVIDENCE_20261107T172922Z.json",
                "research_state/PHASE58_ADAPTIVE_OPTIONS_SMART_ORDER_ROUTER_PAPER_EVIDENCE_20261107T171854Z.json",
                "research_state/PHASE59_FRAGMENTATION_TOXICITY_ARB_PAPER_EVIDENCE_20261107T170655Z.json",
                "research_state/PHASE58_FLOW_TOXICITY_MITIGATOR_PAPER_EVIDENCE_20261107T165643Z.json",
                "research_state/PHASE56_CROSS_VENUE_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T162958Z.json",
                "research_state/PHASE55_CROSS_VENUE_ORDERFLOW_EXECUTION_VALIDATOR_PAPER_EVIDENCE_20261107T163505Z.json",
                "research_state/PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T161211Z.json",
                "research_state/PHASE53_CROSS_MARGIN_STRESS_PROPAGATION_PAPER_EVIDENCE_20261107T152913Z.json",
                "research_state/PHASE52_REALTIME_LIQUIDITY_ALLOCATOR_PAPER_EVIDENCE_20261107T152449Z.json",
                "research_state/PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE_20261107T142001Z.json",
                "research_state/CONTINUOUS_VALIDATION_20261107T181302Z.json",
                "research_state/PAPER_OPS_SESSION_GATE_20261107T181638Z.json",
            ],
            "cross_refs": [
                "phase60_toxicity_resilient_hedge_fusion.py:Phase60ToxicityResilientHedgeFusion/Phase60ToxicityResilientHedgeConfig",
                "PHASE59_AUTONOMOUS_EXECUTION_HARDENING_LOOP_PAPER_EVIDENCE_20261107T175942Z.json",
                "PHASE59_ADAPTIVE_CROSS_ASSET_HEDGE_FUSION_PAPER_EVIDENCE_20261107T172922Z.json",
                "PHASE58_ADAPTIVE_OPTIONS_SMART_ORDER_ROUTER_PAPER_EVIDENCE_20261107T171854Z.json",
                "PHASE59_FRAGMENTATION_TOXICITY_ARB_PAPER_EVIDENCE_20261107T170655Z.json",
                "PHASE58_FLOW_TOXICITY_MITIGATOR_PAPER_EVIDENCE_20261107T165643Z.json",
                "PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE_20261107T142001Z.json",
                "PAPER_OPS_SESSION_GATE_20261107T181638Z.json",
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
    ap.add_argument("--seed", type=int, default=60061)
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
            json.dump(d, f, indent=2, allow_nan=False)
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
