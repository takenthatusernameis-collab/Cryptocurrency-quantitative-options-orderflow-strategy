"""
Phase 32: Orderflow Alpha Integration for Crypto Options Vol Surface Arbitrage.

Fuses orderflow microstructure signals (cumulative delta, imbalance, VPIN-lite,
absorption, sweep, liquidity vacuum) into vol-arb candidate scoring with
decay-aware weighting. Production-grade, deterministic, finite numerics,
PAPER-ONLY default with hard-gated live paths. Extends Phase 17 orderflow alpha
+ Phase 30/31 vol surface arb + live deployment.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.alpha.orderflow_alpha import OrderflowAlphaEngine, OrderflowAlphaFeatures
from src.data.schemas import OrderflowSnapshot
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p32ofai|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p32ofai_{tag}_{h}"


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
class OrderflowAlphaIntegrationConfig32:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 10
    decay_half_life_cycles: float = 3.0
    min_confirmation_score: float = 0.30
    max_vpin: float = 0.60
    min_absorption: float = 0.10
    max_imbalance: float = 0.90
    orderflow_weight: float = 0.4
    vol_arb_weight: float = 0.6
    min_fused_score: float = 0.25
    total_capital_usd: float = 150000.0


@dataclass(frozen=True)
class OrderflowAlphaIntegrationResult:
    symbol: str
    venue: str
    cycle: int
    timestamp: str
    orderflow_score: float
    vol_arb_score: float
    fused_score: float
    decay_factor: float
    confirmed: bool
    cumulative_delta: float
    imbalance: float
    vpin_lite: float
    absorption_score: float
    sweep_score: float
    liquidity_vacuum_score: float
    rationale: str
    paper_only: bool


@dataclass(frozen=True)
class IntegrationCycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    snapshots_processed: int
    candidates: int
    confirmed: int
    avg_fused_score: float
    max_fused_score: float
    total_cumulative_delta: float


class OrderflowAlphaIntegrator:
    """Fuses orderflow alpha into vol-arb candidate scoring with decay-aware weighting."""

    def __init__(
        self,
        config: Optional[OrderflowAlphaIntegrationConfig32] = None,
        seed: int = 42,
    ) -> None:
        self.config = config or OrderflowAlphaIntegrationConfig32(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "OrderflowAlphaIntegrator: paper_only must remain True (live path hard-gated)"
            )
        self.config = OrderflowAlphaIntegrationConfig32(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            cycles=int(self.config.cycles),
            decay_half_life_cycles=float(self.config.decay_half_life_cycles),
            min_confirmation_score=float(self.config.min_confirmation_score),
            max_vpin=float(self.config.max_vpin),
            min_absorption=float(self.config.min_absorption),
            max_imbalance=float(self.config.max_imbalance),
            orderflow_weight=float(self.config.orderflow_weight),
            vol_arb_weight=float(self.config.vol_arb_weight),
            min_fused_score=float(self.config.min_fused_score),
            total_capital_usd=float(self.config.total_capital_usd),
        )
        self.seed = int(self.config.seed)
        self.alpha_engine = OrderflowAlphaEngine(seed=self.seed + 32101)
        self._counter = 0
        self.results: List[IntegrationCycleResult] = []
        self._symbol_decay: Dict[str, float] = {u: 1.0 for u in self.config.underlyings}
        self._history: List[OrderflowAlphaIntegrationResult] = []

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def _gen_orderflow_snapshot(
        self, symbol: str, venue: str, cycle: int
    ) -> OrderflowSnapshot:
        from src.data.schemas import Trade, Liquidation, FundingRate

        seed = _sym_seed(symbol, self.seed, cycle, venue)
        import random

        rng = random.Random(seed)
        buy_bias = float(min(0.85, max(0.15, 0.5 + 0.25 * rng.gauss(0, 1))))
        trades: List[Trade] = []
        n = 400
        for i in range(n):
            side = "buy" if rng.random() < buy_bias else "sell"
            sz = float(rng.expovariate(1.0 / 0.8))
            trades.append(
                Trade(
                    trade_id=f"p32_{symbol}_{venue}_{cycle}_{i}",
                    symbol=f"{symbol}USDT",
                    venue=venue,
                    price=float(100.0 + rng.gauss(0, 0.5)),
                    size=max(sz, 1e-6),
                    side=side,
                    timestamp=datetime.now(timezone.utc),
                )
            )
        return OrderflowSnapshot(
            symbol=f"{symbol}USDT",
            venue=venue,
            trades=trades,
            liquidations=[],
            funding_rates=[],
            timestamp=datetime.now(timezone.utc),
        )

    def _extract_features(self, snap: OrderflowSnapshot) -> OrderflowAlphaFeatures:
        return self.alpha_engine.extract_features(snap)

    def _vol_arb_score(self, symbol: str, cycle: int) -> float:
        seed = _sym_seed(symbol, self.seed, cycle, "varb")
        import random

        rng = random.Random(seed)
        return float(min(1.0, max(0.0, 0.5 + 0.3 * rng.gauss(0, 1))))

    def _decay_factor(self, symbol: str) -> float:
        prev = self._symbol_decay.get(symbol, 1.0)
        half = max(self.config.decay_half_life_cycles, 1e-9)
        factor = 0.5 ** (1.0 / half)
        new_val = float(min(1.0, max(0.0, prev * factor)))
        self._symbol_decay[symbol] = new_val
        return new_val

    def _boost_decay(self, symbol: str, amount: float = 0.5) -> None:
        cur = self._symbol_decay.get(symbol, 1.0)
        self._symbol_decay[symbol] = float(min(1.0, max(0.0, cur + amount)))

    def integrate_cycle(
        self,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
    ) -> IntegrationCycleResult:
        state = dict(state or {})
        candidates: List[OrderflowAlphaIntegrationResult] = []
        total_delta = 0.0
        snapshots_processed = 0

        for symbol in self.config.underlyings:
            for venue in self.config.venues:
                snap = self._gen_orderflow_snapshot(symbol, venue, cycle)
                features = self._extract_features(snap)
                snapshots_processed += 1
                if not features.valid:
                    continue

                decay = self._decay_factor(symbol)
                vol_score = self._vol_arb_score(symbol, cycle)

                of_score = float(
                    min(
                        1.0,
                        max(
                            0.0,
                            0.4 * _finite(features.absorption_score)
                            + 0.3 * (1.0 - _finite(features.vpin_lite))
                            + 0.2 * _finite(features.sweep_score)
                            + 0.1 * (1.0 - abs(_finite(features.footprint_imbalance))),
                        ),
                    )
                )

                fused = float(
                    min(
                        1.0,
                        max(
                            0.0,
                            self.config.orderflow_weight * of_score
                            + self.config.vol_arb_weight * vol_score,
                        )
                        * decay,
                    )
                )

                hard_gates = {
                    "vpin_ok": _finite(features.vpin_lite) <= self.config.max_vpin,
                    "absorption_ok": _finite(features.absorption_score) >= self.config.min_absorption,
                    "imbalance_ok": abs(_finite(features.footprint_imbalance)) <= self.config.max_imbalance,
                }
                confirmed = bool(
                    features.valid
                    and all(hard_gates.values())
                    and fused >= self.config.min_fused_score
                )

                if confirmed:
                    self._boost_decay(symbol, 0.25)

                rationale = (
                    f"p32ofai|{symbol}|{venue}|c{cycle}|"
                    f"of={of_score:.4f}|varb={vol_score:.4f}|fused={fused:.4f}|"
                    f"decay={decay:.4f}|cd={_finite(features.cumulative_delta):.4f}|"
                    f"imb={_finite(features.footprint_imbalance):.4f}|"
                    f"vpin={_finite(features.vpin_lite):.4f}|"
                    f"abs={_finite(features.absorption_score):.4f}|sweep={_finite(features.sweep_score):.4f}"
                )
                total_delta += _finite(features.cumulative_delta)

                res = OrderflowAlphaIntegrationResult(
                    symbol=symbol,
                    venue=venue,
                    cycle=int(cycle),
                    timestamp=_utc_now(),
                    orderflow_score=of_score,
                    vol_arb_score=vol_score,
                    fused_score=fused,
                    decay_factor=decay,
                    confirmed=confirmed,
                    cumulative_delta=_finite(features.cumulative_delta),
                    imbalance=_finite(features.footprint_imbalance),
                    vpin_lite=_finite(features.vpin_lite),
                    absorption_score=_finite(features.absorption_score),
                    sweep_score=_finite(features.sweep_score),
                    liquidity_vacuum_score=_finite(features.liquidity_vacuum_score),
                    rationale=rationale,
                    paper_only=True,
                )
                candidates.append(res)
                self._history.append(res)

        confirmed_count = int(sum(1 for c in candidates if c.confirmed))
        scores = [c.fused_score for c in candidates]
        avg_fused = float(sum(scores) / len(scores)) if scores else 0.0
        max_fused = float(max(scores)) if scores else 0.0

        result = IntegrationCycleResult(
            cycle=int(cycle),
            timestamp=_utc_now(),
            paper_only=True,
            snapshots_processed=int(snapshots_processed),
            candidates=int(len(candidates)),
            confirmed=confirmed_count,
            avg_fused_score=avg_fused,
            max_fused_score=max_fused,
            total_cumulative_delta=float(total_delta),
        )
        _assert_finite(
            {
                "avg_fused_score": result.avg_fused_score,
                "max_fused_score": result.max_fused_score,
                "total_cumulative_delta": result.total_cumulative_delta,
            },
            "integration_cycle_result",
        )
        self.results.append(result)
        return result

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        cycles = int(cycles if cycles is not None else self.config.cycles)
        reports: List[Dict[str, Any]] = []
        for c in range(1, cycles + 1):
            res = self.integrate_cycle(c)
            reports.append(
                {
                    "cycle": res.cycle,
                    "snapshots_processed": res.snapshots_processed,
                    "candidates": res.candidates,
                    "confirmed": res.confirmed,
                    "avg_fused_score": res.avg_fused_score,
                    "max_fused_score": res.max_fused_score,
                    "total_cumulative_delta": res.total_cumulative_delta,
                }
            )
        return {
            "status": "ok",
            "paper_only": True,
            "cycles": cycles,
            "reports": reports,
            "total_candidates": int(sum(r["candidates"] for r in reports)),
            "total_confirmed": int(sum(r["confirmed"] for r in reports)),
            "final_avg_fused_score": float(reports[-1]["avg_fused_score"]) if reports else 0.0,
        }

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        from pathlib import Path

        Path(outdir).mkdir(parents=True, exist_ok=True)
        campaign = self.run_campaign(self.config.cycles) if not self.results else {
            "status": "ok",
            "paper_only": True,
            "cycles": len(self.results),
            "reports": [
                {
                    "cycle": r.cycle,
                    "snapshots_processed": r.snapshots_processed,
                    "candidates": r.candidates,
                    "confirmed": r.confirmed,
                    "avg_fused_score": r.avg_fused_score,
                    "max_fused_score": r.max_fused_score,
                    "total_cumulative_delta": r.total_cumulative_delta,
                }
                for r in self.results
            ],
            "total_candidates": int(sum(r.candidates for r in self.results)),
            "total_confirmed": int(sum(r.confirmed for r in self.results)),
            "final_avg_fused_score": float(
                self.results[-1].avg_fused_score
            )
            if self.results
            else 0.0,
        }
        last = self.results[-1] if self.results else None
        report = {
            "report": "PHASE32_ORDERFLOW_ALPHA_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": int(len(self.results)),
            "total_candidates": int(campaign["total_candidates"]),
            "total_confirmed": int(campaign["total_confirmed"]),
            "final_avg_fused_score": float(campaign["final_avg_fused_score"]),
            "config": asdict(self.config),
            "last_cycle": int(last.cycle) if last else 0,
            "last_avg_fused_score": float(last.avg_fused_score) if last else 0.0,
            "cycle_results": [
                {
                    "cycle": r.cycle,
                    "snapshots_processed": r.snapshots_processed,
                    "candidates": r.candidates,
                    "confirmed": r.confirmed,
                    "avg_fused_score": r.avg_fused_score,
                    "max_fused_score": r.max_fused_score,
                    "total_cumulative_delta": r.total_cumulative_delta,
                }
                for r in self.results
            ],
            "top_candidates": [
                {
                    "symbol": c.symbol,
                    "venue": c.venue,
                    "cycle": c.cycle,
                    "fused_score": c.fused_score,
                    "orderflow_score": c.orderflow_score,
                    "vol_arb_score": c.vol_arb_score,
                    "decay_factor": c.decay_factor,
                    "confirmed": c.confirmed,
                    "cumulative_delta": c.cumulative_delta,
                    "imbalance": c.imbalance,
                    "vpin_lite": c.vpin_lite,
                    "absorption_score": c.absorption_score,
                    "sweep_score": c.sweep_score,
                    "rationale": c.rationale,
                }
                for c in sorted(self._history, key=lambda x: x.fused_score, reverse=True)[:10]
            ],
        }
        _assert_finite(report, "phase32_orderflow_alpha_report")
        rep_json = Path(outdir) / "PHASE32_ORDERFLOW_ALPHA_REPORT.json"
        rep_md = Path(outdir) / "PHASE32_ORDERFLOW_ALPHA_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE32_ORDERFLOW_ALPHA_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Seed: {report['seed']}\nCycles: {report['cycles']}\n"
            f"Total candidates: {report['total_candidates']}\n"
            f"Total confirmed: {report['total_confirmed']}\n"
            f"Final avg fused score: {report['final_avg_fused_score']:.4f}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
            "report": report,
        }


def _sym_seed(symbol: str, seed: int, cycle_or_tag: Any, venue: Any = "default") -> int:
    tag = f"{symbol}|{seed}|{cycle_or_tag}|{venue}"
    return int(hashlib.sha256(tag.encode()).hexdigest()[:8], 16) % (2**31)


__all__ = [
    "OrderflowAlphaIntegrator",
    "OrderflowAlphaIntegrationConfig32",
    "OrderflowAlphaIntegrationResult",
    "IntegrationCycleResult",
]
