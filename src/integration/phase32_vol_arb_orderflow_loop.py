"""
Phase 32: Vol Surface Arbitrage + Orderflow Integration Loop.

Integrates the Phase 31 LiveVolArbLoop (vol surface arb engine, vol risk budget,
dynamic capital allocator, cross-asset hedge router, cross-venue router, live
deployment, continuous validation, production telemetry, observability) with
Phase 32 modules:
  * OrderflowAlphaIntegrator — orderflow alpha fused into candidate scoring
  * ExecutionQualityEngine — slippage model, per-fill TCA, venue comparison
  * LiveRiskControls — position/margin/leverage limits + Phase 31 kill-switch
    coordination

Paper/live gated; default PAPER-ONLY. Deterministic, finite numerics.
Per-cycle TCA + risk report. Extends, does not redo, Phases 17-31.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.execution.phase31_live_vol_arb_loop import (
    LiveVolArbLoop,
    LiveVolArbLoopConfig31,
    LoopCycleResult,
)
from src.execution.phase32_execution_quality import ExecutionQualityEngine
from src.orderflow.phase32_orderflow_alpha_integration import (
    OrderflowAlphaIntegrator,
    OrderflowAlphaIntegrationConfig32,
)
from src.risk.phase32_live_risk_controls import (
    LiveRiskControls,
    LiveRiskControlsConfig32,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p32loop|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p32loop_{tag}_{h}"


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
class VolArbOrderflowLoopConfig32:
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
class VolArbOrderflowCycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    deploy_allowed: bool
    kill_switch_active: bool
    risk_ok: bool
    dislocations: int
    signals: int
    orderflow_candidates: int
    orderflow_confirmed: int
    allocations: int
    hedge_routes: int
    venue_routed: int
    validation_all_ok: bool
    alerts: int
    avg_slippage_bps: float
    max_slippage_bps: float
    avg_total_cost_bps: float
    best_venue: str
    positions_checked: int
    positions_blocked: int
    pnl_usd: float
    drawdown_pct: float
    deployment_id: str


class VolArbOrderflowLoop:
    """Phase 31 live vol arb loop fused with Phase 32 orderflow alpha, execution
    quality, and live risk controls."""

    def __init__(
        self,
        config: Optional[VolArbOrderflowLoopConfig32] = None,
        seed: int = 42,
    ) -> None:
        self.config = config or VolArbOrderflowLoopConfig32(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "VolArbOrderflowLoop: paper_only must remain True (live path hard-gated)"
            )
        self.config = VolArbOrderflowLoopConfig32(
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
        self.loop31 = LiveVolArbLoop(
            config=LiveVolArbLoopConfig31(
                seed=self.seed + 32201,
                paper_only=True,
                cycles=self.config.cycles,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                expiries=self.config.expiries,
                min_equity_usd=self.config.min_equity_usd,
                total_capital_usd=self.config.total_capital_usd,
                enforce_gates=self.config.enforce_gates,
            ),
            seed=self.seed + 32201,
        )
        self.orderflow = OrderflowAlphaIntegrator(
            config=OrderflowAlphaIntegrationConfig32(
                seed=self.seed + 32202,
                paper_only=True,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                cycles=self.config.cycles,
            ),
            seed=self.seed + 32202,
        )
        self.execution = ExecutionQualityEngine(
            seed=self.seed + 32203,
        )
        self.risk = LiveRiskControls(
            config=LiveRiskControlsConfig32(
                seed=self.seed + 32204,
                paper_only=True,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                cycles=self.config.cycles,
            ),
            seed=self.seed + 32204,
            deployment_controller=self.loop31.deployment,
        )
        self._counter = 0
        self.results: List[VolArbOrderflowCycleResult] = []
        self.equity = float(self.config.min_equity_usd)
        self.drawdown_pct = 0.0
        self.pnl_usd = 0.0

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def run_cycle(
        self,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
    ) -> VolArbOrderflowCycleResult:
        state = dict(state or {})
        equity = float(state.get("equity", self.equity))
        drawdown = float(state.get("drawdown_pct", self.drawdown_pct))
        pnl = float(state.get("pnl_usd", self.pnl_usd))

        # 1. Phase 31 live vol arb cycle (deployment gate, vol arb, risk budget,
        #    capital allocation, hedge routing, cross-venue routing, validation,
        #    telemetry, observability).
        loop_res = self.loop31.run_cycle(cycle, state)

        # 2. Phase 32 orderflow alpha integration (decay-aware fused scoring).
        of_res = self.orderflow.integrate_cycle(cycle, state)

        # 3. Phase 32 execution quality (slippage + TCA + venue comparison).
        side = "buy"
        notional = 50000.0
        mid = 4000.0
        eq_res = self.execution.run_cycle(
            cycle,
            {
                "side": side,
                "notional_usd": notional,
                "mid_price": mid,
                "symbol": self.config.underlyings[0],
                "fills": [
                    {
                        "fill_id": self._next_id("fill"),
                        "symbol": self.config.underlyings[0],
                        "side": side,
                        "venue": self.config.venues[0],
                        "notional_usd": notional,
                        "mid_price": mid,
                        "fill_price": mid * (1.0 + 2.0 / 1e4),
                    }
                ],
            },
        )

        # 4. Phase 32 live risk controls (position/margin/leverage + Phase 31
        #    kill-switch coordination).
        positions = [
            {
                "symbol": u,
                "side": side,
                "notional_usd": notional / len(self.config.underlyings),
            }
            for u in self.config.underlyings
        ]
        risk_res = self.risk.run_cycle(
            cycle,
            {
                "equity": equity,
                "drawdown_pct": drawdown,
                "pnl_usd": pnl,
                "daily_loss_usd": 0.0,
                "positions": positions,
            },
        )

        # update equity/pnl deterministically
        cycle_pnl = 0.0
        if loop_res.signals > 0 and of_res.confirmed > 0:
            cycle_pnl = (loop_res.signals * 0.01) * (1.0 + 0.1 * of_res.avg_fused_score)
        self.pnl_usd = float(pnl + cycle_pnl)
        self.drawdown_pct = float(
            max(0.0, drawdown - 0.001 * (1.0 if cycle_pnl >= 0 else 2.0))
        )
        self.equity = float(equity + cycle_pnl)

        result = VolArbOrderflowCycleResult(
            cycle=int(cycle),
            timestamp=_utc_now(),
            paper_only=True,
            deploy_allowed=bool(loop_res.deploy_allowed),
            kill_switch_active=bool(
                loop_res.kill_switch_active or risk_res.kill_switch_active
            ),
            risk_ok=bool(risk_res.risk_ok),
            dislocations=int(loop_res.dislocations),
            signals=int(loop_res.signals),
            orderflow_candidates=int(of_res.candidates),
            orderflow_confirmed=int(of_res.confirmed),
            allocations=int(loop_res.allocations),
            hedge_routes=int(loop_res.hedge_routes),
            venue_routed=int(loop_res.venue_routed),
            validation_all_ok=bool(loop_res.validation_all_ok),
            alerts=int(loop_res.alerts),
            avg_slippage_bps=float(eq_res.avg_slippage_bps),
            max_slippage_bps=float(eq_res.max_slippage_bps),
            avg_total_cost_bps=float(eq_res.avg_total_cost_bps),
            best_venue=str(eq_res.best_venue),
            positions_checked=int(risk_res.positions_checked),
            positions_blocked=int(risk_res.positions_blocked),
            pnl_usd=self.pnl_usd,
            drawdown_pct=self.drawdown_pct,
            deployment_id=loop_res.deployment_id,
        )
        _assert_finite(
            {
                "pnl_usd": result.pnl_usd,
                "drawdown_pct": result.drawdown_pct,
                "avg_slippage_bps": result.avg_slippage_bps,
                "max_slippage_bps": result.max_slippage_bps,
                "avg_total_cost_bps": result.avg_total_cost_bps,
            },
            "vol_arb_orderflow_cycle_result",
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
                    "deploy_allowed": res.deploy_allowed,
                    "kill_switch_active": res.kill_switch_active,
                    "risk_ok": res.risk_ok,
                    "dislocations": res.dislocations,
                    "signals": res.signals,
                    "orderflow_candidates": res.orderflow_candidates,
                    "orderflow_confirmed": res.orderflow_confirmed,
                    "allocations": res.allocations,
                    "hedge_routes": res.hedge_routes,
                    "venue_routed": res.venue_routed,
                    "validation_all_ok": res.validation_all_ok,
                    "alerts": res.alerts,
                    "avg_slippage_bps": res.avg_slippage_bps,
                    "max_slippage_bps": res.max_slippage_bps,
                    "avg_total_cost_bps": res.avg_total_cost_bps,
                    "best_venue": res.best_venue,
                    "positions_checked": res.positions_checked,
                    "positions_blocked": res.positions_blocked,
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
            "total_orderflow_confirmed": int(
                sum(r["orderflow_confirmed"] for r in reports)
            ),
            "total_allocations": int(sum(r["allocations"] for r in reports)),
            "total_venue_routed": int(sum(r["venue_routed"] for r in reports)),
            "kill_switch_active": bool(self.loop31.deployment.kill_switch.active),
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
                    "deploy_allowed": r.deploy_allowed,
                    "kill_switch_active": r.kill_switch_active,
                    "risk_ok": r.risk_ok,
                    "dislocations": r.dislocations,
                    "signals": r.signals,
                    "orderflow_candidates": r.orderflow_candidates,
                    "orderflow_confirmed": r.orderflow_confirmed,
                    "allocations": r.allocations,
                    "hedge_routes": r.hedge_routes,
                    "venue_routed": r.venue_routed,
                    "validation_all_ok": r.validation_all_ok,
                    "alerts": r.alerts,
                    "avg_slippage_bps": r.avg_slippage_bps,
                    "max_slippage_bps": r.max_slippage_bps,
                    "avg_total_cost_bps": r.avg_total_cost_bps,
                    "best_venue": r.best_venue,
                    "positions_checked": r.positions_checked,
                    "positions_blocked": r.positions_blocked,
                    "pnl_usd": r.pnl_usd,
                    "drawdown_pct": r.drawdown_pct,
                }
                for r in self.results
            ],
            "final_pnl_usd": float(self.results[-1].pnl_usd)
            if self.results
            else 0.0,
            "final_drawdown_pct": float(self.results[-1].drawdown_pct)
            if self.results
            else 0.0,
            "total_signals": int(sum(r.signals for r in self.results)),
            "total_orderflow_confirmed": int(
                sum(r.orderflow_confirmed for r in self.results)
            ),
            "total_allocations": int(sum(r.allocations for r in self.results)),
            "total_venue_routed": int(sum(r.venue_routed for r in self.results)),
            "kill_switch_active": bool(
                self.loop31.deployment.kill_switch.active
            ),
        }
        last = self.results[-1] if self.results else None
        report = {
            "report": "PHASE32_VOL_ARB_ORDERFLOW_LOOP_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": int(len(self.results)),
            "final_pnl_usd": float(campaign["final_pnl_usd"]),
            "final_drawdown_pct": float(campaign["final_drawdown_pct"]),
            "total_signals": int(campaign["total_signals"]),
            "total_orderflow_confirmed": int(campaign["total_orderflow_confirmed"]),
            "total_allocations": int(campaign["total_allocations"]),
            "total_venue_routed": int(campaign["total_venue_routed"]),
            "kill_switch_active": bool(campaign["kill_switch_active"]),
            "config": asdict(self.config),
            "last_cycle": int(last.cycle) if last else 0,
            "last_pnl_usd": float(last.pnl_usd) if last else 0.0,
            "last_drawdown_pct": float(last.drawdown_pct) if last else 0.0,
            "cycle_results": [
                {
                    "cycle": r.cycle,
                    "deploy_allowed": r.deploy_allowed,
                    "kill_switch_active": r.kill_switch_active,
                    "risk_ok": r.risk_ok,
                    "dislocations": r.dislocations,
                    "signals": r.signals,
                    "orderflow_candidates": r.orderflow_candidates,
                    "orderflow_confirmed": r.orderflow_confirmed,
                    "allocations": r.allocations,
                    "hedge_routes": r.hedge_routes,
                    "venue_routed": r.venue_routed,
                    "validation_all_ok": r.validation_all_ok,
                    "alerts": r.alerts,
                    "avg_slippage_bps": r.avg_slippage_bps,
                    "max_slippage_bps": r.max_slippage_bps,
                    "avg_total_cost_bps": r.avg_total_cost_bps,
                    "best_venue": r.best_venue,
                    "positions_checked": r.positions_checked,
                    "positions_blocked": r.positions_blocked,
                    "pnl_usd": r.pnl_usd,
                    "drawdown_pct": r.drawdown_pct,
                }
                for r in self.results
            ],
            "orderflow_report": self.orderflow.generate_report(outdir)["report"],
            "execution_report": self.execution.generate_report(outdir)["report"],
            "risk_report": self.risk.generate_report(outdir)["report"],
        }
        _assert_finite(report, "phase32_vol_arb_orderflow_loop_report")
        rep_json = Path(outdir) / "PHASE32_VOL_ARB_ORDERFLOW_LOOP_REPORT.json"
        rep_md = Path(outdir) / "PHASE32_VOL_ARB_ORDERFLOW_LOOP_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE32_VOL_ARB_ORDERFLOW_LOOP_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Seed: {report['seed']}\nCycles: {report['cycles']}\n"
            f"Final PnL USD: {report['final_pnl_usd']:.2f}\n"
            f"Final drawdown: {report['final_drawdown_pct']:.4f}\n"
            f"Total signals: {report['total_signals']}\n"
            f"Total orderflow confirmed: {report['total_orderflow_confirmed']}\n"
            f"Kill switch: {report['kill_switch_active']}\n"
        )
        return {
            "status": "ok",
            "json": str(rep_json),
            "md": str(rep_md),
            "paper_only": True,
            "report": report,
        }


__all__ = [
    "VolArbOrderflowLoop",
    "VolArbOrderflowLoopConfig32",
    "VolArbOrderflowCycleResult",
]
