#!/usr/bin/env python3
"""
Phase 32: Orderflow Vol Surface Arbitrage Campaign Runner (crypto options +
orderflow).

Integrates Phase 31 live vol arb loop + Phase 32 orderflow alpha integration,
execution quality, and live risk controls. Paper-only by default, live hard-gated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.integration.phase32_vol_arb_orderflow_loop import (
    VolArbOrderflowLoop,
    VolArbOrderflowLoopConfig32,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Phase 32 Orderflow Vol Surface Arbitrage Campaign"
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
    config = VolArbOrderflowLoopConfig32(
        seed=args.seed,
        paper_only=True,
        cycles=args.cycles,
        underlyings=tuple(args.underlyings),
        venues=tuple(args.venues),
        expiries=tuple(args.expiries),
        enforce_gates=bool(args.enforce_gates),
    )
    loop = VolArbOrderflowLoop(config=config, seed=args.seed)
    result = loop.run_campaign(cycles=args.cycles)
    loop.generate_report(outdir=args.outdir)
    loop.orderflow.generate_report(outdir=args.outdir)
    loop.execution.generate_report(outdir=args.outdir)
    loop.risk.generate_report(outdir=args.outdir)

    summary = {
        "phase": 32,
        "status": "ok",
        "paper_only": True,
        "modes": args.modes,
        "cycles": args.cycles,
        "seed": args.seed,
        "underlyings": args.underlyings,
        "venues": args.venues,
        "expiries": args.expiries,
        "enforce_gates": bool(args.enforce_gates),
        "final_pnl_usd": result.get("final_pnl_usd", 0.0),
        "final_drawdown_pct": result.get("final_drawdown_pct", 0.0),
        "total_signals": result.get("total_signals", 0),
        "total_orderflow_confirmed": result.get("total_orderflow_confirmed", 0),
        "total_allocations": result.get("total_allocations", 0),
        "total_venue_routed": result.get("total_venue_routed", 0),
        "kill_switch_active": result.get("kill_switch_active", False),
        "reports": result.get("reports", []),
    }
    sjson = Path(args.outdir) / "PHASE32_CAMPAIGN_SUMMARY.json"
    smd = Path(args.outdir) / "PHASE32_CAMPAIGN_SUMMARY.md"
    sjson.write_text(json.dumps(summary, indent=2))
    smd.write_text(
        f"# PHASE32_CAMPAIGN_SUMMARY\n\n"
        f"Status: {summary['status']}\n"
        f"Paper-only: {summary['paper_only']}\n"
        f"Cycles: {summary['cycles']}\n"
        f"Final PnL USD: {summary['final_pnl_usd']:.2f}\n"
        f"Final drawdown: {summary['final_drawdown_pct']:.4f}\n"
        f"Total signals: {summary['total_signals']}\n"
        f"Total orderflow confirmed: {summary['total_orderflow_confirmed']}\n"
        f"Kill switch: {summary['kill_switch_active']}\n"
    )
    print(
        f"PHASE32 OK: cycles={args.cycles}, pnl={summary['final_pnl_usd']:.2f}, "
        f"signals={summary['total_signals']}, "
        f"orderflow_confirmed={summary['total_orderflow_confirmed']}, "
        f"kill_switch={summary['kill_switch_active']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
