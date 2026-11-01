#!/usr/bin/env python3
"""
Run Phase 35 liquidity routing campaign (paper-only by default).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure repo root in path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.integration.phase35_liquidity_routing_loop import LiquidityRoutingLoop, LiquidityRoutingLoopConfig


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 35 Liquidity Routing Campaign")
    p.add_argument("--symbols", nargs="*", default=["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"])
    p.add_argument("--venues", nargs="*", default=["deribit", "okx", "bybit", "binance"])
    p.add_argument("--underlyings", nargs="*", default=["BTC", "ETH", "SOL", "XRP"])
    p.add_argument("--expiries", nargs="*", default=["1W", "2W", "1M"])
    p.add_argument("--modes", default="paper", choices=["paper", "live"])
    p.add_argument("--cycles", type=int, default=15)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--enforce-gates", action="store_true", default=True)
    p.add_argument("--outdir", default="research_state")
    args = p.parse_args()

    if args.modes == "live" and args.enforce_gates:
        print("LIVE mode requested but hard-gated by enforce-gates=true; forcing PAPER-ONLY", file=sys.stderr)
        modes = ["paper"]
    else:
        modes = [args.modes]

    cfg = LiquidityRoutingLoopConfig(
        seed=args.seed,
        paper_only=(modes[0] == "paper"),
        live_enabled=False,
        cycles=args.cycles,
        underlyings=tuple(args.underlyings),
        venues=tuple(args.venues),
        enforce_gates=bool(args.enforce_gates),
    )
    loop = LiquidityRoutingLoop(cfg, seed=args.seed)
    res = loop.generate_report(args.outdir)
    print(json.dumps({"status": "ok", "paper_only": True, "report": res}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
