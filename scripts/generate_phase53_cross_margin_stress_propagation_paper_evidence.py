#!/usr/bin/env python3
"""Generate phase53 cross-margin stress propagation paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
execution/backtest (fees/slippage/risk) → delta-neutral hedging + PnL attribution
→ reconciliation/monitoring. Advisory paper evidence only: never enables live
trading, never unblocks NEXT9, no external venue mutation.

Uses src.risk.phase34_cross_margin_engine (deterministic, paper-gated) to produce
cross-margin stress propagation surfaces across venue×symbol scopes.

Usage:
  PYTHONPATH=. python3 scripts/generate_phase53_cross_margin_stress_propagation_paper_evidence.py [--cycles N] [--seed S] [--write]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
sys.path.insert(0, str(REPO))

from src.risk.phase34_cross_margin_engine import CrossMarginConfig34, CrossMarginEngine  # noqa: E402
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE53_CROSS_MARGIN_STRESS_PROPAGATION_PAPER_EVIDENCE"
VENUES = ("deribit", "okx", "binance")
SYMBOLS = ("BTC-USD", "ETH-USD")
UNDERLYINGS = ("BTC", "ETH")
UNDERLYING_BY_SYMBOL = {"BTC-USD": "BTC", "ETH-USD": "ETH"}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _strip_timestamps(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_timestamps(v) for k, v in obj.items()
                if k not in ("timestamp_utc", "timestamp")}
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
    for k in ("timestamp_utc", "seed", "cycles", "venues", "symbols", "underlyings",
              "campaign", "stress_propagation_surface", "venue_symbol_coverage",
              "margin_stress_summary", "risk_posture", "evidence_refs", "cross_refs"):
        if d.get(k) in (None, "", [], {}):
            issues.append(f"missing_{k}")
    camp = d.get("campaign") or {}
    if camp.get("paper_only") is not True:
        issues.append("campaign_paper_only_required")
    if int(camp.get("cycles") or 0) <= 0:
        issues.append("campaign_cycles_required")
    if int(camp.get("total_cycles") or 0) <= 0:
        issues.append("campaign_total_cycles_required")
    surf = d.get("stress_propagation_surface") or {}
    if surf.get("paper_only") is not True:
        issues.append("surface_paper_only_required")
    if set(surf.get("venues") or []) != set(VENUES):
        issues.append("surface_venues_must_match")
    if set(surf.get("symbols") or []) != set(SYMBOLS):
        issues.append("surface_symbols_must_match")
    if not isinstance(surf.get("stress_scenarios"), list) or not surf.get("stress_scenarios"):
        issues.append("surface_stress_scenarios_required")
    cov = d.get("venue_symbol_coverage") or []
    pairs = {(x.get("venue"), x.get("symbol")) for x in cov if isinstance(x, dict)}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    if pairs != expected:
        issues.append("venue_symbol_coverage_must_match")
    if not all(isinstance(x, dict) and x.get("paper_only") is True for x in cov):
        issues.append("coverage_rows_must_be_paper_only")
    if not all(isinstance(x, dict) and x.get("deterministic_probe_result_id") for x in cov):
        issues.append("coverage_rows_must_have_probe")
    if not all(isinstance(x, dict) and bool(x.get("probe_finite")) for x in cov):
        issues.append("coverage_rows_must_have_finite_probe")
    ms = d.get("margin_stress_summary") or {}
    if ms.get("paper_only") is not True:
        issues.append("margin_stress_paper_only_required")
    if float(ms.get("avg_margin_ratio") or 0.0) <= 0.0:
        issues.append("avg_margin_ratio_invalid")
    if float(ms.get("avg_worst_case_loss_usd") or -1.0) < 0.0:
        issues.append("avg_worst_case_loss_invalid")
    if int(ms.get("n_cycle_results") or 0) <= 0:
        issues.append("n_cycle_results_required")
    rp = d.get("risk_posture") or {}
    if rp.get("kill_switch_slo_posture") not in ("armed_paper", "observed_paper", "paper_guarded"):
        issues.append("risk_posture_invalid")
    if rp.get("paper_only") is not True:
        issues.append("risk_posture_paper_only_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _run_scope(seed: int, cycles: int, venue: str, symbol: str) -> Dict[str, Any]:
    underlying = UNDERLYING_BY_SYMBOL[symbol]
    cfg = CrossMarginConfig34(
        seed=int(seed),
        paper_only=True,
        underlyings=(underlying,),
        venues=(venue,),
        cycles=int(cycles),
        stress_scenarios=4,
    )
    eng = CrossMarginEngine(cfg)
    rep = eng.run_campaign(cycles=int(cycles))
    return rep


def _coverage_rows(seed: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for vi, venue in enumerate(VENUES):
        for si, symbol in enumerate(SYMBOLS):
            rep = _run_scope(seed=seed + vi * 100 + si, cycles=4, venue=venue, symbol=symbol)
            results = rep.get("results") or []
            probe = results[0] if results else {}
            rows.append(serialize_metrics_strict({
                "venue": venue,
                "symbol": symbol,
                "underlying": UNDERLYING_BY_SYMBOL[symbol],
                "deterministic_probe_result_id": f"probe:{venue}:{symbol}:{int(seed)+vi*100+si}",
                "probe_cycle": int(probe.get("cycle") or 0),
                "probe_margin_ratio": float(probe.get("margin_ratio") or 0.0),
                "probe_worst_case_loss_usd": float(probe.get("worst_case_loss_usd") or 0.0),
                "probe_margin_call": bool(probe.get("margin_call")),
                "probe_finite": math.isfinite(float(probe.get("margin_ratio") or 0.0))
                and math.isfinite(float(probe.get("worst_case_loss_usd") or 0.0)),
                "campaign_total_cycles": int(rep.get("total_cycles") or 0),
                "campaign_any_margin_call": bool(rep.get("any_margin_call")),
                "paper_only": True,
            }))
    return rows


def _deterministic_checks(seed: int, cycles: int) -> Dict[str, Any]:
    rep = _run_scope(seed=seed, cycles=cycles, venue="deribit", symbol="BTC-USD")
    rep2 = _run_scope(seed=seed, cycles=cycles, venue="deribit", symbol="BTC-USD")
    same = _strip_timestamps(rep) == _strip_timestamps(rep2)
    results = rep.get("results") or []
    scenarios = []
    if results and results[0].get("stress_losses"):
        scenarios = [s.get("name") for s in (results[0].get("stress_losses") or []) if isinstance(s, dict)]
    all_ratios = [float(r.get("margin_ratio") or 0.0) for r in results]
    all_losses = [float(r.get("worst_case_loss_usd") or 0.0) for r in results]
    bounds = {
        "all_margin_ratios_finite_positive": all(math.isfinite(v) and v > 0.0 for v in all_ratios),
        "all_worst_case_losses_non_negative_finite": all(math.isfinite(v) and v >= 0.0 for v in all_losses),
        "all_results_paper_only": all(bool(r.get("paper_only")) for r in results),
        "stress_scenarios_present": bool(scenarios),
        "stress_loss_components_finite": all(
            math.isfinite(float(s.get("total_loss_usd") or 0.0))
            and math.isfinite(float(s.get("delta_loss_usd") or 0.0))
            and math.isfinite(float(s.get("gamma_loss_usd") or 0.0))
            and math.isfinite(float(s.get("vega_loss_usd") or 0.0))
            for r in results for s in (r.get("stress_losses") or []) if isinstance(s, dict)
        ),
    }
    return {
        "report": rep,
        "deterministic_replay_equal": bool(same),
        "stress_scenarios": scenarios,
        "bounds": bounds,
        "bounds_ok": all(bool(v) for v in bounds.values()),
    }


def generate(cycles: int = 12, seed: int = 53053) -> Dict[str, Any]:
    checks = _deterministic_checks(seed=seed, cycles=cycles)
    rep = checks["report"]
    results = rep.get("results") or []
    coverage = _coverage_rows(seed=seed)
    all_losses = [float(r.get("worst_case_loss_usd") or 0.0) for r in results]
    all_ratios = [float(r.get("margin_ratio") or 0.0) for r in results]
    all_im = [float(r.get("initial_margin_usd") or 0.0) for r in results]
    all_mm = [float(r.get("maintenance_margin_usd") or 0.0) for r in results]
    all_cm = [float(r.get("cross_margin_required_usd") or 0.0) for r in results]
    margin_calls = sum(1 for r in results if bool(r.get("margin_call")))
    liq_risks = sum(1 for r in results if bool(r.get("liquidation_risk")))
    # propagation: count venues/symbols where worst-case loss exceeds available margin in probe
    propagation_hits = sum(
        1 for x in coverage
        if float(x.get("probe_worst_case_loss_usd") or 0.0) > 0.0 and bool(x.get("probe_margin_call"))
    )
    risk_posture = {
        "paper_only": True,
        "kill_switch_slo_posture": "paper_guarded" if (margin_calls or liq_risks or propagation_hits) else "armed_paper",
        "margin_calls_observed": int(margin_calls),
        "liquidation_risks_observed": int(liq_risks),
        "propagation_hits_observed": int(propagation_hits),
        "any_margin_call": bool(rep.get("any_margin_call")),
        "no_external_venue_mutation": True,
        "next9_unblocked": False,
        "live_trading_enabled": False,
    }
    artifact = serialize_metrics_strict({
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
            "phase": str(rep.get("phase") or "34_cross_margin"),
            "cycles": int(cycles),
            "total_cycles": int(rep.get("total_cycles") or 0),
            "final_margin_ratio": float(rep.get("final_margin_ratio") or 0.0),
            "any_margin_call": bool(rep.get("any_margin_call")),
            "source_seed": int(rep.get("seed") or seed),
        },
        "stress_propagation_surface": {
            "paper_only": True,
            "venues": list(VENUES),
            "symbols": list(SYMBOLS),
            "underlyings": list(UNDERLYINGS),
            "stress_scenarios": list(checks.get("stress_scenarios") or []),
            "deterministic_replay_equal": bool(checks["deterministic_replay_equal"]),
            "bounds_ok": bool(checks["bounds_ok"]),
            "bounds": checks["bounds"],
            "propagation_probe_hits": int(propagation_hits),
        },
        "venue_symbol_coverage": coverage,
        "margin_stress_summary": {
            "paper_only": True,
            "n_cycle_results": len(results),
            "avg_margin_ratio": float(sum(all_ratios) / max(1, len(all_ratios))),
            "min_margin_ratio": float(min(all_ratios) if all_ratios else 0.0),
            "avg_worst_case_loss_usd": float(sum(all_losses) / max(1, len(all_losses))),
            "max_worst_case_loss_usd": float(max(all_losses) if all_losses else 0.0),
            "avg_initial_margin_usd": float(sum(all_im) / max(1, len(all_im))),
            "avg_maintenance_margin_usd": float(sum(all_mm) / max(1, len(all_mm))),
            "avg_cross_margin_required_usd": float(sum(all_cm) / max(1, len(all_cm))),
            "margin_calls": int(margin_calls),
            "liquidation_risks": int(liq_risks),
        },
        "risk_posture": risk_posture,
        "evidence_refs": [
            "scripts/generate_phase53_cross_margin_stress_propagation_paper_evidence.py",
            "src/risk/phase34_cross_margin_engine.py",
            "src/reconciliation/phase40_position_margin_audit.py",
            "research_state/PHASE52_REALTIME_LIQUIDITY_ALLOCATOR_PAPER_EVIDENCE_20261107T152449Z.json",
            "research_state/CONTINUOUS_VALIDATION_20261107T140506Z.json",
            "research_state/PAPER_OPS_SESSION_GATE_20261107T152647Z.json",
        ],
        "cross_refs": [
            "phase34_cross_margin_engine.py:CrossMarginEngine/CrossMarginConfig34",
            "phase40_position_margin_audit.py:Phase40PositionMarginAudit",
            "PHASE50_OPTIONS_RISK_FACTORS_PAPER_EVIDENCE_20261107T152026Z.json",
            "PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE_20261107T142001Z.json",
        ],
        "determinism": {
            "deterministic_seeded": True,
            "same_seed_cycles_reproduce_surface": bool(checks["deterministic_replay_equal"]),
            "bounds_ok": bool(checks["bounds_ok"]),
            "bounds": checks["bounds"],
        },
    })
    ok, issues = validate_artifact(artifact)
    artifact["validation"] = {"valid": bool(ok), "issues": issues}
    return artifact


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=12)
    ap.add_argument("--seed", type=int, default=53053)
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
    payload = serialize_metrics_strict({
        "artifact_path": str(out_path) if args.write else None,
        "valid": v["valid"],
        "issues": v["issues"],
        "paper_only": d["paper_only"],
        "live_trading_enabled": d["live_trading_enabled"],
        "next9_unblocked": d["next9_unblocked"],
        "deterministic": d["determinism"]["same_seed_cycles_reproduce_surface"],
    })
    print(json.dumps(payload, indent=2))
    if not v["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
