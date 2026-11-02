#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys

# Ensure repo root on path
sys.path.insert(0, os.getcwd())

from src.integration.phase36_regime_mm_hedge_loop import LoopConfig, Phase36RegimeMMHedgeLoop


def main() -> int:
    p = argparse.ArgumentParser(description="Run Phase 36 Regime MM Hedge Campaign")
    p.add_argument("--symbols", nargs="*", default=["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"])
    p.add_argument("--venues", nargs="*", default=["deribit", "okx", "bybit", "binance"])
    p.add_argument("--underlyings", nargs="*", default=["BTC", "ETH", "SOL", "XRP"])
    p.add_argument("--expiries", nargs="*", default=["20261107", "20261114", "20261121"])
    p.add_argument("--modes", default="paper")
    p.add_argument("--cycles", type=int, default=20)
    p.add_argument("--seed", type=int, default=123456)
    p.add_argument("--enforce-gates", action="store_true", default=True)
    p.add_argument("--outdir", default="research_state")
    args = p.parse_args()

    cfg = LoopConfig(
        symbols=args.symbols,
        venues=args.venues,
        underlyings=args.underlyings,
        expiries=args.expiries,
        modes=args.modes,
        cycles=args.cycles,
        seed=args.seed,
        enforce_gates=args.enforce_gates,
        outdir=args.outdir,
        paper_only=(args.modes != "live"),
    )
    loop = Phase36RegimeMMHedgeLoop(cfg)
    res = loop.run()
    print("PHASE36_OK", res["aggregate"]["n_cycles"], res["aggregate"]["stress_detected_cycles"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
