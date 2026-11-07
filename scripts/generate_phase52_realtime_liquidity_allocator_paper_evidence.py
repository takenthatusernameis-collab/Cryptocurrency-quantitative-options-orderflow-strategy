#!/usr/bin/env python3
"""Generate phase52 realtime liquidity allocator paper evidence (additive, paper-only).

P1 alternate (blocker: no importable `src/**/phase50*options*risk*factor*` module found;
phase50 sources present are toxicity-aware options MM and cross-venue RV executor).
Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
execution/backtest (fees/slippage/risk) → delta-neutral hedging + PnL attribution
→ reconciliation/monitoring. Advisory paper evidence only: never enables live
trading, never unblocks NEXT9, no external venue mutation.

Usage:
  PYTHONPATH=. python3 scripts/generate_phase52_realtime_liquidity_allocator_paper_evidence.py [--cycles N] [--seed S] [--write]
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

from src.execution.phase52_realtime_liquidity_allocator import (  # noqa: E402
    Phase52AllocatorConfig,
    Phase52RealtimeLiquidityAllocator,
)
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE52_REALTIME_LIQUIDITY_ALLOCATOR_PAPER_EVIDENCE"
VENUES = ("deribit", "okx", "binance")
UNDERLYINGS = ("BTC", "ETH")
SYMBOLS = ("BTC-USD", "ETH-USD")
SYMBOL_BY_UNDERLYING = {"BTC": "BTC-USD", "ETH": "ETH-USD"}
TENORS = ("1D", "7D", "30D")
STRIKES = ("ATM", "25D")
P1_BLOCKER = (
    "P1 primary (Phase50 options risk-factors paper evidence) blocked: no importable "
    "src/**/phase50*options*risk*factor* module located. Present phase50 sources are "
    "src/marketmaking/phase50_toxicity_aware_options_mm.py and "
    "src/execution/phase50_cross_venue_relative_value_executor.py (neither is a "
    "Greeks/risk-factor decomposition module). Alternate heavy evidence delivered for "
    "phase52 realtime liquidity allocation (paper-only)."
)


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
              "campaign", "allocation_surface", "venue_symbol_coverage", "slicing_tca_summary",
              "risk_posture", "evidence_refs", "cross_refs", "p1_blocker"):
        if d.get(k) in (None, "", [], {}):
            issues.append(f"missing_{k}")
    camp = d.get("campaign") or {}
    if camp.get("paper_only") is not True:
        issues.append("campaign_paper_only_required")
    if camp.get("gates_ok") is not True:
        issues.append("campaign_gates_ok_required")
    if int(camp.get("cycles") or 0) <= 0:
        issues.append("campaign_cycles_required")
    if int(camp.get("n_allocations") or 0) <= 0:
        issues.append("campaign_n_allocations_required")
    surf = d.get("allocation_surface") or {}
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
    if not all(isinstance(x, dict) and x.get("deterministic_probe_alloc_id") for x in cov):
        issues.append("coverage_rows_must_have_probe_alloc")
    if not all(isinstance(x, dict) and bool(x.get("probe_alloc_finite")) for x in cov):
        issues.append("coverage_rows_must_have_finite_probe")
    tca = d.get("slicing_tca_summary") or {}
    if tca.get("paper_only") is not True:
        issues.append("tca_paper_only_required")
    if int(tca.get("n_slices") or 0) <= 0:
        issues.append("tca_n_slices_required")
    if int(tca.get("n_tca") or 0) <= 0:
        issues.append("tca_n_tca_required")
    if float(tca.get("avg_est_slippage_bps") or -1.0) < 0.0:
        issues.append("tca_slippage_invalid")
    rp = d.get("risk_posture") or {}
    if rp.get("kill_switch_slo_posture") not in ("armed_paper", "observed_paper", "paper_guarded"):
        issues.append("risk_posture_invalid")
    if rp.get("paper_only") is not True:
        issues.append("risk_posture_paper_only_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _coverage_from_allocations(allocs: List[Dict[str, Any]], seed: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for vi, venue in enumerate(VENUES):
        for ui, underlying in enumerate(UNDERLYINGS):
            symbol = SYMBOL_BY_UNDERLYING[underlying]
            cfg = Phase52AllocatorConfig(
                seed=int(seed) + vi * 10 + ui, paper_only=True,
                venues=(venue,), underlyings=(underlying,), tenors=TENORS, strikes=STRIKES, cycles=8,
            )
            eng = Phase52RealtimeLiquidityAllocator(cfg)
            rep = eng.allocate(cycles=8)
            probe_allocs = list(eng.allocations)
            probe = probe_allocs[0] if probe_allocs else {}
            picked = [a for a in allocs if a.get("venue") == venue and a.get("underlying") == underlying]
            rows.append(serialize_metrics_strict({
                "venue": venue,
                "underlying": underlying,
                "symbol": symbol,
                "deterministic_probe_alloc_id": probe.get("alloc_id"),
                "probe_alloc_usd": float(probe.get("alloc_usd") or 0.0),
                "probe_frag_penalty": float(probe.get("frag_penalty") or 0.0),
                "probe_tox_adj_factor": float(probe.get("tox_adj_factor") or 0.0),
                "probe_alloc_finite": math.isfinite(float(probe.get("alloc_usd") or 0.0)),
                "probe_gates_ok": bool(rep.get("gates_ok")),
                "probe_n_allocations": int(rep.get("n_allocations") or 0),
                "probe_total_alloc_usd": float(rep.get("total_alloc_usd") or 0.0),
                "campaign_n_allocations": len(picked),
                "campaign_total_alloc_usd": float(sum(float(a.get("alloc_usd") or 0.0) for a in picked)),
                "paper_only": True,
            }))
    return rows


def _deterministic_checks(seed: int, cycles: int) -> Dict[str, Any]:
    cfg = Phase52AllocatorConfig(seed=int(seed), paper_only=True, venues=VENUES, underlyings=UNDERLYINGS, tenors=TENORS, strikes=STRIKES, cycles=int(cycles))
    eng = Phase52RealtimeLiquidityAllocator(cfg)
    rep = eng.allocate(cycles=int(cycles))
    allocs = list(eng.allocations)
    slices = list(eng.slices)
    tcas = list(eng.tca)
    cfg2 = Phase52AllocatorConfig(seed=int(seed), paper_only=True, venues=VENUES, underlyings=UNDERLYINGS, tenors=TENORS, strikes=STRIKES, cycles=int(cycles))
    eng2 = Phase52RealtimeLiquidityAllocator(cfg2)
    rep2 = eng2.allocate(cycles=int(cycles))
    same = _strip_timestamps(rep) == _strip_timestamps(rep2)
    bounds = {
        "all_alloc_non_negative": all(float(a.get("alloc_usd") or 0.0) >= 0.0 for a in allocs),
        "all_alloc_within_max": all(float(a.get("alloc_usd") or 0.0) <= float(cfg.max_alloc_usd) + 1e-9 for a in allocs),
        "all_frag_bounded": all(0.0 <= float(a.get("frag_penalty") or 0.0) <= float(cfg.frag_penalty_max) + 1e-9 for a in allocs),
        "all_tox_adj_bounded": all(0.0 <= float(a.get("tox_adj_factor") or 0.0) <= 1.0 + 1e-9 for a in allocs),
        "all_slices_positive": all(float(s.get("slice_usd") or 0.0) >= 0.0 for s in slices),
        "all_tca_slippage_non_negative": all(float(t.get("est_slippage_bps") or 0.0) >= 0.0 for t in tcas),
        "all_venues_in_scope": all(a.get("venue") in VENUES for a in allocs),
        "all_underlyings_in_scope": all(a.get("underlying") in UNDERLYINGS for a in allocs),
    }
    return {
        "report": rep, "allocations": allocs, "slices": slices, "tcas": tcas,
        "deterministic_replay_equal": bool(same),
        "bounds": bounds, "bounds_ok": all(bool(v) for v in bounds.values()),
    }


def generate(cycles: int = 60, seed: int = 52052) -> Dict[str, Any]:
    checks = _deterministic_checks(seed=seed, cycles=cycles)
    rep = checks["report"]
    allocs = checks["allocations"]
    slices = checks["slices"]
    tcas = checks["tcas"]
    coverage = _coverage_from_allocations(allocs, seed=seed)
    risk_posture = {
        "paper_only": True,
        "kill_switch_slo_posture": "armed_paper" if bool(rep.get("gates_ok")) and not bool(rep.get("halted_by_kill_switch")) else "paper_guarded",
        "gates_ok": bool(rep.get("gates_ok")),
        "halted_by_kill_switch": bool(rep.get("halted_by_kill_switch")),
        "avg_toxicity": float(rep.get("avg_toxicity") or 0.0),
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
        "p1_blocker": P1_BLOCKER,
        "campaign": {
            "paper_only": True,
            "cycles": int(rep.get("cycles") or cycles),
            "gates_ok": bool(rep.get("gates_ok")),
            "n_allocations": int(rep.get("n_allocations") or 0),
            "n_slices": int(rep.get("n_slices") or 0),
            "n_tca": int(rep.get("n_tca") or 0),
            "total_alloc_usd": float(rep.get("total_alloc_usd") or 0.0),
            "avg_toxicity": float(rep.get("avg_toxicity") or 0.0),
            "halted_by_kill_switch": bool(rep.get("halted_by_kill_switch")),
        },
        "allocation_surface": {
            "phase": "PHASE52_REALTIME_LIQUIDITY_ALLOCATOR",
            "paper_only": True,
            "seed": int(seed),
            "venues": list(VENUES),
            "underlyings": list(UNDERLYINGS),
            "tenors": list(TENORS),
            "strikes": list(STRIKES),
            "gates_ok": bool(rep.get("gates_ok")),
            "n_allocations": int(rep.get("n_allocations") or 0),
            "total_alloc_usd": float(rep.get("total_alloc_usd") or 0.0),
            "max_alloc_usd": float(Phase52AllocatorConfig().max_alloc_usd),
        },
        "venue_symbol_coverage": coverage,
        "slicing_tca_summary": {
            "paper_only": True,
            "n_slices": len(slices),
            "n_tca": len(tcas),
            "avg_slice_usd": (sum(float(s.get("slice_usd") or 0.0) for s in slices) / max(len(slices), 1)),
            "avg_est_slippage_bps": (sum(float(t.get("est_slippage_bps") or 0.0) for t in tcas) / max(len(tcas), 1)),
            "max_est_slippage_bps": max((float(t.get("est_slippage_bps") or 0.0) for t in tcas), default=0.0),
            "slice_alloc_linked": all(any(s.get("alloc_id") == a.get("alloc_id") for a in allocs) for s in slices),
        },
        "determinism": {
            "deterministic_seeded": True,
            "same_seed_cycles_reproduce_surface": bool(checks["deterministic_replay_equal"]),
            "bounds_ok": bool(checks["bounds_ok"]),
            "bounds": checks["bounds"],
        },
        "risk_posture": risk_posture,
        "evidence_refs": [
            "src/execution/phase52_realtime_liquidity_allocator.py",
            "scripts/generate_phase52_realtime_liquidity_allocator_paper_evidence.py",
            "tests/test_generate_phase52_realtime_liquidity_allocator_paper_evidence.py",
        ],
        "cross_refs": [
            "src/marketmaking/phase50_toxicity_aware_options_mm.py",
            "src/execution/phase50_cross_venue_relative_value_executor.py",
            "research_state/PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE_20261107T142001Z.json",
            "research_state/PHASE46_EXECUTION_PAPER_EVIDENCE_20261107T132047Z.json",
            "research_state/CONTINUOUS_VALIDATION_20261107T140506Z.json",
            "research_state/PAPER_OPS_SESSION_GATE_20261107T142904Z.json",
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
    ap.add_argument("--seed", type=int, default=52052)
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
        "p1_blocker_documented": bool(artifact.get("p1_blocker")),
        "artifact_path": str(path) if path else None,
    }, indent=2))
    return 0 if artifact["validation"]["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
