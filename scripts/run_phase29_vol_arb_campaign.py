#!/usr/bin/env python3
"""
Phase 29 campaign runner: Cross-Venue Options Volatility Arbitrage & Delta-Neutral MM Engine
Integrates Phase 17-28, paper-only gated.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Ensure src on path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.arbitrage.phase29_vol_arb import OptionsVolArbEngine, VolArbConfig
from src.risk.phase29_delta_neutral_hedge import DeltaNeutralHedgeEngine, HedgeConfig
from src.execution.phase29_vol_arb_paper_loop import VolArbPaperLoop, VolArbLoopConfig


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    p = argparse.ArgumentParser(description="Run Phase 29 Vol Arb Campaign")
    p.add_argument("--symbols", nargs="*", default=["BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"])
    p.add_argument("--venues", nargs="*", default=["deribit", "okx", "bybit", "binance"])
    p.add_argument("--underlyings", nargs="*", default=["BTC", "ETH", "SOL", "XRP"])
    p.add_argument("--expiries", nargs="*", default=["7D", "30D", "90D"])
    p.add_argument("--modes", nargs="*", default=["paper"])
    p.add_argument("--cycles", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--enforce-gates", action="store_true", default=True)
    p.add_argument("--outdir", default="research_state")
    args = p.parse_args()

    if "live" in args.modes and not os.environ.get("PHASE29_LIVE_CONFIRMED"):
        print("LIVE mode requested but PHASE29_LIVE_CONFIRMED not set; forcing paper-only", flush=True)
        args.modes = ["paper"]

    loop_cfg = VolArbLoopConfig(
        seed=int(args.seed),
        paper_only=True,
        cycles=int(args.cycles),
        underlyings=tuple(args.underlyings),
        venues=tuple(args.venues),
        enforce_gates=bool(args.enforce_gates),
    )
    loop = VolArbPaperLoop(config=loop_cfg, seed=int(args.seed))
    loop_rep = loop.generate_report(outdir=args.outdir)

    # Master report
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    master = {
        "phase": "29_vol_arb_master",
        "timestamp": _utc_now(),
        "args": vars(args),
        "loop": {
            "cycles": len(loop_rep.get("cycles", [])),
            "totals": loop_rep.get("totals", {}),
            "status": loop_rep.get("status"),
        },
        "reports": [
            "PHASE29_VOL_ARB_REPORT.json",
            "PHASE29_DELTA_NEUTRAL_HEDGE_REPORT.json",
            "PHASE29_VOL_ARB_PAPER_LOOP_REPORT.json",
            "PHASE29_VOL_ARB_MASTER_REPORT.json",
        ],
        "status": "ok",
        "paper_only": True,
        "gate_green_required": True,
    }
    (outdir / "PHASE29_VOL_ARB_MASTER_REPORT.json").write_text(json.dumps(master, indent=2))
    (outdir / "PHASE29_VOL_ARB_MASTER_REPORT.md").write_text(
        f"# PHASE29_VOL_ARB_MASTER_REPORT\n\nTimestamp: {master['timestamp']}\nCycles: {master['loop']['cycles']}\nSignals: {loop_rep.get('totals',{}).get('signals')}\nFills: {loop_rep.get('totals',{}).get('fills')}\nNet PnL: {loop_rep.get('totals',{}).get('net_pnl')}\nStatus: {master['status']}\n"
    )
    # Also ensure individual reports exist
    loop.vol_arb.generate_report(outdir=args.outdir)
    loop.hedge.generate_report(outdir=args.outdir)
    print(json.dumps({"status": "ok", "master": str(outdir / "PHASE29_VOL_ARB_MASTER_REPORT.json")}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
