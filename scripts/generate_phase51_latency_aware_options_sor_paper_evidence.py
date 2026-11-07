#!/usr/bin/env python3
"""Generate phase51 latency-aware options SOR paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
execution/backtest (fees/slippage/risk) → delta-neutral hedging + PnL attribution
→ reconciliation/monitoring. Advisory paper evidence only: never enables live
trading, never unblocks NEXT9, no external venue mutation.

Usage:
  PYTHONPATH=. python3 scripts/generate_phase51_latency_aware_options_sor_paper_evidence.py [--cycles N] [--seed S] [--write]
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

from src.execution.phase51_latency_aware_options_sor import (  # noqa: E402
    Phase51LatencyAwareOptionsSOR,
    Phase51SORConfig,
)
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE"
VENUES = ("deribit", "okx", "binance")
UNDERLYINGS = ("BTC", "ETH")
SYMBOLS = ("BTC-USD", "ETH-USD")
SYMBOL_BY_UNDERLYING = {"BTC": "BTC-USD", "ETH": "ETH-USD"}
EXPIRIES = ("7D", "30D")


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
              "campaign", "routing_surface", "venue_symbol_coverage", "tca_summary",
              "risk_posture", "evidence_refs", "cross_refs"):
        if d.get(k) in (None, "", [], {}):
            issues.append(f"missing_{k}")
    camp = d.get("campaign") or {}
    if camp.get("paper_only") is not True:
        issues.append("campaign_paper_only_required")
    if camp.get("gates_ok") is not True:
        issues.append("campaign_gates_ok_required")
    if int(camp.get("total_cycles") or 0) <= 0:
        issues.append("campaign_total_cycles_required")
    surf = d.get("routing_surface") or {}
    if set(surf.get("venues") or []) != set(VENUES):
        issues.append("surface_venues_must_match")
    if set(surf.get("underlyings") or []) != set(UNDERLYINGS):
        issues.append("surface_underlyings_must_match")
    if surf.get("paper_only") is not True:
        issues.append("surface_paper_only_required")
    if surf.get("gates_ok") is not True:
        issues.append("surface_gates_ok_required")
    cov = d.get("venue_symbol_coverage") or []
    pairs = {(x.get("venue"), x.get("symbol")) for x in cov if isinstance(x, dict)}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    if pairs != expected:
        issues.append("venue_symbol_coverage_must_match")
    if not all(isinstance(x, dict) and x.get("paper_only") is True for x in cov):
        issues.append("coverage_rows_must_be_paper_only")
    if not all(isinstance(x, dict) and x.get("deterministic_probe_route_id") for x in cov):
        issues.append("coverage_rows_must_have_probe_route")
    if not all(isinstance(x, dict) and bool(x.get("probe_score_finite")) for x in cov):
        issues.append("coverage_rows_must_have_finite_probe_score")
    tca = d.get("tca_summary") or {}
    if tca.get("paper_only") is not True:
        issues.append("tca_paper_only_required")
    if int(tca.get("n_tcas") or 0) <= 0:
        issues.append("tca_count_required")
    if float(tca.get("avg_slippage_bps") or -1.0) < 0.0:
        issues.append("tca_slippage_invalid")
    if float(tca.get("avg_toxicity_penalty_bps") or -1.0) < 0.0:
        issues.append("tca_toxicity_invalid")
    rp = d.get("risk_posture") or {}
    if rp.get("kill_switch_slo_posture") not in ("armed_paper", "observed_paper", "paper_guarded"):
        issues.append("risk_posture_invalid")
    if rp.get("paper_only") is not True:
        issues.append("risk_posture_paper_only_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _coverage_from_routes(routes: List[Dict[str, Any]], seed: int) -> List[Dict[str, Any]]:
    """Per venue×symbol deterministic routing checks (not dependent on campaign picks)."""
    rows: List[Dict[str, Any]] = []
    for vi, venue in enumerate(VENUES):
        for ui, underlying in enumerate(UNDERLYINGS):
            symbol = SYMBOL_BY_UNDERLYING[underlying]
            # Deterministic per-pair probe: seed+indices ensures stable finite evidence.
            cfg = Phase51SORConfig(seed=int(seed) + vi * 10 + ui, paper_only=True, venues=(venue,), underlyings=(underlying,), expiries=EXPIRIES)
            sor = Phase51LatencyAwareOptionsSOR(cfg)
            strike = 90000.0 if underlying == "BTC" else 3500.0
            d = sor.route_order(underlying, "7D", strike, "call", "buy", 25000.0, 0.4, vi * 10 + ui, toxicity=0.25)
            dd = d.to_dict()
            # also report campaign picks for transparency
            picked = [r for r in routes if r.get("venue") == venue and r.get("underlying") == underlying]
            rows.append(serialize_metrics_strict({
                "venue": venue,
                "underlying": underlying,
                "symbol": symbol,
                "deterministic_probe_route_id": dd.get("route_id"),
                "probe_latency_ms": float(dd.get("latency_ms") or 0.0),
                "probe_slippage_bps": float(dd.get("slippage_bps") or 0.0),
                "probe_toxicity_penalty_bps": float(dd.get("toxicity_penalty_bps") or 0.0),
                "probe_fill_probability": float(dd.get("fill_probability") or 0.0),
                "probe_expected_cost_bps": float(dd.get("expected_cost_bps") or 0.0),
                "probe_score_finite": math.isfinite(float(dd.get("score") or 0.0)),
                "campaign_n_routes": len(picked),
                "paper_only": True,
            }))
    return rows


def _deterministic_routing_checks(seed: int, cycles: int) -> Dict[str, Any]:
    cfg = Phase51SORConfig(seed=int(seed), paper_only=True, venues=VENUES, underlyings=UNDERLYINGS, expiries=EXPIRIES)
    sor = Phase51LatencyAwareOptionsSOR(cfg)
    rep = sor.run_campaign(cycles=int(cycles))
    cfg2 = Phase51SORConfig(seed=int(seed), paper_only=True, venues=VENUES, underlyings=UNDERLYINGS, expiries=EXPIRIES)
    sor2 = Phase51LatencyAwareOptionsSOR(cfg2)
    rep2 = sor2.run_campaign(cycles=int(cycles))
    same = _strip_timestamps(rep) == _strip_timestamps(rep2)
    routes = list(rep.get("routes") or [])
    tcas = list(rep.get("tcas") or [])
    bounds = {
        "all_latency_non_negative": all(float(r.get("latency_ms") or 0.0) >= 0.0 for r in routes),
        "all_slippage_non_negative": all(float(r.get("slippage_bps") or 0.0) >= 0.0 for r in routes),
        "all_toxicity_penalty_non_negative": all(float(r.get("toxicity_penalty_bps") or 0.0) >= 0.0 for r in routes),
        "all_expected_cost_non_negative": all(float(r.get("expected_cost_bps") or 0.0) >= 0.0 for r in routes),
        "all_fill_probability_bounded": all(0.0 <= float(r.get("fill_probability") or 0.0) <= 1.0 for r in routes),
        "all_venues_in_scope": all(r.get("venue") in VENUES for r in routes),
        "all_underlyings_in_scope": all(r.get("underlying") in UNDERLYINGS for r in routes),
        "tca_route_ids_linked": all(any(t.get("route_id") == r.get("route_id") for r in routes) for t in tcas),
    }
    return {
        "campaign": rep,
        "deterministic_replay_equal": bool(same),
        "bounds": bounds,
        "bounds_ok": all(bool(v) for v in bounds.values()),
    }


def generate(cycles: int = 60, seed: int = 51052) -> Dict[str, Any]:
    checks = _deterministic_routing_checks(seed=seed, cycles=cycles)
    rep = checks["campaign"]
    routes = list(rep.get("routes") or [])
    tcas = list(rep.get("tcas") or [])
    coverage = _coverage_from_routes(routes, seed=seed)
    risk_posture = {
        "paper_only": True,
        "kill_switch_slo_posture": "armed_paper" if bool(rep.get("gates_ok")) else "paper_guarded",
        "gates_ok": bool(rep.get("gates_ok")),
        "halted_routes": int(rep.get("halted_routes") or 0),
        "last_halt": rep.get("last_halt"),
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
            "total_cycles": int(rep.get("cycles") or cycles),
            "gates_ok": bool(rep.get("gates_ok")),
            "n_routes": int(rep.get("n_routes") or 0),
            "n_sliced": int(rep.get("n_sliced") or 0),
            "venue_picks": rep.get("venue_picks") or {},
            "halted_routes": int(rep.get("halted_routes") or 0),
        },
        "routing_surface": {
            "phase": "PHASE51_LATENCY_AWARE_OPTIONS_SOR",
            "paper_only": True,
            "seed": int(seed),
            "venues": list(VENUES),
            "underlyings": list(UNDERLYINGS),
            "expiries": list(EXPIRIES),
            "gates_ok": bool(rep.get("gates_ok")),
            "avg_latency_ms": float(rep.get("avg_latency_ms") or 0.0),
            "avg_fill_probability": float(rep.get("avg_fill_probability") or 0.0),
            "avg_toxicity_penalty_bps": float(rep.get("avg_toxicity_penalty_bps") or 0.0),
            "avg_slippage_bps": float(rep.get("avg_slippage_bps") or 0.0),
            "avg_expected_cost_bps": float(rep.get("avg_expected_cost_bps") or 0.0),
            "avg_score": float(rep.get("avg_score") or 0.0),
        },
        "venue_symbol_coverage": coverage,
        "tca_summary": {
            "paper_only": True,
            "n_tcas": len(tcas),
            "avg_slippage_bps": (sum(float(t.get("slippage_bps") or 0.0) for t in tcas) / max(len(tcas), 1)),
            "avg_latency_ms": (sum(float(t.get("latency_ms") or 0.0) for t in tcas) / max(len(tcas), 1)),
            "avg_implementation_shortfall_bps": (sum(float(t.get("implementation_shortfall_bps") or 0.0) for t in tcas) / max(len(tcas), 1)),
            "avg_toxicity_penalty_bps": float(rep.get("avg_toxicity_penalty_bps") or 0.0),
            "route_tca_linked": all(any(t.get("route_id") == r.get("route_id") for r in routes) for t in tcas),
        },
        "determinism": {
            "deterministic_seeded": True,
            "same_seed_cycles_reproduce_surface": bool(checks["deterministic_replay_equal"]),
            "bounds_ok": bool(checks["bounds_ok"]),
            "bounds": checks["bounds"],
        },
        "risk_posture": risk_posture,
        "evidence_refs": [
            "src/execution/phase51_latency_aware_options_sor.py",
            "scripts/generate_phase51_latency_aware_options_sor_paper_evidence.py",
            "tests/test_generate_phase51_latency_aware_options_sor_paper_evidence.py",
        ],
        "cross_refs": [
            "research_state/PHASE51_ROUTING_REPORT.json",
            "research_state/PHASE51_TCA_REPORT.json",
            "research_state/PHASE51_CAMPAIGN_SUMMARY.json",
            "research_state/PHASE37_CROSS_VENUE_ROUTING_REPORT.json",
            "research_state/PHASE46_EXECUTION_PAPER_EVIDENCE_20261107T132047Z.json",
            "research_state/CONTINUOUS_VALIDATION_20261107T140506Z.json",
            "research_state/PAPER_OPS_SESSION_GATE_20261107T141305Z.json",
        ],
    })
    valid, issues = validate_artifact(artifact)
    artifact["validation"] = {"valid": bool(valid), "issues": issues}
    return artifact


def write_artifact(artifact: Dict[str, Any]) -> Path:
    RS.mkdir(parents=True, exist_ok=True)
    ts = _utc()
    path = RS / f"{ARTIFACT_TYPE}_{ts}.json"
    path.write_text(json.dumps(artifact, indent=2, allow_nan=False) + "\n")
    return path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycles", type=int, default=60)
    ap.add_argument("--seed", type=int, default=51052)
    ap.add_argument("--write", dest="write", action="store_true", default=True)
    ap.add_argument("--no-write", dest="write", action="store_false")
    args = ap.parse_args()
    artifact = generate(cycles=args.cycles, seed=args.seed)
    path = write_artifact(artifact) if args.write else None
    print(json.dumps({
        "valid": artifact["validation"]["valid"],
        "issues": artifact["validation"]["issues"],
        "paper_only": artifact["paper_only"],
        "live_trading_enabled": artifact["live_trading_enabled"],
        "next9_unblocked": artifact["next9_unblocked"],
        "advisory": artifact["advisory"],
        "no_external_venue_mutation": artifact["no_external_venue_mutation"],
        "deterministic": artifact["determinism"]["same_seed_cycles_reproduce_surface"],
        "gates_ok": artifact["campaign"]["gates_ok"],
        "venues": artifact["venues"],
        "symbols": artifact["symbols"],
        "artifact_path": str(path) if path else None,
    }, indent=2))
    return 0 if artifact["validation"]["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
