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
    h = hashlib.sha256(f"{seed}|p22tca|{idx}".encode()).hexdigest()[:12]
    return f"2026-11-01T14:{h[:2]}:{h[2:4]}Z"


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p22_{tag}_{h}"


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
class TCAConfig:
    seed: int = 42
    paper_only: bool = True
    arrival_price: float = 100000.0
    benchmark: str = "mid"
    max_tca_bps: float = 100.0
    enforce_hard_limits: bool = True


@dataclass(frozen=True)
class TCATrade:
    trade_id: str
    symbol: str
    venue: str
    strategy: str
    side: str
    notional_usd: float
    qty: float
    arrival_price: float
    fill_price: float
    spread_bps: float
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class TCAResult:
    result_id: str
    trade_id: str
    symbol: str
    venue: str
    strategy: str
    implementation_shortfall_bps: float
    slippage_bps: float
    spread_cost_bps: float
    timing_cost_bps: float
    total_cost_bps: float
    total_cost_usd: float
    within_budget: bool
    paper_only: bool
    timestamp: str


class TCA:
    def __init__(self, config: Optional[TCAConfig] = None, seed: int = 42):
        self.config = config or TCAConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("TCA: paper_only must remain True")
        self.config = TCAConfig(
            seed=int(self.config.seed),
            paper_only=True,
            arrival_price=float(self.config.arrival_price),
            benchmark=str(self.config.benchmark),
            max_tca_bps=float(self.config.max_tca_bps),
            enforce_hard_limits=bool(self.config.enforce_hard_limits),
        )
        self.seed = int(self.config.seed)
        self.audit: List[Dict[str, Any]] = []

    def _tid(self, idx: int) -> str:
        return _make_id(self.seed, "trade", idx)

    def _rid(self, idx: int) -> str:
        return _make_id(self.seed, "tca", idx)

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def make_trade(self, symbol: str, venue: str, strategy: str, side: str, notional_usd: float, qty: float, arrival_price: float, fill_price: float, spread_bps: float, idx: int = 0) -> TCATrade:
        import random

        rng = random.Random(self.seed + 13000 + idx)
        symbol = str(symbol).upper()
        venue = str(venue).lower()
        strategy = str(strategy)
        side = str(side).lower()
        if arrival_price <= 0:
            arrival_price = rng.uniform(80000.0, 120000.0) if symbol == "BTC" else rng.uniform(2000.0, 4000.0)
        if fill_price <= 0:
            fill_price = arrival_price * (1.0 + rng.uniform(-0.002, 0.002)) if side == "buy" else arrival_price * (1.0 - rng.uniform(-0.002, 0.002))
        return TCATrade(
            trade_id=self._tid(idx),
            symbol=symbol,
            venue=venue,
            strategy=strategy,
            side=side,
            notional_usd=float(notional_usd),
            qty=float(qty),
            arrival_price=float(arrival_price),
            fill_price=float(fill_price),
            spread_bps=float(spread_bps),
            paper_only=True,
            timestamp=_det_ts(self.seed, idx),
        )

    def analyze(self, trade: TCATrade, idx: int = 0) -> TCAResult:
        self._log("analyze", {"trade_id": trade.trade_id, "symbol": trade.symbol})
        side_mult = 1.0 if trade.side == "buy" else -1.0
        implementation_shortfall = (trade.fill_price - trade.arrival_price) / trade.arrival_price * 10000.0 * side_mult
        slippage_bps = abs(implementation_shortfall) * 0.5
        spread_cost_bps = trade.spread_bps / 2.0
        timing_cost_bps = abs(implementation_shortfall) * 0.3
        total_cost = slippage_bps + spread_cost_bps + timing_cost_bps
        total_cost = float(max(0.0, min(self.config.max_tca_bps, total_cost)))
        cost_usd = trade.notional_usd * total_cost / 10000.0
        within = total_cost <= self.config.max_tca_bps
        if self.config.enforce_hard_limits and total_cost > self.config.max_tca_bps:
            within = False
        rep = {
            "result_id": self._rid(idx),
            "trade_id": trade.trade_id,
            "symbol": trade.symbol,
            "venue": trade.venue,
            "strategy": trade.strategy,
            "implementation_shortfall_bps": float(implementation_shortfall),
            "slippage_bps": float(slippage_bps),
            "spread_cost_bps": float(spread_cost_bps),
            "timing_cost_bps": float(timing_cost_bps),
            "total_cost_bps": float(total_cost),
            "total_cost_usd": float(cost_usd),
            "within_budget": bool(within),
            "paper_only": True,
            "timestamp": _det_ts(self.seed, idx),
        }
        _assert_no_nan_inf(rep, "p22_tca_result")
        return TCAResult(
            result_id=rep["result_id"],
            trade_id=rep["trade_id"],
            symbol=rep["symbol"],
            venue=rep["venue"],
            strategy=rep["strategy"],
            implementation_shortfall_bps=rep["implementation_shortfall_bps"],
            slippage_bps=rep["slippage_bps"],
            spread_cost_bps=rep["spread_cost_bps"],
            timing_cost_bps=rep["timing_cost_bps"],
            total_cost_bps=rep["total_cost_bps"],
            total_cost_usd=rep["total_cost_usd"],
            within_budget=rep["within_budget"],
            paper_only=True,
            timestamp=rep["timestamp"],
        )

    def generate_report(self, trades: List[TCATrade], results: List[TCAResult]) -> Dict[str, Any]:
        avg_cost = float(sum(r.total_cost_bps for r in results) / len(results)) if results else 0.0
        avg_cost_usd = float(sum(r.total_cost_usd for r in results) / len(results)) if results else 0.0
        within = sum(1 for r in results if r.within_budget)
        by_strategy: Dict[str, float] = {}
        by_venue: Dict[str, float] = {}
        for r in results:
            by_strategy[r.strategy] = by_strategy.get(r.strategy, 0.0) + r.total_cost_bps
            by_venue[r.venue] = by_venue.get(r.venue, 0.0) + r.total_cost_bps
        rep = {
            "report": "PHASE22_TCA_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "trade_count": len(trades),
            "result_count": len(results),
            "trades": [asdict(t) for t in trades],
            "results": [asdict(r) for r in results],
            "summary": {
                "avg_total_cost_bps": float(avg_cost),
                "avg_total_cost_usd": float(avg_cost_usd),
                "within_budget_count": int(within),
                "within_budget_rate": float(within / len(results)) if results else 0.0,
                "by_strategy": {k: float(v) for k, v in by_strategy.items()},
                "by_venue": {k: float(v) for k, v in by_venue.items()},
                "paper_only": True,
            },
            "audit": self.audit,
            "git_sha": _git_sha(),
            "paper_only": True,
        }
        _assert_no_nan_inf(rep, "p22_tca_report")
        return rep
