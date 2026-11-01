"""
Phase 26: Crypto Options Microstructure Arbitrage (Cross-venue IV/Price Dislocations)
Production-grade, deterministic, paper-only safe.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional
import json
from pathlib import Path
import math
import hashlib


@dataclass
class ArbOpportunity:
    arb_id: str
    underlying: str
    venue_a: str
    venue_b: str
    expiry: str
    strike: float
    option_type: str
    dislocation_bps: float
    iv_spread_bps: float
    theoretical_edge_bps: float
    orderflow_confirmed: bool
    confidence: float
    notional_usd: float
    status: str


class OptionsArb:
    def __init__(self, seed: int = 12345):
        self.seed = int(seed)
        self.opps: List[ArbOpportunity] = []
        self.venues = ["deribit", "okx", "bybit", "binance"]
        self.underlyings = ["BTC", "ETH", "SOL", "XRP"]

    def _arb_id(self, u: str, v1: str, v2: str, exp: str, strike: float, idx: int) -> str:
        h = hashlib.sha256(f"{self.seed}|p26|arb|{u}|{v1}|{v2}|{exp}|{strike}|{idx}".encode()).hexdigest()[:12]
        return f"p26arb_{h}"

    def detect_cross_venue_dislocations(self, quotes: List[Dict[str, Any]], orderflow: Optional[List[Dict[str, Any]]] = None) -> List[ArbOpportunity]:
        if not quotes:
            raise ValueError("no quotes")
        # Group by (underlying, expiry, strike, option_type)
        groups: Dict[tuple, List[Dict[str, Any]]] = {}
        for q in quotes:
            key = (q.get("underlying"), q.get("expiry"), q.get("strike"), q.get("option_type", "call"))
            if key not in groups:
                groups[key] = []
            groups[key].append(q)
        opps: List[ArbOpportunity] = []
        of_score = 0.0
        if orderflow:
            bid_vol = sum(float(x.get("bid_vol", 0)) for x in orderflow)
            ask_vol = sum(float(x.get("ask_vol", 0)) for x in orderflow)
            tox = sum(float(x.get("toxicity", 0)) for x in orderflow) / max(1, len(orderflow))
            of_score = (bid_vol - ask_vol) / max(1.0, bid_vol + ask_vol) - tox * 0.3
            if not math.isfinite(of_score):
                of_score = 0.0
        idx = 0
        for key, lst in groups.items():
            if len(lst) < 2:
                continue
            # compare venues
            for i in range(len(lst)):
                for j in range(i + 1, len(lst)):
                    qa, qb = lst[i], lst[j]
                    va, vb = qa.get("venue", "deribit"), qb.get("venue", "okx")
                    if va == vb:
                        continue
                    pa = float(qa.get("mid_price", qa.get("price", 0)))
                    pb = float(qb.get("mid_price", qb.get("price", 0)))
                    if pa <= 0 or pb <= 0 or not (math.isfinite(pa) and math.isfinite(pb)):
                        continue
                    iv_a = float(qa.get("iv", 0.5))
                    iv_b = float(qb.get("iv", 0.5))
                    if not (math.isfinite(iv_a) and math.isfinite(iv_b)):
                        raise ValueError("non-finite iv")
                    disloc_bps = abs(pa - pb) / max(1e-18, (pa + pb) / 2.0) * 10000.0
                    iv_spread_bps = abs(iv_a - iv_b) / max(1e-18, (iv_a + iv_b) / 2.0) * 10000.0
                    edge_bps = max(disloc_bps * 0.6 + iv_spread_bps * 0.4, 0.0)
                    if edge_bps < 5.0:  # minimum threshold
                        continue
                    conf = min(0.99, 0.5 + 0.01 * edge_bps + 0.1 * max(0.0, of_score))
                    if not math.isfinite(conf):
                        conf = 0.5
                    notional = float(qa.get("notional", 50000.0)) * (1.0 + 0.1 * (idx % 3))
                    opp = ArbOpportunity(
                        arb_id=self._arb_id(key[0], va, vb, key[1], float(key[2]), idx),
                        underlying=str(key[0]),
                        venue_a=str(va),
                        venue_b=str(vb),
                        expiry=str(key[1]),
                        strike=float(key[2]),
                        option_type=str(key[3]),
                        dislocation_bps=float(disloc_bps),
                        iv_spread_bps=float(iv_spread_bps),
                        theoretical_edge_bps=float(edge_bps),
                        orderflow_confirmed=bool(abs(of_score) > 0.05),
                        confidence=float(conf),
                        notional_usd=float(notional),
                        status="detected",
                    )
                    opps.append(opp)
                    self.opps.append(opp)
                    idx += 1
        # ensure finite
        for o in opps:
            if not all(math.isfinite(getattr(o, x)) for x in ["dislocation_bps", "iv_spread_bps", "theoretical_edge_bps", "confidence", "notional_usd"]):
                raise ValueError("non-finite arb")
        return opps

    def detect_calendar_diagonal(self, quotes: List[Dict[str, Any]], orderflow: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        if not quotes:
            raise ValueError("no quotes")
        # find same underlying/strike/type different expiries
        by_key: Dict[tuple, List[Dict[str, Any]]] = {}
        for q in quotes:
            key = (q.get("underlying"), q.get("strike"), q.get("option_type", "call"))
            if key not in by_key:
                by_key[key] = []
            by_key[key].append(q)
        res: List[Dict[str, Any]] = []
        for key, lst in by_key.items():
            if len(lst) < 2:
                continue
            # sort by tenor dummy
            for i in range(len(lst)):
                for j in range(i + 1, len(lst)):
                    a, b = lst[i], lst[j]
                    if a.get("expiry") == b.get("expiry"):
                        continue
                    iv_a, iv_b = float(a.get("iv", 0.5)), float(b.get("iv", 0.5))
                    if not (math.isfinite(iv_a) and math.isfinite(iv_b)):
                        raise ValueError("non-finite iv")
                    sprd = abs(iv_a - iv_b)
                    if sprd < 0.01:
                        continue
                    res.append({
                        "type": "calendar" if abs(float(a.get("strike", 0)) - float(b.get("strike", 0))) < 1e-9 else "diagonal",
                        "underlying": key[0],
                        "strike": float(key[1]),
                        "option_type": key[2],
                        "exp_a": a.get("expiry"),
                        "exp_b": b.get("expiry"),
                        "iv_spread": float(sprd),
                        "edge_bps": float(min(50.0, sprd * 10000.0 * 0.3)),
                        "orderflow_confirmed": bool(orderflow and len(orderflow) > 0),
                        "status": "detected",
                    })
        for r in res:
            if not math.isfinite(r["iv_spread"]) or not math.isfinite(r["edge_bps"]):
                raise ValueError("non-finite spread")
        return res

    def generate_report(self, opps: List[ArbOpportunity], spreads: List[Dict[str, Any]], outdir: str = "research_state") -> Dict[str, Any]:
        report = {
            "status": "ok",
            "phase": 26,
            "component": "options_arb",
            "opportunities": len(opps),
            "spreads": len(spreads),
            "venues": self.venues,
            "underlyings": self.underlyings,
            "avg_edge_bps": float(sum(o.theoretical_edge_bps for o in opps) / len(opps)) if opps else 0.0,
            "max_edge_bps": float(max((o.theoretical_edge_bps for o in opps), default=0.0)),
            "orderflow_confirmed_count": int(sum(1 for o in opps if o.orderflow_confirmed)),
            "opps": [asdict(o) for o in opps],
            "spreads_detail": spreads,
        }
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE26_OPTIONS_ARB_REPORT.json"
        pmd = Path(outdir) / "PHASE26_OPTIONS_ARB_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(f"# PHASE26_OPTIONS_ARB_REPORT\n\nStatus: ok\nOpportunities: {len(opps)}\nSpreads: {len(spreads)}\nAvg edge (bps): {report['avg_edge_bps']:.2f}\n")
        return report
