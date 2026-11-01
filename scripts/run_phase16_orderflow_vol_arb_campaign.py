#!/usr/bin/env python3
"""Run Phase 16 Orderflow Signal Fusion + Cross-Asset Options Vol Surface Arb Campaign."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.alpha.phase16_campaign import Phase16Campaign


def main() -> int:
    p = argparse.ArgumentParser(description="Run Phase 16 orderflow + vol surface arb campaign")
    p.add_argument("--symbols", nargs="+", default=["BTC", "ETH"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--venues", nargs="+", default=["deribit", "okx", "binance"])
    p.add_argument("--paper-only", action="store_true", default=True)
    p.add_argument("--outdir", type=str, default="research_state")
    p.add_argument("--cycles", type=int, default=5)
    args = p.parse_args()

    if not args.paper_only:
        print("ERROR: paper-only required for Phase 16", file=sys.stderr)
        return 2

    campaign = Phase16Campaign(
        symbols=tuple(args.symbols),
        seed=args.seed,
        venues=tuple(args.venues),
        paper_only=True,
        outdir=Path(args.outdir),
        cycles=args.cycles,
    )
    res = campaign.run()
    print(json.dumps({
        "status": res.get("status"),
        "campaign_id": res.get("campaign_id"),
        "seed": res.get("master_report", {}).get("seed"),
        "symbols": res.get("master_report", {}).get("symbols"),
        "venues": res.get("master_report", {}).get("venues"),
        "paper_only": res.get("master_report", {}).get("paper_only"),
        "counts": res.get("master_report", {}).get("counts"),
        "artifacts": res.get("master_report", {}).get("artifacts"),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
