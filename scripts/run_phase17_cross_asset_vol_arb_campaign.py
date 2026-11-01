#!/usr/bin/env python3
"""Run Phase 17 Cross-Asset Options Volatility Surface Arbitrage + Orderflow
Confirmation Campaign (crypto options + orderflow). Default PAPER-ONLY."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.alpha.phase17_campaign import Phase17Campaign


def main() -> int:
    p = argparse.ArgumentParser(description="Run Phase 17 cross-asset vol surface arb + orderflow confirmation campaign")
    p.add_argument("--symbols", nargs="+", default=["BTC", "ETH", "SOL"])
    p.add_argument("--venues", nargs="+", default=["deribit", "okx", "binance", "bybit", "bitget"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--paper-only", action="store_true", default=True)
    p.add_argument("--no-paper-only", dest="paper_only", action="store_false")
    p.add_argument("--outdir", type=str, default="research_state")
    p.add_argument("--cycles", type=int, default=5)
    args = p.parse_args()

    if not args.paper_only:
        print("ERROR: paper-only required for Phase 17 (live path hard-gated)", file=sys.stderr)
        return 2

    campaign = Phase17Campaign(
        symbols=tuple(args.symbols),
        seed=args.seed,
        venues=tuple(args.venues),
        paper_only=True,
        outdir=Path(args.outdir),
        cycles=args.cycles,
    )
    res = campaign.run()
    mr = res.get("master_report", {})
    print(json.dumps({
        "status": res.get("status"),
        "campaign_id": res.get("campaign_id"),
        "seed": mr.get("seed"),
        "symbols": mr.get("symbols"),
        "venues": mr.get("venues"),
        "paper_only": mr.get("paper_only"),
        "cycles": mr.get("cycles"),
        "counts": mr.get("counts"),
        "backtest": res.get("backtest"),
        "killed": res.get("killed"),
        "kill_reason": res.get("kill_reason"),
        "artifacts": mr.get("artifacts"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
