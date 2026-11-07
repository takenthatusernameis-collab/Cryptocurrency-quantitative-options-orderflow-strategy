#!/usr/bin/env python3
"""Generate phase55 cross-venue orderflow execution validator paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
features/signals → execution/backtest (fees/slippage/risk) → delta-neutral
hedging + directional/hedge PnL attribution → reconciliation/monitoring.
Advisory paper evidence only: never enables live trading, never unblocks NEXT9,
no external venue mutation, no refactor of phase79/80/110.

Uses src.execution.phase55_cross_venue_orderflow_execution_validator
(deterministic, paper-only, hard-gated) to produce cross-venue options
orderflow execution validation surfaces (fill-rate vs model, slippage/TCA
reconciliation, per-venue latency scoring, toxicity-adjusted execution quality)
across the repo-prioritized venue×symbol scope.

Usage:
  PYTHONPATH=. python3 scripts/generate_phase55_cross_venue_orderflow_execution_validator_paper_evidence.py [--cycles N] [--seed S] [--write]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
sys.path.insert(0, str(REPO))

from src.execution.phase55_cross_venue_orderflow_execution_validator import (  # noqa: E402
    Phase55CrossVenueOrderflowExecutionValidator,
    Phase55ExecutionValidationConfig,
)
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE55_CROSS_VENUE_ORDERFLOW_EXECUTION_VALIDATOR_PAPER_EVIDENCE"
# Repo-priority scope per repo name: Deribit/OKX/Binance × BTC/ETH.
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
        "execution_validation_surface",
        "venue_symbol_coverage",
        "execution_stress_summary",
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
    if int(camp.get("total_fills") or 0) <= 0:
        issues.append("campaign_total_fills_required")
    if camp.get("gates_ok") is not True:
        issues.append("campaign_gates_ok_required")
    surf = d.get("execution_validation_surface") or {}
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
    cov = d.get("venue_symbol_coverage") or []
    pairs = {(x.get("venue"), x.get("symbol")) for x in cov if isinstance(x, dict)}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    if pairs != expected:
        issues.append("venue_symbol_coverage_must_match")
    if not all(isinstance(x, dict) and x.get("paper_only") is True for x in cov):
        issues.append("coverage_rows_must_be_paper_only")
    if not all(isinstance(x, dict) and x.get("deterministic_probe_route_id") for x in cov):
        issues.append("coverage_rows_must_have_probe")
    if not all(isinstance(x, dict) and bool(x.get("probe_finite")) for x in cov):
        issues.append("coverage_rows_must_have_finite_probe")
    es = d.get("execution_stress_summary") or {}
    if es.get("paper_only") is not True:
        issues.append("execution_stress_paper_only_required")
    if int(es.get("total_fills") or 0) <= 0:
        issues.append("total_fills_required")
    if float(es.get("avg_quality_score") or -1.0) < 0.0:
        issues.append("avg_quality_score_invalid")
    rp = d.get("risk_posture") or {}
    if rp.get("kill_switch_slo_posture") not in ("armed_paper", "observed_paper", "paper_guarded"):
        issues.append("risk_posture_invalid")
    if rp.get("paper_only") is not True:
        issues.append("risk_posture_paper_only_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _run_scope(seed: int, cycles: int, venue: str, symbol: str) -> Dict[str, Any]:
    """Run deterministic phase55 validation for one venue×symbol probe scope.

    Phase55 validates across its configured venue set; we probe a single venue
    while keeping paper-only guards and mapping repo-priority symbol to underlying.
    """
    underlying = UNDERLYING_BY_SYMBOL[symbol]
    with tempfile.TemporaryDirectory() as td:
        cfg = Phase55ExecutionValidationConfig(
            seed=int(seed),
            paper_only=True,
            underlyings=(underlying,),
            venues=(venue,),
            cycles=int(cycles),
            outdir=td,
        )
        eng = Phase55CrossVenueOrderflowExecutionValidator(cfg)
        rep = eng.run_campaign(cycles=int(cycles))
    vs = (rep.get("venue_summaries") or {}).get(venue) or {}
    gates_ok = bool(rep.get("gates_ok"))
    finite_ok = all(
        math.isfinite(float(vs.get(k) or 0.0))
        for k in ("fill_rate_vs_model", "avg_slippage_bps", "avg_latency_ms", "avg_toxicity", "avg_quality_score")
    )
    return serialize_metrics_strict(
        {
            "phase": "55_cross_venue_orderflow_execution_validator",
            "paper_only": True,
            "venue": venue,
            "symbol": symbol,
            "underlying": underlying,
            "cycles": int(rep.get("cycles") or cycles),
            "total_fills": int(rep.get("total_fills") or 0),
            "total_breaches": int(rep.get("total_breaches") or 0),
            "gates_ok": bool(gates_ok and finite_ok),
            "fill_rate_vs_model_ok": bool(rep.get("fill_rate_vs_model_ok")),
            "slippage_tca_reconciliation_ok": bool(rep.get("slippage_tca_reconciliation_ok")),
            "per_venue_latency_scoring_ok": bool(rep.get("per_venue_latency_scoring_ok")),
            "toxicity_adjusted_quality_ok": bool(rep.get("toxicity_adjusted_quality_ok")),
            "venue_gates_ok": bool(rep.get("venue_gates_ok")),
            "avg_quality_score": float(vs.get("avg_quality_score") or 0.0),
            "fill_rate_vs_model": float(vs.get("fill_rate_vs_model") or 0.0),
            "avg_slippage_bps": float(vs.get("avg_slippage_bps") or 0.0),
            "avg_latency_ms": float(vs.get("avg_latency_ms") or 0.0),
            "avg_toxicity": float(vs.get("avg_toxicity") or 0.0),
            "kill_switch_halted": False,
            "slo_ok": bool(gates_ok and finite_ok),
            "seed": int(seed),
            "integration": str(rep.get("integration") or "Phase51+Phase32+Phase52"),
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
                        "deterministic_probe_route_id": f"p55execval:{venue}:{symbol}:{int(seed)+vi*100+si}",
                        "probe_cycle": 0,
                        "probe_gates_ok": bool(rep.get("gates_ok")),
                        "probe_fill_rate_vs_model_ok": bool(rep.get("fill_rate_vs_model_ok")),
                        "probe_slippage_tca_reconciliation_ok": bool(rep.get("slippage_tca_reconciliation_ok")),
                        "probe_per_venue_latency_scoring_ok": bool(rep.get("per_venue_latency_scoring_ok")),
                        "probe_toxicity_adjusted_quality_ok": bool(rep.get("toxicity_adjusted_quality_ok")),
                        "probe_avg_quality_score": float(rep.get("avg_quality_score") or 0.0),
                        "probe_fill_rate_vs_model": float(rep.get("fill_rate_vs_model") or 0.0),
                        "probe_avg_slippage_bps": float(rep.get("avg_slippage_bps") or 0.0),
                        "probe_avg_latency_ms": float(rep.get("avg_latency_ms") or 0.0),
                        "probe_avg_toxicity": float(rep.get("avg_toxicity") or 0.0),
                        "probe_kill_switch_halted": bool(rep.get("kill_switch_halted")),
                        "probe_finite": all(
                            math.isfinite(float(rep.get(k) or 0.0))
                            for k in ("avg_quality_score", "fill_rate_vs_model", "avg_slippage_bps", "avg_latency_ms", "avg_toxicity")
                        ),
                        "campaign_cycles": int(rep.get("cycles") or 0),
                        "campaign_total_fills": int(rep.get("total_fills") or 0),
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
        "fill_rate_finite_0_1": math.isfinite(float(rep.get("fill_rate_vs_model") or 0.0)) and 0.0 <= float(rep.get("fill_rate_vs_model") or 0.0) <= 1.0,
        "slippage_finite_nonneg": math.isfinite(float(rep.get("avg_slippage_bps") or 0.0)) and float(rep.get("avg_slippage_bps") or 0.0) >= 0.0,
        "latency_finite_nonneg": math.isfinite(float(rep.get("avg_latency_ms") or 0.0)) and float(rep.get("avg_latency_ms") or 0.0) >= 0.0,
        "toxicity_finite_0_1": math.isfinite(float(rep.get("avg_toxicity") or 0.0)) and 0.0 <= float(rep.get("avg_toxicity") or 0.0) <= 1.0,
        "quality_finite_0_1": math.isfinite(float(rep.get("avg_quality_score") or 0.0)) and 0.0 <= float(rep.get("avg_quality_score") or 0.0) <= 1.0,
        "campaign_gates_ok": bool(rep.get("gates_ok")),
        "all_reports_paper_only": bool(rep.get("paper_only")),
    }
    return {"report": rep, "deterministic_replay_equal": bool(same), "bounds": bounds, "bounds_ok": all(bool(v) for v in bounds.values())}


def generate(cycles: int = 60, seed: int = 55055) -> Dict[str, Any]:
    checks = _deterministic_checks(seed=seed, cycles=cycles)
    rep = checks["report"]
    coverage = _coverage_rows(seed=seed, cycles=max(1, COVERAGE_CYCLES))
    qual_vals = [float(x["probe_avg_quality_score"]) for x in coverage]
    fill_vals = [float(x["probe_fill_rate_vs_model"]) for x in coverage]
    slip_vals = [float(x["probe_avg_slippage_bps"]) for x in coverage]
    lat_vals = [float(x["probe_avg_latency_ms"]) for x in coverage]
    tox_vals = [float(x["probe_avg_toxicity"]) for x in coverage]
    halted_cycles = sum(1 for x in coverage if bool(x["probe_kill_switch_halted"]))
    gates_all_ok = all(bool(x["probe_gates_ok"]) for x in coverage)
    total_fills = sum(int(x.get("campaign_total_fills") or 0) for x in coverage)
    risk_posture = {
        "paper_only": True,
        "kill_switch_slo_posture": "paper_guarded" if (halted_cycles or not gates_all_ok) else "armed_paper",
        "halted_coverage_rows": int(halted_cycles),
        "all_coverage_gates_ok": bool(gates_all_ok),
        "slo_posture_recorded": bool(rep.get("slo_ok")),
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
                "phase": str(rep.get("phase") or "55_cross_venue_orderflow_execution_validator"),
                "cycles": int(cycles),
                "probe_total_cycles": int(rep.get("cycles") or 0),
                "gates_ok": bool(rep.get("gates_ok")),
                "slo_ok": bool(rep.get("slo_ok")),
                "total_fills": int(total_fills),
                "total_breaches": int(rep.get("total_breaches") or 0),
                "fill_rate_vs_model_ok": bool(rep.get("fill_rate_vs_model_ok")),
                "slippage_tca_reconciliation_ok": bool(rep.get("slippage_tca_reconciliation_ok")),
                "per_venue_latency_scoring_ok": bool(rep.get("per_venue_latency_scoring_ok")),
                "toxicity_adjusted_quality_ok": bool(rep.get("toxicity_adjusted_quality_ok")),
                "integration": str(rep.get("integration") or "Phase51+Phase32+Phase52"),
                "source_seed": int(rep.get("seed") or seed),
            },
            "execution_validation_surface": {
                "paper_only": True,
                "venues": list(VENUES),
                "symbols": list(SYMBOLS),
                "underlyings": list(UNDERLYINGS),
                "deterministic_replay_equal": bool(checks["deterministic_replay_equal"]),
                "bounds_ok": bool(checks["bounds_ok"]),
                "bounds": checks["bounds"],
                "coverage_pairs": len(coverage),
                "avg_quality_score": float(sum(qual_vals) / max(1, len(qual_vals))),
                "avg_fill_rate_vs_model": float(sum(fill_vals) / max(1, len(fill_vals))),
                "avg_slippage_bps": float(sum(slip_vals) / max(1, len(slip_vals))),
                "avg_latency_ms": float(sum(lat_vals) / max(1, len(lat_vals))),
                "avg_toxicity": float(sum(tox_vals) / max(1, len(tox_vals))),
            },
            "venue_symbol_coverage": coverage,
            "execution_stress_summary": {
                "paper_only": True,
                "total_fills": int(total_fills),
                "coverage_rows": len(coverage),
                "avg_quality_score": float(sum(qual_vals) / max(1, len(qual_vals))),
                "min_quality_score": float(min(qual_vals) if qual_vals else 0.0),
                "max_quality_score": float(max(qual_vals) if qual_vals else 0.0),
                "avg_fill_rate_vs_model": float(sum(fill_vals) / max(1, len(fill_vals))),
                "avg_slippage_bps": float(sum(slip_vals) / max(1, len(slip_vals))),
                "avg_latency_ms": float(sum(lat_vals) / max(1, len(lat_vals))),
                "avg_toxicity": float(sum(tox_vals) / max(1, len(tox_vals))),
                "kill_switch_halted_rows": int(halted_cycles),
            },
            "risk_posture": risk_posture,
            "evidence_refs": [
                "scripts/generate_phase55_cross_venue_orderflow_execution_validator_paper_evidence.py",
                "src/execution/phase55_cross_venue_orderflow_execution_validator.py",
                "src/execution/phase51_latency_aware_options_sor.py",
                "src/execution/phase32_execution_quality.py",
                "src/orderflow/phase52_toxicity_resilient_flow_optimizer.py",
                "src/telemetry/serialization.py",
                "research_state/PHASE56_CROSS_VENUE_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T162958Z.json",
                "research_state/PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T161211Z.json",
                "research_state/PHASE53_CROSS_MARGIN_STRESS_PROPAGATION_PAPER_EVIDENCE_20261107T152913Z.json",
                "research_state/PHASE52_REALTIME_LIQUIDITY_ALLOCATOR_PAPER_EVIDENCE_20261107T152449Z.json",
                "research_state/PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE_20261107T142001Z.json",
                "research_state/PHASE50_OPTIONS_RISK_FACTORS_PAPER_EVIDENCE_20261107T152026Z.json",
                "research_state/CONTINUOUS_VALIDATION_20261107T160845Z.json",
                "research_state/PAPER_OPS_SESSION_GATE_20261107T163013Z.json",
            ],
            "cross_refs": [
                "phase55_cross_venue_orderflow_execution_validator.py:Phase55CrossVenueOrderflowExecutionValidator/Phase55ExecutionValidationConfig",
                "PHASE56_CROSS_VENUE_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T162958Z.json",
                "PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T161211Z.json",
                "PHASE53_CROSS_MARGIN_STRESS_PROPAGATION_PAPER_EVIDENCE_20261107T152913Z.json",
                "PHASE52_REALTIME_LIQUIDITY_ALLOCATOR_PAPER_EVIDENCE_20261107T152449Z.json",
                "PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE_20261107T142001Z.json",
                "PHASE50_OPTIONS_RISK_FACTORS_PAPER_EVIDENCE_20261107T152026Z.json",
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
    ap.add_argument("--cycles", type=int, default=60)
    ap.add_argument("--seed", type=int, default=55055)
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
