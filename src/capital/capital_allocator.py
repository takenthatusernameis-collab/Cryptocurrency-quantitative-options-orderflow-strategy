"""Deterministic capital budgeting across strategies/venues with risk-budget caps and drawdown guards.

Phase 14: live capital deployment with paper-only default.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from src.telemetry.serialization import serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _det_ts(seed: int) -> str:
    base = datetime(2026, 11, 1, tzinfo=timezone.utc)
    from datetime import timedelta
    return (base + timedelta(seconds=int(seed))).isoformat().replace("+00:00", "Z")


@dataclass
class AllocationConfig:
    total_capital: float = 1_000_000.0
    max_drawdown_pct: float = 0.10  # 10% hard cap
    risk_budget_pct: float = 0.02  # 2% per strategy risk budget
    max_leverage: float = 2.0
    per_strategy_cap: float = 0.30  # 30% of capital max per strategy
    per_venue_cap: float = 0.40
    reserve_pct: float = 0.05
    paper_only: bool = True


def default_allocation_config() -> AllocationConfig:
    return AllocationConfig()


@dataclass
class CapitalAllocation:
    allocation_id: str
    strategy: str
    venue: str
    symbol: str
    allocated_capital: float
    risk_budget: float
    leverage_limit: float
    drawdown_guard_active: bool
    paper_only: bool
    timestamp: str
    rationale: str


class CapitalAllocator:
    def __init__(self, config: Optional[AllocationConfig] = None, seed: int = 42):
        self.config = config or default_allocation_config()
        self.seed = int(seed)
        self._counter = 0
        # Enforce paper-only by default
        if self.config.paper_only is False:
            # Must still be explicitly allowed - but we enforce via gate; keep flag as-is
            pass
        else:
            self.config.paper_only = True

    def _aid(self) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|alloc|{self._counter}".encode()).hexdigest()[:12]
        return f"alloc_{h}"

    def allocate(
        self,
        strategies: List[str],
        venues: List[str],
        symbols: List[str],
        current_drawdown_pct: float = 0.0,
    ) -> List[CapitalAllocation]:
        if not math.isfinite(current_drawdown_pct):
            raise ValueError("current_drawdown_pct must be finite")
        if current_drawdown_pct < 0.0 or current_drawdown_pct > 1.0:
            raise ValueError("current_drawdown_pct must be in [0,1]")

        allocations: List[CapitalAllocation] = []
        total = float(self.config.total_capital)
        reserve = total * float(self.config.reserve_pct)
        deployable = total - reserve
        if deployable < 0:
            raise ValueError("reserve_pct exceeds total_capital")

        # Deterministic distribution
        n = max(1, len(strategies) * len(venues) * len(symbols))
        base = deployable / float(n)
        dd_guard = current_drawdown_pct >= self.config.max_drawdown_pct
        if dd_guard:
            base = 0.0  # hard drawdown guard

        idx = 0
        for strat in strategies:
            for venue in venues:
                for sym in symbols:
                    idx += 1
                    alloc_cap = min(base, total * self.config.per_strategy_cap)
                    alloc_cap = min(alloc_cap, total * self.config.per_venue_cap)
                    if dd_guard:
                        alloc_cap = 0.0
                    risk_budget = alloc_cap * self.config.risk_budget_pct
                    if not math.isfinite(alloc_cap) or alloc_cap < 0:
                        alloc_cap = 0.0
                    if not math.isfinite(risk_budget) or risk_budget < 0:
                        risk_budget = 0.0
                    allocations.append(
                        CapitalAllocation(
                            allocation_id=self._aid(),
                            strategy=str(strat),
                            venue=str(venue).lower(),
                            symbol=str(sym).upper(),
                            allocated_capital=float(alloc_cap),
                            risk_budget=float(risk_budget),
                            leverage_limit=float(self.config.max_leverage),
                            drawdown_guard_active=bool(dd_guard),
                            paper_only=bool(self.config.paper_only),
                            timestamp=_det_ts(self.seed + idx),
                            rationale=f"deterministic_allocation_seed{self.seed}",
                        )
                    )
        return allocations

    def validate_invariants(self, allocations: List[CapitalAllocation]) -> Dict[str, Any]:
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
            if a.risk_budget < 0 or not math.isfinite(a.risk_budget):
                violations.append(f"invalid_risk_budget:{a.allocation_id}")
            if a.allocated_capital < 0 or not math.isfinite(a.allocated_capital):
                violations.append(f"invalid_alloc:{a.allocation_id}")
            if not a.paper_only:
                # Paper-only must be enforced
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

    def generate_report(self, allocations: List[CapitalAllocation]) -> Dict[str, Any]:
        inv = self.validate_invariants(allocations)
        rep = {
            "report": "CAPITAL_ALLOCATION_REPORT",
            "timestamp": _det_ts(self.seed),
            "seed": self.seed,
            "config": asdict(self.config),
            "allocations": [asdict(a) for a in allocations],
            "invariants": inv,
            "counts": {"allocations": len(allocations)},
            "paper_only": bool(self.config.paper_only),
        }
        return serialize_metrics_strict(rep)
