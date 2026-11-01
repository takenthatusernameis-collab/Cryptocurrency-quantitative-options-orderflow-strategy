#!/usr/bin/env python3
"""
Phase 30: Vol Surface Arbitrage Campaign Runner (crypto options + orderflow).
Integrates Phase 17-29, paper-only by default, hard-gated for live.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from src.execution.phase30_vol_arb_paper_loop import VolSurfaceArbPaperLoop


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 30 Vol Surface Arbitrage Campaign")
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
    loop = VolSurfaceArbPaperLoop(seed=args.seed)
    result = loop.run_campaign(cycles=args.cycles)

    # Write campaign summary
    summary = {
        "phase": 30,
        "status": "ok",
        "paper_only": True,
        "modes": args.modes,
        "cycles": args.cycles,
        "seed": args.seed,
        "underlyings": args.underlyings,
        "venues": args.venues,
        "expiries": args.expiries,
        "reports": result.get("reports", []),
    }
    sjson = Path(args.outdir) / "PHASE30_CAMPAIGN_SUMMARY.json"
    smd = Path(args.outdir) / "PHASE30_CAMPAIGN_SUMMARY.md"
    sjson.write_text(json.dumps(summary, indent=2))
    smd.write_text(f"# PHASE30_CAMPAIGN_SUMMARY\n\nStatus: ok\nPaper-only: true\nCycles: {args.cycles}\n")
    print(f"PHASE30 OK: cycles={args.cycles}, reports={len(result.get('reports', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
