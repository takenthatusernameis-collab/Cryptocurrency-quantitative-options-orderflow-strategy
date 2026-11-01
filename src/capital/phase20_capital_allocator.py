"""Phase 20 CapitalAllocator: risk-budget allocation, per-strategy/per-venue caps,
Kelly-ish sizing with hard limits, rebalance hooks, deterministic. Crypto options + orderflow."""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

from src.telemetry.serialization import serialize_metrics_strict


_BASE_DAY = datetime(2026, 11, 1, tzinfo=timezone.utc)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _det_ts(seed: int, offset: int = 0) -> str:
    return (_BASE_DAY + timedelta(seconds=int(seed) + int(offset))).isoformat().replace("+00:00", "Z")


@dataclass
class Phase20AllocationConfig:
    total_capital: float = 2_000_000.0
    max_drawdown_pct: float = 0.08
    risk_budget_pct: float = 0.015
    max_leverage: float = 1.8
    per_strategy_cap: float = 0.25
    per_venue_cap: float = 0.35
    reserve_pct: float = 0.07
    kelly_fraction: float = 0.25
    rebalance_threshold_pct: float = 0.05
    paper_only: bool = True


def default_phase20_allocation_config() -> Phase20AllocationConfig:
    return Phase20AllocationConfig()


@dataclass
class Phase20CapitalAllocation:
    allocation_id: str
    strategy: str
    venue: str
    symbol: str
    allocated_capital: float
    risk_budget: float
    kelly_sized: float
    leverage_limit: float
    rebalance_required: bool
    drawdown_guard_active: bool
    paper_only: bool
    timestamp: str
    rationale: str


