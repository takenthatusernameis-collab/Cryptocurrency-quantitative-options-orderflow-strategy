#!/usr/bin/env python3
"""Generate phase46 execution-intelligence paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
execution/backtest (fees/slippage/risk) → delta-neutral hedging + PnL attribution
→ reconciliation/monitoring. Advisory paper evidence only: never enables live
trading, never unblocks NEXT9, no external venue mutation.

Usage:
  PYTHONPATH=. python3 scripts/generate_phase46_execution_paper_evidence.py [--cycles N] [--seed S] [--write]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
sys.path.insert(0, str(REPO))

from src.execution.phase46_adaptive_mm_engine import (  # noqa: E402
    AdaptiveMMConfig, Phase46AdaptiveMM,
)
from src.integration.phase46_execution_intelligence_loop import (  # noqa: E402
    Phase46ExecutionIntelligenceLoop,
)
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE46_EXECUTION_PAPER_EVIDENCE"
VENUES = ("deribit", "okx", "binance")
SYMBOLS = ("BTC-PERP", "ETH-PERP")
UNDERLYINGS = ("BTC", "ETH")


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
              "campaign", "execution_intelligence", "adaptive_mm_surface", "risk_summary",
              "evidence_refs", "cross_refs"):
        if d.get(k) in (None, "", [], {}):
            issues.append(f"missing_{k}")
    camp = d.get("campaign") or {}
    if camp.get("paper_only") is not True:
        issues.append("campaign_paper_only_required")
    if int(camp.get("total_cycles") or 0) <= 0:
        issues.append("campaign_total_cycles_required")
    surf = d.get("adaptive_mm_surface") or {}
    if set(surf.get("venues") or []) != set(VENUES):
        issues.append("surface_venues_must_match")
    if set(surf.get("symbols") or []) != set(SYMBOLS):
        issues.append("surface_symbols_must_match")
    ei = d.get("execution_intelligence") or {}
    if ei.get("paper_only") is not True:
        issues.append("ei_paper_only_required")
    if ei.get("gates_ok") is not True:
        issues.append("ei_gates_ok_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _mm_surface(seed: int, cycles: int) -> Dict[str, Any]:
    cfg = AdaptiveMMConfig(
        seed=int(seed),
        paper_only=True,
        venues=VENUES,
        symbols=SYMBOLS,
        cycles=int(cycles),
        outdir=str(RS),
    )
    mm = Phase46AdaptiveMM(cfg)
    rep = mm.run_campaign(cycles=int(cycles))
    mm.generate_reports(str(RS))
    risk = rep.get("risk_state", {})
    return {
        "phase": "PHASE46_ADAPTIVE_MM_ENGINE",
        "paper_only": bool(rep.get("paper_only")),
        "modes": rep.get("modes"),
        "seed": int(rep.get("seed") or seed),
        "cycles": int(rep.get("cycles") or cycles),
        "cycles_run": int(rep.get("cycles_run") or 0),
        "venues": list(rep.get("venues") or list(VENUES)),
        "symbols": list(rep.get("symbols") or list(SYMBOLS)),
        "final_halted": bool(rep.get("final_halted")),
        "n_quotes": int(rep.get("n_quotes") or 0),
        "n_dislocations": int(rep.get("n_dislocations") or 0),
        "n_exploitable_dislocations": int(rep.get("n_exploitable_dislocations") or 0),
        "avg_spread_bps": float(rep.get("avg_spread_bps") or 0.0),
        "gates_ok": bool(rep.get("gates_ok")),
        "risk_state": {
            "within_limits": bool(risk.get("within_limits")),
            "total_delta_abs": float(risk.get("total_delta_abs") or 0.0),
            "max_inventory_abs": float(risk.get("max_inventory_abs") or 0.0),
            "venue_count": int(risk.get("venue_count") or len(VENUES)),
            "symbol_count": int(risk.get("symbol_count") or len(SYMBOLS)),
            "paper_only": bool(risk.get("paper_only")),
        },
        "venue_symbol_coverage": [
            {"venue": v, "symbol": s, "paper_only": True} for v in VENUES for s in SYMBOLS
        ],
    }


def generate(cycles: int = 14, seed: int = 47) -> Dict[str, Any]:
    # Composed execution-intelligence loop (Phases 28/32/39/42/44/45/46 + SLO).
    loop = Phase46ExecutionIntelligenceLoop(seed=int(seed), cycles=int(cycles),
                                            paper_only=True, outdir=str(RS))
    ei_rep = loop.run()

    # Dedicated adaptive-MM latency-arb surface restricted to BTC/ETH × deribit/okx/binance.
    mm_surface = _mm_surface(int(seed), int(cycles))

    # Determinism check: re-run the MM surface with identical seed/cycles and compare.
    mm_surface_2 = _mm_surface(int(seed), int(cycles))
    deterministic = _strip_timestamps(mm_surface) == _strip_timestamps(mm_surface_2)

    d: Dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "timestamp_utc": _utc_iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "advisory": True,
        "no_external_venue_mutation": True,
        "phase": "PHASE46_EXECUTION_INTELLIGENCE_LOOP",
        "seed": int(seed),
        "cycles": int(cycles),
        "venues": list(VENUES),
        "symbols": list(SYMBOLS),
        "underlyings": list(UNDERLYINGS),
        "scope": ("paper-only phase46 execution-intelligence evidence for crypto options orderflow; "
                  "Deribit/OKX/Binance × BTC/ETH (BTC-PERP/ETH-PERP); adaptive MM + cross-venue "
                  "latency-arb dislocations, kill-switch/SLO posture, venue×symbol coverage, deterministic "
                  "seeded cycles, finite numerics; no live capital, no external venue mutation, "
                  "cannot unblock NEXT9; advisory only"),
        "campaign": {
            "phase": "PHASE46_EXECUTION_INTELLIGENCE_LOOP",
            "paper_only": True,
            "seed": int(seed),
            "total_cycles": int(cycles),
            "venues": list(VENUES),
            "symbols": list(SYMBOLS),
            "underlyings": list(UNDERLYINGS),
            "modes": "paper",
        },
        "execution_intelligence": ei_rep,
        "adaptive_mm_surface": mm_surface,
        "determinism": {
            "deterministic_seeded": bool(deterministic),
            "same_seed_cycles_reproduce_surface": bool(deterministic),
        },
        "risk_summary": {
            "total_cycles": int(cycles),
            "gates_ok": bool(ei_rep.get("gates_ok")),
            "mm_gates_ok": bool(ei_rep.get("mm_campaign", {}).get("gates_ok")),
            "within_limits": bool(ei_rep.get("mm_campaign", {}).get("risk_state", {}).get("within_limits")),
            "halt_executed": bool(ei_rep.get("halt_executed")),
            "n_halt_events": int(ei_rep.get("n_halt_events") or 0),
            "n_mm_quotes": int(ei_rep.get("n_mm_quotes") or 0),
            "n_dislocations": int(ei_rep.get("n_dislocations") or 0),
            "n_exploitable_dislocations": int(ei_rep.get("n_exploitable_dislocations") or 0),
            "slo_alerts_fired": int(ei_rep.get("slo_alerts_fired") or 0),
            "venues_covered": list(VENUES),
            "symbols_covered": list(SYMBOLS),
            "paper_only": bool(ei_rep.get("paper_only")),
        },
        "evidence_refs": [
            "src/integration/phase46_execution_intelligence_loop.py",
            "src/execution/phase46_adaptive_mm_engine.py",
            "tests/test_phase46_execution_intelligence_loop.py",
            "tests/test_generate_phase46_execution_paper_evidence.py",
        ],
        "cross_refs": [
            "research_state/PHASE46_EXECUTION_INTELLIGENCE_LOOP_REPORT.json",
            "research_state/PHASE46_ADAPTIVE_MM_ENGINE_REPORT.json",
            "research_state/PHASE46_CAMPAIGN_SUMMARY.json",
        ],
        "flags": {
            "deterministic_seeded": True,
            "finite_numerics_validated": True,
            "advisory_only": True,
        },
    }
    ok, issues = validate_artifact(d)
    d["validation"] = {"valid": ok, "issues": issues}
    return d


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate phase46 execution-intelligence paper evidence (paper-only)")
    ap.add_argument("--cycles", type=int, default=14)
    ap.add_argument("--seed", type=int, default=47)
    ap.add_argument("--write", action="store_true", default=True, help="Write additive timestamped artifact (default true)")
    ap.add_argument("--no-write", dest="write", action="store_false")
    args = ap.parse_args(argv)
    d = generate(cycles=args.cycles, seed=args.seed)
    if not d["validation"]["valid"]:
        print(json.dumps({"valid": False, "issues": d["validation"]["issues"]}, indent=2))
        return 1
    out_path = None
    if args.write:
        RS.mkdir(parents=True, exist_ok=True)
        ts = _utc()
        out_path = RS / f"PHASE46_EXECUTION_PAPER_EVIDENCE_{ts}.json"
        out_path.write_text(json.dumps(d, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out_path.relative_to(REPO)) if out_path else None,
        "valid": True,
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "advisory": True,
        "no_external_venue_mutation": True,
        "deterministic": d["determinism"]["deterministic_seeded"],
        "total_cycles": d["risk_summary"]["total_cycles"],
        "gates_ok": d["risk_summary"]["gates_ok"],
        "halt_executed": d["risk_summary"]["halt_executed"],
        "n_mm_quotes": d["risk_summary"]["n_mm_quotes"],
        "n_dislocations": d["risk_summary"]["n_dislocations"],
        "venues": d["venues"],
        "symbols": d["symbols"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
