"""
Phase 28: Cross-Venue Market Making Paper Loop (crypto options + orderflow).
Integrates cross-venue market making + inventory rebalancing + router/healer/observability
(Phases 17-27), paper-only gated, per-cycle TCA + fill-quality capture.
Production-grade, deterministic, paper-only safe.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json
import math
import random
from pathlib import Path

from src.execution.phase24_cross_venue_router import CrossVenueRouter
from src.execution.phase28_cross_venue_mm import CrossVenueMarketMaker, CrossVenueMMConfig, VenueQuote
from src.monitoring.phase18_observability import Phase18Observability
from src.risk.phase28_inventory_rebalance import InventoryRebalancer, InventoryRebalanceConfig, VenueInventory
from src.options.phase27_market_maker import Greeks, Fill
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p28loop|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p28loop_{tag}_{h}"


@dataclass(frozen=True)
class CVMMPaperLoopConfig:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    expiries: tuple = ("7D", "30D", "90D")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 10
    enforce_gates: bool = True


@dataclass(frozen=True)
class CycleResult:
    cycle: int
    symbol: str
    quotes_placed: int
    fills: int
    cross_venue_dislocations: int
    rebalance_orders: int
    avg_spread_bps: float
    inventory_utilization: float
    risk_passed: bool
    tca_fill_quality_bps: float
    paper_only: bool
    timestamp: str


class CVMMPaperLoop:
    def __init__(self, config: Optional[CVMMPaperLoopConfig] = None, seed: int = 42):
        self.config = config or CVMMPaperLoopConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("CVMMPaperLoop: paper_only must remain True (live path hard-gated)")
        self.config = CVMMPaperLoopConfig(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            expiries=tuple(self.config.expiries),
            venues=tuple(self.config.venues),
            cycles=int(self.config.cycles),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        mm_cfg = CrossVenueMMConfig(
            seed=self.seed,
            paper_only=True,
            underlyings=self.config.underlyings,
            expiries=self.config.expiries,
            venues=self.config.venues,
            enforce_gates=self.config.enforce_gates,
        )
        inv_cfg = InventoryRebalanceConfig(
            seed=self.seed,
            paper_only=True,
            underlyings=self.config.underlyings,
            venues=self.config.venues,
            enforce_hard_limits=self.config.enforce_gates,
        )
        self.cvmm = CrossVenueMarketMaker(config=mm_cfg)
        self.router = CrossVenueRouter(seed=self.seed + 40000)
        self.rebalancer = InventoryRebalancer(config=inv_cfg)
        self.obs = Phase18Observability(seed=self.seed + 50000, paper_only=True)
        self.cycle_count = 0
        self.results: List[CycleResult] = []
        self.audit: List[Dict[str, Any]] = []

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def _next_id(self, tag: str) -> str:
        self._counter += 1 if hasattr(self, "_counter") else 1
        if not hasattr(self, "_counter"):
            self._counter = 1
        h = hashlib.sha256(f"{self.seed}|p28loop|{tag}|{self._counter}".encode()).hexdigest()[:12]
        return f"p28loop_{tag}_{h}"

    def run_cycle(
        self,
        cycle: int,
        tape: Optional[List[Dict[str, Any]]] = None,
        recent_trades: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        if not self.config.paper_only:
            raise RuntimeError("hard gate: live disabled")
        tape = tape if tape is not None else [{"bid_vol": 10, "ask_vol": 12, "toxicity": 0.1}, {"bid_vol": 15, "ask_vol": 11, "toxicity": 0.05}]
        recent_trades = recent_trades if recent_trades is not None else [
            {"aggressor_side": "buy", "qty": 100.0},
            {"aggressor_side": "sell", "qty": 60.0},
        ]
        rng = random.Random(self.seed + 28000 + cycle)
        strike_map = {"BTC": 100000.0, "ETH": 4000.0, "SOL": 150.0, "XRP": 50.0}
        mid_map = {"BTC": 100000.0, "ETH": 4000.0, "SOL": 150.0, "XRP": 50.0}
        total_quotes = 0
        total_fills = 0
        total_spread = 0.0
        total_dislocations = 0
        total_rebalance_orders = 0
        tca_quality_sum = 0.0
        tca_quality_count = 0
        cycle_inventories: List[VenueInventory] = []
        flagged = 0
        for und in self.config.underlyings:
            strike = float(strike_map.get(und, 1000.0))
            mid = float(mid_map.get(und, 1000.0)) * rng.uniform(0.9, 1.1)
            mid = float(max(1.0, mid))
            depth = rng.uniform(0.5, 1.5)
            notional = rng.uniform(100000.0, 1000000.0)
            venue_quotes = self.cvmm.make_venue_quotes(und, self.config.expiries[cycle % len(self.config.expiries)], strike, "call" if cycle % 2 == 0 else "put", mid, tape, depth, notional, recent_trades)
            total_quotes += len(venue_quotes)
            greeks = Greeks(delta=rng.uniform(-100.0, 100.0), gamma=rng.uniform(0.001, 0.05), vega=rng.uniform(100.0, 5000.0), theta=rng.uniform(-10000.0, -100.0), rho=rng.uniform(-50.0, 50.0))
            self.cvmm.update_greeks(und, greeks)
            cvq = self.cvmm.aggregate_best_quote(und, self.config.expiries[cycle % len(self.config.expiries)], strike, "call" if cycle % 2 == 0 else "put", venue_quotes)
            total_spread += cvq.spread_bps
            dislocs = self.cvmm.detect_dislocations(und, self.config.expiries[cycle % len(self.config.expiries)], strike, "call" if cycle % 2 == 0 else "put", venue_quotes, notional_usd=notional)
            total_dislocations += len(dislocs)
            if cvq.dislocation_bps > self.cvmm.config.adverse_selection_threshold * 100:
                flagged += 1
            self.cvmm.route_decision(und, "sell", notional, idx=cycle)
            self.cvmm.route_decision(und, "buy", notional, idx=cycle + len(self.config.underlyings))
            fill_rate = 0.1 + 0.1 * rng.random()
            n_fills = int(total_quotes * fill_rate) if cycle == 0 else int(len(venue_quotes) * fill_rate)
            n_fills = max(1, n_fills)
            for i in range(n_fills):
                fill_qty = rng.uniform(0.01, 5.0)
                fill_price = rng.uniform(max(1.0, mid * 0.995), mid * 1.005)
                side = "buy" if rng.random() > 0.5 else "sell"
                venue = self.config.venues[i % len(self.config.venues)]
                f = Fill(fill_id=self.cvmm._next_id("fill"), quote_id=cvq.quote_id, underlying=und, side=side, fill_qty=float(fill_qty), fill_price=float(fill_price), timestamp=_utc_now(), paper_only=True)
                self.cvmm.apply_fill(f, venue=venue)
                total_fills += 1
                slippage_bps = abs(fill_price - mid) / mid * 10000.0
                tca_quality_sum += slippage_bps
                tca_quality_count += 1
            venue = self.config.venues[cycle % len(self.config.venues)]
            snap = self.rebalancer.snapshot_venue_inventory(venue, und, self.cvmm.inventory.get(und, 0.0), mid, greeks.delta, greeks.gamma, greeks.vega, greeks.theta, greeks.rho, notional_usd=notional)
            cycle_inventories.append(snap)
        limits = self.cvmm.risk_state()
        imbalance = self.rebalancer.detect_imbalance(cycle_inventories)
        rebalance_orders: List[Dict[str, Any]] = []
        if imbalance.rebalance_required:
            plans = self.rebalancer.rebalance_plan(imbalance, price=mid_map.get(self.config.underlyings[0], 1000.0))
            for p in plans:
                self.rebalancer.apply_rebalance(p)
                rebalance_orders.append(asdict(p))
            total_rebalance_orders = len(rebalance_orders)
        tca_fill_quality_bps = float(tca_quality_sum / max(1, tca_quality_count))
        rep = {
            "cycle": cycle,
            "underlyings": list(self.config.underlyings),
            "expiries": list(self.config.expiries),
            "quotes_placed": total_quotes,
            "fills": total_fills,
            "cross_venue_dislocations": total_dislocations,
            "rebalance_orders": total_rebalance_orders,
            "avg_spread_bps": float(total_spread / max(1, total_quotes)),
            "risk_passed": bool(limits["within_limits"]),
            "adverse_selection_flagged": int(flagged),
            "tca_fill_quality_bps": float(tca_fill_quality_bps),
            "imbalance": {"total_net": imbalance.total_net, "max_imbalance": imbalance.max_imbalance, "imbalance_bps": imbalance.imbalance_bps, "rebalance_required": imbalance.rebalance_required},
            "risk_state": limits,
            "rebalance_orders_detail": rebalance_orders,
            "paper_only": True,
            "timestamp": _utc_now(),
        }
        _assert_finite(rep, f"cv_mm_paper_loop_cycle_{cycle}")
        res = CycleResult(
            cycle=int(cycle),
            symbol=",".join(self.config.underlyings),
            quotes_placed=int(total_quotes),
            fills=int(total_fills),
            cross_venue_dislocations=int(total_dislocations),
            rebalance_orders=int(total_rebalance_orders),
            avg_spread_bps=float(total_spread / max(1, total_quotes)),
            inventory_utilization=float(min(1.0, sum(abs(v) for v in self.cvmm.inventory.values()) / max(1e-9, self.cvmm.config.max_inventory * len(self.config.underlyings)))),
            risk_passed=bool(limits["within_limits"]),
            tca_fill_quality_bps=float(tca_fill_quality_bps),
            paper_only=True,
            timestamp=_utc_now(),
        )
        self.results.append(res)
        self.cycle_count += 1
        self._log("cycle", {"cycle": cycle, "quotes_placed": total_quotes, "fills": total_fills, "dislocations": total_dislocations, "rebalance_orders": total_rebalance_orders, "risk_passed": limits["within_limits"], "tca_fill_quality_bps": tca_fill_quality_bps})
        return serialize_metrics_strict(rep)

    def run(self, cycles: Optional[int] = None, tape: Optional[List[Dict[str, Any]]] = None, recent_trades: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        n = int(cycles if cycles is not None else self.config.cycles)
        if n < 1 or n > 1000:
            raise ValueError("cycles out of range")
        results: List[Dict[str, Any]] = []
        for c in range(n):
            results.append(self.run_cycle(c, tape, recent_trades))
        self._log("run_completed", {"cycles": n})
        return results

    def generate_report(self) -> Dict[str, Any]:
        total_quotes = sum(r.quotes_placed for r in self.results)
        total_fills = sum(r.fills for r in self.results)
        total_dislocations = sum(r.cross_venue_dislocations for r in self.results)
        total_rebalances = sum(r.rebalance_orders for r in self.results)
        overall_risk = all(r.risk_passed for r in self.results)
        avg_tca = float(sum(r.tca_fill_quality_bps for r in self.results) / max(1, len(self.results)))
        rep = {
            "report": "PHASE28_CV_MM_PAPER_LOOP_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "cycle_count": self.cycle_count,
            "total_quotes_placed": int(total_quotes),
            "total_fills": int(total_fills),
            "total_cross_venue_dislocations": int(total_dislocations),
            "total_rebalance_orders": int(total_rebalances),
            "overall_risk_passed": bool(overall_risk),
            "avg_tca_fill_quality_bps": float(avg_tca),
            "results": [asdict(r) for r in self.results],
            "final_risk_state": self.cvmm.risk_state(),
            "inventory_rebalance_report": self.rebalancer.generate_report(),
            "audit": self.audit,
            "paper_only": True,
        }
        _assert_finite(rep, "cv_mm_paper_loop_report")
        return serialize_metrics_strict(rep)

    def save_report(self, report: Dict[str, Any], outdir: str = "research_state") -> str:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        pjson = Path(outdir) / "PHASE28_CV_MM_PAPER_LOOP_REPORT.json"
        pmd = Path(outdir) / "PHASE28_CV_MM_PAPER_LOOP_REPORT.md"
        pjson.write_text(json.dumps(report, indent=2))
        pmd.write_text(
            f"# PHASE28_CV_MM_PAPER_LOOP_REPORT\n\nStatus: ok\nCycles: {self.cycle_count}\n"
            f"Quotes: {sum(r.quotes_placed for r in self.results)}\nFills: {sum(r.fills for r in self.results)}\n"
            f"Dislocations: {sum(r.cross_venue_dislocations for r in self.results)}\n"
            f"Rebalance orders: {sum(r.rebalance_orders for r in self.results)}\n"
            f"Risk passed: {all(r.risk_passed for r in self.results)}\nPaper-only: True\n"
        )
        return str(pjson)


__all__ = ["CVMMPaperLoop", "CVMMPaperLoopConfig", "CycleResult"]