class Phase20CapitalAllocator:
    def __init__(self, config: Optional[Phase20AllocationConfig] = None, seed: int = 42):
        self.config = config or default_phase20_allocation_config()
        if self.config.paper_only is False:
            raise ValueError("Phase20CapitalAllocator: paper_only must remain True by default")
        self.config.paper_only = True
        self.seed = int(seed)
        self._counter = 0

    def _aid(self) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|p20alloc|{self._counter}".encode()).hexdigest()[:12]
        return f"p20_alloc_{h}"

    def allocate(
        self,
        strategies: List[str],
        venues: List[str],
        symbols: List[str],
        current_drawdown_pct: float = 0.0,
        expected_edge: Optional[Dict[str, float]] = None,
        current_allocations: Optional[Dict[str, float]] = None,
    ) -> List[Phase20CapitalAllocation]:
        if not math.isfinite(current_drawdown_pct):
            raise ValueError("current_drawdown_pct must be finite")
        if current_drawdown_pct < 0.0 or current_drawdown_pct > 1.0:
            raise ValueError("current_drawdown_pct must be in [0,1]")

        expected_edge = expected_edge or {}
        current_allocations = current_allocations or {}
        total = float(self.config.total_capital)
        reserve = total * float(self.config.reserve_pct)
        deployable = total - reserve
        if deployable < 0.0:
            raise ValueError("reserve_pct exceeds total_capital")

        n = max(1, len(strategies) * len(venues) * len(symbols))
        base = deployable / float(n)
        dd_guard = current_drawdown_pct >= self.config.max_drawdown_pct
        if dd_guard:
            base = 0.0

        allocations: List[Phase20CapitalAllocation] = []
        idx = 0
        for strat in strategies:
            for venue in venues:
                for sym in symbols:
                    idx += 1
                    key = f"{strat}|{venue}|{sym}"
                    edge = float(expected_edge.get(key, 0.01))
                    if not math.isfinite(edge):
                        edge = 0.01
                    kelly_raw = edge / max(0.02, 1.0 - edge)
                    kelly_sized = alloc_cap_candidate = min(base, total * self.config.per_strategy_cap)
                    kelly_sized = min(kelly_sized * (1.0 + self.config.kelly_fraction * kelly_raw), alloc_cap_candidate)
                    alloc_cap = kelly_sized
                    alloc_cap = min(alloc_cap, total * self.config.per_venue_cap)
                    if dd_guard:
                        alloc_cap = 0.0
                    risk_budget = alloc_cap * self.config.risk_budget_pct
                    if not math.isfinite(alloc_cap) or alloc_cap < 0.0:
                        alloc_cap = 0.0
                    if not math.isfinite(risk_budget) or risk_budget < 0.0:
                        risk_budget = 0.0
                    if not math.isfinite(kelly_sized) or kelly_sized < 0.0:
                        kelly_sized = 0.0
                    cur = float(current_allocations.get(key, alloc_cap))
                    if not math.isfinite(cur):
                        cur = alloc_cap
                    rebalance_required = abs(cur - alloc_cap) / max(alloc_cap, 1e-12) > self.config.rebalance_threshold_pct
                    allocations.append(
                        Phase20CapitalAllocation(
                            allocation_id=self._aid(),
                            strategy=str(strat),
                            venue=str(venue).lower(),
                            symbol=str(sym).upper(),
                            allocated_capital=float(alloc_cap),
                            risk_budget=float(risk_budget),
                            kelly_sized=float(kelly_sized),
                            leverage_limit=float(self.config.max_leverage),
                            rebalance_required=bool(rebalance_required),
                            drawdown_guard_active=bool(dd_guard),
                            paper_only=True,
                            timestamp=_det_ts(self.seed, idx),
                            rationale="deterministic_phase20_kelly_sized_allocation",
                        )
                    )
        return allocations

    def validate_invariants(self, allocations: List[Phase20CapitalAllocation]) -> Dict[str, Any]:
        total_alloc = sum(a.allocated_capital for a in allocations)
        by_strat: Dict[str, float] = {}
        by_venue: Dict[str, float] = {}
        violations: List[str] = []
        for a in allocations:
            by_strat[a.strategy] = by_strat.get(a.strategy, 0.0) + a.allocated_capital
            by_venue[a.venue] = by_venue.get(a.venue, 0.0) + a.allocated_capital
            if a.allocated_capital > self.config.total_capital * self.config.per_strategy_cap + 1e-12:
                violations.append(f"strategy_cap_exceeded:{a.strategy}")
            if a.allocated_capital > self.config.total_capital * self.config.per_venue_cap + 1e-12:
                violations.append(f"venue_cap_exceeded:{a.venue}")
            if a.risk_budget < 0.0 or not math.isfinite(a.risk_budget):
                violations.append(f"invalid_risk_budget:{a.allocation_id}")
            if a.allocated_capital < 0.0 or not math.isfinite(a.allocated_capital):
                violations.append(f"invalid_alloc:{a.allocation_id}")
            if not a.paper_only:
                violations.append(f"paper_only_violation:{a.allocation_id}")
        if total_alloc > self.config.total_capital * (1.0 - self.config.reserve_pct) + 1e-9:
            violations.append("total_deployable_exceeded")
        rep = {
            "timestamp": _det_ts(self.seed),
            "total_allocated": float(total_alloc),
            "total_capital": float(self.config.total_capital),
            "reserve_pct": float(self.config.reserve_pct),
            "by_strategy": {k: float(v) for k, v in by_strat.items()},
            "by_venue": {k: float(v) for k, v in by_venue.items()},
            "violations": violations,
            "valid": len(violations) == 0,
            "paper_only_enforced": all(a.paper_only for a in allocations) if allocations else True,
        }
        return serialize_metrics_strict(rep)

    def generate_report(self, allocations: List[Phase20CapitalAllocation]) -> Dict[str, Any]:
        inv = self.validate_invariants(allocations)
        rep = {
            "report": "PHASE20_CAPITAL_ALLOCATION_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "allocations": [asdict(a) for a in allocations],
            "invariants": inv,
            "counts": {"allocations": len(allocations), "rebalance_required": sum(1 for a in allocations if a.rebalance_required)},
            "paper_only": True,
        }
        return serialize_metrics_strict(rep)
