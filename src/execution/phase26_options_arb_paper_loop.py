"""
Phase 26: Options Arb Paper Loop integrating Phase 24-25
"""
from __future__ import annotations

from typing import Dict, Any, List
import json
from pathlib import Path
import time

from src.options.phase26_options_arb import OptionsArb
from src.options.phase26_liquidity_capture import LiquidityCapture
from src.options.phase25_vol_surface import VolSurface
from src.options.phase25_iv_skew_orderflow import IVSkewOrderflow
from src.hedging.phase25_delta_hedge_optimizer import DeltaHedgeOptimizer


class OptionsArbPaperLoop:
    def __init__(self, seed: int = 12345, paper_only: bool = True):
        if not paper_only:
            raise RuntimeError("live not enabled - paper_only required")
        self.seed = int(seed)
        self.paper_only = bool(paper_only)
        self.arb = OptionsArb(seed=seed)
        self.liq = LiquidityCapture(seed=seed)
        self.vs = VolSurface(seed=seed)
        self.skew = IVSkewOrderflow(seed=seed)
        self.hedge = DeltaHedgeOptimizer(seed=seed)
        self.cycles = 0

    def run_cycle(self, quotes: List[Dict[str, Any]], tape: List[Dict[str, Any]], delta_book: Dict[str, Any], liquidity: Dict[str, Any], fees: Dict[str, Any]) -> Dict[str, Any]:
        if not self.paper_only:
            raise RuntimeError("hard gate: live disabled")
        vs_rep = self.vs.build_surface(quotes, orderflow=tape)
        sk_rep = self.skew.adjust_skew([{"underlying": "BTC", "expiry": "30D", "delta": 25.0, "rr": 0.02, "bf": 0.01, "iv": 0.5}], tape)
        hd_rep = self.hedge.optimize(delta_book, liquidity, fees)
        opps = self.arb.detect_cross_venue_dislocations(quotes, orderflow=tape)
        spreads = self.arb.detect_calendar_diagonal(quotes, orderflow=tape)
        plans = self.liq.maker_first_route([{"venue_a": o.venue_a, "theoretical_edge_bps": o.theoretical_edge_bps, "notional_usd": o.notional_usd} for o in opps], liquidity, fees, tape)
        intg = self.liq.integrate_fill_predictor(plans, {"base_prob": 0.7})
        self.cycles += 1
        res = {
            "status": "ok",
            "cycle": self.cycles,
            "paper_only": True,
            "vol_surface": vs_rep,
            "iv_skew": sk_rep,
            "hedge": hd_rep,
            "arbitrage_opps": len(opps),
            "calendar_diagonal_spreads": len(spreads),
            "liquidity_plans": len(plans),
            "integrated_plans": len(intg),
            "ts": int(time.time()),
        }
        return res

    def run(self, cycles: int = 5, **kwargs) -> Dict[str, Any]:
        if cycles < 1 or cycles > 1000:
            raise ValueError("cycles out of range")
        results = []
        for i in range(cycles):
            quotes = [
                {"underlying": "BTC", "expiry": "30D", "strike": 100000, "option_type": "call", "venue": "deribit", "iv": 0.55, "mid_price": 5200, "notional": 50000},
                {"underlying": "BTC", "expiry": "30D", "strike": 100000, "option_type": "call", "venue": "okx", "iv": 0.57, "mid_price": 5350, "notional": 50000},
                {"underlying": "ETH", "expiry": "30D", "strike": 4000, "option_type": "call", "venue": "deribit", "iv": 0.60, "mid_price": 210, "notional": 40000},
                {"underlying": "ETH", "expiry": "30D", "strike": 4000, "option_type": "call", "venue": "bybit", "iv": 0.61, "mid_price": 215, "notional": 40000},
            ]
            tape = [{"bid_vol": 12, "ask_vol": 10, "toxicity": 0.08}, {"bid_vol": 14, "ask_vol": 11, "toxicity": 0.07}]
            delta_book = {"net_delta": 3.0, "notional": 300000.0}
            liquidity = {"deribit": {"mid": 100000, "depth": 1.0}, "okx": {"mid": 100001, "depth": 0.9}, "bybit": {"mid": 99999, "depth": 0.7}}
            fees = {"deribit": 2.0, "okx": 2.5, "bybit": 3.0}
            results.append(self.run_cycle(quotes, tape, delta_book, liquidity, fees))
        arb_rep = self.arb.generate_report(self.arb.opps, self.arb.detect_calendar_diagonal(quotes, tape) if 'quotes' in locals() else [], outdir=kwargs.get("outdir", "research_state"))
        liq_rep = self.liq.generate_report(self.liq.plans, self.liq.integrate_fill_predictor(self.liq.plans, {"base_prob": 0.7}), outdir=kwargs.get("outdir", "research_state"))
        rep = {
            "status": "ok",
            "cycles": cycles,
            "paper_only": True,
            "results": len(results),
            "gates_passed": True,
            "options_arb_report": arb_rep.get("status"),
            "liquidity_capture_report": liq_rep.get("status"),
        }
        return rep

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE26_OPTIONS_ARB_PAPER_LOOP_REPORT.json"
        pmd = Path(outdir) / "PHASE26_OPTIONS_ARB_PAPER_LOOP_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(f"# PHASE26_OPTIONS_ARB_PAPER_LOOP_REPORT\n\nStatus: {report.get('status')}\nCycles: {report.get('cycles')}\n")
        return str(pjson)
