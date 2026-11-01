#!/usr/bin/env python3
"""Phase 24 Cross-Venue Router (PAPER-ONLY).

Multi-venue orderflow routing with venue selection, deterministic.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p24cv|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p24cv_{tag}_{h}"


def _assert_finite(obj: Any, label: str = "obj") -> None:
    bad: List[str] = []

    def walk(v: Any, p: str) -> None:
        if isinstance(v, dict):
            for k, val in v.items():
                walk(val, f"{p}/{k}")
        elif isinstance(v, (list, tuple)):
            for i, val in enumerate(v):
                walk(val, f"{p}[{i}]")
        elif isinstance(v, float) and not isinstance(v, bool):
            if not math.isfinite(v):
                bad.append(p)

    walk(obj, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class CrossVenueConfig:
    seed: int = 42
    paper_only: bool = True
    venues: tuple = ("deribit", "okx", "binance", "bybit", "bitget")
    cost_weight: float = 0.35
    latency_weight: float = 0.25
    liquidity_weight: float = 0.25
    orderflow_weight: float = 0.15
    min_depth_usd: float = 80000.0
    max_latency_ms: float = 60.0
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class VenueMetrics:
    venue: str
    symbol: str
    bid_ask_spread_bps: float
    depth_usd: float
    latency_ms: float
    taker_fee_bps: float
    orderflow_score: float
    fill_probability: float
    available: bool
    timestamp: str


@dataclass(frozen=True)
class CrossVenueDecision:
    decision_id: str
    symbol: str
    side: str
    notional_usd: float
    primary_venue: str
    backup_venues: List[str]
    venue_scores: Dict[str, float]
    routed_split: Dict[str, float]
    expected_cost_bps: float
    expected_latency_ms: float
    orderflow_routed: bool
    paper_only: bool
    timestamp: str


class CrossVenueRouter:
    def __init__(self, config: Optional[CrossVenueConfig] = None, seed: int = 42):
        self.config = config or CrossVenueConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("CrossVenueRouter: paper_only must remain True")
        self.config = CrossVenueConfig(
            seed=int(self.config.seed),
            paper_only=True,
            venues=tuple(self.config.venues),
            cost_weight=float(self.config.cost_weight),
            latency_weight=float(self.config.latency_weight),
            liquidity_weight=float(self.config.liquidity_weight),
            orderflow_weight=float(self.config.orderflow_weight),
            min_depth_usd=float(self.config.min_depth_usd),
            max_latency_ms=float(self.config.max_latency_ms),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self.decisions: List[CrossVenueDecision] = []
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def collect_venue_metrics(self, symbol: str, idx: int = 0) -> Dict[str, VenueMetrics]:
        import random

        rng = random.Random(self.seed + 25000 + idx)
        out: Dict[str, VenueMetrics] = {}
        for v in self.config.venues:
            spread = rng.uniform(0.4, 4.5)
            depth = rng.uniform(40000.0, 6000000.0)
            lat = rng.uniform(4.0, 55.0)
            fee = rng.uniform(0.3, 2.5)
            of_score = rng.uniform(0.4, 0.95)
            fill_p = rng.uniform(0.7, 0.99)
            avail = depth >= self.config.min_depth_usd and lat <= self.config.max_latency_ms
            m = VenueMetrics(
                venue=str(v).lower(),
                symbol=str(symbol).upper(),
                bid_ask_spread_bps=float(spread),
                depth_usd=float(depth),
                latency_ms=float(lat),
                taker_fee_bps=float(fee),
                orderflow_score=float(of_score),
                fill_probability=float(fill_p),
                available=bool(avail),
                timestamp=_utc_now(),
            )
            _assert_finite(asdict(m), f"metrics_{v}")
            out[v] = m
        return out

    def score_venues(self, metrics: Dict[str, VenueMetrics], notional_usd: float) -> Dict[str, float]:
        scores: Dict[str, float] = {}
        for ven, m in metrics.items():
            cost_score = 1.0 - min(m.bid_ask_spread_bps + m.taker_fee_bps, 20.0) / 20.0
            lat_score = 1.0 - min(m.latency_ms, self.config.max_latency_ms) / self.config.max_latency_ms
            liq_score = min(m.depth_usd / max(notional_usd * 10.0, 100000.0), 1.0)
            of_score = m.orderflow_score
            s = (
                self.config.cost_weight * cost_score
                + self.config.latency_weight * lat_score
                + self.config.liquidity_weight * liq_score
                + self.config.orderflow_weight * of_score
            )
            if not m.available and self.config.enforce_hard_limits:
                s *= 0.1
            scores[ven] = float(max(0.0, min(1.0, s)))
        return scores

    def route(self, symbol: str, side: str, notional_usd: float, venues: Optional[List[str]] = None, idx: int = 0) -> CrossVenueDecision:
        vlist = list(venues) if venues is not None else list(self.config.venues)
        metrics = self.collect_venue_metrics(symbol, idx)
        metrics_f = {k: v for k, v in metrics.items() if k in vlist}
        scores = self.score_venues(metrics_f, float(notional_usd))
        sorted_v = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        primary = sorted_v[0][0] if sorted_v else vlist[0]
        backups = [v for v, _ in sorted_v[1:4]]
        # build split - primary gets majority
        split: Dict[str, float] = {}
        if sorted_v:
            # deterministic split
            rem = 1.0
            for i, (v, sc) in enumerate(sorted_v[:3]):
                if i == 0:
                    w = 0.6 + 0.1 * sc
                elif i == 1:
                    w = 0.25
                else:
                    w = 0.1
                w = max(0.05, min(rem, w))
                split[v] = float(w)
                rem -= w
            if rem > 1e-12 and split:
                # add to primary
                first = list(split.keys())[0]
                split[first] = float(split[first] + rem)
        # normalize
        ssum = sum(split.values())
        if ssum > 0:
            split = {k: float(v / ssum) for k, v in split.items()}
        # expected metrics
        pm = metrics_f.get(primary)
        exp_cost = float((pm.bid_ask_spread_bps + pm.taker_fee_bps) if pm else 2.0)
        exp_lat = float(pm.latency_ms if pm else 20.0)
        dec = CrossVenueDecision(
            decision_id=_make_id(self.seed, "dec", len(self.decisions) + idx),
            symbol=str(symbol).upper(),
            side=str(side).lower(),
            notional_usd=float(notional_usd),
            primary_venue=primary,
            backup_venues=backups,
            venue_scores=scores,
            routed_split=split,
            expected_cost_bps=exp_cost,
            expected_latency_ms=exp_lat,
            orderflow_routed=True,
            paper_only=True,
            timestamp=_utc_now(),
        )
        _assert_finite(asdict(dec), f"decision_{idx}")
        self.decisions.append(dec)
        self._log("routed", {"symbol": symbol, "primary": primary})
        return dec

    def generate_report(self, decisions: Optional[List[CrossVenueDecision]] = None) -> Dict[str, Any]:
        decs = decisions if decisions is not None else self.decisions
        rep = {
            "report": "PHASE24_CROSS_VENUE_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "decision_count": len(decs),
            "routed_count": len([d for d in decs if d.orderflow_routed]),
            "venues": list(self.config.venues),
            "decisions": [asdict(d) for d in decs],
            "audit_count": len(self.audit),
            "paper_only": True,
        }
        _assert_finite(rep, "cross_venue_report")
        assert_json_valid(rep)
        return serialize_metrics_strict(rep)
