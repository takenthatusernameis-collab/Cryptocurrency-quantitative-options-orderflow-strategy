"""
Phase 31: Live Vol Surface Arbitrage Loop for Crypto Options + Orderflow.

Integrates Phase 30 (vol surface arb engine, vol risk budget, dynamic capital allocator,
cross-asset hedge router) + Phase 31 (live deployment controller, continuous validation,
production telemetry) + Phase 18 (observability) + Phase 24 (cross-venue router).
Paper/live gated; default PAPER-ONLY. Deterministic, finite numerics.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.alpha.phase17_campaign import Phase17TradeIntent
from src.capital.phase30_dynamic_capital_allocator import (
    DynamicCapitalAllocator,
    DynamicCapitalAllocatorConfig,
)
from src.deployment.phase31_live_deployment_controller import LiveDeploymentController
from src.execution.phase24_cross_venue_router import CrossVenueRouter
from src.execution.phase30_cross_asset_hedge_router import CrossAssetHedgeRouter
from src.monitoring.phase18_observability import Phase18Observability
from src.monitoring.phase31_continuous_validation import ContinuousValidationEngine
from src.options.phase30_vol_surface_arb import OptionsVolSurfaceArbEngine
from src.observability.phase31_production_telemetry import ProductionTelemetry
from src.risk.phase30_vol_risk_budget import VolRiskBudgetManager
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p31loop|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p31_{tag}_{h}"


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
class LiveVolArbLoopConfig31:
    seed: int = 42
    paper_only: bool = True
    cycles: int = 10
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    expiries: tuple = ("7D", "30D", "90D")
    min_equity_usd: float = 100000.0
    total_capital_usd: float = 150000.0
    enforce_gates: bool = True


@dataclass(frozen=True)
class LoopCycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    deploy_allowed: bool
    kill_switch_active: bool
    dislocations: int
    signals: int
    allocations: int
    hedge_routes: int
    venue_routed: int
    validation_all_ok: bool
    alerts: int
    pnl_usd: float
    drawdown_pct: float
    deployment_id: str


class LiveVolArbLoop:
    def __init__(
        self,
        config: Optional[LiveVolArbLoopConfig31] = None,
        seed: int = 42,
    ) -> None:
        self.config = config or LiveVolArbLoopConfig31(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "LiveVolArbLoop: paper_only must remain True (live path hard-gated)"
            )
        self.config = LiveVolArbLoopConfig31(
            seed=int(self.config.seed),
            paper_only=True,
            cycles=int(self.config.cycles),
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            expiries=tuple(self.config.expiries),
            min_equity_usd=float(self.config.min_equity_usd),
            total_capital_usd=float(self.config.total_capital_usd),
            enforce_gates=bool(self.config.enforce_gates),
        )
        self.seed = int(self.config.seed)
        self.engine = OptionsVolSurfaceArbEngine(seed=self.seed + 31101)
        self.risk = VolRiskBudgetManager(seed=self.seed + 31102)
        self.allocator = DynamicCapitalAllocator(
            config=DynamicCapitalAllocatorConfig(seed=self.seed + 31103, total_capital_usd=self.config.total_capital_usd),
            seed=self.seed + 31103,
        )
        self.hedge_router = CrossAssetHedgeRouter(seed=self.seed + 31104)
        self.router = CrossVenueRouter(seed=self.seed + 31105)
        self.observability = Phase18Observability(seed=self.seed + 31106, paper_only=True)
        self.deployment = LiveDeploymentController(seed=self.seed + 31107)
        self.validation = ContinuousValidationEngine(seed=self.seed + 31108)
        self.telemetry = ProductionTelemetry(seed=self.seed + 31109)
        self._counter = 0
        self.results: List[LoopCycleResult] = []
        self.equity = float(self.config.min_equity_usd)
        self.drawdown_pct = 0.0
        self.pnl_usd = 0.0
        self._baseline_set = False

    def _ensure_baseline(self) -> None:
        """Establish drift baselines once at campaign start. Never reset per cycle."""
        if self._baseline_set:
            return
        self.validation.set_baseline(
            {
                "drawdown_pct": 0.02,
                "var_pct": 0.02,
                "iv_skew_bps": 10.0,
                "sharpe": 1.0,
                "fill_reject_rate": 0.05,
                "latency_p95_ms": 80.0,
            }
        )
        self._baseline_set = True

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def _gen_quotes(self, cycle: int) -> List[Dict[str, Any]]:
        spots = {"BTC": 65000.0, "ETH": 3500.0, "SOL": 150.0, "XRP": 0.6}
        quotes: List[Dict[str, Any]] = []
        for und in self.config.underlyings:
            spot = spots.get(und, 1000.0)
            for exp in self.config.expiries:
                for strike in [spot * 0.9, spot, spot * 1.1]:
                    for opt in ["call", "put"]:
                        for vi, v in enumerate(self.config.venues):
                            base_iv = 0.62 if und == "BTC" else 0.82 if und == "ETH" else 1.02 if und == "SOL" else 0.95
                            bump = (vi - 1) * 0.014 + 0.001 * (cycle % 5)
                            bid_iv = base_iv + bump - 0.01
                            ask_iv = base_iv + bump + 0.01
                            quotes.append(
                                {
                                    "quote_id": f"q31_{und}_{exp}_{strike}_{opt}_{v}_c{cycle}",
                                    "underlying": und,
                                    "expiry": exp,
                                    "strike": float(strike),
                                    "option_type": opt,
                                    "venue": v,
                                    "bid_iv": float(bid_iv),
                                    "ask_iv": float(ask_iv),
                                    "mid_iv": float((bid_iv + ask_iv) / 2.0),
                                    "volume": float(12 + vi),
                                    "oi": float(60 + vi * 12),
                                }
                            )
        return quotes

    def run_cycle(
        self,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
    ) -> LoopCycleResult:
        state = dict(state or {})
        equity = float(state.get("equity", self.equity))
        drawdown = float(state.get("drawdown_pct", self.drawdown_pct))
        pnl = float(state.get("pnl_usd", self.pnl_usd))

        # 1. Deployment gate + venue health
        self._ensure_baseline()
        deploy = self.deployment.deploy_cycle(cycle, [], state)
        if not deploy["deploy_allowed"]:
            self.equity = equity
            self.drawdown_pct = drawdown
            self.pnl_usd = pnl
            return LoopCycleResult(
                cycle=int(cycle),
                timestamp=_utc_now(),
                paper_only=True,
                deploy_allowed=False,
                kill_switch_active=bool(deploy["kill_switch_active"]),
                dislocations=0,
                signals=0,
                allocations=0,
                hedge_routes=0,
                venue_routed=0,
                validation_all_ok=False,
                alerts=0,
                pnl_usd=pnl,
                drawdown_pct=drawdown,
                deployment_id=deploy["deployment_id"],
            )

        # 2. Vol surface arb: detect dislocations + build signals
        quotes = self._gen_quotes(cycle)
        self.engine.ingest_iv_quotes(quotes)
        dislocations = self.engine.detect_dislocations()
        signals = self.engine.build_signals()

        # 3. Risk budget evaluation
        exp_by_und: Dict[str, Dict[str, float]] = {}
        for s in signals:
            und = str(s.underlying)
            exp_by_und.setdefault(und, {"delta": 0.0, "gamma": 0.0, "vega": 0.0})
            exp_by_und[und]["delta"] += float(s.net_delta)
            exp_by_und[und]["gamma"] += float(s.net_gamma)
            exp_by_und[und]["vega"] += float(s.net_vega)
        self.risk.update_exposure(exp_by_und)
        risk_states = self.risk.evaluate(regime="normal", drawdown_pct=drawdown)
        budget_ok = all(st.budget_ok for st in risk_states) and not self.risk.kill_switch_triggered

        # 4. Capital allocation
        opportunities = [
            {
                "underlying": s.underlying,
                "strategy": s.strategy,
                "venue": s.dislocation.buy_venue,
                "edge_bps": float(s.dislocation.iv_diff_bps),
                "win_rate": 0.55 + 0.1 * float(s.risk_score),
            }
            for s in signals
        ]
        allocations = self.allocator.allocate(opportunities, regime="normal", drawdown_pct=drawdown) if budget_ok else []

        # 5. Hedge routing for delta drift
        hedge_needs = [
            {"underlying": s.underlying, "delta_drift": float(s.net_delta)}
            for s in signals
            if abs(float(s.net_delta)) > 1e-6
        ]
        hedge_routes = self.hedge_router.route_hedges(hedge_needs) if budget_ok else []

        # 6. Cross-venue routing
        venue_routed = 0
        for s in signals[:5]:
            self.router.route(
                symbol=f"{s.underlying}USDT",
                side="buy",
                notional_usd=float(s.dislocation.iv_diff_bps) * 1000.0,
                venues=list(self.config.venues),
                idx=cycle,
            )
            venue_routed += 1

        # 7. Continuous validation
        iv_skew = self.engine.max_iv_skew_bps()
        state_metrics = {
            "drawdown_pct": drawdown,
            "var_pct": min(drawdown * 1.2, 0.1),
            "iv_skew_bps": iv_skew,
            "sharpe": 1.2,
            "fill_reject_rate": 0.05,
            "latency_p95_ms": 90.0,
        }
        validation = self.validation.validate_cycle(cycle, state_metrics, state_metrics)

        # 8. Telemetry: metrics, traces, logs
        trace_id = self.telemetry.start_trace("vol_arb_cycle", str(self.config.venues[0]))
        self.telemetry.record_metric("vol_arb.dislocations", float(len(dislocations)), {"cycle": str(cycle)})
        self.telemetry.record_metric("vol_arb.signals", float(len(signals)), {"cycle": str(cycle)})
        self.telemetry.record_metric("vol_arb.pnl_usd", pnl, {"cycle": str(cycle)})
        self.telemetry.record_metric("vol_arb.drawdown_pct", drawdown, {"cycle": str(cycle)})
        self.telemetry.end_trace(trace_id, status="ok", end_ms=45.0)
        self.telemetry.log("info", f"cycle {cycle} complete", {"signals": len(signals), "deploy_allowed": True})

        # 9. Observability SLOs
        intents = [
            Phase17TradeIntent(
                intent_id=self._next_id("intent"),
                symbol=f"{s.underlying}USDT",
                side="buy",
                qty=1.0,
                size_usd=1000.0,
                expiry=s.expiry,
                strike_band=[float(s.dislocation.strike) * 0.9, float(s.dislocation.strike) * 1.1],
                option_type=s.dislocation.option_type,
                order_type="limit",
                limit_logic="post_only",
                rationale_hash=_make_id(self.seed, "rationale", i),
                regime="normal",
                confidence=float(s.risk_score),
                delta_est=float(s.net_delta),
                vega_est=float(s.net_vega),
                gamma_est=float(s.net_gamma),
                dte_days=7.0,
                liquidity_score=0.8,
                orderflow_confirmed=True,
                confirmation_score=0.9,
                risk_flags=[],
            )
            for i, s in enumerate(signals[:3])
        ]
        self.observability.compute_slos(intents, [], kill_switch_triggered=bool(deploy["kill_switch_active"]), kill_count=0)

        # update equity/pnl deterministically
        cycle_pnl = 0.0
        if signals:
            cycle_pnl = sum(float(s.expected_pnl_usd) for s in signals[:3]) * 0.01
        self.pnl_usd = float(pnl + cycle_pnl)
        self.drawdown_pct = float(max(0.0, drawdown - 0.001 * (1.0 if cycle_pnl >= 0 else 2.0)))
        self.equity = float(equity + cycle_pnl)

        res = LoopCycleResult(
            cycle=int(cycle),
            timestamp=_utc_now(),
            paper_only=True,
            deploy_allowed=True,
            kill_switch_active=bool(deploy["kill_switch_active"]),
            dislocations=int(len(dislocations)),
            signals=int(len(signals)),
            allocations=int(len(allocations)),
            hedge_routes=int(len(hedge_routes)),
            venue_routed=int(venue_routed),
            validation_all_ok=bool(validation.all_ok),
            alerts=int(len(validation.alerts)),
            pnl_usd=self.pnl_usd,
            drawdown_pct=self.drawdown_pct,
            deployment_id=deploy["deployment_id"],
        )
        _assert_finite(
            {
                "pnl_usd": res.pnl_usd,
                "drawdown_pct": res.drawdown_pct,
                "dislocations": float(res.dislocations),
                "signals": float(res.signals),
            },
            "loop_cycle_result",
        )
        self.results.append(res)
        return res

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        cycles = int(cycles if cycles is not None else self.config.cycles)
        self._ensure_baseline()
        reports: List[Dict[str, Any]] = []
        for c in range(1, cycles + 1):
            res = self.run_cycle(c)
            reports.append(
                {
                    "cycle": res.cycle,
                    "deploy_allowed": res.deploy_allowed,
                    "kill_switch_active": res.kill_switch_active,
                    "dislocations": res.dislocations,
                    "signals": res.signals,
                    "allocations": res.allocations,
                    "hedge_routes": res.hedge_routes,
                    "venue_routed": res.venue_routed,
                    "validation_all_ok": res.validation_all_ok,
                    "alerts": res.alerts,
                    "pnl_usd": res.pnl_usd,
                    "drawdown_pct": res.drawdown_pct,
                }
            )
        return {
            "status": "ok",
            "paper_only": True,
            "cycles": cycles,
            "reports": reports,
            "final_pnl_usd": float(self.pnl_usd),
            "final_drawdown_pct": float(self.drawdown_pct),
            "total_signals": int(sum(r["signals"] for r in reports)),
            "total_allocations": int(sum(r["allocations"] for r in reports)),
        }

    def generate_report(self, outdir: str = "research_state") -> Dict[str, Any]:
        from pathlib import Path

        Path(outdir).mkdir(parents=True, exist_ok=True)
        last = self.results[-1] if self.results else None
        report = {
            "report": "PHASE31_LIVE_VOL_ARB_LOOP_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": int(len(self.results)),
            "equity": float(self.equity),
            "pnl_usd": float(self.pnl_usd),
            "drawdown_pct": float(self.drawdown_pct),
            "last_cycle": int(last.cycle) if last else 0,
            "last_validation_all_ok": bool(last.validation_all_ok) if last else True,
            "total_signals": int(sum(r.signals for r in self.results)),
            "total_allocations": int(sum(r.allocations for r in self.results)),
            "total_hedge_routes": int(sum(r.hedge_routes for r in self.results)),
            "total_venue_routed": int(sum(r.venue_routed for r in self.results)),
            "kill_switch_active": bool(self.deployment.kill_switch.active),
            "deployment_report": self.deployment.generate_report(outdir),
            "validation_report": self.validation.generate_report(outdir),
            "telemetry_report": self.telemetry.generate_report(outdir),
            "cycle_results": [
                {
                    "cycle": r.cycle,
                    "deploy_allowed": r.deploy_allowed,
                    "kill_switch_active": r.kill_switch_active,
                    "dislocations": r.dislocations,
                    "signals": r.signals,
                    "allocations": r.allocations,
                    "hedge_routes": r.hedge_routes,
                    "venue_routed": r.venue_routed,
                    "validation_all_ok": r.validation_all_ok,
                    "alerts": r.alerts,
                    "pnl_usd": r.pnl_usd,
                    "drawdown_pct": r.drawdown_pct,
                }
                for r in self.results
            ],
        }
        _assert_finite(report, "phase31_live_vol_arb_loop_report")
        rep_json = Path(outdir) / "PHASE31_LIVE_VOL_ARB_LOOP_REPORT.json"
        rep_md = Path(outdir) / "PHASE31_LIVE_VOL_ARB_LOOP_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE31_LIVE_VOL_ARB_LOOP_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Cycles: {report['cycles']}\nEquity: {report['equity']:.2f}\n"
            f"PnL USD: {report['pnl_usd']:.2f}\nDrawdown: {report['drawdown_pct']:.4f}\n"
            f"Total signals: {report['total_signals']}\nKill switch: {report['kill_switch_active']}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
        }


__all__ = [
    "LiveVolArbLoop",
    "LiveVolArbLoopConfig31",
    "LoopCycleResult",
]
