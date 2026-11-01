"""
Phase 26: Liquidity Capture (maker-first routing, adverse selection filters)
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import json
from pathlib import Path
import math
import hashlib


@dataclass
class CapturePlan:
    plan_id: str
    venue: str
    side: str
    mode: str  # maker-first
    notional_usd: float
    expected_fill_prob: float
    adverse_selection_score: float
    toxicity_filtered: bool
    fee_bps: float
    net_edge_bps: float
    status: str


class LiquidityCapture:
    def __init__(self, seed: int = 12345):
        self.seed = int(seed)
        self.plans: List[CapturePlan] = []
        self.venues = ["deribit", "okx", "bybit", "binance"]

    def _pid(self, v: str, idx: int) -> str:
        h = hashlib.sha256(f"{self.seed}|p26|liq|{v}|{idx}".encode()).hexdigest()[:12]
        return f"p26liq_{h}"

    def maker_first_route(self, opps: List[Dict[str, Any]], liquidity: Dict[str, Any], fees: Dict[str, Any], orderflow: List[Dict[str, Any]] = None) -> List[CapturePlan]:
        if not opps:
            raise ValueError("no opportunities")
        plans: List[CapturePlan] = []
        tox = 0.0
        if orderflow:
            tox = sum(float(x.get("toxicity", 0)) for x in orderflow) / max(1, len(orderflow))
        idx = 0
        for o in opps:
            ven = o.get("venue_a") or self.venues[idx % len(self.venues)]
            depth = float((liquidity.get(ven) or {}).get("depth", 0.5))
            fee = float((fees.get(ven) if fees else 2.0) or 2.0)
            # adverse selection filter
            as_score = tox * 0.8 + (1.0 - min(1.0, depth)) * 0.2
            if as_score > 0.6:
                continue  # filtered
            fill_prob = min(0.95, 0.4 + 0.3 * depth - 0.2 * tox)
            edge = float(o.get("theoretical_edge_bps", 10.0))
            net_edge = edge - fee - as_score * 10.0
            if net_edge < 2.0:
                continue
            if not all(math.isfinite(x) for x in [fill_prob, as_score, fee, net_edge]):
                raise ValueError("non-finite liquidity")
            plan = CapturePlan(
                plan_id=self._pid(ven, idx),
                venue=str(ven),
                side="maker",
                mode="maker-first",
                notional_usd=float(o.get("notional_usd", 50000.0)),
                expected_fill_prob=float(fill_prob),
                adverse_selection_score=float(as_score),
                toxicity_filtered=bool(tox < 0.15),
                fee_bps=float(fee),
                net_edge_bps=float(net_edge),
                status="planned",
            )
            plans.append(plan)
            self.plans.append(plan)
            idx += 1
        return plans

    def integrate_fill_predictor(self, plans: List[CapturePlan], fill_pred: Dict[str, Any]) -> List[Dict[str, Any]]:
        res = []
        for p in plans:
            bp = float(fill_pred.get("base_prob", p.expected_fill_prob))
            adj = bp * (1.0 - 0.1 * p.adverse_selection_score)
            if not math.isfinite(adj):
                raise ValueError("non-finite fill pred")
            res.append({**asdict(p), "predicted_fill_prob": float(min(0.99, max(0.01, adj))), "integrated": True})
        return res

    def generate_report(self, plans: List[CapturePlan], integrated: List[Dict[str, Any]], outdir: str = "research_state") -> Dict[str, Any]:
        report = {
            "status": "ok",
            "phase": 26,
            "component": "liquidity_capture",
            "plans": len(plans),
            "integrated": len(integrated),
            "maker_first": True,
            "avg_net_edge_bps": float(sum(p.net_edge_bps for p in plans) / len(plans)) if plans else 0.0,
            "avg_fill_prob": float(sum(p.expected_fill_prob for p in plans) / len(plans)) if plans else 0.0,
            "filtered_as": int(sum(1 for p in plans if p.adverse_selection_score < 0.3)),
            "plans_detail": [asdict(p) for p in plans],
            "integrated_detail": integrated,
        }
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE26_LIQUIDITY_CAPTURE_REPORT.json"
        pmd = Path(outdir) / "PHASE26_LIQUIDITY_CAPTURE_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(f"# PHASE26_LIQUIDITY_CAPTURE_REPORT\n\nStatus: ok\nPlans: {len(plans)}\nAvg net edge (bps): {report['avg_net_edge_bps']:.2f}\n")
        return report
