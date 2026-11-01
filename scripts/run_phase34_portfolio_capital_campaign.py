#!/usr/bin/env python3
"""
Run Phase 34 Portfolio + Capital Campaign.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.integration.phase34_portfolio_capital_loop import (
    Phase34PortfolioCapitalLoop,
    Phase34PortfolioCapitalLoopConfig34,
)


def main() -> int:
    p = argparse.ArgumentParser(description="Phase 34 Portfolio Capital Campaign")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--cycles", type=int, default=10)
    p.add_argument("--underlyings", type=str, default="BTC,ETH,SOL,XRP")
    p.add_argument("--venues", type=str, default="deribit,okx,bybit,binance")
    p.add_argument("--expiries", type=str, default="7D,30D,90D")
    p.add_argument("--modes", type=str, default="paper")
    p.add_argument("--outdir", type=str, default="research_state")
    p.add_argument("--enforce-gates", action="store_true", default=True)
    args = p.parse_args()

    if args.modes != "paper":
        raise ValueError("Live modes hard-gated; only 'paper' allowed in this build")
    cfg = Phase34PortfolioCapitalLoopConfig34(
        seed=args.seed,
        paper_only=True,
        cycles=args.cycles,
        underlyings=tuple(s.strip() for s in args.underlyings.split(",") if s.strip()),
        venues=tuple(s.strip() for s in args.venues.split(",") if s.strip()),
        expiries=tuple(s.strip() for s in args.expiries.split(",") if s.strip()),
        enforce_gates=bool(args.enforce_gates),
    )
    loop = Phase34PortfolioCapitalLoop(config=cfg, seed=args.seed)
    camp = loop.run_campaign(cycles=args.cycles)
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    paths = loop.generate_report(str(out))
    summary = {
        "phase": "34",
        "seed": args.seed,
        "cycles": args.cycles,
        "paper_only": True,
        "campaign": camp,
        "reports": paths,
    }
    (out / "PHASE34_RUN_SUMMARY.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({"ok": True, "phase": "34", "cycles": args.cycles, "paper_only": True, "reports": paths}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
