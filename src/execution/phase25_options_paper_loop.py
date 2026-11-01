"""
Phase 25: Options Paper Loop integrating vol surface + skew/orderflow + hedging
"""
from __future__ import annotations

from typing import Dict, Any, List
import json
from pathlib import Path
import time

from src.options.phase25_vol_surface import VolSurface
from src.options.phase25_iv_skew_orderflow import IVSkewOrderflow
from src.hedging.phase25_delta_hedge_optimizer import DeltaHedgeOptimizer


class OptionsPaperLoop:
    def __init__(self, seed: int = 12345, paper_only: bool = True):
        if not paper_only:
            raise RuntimeError("live not enabled - paper_only required")
        self.seed = int(seed)
        self.paper_only = bool(paper_only)
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
        self.cycles += 1
        res = {
            "status": "ok",
            "cycle": self.cycles,
            "paper_only": True,
            "vol_surface": vs_rep,
            "iv_skew": sk_rep,
            "hedge": hd_rep,
            "ts": int(time.time()),
        }
        return res

    def run(self, cycles: int = 5, **kwargs) -> Dict[str, Any]:
        if cycles < 1 or cycles > 1000:
            raise ValueError("cycles out of range")
        results = []
        for i in range(cycles):
            quotes = [
                {"underlying": "BTC", "expiry": "30D", "strike": 100000, "iv": 0.55, "bid_iv": 0.54, "ask_iv": 0.56, "volume": 10},
                {"underlying": "ETH", "expiry": "30D", "strike": 4000, "iv": 0.6, "bid_iv": 0.59, "ask_iv": 0.61, "volume": 8},
            ]
            tape = [{"bid_vol": 10, "ask_vol": 12, "toxicity": 0.1}, {"bid_vol": 15, "ask_vol": 10, "toxicity": 0.05}]
            delta_book = {"net_delta": 5.0, "notional": 500000.0}
            liquidity = {"deribit": {"mid": 100000, "depth": 1.0}, "okx": {"mid": 100001, "depth": 0.8}, "bybit": {"mid": 99999, "depth": 0.6}}
            fees = {"deribit": 2.0, "okx": 2.5, "bybit": 3.0}
            results.append(self.run_cycle(quotes, tape, delta_book, liquidity, fees))
        rep = {
            "status": "ok",
            "cycles": cycles,
            "paper_only": True,
            "results": len(results),
            "gates_passed": True,
        }
        return rep

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE25_OPTIONS_PAPER_LOOP_REPORT.json"
        pmd = Path(outdir) / "PHASE25_OPTIONS_PAPER_LOOP_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(f"# PHASE25_OPTIONS_PAPER_LOOP_REPORT\n\nStatus: {report.get('status')}\n")
        return str(pjson)
