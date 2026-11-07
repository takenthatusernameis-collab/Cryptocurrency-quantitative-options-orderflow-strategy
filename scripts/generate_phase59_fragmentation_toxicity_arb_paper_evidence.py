#!/usr/bin/env python3
"""Generate phase59 fragmentation+toxicity arb engine paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
features/signals → execution/backtest (fees/slippage/risk) → delta-neutral
hedging + directional/hedge PnL attribution → reconciliation/monitoring.
Advisory paper evidence only: never enables live trading, never unblocks NEXT9,
no external venue mutation, no refactor of phase79/80/110.

Uses src.liquidity.phase59_fragmentation_toxicity_arb_engine
(deterministic, paper-only, hard-gated) to produce fragmentation+toxicity
arbitrage surfaces (basis detection, toxicity/adverse-selection filters,
venue quarantine logic, hard notional limits, kill-switch/SLO posture)
across the repo-prioritized venue×symbol scope.

Usage:
  PYTHONPATH=. /usr/share/miniconda/bin/python scripts/generate_phase59_fragmentation_toxicity_arb_paper_evidence.py [--cycles N] [--seed S] [--write]
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

from src.liquidity.phase59_fragmentation_toxicity_arb_engine import (  # noqa: E402
    Phase59FragmentationToxicityArbConfig,
    Phase59FragmentationToxicityArbEngine,
)
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE59_FRAGMENTATION_TOXICITY_ARB_PAPER_EVIDENCE"
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
        "fragmentation_toxicity_arb_surface",
        "venue_symbol_coverage",
        "arb_stress_summary",
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
    surf = d.get("fragmentation_toxicity_arb_surface") or {}
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
    rp = d.get("risk_posture") or {}
    if rp.get("kill_switch_slo_posture") not in ("armed_paper", "observed_paper", "paper_guarded"):
        issues.append("risk_posture_invalid")
    if rp.get("paper_only") is not True:
        issues.append("risk_posture_paper_only_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _run_scope(seed: int, cycles: int, venue: str, symbol: str) -> Dict[str, Any]:
    """Run deterministic phase59 arb probe for one repo-priority venue×symbol scope.

    Phase59 selects venue pairs from configured venues; we keep a pair that
    includes the probed venue (deterministic) while remaining paper-only and
    finite. No external venue mutation.
    """
    underlying = UNDERLYING_BY_SYMBOL[symbol]
    peer = "okx" if venue == "deribit" else "deribit"
    venues = (venue, peer) if venue != peer else (venue, "okx")
    cfg = Phase59FragmentationToxicityArbConfig(
        seed=int(seed),
        paper_only=True,
        underlyings=(underlying,),
        venues=venues,
        cycles=int(cycles),
    )
    eng = Phase59FragmentationToxicityArbEngine(cfg)
    rep = eng.run_arb(cycles=int(cycles))
    finite_ok = all(
        math.isfinite(float(rep.get(k) or 0.0))
        for k in ("avg_edge_bps", "avg_toxicity")
    ) and math.isfinite(float(rep.get("n_opportunities") or 0))
    return serialize_metrics_strict(
        {
            "phase": str(rep.get("phase") or "PHASE59_FRAGMENTATION_TOXICITY_ARB_ENGINE"),
            "paper_only": True,
            "venue": venue,
            "symbol": symbol,
            "underlying": underlying,
            "cycles": int(rep.get("cycles") or cycles),
            "n_opportunities": int(rep.get("n_opportunities") or 0),
            "n_filters": int(rep.get("n_filters") or 0),
            "n_venue_quarantines": int(rep.get("n_venue_quarantines") or 0),
            "n_hard_limit_rejects": int(rep.get("n_hard_limit_rejects") or 0),
            "avg_edge_bps": float(rep.get("avg_edge_bps") or 0.0),
            "avg_toxicity": float(rep.get("avg_toxicity") or 0.0),
            "gates_ok": bool(rep.get("gates_ok")) and bool(finite_ok),
            "halted": bool(rep.get("halted")),
            "tox58_ok": bool(rep.get("tox58_ok")),
            "frag53_ok": bool(rep.get("frag53_ok")),
            "sor58_ok": bool(rep.get("sor58_ok")),
            "composed_phases": str(rep.get("composed_phases") or "17-58"),
            "seed": int(seed),
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
                        "deterministic_probe_route_id": f"p59fragtox:{venue}:{symbol}:{int(seed)+vi*100+si}",
                        "probe_cycle": 0,
                        "probe_gates_ok": bool(rep.get("gates_ok")),
                        "probe_halted": bool(rep.get("halted")),
                        "probe_n_opportunities": int(rep.get("n_opportunities") or 0),
                        "probe_n_filters": int(rep.get("n_filters") or 0),
                        "probe_n_venue_quarantines": int(rep.get("n_venue_quarantines") or 0),
                        "probe_avg_edge_bps": float(rep.get("avg_edge_bps") or 0.0),
                        "probe_avg_toxicity": float(rep.get("avg_toxicity") or 0.0),
                        "probe_finite": all(
                            math.isfinite(float(rep.get(k) or 0.0))
                            for k in ("avg_edge_bps", "avg_toxicity")
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
        "avg_edge_bps_finite_nonneg": math.isfinite(float(rep.get("avg_edge_bps") or 0.0)) and float(rep.get("avg_edge_bps") or 0.0) >= 0.0,
        "avg_toxicity_finite_0_1": math.isfinite(float(rep.get("avg_toxicity") or 0.0)) and 0.0 <= float(rep.get("avg_toxicity") or 0.0) <= 1.0,
        "n_opportunities_nonneg": int(rep.get("n_opportunities") or 0) >= 0,
        "n_filters_nonneg": int(rep.get("n_filters") or 0) >= 0,
        "n_venue_quarantines_nonneg": int(rep.get("n_venue_quarantines") or 0) >= 0,
        "campaign_gates_ok": bool(rep.get("gates_ok")),
        "all_reports_paper_only": bool(rep.get("paper_only")),
    }
    return {"report": rep, "deterministic_replay_equal": bool(same), "bounds": bounds, "bounds_ok": all(bool(v) for v in bounds.values())}


def generate(cycles: int = 80, seed: int = 59059) -> Dict[str, Any]:
    checks = _deterministic_checks(seed=seed, cycles=cycles)
    rep = checks["report"]
    coverage = _coverage_rows(seed=seed, cycles=max(1, COVERAGE_CYCLES))
    edge_vals = [float(x["probe_avg_edge_bps"]) for x in coverage]
    tox_vals = [float(x["probe_avg_toxicity"]) for x in coverage]
    opp_vals = [int(x["probe_n_opportunities"]) for x in coverage]
    filt_vals = [int(x["probe_n_filters"]) for x in coverage]
    q_vals = [int(x["probe_n_venue_quarantines"]) for x in coverage]
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
                "phase": str(rep.get("phase") or "PHASE59_FRAGMENTATION_TOXICITY_ARB_ENGINE"),
                "cycles": int(cycles),
                "probe_total_cycles": int(rep.get("cycles") or 0),
                "gates_ok": bool(rep.get("gates_ok")),
                "slo_ok": bool(rep.get("gates_ok")),
                "n_opportunities": int(rep.get("n_opportunities") or 0),
                "n_filters": int(rep.get("n_filters") or 0),
                "n_venue_quarantines": int(rep.get("n_venue_quarantines") or 0),
                "n_hard_limit_rejects": int(rep.get("n_hard_limit_rejects") or 0),
                "tox58_ok": bool(rep.get("tox58_ok")),
                "frag53_ok": bool(rep.get("frag53_ok")),
                "sor58_ok": bool(rep.get("sor58_ok")),
                "composed_phases": str(rep.get("composed_phases") or "17-58"),
                "source_seed": int(rep.get("seed") or seed),
            },
            "fragmentation_toxicity_arb_surface": {
                "paper_only": True,
                "venues": list(VENUES),
                "symbols": list(SYMBOLS),
                "underlyings": list(UNDERLYINGS),
                "deterministic_replay_equal": bool(checks["deterministic_replay_equal"]),
                "bounds_ok": bool(checks["bounds_ok"]),
                "bounds": checks["bounds"],
                "coverage_pairs": len(coverage),
                "avg_edge_bps": float(sum(edge_vals) / max(1, len(edge_vals))),
                "avg_toxicity": float(sum(tox_vals) / max(1, len(tox_vals))),
                "total_n_opportunities": int(sum(opp_vals)),
                "total_n_filters": int(sum(filt_vals)),
                "total_n_venue_quarantines": int(sum(q_vals)),
            },
            "venue_symbol_coverage": coverage,
            "arb_stress_summary": {
                "paper_only": True,
                "coverage_rows": len(coverage),
                "avg_edge_bps": float(sum(edge_vals) / max(1, len(edge_vals))),
                "min_edge_bps": float(min(edge_vals) if edge_vals else 0.0),
                "max_edge_bps": float(max(edge_vals) if edge_vals else 0.0),
                "avg_toxicity": float(sum(tox_vals) / max(1, len(tox_vals))),
                "total_n_opportunities": int(sum(opp_vals)),
                "total_n_filters": int(sum(filt_vals)),
                "total_n_venue_quarantines": int(sum(q_vals)),
                "halted_rows": int(halted_cycles),
            },
            "risk_posture": risk_posture,
            "evidence_refs": [
                "scripts/generate_phase59_fragmentation_toxicity_arb_paper_evidence.py",
                "src/liquidity/phase59_fragmentation_toxicity_arb_engine.py",
                "src/liquidity/phase53_fragmentation_arb_engine.py",
                "src/orderflow/phase58_flow_toxicity_mitigator.py",
                "src/execution/phase58_adaptive_options_smart_order_router.py",
                "src/risk/phase39_kill_switches_circuit_breakers.py",
                "src/telemetry/serialization.py",
                "research_state/PHASE58_FLOW_TOXICITY_MITIGATOR_PAPER_EVIDENCE_20261107T165643Z.json",
                "research_state/PHASE56_CROSS_VENUE_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T162958Z.json",
                "research_state/PHASE55_CROSS_VENUE_ORDERFLOW_EXECUTION_VALIDATOR_PAPER_EVIDENCE_20261107T163505Z.json",
                "research_state/PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T161211Z.json",
                "research_state/PHASE53_CROSS_MARGIN_STRESS_PROPAGATION_PAPER_EVIDENCE_20261107T152913Z.json",
                "research_state/PHASE52_REALTIME_LIQUIDITY_ALLOCATOR_PAPER_EVIDENCE_20261107T152449Z.json",
                "research_state/CONTINUOUS_VALIDATION_20261107T160845Z.json",
                "research_state/PAPER_OPS_SESSION_GATE_20261107T165832Z.json",
            ],
            "cross_refs": [
                "phase59_fragmentation_toxicity_arb_engine.py:Phase59FragmentationToxicityArbEngine/Phase59FragmentationToxicityArbConfig",
                "PHASE58_FLOW_TOXICITY_MITIGATOR_PAPER_EVIDENCE_20261107T165643Z.json",
                "PHASE56_CROSS_VENUE_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T162958Z.json",
                "PHASE55_CROSS_VENUE_ORDERFLOW_EXECUTION_VALIDATOR_PAPER_EVIDENCE_20261107T163505Z.json",
                "PHASE54_CROSS_ASSET_OPTIONS_FLOW_SYNTHESIZER_PAPER_EVIDENCE_20261107T161211Z.json",
                "PHASE53_CROSS_MARGIN_STRESS_PROPAGATION_PAPER_EVIDENCE_20261107T152913Z.json",
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
    ap.add_argument("--seed", type=int, default=59059)
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
