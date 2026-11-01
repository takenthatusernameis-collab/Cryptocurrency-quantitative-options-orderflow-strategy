#!/usr/bin/env python3
"""
Phase 33: Capital + Orderflow Campaign Runner (crypto options +
orderflow).

Integrates Phase 31 live deployment + Phase 32 execution/risk + Phase 33
adaptive orderflow hedge, live capital rollout, and venue liquidity sweep.
Paper-only by default, live hard-gated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.integration.phase33_capital_orderflow_loop import (
    Phase33CapitalOrderflowLoop,
    Phase33CapitalOrderflowLoopConfig33,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Phase 33 Capital + Orderflow Campaign"
    )
    parser.add_argument("--symbols", nargs="*", default=["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT"])
    parser.add_argument("--venues", nargs="*", default=["deribit", "okx", "bybit", "binance"])
    parser.add_argument("--underlyings", nargs="*", default=["BTC", "ETH", "SOL", "XRP"])
    parser.add_argument("--expiries", nargs="*", default=["7D", "30D", "90D"])
    parser.add_argument("--modes", default="paper", help="paper/live (live hard-gated)")
    parser.add_argument("--cycles", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--enforce-gates", action="store_true", default=True)
    parser.add_argument("--outdir", default="research_state")
    args = parser.parse_args()

    if args.modes.lower() != "paper":
        raise SystemExit("LIVE MODE HARD-GATED: only paper mode allowed")

    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    config = Phase33CapitalOrderflowLoopConfig33(
        seed=args.seed,
        paper_only=True,
        cycles=args.cycles,
        underlyings=tuple(args.underlyings),
        venues=tuple(args.venues),
        expiries=tuple(args.expiries),
        enforce_gates=bool(args.enforce_gates),
    )
    loop = Phase33CapitalOrderflowLoop(config=config, seed=args.seed)
    result = loop.run_campaign(cycles=args.cycles)
    loop.generate_report(outdir=args.outdir)
    loop.hedge.generate_report(outdir=args.outdir)
    loop.rollout.generate_report(outdir=args.outdir)
    loop.sweep.generate_report(outdir=args.outdir)
    loop.execution.generate_report(outdir=args.outdir)

    summary = {
        "phase": 33,
        "status": "ok",
        "paper_only": True,
        "modes": args.modes,
        "cycles": args.cycles,
        "seed": args.seed,
        "underlyings": args.underlyings,
        "venues": args.venues,
        "expiries": args.expiries,
        "enforce_gates": bool(args.enforce_gates),
        "final_phase": result.get("final_phase", "canary"),
        "final_pnl_usd": result.get("final_pnl_usd", 0.0),
        "final_drawdown_pct": result.get("final_drawdown_pct", 0.0),
        "total_signals": result.get("total_signals", 0),
        "total_orderflow_confirmed": result.get("total_orderflow_confirmed", 0),
        "total_hedges_computed": result.get("total_hedges_computed", 0),
        "total_venues_rotated": result.get("total_venues_rotated", 0),
        "total_sweeps_routed": result.get("total_sweeps_routed", 0),
        "total_swept_notional_usd": result.get("total_swept_notional_usd", 0.0),
        "capital_allocated_usd": result.get("capital_allocated_usd", 0.0),
        "kill_switch_active": result.get("kill_switch_active", False),
        "reports": result.get("reports", []),
    }
    sjson = Path(args.outdir) / "PHASE33_CAMPAIGN_SUMMARY.json"
    smd = Path(args.outdir) / "PHASE33_CAMPAIGN_SUMMARY.md"
    sjson.write_text(json.dumps(summary, indent=2))
    smd.write_text(
        f"# PHASE33_CAMPAIGN_SUMMARY\n\n"
        f"Status: {summary['status']}\n"
        f"Paper-only: {summary['paper_only']}\n"
        f"Cycles: {summary['cycles']}\n"
        f"Final phase: {summary['final_phase']}\n"
        f"Final PnL USD: {summary['final_pnl_usd']:.2f}\n"
        f"Final drawdown: {summary['final_drawdown_pct']:.4f}\n"
        f"Total signals: {summary['total_signals']}\n"
        f"Total orderflow confirmed: {summary['total_orderflow_confirmed']}\n"
        f"Total hedges computed: {summary['total_hedges_computed']}\n"
        f"Total venues rotated: {summary['total_venues_rotated']}\n"
        f"Total sweeps routed: {summary['total_sweeps_routed']}\n"
        f"Total swept notional USD: {summary['total_swept_notional_usd']:.2f}\n"
        f"Kill switch: {summary['kill_switch_active']}\n"
    )
    print(
        f"PHASE33 OK: cycles={args.cycles}, phase={summary['final_phase']}, "
        f"pnl={summary['final_pnl_usd']:.2f}, signals={summary['total_signals']}, "
        f"hedges={summary['total_hedges_computed']}, sweeps={summary['total_sweeps_routed']}, "
        f"kill_switch={summary['kill_switch_active']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
