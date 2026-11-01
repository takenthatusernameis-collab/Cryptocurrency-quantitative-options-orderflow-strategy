#!/usr/bin/env python3
"""
Phase 31: Live Vol Surface Arbitrage Campaign Runner (crypto options + orderflow).

Integrates Phase 30 + Phase 31 (live deployment, continuous validation, production telemetry)
+ Phase 18 observability + Phase 24 router. Paper-only by default, live hard-gated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.execution.phase31_live_vol_arb_loop import LiveVolArbLoop, LiveVolArbLoopConfig31


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 31 Live Vol Surface Arbitrage Campaign")
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
    config = LiveVolArbLoopConfig31(
        seed=args.seed,
        paper_only=True,
        cycles=args.cycles,
        underlyings=tuple(args.underlyings),
        venues=tuple(args.venues),
        expiries=tuple(args.expiries),
        enforce_gates=bool(args.enforce_gates),
    )
    loop = LiveVolArbLoop(config=config, seed=args.seed)
    result = loop.run_campaign(cycles=args.cycles)

    loop.generate_report(outdir=args.outdir)

    summary = {
        "phase": 31,
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
        "total_allocations": result.get("total_allocations", 0),
        "total_hedge_routes": result.get("total_hedge_routes", 0),
        "total_venue_routed": sum(r.get("venue_routed", 0) for r in result.get("reports", [])),
        "kill_switch_active": loop.deployment.kill_switch.active,
        "reports": result.get("reports", []),
    }
    sjson = Path(args.outdir) / "PHASE31_CAMPAIGN_SUMMARY.json"
    smd = Path(args.outdir) / "PHASE31_CAMPAIGN_SUMMARY.md"
    sjson.write_text(json.dumps(summary, indent=2))
    smd.write_text(
        f"# PHASE31_CAMPAIGN_SUMMARY\n\n"
        f"Status: {summary['status']}\n"
        f"Paper-only: {summary['paper_only']}\n"
        f"Cycles: {summary['cycles']}\n"
        f"Final PnL USD: {summary['final_pnl_usd']:.2f}\n"
        f"Final drawdown: {summary['final_drawdown_pct']:.4f}\n"
        f"Total signals: {summary['total_signals']}\n"
        f"Kill switch: {summary['kill_switch_active']}\n"
    )
    print(
        f"PHASE31 OK: cycles={args.cycles}, pnl={summary['final_pnl_usd']:.2f}, "
        f"signals={summary['total_signals']}, kill_switch={summary['kill_switch_active']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
