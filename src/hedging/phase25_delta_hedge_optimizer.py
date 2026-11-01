"""
Phase 25: Delta-Hedging Optimizer (cost-aware, liquidity-aware, cross-venue)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any
import json
from pathlib import Path
import math


@dataclass
class HedgeAction:
    venue: str
    side: str
    qty: float
    price: float
    cost_bps: float
    urgency: float


class DeltaHedgeOptimizer:
    def __init__(self, seed: int = 12345):
        self.seed = int(seed)
        self.actions: List[HedgeAction] = []
        self.circuit_breaker = {"enabled": True, "tripped": False, "max_notional": 10_000_000.0}

    def optimize(self, delta_book: Dict[str, Any], liquidity: Dict[str, Any], fees: Dict[str, Any]) -> Dict[str, Any]:
        net_delta = float(delta_book.get("net_delta", 0.0))
        notional = float(delta_book.get("notional", 0.0))
        if not math.isfinite(net_delta) or not math.isfinite(notional):
            raise ValueError("non-finite")
        if not self.circuit_breaker["enabled"]:
            raise RuntimeError("circuit breaker disabled")
        if abs(notional) > self.circuit_breaker["max_notional"]:
            self.circuit_breaker["tripped"] = True
            return {"status": "blocked", "reason": "notional_exceeds_limit", "actions": []}
        # determine hedge direction
        side = "sell" if net_delta > 0 else "buy"
        qty = abs(net_delta) * 0.1  # contract units simplified
        venues = ["deribit", "okx", "bybit"]
        actions = []
        for i, v in enumerate(venues):
            px = float(liquidity.get(v, {}).get("mid", 100000.0))
            fee = float(fees.get(v, 2.0))  # bps
            # liquidity-aware allocation
            depth = float(liquidity.get(v, {}).get("depth", 1.0))
            alloc = qty * (depth / (sum(float(liquidity.get(x, {}).get("depth", 1.0)) for x in venues)))
            if alloc < 1e-12:
                continue
            ha = HedgeAction(venue=v, side=side, qty=float(alloc), price=float(px), cost_bps=float(fee), urgency=0.5 + i * 0.1)
            actions.append(ha)
            self.actions.append(ha)
        cost_est = sum(a.qty * a.price * a.cost_bps / 10000.0 for a in actions)
        report = {
            "status": "ok",
            "net_delta": float(net_delta),
            "notional": float(notional),
            "actions": len(actions),
            "estimated_cost": float(cost_est),
            "circuit_breaker_tripped": bool(self.circuit_breaker["tripped"]),
        }
        return report

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE25_DELTA_HEDGE_OPTIMIZER_REPORT.json"
        pmd = Path(outdir) / "PHASE25_DELTA_HEDGE_OPTIMIZER_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(f"# PHASE25_DELTA_HEDGE_OPTIMIZER_REPORT\n\nStatus: {report.get('status')}\n")
        return str(pjson)
