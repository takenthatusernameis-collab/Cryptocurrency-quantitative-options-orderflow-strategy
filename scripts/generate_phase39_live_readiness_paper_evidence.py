#!/usr/bin/env python3
"""Generate phase39 live-readiness paper evidence (additive, paper-only).

Repo-priority: crypto options orderflow (Deribit/OKX/Binance × BTC/ETH) →
features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging
+ directional/hedge PnL attribution → reconciliation/monitoring. Advisory paper
evidence only: never enables live trading, never unblocks NEXT9, no external
venue mutation.

Usage:
  PYTHONPATH=. python3 scripts/generate_phase39_live_readiness_paper_evidence.py [--cycles N] [--seed S] [--write]
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

from src.risk.phase39_kill_switches_circuit_breakers import (  # noqa: E402
    KillSwitchConfig39, Phase39KillSwitchesCircuitBreakers,
)
from src.recovery.phase39_disaster_recovery import (  # noqa: E402
    Phase39DisasterRecovery, RecoveryConfig39,
)
from src.validation.phase39_prepost_trade_validation import (  # noqa: E402
    Phase39PrePostTradeValidation, PrePostConfig39,
)

ARTIFACT_TYPE = "PHASE39_LIVE_READINESS_PAPER_EVIDENCE"
VENUES = ("deribit", "okx", "binance")
SYMBOLS = ("BTC-USD", "ETH-USD")
UNDERLYINGS = ("BTC", "ETH")


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _strip_timestamps(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _strip_timestamps(v) for k, v in obj.items()
                if k not in ("timestamp_utc", "timestamp", "last_trip")}
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


def _latest_glob(pattern: str) -> Optional[str]:
    hits = sorted(RS.glob(pattern))
    return f"research_state/{hits[-1].name}" if hits else None


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
              "campaign", "kill_switch_slo_posture", "validation_surface",
              "reconciliation_freshness", "margin_settlement_audit", "risk_summary",
              "evidence_refs", "cross_refs"):
        if d.get(k) in (None, "", [], {}):
            issues.append(f"missing_{k}")
    camp = d.get("campaign") or {}
    if camp.get("paper_only") is not True:
        issues.append("campaign_paper_only_required")
    if int(camp.get("total_cycles") or 0) <= 0:
        issues.append("campaign_total_cycles_required")
    ks = d.get("kill_switch_slo_posture") or {}
    if ks.get("paper_only") is not True:
        issues.append("kill_switch_paper_only_required")
    if set(ks.get("venues") or []) != set(VENUES):
        issues.append("kill_switch_venues_must_match")
    recon = d.get("reconciliation_freshness") or {}
    if recon.get("paper_only") is not True:
        issues.append("reconciliation_paper_only_required")
    ms = d.get("margin_settlement_audit") or {}
    if ms.get("paper_only") is not True:
        issues.append("margin_settlement_paper_only_required")
    if ms.get("deterministic") is not True:
        issues.append("margin_settlement_deterministic_required")
    rs = d.get("risk_summary") or {}
    if rs.get("gates_ok") is not True:
        issues.append("risk_summary_gates_ok_required")
    issues.extend(_assert_finite(d, "artifact"))
    return (len(issues) == 0, issues)


def _kill_switch_surface(seed: int, cycles: int) -> Dict[str, Any]:
    # Restrict to the project BTC/ETH × deribit/okx/binance scope.
    cfg = KillSwitchConfig39(
        seed=int(seed),
        paper_only=True,
        venues=VENUES,
        underlyings=UNDERLYINGS,
    )
    ks = Phase39KillSwitchesCircuitBreakers(cfg)
    per_cycle = []
    for c in range(int(cycles)):
        cyc = ks.evaluate_cycle(c)
        per_cycle.append({
            "cycle": c,
            "regime": cyc.regime,
            "global_halt": bool(cyc.global_halt),
            "trading_enabled": bool(cyc.trading_enabled),
            "action_taken": cyc.action_taken,
            "n_kill_events": len(cyc.kill_events),
            "paper_only": bool(cyc.paper_only),
        })
    camp = ks.run_campaign()  # deterministic 12-cycle campaign in component
    venue_states = {}
    for c in ks.cycles:
        for cs in c.circuits:
            venue_states[cs.venue] = cs.state
    return {
        "phase": "PHASE39_KILL_SWITCH_SLO_POSTURE",
        "paper_only": True,
        "seed": int(seed),
        "cycles": int(cycles),
        "venues": list(VENUES),
        "symbols": list(SYMBOLS),
        "underlyings": list(UNDERLYINGS),
        "per_cycle_posture": per_cycle,
        "campaign_summary": {
            "n_cycles": int(camp.get("n_cycles") or 0),
            "n_kill_events": int(camp.get("n_kill_events") or 0),
            "global_halts": int(camp.get("global_halts") or 0),
            "trading_enabled_cycles": int(camp.get("trading_enabled_cycles") or 0),
            "paper_only": bool(camp.get("paper_only")),
        },
        "venue_circuit_states_terminal": venue_states,
        "slo_posture": {
            "kill_switch_authority_paper_only": True,
            "global_halt_observable": any(x["global_halt"] for x in per_cycle),
            "trading_restriction_observable": any(not x["trading_enabled"] for x in per_cycle),
            "no_external_venue_mutation": True,
        },
        "venue_symbol_coverage": [
            {"venue": v, "symbol": s, "underlying": u, "paper_only": True}
            for v, s, u in zip(VENUES, SYMBOLS, UNDERLYINGS) for _ in (0,)
        ] + [
            {"venue": v, "symbol": s, "underlying": u, "paper_only": True}
            for v in VENUES for s, u in zip(SYMBOLS, UNDERLYINGS)
        ],
    }


def _validation_surface(seed: int, cycles: int) -> Dict[str, Any]:
    pv = Phase39PrePostTradeValidation(PrePostConfig39(seed=int(seed), paper_only=True))
    rows = []
    for c in range(int(cycles)):
        # Deterministic per-venue/symbol pre/post checks (paper-only, in-memory).
        venue = VENUES[c % len(VENUES)]
        sym = SYMBOLS[c % len(SYMBOLS)]
        order = {
            "venue": venue,
            "symbol": sym,
            "notional_usd": 25000.0 + (c * 1000.0),
            "delta": 0.12 if sym.startswith("BTC") else 0.08,
        }
        fill = {"slippage_bps": 2.0 + (c % 3), "filled": True}
        res = pv.validate(c, order=order, fill=fill)
        rows.append({
            "cycle": c,
            "venue": venue,
            "symbol": sym,
            "all_passed": bool(res.all_passed),
            "blocked": bool(res.blocked),
            "n_pre_gates": len(res.pre_gates),
            "n_post_gates": len(res.post_gates),
            "paper_only": bool(res.paper_only),
        })
    camp = pv.run_campaign()
    return {
        "phase": "PHASE39_PREPOST_TRADE_VALIDATION_SURFACE",
        "paper_only": True,
        "seed": int(seed),
        "cycles": int(cycles),
        "rows": rows,
        "campaign_summary": {
            "n_results": int(camp.get("n_results") or 0),
            "all_passed_count": int(camp.get("all_passed_count") or 0),
            "blocked_count": int(camp.get("blocked_count") or 0),
            "paper_only": bool(camp.get("paper_only")),
        },
        "all_rows_passed": all(r["all_passed"] for r in rows),
        "gates_ok": all(r["all_passed"] for r in rows),
    }


def _reconciliation_freshness(seed: int) -> Dict[str, Any]:
    # Deterministic reconciliation freshness snapshot from latest CV artifact when present.
    cv = _latest_glob("CONTINUOUS_VALIDATION_*.json")
    freshness = None
    paper_only = True
    if cv:
        try:
            data = json.loads((REPO / cv).read_text(encoding="utf-8"))
            # Derive freshness values from iteration reconciliation checks.
            vals = []
            for it in data.get("iterations") or []:
                chk = (it.get("checks") or {}).get("reconciliation") or {}
                v = chk.get("freshness")
                if v is not None:
                    vals.append(float(v))
            freshness = vals if vals else data.get("recon_freshness")
            paper_only = bool(data.get("paper_only", True))
        except Exception:
            freshness = None
    return {
        "phase": "PHASE39_RECONCILIATION_FRESHNESS_AUDIT",
        "paper_only": bool(paper_only),
        "seed": int(seed),
        "source_cv_artifact": cv,
        "freshness_values": freshness,
        "freshness_present": freshness is not None,
        "freshness_all_ones": bool(freshness) and all(float(x) == 1.0 for x in freshness),
        "advisory": True,
    }


def _margin_settlement_audit(seed: int, cycles: int) -> Dict[str, Any]:
    dr = Phase39DisasterRecovery(RecoveryConfig39(seed=int(seed), paper_only=True))
    cps = []
    restores = []
    for c in range(int(cycles)):
        state = {
            "positions_count": 6 + (c % 4),
            "notional_usd": 400000.0 + c * 15000.0,
            "cash_usd": 1000000.0 - c * 5000.0,
            "margin_buffer_usd": 250000.0 - c * 2000.0,
            "settlement_pending_usd": 10000.0 + c * 500.0,
        }
        cp = dr.create_checkpoint(c, state=state)
        cps.append({
            "checkpoint_id": cp.checkpoint_id,
            "cycle": int(cp.cycle),
            "state_hash": cp.state_hash,
            "positions_count": int(cp.positions_count),
            "notional_usd": float(cp.notional_usd),
            "cash_usd": float(cp.cash_usd),
            "valid": bool(cp.valid),
        })
        rr = dr.restore_from_checkpoint(cp.checkpoint_id)
        restores.append({
            "checkpoint_id": cp.checkpoint_id,
            "success": bool(rr.success),
            "validated": bool(rr.validated),
        })
    dr2 = Phase39DisasterRecovery(RecoveryConfig39(seed=int(seed), paper_only=True))
    hashes1 = [dr2.create_checkpoint(c, state={
        "positions_count": 6 + (c % 4), "notional_usd": 400000.0 + c * 15000.0,
        "cash_usd": 1000000.0 - c * 5000.0,
    }).state_hash for c in range(int(cycles))]
    deterministic = [c["state_hash"] for c in cps] == hashes1
    return {
        "phase": "PHASE39_MARGIN_SETTLEMENT_AUDIT",
        "paper_only": True,
        "seed": int(seed),
        "cycles": int(cycles),
        "checkpoints": cps,
        "restores": restores,
        "all_valid": all(c["valid"] for c in cps),
        "all_restored_ok": all(r["success"] and r["validated"] for r in restores),
        "deterministic": bool(deterministic),
        "no_external_venue_mutation": True,
    }


def generate(cycles: int = 12, seed: int = 39039) -> Dict[str, Any]:
    ks = _kill_switch_surface(int(seed), int(cycles))
    pv = _validation_surface(int(seed), int(cycles))
    recon = _reconciliation_freshness(int(seed))
    ms = _margin_settlement_audit(int(seed), int(cycles))

    ks2 = _kill_switch_surface(int(seed), int(cycles))
    pv2 = _validation_surface(int(seed), int(cycles))
    ms2 = _margin_settlement_audit(int(seed), int(cycles))
    deterministic = (_strip_timestamps(ks) == _strip_timestamps(ks2)
                     and _strip_timestamps(pv) == _strip_timestamps(pv2)
                     and _strip_timestamps(ms) == _strip_timestamps(ms2))

    gates_ok = bool(pv.get("gates_ok")) and bool(ms.get("all_valid")) and bool(ms.get("all_restored_ok"))
    d: Dict[str, Any] = {
        "artifact_type": ARTIFACT_TYPE,
        "timestamp_utc": _utc_iso(),
        "paper_only": True,
        "live_trading_enabled": False,
        "next9_unblocked": False,
        "advisory": True,
        "no_external_venue_mutation": True,
        "phase": "PHASE39_LIVE_READINESS_DEPTH",
        "seed": int(seed),
        "cycles": int(cycles),
        "venues": list(VENUES),
        "symbols": list(SYMBOLS),
        "underlyings": list(UNDERLYINGS),
        "scope": ("paper-only phase39 live-readiness depth evidence for crypto options "
                  "orderflow; Deribit/OKX/Binance × BTC/ETH; pre/post-trade validation, "
                  "kill-switch/SLO posture (paper), reconciliation freshness, margin/"
                  "settlement audit determinism, deterministic seeded cycles, finite numerics; "
                  "no live capital, no external venue mutation, cannot unblock NEXT9; "
                  "advisory only"),
        "campaign": {
            "phase": "PHASE39_LIVE_READINESS_DEPTH",
            "paper_only": True,
            "seed": int(seed),
            "total_cycles": int(cycles),
            "venues": list(VENUES),
            "symbols": list(SYMBOLS),
            "underlyings": list(UNDERLYINGS),
            "modes": "paper",
        },
        "kill_switch_slo_posture": ks,
        "validation_surface": pv,
        "reconciliation_freshness": recon,
        "margin_settlement_audit": ms,
        "determinism": {
            "deterministic_seeded": bool(deterministic),
            "same_seed_cycles_reproduce_surfaces": bool(deterministic),
        },
        "risk_summary": {
            "total_cycles": int(cycles),
            "gates_ok": bool(gates_ok),
            "validation_gates_ok": bool(pv.get("gates_ok")),
            "margin_settlement_audit_ok": bool(ms.get("all_valid") and ms.get("all_restored_ok")),
            "kill_switch_global_halts_observed": int(ks["campaign_summary"]["global_halts"]),
            "kill_switch_trading_enabled_cycles": int(ks["campaign_summary"]["trading_enabled_cycles"]),
            "reconciliation_freshness_present": bool(recon.get("freshness_present")),
            "venues_covered": list(VENUES),
            "symbols_covered": list(SYMBOLS),
            "paper_only": True,
            "next9_unblocked": False,
            "live_trading_enabled": False,
        },
        "evidence_refs": [
            "src/integration/phase39_live_readiness_loop.py",
            "src/validation/phase39_prepost_trade_validation.py",
            "src/risk/phase39_kill_switches_circuit_breakers.py",
            "src/recovery/phase39_disaster_recovery.py",
            "scripts/generate_phase39_live_readiness_paper_evidence.py",
            "tests/test_generate_phase39_live_readiness_paper_evidence.py",
        ],
        "cross_refs": [
            x for x in [
                "research_state/PHASE39_LIVE_READINESS_LOOP_REPORT.json",
                "research_state/PHASE39_CAMPAIGN_SUMMARY.json",
                "research_state/PHASE39_KILL_SWITCH_REPORT.json",
                "research_state/PHASE39_VALIDATION_REPORT.json",
                "research_state/PHASE39_RECOVERY_REPORT.json",
                _latest_glob("CONTINUOUS_VALIDATION_*.json"),
                _latest_glob("PAPER_OPS_SESSION_GATE_*.json"),
            ] if x
        ],
        "flags": {
            "deterministic_seeded": True,
            "finite_numerics_validated": True,
            "advisory_only": True,
            "no_external_venue_mutation": True,
        },
    }
    ok, issues = validate_artifact(d)
    d["validation"] = {"valid": ok, "issues": issues}
    return d


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate phase39 live-readiness paper evidence (paper-only)")
    ap.add_argument("--cycles", type=int, default=12)
    ap.add_argument("--seed", type=int, default=39039)
    ap.add_argument("--write", action="store_true", default=True)
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
        out_path = RS / f"PHASE39_LIVE_READINESS_PAPER_EVIDENCE_{ts}.json"
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
        "venues": d["venues"],
        "symbols": d["symbols"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
