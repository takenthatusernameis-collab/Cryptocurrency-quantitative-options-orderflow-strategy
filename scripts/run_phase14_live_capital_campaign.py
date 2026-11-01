#!/usr/bin/env python3
"""Run Phase 14 Live Capital Campaign (crypto options + orderflow)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from src.deployment.phase14_campaign import Phase14Campaign


def main() -> int:
    p = argparse.ArgumentParser(description="Run Phase 14 live-capital campaign")
    p.add_argument("--symbols", nargs="+", default=["BTC", "ETH"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--venues", nargs="+", default=["deribit", "okx", "binance"])
    p.add_argument("--paper-only", action="store_true", default=True)
    p.add_argument("--outdir", type=str, default="research_state")
    args = p.parse_args()

    if not args.paper_only:
        print("ERROR: paper-only required for Phase 14", file=sys.stderr)
        return 2

    camp = Phase14Campaign(
        symbols=tuple(args.symbols),
        seed=args.seed,
        venues=tuple(args.venues),
        paper_only=True,
        outdir=Path(args.outdir),
    )
    res = camp.run()
    print(json.dumps({
        "status": res.get("status"),
        "artifacts": res.get("master_report", {}).get("artifacts", []),
        "counts": res.get("master_report", {}).get("counts", {}),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
