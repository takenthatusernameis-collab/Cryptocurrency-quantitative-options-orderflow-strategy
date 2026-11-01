"""
Phase 25: IV Skew/Risk Reversal driven by Orderflow
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Any
import json
from pathlib import Path
import math


@dataclass
class SkewPoint:
    underlying: str
    expiry: str
    delta: float
    rr: float  # risk reversal
    bf: float  # butterfly
    iv: float
    of_score: float


class IVSkewOrderflow:
    def __init__(self, seed: int = 12345):
        self.seed = int(seed)
        self.skews: List[SkewPoint] = []

    def compute_orderflow_score(self, tape: List[Dict[str, Any]]) -> float:
        if not tape:
            return 0.0
        imb = []
        tox = []
        for t in tape:
            bid = float(t.get("bid_vol", 0.0))
            ask = float(t.get("ask_vol", 0.0))
            tot = bid + ask
            if tot > 0:
                imb.append((bid - ask) / tot)
            tox.append(float(t.get("toxicity", 0.0)))
        s_imb = sum(imb) / len(imb) if imb else 0.0
        s_tox = sum(tox) / len(tox) if tox else 0.0
        score = 0.6 * s_imb - 0.4 * s_tox
        if not math.isfinite(score):
            raise ValueError("non-finite score")
        return float(max(-1.0, min(1.0, score)))

    def adjust_skew(self, base_skew: List[Dict[str, Any]], tape: List[Dict[str, Any]]) -> Dict[str, Any]:
        of_score = self.compute_orderflow_score(tape)
        out = []
        for s in base_skew:
            delta = float(s.get("delta", 25.0))
            rr_base = float(s.get("rr", 0.02))
            bf_base = float(s.get("bf", 0.01))
            iv_base = float(s.get("iv", 0.5))
            # deterministic adjustment
            adj_rr = rr_base + 0.01 * of_score * (1.0 if delta > 0 else -1.0)
            adj_bf = bf_base * (1.0 + 0.05 * abs(of_score))
            adj_iv = iv_base * (1.0 + 0.002 * of_score)
            if not all(math.isfinite(x) for x in [adj_rr, adj_bf, adj_iv]):
                raise ValueError("non-finite adj")
            sp = SkewPoint(
                underlying=s.get("underlying", "BTC"),
                expiry=s.get("expiry", "30D"),
                delta=delta,
                rr=float(adj_rr),
                bf=float(adj_bf),
                iv=float(adj_iv),
                of_score=float(of_score),
            )
            out.append(sp)
            self.skews.append(sp)
        report = {
            "status": "ok",
            "count": len(out),
            "orderflow_score": float(of_score),
            "skew_hash": hash(json.dumps([sp.__dict__ for sp in out], sort_keys=True)) & 0xFFFFFFFF,
        }
        return report

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE25_IV_SKEW_ORDERFLOW_REPORT.json"
        pmd = Path(outdir) / "PHASE25_IV_SKEW_ORDERFLOW_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(f"# PHASE25_IV_SKEW_ORDERFLOW_REPORT\n\nStatus: {report.get('status')}\n")
        return str(pjson)
