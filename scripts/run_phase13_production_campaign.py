#!/usr/bin/env python3
"""CLI to run Phase 13 production deployment, continuous monitoring,
auto-healing and model governance campaign (crypto options + orderflow).

Usage:
    python scripts/run_phase13_production_campaign.py run --seed 42
    python scripts/run_phase13_production_campaign.py status
"""
from __future__ import annotations

import json
import sys
from typing import Any, Dict, Optional

try:  # package context
    from src.deployment.phase13_campaign import Phase13Campaign
except ImportError:  # fallback when cwd is repo root and src is on path
    from phase13_campaign import Phase13Campaign  # type: ignore


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Run Phase 13 production deployment campaign")
    parser.add_argument("command", choices=["run", "status"],
                        help="Command to execute")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--symbols", type=str, default="BTC,ETH")
    parser.add_argument("--venues", type=str, default="deribit,okx,binance")
    parser.add_argument("--paper-only", action="store_true", default=True)
    parser.add_argument("--live", action="store_true",
                        help="Attempt live mode (still paper-only gated by default)")
    args = parser.parse_args(argv)

    symbols = tuple(s.strip().upper() for s in args.symbols.split(",") if s.strip())
    venues = tuple(v.strip().lower() for v in args.venues.split(",") if v.strip())
    paper_only = bool(args.paper_only) and not args.live

    try:
        if args.command == "run":
            camp = Phase13Campaign(symbols=symbols, seed=args.seed,
                                   venues=venues, paper_only=paper_only)
            res = camp.run()
            out = {
                "status": "completed",
                "campaign_id": camp.campaign_id,
                "seed": camp.seed,
                "symbols": list(camp.symbols),
                "venues": list(camp.venues),
                "paper_only": camp.paper_only,
                "counts": camp.counts,
                "artifacts": camp.artifacts,
                "master_report_artifact": res.get("master_report_artifact"),
            }
            print(json.dumps(out, indent=2, allow_nan=False))
            return 0
        elif args.command == "status":
            print(json.dumps({
                "status": "no_campaign_run",
                "command": "run --seed 42",
            }, indent=2, allow_nan=False))
            return 0
    except Exception as exc:  # pragma: no cover - CLI boundary
        print(json.dumps({"error": str(exc)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
