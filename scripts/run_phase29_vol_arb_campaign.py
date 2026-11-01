#!/usr/bin/env python3
"""
Phase 29: Cross-Venue Options Volatility Arbitrage & Delta-Neutral Market Making Campaign
Crypto options + orderflow. Paper-only by default. Hard gates for live paths.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.execution.phase29_vol_arb_paper_loop import VolArbPaperLoop, VolArbLoopConfig


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def main() -> int:
    p = argparse.ArgumentParser(description="Run Phase 29 vol arb campaign")
    p.add_argument("--symbols", nargs="*", default=None)
    p.add_argument("--venues", nargs="*", default=["deribit", "okx", "bybit", "binance"])
    p.add_argument("--underlyings", nargs="*", default=["BTC", "ETH", "SOL", "XRP"])
    p.add_argument("--expiries", nargs="*", default=["7D", "30D", "90D"])
    p.add_argument("--modes", nargs="*", default=["paper"])
    p.add_argument("--cycles", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--enforce-gates", action="store_true", default=True)
    p.add_argument("--outdir", default="research_state")
    args = p.parse_args()

    mode = args.modes[0] if args.modes else "paper"
    if mode != "paper":
        raise ValueError("Phase 29: live mode hard-gated. Only 'paper' allowed by default.")

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    cfg = VolArbLoopConfig(
        seed=int(args.seed),
        paper_only=True,
        cycles=int(args.cycles),
        underlyings=tuple(args.underlyings),
        venues=tuple(args.venues),
        enforce_gates=bool(args.enforce_gates),
    )
    loop = VolArbPaperLoop(config=cfg, seed=int(args.seed))
    loop_rep = loop.generate_report(outdir=str(outdir))
    loop.vol_arb.generate_report(outdir=str(outdir))
    loop.hedge.generate_report(outdir=str(outdir))

    master = {
        "phase": "29_vol_arb_master",
        "timestamp": _utc_now(),
        "status": "ok",
        "paper_only": True,
        "config": {
            "underlyings": list(args.underlyings),
            "venues": list(args.venues),
            "expiries": list(args.expiries),
            "cycles": int(args.cycles),
            "seed": int(args.seed),
        },
        "loop_totals": loop_rep.get("totals", {}),
        "artifacts": [
            "PHASE29_VOL_ARB_REPORT.json",
            "PHASE29_VOL_ARB_REPORT.md",
            "PHASE29_DELTA_NEUTRAL_HEDGE_REPORT.json",
            "PHASE29_DELTA_NEUTRAL_HEDGE_REPORT.md",
            "PHASE29_VOL_ARB_PAPER_LOOP_REPORT.json",
            "PHASE29_VOL_ARB_PAPER_LOOP_REPORT.md",
            "PHASE29_VOL_ARB_MASTER_REPORT.json",
        ],
    }
    (outdir / "PHASE29_VOL_ARB_MASTER_REPORT.json").write_text(json.dumps(master, indent=2))
    md = []
    md.append("# Phase 29 Vol Arb Master Report")
    md.append("")
    md.append(f"- Timestamp: {master['timestamp']}")
    md.append(f"- Status: {master['status']}")
    md.append(f"- Paper only: true")
    md.append(f"- Cycles: {master['config']['cycles']}")
    md.append(f"- Net PnL: {master['loop_totals'].get('net_pnl')}")
    md.append("")
    (outdir / "PHASE29_VOL_ARB_MASTER_REPORT.md").write_text("\n".join(md))
    print(json.dumps({"status": "ok", "outdir": str(outdir)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
