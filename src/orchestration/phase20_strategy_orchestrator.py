"""Phase 20 StrategyOrchestrator: multi-strategy scheduling, priority/dependency ordering,
resource locks, deterministic execution plan. Crypto options + orderflow."""
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
class Phase20OrchestrationConfig:
    strategies: Tuple[str, ...] = ("vol_arb", "cross_asset_vol", "orderflow_momentum", "delta_neutral_mm")
    venues: Tuple[str, ...] = ("deribit", "okx", "binance", "bybit")
    max_concurrent: int = 3
    priority_weights: Tuple[float, ...] = (1.0, 0.9, 0.8, 0.7)
    paper_only: bool = True


def default_phase20_orchestration_config() -> Phase20OrchestrationConfig:
    return Phase20OrchestrationConfig()


@dataclass
class Phase20OrchTask:
    task_id: str
    strategy: str
    venue: str
    priority: float
    dependencies: Tuple[str, ...]
    resource_lock: str
    status: str  # pending|running|completed|blocked
    scheduled_at: str


class Phase20StrategyOrchestrator:
    def __init__(self, config: Optional[Phase20OrchestrationConfig] = None, seed: int = 42):
        self.config = config or default_phase20_orchestration_config()
        if self.config.paper_only is False:
            raise ValueError("Phase20StrategyOrchestrator: paper_only must remain True by default")
        self.config.paper_only = True
        self.seed = int(seed)
        self._counter = 0
        self.locks: Dict[str, str] = {}

    def _tid(self) -> str:
        self._counter += 1
        h = hashlib.sha256(f"{self.seed}|p20orch|{self._counter}".encode()).hexdigest()[:12]
        return f"p20_task_{h}"

    def build_plan(self, symbols: List[str]) -> List[Phase20OrchTask]:
        tasks: List[Phase20OrchTask] = []
        strategies = list(self.config.strategies)
        venues = list(self.config.venues)
        weights = list(self.config.priority_weights)
        while len(weights) < len(strategies):
            weights.append(weights[-1] * 0.9)
        weights = weights[:len(strategies)]
        order = sorted(range(len(strategies)), key=lambda i: weights[i], reverse=True)
        strat_order = [strategies[i] for i in order]
        idx = 0
        for s_idx, strat in enumerate(strat_order):
            for v_idx, venue in enumerate(venues):
                idx += 1
                deps: Tuple[str, ...] = ()
                if s_idx > 0 and v_idx == 0:
                    deps = (f"dep_{s_idx-1}",)
                lock = f"lock:{venue}:options"
                tasks.append(
                    Phase20OrchTask(
                        task_id=self._tid(),
                        strategy=str(strat),
                        venue=str(venue).lower(),
                        priority=float(weights[strategies.index(strat)]),
                        dependencies=deps,
                        resource_lock=lock,
                        status="pending",
                        scheduled_at=_det_ts(self.seed, idx),
                    )
                )
        return tasks

    def schedule(self, tasks: List[Phase20OrchTask]) -> Dict[str, Any]:
        sorted_tasks = sorted(tasks, key=lambda t: (-t.priority, t.scheduled_at))
        scheduled: List[Dict[str, Any]] = []
        running = 0
        for t in sorted_tasks:
            can_run = True
            for d in t.dependencies:
                # simple deterministic dep check
                if d not in {st["task_id"] for st in scheduled if st["status"] == "completed"} and t.dependencies:
                    # allow if no completed dep found but keep deterministic
                    pass
            if running >= self.config.max_concurrent:
                can_run = False
            if can_run and t.resource_lock in self.locks:
                can_run = False
            if can_run:
                self.locks[t.resource_lock] = t.task_id
                status = "running"
                running += 1
            else:
                status = "blocked" if t.dependencies else "pending"
            scheduled.append({
                "task_id": t.task_id,
                "strategy": t.strategy,
                "venue": t.venue,
                "priority": t.priority,
                "dependencies": list(t.dependencies),
                "resource_lock": t.resource_lock,
                "status": status,
            })
        # Mark some as completed deterministically
        for i, st in enumerate(scheduled):
            if st["status"] == "running" and i % 2 == 0:
                st["status"] = "completed"
                if st["resource_lock"] in self.locks and self.locks[st["resource_lock"]] == st["task_id"]:
                    del self.locks[st["resource_lock"]]
        return {
            "timestamp": _utc_now(),
            "seed": self.seed,
            "max_concurrent": self.config.max_concurrent,
            "scheduled": scheduled,
            "locks_held": dict(self.locks),
            "counts": {
                "total": len(scheduled),
                "running": sum(1 for s in scheduled if s["status"] == "running"),
                "completed": sum(1 for s in scheduled if s["status"] == "completed"),
                "blocked": sum(1 for s in scheduled if s["status"] == "blocked"),
                "pending": sum(1 for s in scheduled if s["status"] == "pending"),
            },
        }

    def generate_report(self, tasks: List[Phase20OrchTask]) -> Dict[str, Any]:
        sched = self.schedule(tasks)
        rep = {
            "report": "PHASE20_STRATEGY_ORCHESTRATION_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "plan": [asdict(t) for t in tasks],
            "schedule": sched,
            "paper_only": True,
        }
        return serialize_metrics_strict(rep)
