"""
Phase 34: Portfolio + Capital Integration Loop for Crypto Options Vol Surface Arbitrage + Orderflow.

Integrates Phases 31-33 with Phase 34 portfolio Greeks, cross-margin, adaptive capital reallocation.
Paper/live gated; default PAPER-ONLY. Deterministic, finite numerics.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from src.execution.phase32_execution_quality import ExecutionQualityEngine
from src.execution.phase34_adaptive_capital_reallocation import (
    AdaptiveCapitalReallocation,
    AdaptiveCapitalReallocationConfig34,
)
from src.integration.phase32_vol_arb_orderflow_loop import (
    VolArbOrderflowLoop,
    VolArbOrderflowLoopConfig32,
)
from src.risk.phase32_live_risk_controls import LiveRiskControls
from src.risk.phase34_cross_margin_engine import CrossMarginEngine, CrossMarginConfig34
from src.risk.phase34_portfolio_greeks_aggregator import (
    PortfolioGreeksAggregator,
    PortfolioGreeksConfig34,
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p34loop|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p34loop_{tag}_{h}"


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
class Phase34PortfolioCapitalLoopConfig34:
    seed: int = 42
    paper_only: bool = True
    cycles: int = 10
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    expiries: tuple = ("7D", "30D", "90D")
    min_equity_usd: float = 1000000.0
    total_capital_usd: float = 1500000.0
    enforce_gates: bool = True

    def __post_init__(self) -> None:
        if not bool(self.paper_only):
            raise ValueError("Phase34PortfolioCapitalLoop: paper_only must remain True (live path hard-gated)")



@dataclass(frozen=True)
class Phase34CycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    phase: str
    deploy_allowed: bool
    live_allowed: bool
    kill_switch_active: bool
    risk_ok: bool
    margin_ok: bool
    greeks_ok: bool
    reallocation_ok: bool
    dislocations: int
    signals: int
    total_positions: int
    total_delta_usd: float
    total_gamma_usd: float
    total_vega_usd: float
    total_theta_usd: float
    cross_margin_required_usd: float
    margin_ratio: float
    margin_call: bool
    worst_case_loss_usd: float
    rebalances: int
    capital_utilization_pct: float
    pnl_usd: float
    drawdown_pct: float
    equity_usd: float
    avg_total_cost_bps: float
    best_venue: str
    deployment_id: str


class Phase34PortfolioCapitalLoop:
    """Phases 31-33 + Phase 34 portfolio/margin/reallocation."""

    def __init__(self, config: Optional[Phase34PortfolioCapitalLoopConfig34] = None, seed: int = 42) -> None:
        self.config = config or Phase34PortfolioCapitalLoopConfig34(seed=seed)
        if not self.config.paper_only:
            raise ValueError("Phase34PortfolioCapitalLoop: paper_only must remain True (live path hard-gated)")
        self.config = Phase34PortfolioCapitalLoopConfig34(
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
        self.loop32 = VolArbOrderflowLoop(
            config=VolArbOrderflowLoopConfig32(
                seed=self.seed + 34401,
                paper_only=True,
                cycles=self.config.cycles,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                expiries=self.config.expiries,
                min_equity_usd=self.config.min_equity_usd,
                total_capital_usd=self.config.total_capital_usd,
                enforce_gates=self.config.enforce_gates,
            ),
            seed=self.seed + 34401,
        )
        self.greeks = PortfolioGreeksAggregator(
            config=PortfolioGreeksConfig34(
                seed=self.seed + 34402,
                paper_only=True,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                expiries=self.config.expiries,
                cycles=self.config.cycles,
            ),
            seed=self.seed + 34402,
        )
        self.margin = CrossMarginEngine(
            config=CrossMarginConfig34(
                seed=self.seed + 34403,
                paper_only=True,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                cycles=self.config.cycles,
            ),
            seed=self.seed + 34403,
        )
        self.realloc = AdaptiveCapitalReallocation(
            config=AdaptiveCapitalReallocationConfig34(
                seed=self.seed + 34404,
                paper_only=True,
                underlyings=self.config.underlyings,
                venues=self.config.venues,
                cycles=self.config.cycles,
                total_capital_usd=self.config.total_capital_usd,
            ),
            seed=self.seed + 34404,
        )
        self.execution = ExecutionQualityEngine(seed=self.seed + 34405)
        self._counter = 0
        self.results: List[Phase34CycleResult] = []
        self.equity = float(self.config.min_equity_usd)
        self.drawdown_pct = 0.0
        self.pnl_usd = 0.0
        self.phase = "canary"

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def run_cycle(self, cycle: int) -> Phase34CycleResult:
        base = self.loop32.run_cycle(cycle)
        g = self.greeks.aggregate(cycle)
        m = self.margin.compute_margin(cycle, equity_usd=self.equity, portfolio_notional_usd=max(1.0, abs(g.total_delta_usd) * 2.0))
        r = self.realloc.reallocate(cycle)
        risk_ok = base.risk_ok and g.risk_ok and m.margin_call is False
        margin_ok = not m.margin_call and m.liquidation_risk is False
        greeks_ok = g.risk_ok
        reallocation_ok = r.risk_ok
        pnl = base.pnl_usd * 1.02
        self.pnl_usd += pnl
        if self.equity - self.pnl_usd < self.config.min_equity_usd:
            self.drawdown_pct = max(0.0, (self.config.min_equity_usd - (self.equity - self.pnl_usd)) / max(1e-12, self.config.min_equity_usd))
        res = Phase34CycleResult(
            cycle=cycle,
            timestamp=_utc_now(),
            paper_only=True,
            phase=self.phase,
            deploy_allowed=base.deploy_allowed,
            live_allowed=False,
            kill_switch_active=base.kill_switch_active,
            risk_ok=risk_ok and margin_ok,
            margin_ok=margin_ok,
            greeks_ok=greeks_ok,
            reallocation_ok=reallocation_ok,
            dislocations=base.dislocations,
            signals=base.signals,
            total_positions=g.total_positions,
            total_delta_usd=g.total_delta_usd,
            total_gamma_usd=g.total_gamma_usd,
            total_vega_usd=g.total_vega_usd,
            total_theta_usd=g.total_theta_usd,
            cross_margin_required_usd=m.cross_margin_required_usd,
            margin_ratio=m.margin_ratio,
            margin_call=m.margin_call,
            worst_case_loss_usd=m.worst_case_loss_usd,
            rebalances=r.rebalances,
            capital_utilization_pct=r.capital_utilization_pct,
            pnl_usd=_finite(pnl),
            drawdown_pct=_finite(self.drawdown_pct),
            equity_usd=_finite(self.equity - self.pnl_usd),
            avg_total_cost_bps=base.avg_total_cost_bps,
            best_venue=base.best_venue,
            deployment_id=base.deployment_id,
        )
        _assert_finite(asdict(res), "Phase34CycleResult")
        self.results.append(res)
        return res

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        c = int(cycles) if cycles is not None else int(self.config.cycles)
        all_res = [self.run_cycle(i) for i in range(1, c + 1)]
        report = {
            "phase": "34_portfolio_capital",
            "seed": self.seed,
            "paper_only": True,
            "cycles": c,
            "results": [asdict(r) for r in all_res],
            "total_cycles": len(all_res),
            "final_risk_ok": all_res[-1].risk_ok if all_res else True,
            "final_margin_ratio": all_res[-1].margin_ratio if all_res else 0.0,
            "final_equity_usd": all_res[-1].equity_usd if all_res else self.equity,
            "total_pnl_usd": sum(r.pnl_usd for r in all_res),
            "any_margin_call": any(r.margin_call for r in all_res),
        }
        _assert_finite(report, "phase34_campaign_report")
        return report

    def generate_report(self, outdir: str) -> Dict[str, Any]:
        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        camp = self.run_campaign()
        import json

        json_path = out / "PHASE34_PORTFOLIO_CAPITAL_LOOP_REPORT.json"
        json_path.write_text(json.dumps(camp, indent=2))
        md_path = out / "PHASE34_PORTFOLIO_CAPITAL_LOOP_REPORT.md"
        md_path.write_text(f"# Phase 34 Portfolio Capital Loop Report\n\nSeed: {self.seed}\nPaper-only: true\nCycles: {camp['cycles']}\n")
        self.greeks.generate_report(outdir)
        self.margin.generate_report(outdir)
        self.realloc.generate_report(outdir)
        camp_path = out / "PHASE34_CAMPAIGN_SUMMARY.json"
        camp_path.write_text(json.dumps(camp, indent=2))
        return {"json": str(json_path), "md": str(md_path), "summary": str(camp_path)}
