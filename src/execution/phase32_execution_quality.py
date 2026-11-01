"""
Phase 32: Execution Quality Engine for Crypto Options Cross-Venue Execution.

Production-grade slippage model, per-fill TCA, venue comparison, and execution
quality scoring. Deterministic, finite numerics, PAPER-ONLY default with
hard-gated live paths. Extends Phase 24 cross-venue router + Phase 30/31.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p32eq|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p32eq_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


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
class ExecutionQualityConfig32:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 10
    slippage_bps_base: float = 2.0
    slippage_bps_vol_mult: float = 3.0
    latency_ms_base: float = 40.0
    fill_rate_base: float = 0.95
    maker_taker_fee_bps: float = 0.05
    notional_impact_bps: float = 0.0005
    min_fill_rate: float = 0.80
    max_slippage_bps: float = 25.0


@dataclass(frozen=True)
class SlippageEstimate:
    symbol: str
    side: str
    venue: str
    notional_usd: float
    slippage_bps: float
    expected_fill_price: float
    latency_ms: float
    fill_rate: float
    fee_bps: float
    total_cost_bps: float
    paper_only: bool


@dataclass(frozen=True)
class TCAResult:
    fill_id: str
    symbol: str
    side: str
    venue: str
    notional_usd: float
    realized_slippage_bps: float
    timing_cost_bps: float
    fee_bps: float
    total_cost_bps: float
    mid_price: float
    fill_price: float
    timestamp: str
    paper_only: bool


@dataclass(frozen=True)
class VenueComparison:
    venue: str
    slippage_bps: float
    latency_ms: float
    fill_rate: float
    total_cost_bps: float
    quality_score: float
    rank: int


@dataclass(frozen=True)
class ExecutionQualityCycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    slippage_estimates: int
    tca_results: int
    avg_slippage_bps: float
    max_slippage_bps: float
    avg_total_cost_bps: float
    venues_compared: int
    best_venue: str


class ExecutionQualityEngine:
    """Slippage model, per-fill TCA, and venue comparison for crypto options."""

    def __init__(
        self,
        config: Optional[ExecutionQualityConfig32] = None,
        seed: int = 42,
    ) -> None:
        self.config = config or ExecutionQualityConfig32(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "ExecutionQualityEngine: paper_only must remain True (live path hard-gated)"
            )
        self.config = ExecutionQualityConfig32(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            cycles=int(self.config.cycles),
            slippage_bps_base=float(self.config.slippage_bps_base),
            slippage_bps_vol_mult=float(self.config.slippage_bps_vol_mult),
            latency_ms_base=float(self.config.latency_ms_base),
            fill_rate_base=float(self.config.fill_rate_base),
            maker_taker_fee_bps=float(self.config.maker_taker_fee_bps),
            notional_impact_bps=float(self.config.notional_impact_bps),
            min_fill_rate=float(self.config.min_fill_rate),
            max_slippage_bps=float(self.config.max_slippage_bps),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.results: List[ExecutionQualityCycleResult] = []
        self._slippage_history: List[SlippageEstimate] = []
        self._tca_history: List[TCAResult] = []

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def _seed_for(self, symbol: str, venue: str, cycle: int, tag: str) -> int:
        tagstr = f"{symbol}|{venue}|{cycle}|{tag}|{self.seed}"
        return int(hashlib.sha256(tagstr.encode()).hexdigest()[:8], 16) % (2**31)

    def estimate_slippage(
        self,
        symbol: str,
        side: str,
        notional_usd: float,
        venue: str,
        cycle: int,
        mid_price: float = 0.0,
    ) -> SlippageEstimate:
        seed = self._seed_for(symbol, venue, cycle, "slip")
        import random

        rng = random.Random(seed)
        notional = _finite(notional_usd)
        venue_idx = list(self.config.venues).index(venue) if venue in self.config.venues else 0
        venue_shift = float(venue_idx) * 0.25
        vol_shock = float(rng.gauss(0, 1))
        slippage_bps = float(
            min(
                self.config.max_slippage_bps,
                max(
                    0.0,
                    self.config.slippage_bps_base
                    + venue_shift
                    + self.config.slippage_bps_vol_mult * abs(vol_shock)
                    + self.config.notional_impact_bps * notional / 1e6,
                ),
            )
        )
        latency_ms = float(
            max(
                1.0,
                self.config.latency_ms_base + venue_idx * 8.0 + rng.gauss(0, 3.0),
            )
        )
        fill_rate = float(
            min(
                1.0,
                max(
                    self.config.min_fill_rate,
                    self.config.fill_rate_base - venue_idx * 0.01 + rng.gauss(0, 0.01),
                ),
            )
        )
        fee_bps = float(self.config.maker_taker_fee_bps)
        total_cost_bps = float(slippage_bps + fee_bps)
        mid = _finite(mid_price) if _finite(mid_price) > 0 else 1000.0
        side_mult = 1.0 if str(side).lower() == "buy" else -1.0
        fill_price = float(mid * (1.0 + side_mult * slippage_bps / 1e4))

        est = SlippageEstimate(
            symbol=symbol,
            side=str(side).lower(),
            venue=venue,
            notional_usd=notional,
            slippage_bps=slippage_bps,
            expected_fill_price=fill_price,
            latency_ms=latency_ms,
            fill_rate=fill_rate,
            fee_bps=fee_bps,
            total_cost_bps=total_cost_bps,
            paper_only=True,
        )
        _assert_finite(
            {
                "slippage_bps": est.slippage_bps,
                "expected_fill_price": est.expected_fill_price,
                "latency_ms": est.latency_ms,
                "fill_rate": est.fill_rate,
                "total_cost_bps": est.total_cost_bps,
            },
            "slippage_estimate",
        )
        self._slippage_history.append(est)
        return est

    def tca_per_fill(
        self,
        fill_id: str,
        symbol: str,
        side: str,
        venue: str,
        notional_usd: float,
        mid_price: float,
        fill_price: float,
        cycle: int,
    ) -> TCAResult:
        mid = _finite(mid_price)
        fpx = _finite(fill_price)
        notional = _finite(notional_usd)
        side_mult = 1.0 if str(side).lower() == "buy" else -1.0
        if mid > 0:
            realized_slippage_bps = float(
                (fpx - mid) / mid * 1e4 * side_mult
            )
        else:
            realized_slippage_bps = 0.0
        timing_cost_bps = float(abs(realized_slippage_bps) * 0.5)
        fee_bps = float(self.config.maker_taker_fee_bps)
        total_cost_bps = float(abs(realized_slippage_bps) + timing_cost_bps + fee_bps)

        tca = TCAResult(
            fill_id=fill_id,
            symbol=symbol,
            side=str(side).lower(),
            venue=venue,
            notional_usd=notional,
            realized_slippage_bps=realized_slippage_bps,
            timing_cost_bps=timing_cost_bps,
            fee_bps=fee_bps,
            total_cost_bps=total_cost_bps,
            mid_price=mid,
            fill_price=fpx,
            timestamp=_utc_now(),
            paper_only=True,
        )
        _assert_finite(
            {
                "realized_slippage_bps": tca.realized_slippage_bps,
                "timing_cost_bps": tca.timing_cost_bps,
                "fee_bps": tca.fee_bps,
                "total_cost_bps": tca.total_cost_bps,
                "mid_price": tca.mid_price,
                "fill_price": tca.fill_price,
            },
            "tca_result",
        )
        self._tca_history.append(tca)
        return tca

    def compare_venues(
        self,
        symbol: str,
        side: str,
        notional_usd: float,
        cycle: int,
        mid_price: float = 0.0,
    ) -> List[VenueComparison]:
        comps: List[VenueComparison] = []
        for venue in self.config.venues:
            est = self.estimate_slippage(symbol, side, notional_usd, venue, cycle, mid_price)
            comps.append(
                VenueComparison(
                    venue=venue,
                    slippage_bps=est.slippage_bps,
                    latency_ms=est.latency_ms,
                    fill_rate=est.fill_rate,
                    total_cost_bps=est.total_cost_bps,
                    quality_score=0.0,
                    rank=0,
                )
            )
        comps.sort(key=lambda c: (c.total_cost_bps, c.latency_ms, -c.fill_rate))
        for i, c in enumerate(comps):
            qs = float(
                min(
                    1.0,
                    max(
                        0.0,
                        1.0
                        - (c.total_cost_bps / max(self.config.max_slippage_bps, 1e-9)) * 0.5
                        - (c.latency_ms / 500.0) * 0.3
                        + (c.fill_rate - 0.5) * 0.2,
                    ),
                )
            )
            comps[i] = VenueComparison(
                venue=c.venue,
                slippage_bps=c.slippage_bps,
                latency_ms=c.latency_ms,
                fill_rate=c.fill_rate,
                total_cost_bps=c.total_cost_bps,
                quality_score=qs,
                rank=i + 1,
            )
        return comps

    def run_cycle(
        self,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
    ) -> ExecutionQualityCycleResult:
        state = dict(state or {})
        side = str(state.get("side", "buy"))
        notional = float(state.get("notional_usd", 50000.0))
        mid = float(state.get("mid_price", 4000.0))
        symbol = str(state.get("symbol", "ETH"))

        estimates: List[SlippageEstimate] = []
        for venue in self.config.venues:
            estimates.append(
                self.estimate_slippage(symbol, side, notional, venue, cycle, mid)
            )

        fills = state.get("fills", [])
        tca_results: List[TCAResult] = []
        for i, f in enumerate(fills):
            tca_results.append(
                self.tca_per_fill(
                    fill_id=str(f.get("fill_id", self._next_id("fill"))),
                    symbol=str(f.get("symbol", symbol)),
                    side=str(f.get("side", side)),
                    venue=str(f.get("venue", self.config.venues[0])),
                    notional_usd=float(f.get("notional_usd", notional)),
                    mid_price=float(f.get("mid_price", mid)),
                    fill_price=float(f.get("fill_price", mid)),
                    cycle=int(cycle),
                )
            )

        comps = self.compare_venues(symbol, side, notional, cycle, mid)
        best_venue = comps[0].venue if comps else self.config.venues[0]

        slip_vals = [e.slippage_bps for e in estimates]
        cost_vals = [e.total_cost_bps for e in estimates]
        result = ExecutionQualityCycleResult(
            cycle=int(cycle),
            timestamp=_utc_now(),
            paper_only=True,
            slippage_estimates=int(len(estimates)),
            tca_results=int(len(tca_results)),
            avg_slippage_bps=float(sum(slip_vals) / len(slip_vals)) if slip_vals else 0.0,
            max_slippage_bps=float(max(slip_vals)) if slip_vals else 0.0,
            avg_total_cost_bps=float(sum(cost_vals) / len(cost_vals)) if cost_vals else 0.0,
            venues_compared=int(len(comps)),
            best_venue=best_venue,
        )
        _assert_finite(
            {
                "avg_slippage_bps": result.avg_slippage_bps,
                "max_slippage_bps": result.max_slippage_bps,
                "avg_total_cost_bps": result.avg_total_cost_bps,
            },
            "execution_quality_cycle_result",
        )
        self.results.append(result)
        return result

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        cycles = int(cycles if cycles is not None else self.config.cycles)
        reports: List[Dict[str, Any]] = []
        for c in range(1, cycles + 1):
            res = self.run_cycle(c)
            reports.append(
                {
                    "cycle": res.cycle,
                    "slippage_estimates": res.slippage_estimates,
                    "tca_results": res.tca_results,
                    "avg_slippage_bps": res.avg_slippage_bps,
                    "max_slippage_bps": res.max_slippage_bps,
                    "avg_total_cost_bps": res.avg_total_cost_bps,
                    "venues_compared": res.venues_compared,
                    "best_venue": res.best_venue,
                }
            )
        return {
            "status": "ok",
            "paper_only": True,
            "cycles": cycles,
            "reports": reports,
            "total_slippage_estimates": int(sum(r["slippage_estimates"] for r in reports)),
            "total_tca_results": int(sum(r["tca_results"] for r in reports)),
            "final_avg_slippage_bps": float(reports[-1]["avg_slippage_bps"]) if reports else 0.0,
        }

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        from pathlib import Path

        Path(outdir).mkdir(parents=True, exist_ok=True)
        campaign = (
            self.run_campaign(self.config.cycles) if not self.results else {
                "status": "ok",
                "paper_only": True,
                "cycles": len(self.results),
                "reports": [
                    {
                        "cycle": r.cycle,
                        "slippage_estimates": r.slippage_estimates,
                        "tca_results": r.tca_results,
                        "avg_slippage_bps": r.avg_slippage_bps,
                        "max_slippage_bps": r.max_slippage_bps,
                        "avg_total_cost_bps": r.avg_total_cost_bps,
                        "venues_compared": r.venues_compared,
                        "best_venue": r.best_venue,
                    }
                    for r in self.results
                ],
                "total_slippage_estimates": int(sum(r.slippage_estimates for r in self.results)),
                "total_tca_results": int(sum(r.tca_results for r in self.results)),
                "final_avg_slippage_bps": float(self.results[-1].avg_slippage_bps) if self.results else 0.0,
            }
        )
        last = self.results[-1] if self.results else None
        report = {
            "report": "PHASE32_EXECUTION_QUALITY_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": int(len(self.results)),
            "total_slippage_estimates": int(campaign["total_slippage_estimates"]),
            "total_tca_results": int(campaign["total_tca_results"]),
            "final_avg_slippage_bps": float(campaign["final_avg_slippage_bps"]),
            "config": asdict(self.config),
            "last_cycle": int(last.cycle) if last else 0,
            "last_avg_slippage_bps": float(last.avg_slippage_bps) if last else 0.0,
            "last_max_slippage_bps": float(last.max_slippage_bps) if last else 0.0,
            "cycle_results": [
                {
                    "cycle": r.cycle,
                    "slippage_estimates": r.slippage_estimates,
                    "tca_results": r.tca_results,
                    "avg_slippage_bps": r.avg_slippage_bps,
                    "max_slippage_bps": r.max_slippage_bps,
                    "avg_total_cost_bps": r.avg_total_cost_bps,
                    "venues_compared": r.venues_compared,
                    "best_venue": r.best_venue,
                }
                for r in self.results
            ],
            "venue_rankings": [
                {
                    "venue": c.venue,
                    "rank": c.rank,
                    "slippage_bps": c.slippage_bps,
                    "latency_ms": c.latency_ms,
                    "fill_rate": c.fill_rate,
                    "total_cost_bps": c.total_cost_bps,
                    "quality_score": c.quality_score,
                }
                for c in self.compare_venues("ETH", "buy", 50000.0, 1, 4000.0)
            ],
        }
        _assert_finite(report, "phase32_execution_quality_report")
        rep_json = Path(outdir) / "PHASE32_EXECUTION_QUALITY_REPORT.json"
        rep_md = Path(outdir) / "PHASE32_EXECUTION_QUALITY_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE32_EXECUTION_QUALITY_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Seed: {report['seed']}\nCycles: {report['cycles']}\n"
            f"Total slippage estimates: {report['total_slippage_estimates']}\n"
            f"Total TCA results: {report['total_tca_results']}\n"
            f"Final avg slippage bps: {report['final_avg_slippage_bps']:.4f}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
            "report": report,
        }


__all__ = [
    "ExecutionQualityEngine",
    "ExecutionQualityConfig32",
    "SlippageEstimate",
    "TCAResult",
    "VenueComparison",
    "ExecutionQualityCycleResult",
]
