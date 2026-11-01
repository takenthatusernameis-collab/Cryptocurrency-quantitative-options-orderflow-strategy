#!/usr/bin/env python3
import hashlib
import math
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _git_sha() -> str | None:
    sha = os.environ.get("GIT_SHA")
    if sha:
        return str(sha)
    try:
        r = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd="/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5,
        )
        if r.returncode == 0:
            return r.stdout.decode().strip()
    except Exception:
        pass
    return None


def _det_ts(seed: int, idx: int = 0) -> str:
    h = hashlib.sha256(f"{seed}|p22router|{idx}".encode()).hexdigest()[:12]
    return f"2026-11-01T14:{h[:2]}:{h[2:4]}Z"


def _assert_no_nan_inf(obj: Any, label: str) -> None:
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
        raise ValueError(f"Non-finite values detected in {label}: {bad[:10]}")


@dataclass(frozen=True)
class RouterConfig:
    seed: int = 42
    paper_only: bool = True
    venues: tuple = ("deribit", "okx", "binance", "bybit", "bitget")
    max_latency_ms: float = 50.0
    max_spread_bps: float = 5.0
    min_depth_usd: float = 100000.0
    cost_weight: float = 0.4
    latency_weight: float = 0.3
    liquidity_weight: float = 0.3
    enforce_hard_limits: bool = True
    default_venue: str = "deribit"


@dataclass(frozen=True)
class VenueQuote:
    venue: str
    symbol: str
    bid: float
    ask: float
    mid: float
    spread_bps: float
    depth_usd: float
    latency_ms: float
    fee_bps: float
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class RoutingDecision:
    decision_id: str
    symbol: str
    side: str
    notional_usd: float
    selected_venue: str
    score: float
    venue_scores: Dict[str, float]
    expected_slippage_bps: float
    expected_latency_ms: float
    expected_fee_bps: float
    paper_only: bool
    timestamp: str
    routed: bool


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p22_{tag}_{h}"


class SmartOrderRouter:
    def __init__(self, config: Optional[RouterConfig] = None, seed: int = 42):
        self.config = config or RouterConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("SmartOrderRouter: paper_only must remain True")
        self.config = RouterConfig(
            seed=int(self.config.seed),
            paper_only=True,
            venues=tuple(self.config.venues),
            max_latency_ms=float(self.config.max_latency_ms),
            max_spread_bps=float(self.config.max_spread_bps),
            min_depth_usd=float(self.config.min_depth_usd),
            cost_weight=float(self.config.cost_weight),
            latency_weight=float(self.config.latency_weight),
            liquidity_weight=float(self.config.liquidity_weight),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
            default_venue=str(self.config.default_venue),
        )
        self.seed = int(self.config.seed)
        self.audit: List[Dict[str, Any]] = []

    def _sid(self, idx: int) -> str:
        return _make_id(self.seed, "dec", idx)

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def quote_venue(self, venue: str, symbol: str, idx: int = 0) -> VenueQuote:
        import random

        rng = random.Random(self.seed + 1000 + idx)
        venue = str(venue).lower()
        symbol = str(symbol).upper()
        mid = rng.uniform(80000.0, 120000.0) if symbol == "BTC" else rng.uniform(2000.0, 4000.0)
        spread_bps = rng.uniform(0.5, 4.0)
        bid = mid * (1.0 - spread_bps / 20000.0)
        ask = mid * (1.0 + spread_bps / 20000.0)
        depth_usd = rng.uniform(50000.0, 5000000.0)
        latency_ms = rng.uniform(5.0, 45.0)
        fee_bps = rng.uniform(0.5, 3.0)
        return VenueQuote(
            venue=venue,
            symbol=symbol,
            bid=float(bid),
            ask=float(ask),
            mid=float(mid),
            spread_bps=float(spread_bps),
            depth_usd=float(depth_usd),
            latency_ms=float(latency_ms),
            fee_bps=float(fee_bps),
            paper_only=True,
            timestamp=_det_ts(self.seed, idx),
        )

    def score_venue(self, quote: VenueQuote, notional_usd: float) -> float:
        cost_score = 1.0 / (1.0 + (quote.spread_bps + quote.fee_bps) / 10.0)
        lat_score = 1.0 / (1.0 + quote.latency_ms / self.config.max_latency_ms)
        liq_score = min(1.0, quote.depth_usd / max(notional_usd, 1.0))
        score = (
            self.config.cost_weight * cost_score
            + self.config.latency_weight * lat_score
            + self.config.liquidity_weight * liq_score
        )
        return float(max(0.0, min(1.0, score)))

    def route(
        self,
        symbol: str,
        side: str,
        notional_usd: float,
        venues: Optional[List[str]] = None,
        idx: int = 0,
    ) -> RoutingDecision:
        self._log("route", {"symbol": symbol, "side": side, "notional_usd": notional_usd})
        venue_list = list(venues) if venues else list(self.config.venues)
        quotes = [self.quote_venue(v, symbol, idx + i) for i, v in enumerate(venue_list)]
        venue_scores: Dict[str, float] = {}
        for q in quotes:
            venue_scores[q.venue] = self.score_venue(q, notional_usd)
        best = max(venue_scores, key=venue_scores.get)
        best_q = next(q for q in quotes if q.venue == best)
        eligible = [q for q in quotes if q.latency_ms <= self.config.max_latency_ms and q.spread_bps <= self.config.max_spread_bps and q.depth_usd >= self.config.min_depth_usd]
        routed = len(eligible) > 0 and self.config.enforce_hard_limits is False or (len(eligible) > 0)
        if self.config.enforce_hard_limits and len(eligible) == 0:
            routed = False
            best = str(self.config.default_venue)
        slippage_bps = best_q.spread_bps / 2.0 + 0.5
        rep = {
            "decision_id": self._sid(idx),
            "symbol": str(symbol).upper(),
            "side": str(side).lower(),
            "notional_usd": float(notional_usd),
            "selected_venue": str(best).lower(),
            "score": float(venue_scores.get(best, 0.0)),
            "venue_scores": {k: float(v) for k, v in venue_scores.items()},
            "expected_slippage_bps": float(slippage_bps),
            "expected_latency_ms": float(best_q.latency_ms),
            "expected_fee_bps": float(best_q.fee_bps),
            "paper_only": True,
            "timestamp": _det_ts(self.seed, idx),
            "routed": bool(routed),
        }
        _assert_no_nan_inf(rep, "p22_routing_decision")
        return RoutingDecision(
            decision_id=rep["decision_id"],
            symbol=rep["symbol"],
            side=rep["side"],
            notional_usd=rep["notional_usd"],
            selected_venue=rep["selected_venue"],
            score=rep["score"],
            venue_scores=rep["venue_scores"],
            expected_slippage_bps=rep["expected_slippage_bps"],
            expected_latency_ms=rep["expected_latency_ms"],
            expected_fee_bps=rep["expected_fee_bps"],
            paper_only=True,
            timestamp=rep["timestamp"],
            routed=rep["routed"],
        )

    def generate_report(self, decisions: List[RoutingDecision]) -> Dict[str, Any]:
        rep = {
            "report": "PHASE22_SMART_ROUTING_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "decision_count": len(decisions),
            "decisions": [asdict(d) for d in decisions],
            "routed_count": sum(1 for d in decisions if d.routed),
            "audit": self.audit,
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p22_router_report")
        return rep
