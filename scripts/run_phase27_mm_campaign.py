#!/usr/bin/env python3
"""Phase 27 Market Making campaign CLI (PAPER-ONLY)."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from src.execution.phase27_mm_paper_loop import MMPaperLoop, MMPaperLoopConfig
from src.options.phase27_market_maker import OptionsMarketMaker, MMConfig
from src.risk.phase27_inventory_risk import InventoryRiskManager, InventoryRiskConfig


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phase 27 Crypto Options Market Making campaign (paper-only)")
    p.add_argument("--symbols", type=str, default="BTC,ETH,SOL,XRP")
    p.add_argument("--venues", type=str, default="deribit,okx,bybit,binance")
    p.add_argument("--underlyings", type=str, default="BTC,ETH,SOL,XRP")
    p.add_argument("--expiries", type=str, default="7D,30D,90D")
    p.add_argument("--modes", type=str, default="paper", help="paper (default) or live (hard-gated, rejected)")
    p.add_argument("--cycles", type=int, default=10)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--enforce-gates", action="store_true", default=True)
    p.add_argument("--no-enforce-gates", action="store_false", dest="enforce_gates")
    p.add_argument("--outdir", type=str, default="research_state")
    return p


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    modes = [m.strip().lower() for m in args.modes.split(",") if m.strip()]
    if "live" in modes:
        raise SystemExit("live mode is hard-gated and disabled; run paper-only")
    underlyings = tuple(u.strip().upper() for u in args.underlyings.split(",") if u.strip())
    expiries = tuple(e.strip() for e in args.expiries.split(",") if e.strip())
    venues = tuple(v.strip().lower() for v in args.venues.split(",") if v.strip())
    mm_cfg = MMConfig(seed=args.seed, paper_only=True, underlyings=underlyings, expiries=expiries, venues=venues, enforce_gates=bool(args.enforce_gates))
    inv_cfg = InventoryRiskConfig(seed=args.seed, paper_only=True, underlyings=underlyings, expiries=expiries, enforce_hard_limits=bool(args.enforce_gates))
    loop_cfg = MMPaperLoopConfig(seed=args.seed, paper_only=True, underlyings=underlyings, expiries=expiries, venues=venues, cycles=int(args.cycles), enforce_gates=bool(args.enforce_gates))
    mm = OptionsMarketMaker(config=mm_cfg)
    risk = InventoryRiskManager(config=inv_cfg)
    loop = MMPaperLoop(config=loop_cfg)
    tape = [{"bid_vol": 10, "ask_vol": 12, "toxicity": 0.1}, {"bid_vol": 15, "ask_vol": 11, "toxicity": 0.05}]
    results = loop.run(cycles=int(args.cycles), tape=tape)
    mm_rep = mm.generate_report()
    risk_rep = risk.generate_report()
    loop_rep = loop.generate_report()
    mm.save_report(mm_rep, outdir=args.outdir)
    risk.save_report(risk_rep, outdir=args.outdir)
    loop.save_report(loop_rep, outdir=args.outdir)
    master = {
        "campaign": "phase27_market_making",
        "seed": args.seed,
        "modes": modes,
        "underlyings": list(underlyings),
        "expiries": list(expiries),
        "venues": list(venues),
        "cycles": int(args.cycles),
        "paper_only": True,
        "enforce_gates": bool(args.enforce_gates),
        "results": results,
        "market_maker_report": mm_rep,
        "inventory_risk_report": risk_rep,
        "mm_paper_loop_report": loop_rep,
        "timestamp": _utc_now(),
    }
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    pjson = Path(args.outdir) / "PHASE27_MM_MASTER_REPORT.json"
    pmd = Path(args.outdir) / "PHASE27_MM_MASTER_REPORT.md"
    pjson.write_text(json.dumps(master, indent=2))
    pmd.write_text(f"# PHASE27_MM_MASTER_REPORT\n\nStatus: ok\nCycles: {int(args.cycles)}\nPaper-only: True\n")
    print(json.dumps({"status": "ok", "campaign": "phase27_market_making", "cycles": int(args.cycles), "paper_only": True, "outdir": args.outdir}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
