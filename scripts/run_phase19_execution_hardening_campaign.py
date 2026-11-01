#!/usr/bin/env python3
"""Run Phase 19: Live-Capital Execution Hardening (paper->live gate, OMS, execution risk)."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from src.alpha.phase17_campaign import Phase17Campaign, _assert_no_nan_inf
from src.analytics.phase18_attribution import Phase18Attribution
from src.analytics.phase18_greeks_snapshot import Phase18GreeksSnapshot
from src.monitoring.phase18_observability import Phase18Observability
from src.execution.phase19_paper_live_gate import PaperLiveGate
from src.execution.phase19_order_manager import OrderManager
from src.risk.phase19_execution_risk import ExecutionRiskEngine
from src.telemetry.serialization import serialize_metrics_strict, assert_json_valid


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> str | None:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return sha
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=5)
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 19 execution hardening campaign")
    p.add_argument("--symbols", nargs="*", default=["BTC", "ETH", "SOL", "XRP", "ADA"])
    p.add_argument("--venues", nargs="*", default=["deribit", "okx", "binance", "bybit", "bitget"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cycles", type=int, default=5)
    p.add_argument("--paper-only", action="store_true", default=True)
    p.add_argument("--enforce-gates", action="store_true", default=True)
    p.add_argument("--outdir", type=str, default=str(REPO_ROOT / "research_state"))
    args = p.parse_args()

    if not args.paper_only:
        raise SystemExit("paper-only required for Phase 19")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Integrate Phase 17
    camp17 = Phase17Campaign(symbols=tuple(args.symbols), seed=args.seed, venues=tuple(args.venues),
                             paper_only=True, outdir=outdir, cycles=args.cycles)
    res17 = camp17.run()
    intents = camp17.intents
    confirmations = camp17.confirmations

    # Phase 18 for observability context
    attr = Phase18Attribution(seed=args.seed, paper_only=True)
    obs = Phase18Observability(seed=args.seed, paper_only=True)
    greeks_snap = Phase18GreeksSnapshot(seed=args.seed, paper_only=True)
    rep_attr = attr.generate_report(intents, artifacts=res17.get("artifacts"))
    rep_obs = obs.generate_report(intents, confirmations, kill_switch_triggered=bool(res17.get("killed", False)),
                                   kill_count=1 if res17.get("killed") else 0, venues=tuple(args.venues))
    rep_greeks = greeks_snap.generate_report(intents)

    # Phase 19 components
    gate = PaperLiveGate(paper_only=True, seed=args.seed)
    oms = OrderManager(paper_only=True, seed=args.seed, venues=tuple(args.venues))
    risk_eng = ExecutionRiskEngine(paper_only=True, seed=args.seed)

    # Evaluate gate in paper state (missing acks -> blocked for live, allowed for paper)
    state = {"equity": 150000.0, "total_notional": sum(float(i.size_usd) for i in intents[:10]) if intents else 50000.0,
             "drawdown_pct": 0.01, "capital_ack": False, "risk_ack": False, "manual_approval": False,
             "connectivity_ok": False, "compliance_ok": False}
    decision = gate.evaluate(state=state, intents_count=len(intents), confirmations_count=len([c for c in confirmations if getattr(c, 'confirmed', False)]))

    # Process intents through OMS + risk
    orders_created = 0
    for idx, intent in enumerate(intents[: min(20, len(intents))]):
        intent_d = {
            "intent_id": getattr(intent, "intent_id"),
            "symbol": getattr(intent, "symbol"),
            "side": getattr(intent, "side"),
            "qty": getattr(intent, "qty"),
            "order_type": getattr(intent, "order_type"),
            "limit_price": getattr(intent, "size_usd", 10000.0) / max(getattr(intent, "qty", 0.01), 1e-12),
            "delta_est": getattr(intent, "delta_est", 0.0),
            "vega_est": getattr(intent, "vega_est", 0.0),
            "gamma_est": getattr(intent, "gamma_est", 0.0),
            "theta_est": getattr(intent, "theta_est", 0.0),
            "slippage_bps_est": 2.0,
        }
        pre = risk_eng.pre_trade_check(intent_d, state=state, venue=args.venues[idx % len(args.venues)])
        if not pre["approved"] and args.enforce_gates:
            # In paper mode we still record; OMS will reject
            o = oms.create_order(intent_d, venue=args.venues[idx % len(args.venues)])
            oms.reject(o.order_id, reason="pre_trade_risk_reject")
        else:
            o = oms.create_order(intent_d, venue=args.venues[idx % len(args.venues)])
            oms.submit(o.order_id)
            oms.simulate_fill(o.order_id)
        orders_created += 1

    rep_gate = gate.generate_report(decision)
    rep_oms = oms.generate_report()
    rep_risk = risk_eng.generate_report()

    sha = _git_sha()
    for rep in [rep_gate, rep_oms, rep_risk]:
        rep["git_sha"] = sha
        rep["campaign_id"] = camp17.campaign_id
        rep["venues"] = list(args.venues)
        rep["symbols"] = list(args.symbols)
        rep["seed"] = int(args.seed)
        rep["timestamp"] = _utc_now()
        _assert_no_nan_inf(rep, rep.get("report", "unknown"))
        assert_json_valid(rep)

    paths: List[str] = []
    mapping = [
        ("PHASE19_PAPER_LIVE_GATE_REPORT", rep_gate),
        ("PHASE19_ORDER_MANAGEMENT_REPORT", rep_oms),
        ("PHASE19_EXECUTION_RISK_REPORT", rep_risk),
    ]
    for name, rep in mapping:
        rep_ser = serialize_metrics_strict(rep)
        p_json = outdir / f"{name}.json"
        p_md = outdir / f"{name}.md"
        p_json.write_text(json.dumps(rep_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
        lines = [f"# {name}", f"Timestamp (UTC): {rep_ser.get('timestamp')}", f"Campaign ID: {rep_ser.get('campaign_id')}",
                 f"Seed: {rep_ser.get('seed')}", f"Symbols: {', '.join(rep_ser.get('symbols', []))}",
                 f"Paper-only: True", f"Git SHA: {rep_ser.get('git_sha')}", ""]
        if "reconciliation" in rep_ser:
            lines.append("## Reconciliation")
            for k, v in rep_ser["reconciliation"].items():
                lines.append(f"- {k}: {v}")
            lines.append("")
        elif "limits" in rep_ser:
            lines.append("## Limits")
            for k, v in rep_ser["limits"].items():
                lines.append(f"- {k}: {v}")
            lines.append("")
        elif "breach_count" in rep_ser or "breaches" in rep_ser:
            lines.append(f"## Breaches: {rep_ser.get('breach_count', len(rep_ser.get('breaches', [])))}")
            lines.append("")
        p_md.write_text("\n".join(lines), encoding="utf-8")
        paths.extend([str(p_json), str(p_md)])

    master = {
        "report": "PHASE19_EXECUTION_HARDENING_MASTER_REPORT",
        "campaign": "phase19_execution_hardening",
        "campaign_id": camp17.campaign_id,
        "timestamp": _utc_now(),
        "seed": args.seed,
        "symbols": list(args.symbols),
        "venues": list(args.venues),
        "paper_only": True,
        "status": "completed",
        "phase17_status": res17.get("status"),
        "gate_live_allowed": rep_gate.get("decision", {}).get("live_allowed") if isinstance(rep_gate.get("decision"), dict) else False,
        "gate_blocked_reasons": (rep_gate.get("decision") or {}).get("blocked_reasons") if isinstance(rep_gate.get("decision"), dict) else [],
        "git_sha": sha,
        "artifacts": [
            "PHASE19_PAPER_LIVE_GATE_REPORT.json",
            "PHASE19_PAPER_LIVE_GATE_REPORT.md",
            "PHASE19_ORDER_MANAGEMENT_REPORT.json",
            "PHASE19_ORDER_MANAGEMENT_REPORT.md",
            "PHASE19_EXECUTION_RISK_REPORT.json",
            "PHASE19_EXECUTION_RISK_REPORT.md",
        ],
        "counts": {
            "intents": len(intents),
            "confirmations": len(confirmations),
            "orders_processed": orders_created,
            "orders_total": rep_oms.get("order_count", 0),
        },
    }
    _assert_no_nan_inf(master, "phase19_master")
    master_ser = serialize_metrics_strict(master)
    m_json = outdir / "PHASE19_EXECUTION_HARDENING_MASTER_REPORT.json"
    m_md = outdir / "PHASE19_EXECUTION_HARDENING_MASTER_REPORT.md"
    m_json.write_text(json.dumps(master_ser, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    m_md.write_text("\n".join([f"# {master_ser['report']}", f"Timestamp: {master_ser['timestamp']}", f"Status: {master_ser['status']}", ""]), encoding="utf-8")
    paths.extend([str(m_json), str(m_md)])

    print(json.dumps({"status": "ok", "artifacts": paths, "campaign_id": camp17.campaign_id}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
