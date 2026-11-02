"""
Phase 42: Orderflow-driven hedged executor for crypto options.
Uses orderflow microstructure signals (OFI/imbalance/footprint) with regime-aware
dynamic hedge ratios, budget constraints, slippage-aware sizing. PAPER-ONLY hard gate.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p42hedge|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p42hedge_{tag}_{h}"


def _finite(x: float, default: float = 0.0) -> float:
    try:
        v = float(x)
    except Exception:
        return default
    return v if math.isfinite(v) else default


def _assert_finite_dict(d: Dict[str, Any], label: str = "obj") -> None:
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

    walk(d, "$")
    if bad:
        raise ValueError(f"Non-finite in {label}: {bad[:10]}")


@dataclass(frozen=True)
class HedgedExecutorConfig42:
    seed: int = 42043
    paper_only: bool = True
    underlyings: Tuple[str, ...] = ("BTC", "ETH", "SOL", "XRP")
    venues: Tuple[str, ...] = ("deribit", "okx", "bybit", "binance")
    cycles: int = 16
    max_hedge_budget_usd: float = 250000.0
    max_slippage_bps: float = 12.0
    orderflow_sensitivity: float = 0.65
    gamma_hedge_enabled: bool = True


@dataclass(frozen=True)
class OrderflowSignal:
    signal_id: str
    underlying: str
    venue: str
    ofi: float
    imbalance: float
    footprint_pressure: float
    liquidity_score: float
    regime: str
    timestamp: str


@dataclass(frozen=True)
class HedgeOrder:
    order_id: str
    underlying: str
    venue: str
    side: str
    notional_usd: float
    hedge_ratio: float
    slippage_est_bps: float
    reason: str
    gamma_component: float
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class HedgedExecutionPlan:
    cycle: int
    timestamp: str
    paper_only: bool
    regime: str
    portfolio_delta_usd: float
    orderflow_signals: Tuple[OrderflowSignal, ...]
    hedge_orders: Tuple[HedgeOrder, ...]
    total_hedge_notional_usd: float
    hedge_budget_utilization: float
    avg_slippage_est_bps: float
    delta_neutral_after_hedge_est: float
    gamma_hedged_usd: float
    within_budget: bool
    within_slippage: bool
    execution_ok: bool
    warnings: Tuple[str, ...]


class Phase42OrderflowHedgedExecutor:
    def __init__(self, config: Optional[HedgedExecutorConfig42] = None, seed: int = 42043) -> None:
        self.config = config or HedgedExecutorConfig42(seed=seed)
        if not isinstance(self.config.paper_only, bool):
            raise ValueError("paper_only must be bool")
        if not self.config.paper_only:
            raise ValueError("Phase42OrderflowHedgedExecutor: paper_only must remain True (live path hard-gated)")
        self.config = HedgedExecutorConfig42(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            cycles=int(self.config.cycles),
            max_hedge_budget_usd=float(self.config.max_hedge_budget_usd),
            max_slippage_bps=float(self.config.max_slippage_bps),
            orderflow_sensitivity=float(self.config.orderflow_sensitivity),
            gamma_hedge_enabled=bool(self.config.gamma_hedge_enabled),
        )
        self.seed = int(self.config.seed)
        self._counter = 0
        self.plans: List[HedgedExecutionPlan] = []

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def _regime(self, cycle: int) -> str:
        r = (self.seed + cycle * 11) % 4
        return ("calm", "trend", "volup", "stressed")[r]

    def generate_orderflow_signals(self, cycle: int) -> List[OrderflowSignal]:
        import random
        rng = random.Random(int(hashlib.sha256(f"{self.seed}|of|{cycle}".encode()).hexdigest()[:16], 16))
        sigs: List[OrderflowSignal] = []
        regime = self._regime(cycle)
        for u in self.config.underlyings:
            for v in self.config.venues[:2]:
                ofi = rng.uniform(-0.8, 0.8)
                imb = rng.uniform(-0.6, 0.6)
                fp = rng.uniform(-0.5, 0.5)
                liq = rng.uniform(0.4, 0.95)
                sigs.append(OrderflowSignal(
                    signal_id=self._next_id("sig"),
                    underlying=u,
                    venue=v,
                    ofi=_finite(ofi),
                    imbalance=_finite(imb),
                    footprint_pressure=_finite(fp),
                    liquidity_score=_finite(liq),
                    regime=regime,
                    timestamp=_utc_now(),
                ))
        return sigs

    def plan_hedge(self, cycle: int, portfolio_delta_usd: float = 0.0, portfolio_gamma_usd: float = 0.0,
                   orderflow_signals: Optional[List[OrderflowSignal]] = None) -> HedgedExecutionPlan:
        if orderflow_signals is None:
            orderflow_signals = self.generate_orderflow_signals(cycle)
        regime = self._regime(cycle)
        pd = _finite(portfolio_delta_usd)
        pg = _finite(portfolio_gamma_usd)

        hedge_orders: List[HedgeOrder] = []
        for sig in orderflow_signals:
            flow_adjust = 1.0 + self.config.orderflow_sensitivity * (sig.ofi + sig.imbalance) / 2.0
            if regime == "stressed":
                flow_adjust *= 1.25
            elif regime == "volup":
                flow_adjust *= 1.15
            base_notional = abs(pd) * 0.18 * flow_adjust
            gamma_comp = 0.0
            if self.config.gamma_hedge_enabled and abs(pg) > 10000:
                gamma_comp = abs(pg) * 0.12 * (0.8 + 0.4 * sig.liquidity_score)
                base_notional += gamma_comp
            base_notional = min(base_notional, self.config.max_hedge_budget_usd / max(1, len(orderflow_signals)))
            if base_notional < 1000.0:
                continue
            side = "sell" if (pd > 0 and (sig.ofi < 0 or sig.imbalance < 0)) or (pd < 0 and sig.ofi >= 0) else "buy"
            slip = _finite(4.0 + 8.0 * (1.0 - sig.liquidity_score) + (4.0 if regime == "stressed" else 0.0))
            if slip > self.config.max_slippage_bps:
                slip = self.config.max_slippage_bps
            ho = HedgeOrder(
                order_id=self._next_id("order"),
                underlying=sig.underlying,
                venue=sig.venue,
                side=side,
                notional_usd=_finite(min(base_notional, self.config.max_hedge_budget_usd)),
                hedge_ratio=_finite(abs(base_notional) / max(abs(pd), 1.0) if pd != 0 else 0.0),
                slippage_est_bps=_finite(slip),
                reason=f"of_driven_{regime}",
                gamma_component=_finite(gamma_comp),
                paper_only=True,
                timestamp=_utc_now(),
            )
            hedge_orders.append(ho)

        total_not = sum(h.notional_usd for h in hedge_orders)
        avg_slip = sum(h.slippage_est_bps for h in hedge_orders) / len(hedge_orders) if hedge_orders else 0.0
        budget_util = total_not / self.config.max_hedge_budget_usd if self.config.max_hedge_budget_usd > 0 else 0.0
        delta_after = pd - total_not * (0.7 if pd > 0 else -0.7)
        gamma_hedged = sum(h.gamma_component for h in hedge_orders)
        within_budget = total_not <= self.config.max_hedge_budget_usd + 1e-9
        within_slip = avg_slip <= self.config.max_slippage_bps + 1e-9
        warnings: List[str] = []
        if not within_budget:
            warnings.append("hedge_budget_exceeded")
        if not within_slip:
            warnings.append("slippage_above_threshold")
        if regime == "stressed":
            warnings.append("stressed_regime_hedge_aggressive")
        exec_ok = within_budget and within_slip

        plan = HedgedExecutionPlan(
            cycle=cycle,
            timestamp=_utc_now(),
            paper_only=True,
            regime=regime,
            portfolio_delta_usd=_finite(pd),
            orderflow_signals=tuple(orderflow_signals),
            hedge_orders=tuple(hedge_orders),
            total_hedge_notional_usd=_finite(total_not),
            hedge_budget_utilization=_finite(min(1.0, budget_util)),
            avg_slippage_est_bps=_finite(avg_slip),
            delta_neutral_after_hedge_est=_finite(delta_after),
            gamma_hedged_usd=_finite(gamma_hedged),
            within_budget=within_budget,
            within_slippage=within_slip,
            execution_ok=exec_ok,
            warnings=tuple(warnings),
        )
        _assert_finite_dict(asdict(plan), "HedgedExecutionPlan")
        self.plans.append(plan)
        return plan

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        c = int(cycles) if cycles is not None else int(self.config.cycles)
        import random
        rng = random.Random(self.seed)
        plans = []
        for i in range(1, c + 1):
            pd = rng.uniform(-400000.0, 400000.0)
            pg = rng.uniform(-200000.0, 200000.0)
            plans.append(self.plan_hedge(i, portfolio_delta_usd=pd, portfolio_gamma_usd=pg))
        report = {
            "phase": "PHASE42_ORDERFLOW_HEDGED_EXECUTOR",
            "seed": self.seed,
            "paper_only": True,
            "cycles": c,
            "plans": [asdict(p) for p in plans],
            "total_cycles": len(plans),
            "execution_ok_all": all(p.execution_ok for p in plans),
            "total_hedge_notional": sum(p.total_hedge_notional_usd for p in plans),
            "avg_budget_util": sum(p.hedge_budget_utilization for p in plans) / len(plans) if plans else 0.0,
        }
        _assert_finite_dict(report, "hedged_executor_campaign")
        return report

    def generate_reports(self, outdir: str) -> Dict[str, Any]:
        from pathlib import Path
        import json

        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        camp = self.run_campaign()
        j = out / "PHASE42_ORDERFLOW_HEDGED_EXECUTOR_REPORT.json"
        j.write_text(json.dumps(camp, indent=2))
        m = out / "PHASE42_ORDERFLOW_HEDGED_EXECUTOR_REPORT.md"
        m.write_text(f"# Phase 42 Orderflow Hedged Executor Report\n\nSeed: {self.seed}\nPaper-only: true\nCycles: {camp['cycles']}\nExecution OK all: {camp['execution_ok_all']}\nTotal hedge notional: {camp['total_hedge_notional']:.2f}\n")
        return {"json": str(j), "md": str(m)}
