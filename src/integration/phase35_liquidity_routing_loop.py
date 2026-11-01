"""
Phase 35: Liquidity Routing Loop integrating Phases 31-34 with Phase 35.
Crypto options vol surface arb + orderflow, paper/live gated. Deterministic.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import hashlib
import json
import math
from pathlib import Path

from src.telemetry.serialization import serialize_metrics_strict
from src.execution.phase35_cross_venue_liquidity_aggregator import CrossVenueLiquidityAggregator, LiquidityAggregatorConfig
from src.execution.phase35_smart_order_router import SmartOrderRouter, SmartOrderRouterConfig
from src.risk.phase35_adversarial_slippage_controller import AdversarialSlippageController, AdversarialSlippageConfig


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
    h = hashlib.sha256(f"{seed}|p35loop|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p35loop_{tag}_{h}"


@dataclass(frozen=True)
class LiquidityRoutingLoopConfig:
    seed: int = 42
    paper_only: bool = True
    live_enabled: bool = False
    cycles: int = 10
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    enforce_gates: bool = True


@dataclass(frozen=True)
class LoopCycleResult:
    cycle_id: str
    cycle_idx: int
    aggregated_liquidity: int
    routed_orders: int
    mitigations: int
    blocked_orders: int
    net_tca_score: float
    timestamp: str


class LiquidityRoutingLoop:
    def __init__(self, config: Optional[LiquidityRoutingLoopConfig] = None, seed: int = 42):
        self.config = config or LiquidityRoutingLoopConfig(seed=seed)
        if not self.config.paper_only or self.config.live_enabled:
            if self.config.enforce_gates and (self.config.live_enabled or not self.config.paper_only):
                # Enforce paper-only hard gate
                raise ValueError("LiquidityRoutingLoop: paper_only must remain True (live path hard-gated)")
            self.config = LiquidityRoutingLoopConfig(
                seed=int(self.config.seed),
                paper_only=True,
                live_enabled=False,
                cycles=int(self.config.cycles),
                underlyings=tuple(self.config.underlyings),
                venues=tuple(self.config.venues),
                enforce_gates=bool(self.config.enforce_gates),
            )
        else:
            self.config = LiquidityRoutingLoopConfig(
                seed=int(self.config.seed),
                paper_only=True,
                live_enabled=False,
                cycles=int(self.config.cycles),
                underlyings=tuple(self.config.underlyings),
                venues=tuple(self.config.venues),
                enforce_gates=bool(self.config.enforce_gates),
            )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.agg = CrossVenueLiquidityAggregator(LiquidityAggregatorConfig(seed=self.seed), seed=self.seed)
        self.router = SmartOrderRouter(SmartOrderRouterConfig(seed=self.seed), seed=self.seed)
        self.ctrl = AdversarialSlippageController(AdversarialSlippageConfig(seed=self.seed), seed=self.seed)
        self.cycle_results: List[LoopCycleResult] = []

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        n = cycles or self.config.cycles
        self.cycle_results = []
        total_routed = 0
        total_blocked = 0
        tca_sum = 0.0

        for i in range(n):
            agg_res = self.agg.aggregate_liquidity()
            # generate orders
            orders: List[Dict[str, Any]] = []
            for j in range(3 + (i % 3)):
                orders.append({
                    "order_id": self._next_id(f"ord{i}"),
                    "underlying": self.config.underlyings[j % len(self.config.underlyings)],
                    "side": "buy" if (j % 2 == 0) else "sell",
                    "option_type": "call" if (j % 2 == 0) else "put",
                    "notional_usd": 25000.0 + j * 15000.0,
                    "qty_contracts": 1.0 + j * 0.5,
                })
            routed = self.router.route_orders(orders)
            mit = self.ctrl.control_slippage([asdict(r) for r in routed])
            routed_count = len(routed)
            blocked = self.ctrl.blocked_count
            tca = sum(r.tca_score for r in routed) / routed_count if routed_count > 0 else 0.0
            cr = LoopCycleResult(
                cycle_id=self._next_id("cycle"),
                cycle_idx=i,
                aggregated_liquidity=len(agg_res),
                routed_orders=routed_count,
                mitigations=len(mit),
                blocked_orders=blocked,
                net_tca_score=float(tca),
                timestamp=_utc_now(),
            )
            _assert_finite(asdict(cr), "cycle_result")
            self.cycle_results.append(cr)
            total_routed += routed_count
            total_blocked += blocked
            tca_sum += tca

        summary = {
            "status": "ok",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "live_enabled": False,
            "cycles": n,
            "total_aggregated": len(self.agg.aggregated),
            "total_routed": total_routed,
            "total_blocked": total_blocked,
            "avg_tca_score": float(tca_sum / n if n > 0 else 0.0),
            "cycle_results": [asdict(c) for c in self.cycle_results],
        }
        _assert_finite(summary, "phase35_liquidity_routing_loop_summary")
        return summary

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        Path(outdir).mkdir(parents=True, exist_ok=True)
        summary = self.run_campaign(self.config.cycles)
        rep_json = Path(outdir) / "PHASE35_LIQUIDITY_ROUTING_LOOP_REPORT.json"
        rep_md = Path(outdir) / "PHASE35_LIQUIDITY_ROUTING_LOOP_REPORT.md"
        sum_json = Path(outdir) / "PHASE35_CAMPAIGN_SUMMARY.json"
        sum_md = Path(outdir) / "PHASE35_CAMPAIGN_SUMMARY.md"

        rep_md.write_text(
            f"# PHASE35_LIQUIDITY_ROUTING_LOOP_REPORT\n\n"
            f"Timestamp: {summary['timestamp']}\nStatus: ok\nPaper-only: true | Live: false\n"
            f"Cycles: {summary['cycles']}\nTotal routed: {summary['total_routed']}\n"
            f"Total blocked: {summary['total_blocked']}\nAvg TCA: {summary['avg_tca_score']:.4f}\n"
        )
        sum_md.write_text(
            f"# PHASE35_CAMPAIGN_SUMMARY\n\n"
            f"Timestamp: {summary['timestamp']}\nPhase: 35\nStatus: ok\n"
            f"Paper-only: true (live hard-gated)\n"
            f"Routed: {summary['total_routed']} | Blocked: {summary['total_blocked']} | Cycles: {summary['cycles']}\n"
        )
        rep_json.write_text(json.dumps(serialize_metrics_strict(summary), indent=2))
        sum_json.write_text(json.dumps(serialize_metrics_strict(summary), indent=2))

        # also generate component reports
        self.agg.generate_report(outdir)
        self.router.generate_report(outdir)
        self.ctrl.generate_report(outdir)

        return {"status": "ok", "json": str(rep_json), "md": str(rep_md), "campaign_summary_json": str(sum_json), "campaign_summary_md": str(sum_md), "paper_only": True}
