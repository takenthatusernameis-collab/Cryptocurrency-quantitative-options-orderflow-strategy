#!/usr/bin/env python3
"""
Phase 26: Options Arb Campaign
"""
import argparse
import json
from pathlib import Path

from src.options.phase26_options_arb import OptionsArb
from src.options.phase26_liquidity_capture import LiquidityCapture
from src.execution.phase26_options_arb_paper_loop import OptionsArbPaperLoop


def main():
    p = argparse.ArgumentParser(description="Phase26 Options Arb Campaign")
    p.add_argument("--symbols", default="BTC,ETH,SOL,XRP")
    p.add_argument("--venues", default="deribit,okx,bybit,binance")
    p.add_argument("--underlyings", default="BTC,ETH,SOL,XRP")
    p.add_argument("--expiries", default="30D,7D,90D")
    p.add_argument("--modes", default="paper")
    p.add_argument("--cycles", type=int, default=5)
    p.add_argument("--seed", type=int, default=12345)
    p.add_argument("--enforce-gates", action="store_true", default=True)
    p.add_argument("--outdir", default="research_state")
    args = p.parse_args()

    if "live" in args.modes and args.enforce_gates:
        pass

    arb = OptionsArb(seed=args.seed)
    liq = LiquidityCapture(seed=args.seed)
    loop = OptionsArbPaperLoop(seed=args.seed, paper_only=True)

    quotes = [
        {"underlying": "BTC", "expiry": "30D", "strike": 100000, "option_type": "call", "venue": "deribit", "iv": 0.55, "mid_price": 5200, "notional": 50000},
        {"underlying": "BTC", "expiry": "30D", "strike": 100000, "option_type": "call", "venue": "okx", "iv": 0.57, "mid_price": 5350, "notional": 50000},
        {"underlying": "BTC", "expiry": "30D", "strike": 100000, "option_type": "call", "venue": "bybit", "iv": 0.56, "mid_price": 5275, "notional": 50000},
        {"underlying": "ETH", "expiry": "30D", "strike": 4000, "option_type": "call", "venue": "deribit", "iv": 0.60, "mid_price": 210, "notional": 40000},
        {"underlying": "ETH", "expiry": "30D", "strike": 4000, "option_type": "call", "venue": "okx", "iv": 0.62, "mid_price": 218, "notional": 40000},
        {"underlying": "SOL", "expiry": "30D", "strike": 150, "option_type": "put", "venue": "deribit", "iv": 0.70, "mid_price": 8.5, "notional": 30000},
        {"underlying": "SOL", "expiry": "30D", "strike": 150, "option_type": "put", "venue": "bybit", "iv": 0.72, "mid_price": 9.0, "notional": 30000},
        {"underlying": "XRP", "expiry": "7D", "strike": 0.5, "option_type": "call", "venue": "deribit", "iv": 0.80, "mid_price": 0.012, "notional": 20000},
        {"underlying": "XRP", "expiry": "7D", "strike": 0.5, "option_type": "call", "venue": "okx", "iv": 0.83, "mid_price": 0.013, "notional": 20000},
        {"underlying": "BTC", "expiry": "7D", "strike": 100000, "option_type": "call", "venue": "deribit", "iv": 0.53, "mid_price": 1800, "notional": 50000},
        {"underlying": "BTC", "expiry": "90D", "strike": 100000, "option_type": "call", "venue": "deribit", "iv": 0.57, "mid_price": 9800, "notional": 50000},
    ]
    tape = [{"bid_vol": 15, "ask_vol": 10, "toxicity": 0.07}, {"bid_vol": 12, "ask_vol": 14, "toxicity": 0.09}]
    liquidity = {"deribit": {"mid": 100000, "depth": 1.0}, "okx": {"mid": 100001, "depth": 0.9}, "bybit": {"mid": 99999, "depth": 0.7}, "binance": {"mid": 100000, "depth": 0.6}}
    fees = {"deribit": 2.0, "okx": 2.5, "bybit": 3.0, "binance": 3.5}

    opps = arb.detect_cross_venue_dislocations(quotes, orderflow=tape)
    spreads = arb.detect_calendar_diagonal(quotes, orderflow=tape)
    plans = liq.maker_first_route([{"venue_a": o.venue_a, "theoretical_edge_bps": o.theoretical_edge_bps, "notional_usd": o.notional_usd} for o in opps], liquidity, fees, tape)
    intg = liq.integrate_fill_predictor(plans, {"base_prob": 0.72})
    loop_rep = loop.run(cycles=args.cycles)

    arb_rep = arb.generate_report(opps, spreads, args.outdir)
    liq_rep = liq.generate_report(plans, intg, args.outdir)
    loop.save_report(loop_rep, args.outdir)

    master = {
        "status": "ok",
        "phase": 26,
        "campaign": "options_microstructure_arb",
        "modes": args.modes,
        "enforce_gates": bool(args.enforce_gates),
        "paper_only": True,
        "options_arb": arb_rep,
        "liquidity_capture": liq_rep,
        "options_arb_paper_loop": loop_rep,
    }
    Path(args.outdir).mkdir(parents=True, exist_ok=True)
    (Path(args.outdir) / "PHASE26_OPTIONS_ARB_MASTER_REPORT.json").write_text(json.dumps(master, indent=2))
    (Path(args.outdir) / "PHASE26_OPTIONS_ARB_MASTER_REPORT.md").write_text("# PHASE26_OPTIONS_ARB_MASTER_REPORT\n\nStatus: ok\nPhase: 26\n")
    print(json.dumps({"status": "ok", "phase": 26}))


if __name__ == "__main__":
    main()
