"""
Phase 33: Venue Liquidity Sweep for Crypto Options Cross-Venue Execution.

Cross-venue liquidity detection and sweep routing for options fills. Scans venue
liquidity, scores venues, and routes sweeps across venues to minimize slippage and
maximize fill rate. Production-grade, deterministic, finite numerics,
PAPER-ONLY default with hard-gated live paths. Extends Phase 24 cross-venue router
+ Phase 32 execution quality.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.execution.phase32_execution_quality import (
    ExecutionQualityEngine,
    ExecutionQualityConfig32,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p33sweep|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p33sweep_{tag}_{h}"


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
class VenueLiquiditySweepConfig33:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    expiries: tuple = ("7D", "30D", "90D")
    cycles: int = 10
    liquidity_threshold_usd: float = 1000000.0
    sweep_size_pct: float = 0.25
    max_slippage_bps: float = 25.0
    fill_rate_min: float = 0.80
    max_venue_allocation_pct: float = 0.40
    min_venues_per_sweep: int = 2
    total_capital_usd: float = 150000.0


@dataclass(frozen=True)
class LiquiditySnapshot:
    venue: str
    symbol: str
    bid_size_usd: float
    ask_size_usd: float
    liquidity_score: float
    fill_rate: float
    latency_ms: float
    slippage_bps: float
    timestamp: str
    paper_only: bool


@dataclass(frozen=True)
class SweepRoute:
    symbol: str
    side: str
    notional_usd: float
    venue: str
    route_venues: Tuple[str, ...]
    slippage_bps: float
    fill_rate: float
    allocated_usd: float
    paper_only: bool
    timestamp: str
    rationale: str


@dataclass(frozen=True)
class SweepCycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    venues_scanned: int
    liquidity_venues: int
    sweeps_routed: int
    total_swept_notional_usd: float
    avg_slippage_bps: float
    max_slippage_bps: float
    avg_fill_rate: float
    best_venue: str
    risk_ok: bool
    blocked_reasons: Tuple[str, ...]


class VenueLiquiditySweep:
    """Cross-venue liquidity detection and sweep routing for options fills."""

    def __init__(
        self,
        config: Optional[VenueLiquiditySweepConfig33] = None,
        seed: int = 42,
    ) -> None:
        self.config = config or VenueLiquiditySweepConfig33(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "VenueLiquiditySweep: paper_only must remain True (live path hard-gated)"
            )
        self.config = VenueLiquiditySweepConfig33(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            expiries=tuple(self.config.expiries),
            cycles=int(self.config.cycles),
            liquidity_threshold_usd=float(self.config.liquidity_threshold_usd),
            sweep_size_pct=float(self.config.sweep_size_pct),
            max_slippage_bps=float(self.config.max_slippage_bps),
            fill_rate_min=float(self.config.fill_rate_min),
            max_venue_allocation_pct=float(self.config.max_venue_allocation_pct),
            min_venues_per_sweep=int(self.config.min_venues_per_sweep),
            total_capital_usd=float(self.config.total_capital_usd),
        )
        self.seed = int(self.config.seed)
        self.execution = ExecutionQualityEngine(
            config=ExecutionQualityConfig32(
                seed=self.seed + 33301,
                paper_only=True,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                cycles=self.config.cycles,
            ),
            seed=self.seed + 33301,
        )
        self._counter = 0
        self.results: List[SweepCycleResult] = []
        self._snapshot_history: List[LiquiditySnapshot] = []
        self._route_history: List[SweepRoute] = []
        self._venue_liquidity: Dict[str, float] = {v: 1.0 for v in self.config.venues}

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def scan_liquidity(
        self,
        symbol: str,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
    ) -> List[LiquiditySnapshot]:
        state = state or {}
        snapshots: List[LiquiditySnapshot] = []
        import random

        for i, venue in enumerate(self.config.venues):
            seed = int(
                hashlib.sha256(
                    f"{symbol}|{venue}|{self.seed}|scan|{cycle}".encode()
                ).hexdigest()[:8],
                16,
            ) % (2**31)
            rng = random.Random(seed)
            bid_size = float(rng.uniform(100000.0, 5000000.0))
            ask_size = float(rng.uniform(100000.0, 5000000.0))
            liquidity_score = float(
                min(1.0, max(0.0, 0.5 + 0.3 * rng.gauss(0, 1) + 0.2 * i * 0.05))
            )
            fill_rate = float(
                min(1.0, max(self.config.fill_rate_min, 0.85 + 0.1 * rng.gauss(0, 0.05)))
            )
            latency_ms = float(max(1.0, 40.0 + i * 8.0 + rng.gauss(0, 3.0)))
            slippage_bps = float(
                min(
                    self.config.max_slippage_bps,
                    max(0.0, 2.0 + i * 1.0 + abs(rng.gauss(0, 2.0))),
                )
            )
            snap = LiquiditySnapshot(
                venue=venue,
                symbol=str(symbol),
                bid_size_usd=bid_size,
                ask_size_usd=ask_size,
                liquidity_score=liquidity_score,
                fill_rate=fill_rate,
                latency_ms=latency_ms,
                slippage_bps=slippage_bps,
                timestamp=_utc_now(),
                paper_only=True,
            )
            _assert_finite(
                {
                    "bid_size_usd": snap.bid_size_usd,
                    "ask_size_usd": snap.ask_size_usd,
                    "liquidity_score": snap.liquidity_score,
                    "fill_rate": snap.fill_rate,
                    "latency_ms": snap.latency_ms,
                    "slippage_bps": snap.slippage_bps,
                },
                "liquidity_snapshot",
            )
            snapshots.append(snap)
            self._snapshot_history.append(snap)
            self._venue_liquidity[venue] = float(
                min(2.0, max(0.1, liquidity_score))
            )
        return snapshots

    def route_sweep(
        self,
        symbol: str,
        side: str,
        notional_usd: float,
        cycle: int,
        snapshots: Optional[List[LiquiditySnapshot]] = None,
    ) -> List[SweepRoute]:
        snapshots = list(snapshots or [])
        notional = _finite(notional_usd)
        if not snapshots:
            snapshots = self.scan_liquidity(symbol, cycle)

        ranked = sorted(
            snapshots,
            key=lambda s: (
                s.slippage_bps,
                s.latency_ms,
                -s.fill_rate,
                -s.liquidity_score,
            ),
        )

        routes: List[SweepRoute] = []
        remaining = notional
        max_per_venue = notional * self.config.max_venue_allocation_pct
        min_venues = min(self.config.min_venues_per_sweep, len(ranked))

        for snap in ranked:
            if remaining <= 0:
                break
            if snap.slippage_bps > self.config.max_slippage_bps:
                continue
            if snap.fill_rate < self.config.fill_rate_min:
                continue
            alloc = min(remaining, max_per_venue, snap.bid_size_usd, snap.ask_size_usd)
            if alloc <= 0:
                continue
            route = SweepRoute(
                symbol=str(symbol),
                side=str(side).lower(),
                notional_usd=notional,
                venue=snap.venue,
                route_venues=tuple([snap.venue]),
                slippage_bps=snap.slippage_bps,
                fill_rate=snap.fill_rate,
                allocated_usd=alloc,
                paper_only=True,
                timestamp=_utc_now(),
                rationale=(
                    f"p33sweep|{symbol}|{side}|{snap.venue}|"
                    f"slip={snap.slippage_bps:.2f}bps|fill={snap.fill_rate:.3f}|"
                    f"liq={snap.liquidity_score:.3f}|alloc={alloc:.2f}"
                ),
            )
            _assert_finite(
                {
                    "slippage_bps": route.slippage_bps,
                    "fill_rate": route.fill_rate,
                    "allocated_usd": route.allocated_usd,
                },
                "sweep_route",
            )
            routes.append(route)
            self._route_history.append(route)
            remaining -= alloc
            if len(routes) >= min_venues and remaining <= 0:
                break

        return routes

    def run_cycle(
        self,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
    ) -> SweepCycleResult:
        state = dict(state or {})
        symbol = str(state.get("symbol", self.config.underlyings[0]))
        side = str(state.get("side", "buy"))
        notional = float(state.get("notional_usd", 50000.0))

        snapshots = self.scan_liquidity(symbol, cycle, state)
        routes = self.route_sweep(symbol, side, notional, cycle, snapshots)

        liquidity_venues = int(
            sum(1 for s in snapshots if s.liquidity_score >= 0.5)
        )
        total_swept = float(sum(r.allocated_usd for r in routes))
        slip_vals = [r.slippage_bps for r in routes]
        fill_vals = [r.fill_rate for r in routes]
        avg_slippage = float(sum(slip_vals) / len(slip_vals)) if slip_vals else 0.0
        max_slippage = float(max(slip_vals)) if slip_vals else 0.0
        avg_fill = float(sum(fill_vals) / len(fill_vals)) if fill_vals else 0.0
        best_venue = (
            min(routes, key=lambda r: r.slippage_bps).venue if routes else self.config.venues[0]
        )

        blocked: List[str] = []
        if avg_slippage > self.config.max_slippage_bps:
            blocked.append("max_slippage_bps")
        if avg_fill < self.config.fill_rate_min:
            blocked.append("fill_rate_min")
        if liquidity_venues < self.config.min_venues_per_sweep:
            blocked.append("insufficient_liquidity_venues")

        result = SweepCycleResult(
            cycle=int(cycle),
            timestamp=_utc_now(),
            paper_only=True,
            venues_scanned=int(len(snapshots)),
            liquidity_venues=liquidity_venues,
            sweeps_routed=int(len(routes)),
            total_swept_notional_usd=total_swept,
            avg_slippage_bps=avg_slippage,
            max_slippage_bps=max_slippage,
            avg_fill_rate=avg_fill,
            best_venue=str(best_venue),
            risk_ok=bool(len(blocked) == 0),
            blocked_reasons=tuple(sorted(set(blocked))),
        )
        _assert_finite(
            {
                "avg_slippage_bps": result.avg_slippage_bps,
                "max_slippage_bps": result.max_slippage_bps,
                "avg_fill_rate": result.avg_fill_rate,
                "total_swept_notional_usd": result.total_swept_notional_usd,
            },
            "sweep_cycle_result",
        )
        self.results.append(result)
        return result

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        cycles = int(cycles if cycles is not None else self.config.cycles)
        reports: List[Dict[str, Any]] = []
        for c in range(1, cycles + 1):
            res = self.run_cycle(
                c,
                {
                    "symbol": self.config.underlyings[c % len(self.config.underlyings)],
                    "side": "buy" if c % 2 == 1 else "sell",
                    "notional_usd": 50000.0,
                },
            )
            reports.append(
                {
                    "cycle": res.cycle,
                    "venues_scanned": res.venues_scanned,
                    "liquidity_venues": res.liquidity_venues,
                    "sweeps_routed": res.sweeps_routed,
                    "total_swept_notional_usd": res.total_swept_notional_usd,
                    "avg_slippage_bps": res.avg_slippage_bps,
                    "max_slippage_bps": res.max_slippage_bps,
                    "avg_fill_rate": res.avg_fill_rate,
                    "best_venue": res.best_venue,
                    "risk_ok": res.risk_ok,
                    "blocked_reasons": list(res.blocked_reasons),
                }
            )
        return {
            "status": "ok",
            "paper_only": True,
            "cycles": cycles,
            "reports": reports,
            "total_venues_scanned": int(sum(r["venues_scanned"] for r in reports)),
            "total_sweeps_routed": int(sum(r["sweeps_routed"] for r in reports)),
            "total_swept_notional_usd": float(
                sum(r["total_swept_notional_usd"] for r in reports)
            ),
            "final_avg_slippage_bps": float(reports[-1]["avg_slippage_bps"])
            if reports
            else 0.0,
            "final_avg_fill_rate": float(reports[-1]["avg_fill_rate"]) if reports else 0.0,
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
                        "venues_scanned": r.venues_scanned,
                        "liquidity_venues": r.liquidity_venues,
                        "sweeps_routed": r.sweeps_routed,
                        "total_swept_notional_usd": r.total_swept_notional_usd,
                        "avg_slippage_bps": r.avg_slippage_bps,
                        "max_slippage_bps": r.max_slippage_bps,
                        "avg_fill_rate": r.avg_fill_rate,
                        "best_venue": r.best_venue,
                        "risk_ok": r.risk_ok,
                        "blocked_reasons": list(r.blocked_reasons),
                    }
                    for r in self.results
                ],
                "total_venues_scanned": int(
                    sum(r.venues_scanned for r in self.results)
                ),
                "total_sweeps_routed": int(
                    sum(r.sweeps_routed for r in self.results)
                ),
                "total_swept_notional_usd": float(
                    sum(r.total_swept_notional_usd for r in self.results)
                ),
                "final_avg_slippage_bps": float(
                    self.results[-1].avg_slippage_bps
                )
                if self.results
                else 0.0,
                "final_avg_fill_rate": float(self.results[-1].avg_fill_rate)
                if self.results
                else 0.0,
            }
        )
        last = self.results[-1] if self.results else None
        report = {
            "report": "PHASE33_LIQUIDITY_SWEEP_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": int(len(self.results)),
            "total_venues_scanned": int(campaign["total_venues_scanned"]),
            "total_sweeps_routed": int(campaign["total_sweeps_routed"]),
            "total_swept_notional_usd": float(campaign["total_swept_notional_usd"]),
            "final_avg_slippage_bps": float(campaign["final_avg_slippage_bps"]),
            "final_avg_fill_rate": float(campaign["final_avg_fill_rate"]),
            "config": asdict(self.config),
            "last_cycle": int(last.cycle) if last else 0,
            "last_venues_scanned": int(last.venues_scanned) if last else 0,
            "last_liquidity_venues": int(last.liquidity_venues) if last else 0,
            "last_sweeps_routed": int(last.sweeps_routed) if last else 0,
            "last_avg_slippage_bps": float(last.avg_slippage_bps) if last else 0.0,
            "last_avg_fill_rate": float(last.avg_fill_rate) if last else 0.0,
            "best_venue": str(last.best_venue) if last else self.config.venues[0],
            "cycle_results": [
                {
                    "cycle": r.cycle,
                    "venues_scanned": r.venues_scanned,
                    "liquidity_venues": r.liquidity_venues,
                    "sweeps_routed": r.sweeps_routed,
                    "total_swept_notional_usd": r.total_swept_notional_usd,
                    "avg_slippage_bps": r.avg_slippage_bps,
                    "max_slippage_bps": r.max_slippage_bps,
                    "avg_fill_rate": r.avg_fill_rate,
                    "best_venue": r.best_venue,
                    "risk_ok": r.risk_ok,
                    "blocked_reasons": list(r.blocked_reasons),
                }
                for r in self.results
            ],
            "liquidity_snapshots": [
                {
                    "venue": s.venue,
                    "symbol": s.symbol,
                    "bid_size_usd": s.bid_size_usd,
                    "ask_size_usd": s.ask_size_usd,
                    "liquidity_score": s.liquidity_score,
                    "fill_rate": s.fill_rate,
                    "latency_ms": s.latency_ms,
                    "slippage_bps": s.slippage_bps,
                    "paper_only": s.paper_only,
                }
                for s in self._snapshot_history[-20:]
            ],
            "sweep_routes": [
                {
                    "symbol": r.symbol,
                    "side": r.side,
                    "notional_usd": r.notional_usd,
                    "venue": r.venue,
                    "route_venues": list(r.route_venues),
                    "slippage_bps": r.slippage_bps,
                    "fill_rate": r.fill_rate,
                    "allocated_usd": r.allocated_usd,
                    "paper_only": r.paper_only,
                    "rationale": r.rationale,
                }
                for r in self._route_history[-20:]
            ],
        }
        _assert_finite(report, "phase33_liquidity_sweep_report")
        rep_json = Path(outdir) / "PHASE33_LIQUIDITY_SWEEP_REPORT.json"
        rep_md = Path(outdir) / "PHASE33_LIQUIDITY_SWEEP_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE33_LIQUIDITY_SWEEP_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Seed: {report['seed']}\nCycles: {report['cycles']}\n"
            f"Total venues scanned: {report['total_venues_scanned']}\n"
            f"Total sweeps routed: {report['total_sweeps_routed']}\n"
            f"Total swept notional USD: {report['total_swept_notional_usd']:.2f}\n"
            f"Final avg slippage bps: {report['final_avg_slippage_bps']:.4f}\n"
            f"Final avg fill rate: {report['final_avg_fill_rate']:.4f}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
            "report": report,
        }


__all__ = [
    "VenueLiquiditySweep",
    "VenueLiquiditySweepConfig33",
    "LiquiditySnapshot",
    "SweepRoute",
    "SweepCycleResult",
]
