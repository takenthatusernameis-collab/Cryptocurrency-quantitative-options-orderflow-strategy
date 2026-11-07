#!/usr/bin/env python3
"""Generate phase50 options risk-factors paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
execution/backtest (fees/slippage/risk) → delta-neutral hedging + PnL attribution
→ reconciliation/monitoring. Advisory paper evidence only: never enables live
trading, never unblocks NEXT9, no external venue mutation.

Usage:
  PYTHONPATH=. python3 scripts/generate_phase50_options_risk_factors_paper_evidence.py [--cycles N] [--seed S] [--write]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

REPO = Path(__file__).resolve().parents[1]
RS = REPO / "research_state"
sys.path.insert(0, str(REPO))

from src.execution.phase50_cross_venue_relative_value_executor import (  # noqa: E402
    Phase50CrossVenueRelativeValueExecutor,
    Phase50RVConfig,
)
from src.integration.phase50_options_orderflow_execution_loop import (  # noqa: E402
    Phase50OptionsOrderflowExecutionLoop,
)
from src.marketmaking.phase50_toxicity_aware_options_mm import (  # noqa: E402
    Phase50MMConfig,
    Phase50ToxicityAwareOptionsMM,
)
from src.telemetry.serialization import serialize_metrics_strict  # noqa: E402

ARTIFACT_TYPE = "PHASE50_OPTIONS_RISK_FACTORS_PAPER_EVIDENCE"
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


def _make_probe_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p50rf|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p50rf_{tag}_{h}"


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
              "campaign", "rv_surface", "greeks_surface", "venue_symbol_coverage",
              "integrated_loop", "risk_posture", "evidence_refs", "cross_refs"):
        if d.get(k) in (None, "", [], {}):
            issues.append(f"missing_{k}")
    camp = d.get("campaign") or {}
    if camp.get("paper_only") is not True:
        issues.append("campaign_paper_only_required")
    if camp.get("gates_ok") is not True:
        issues.append("campaign_gates_ok_required")
    if int(camp.get("total_cycles") or 0) <= 0:
        issues.append("campaign_total_cycles_required")
    for key, venues_exp, underlyings_exp in (("rv_surface", VENUES, UNDERLYINGS),
                                              ("greeks_surface", VENUES, UNDERLYINGS)):
        surf = d.get(key) or {}
        if set(surf.get("venues") or []) != set(venues_exp):
            issues.append(f"{key}_venues_must_match")
        if set(surf.get("underlyings") or []) != set(underlyings_exp):
            issues.append(f"{key}_underlyings_must_match")
        if surf.get("paper_only") is not True:
            issues.append(f"{key}_paper_only_required")
        if surf.get("gates_ok") is not True:
            issues.append(f"{key}_gates_ok_required")
        rows = surf.get("rows") or []
        if not rows:
            issues.append(f"{key}_rows_required")
        if not all(isinstance(x, dict) and x.get("paper_only") is True for x in rows):
            issues.append(f"{key}_rows_paper_only_required")
    cov = d.get("venue_symbol_coverage") or []
    pairs = {(x.get("venue"), x.get("symbol")) for x in cov if isinstance(x, dict)}
    expected = {(v, s) for v in VENUES for s in SYMBOLS}
    if pairs != expected:
        issues.append("venue_symbol_coverage_must_match")
    if not all(isinstance(x, dict) and x.get("paper_only") is True for x in cov):
        issues.append("coverage_rows_must_be_paper_only")
    if not all(isinstance(x, dict) and x.get("deterministic_probe_id") for x in cov):
        issues.append("coverage_rows_must_have_probe_id")
    if not all(isinstance(x, dict) and bool(x.get("probe_finite")) for x in cov):
        issues.append("coverage_rows_must_have_finite_probe")
    il = d.get("integrated_loop") or {}
    if il.get("paper_only") is not True:
        issues.append("integrated_loop_paper_only_required")
    rp = d.get("risk_posture") or {}
    if rp.get("kill_switch_slo_posture") not in ("armed_paper", "observed_paper", "paper_guarded"):
        issues.append("risk_posture_invalid")
    if rp.get("paper_only") is not True:
        issues.append("risk_posture_paper_only_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _rv_probe(seed: int, underlying: str, venue: str) -> Dict[str, Any]:
    cfg = Phase50RVConfig(seed=int(seed), paper_only=True, venues=VENUES, underlyings=(underlying,), expiries=EXPIRIES, rv_threshold_bps=0.4, min_rv_bps=0.5)
    ex = Phase50CrossVenueRelativeValueExecutor(cfg)
    opps = ex.detect_rv_opps(cycles=1)
    involved = [o for o in opps if o.get("buy_venue") == venue or o.get("sell_venue") == venue]
    return {
        "venue": venue,
        "underlying": underlying,
        "symbol": SYMBOL_BY_UNDERLYING[underlying],
        "n_rv_opps": int(len(involved)),
        "avg_rv_bps": float(sum(float(o.get("rv_bps", 0.0)) for o in involved) / max(1, len(involved))),
        "avg_net_edge_bps": float(sum(float(o.get("net_edge_bps", 0.0)) for o in involved) / max(1, len(involved))),
        "avg_tca_est_slip_bps": float(sum(float(o.get("tca_est_slip_bps", 0.0)) for o in involved) / max(1, len(involved))),
        "n_exploitable": int(sum(1 for o in involved if float(o.get("net_edge_bps", 0.0)) >= cfg.min_rv_bps)),
        "deterministic_probe_id": _make_probe_id(seed, "rv", hash((venue, underlying)) % 100000),
        "probe_finite": all(math.isfinite(float(o.get("rv_bps", 0.0))) and math.isfinite(float(o.get("net_edge_bps", 0.0))) for o in involved),
        "paper_only": True,
    }


def _mm_probe(seed: int, underlying: str, venue: str) -> Dict[str, Any]:
    cfg = Phase50MMConfig(seed=int(seed) + 7, paper_only=True, underlyings=(underlying,), venues=(venue,), expiries=EXPIRIES)
    mm = Phase50ToxicityAwareOptionsMM(cfg)
    quotes = mm.generate_quotes(cycles=1)
    return {
        "venue": venue,
        "underlying": underlying,
        "symbol": SYMBOL_BY_UNDERLYING[underlying],
        "n_quotes": int(len(quotes)),
        "avg_spread_bps": float(sum(float(q.get("spread_bps", 0.0)) for q in quotes) / max(1, len(quotes))),
        "n_shaded": int(sum(1 for q in quotes if q.get("shaded"))),
        "n_greeks_neutral": int(sum(1 for q in quotes if q.get("greens_neutral"))),
        "avg_delta": float(sum(float(q.get("delta", 0.0)) for q in quotes) / max(1, len(quotes))),
        "avg_gamma": float(sum(float(q.get("gamma", 0.0)) for q in quotes) / max(1, len(quotes))),
        "avg_vega": float(sum(float(q.get("vega", 0.0)) for q in quotes) / max(1, len(quotes))),
        "deterministic_probe_id": _make_probe_id(seed, "mm", hash((venue, underlying)) % 100000),
        "probe_finite": all(math.isfinite(float(q.get("spread_bps", 0.0))) and math.isfinite(float(q.get("delta", 0.0))) and math.isfinite(float(q.get("gamma", 0.0))) and math.isfinite(float(q.get("vega", 0.0))) for q in quotes),
        "paper_only": True,
    }


def _coverage(seed: int) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    idx = 0
    for venue in VENUES:
        for underlying in UNDERLYINGS:
            rv = _rv_probe(seed + idx * 3 + 1, underlying, venue)
            mm = _mm_probe(seed + idx * 3 + 2, underlying, venue)
            rows.append(serialize_metrics_strict({
                "venue": venue,
                "underlying": underlying,
                "symbol": mm["symbol"],
                "rv_probe": rv,
                "mm_probe": mm,
                "deterministic_probe_id": _make_probe_id(seed, "cov", idx),
                "probe_finite": bool(rv["probe_finite"] and mm["probe_finite"]),
                "campaign_rv_n_opps": int(rv["n_rv_opps"]),
                "campaign_mm_n_quotes": int(mm["n_quotes"]),
                "paper_only": True,
            }))
            idx += 1
    return rows


def _deterministic_checks(seed: int, cycles: int) -> Dict[str, Any]:
    cfg_rv = Phase50RVConfig(seed=int(seed), paper_only=True, venues=VENUES, underlyings=UNDERLYINGS, expiries=EXPIRIES, rv_threshold_bps=0.4, min_rv_bps=0.5)
    ex1 = Phase50CrossVenueRelativeValueExecutor(cfg_rv)
    rep1 = ex1.run_campaign(cycles=int(cycles))
    ex2 = Phase50CrossVenueRelativeValueExecutor(Phase50RVConfig(seed=int(seed), paper_only=True, venues=VENUES, underlyings=UNDERLYINGS, expiries=EXPIRIES, rv_threshold_bps=0.4, min_rv_bps=0.5))
    rep2 = ex2.run_campaign(cycles=int(cycles))
    rv_same = _strip_timestamps(rep1) == _strip_timestamps(rep2)

    cfg_mm = Phase50MMConfig(seed=int(seed), paper_only=True, underlyings=UNDERLYINGS, venues=VENUES, expiries=EXPIRIES)
    mm1 = Phase50ToxicityAwareOptionsMM(cfg_mm)
    rep_mm1 = mm1.run_campaign(cycles=int(cycles))
    mm2 = Phase50ToxicityAwareOptionsMM(Phase50MMConfig(seed=int(seed), paper_only=True, underlyings=UNDERLYINGS, venues=VENUES, expiries=EXPIRIES))
    rep_mm2 = mm2.run_campaign(cycles=int(cycles))
    mm_same = _strip_timestamps(rep_mm1) == _strip_timestamps(rep_mm2)

    rv_opp_list = [o.to_dict() for o in ex1.opps] if hasattr(ex1, "opps") else []
    rv_rows = []
    for u in UNDERLYINGS:
        for e in EXPIRIES:
            subset = [o for o in rv_opp_list if o.get("underlying") == u and o.get("expiry") == e]
            rv_rows.append(serialize_metrics_strict({
                "underlying": u,
                "expiry": e,
                "symbol": SYMBOL_BY_UNDERLYING[u],
                "n_opps": int(len(subset)),
                "n_exploitable": int(sum(1 for o in subset if float(o.get("net_edge_bps", 0.0)) >= cfg_rv.min_rv_bps)),
                "avg_net_edge_bps": float(sum(float(o.get("net_edge_bps", 0.0)) for o in subset) / max(1, len(subset))),
                "paper_only": True,
            }))
    mm_quotes = [q.to_dict() for q in mm1.quotes] if hasattr(mm1, "quotes") else []
    bounds = {
        "all_rv_net_edge_finite": all(math.isfinite(float(o.get("net_edge_bps", 0.0))) for o in rv_opp_list),
        "all_rv_slippage_non_negative": all(float(o.get("tca_est_slip_bps", 0.0)) >= 0.0 for o in rv_opp_list),
        "all_mm_spread_non_negative": all(float(q.get("spread_bps", 0.0)) >= 0.0 for q in mm_quotes),
        "all_mm_spread_bounded": all(float(q.get("spread_bps", 0.0)) <= 1000.0 for q in mm_quotes),
        "all_venues_in_scope": all(o.get("buy_venue") in VENUES and o.get("sell_venue") in VENUES for o in rv_opp_list) and all(q.get("venue") in VENUES for q in mm_quotes),
        "all_underlyings_in_scope": all(o.get("underlying") in UNDERLYINGS for o in rv_opp_list) and all(q.get("underlying") in UNDERLYINGS for q in mm_quotes),
    }
    return {
        "rv_campaign": rep1,
        "mm_campaign": rep_mm1,
        "rv_deterministic_replay_equal": bool(rv_same),
        "mm_deterministic_replay_equal": bool(mm_same),
        "deterministic_replay_equal": bool(rv_same and mm_same),
        "bounds": bounds,
        "bounds_ok": all(bool(v) for v in bounds.values()),
        "rv_rows": rv_rows,
        "mm_rows": mm_quotes,
    }


def generate(cycles: int = 40, seed: int = 50052) -> Dict[str, Any]:
    checks = _deterministic_checks(seed=seed, cycles=cycles)
    rep_rv = checks["rv_campaign"]
    rep_mm = checks["mm_campaign"]
    coverage = _coverage(seed=seed)

    il = Phase50OptionsOrderflowExecutionLoop(seed=int(seed), cycles=min(int(cycles), 20), paper_only=True, outdir=str(RS))
    il_rep = il.run()
    gates_ok = bool(il_rep.get("gates_ok", False) and rep_rv.get("gates_ok", False) and rep_mm.get("gates_ok", False))

    risk_posture = {
        "paper_only": True,
        "kill_switch_slo_posture": "armed_paper" if gates_ok else "paper_guarded",
        "gates_ok": bool(gates_ok),
        "halt_executed": bool(il_rep.get("halt_executed", False)),
        "halt_events": int(len(il_rep.get("halt_events") or [])),
        "slo_alerts_fired": int(il_rep.get("slo_alerts_fired") or 0),
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
            "total_cycles": int(cycles),
            "gates_ok": bool(gates_ok),
            "n_rv_opps": int(rep_rv.get("n_opps") or 0),
            "n_rv_exploitable": int(rep_rv.get("n_exploitable") or 0),
            "avg_rv_net_edge_bps": float(rep_rv.get("avg_net_edge_bps") or 0.0),
            "n_mm_quotes": int(rep_mm.get("n_quotes") or 0),
            "n_mm_shaded": int(rep_mm.get("n_shaded") or 0),
            "n_mm_greeks_neutral": int(rep_mm.get("n_greeks_neutral") or 0),
            "avg_mm_spread_bps": float(rep_mm.get("avg_spread_bps") or 0.0),
            "integrated_loop_gates_ok": bool(il_rep.get("gates_ok", False)),
            "halt_executed": bool(il_rep.get("halt_executed", False)),
        },
        "rv_surface": {
            "phase": "PHASE50_CROSS_VENUE_RELATIVE_VALUE_EXECUTOR",
            "paper_only": True,
            "seed": int(seed),
            "venues": list(VENUES),
            "underlyings": list(UNDERLYINGS),
            "expiries": list(EXPIRIES),
            "gates_ok": bool(rep_rv.get("gates_ok", False)),
            "n_opps": int(rep_rv.get("n_opps") or 0),
            "n_exploitable": int(rep_rv.get("n_exploitable") or 0),
            "avg_net_edge_bps": float(rep_rv.get("avg_net_edge_bps") or 0.0),
            "rows": checks["rv_rows"],
        },
        "greeks_surface": {
            "phase": "PHASE50_TOXICITY_AWARE_OPTIONS_MM",
            "paper_only": True,
            "seed": int(seed),
            "venues": list(VENUES),
            "underlyings": list(UNDERLYINGS),
            "expiries": list(EXPIRIES),
            "gates_ok": bool(rep_mm.get("gates_ok", False)),
            "n_quotes": int(rep_mm.get("n_quotes") or 0),
            "n_shaded": int(rep_mm.get("n_shaded") or 0),
            "n_greeks_neutral": int(rep_mm.get("n_greeks_neutral") or 0),
            "avg_spread_bps": float(rep_mm.get("avg_spread_bps") or 0.0),
            "rows": [
                serialize_metrics_strict({
                    "venue": v,
                    "underlying": u,
                    "symbol": SYMBOL_BY_UNDERLYING[u],
                    "paper_only": True,
                }) for v in VENUES for u in UNDERLYINGS
            ],
        },
        "venue_symbol_coverage": coverage,
        "integrated_loop": {
            "phase": "PHASE50_OPTIONS_ORDERFLOW_EXECUTION_LOOP",
            "paper_only": True,
            "cycles": min(int(cycles), 20),
            "gates_ok": bool(il_rep.get("gates_ok", False)),
            "halt_executed": bool(il_rep.get("halt_executed", False)),
            "halt_events": int(len(il_rep.get("halt_events") or [])),
            "slo_alerts_fired": int(il_rep.get("slo_alerts_fired") or 0),
            "toxicity_mm50_gates_ok": bool(il_rep.get("toxicity_mm50", {}).get("gates_ok")),
            "cross_venue_rv50_gates_ok": bool(il_rep.get("cross_venue_rv50", {}).get("gates_ok")),
            "risk_hedge_campaign_gates_ok": bool(il_rep.get("risk_hedge_campaign", {}).get("gates_ok")),
            "resilience_campaign_gates_ok": bool(il_rep.get("resilience_campaign", {}).get("gates_ok")),
            "phase39_kill_switches_gates_ok": bool(il_rep.get("phase39_kill_switches", {}).get("gates_ok")),
        },
        "determinism": {
            "deterministic_seeded": True,
            "rv_same_seed_reproduces_surface": bool(checks["rv_deterministic_replay_equal"]),
            "mm_same_seed_reproduces_surface": bool(checks["mm_deterministic_replay_equal"]),
            "same_seed_cycles_reproduce_surface": bool(checks["deterministic_replay_equal"]),
            "bounds_ok": bool(checks["bounds_ok"]),
            "bounds": checks["bounds"],
        },
        "risk_posture": risk_posture,
        "evidence_refs": [
            "src/execution/phase50_cross_venue_relative_value_executor.py",
            "src/marketmaking/phase50_toxicity_aware_options_mm.py",
            "src/integration/phase50_options_orderflow_execution_loop.py",
            "scripts/generate_phase50_options_risk_factors_paper_evidence.py",
            "tests/test_generate_phase50_options_risk_factors_paper_evidence.py",
        ],
        "cross_refs": [
            "research_state/PHASE42_GREEKS_RISK_PAPER_EVIDENCE_20261107T130556Z.json",
            "research_state/PHASE46_EXECUTION_PAPER_EVIDENCE_20261107T132047Z.json",
            "research_state/PHASE51_LATENCY_AWARE_OPTIONS_SOR_PAPER_EVIDENCE_20261107T142001Z.json",
            "research_state/PHASE39_LIVE_READINESS_PAPER_EVIDENCE_20261107T141256Z.json",
            "research_state/CONTINUOUS_VALIDATION_20261107T140506Z.json",
            "research_state/PAPER_OPS_SESSION_GATE_20261107T150604Z.json",
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
    ap.add_argument("--cycles", type=int, default=40)
    ap.add_argument("--seed", type=int, default=50052)
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
