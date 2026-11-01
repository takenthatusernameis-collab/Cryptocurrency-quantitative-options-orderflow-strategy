"""
Phase 33: Capital + Orderflow Integration Loop for Crypto Options Vol Surface Arbitrage.

Integrates Phase 31 live deployment controller + Phase 32 execution/risk + Phase 33
adaptive orderflow hedge, live capital rollout, and venue liquidity sweep.
Paper/live gated; default PAPER-ONLY. Deterministic, finite numerics.
Per-cycle TCA + capital/risk report. Extends, does not redo, Phases 17-32.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.deployment.phase31_live_deployment_controller import (
    LiveDeploymentController,
    DeploymentConfig,
)
from src.execution.phase32_execution_quality import ExecutionQualityEngine
from src.execution.phase33_adaptive_orderflow_hedge import (
    AdaptiveOrderflowHedgeRouter,
    AdaptiveOrderflowHedgeConfig33,
    HedgeCycleResult,
)
from src.integration.phase32_vol_arb_orderflow_loop import (
    VolArbOrderflowLoop,
    VolArbOrderflowLoopConfig32,
)
from src.orderflow.phase33_venue_liquidity_sweep import (
    VenueLiquiditySweep,
    VenueLiquiditySweepConfig33,
)
from src.risk.phase32_live_risk_controls import (
    LiveRiskControls,
    LiveRiskControlsConfig32,
)
from src.risk.phase33_live_capital_rollout import (
    LiveCapitalRollout,
    LiveCapitalRolloutConfig33,
    RolloutCycleResult,
)
from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p33loop|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p33loop_{tag}_{h}"


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
class Phase33CapitalOrderflowLoopConfig33:
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
class Phase33CycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    phase: str
    deploy_allowed: bool
    live_allowed: bool
    kill_switch_active: bool
    risk_ok: bool
    sweep_ok: bool
    dislocations: int
    signals: int
    orderflow_candidates: int
    orderflow_confirmed: int
    hedges_computed: int
    venues_rotated: int
    sweeps_routed: int
    total_swept_notional_usd: float
    avg_hedge_ratio: float
    avg_slippage_bps: float
    max_slippage_bps: float
    avg_fill_rate: float
    capital_allocated_usd: float
    canary_pnl_usd: float
    pnl_usd: float
    drawdown_pct: float
    avg_total_cost_bps: float
    best_venue: str
    deployment_id: str


class Phase33CapitalOrderflowLoop:
    """Phase 31 deployment + Phase 32 execution/risk + Phase 33 hedge/rollout/sweep."""

    def __init__(
        self,
        config: Optional[Phase33CapitalOrderflowLoopConfig33] = None,
        seed: int = 42,
    ) -> None:
        self.config = config or Phase33CapitalOrderflowLoopConfig33(seed=seed)
        if not self.config.paper_only:
            raise ValueError(
                "Phase33CapitalOrderflowLoop: paper_only must remain True (live path hard-gated)"
            )
        self.config = Phase33CapitalOrderflowLoopConfig33(
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
        self.loop31 = VolArbOrderflowLoop(
            config=VolArbOrderflowLoopConfig32(
                seed=self.seed + 33401,
                paper_only=True,
                cycles=self.config.cycles,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                expiries=self.config.expiries,
                min_equity_usd=self.config.min_equity_usd,
                total_capital_usd=self.config.total_capital_usd,
                enforce_gates=self.config.enforce_gates,
            ),
            seed=self.seed + 33401,
        )
        self.hedge = AdaptiveOrderflowHedgeRouter(
            config=AdaptiveOrderflowHedgeConfig33(
                seed=self.seed + 33402,
                paper_only=True,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                expiries=self.config.expiries,
                cycles=self.config.cycles,
                total_capital_usd=self.config.total_capital_usd,
            ),
            seed=self.seed + 33402,
        )
        self.rollout = LiveCapitalRollout(
            config=LiveCapitalRolloutConfig33(
                seed=self.seed + 33403,
                paper_only=True,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                expiries=self.config.expiries,
                cycles=self.config.cycles,
                total_capital_usd=self.config.total_capital_usd,
                min_equity_usd=self.config.min_equity_usd,
                enforce_gates=self.config.enforce_gates,
            ),
            seed=self.seed + 33403,
            deployment_controller=self.loop31.loop31.deployment,
            risk_controls=self.loop31.risk,
        )
        self.sweep = VenueLiquiditySweep(
            config=VenueLiquiditySweepConfig33(
                seed=self.seed + 33404,
                paper_only=True,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                expiries=self.config.expiries,
                cycles=self.config.cycles,
                total_capital_usd=self.config.total_capital_usd,
            ),
            seed=self.seed + 33404,
        )
        self.execution = ExecutionQualityEngine(
            seed=self.seed + 33405,
        )
        self._counter = 0
        self.results: List[Phase33CycleResult] = []
        self.equity = float(self.config.min_equity_usd)
        self.drawdown_pct = 0.0
        self.pnl_usd = 0.0
        self.phase = "canary"

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def run_cycle(
        self,
        cycle: int,
        state: Optional[Dict[str, Any]] = None,
    ) -> Phase33CycleResult:
        state = dict(state or {})
        equity = float(state.get("equity", self.equity))
        drawdown = float(state.get("drawdown_pct", self.drawdown_pct))
        pnl = float(state.get("pnl_usd", self.pnl_usd))
        symbol = str(state.get("symbol", self.config.underlyings[0]))
        side = str(state.get("side", "buy"))
        notional = float(state.get("notional_usd", 50000.0))

        # 1. Phase 31/32 vol arb + orderflow loop.
        loop_res = self.loop31.run_cycle(cycle, state)

        # 2. Phase 33 adaptive orderflow hedge (delta/gamma/vega + venue rotation).
        expiry = self.config.expiries[cycle % len(self.config.expiries)]
        hedge_res = self.hedge.run_cycle(
            cycle,
            {
                "delta_notional_usd": notional,
                "gamma_notional_usd": notional * 0.5,
                "vega_notional_usd": notional * 0.75,
            },
        )

        # 3. Phase 33 live capital rollout (canary -> live gated).
        rollout_res = self.rollout.run_cycle(
            cycle,
            {"equity": equity, "drawdown_pct": drawdown, "pnl_usd": pnl},
        )
        self.phase = rollout_res.phase

        # 4. Phase 33 venue liquidity sweep (cross-venue routing).
        sweep_res = self.sweep.run_cycle(
            cycle,
            {"symbol": symbol, "side": side, "notional_usd": notional},
        )

        # 5. Phase 32 execution quality TCA.
        eq_res = self.execution.run_cycle(
            cycle,
            {
                "side": side,
                "notional_usd": notional,
                "mid_price": 4000.0,
                "symbol": symbol,
                "fills": [
                    {
                        "fill_id": self._next_id("fill"),
                        "symbol": symbol,
                        "side": side,
                        "venue": sweep_res.best_venue,
                        "notional_usd": notional,
                        "mid_price": 4000.0,
                        "fill_price": 4000.0 * (1.0 + 2.0 / 1e4),
                    }
                ],
            },
        )

        # update equity/pnl deterministically
        cycle_pnl = 0.0
        if loop_res.signals > 0 and loop_res.orderflow_confirmed > 0:
            cycle_pnl = (loop_res.signals * 0.01) * (
                1.0 + 0.1 * loop_res.orderflow_confirmed / max(loop_res.orderflow_candidates, 1)
            )
        if rollout_res.live_allowed:
            cycle_pnl += sweep_res.total_swept_notional_usd * 0.0001
        self.pnl_usd = float(pnl + cycle_pnl)
        self.drawdown_pct = float(
            max(0.0, drawdown - 0.001 * (1.0 if cycle_pnl >= 0 else 2.0))
        )
        self.equity = float(equity + cycle_pnl)

        blocked: List[str] = []
        if not hedge_res.risk_ok:
            blocked.append("hedge_risk")
        if not rollout_res.risk_ok:
            blocked.append("rollout_risk")
        if not sweep_res.risk_ok:
            blocked.append("sweep_risk")

        result = Phase33CycleResult(
            cycle=int(cycle),
            timestamp=_utc_now(),
            paper_only=True,
            phase=self.phase,
            deploy_allowed=bool(loop_res.deploy_allowed),
            live_allowed=bool(rollout_res.live_allowed),
            kill_switch_active=bool(
                loop_res.kill_switch_active or rollout_res.live_allowed is False and loop_res.kill_switch_active
            ),
            risk_ok=bool(
                loop_res.risk_ok
                and hedge_res.risk_ok
                and rollout_res.risk_ok
                and sweep_res.risk_ok
                and len(blocked) == 0
            ),
            sweep_ok=bool(sweep_res.risk_ok),
            dislocations=int(loop_res.dislocations),
            signals=int(loop_res.signals),
            orderflow_candidates=int(loop_res.orderflow_candidates),
            orderflow_confirmed=int(loop_res.orderflow_confirmed),
            hedges_computed=int(hedge_res.hedges_computed),
            venues_rotated=int(hedge_res.venues_rotated),
            sweeps_routed=int(sweep_res.sweeps_routed),
            total_swept_notional_usd=float(sweep_res.total_swept_notional_usd),
            avg_hedge_ratio=float(hedge_res.avg_hedge_ratio),
            avg_slippage_bps=float(eq_res.avg_slippage_bps),
            max_slippage_bps=float(eq_res.max_slippage_bps),
            avg_fill_rate=float(sweep_res.avg_fill_rate),
            capital_allocated_usd=float(rollout_res.capital_allocated_usd),
            canary_pnl_usd=float(rollout_res.canary_pnl_usd),
            pnl_usd=self.pnl_usd,
            drawdown_pct=self.drawdown_pct,
            avg_total_cost_bps=float(eq_res.avg_total_cost_bps),
            best_venue=str(sweep_res.best_venue),
            deployment_id=loop_res.deployment_id,
        )
        _assert_finite(
            {
                "pnl_usd": result.pnl_usd,
                "drawdown_pct": result.drawdown_pct,
                "avg_slippage_bps": result.avg_slippage_bps,
                "max_slippage_bps": result.max_slippage_bps,
                "avg_total_cost_bps": result.avg_total_cost_bps,
                "avg_hedge_ratio": result.avg_hedge_ratio,
                "total_swept_notional_usd": result.total_swept_notional_usd,
                "capital_allocated_usd": result.capital_allocated_usd,
            },
            "phase33_cycle_result",
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
                    "equity": self.equity,
                    "drawdown_pct": self.drawdown_pct,
                    "pnl_usd": self.pnl_usd,
                    "symbol": self.config.underlyings[(c - 1) % len(self.config.underlyings)],
                    "side": "buy" if c % 2 == 1 else "sell",
                    "notional_usd": 50000.0,
                },
            )
            reports.append(
                {
                    "cycle": res.cycle,
                    "phase": res.phase,
                    "deploy_allowed": res.deploy_allowed,
                    "live_allowed": res.live_allowed,
                    "kill_switch_active": res.kill_switch_active,
                    "risk_ok": res.risk_ok,
                    "sweep_ok": res.sweep_ok,
                    "dislocations": res.dislocations,
                    "signals": res.signals,
                    "orderflow_candidates": res.orderflow_candidates,
                    "orderflow_confirmed": res.orderflow_confirmed,
                    "hedges_computed": res.hedges_computed,
                    "venues_rotated": res.venues_rotated,
                    "sweeps_routed": res.sweeps_routed,
                    "total_swept_notional_usd": res.total_swept_notional_usd,
                    "avg_hedge_ratio": res.avg_hedge_ratio,
                    "avg_slippage_bps": res.avg_slippage_bps,
                    "max_slippage_bps": res.max_slippage_bps,
                    "avg_fill_rate": res.avg_fill_rate,
                    "capital_allocated_usd": res.capital_allocated_usd,
                    "canary_pnl_usd": res.canary_pnl_usd,
                    "pnl_usd": res.pnl_usd,
                    "drawdown_pct": res.drawdown_pct,
                    "avg_total_cost_bps": res.avg_total_cost_bps,
                    "best_venue": res.best_venue,
                    "deployment_id": res.deployment_id,
                }
            )
        return {
            "status": "ok",
            "paper_only": True,
            "cycles": cycles,
            "reports": reports,
            "final_phase": self.phase,
            "final_pnl_usd": float(self.pnl_usd),
            "final_drawdown_pct": float(self.drawdown_pct),
            "total_signals": int(sum(r["signals"] for r in reports)),
            "total_orderflow_confirmed": int(
                sum(r["orderflow_confirmed"] for r in reports)
            ),
            "total_hedges_computed": int(sum(r["hedges_computed"] for r in reports)),
            "total_venues_rotated": int(sum(r["venues_rotated"] for r in reports)),
            "total_sweeps_routed": int(sum(r["sweeps_routed"] for r in reports)),
            "total_swept_notional_usd": float(
                sum(r["total_swept_notional_usd"] for r in reports)
            ),
            "final_capital_allocated_usd": float(self.capital_allocated_usd)
            if hasattr(self, "capital_allocated_usd")
            else 0.0,
            "kill_switch_active": bool(
                self.loop31.loop31.deployment.kill_switch.active
            ),
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
                        "phase": r.phase,
                        "deploy_allowed": r.deploy_allowed,
                        "live_allowed": r.live_allowed,
                        "kill_switch_active": r.kill_switch_active,
                        "risk_ok": r.risk_ok,
                        "sweep_ok": r.sweep_ok,
                        "dislocations": r.dislocations,
                        "signals": r.signals,
                        "orderflow_candidates": r.orderflow_candidates,
                        "orderflow_confirmed": r.orderflow_confirmed,
                        "hedges_computed": r.hedges_computed,
                        "venues_rotated": r.venues_rotated,
                        "sweeps_routed": r.sweeps_routed,
                        "total_swept_notional_usd": r.total_swept_notional_usd,
                        "avg_hedge_ratio": r.avg_hedge_ratio,
                        "avg_slippage_bps": r.avg_slippage_bps,
                        "max_slippage_bps": r.max_slippage_bps,
                        "avg_fill_rate": r.avg_fill_rate,
                        "capital_allocated_usd": r.capital_allocated_usd,
                        "canary_pnl_usd": r.canary_pnl_usd,
                        "pnl_usd": r.pnl_usd,
                        "drawdown_pct": r.drawdown_pct,
                        "avg_total_cost_bps": r.avg_total_cost_bps,
                        "best_venue": r.best_venue,
                        "deployment_id": r.deployment_id,
                    }
                    for r in self.results
                ],
                "final_phase": self.phase,
                "final_pnl_usd": float(self.pnl_usd),
                "final_drawdown_pct": float(self.drawdown_pct),
                "total_signals": int(sum(r.signals for r in self.results)),
                "total_orderflow_confirmed": int(
                    sum(r.orderflow_confirmed for r in self.results)
                ),
                "total_hedges_computed": int(
                    sum(r.hedges_computed for r in self.results)
                ),
                "total_venues_rotated": int(
                    sum(r.venues_rotated for r in self.results)
                ),
                "total_sweeps_routed": int(
                    sum(r.sweeps_routed for r in self.results)
                ),
                "total_swept_notional_usd": float(
                    sum(r.total_swept_notional_usd for r in self.results)
                ),
                "kill_switch_active": bool(
                    self.loop31.loop31.deployment.kill_switch.active
                ),
            }
        )
        last = self.results[-1] if self.results else None
        report = {
            "report": "PHASE33_CAPITAL_ORDERFLOW_LOOP_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "paper_only": True,
            "cycles": int(len(self.results)),
            "final_phase": self.phase,
            "final_pnl_usd": float(campaign["final_pnl_usd"]),
            "final_drawdown_pct": float(campaign["final_drawdown_pct"]),
            "total_signals": int(campaign["total_signals"]),
            "total_orderflow_confirmed": int(campaign["total_orderflow_confirmed"]),
            "total_hedges_computed": int(campaign["total_hedges_computed"]),
            "total_venues_rotated": int(campaign["total_venues_rotated"]),
            "total_sweeps_routed": int(campaign["total_sweeps_routed"]),
            "total_swept_notional_usd": float(campaign["total_swept_notional_usd"]),
            "kill_switch_active": bool(campaign["kill_switch_active"]),
            "config": asdict(self.config),
            "last_cycle": int(last.cycle) if last else 0,
            "last_phase": str(last.phase) if last else "canary",
            "last_pnl_usd": float(last.pnl_usd) if last else 0.0,
            "last_drawdown_pct": float(last.drawdown_pct) if last else 0.0,
            "last_capital_allocated_usd": float(last.capital_allocated_usd) if last else 0.0,
            "cycle_results": [
                {
                    "cycle": r.cycle,
                    "phase": r.phase,
                    "deploy_allowed": r.deploy_allowed,
                    "live_allowed": r.live_allowed,
                    "kill_switch_active": r.kill_switch_active,
                    "risk_ok": r.risk_ok,
                    "sweep_ok": r.sweep_ok,
                    "dislocations": r.dislocations,
                    "signals": r.signals,
                    "orderflow_candidates": r.orderflow_candidates,
                    "orderflow_confirmed": r.orderflow_confirmed,
                    "hedges_computed": r.hedges_computed,
                    "venues_rotated": r.venues_rotated,
                    "sweeps_routed": r.sweeps_routed,
                    "total_swept_notional_usd": r.total_swept_notional_usd,
                    "avg_hedge_ratio": r.avg_hedge_ratio,
                    "avg_slippage_bps": r.avg_slippage_bps,
                    "max_slippage_bps": r.max_slippage_bps,
                    "avg_fill_rate": r.avg_fill_rate,
                    "capital_allocated_usd": r.capital_allocated_usd,
                    "canary_pnl_usd": r.canary_pnl_usd,
                    "pnl_usd": r.pnl_usd,
                    "drawdown_pct": r.drawdown_pct,
                    "avg_total_cost_bps": r.avg_total_cost_bps,
                    "best_venue": r.best_venue,
                    "deployment_id": r.deployment_id,
                }
                for r in self.results
            ],
            "hedge_report": self.hedge.generate_report(outdir)["report"],
            "rollout_report": self.rollout.generate_report(outdir)["report"],
            "sweep_report": self.sweep.generate_report(outdir)["report"],
            "execution_report": self.execution.generate_report(outdir)["report"],
        }
        _assert_finite(report, "phase33_capital_orderflow_loop_report")
        rep_json = Path(outdir) / "PHASE33_CAPITAL_ORDERFLOW_LOOP_REPORT.json"
        rep_md = Path(outdir) / "PHASE33_CAPITAL_ORDERFLOW_LOOP_REPORT.md"
        rep_json.write_text(__import__("json").dumps(serialize_metrics_strict(report), indent=2))
        rep_md.write_text(
            f"# PHASE33_CAPITAL_ORDERFLOW_LOOP_REPORT\n\n"
            f"Timestamp: {report['timestamp']}\nPaper-only: {report['paper_only']}\n"
            f"Seed: {report['seed']}\nCycles: {report['cycles']}\n"
            f"Final phase: {report['final_phase']}\n"
            f"Final PnL USD: {report['final_pnl_usd']:.2f}\n"
            f"Final drawdown: {report['final_drawdown_pct']:.4f}\n"
            f"Total signals: {report['total_signals']}\n"
            f"Total orderflow confirmed: {report['total_orderflow_confirmed']}\n"
            f"Total hedges computed: {report['total_hedges_computed']}\n"
            f"Total venues rotated: {report['total_venues_rotated']}\n"
            f"Total sweeps routed: {report['total_sweeps_routed']}\n"
            f"Total swept notional USD: {report['total_swept_notional_usd']:.2f}\n"
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
    "Phase33CapitalOrderflowLoop",
    "Phase33CapitalOrderflowLoopConfig33",
    "Phase33CycleResult",
]
