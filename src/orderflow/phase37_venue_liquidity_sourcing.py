from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class SourcingConfig:
    seed: int = 424242
    paper_only: bool = True
    min_liquidity_usd: float = 100000.0
    imbalance_threshold: float = 0.2
    max_latency_ms: float = 50.0


@dataclass
class VenueLiquidity:
    venue: str
    bid_depth_usd: float
    ask_depth_usd: float
    bid_sz: float
    ask_sz: float
    imbalance: float
    latency_ms: float
    score: float
    valid: bool = True


@dataclass
class SourcingResult:
    ok: bool
    sources: List[VenueLiquidity]
    top_venues: List[str]
    metrics: Dict[str, float]
    warnings: List[str]


class VenueLiquiditySourcing:
    def __init__(self, cfg: SourcingConfig | None = None):
        self.cfg = cfg or SourcingConfig()
        if not self.cfg.paper_only:
            raise ValueError("live sourcing paths must be explicitly gated; default paper_only True")

    def _finite(self, x: float) -> bool:
        return math.isfinite(x)

    def scan(self, venues: List[str], orderflow_imbalance: float = 0.0, depth_scale: float = 1.0) -> SourcingResult:
        if not math.isfinite(orderflow_imbalance):
            orderflow_imbalance = 0.0
        if not math.isfinite(depth_scale) or depth_scale <= 0:
            depth_scale = 1.0
        warnings: List[str] = []
        sources: List[VenueLiquidity] = []
        for v in venues:
            bid_depth_usd = max(self.cfg.min_liquidity_usd * 0.5, 150000.0 * depth_scale * (1.0 - min(0.3, max(0.0, orderflow_imbalance))))
            ask_depth_usd = max(self.cfg.min_liquidity_usd * 0.5, 150000.0 * depth_scale * (1.0 + min(0.3, max(0.0, orderflow_imbalance))))
            bid_sz = bid_depth_usd / 50000.0
            ask_sz = ask_depth_usd / 50000.0
            imb = (bid_depth_usd - ask_depth_usd) / max(bid_depth_usd + ask_depth_usd, 1e-12)
            lat = 10.0 + (hash(v) % 20)
            score = (bid_depth_usd + ask_depth_usd) / 300000.0 * (1.0 - min(1.0, lat / 100.0))
            if not self._finite(bid_depth_usd):
                bid_depth_usd = self.cfg.min_liquidity_usd
                warnings.append(f"finite_bid_{v}")
            if not self._finite(ask_depth_usd):
                ask_depth_usd = self.cfg.min_liquidity_usd
                warnings.append(f"finite_ask_{v}")
            sources.append(
                VenueLiquidity(
                    venue=v,
                    bid_depth_usd=bid_depth_usd,
                    ask_depth_usd=ask_depth_usd,
                    bid_sz=max(0.01, bid_sz),
                    ask_sz=max(0.01, ask_sz),
                    imbalance=imb,
                    latency_ms=lat,
                    score=max(0.0, score),
                    valid=True,
                )
            )
        sources_sorted = sorted(sources, key=lambda x: x.score, reverse=True)
        top_venues = [s.venue for s in sources_sorted if s.score > 0.1][:4]
        metrics = {
            "n_venues": float(len(sources)),
            "avg_score": sum(s.score for s in sources) / max(1, len(sources)),
            "total_depth_usd": sum(s.bid_depth_usd + s.ask_depth_usd for s in sources),
            "max_imbalance": max((abs(s.imbalance) for s in sources), default=0.0),
        }
        return SourcingResult(ok=True, sources=sources, top_venues=top_venues, metrics=metrics, warnings=warnings)
