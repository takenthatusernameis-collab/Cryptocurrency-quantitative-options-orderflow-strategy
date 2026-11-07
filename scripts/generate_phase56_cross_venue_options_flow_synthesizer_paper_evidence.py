#!/usr/bin/env python3
"""Generate phase56 cross-venue options flow synthesizer paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
features/signals → execution/backtest (fees/slippage/risk) → delta-neutral
hedging + directional/hedge PnL attribution → reconciliation/monitoring.
Advisory paper evidence only: never enables live trading, never unblocks NEXT9,
no external venue mutation, no refactor of phase79/80/110.

Uses src.flow.phase56_cross_venue_options_flow_synthesizer (deterministic,
paper-only, hard-gated) to produce cross-venue options flow synthesis surfaces
(fragmentation/toxicity/regime/routing) across the repo-prioritized venue×symbol
scope.

Usage:
  PYTHONPATH=. python3 scripts/generate_phase56_cross_venue_options_flow_synthesizer_paper_evidence.py [--cycles N] [--seed S] [--write]
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

from src.flow.phase56_cross_venue_options_flow_synthesizer import (  # noqa: E402
    Phase56CrossVenueOptionsFlowSynthesizer,
    Phase56FlowSynthConfig,
)
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE56_CROSS_VENUE_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE"
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
        "flow_synthesis_surface",
        "venue_symbol_coverage",
        "flow_stress_summary",
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
    if int(camp.get("total_cycles") or 0) <= 0:
        issues.append("campaign_total_cycles_required")
    if camp.get("gates_ok") is not True:
        issues.append("campaign_gates_ok_required")
    surf = d.get("flow_synthesis_surface") or {}
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
    if not all(
        isinstance(x, dict) and x.get("deterministic_probe_route_id") for x in cov
    ):
        issues.append("coverage_rows_must_have_probe")
    if not all(isinstance(x, dict) and bool(x.get("probe_finite")) for x in cov):
        issues.append("coverage_rows_must_have_finite_probe")
    fs = d.get("flow_stress_summary") or {}
    if fs.get("paper_only") is not True:
        issues.append("flow_stress_paper_only_required")
    if int(fs.get("n_syntheses") or 0) <= 0:
        issues.append("n_syntheses_required")
    if float(fs.get("avg_fragmentation") or -1.0) < 0.0:
        issues.append("avg_fragmentation_invalid")
    rp = d.get("risk_posture") or {}
    if rp.get("kill_switch_slo_posture") not in (
        "armed_paper",
        "observed_paper",
        "paper_guarded",
    ):
        issues.append("risk_posture_invalid")
    if rp.get("paper_only") is not True:
        issues.append("risk_posture_paper_only_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _venue_flows(venue: str, symbol: str, cycle: int, seed: int) -> Dict[str, Dict[str, float]]:
    base = (hash((venue, symbol, cycle, seed)) % 1000) / 1000.0
    tox = (hash((venue, symbol, "tox", cycle, seed)) % 1000) / 2500.0  # 0..0.4
    if symbol == "BTC-USD":
        bid = 100.0 + 40.0 * base
        ask = 95.0 + 35.0 * (1.0 - base)
    else:
        bid = 80.0 + 30.0 * base
        ask = 78.0 + 28.0 * (1.0 - base)
    return {
        venue: {
            "bid_vol": float(bid),
            "ask_vol": float(ask),
            "toxicity": float(min(0.45, max(0.01, tox))),
        }
    }


def _run_scope(seed: int, cycles: int, venue: str, symbol: str) -> Dict[str, Any]:
    """Run deterministic cross-venue synthesis cycles for one venue×symbol probe scope.

    Phase56 synthesizes across its configured venue set; we provide a single-venue
    flow map to probe that venue's contribution while keeping paper-only guards.
    """
    cfg = Phase56FlowSynthConfig(seed=int(seed), paper_only=True, venues=(venue,), max_venues=1)
    eng = Phase56CrossVenueOptionsFlowSynthesizer(cfg)
    rows: List[Dict[str, Any]] = []
    for i in range(max(1, int(cycles))):
        flows = _venue_flows(venue, symbol, i, seed)
        rep = eng.synthesize(venue_flows=flows)
        rows.append(rep)
    avg_frag = sum(float(r.get("avg_fragmentation") or 0.0) for r in rows) / len(rows)
    avg_tox = sum(float(r.get("avg_toxicity") or 0.0) for r in rows) / len(rows)
    regimes = [str(r.get("regime") or "unknown") for r in rows]
    routes = [str(r.get("routing_recommendation") or "unknown") for r in rows]
    gates_ok = all(bool(r.get("paper_only")) and bool(r.get("live_path_hard_gated")) for r in rows)
    finite_ok = all(
        math.isfinite(float(r.get("avg_fragmentation") or 0.0))
        and math.isfinite(float(r.get("avg_toxicity") or 0.0))
        for r in rows
    )
    return serialize_metrics_strict(
        {
            "phase": "56_cross_venue_options_flow_synthesizer",
            "paper_only": True,
            "venue": venue,
            "symbol": symbol,
            "cycles": len(rows),
            "n_syntheses": len(rows),
            "avg_fragmentation": avg_frag,
            "avg_toxicity": avg_tox,
            "regimes": regimes,
            "routes": routes,
            "gates_ok": bool(gates_ok and finite_ok),
            "kill_switch_halted": False,
            "slo_ok": bool(gates_ok and finite_ok),
            "seed": int(seed),
            "sample": rows[0] if rows else {},
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
                        "deterministic_probe_route_id": f"p56route:{venue}:{symbol}:{int(seed)+vi*100+si}",
                        "probe_cycle": 0,
                        "probe_regime": str((rep.get("regimes") or ["unknown"])[0]),
                        "probe_fragmentation": float(rep.get("avg_fragmentation") or 0.0),
                        "probe_toxicity": float(rep.get("avg_toxicity") or 0.0),
                        "probe_routing_recommendation": str((rep.get("routes") or ["unknown"])[0]),
                        "probe_gates_ok": bool(rep.get("gates_ok")),
                        "probe_kill_switch_halted": bool(rep.get("kill_switch_halted")),
                        "probe_finite": math.isfinite(float(rep.get("avg_fragmentation") or 0.0))
                        and math.isfinite(float(rep.get("avg_toxicity") or 0.0)),
                        "campaign_total_cycles": int(rep.get("cycles") or 0),
                        "campaign_n_syntheses": int(rep.get("n_syntheses") or 0),
                        "paper_only": True,
                    }
                )
            )
    return rows


def _deterministic_checks(seed: int, cycles: int) -> Dict[str, Any]:
    rep = _run_scope(seed=seed, cycles=cycles, venue="deribit", symbol="BTC-USD")
    rep2 = _run_scope(seed=seed, cycles=cycles, venue="deribit", symbol="BTC-USD")
    same = _strip_timestamps(rep) == _strip_timestamps(rep2)
    frag = float(rep.get("avg_fragmentation") or 0.0)
    tox = float(rep.get("avg_toxicity") or 0.0)
    bounds = {
        "fragmentation_finite_0_1": math.isfinite(frag) and 0.0 <= frag <= 1.0,
        "toxicity_finite_0_1": math.isfinite(tox) and 0.0 <= tox <= 1.0,
        "campaign_gates_ok": bool(rep.get("gates_ok")),
        "all_reports_paper_only": bool(rep.get("paper_only")),
    }
    return {
        "report": rep,
        "deterministic_replay_equal": bool(same),
        "bounds": bounds,
        "bounds_ok": all(bool(v) for v in bounds.values()),
    }


def generate(cycles: int = 60, seed: int = 56056) -> Dict[str, Any]:
    checks = _deterministic_checks(seed=seed, cycles=cycles)
    rep = checks["report"]
    coverage = _coverage_rows(seed=seed, cycles=max(1, COVERAGE_CYCLES))
    frag_vals = [float(x["probe_fragmentation"]) for x in coverage]
    tox_vals = [float(x["probe_toxicity"]) for x in coverage]
    halted_cycles = sum(1 for x in coverage if bool(x["probe_kill_switch_halted"]))
    gates_all_ok = all(bool(x["probe_gates_ok"]) for x in coverage)
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
                "phase": str(rep.get("phase") or "56_cross_venue_options_flow_synthesizer"),
                "cycles": int(cycles),
                "total_cycles": int(rep.get("cycles") or 0),
                "gates_ok": bool(rep.get("gates_ok")),
                "slo_ok": bool(rep.get("slo_ok")),
                "avg_fragmentation": float(rep.get("avg_fragmentation") or 0.0),
                "avg_toxicity": float(rep.get("avg_toxicity") or 0.0),
                "n_syntheses": int(rep.get("n_syntheses") or 0),
                "kill_switch_halted": bool(rep.get("kill_switch_halted")),
                "source_seed": int(rep.get("seed") or seed),
            },
            "flow_synthesis_surface": {
                "paper_only": True,
                "venues": list(VENUES),
                "symbols": list(SYMBOLS),
                "underlyings": list(UNDERLYINGS),
                "deterministic_replay_equal": bool(checks["deterministic_replay_equal"]),
                "bounds_ok": bool(checks["bounds_ok"]),
                "bounds": checks["bounds"],
                "coverage_pairs": len(coverage),
                "regimes_present_surface": sorted(
                    {
                        str(x.get("probe_routing_recommendation") or "unknown")
                        for x in coverage
                    }
                ),
            },
            "venue_symbol_coverage": coverage,
            "flow_stress_summary": {
                "paper_only": True,
                "n_syntheses": int(rep.get("n_syntheses") or 0),
                "avg_fragmentation": float(sum(frag_vals) / max(1, len(frag_vals))),
                "min_fragmentation": float(min(frag_vals) if frag_vals else 0.0),
                "max_fragmentation": float(max(frag_vals) if frag_vals else 0.0),
                "avg_toxicity": float(sum(tox_vals) / max(1, len(tox_vals))),
                "kill_switch_halted_rows": int(halted_cycles),
                "coverage_rows": len(coverage),
            },
            "risk_posture": risk_posture,
            "evidence_refs": [
                "scripts/generate_phase56_cross_venue_options_flow_synthesizer_paper_evidence.py",
                "src/flow/phase56_cross_venue_options_flow_synthesizer.py",
                "src/telemetry/serialization.py",
                "research_state/PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T161211Z.json",
                "research_state/PHASE53_CROSS_MARGIN_STRESS_PROPAGATION_PAPER_EVIDENCE_20261107T152913Z.json",
                "research_state/PHASE52_REALTIME_LIQUIDITY_ALLOCATOR_PAPER_EVIDENCE_20261107T152449Z.json",
                "research_state/PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE_20261107T142001Z.json",
                "research_state/PHASE50_OPTIONS_RISK_FACTORS_PAPER_EVIDENCE_20261107T152026Z.json",
                "research_state/CONTINUOUS_VALIDATION_20261107T160845Z.json",
                "research_state/PAPER_OPS_SESSION_GATE_20261107T162756Z.json",
            ],
            "cross_refs": [
                "phase56_cross_venue_options_flow_synthesizer.py:Phase56CrossVenueOptionsFlowSynthesizer/Phase56FlowSynthConfig",
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
    ap.add_argument("--seed", type=int, default=56056)
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
