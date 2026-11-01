"""
Phase 34: Cross-Margin Engine for Crypto Options Vol Surface Arbitrage + Orderflow.

Cross-margin requirements, stress loss scenarios, margin call detection, deterministic.
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
    h = hashlib.sha256(f"{seed}|p34margin|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p34margin_{tag}_{h}"


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
class CrossMarginConfig34:
    seed: int = 42
    paper_only: bool = True
    underlyings: tuple = ("BTC", "ETH", "SOL", "XRP")
    venues: tuple = ("deribit", "okx", "bybit", "binance")
    cycles: int = 10
    initial_margin_rate: float = 0.15
    maintenance_margin_rate: float = 0.10
    cross_margin_discount: float = 0.15
    stress_scenarios: int = 4
    margin_call_threshold: float = 1.0


@dataclass(frozen=True)
class StressScenario:
    name: str
    shock_pct: float
    delta_loss_usd: float
    gamma_loss_usd: float
    vega_loss_usd: float
    total_loss_usd: float
    paper_only: bool
    timestamp: str


@dataclass(frozen=True)
class MarginCycleResult:
    cycle: int
    timestamp: str
    paper_only: bool
    initial_margin_usd: float
    maintenance_margin_usd: float
    cross_margin_required_usd: float
    available_margin_usd: float
    margin_ratio: float
    stress_losses: Tuple[StressScenario, ...]
    worst_case_loss_usd: float
    margin_call: bool
    liquidation_risk: bool
    blocked_reasons: Tuple[str, ...]


class CrossMarginEngine:
    """Cross-margin requirements, stress tests, margin call detection."""

    def __init__(self, config: Optional[CrossMarginConfig34] = None, seed: int = 42) -> None:
        self.config = config or CrossMarginConfig34(seed=seed)
        if not self.config.paper_only:
            raise ValueError("CrossMarginEngine: paper_only must remain True (live path hard-gated)")
        self.config = CrossMarginConfig34(
            seed=int(self.config.seed),
            paper_only=True,
            underlyings=tuple(self.config.underlyings),
            venues=tuple(self.config.venues),
            cycles=int(self.config.cycles),
            initial_margin_rate=float(self.config.initial_margin_rate),
            maintenance_margin_rate=float(self.config.maintenance_margin_rate),
            cross_margin_discount=float(self.config.cross_margin_discount),
            stress_scenarios=int(self.config.stress_scenarios),
            margin_call_threshold=float(self.config.margin_call_threshold),
        )
        self.seed = int(self.config.seed)
        self.results: List[MarginCycleResult] = []
        self._counter = 0

    def _next_id(self, tag: str) -> str:
        self._counter += 1
        return _make_id(self.seed, tag, self._counter)

    def compute_margin(self, cycle: int, equity_usd: float = 200000.0, portfolio_notional_usd: float = 1000000.0) -> MarginCycleResult:
        im = portfolio_notional_usd * self.config.initial_margin_rate
        mm = portfolio_notional_usd * self.config.maintenance_margin_rate
        cm_req = im * (1.0 - self.config.cross_margin_discount)
        avail = max(0.0, equity_usd - cm_req * 0.1)
        margin_ratio = avail / max(1e-12, cm_req)
        stress_list: List[StressScenario] = []
        scenarios = [("spot_down10", -0.10), ("vol_up20", 0.20), ("spot_down15vol_up15", -0.15), ("tail_wide", -0.25)]
        for name, shock in scenarios[: self.config.stress_scenarios]:
            seed = int(hashlib.sha256(f"{name}|{cycle}|{self.seed}".encode()).hexdigest()[:8], 16) % (2 ** 31)
            import random

            rng = random.Random(seed)
            delta_loss = _finite(portfolio_notional_usd * abs(shock) * rng.uniform(0.3, 0.7) * (1.0 if shock < 0 else 0.3))
            gamma_loss = _finite(portfolio_notional_usd * abs(shock) ** 2 * rng.uniform(0.1, 0.3))
            vega_loss = _finite(portfolio_notional_usd * rng.uniform(0.02, 0.08) * (1.0 if "vol" in name else 0.01))
            total_loss = delta_loss + gamma_loss + vega_loss
            stress_list.append(
                StressScenario(
                    name=name,
                    shock_pct=float(shock),
                    delta_loss_usd=_finite(delta_loss),
                    gamma_loss_usd=_finite(gamma_loss),
                    vega_loss_usd=_finite(vega_loss),
                    total_loss_usd=_finite(total_loss),
                    paper_only=True,
                    timestamp=_utc_now(),
                )
            )
        worst = max((s.total_loss_usd for s in stress_list), default=0.0)
        margin_call = margin_ratio < self.config.margin_call_threshold or worst > avail
        liq_risk = margin_ratio < 0.8
        blocked: List[str] = []
        if margin_call:
            blocked.append("margin_call")
        if liq_risk:
            blocked.append("liquidation_risk")
        res = MarginCycleResult(
            cycle=cycle,
            timestamp=_utc_now(),
            paper_only=True,
            initial_margin_usd=_finite(im),
            maintenance_margin_usd=_finite(mm),
            cross_margin_required_usd=_finite(cm_req),
            available_margin_usd=_finite(avail),
            margin_ratio=_finite(margin_ratio),
            stress_losses=tuple(stress_list),
            worst_case_loss_usd=_finite(worst),
            margin_call=bool(margin_call),
            liquidation_risk=bool(liq_risk),
            blocked_reasons=tuple(blocked),
        )
        _assert_finite(asdict(res), "MarginCycleResult")
        self.results.append(res)
        return res

    def run_campaign(self, cycles: Optional[int] = None) -> Dict[str, Any]:
        c = int(cycles) if cycles is not None else int(self.config.cycles)
        all_res = [self.compute_margin(i) for i in range(1, c + 1)]
        report = {
            "phase": "34_cross_margin",
            "seed": self.seed,
            "paper_only": True,
            "cycles": c,
            "results": [asdict(r) for r in all_res],
            "total_cycles": len(all_res),
            "final_margin_ratio": all_res[-1].margin_ratio if all_res else 0.0,
            "any_margin_call": any(r.margin_call for r in all_res),
        }
        _assert_finite(report, "margin_campaign_report")
        return report

    def generate_report(self, outdir: str) -> Dict[str, Any]:
        from pathlib import Path
        import json

        out = Path(outdir)
        out.mkdir(parents=True, exist_ok=True)
        camp = self.run_campaign()
        json_path = out / "PHASE34_CROSS_MARGIN_REPORT.json"
        json_path.write_text(json.dumps(camp, indent=2))
        md_path = out / "PHASE34_CROSS_MARGIN_REPORT.md"
        md_path.write_text(f"# Phase 34 Cross Margin Report\n\nSeed: {self.seed}\nPaper-only: true\nCycles: {camp['cycles']}\n")
        return {"json": str(json_path), "md": str(md_path)}
