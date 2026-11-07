#!/usr/bin/env python3
"""Generate phase42 Greeks risk monitor paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
delta-neutral hedging / Greeks risk monitoring. Advisory paper evidence only:
never enables live trading, never unblocks NEXT9, no external venue mutation.

Usage:
  PYTHONPATH=. python3 scripts/generate_phase42_greeks_risk_paper_evidence.py [--cycles N] [--seed S] [--write]
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

from src.risk.phase42_greeks_risk_monitor import GreeksMonitorConfig42, Phase42GreeksRiskMonitor  # noqa: E402

ARTIFACT_TYPE = "PHASE42_GREEKS_RISK_PAPER_EVIDENCE"
VENUES = ("deribit", "okx", "binance")
SYMBOLS = ("BTC", "ETH")
EXPIRIES = ("7D", "30D", "90D")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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
    for k in ("timestamp_utc", "seed", "venues", "symbols", "campaign", "risk_summary", "evidence_refs"):
        if d.get(k) in (None, "", [], {}):
            issues.append(f"missing_{k}")
    camp = d.get("campaign") or {}
    if camp.get("paper_only") is not True:
        issues.append("campaign_paper_only_required")
    if int(camp.get("total_cycles") or 0) <= 0:
        issues.append("campaign_total_cycles_required")
    by_u = ((camp.get("snapshots") or [{}])[0] or {}).get("by_underlying") or []
    if set(x.get("underlying") for x in by_u if isinstance(x, dict)) != set(SYMBOLS):
        issues.append("campaign_underlyings_must_match_symbols")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def generate(cycles: int = 12, seed: int = 42042) -> Dict[str, Any]:
    cfg = GreeksMonitorConfig42(
        seed=int(seed),
        paper_only=True,
        underlyings=SYMBOLS,
        venues=VENUES,
        expiries=EXPIRIES,
        cycles=int(cycles),
    )
    monitor = Phase42GreeksRiskMonitor(cfg)
    camp = monitor.run_campaign(int(cycles))
    snaps = camp.get("snapshots") or []
    tail_alerts = sum(1 for s in snaps if s.get("tail_gamma_alert"))
    blocked_cycles = sum(1 for s in snaps if not s.get("risk_ok", True))
    stressed_cycles = sum(1 for s in snaps if s.get("regime") == "stressed")
    d: Dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "timestamp_utc": _utc_iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "advisory": True,
        "no_external_venue_mutation": True,
        "phase": "PHASE42_GREEKS_RISK_MONITOR",
        "seed": int(seed),
        "cycles": int(cycles),
        "venues": list(VENUES),
        "symbols": list(SYMBOLS),
        "expiries": list(EXPIRIES),
        "scope": "paper-only phase42 Greeks risk monitor evidence for crypto options orderflow; Deribit/OKX/Binance × BTC/ETH; delta/gamma/vega/theta netting, tail-gamma, regime-aware monitoring; no live capital, no external venue mutation, cannot unblock NEXT9",
        "campaign": camp,
        "risk_summary": {
            "total_cycles": int(camp.get("total_cycles") or 0),
            "final_risk_ok": bool(camp.get("final_risk_ok")),
            "blocked_cycles": int(blocked_cycles),
            "tail_gamma_alerts": int(tail_alerts),
            "stressed_regime_cycles": int(stressed_cycles),
            "avg_total_delta_usd": float(camp.get("avg_total_delta_usd") or 0.0),
            "avg_total_gamma_usd": float(camp.get("avg_total_gamma_usd") or 0.0),
            "avg_total_vega_usd": float(camp.get("avg_total_vega_usd") or 0.0),
            "underlyings_covered": list(SYMBOLS),
            "venues_covered": list(VENUES),
        },
        "evidence_refs": [
            "src/risk/phase42_greeks_risk_monitor.py",
            "tests/test_phase42_greeks_risk_monitor.py",
            "research_state/PHASE42_GREEKS_RISK_MONITOR_REPORT.json",
            "research_state/CROSSVENUE_ORCHESTRATION_REPORT.json",
            "research_state/PHASE37_CROSS_VENUE_ROUTING_REPORT.json",
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
    ap = argparse.ArgumentParser(description="Generate phase42 Greeks risk paper evidence (paper-only)")
    ap.add_argument("--cycles", type=int, default=12)
    ap.add_argument("--seed", type=int, default=42042)
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
        out_path = RS / f"PHASE42_GREEKS_RISK_PAPER_EVIDENCE_{ts}.json"
        out_path.write_text(json.dumps(d, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "wrote": str(out_path.relative_to(REPO)) if out_path else None,
        "valid": True,
        "paper_only": True,
        "next9_unblocked": False,
        "total_cycles": d["risk_summary"]["total_cycles"],
        "final_risk_ok": d["risk_summary"]["final_risk_ok"],
        "tail_gamma_alerts": d["risk_summary"]["tail_gamma_alerts"],
        "blocked_cycles": d["risk_summary"]["blocked_cycles"],
        "venues": d["venues"],
        "symbols": d["symbols"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
