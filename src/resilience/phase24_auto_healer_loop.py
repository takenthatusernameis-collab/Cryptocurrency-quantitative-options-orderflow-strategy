#!/usr/bin/env python3
"""Phase 24 Auto-Healer Loop (PAPER-ONLY).

Continuous health monitoring, auto-recovery, circuit-breaker integration, deterministic.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from src.telemetry.serialization import assert_json_valid, serialize_metrics_strict


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _make_id(seed: int, tag: str, idx: int) -> str:
    h = hashlib.sha256(f"{seed}|p24ah|{tag}|{idx}".encode()).hexdigest()[:12]
    return f"p24ah_{tag}_{h}"


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
class AutoHealerConfig:
    seed: int = 42
    paper_only: bool = True
    components: tuple = ("oms", "router", "risk", "data", "execution", "telemetry")
    check_interval_sec: float = 1.0
    max_retries: int = 5
    cooldown_sec: float = 5.0
    fail_fast: bool = True
    auto_recover: bool = True


@dataclass(frozen=True)
class HealthCheck:
    check_id: str
    component: str
    healthy: bool
    latency_ms: float
    error_rate: float
    uptime_pct: float
    timestamp: str


@dataclass(frozen=True)
class HealAction:
    action_id: str
    component: str
    action_type: str  # restart/reconnect/retry/escalate
    success: bool
    duration_ms: float
    reason: str
    timestamp: str


@dataclass(frozen=True)
class HealerState:
    component: str
    state: str  # healthy/degraded/unhealthy/recovered
    failures: int
    heals: int
    last_action: Optional[str]
    circuit_open: bool
    timestamp: str


class AutoHealerLoop:
    def __init__(self, config: Optional[AutoHealerConfig] = None, seed: int = 42):
        self.config = config or AutoHealerConfig(seed=seed)
        if not self.config.paper_only:
            raise ValueError("AutoHealerLoop: paper_only must remain True")
        self.config = AutoHealerConfig(
            seed=int(self.config.seed),
            paper_only=True,
            components=tuple(self.config.components),
            check_interval_sec=float(self.config.check_interval_sec),
            max_retries=int(self.config.max_retries),
            cooldown_sec=float(self.config.cooldown_sec),
            fail_fast=bool(self.config.fail_fast),
            auto_recover=bool(self.config.auto_recover),
        )
        self.seed = int(self.config.seed)
        self.health_checks: List[HealthCheck] = []
        self.heal_actions: List[HealAction] = []
        self.states: Dict[str, HealerState] = {}
        self.audit: List[Dict[str, Any]] = []
        for c in self.config.components:
            self.states[c] = HealerState(
                component=c,
                state="healthy",
                failures=0,
                heals=0,
                last_action=None,
                circuit_open=False,
                timestamp=_utc_now(),
            )

    def _log(self, action: str, details: Dict[str, Any]) -> None:
        self.audit.append({"timestamp": _utc_now(), "action": action, "details": dict(details)})

    def monitor(self, cycle: int) -> List[HealthCheck]:
        import random

        rng = random.Random(self.seed + 26000 + cycle)
        checks: List[HealthCheck] = []
        for c in self.config.components:
            healthy = rng.random() > 0.08  # mostly healthy
            err_rate = rng.uniform(0.0, 0.05) if healthy else rng.uniform(0.1, 0.4)
            lat = rng.uniform(1.0, 30.0)
            uptime = rng.uniform(99.9, 100.0) if healthy else rng.uniform(95.0, 99.5)
            hc = HealthCheck(
                check_id=_make_id(self.seed, "hc", len(self.health_checks) + len(checks)),
                component=c,
                healthy=bool(healthy),
                latency_ms=float(lat),
                error_rate=float(err_rate),
                uptime_pct=float(uptime),
                timestamp=_utc_now(),
            )
            _assert_finite(asdict(hc), f"health_{c}")
            checks.append(hc)
            if not healthy:
                st = self.states[c]
                self.states[c] = HealerState(
                    component=c,
                    state="degraded" if err_rate < 0.25 else "unhealthy",
                    failures=st.failures + 1,
                    heals=st.heals,
                    last_action=st.last_action,
                    circuit_open=err_rate >= 0.3,
                    timestamp=_utc_now(),
                )
            else:
                st = self.states[c]
                if st.failures > 0 and self.config.auto_recover:
                    self.states[c] = HealerState(
                        component=c,
                        state="recovered" if st.failures < 3 else "healthy",
                        failures=st.failures,
                        heals=st.heals,
                        last_action=st.last_action,
                        circuit_open=False,
                        timestamp=_utc_now(),
                    )
        self.health_checks.extend(checks)
        self._log("monitored", {"cycle": cycle, "count": len(checks)})
        return checks

    def heal(self, checks: List[HealthCheck], cycle: int) -> List[HealAction]:
        import random

        rng = random.Random(self.seed + 26100 + cycle)
        actions: List[HealAction] = []
        for hc in checks:
            if not hc.healthy and self.config.auto_recover:
                st = self.states.get(hc.component)
                if st and st.failures <= self.config.max_retries:
                    act_type = "retry" if st.failures < 2 else ("reconnect" if st.failures < 4 else "restart")
                    if st.circuit_open:
                        act_type = "escalate"
                    success = rng.random() > 0.1
                    dur = rng.uniform(10.0, 500.0)
                    ha = HealAction(
                        action_id=_make_id(self.seed, "ha", len(self.heal_actions) + len(actions)),
                        component=hc.component,
                        action_type=act_type,
                        success=bool(success),
                        duration_ms=float(dur),
                        reason=f"auto_heal_cycle_{cycle}",
                        timestamp=_utc_now(),
                    )
                    _assert_finite(asdict(ha), f"heal_{hc.component}")
                    actions.append(ha)
                    if success:
                        self.states[hc.component] = HealerState(
                            component=hc.component,
                            state="recovered",
                            failures=st.failures,
                            heals=st.heals + 1,
                            last_action=act_type,
                            circuit_open=False,
                            timestamp=_utc_now(),
                        )
        self.heal_actions.extend(actions)
        self._log("healed", {"cycle": cycle, "count": len(actions)})
        return actions

    def run_loop(self, cycles: int = 10) -> Dict[str, Any]:
        summary = []
        for c in range(cycles):
            checks = self.monitor(c)
            acts = self.heal(checks, c)
            summary.append({
                "cycle": c,
                "checks": len(checks),
                "unhealthy": len([x for x in checks if not x.healthy]),
                "heals": len(acts),
                "paper_only": True,
            })
        self._log("loop_completed", {"cycles": cycles})
        return serialize_metrics_strict({"summary": summary, "cycles": cycles, "paper_only": True})

    def generate_report(self) -> Dict[str, Any]:
        total_heals = len(self.heal_actions)
        success_heals = len([h for h in self.heal_actions if h.success])
        success_rate = (success_heals / total_heals) if total_heals > 0 else 1.0
        rep = {
            "report": "PHASE24_AUTO_HEALER_REPORT",
            "timestamp": _utc_now(),
            "seed": self.seed,
            "config": asdict(self.config),
            "total_health_checks": len(self.health_checks),
            "total_heal_actions": total_heals,
            "heal_success_rate": float(success_rate),
            "states": {k: asdict(v) for k, v in self.states.items()},
            "recent_heals": [asdict(h) for h in self.heal_actions[-50:]],
            "audit_count": len(self.audit),
            "paper_only": True,
        }
        _assert_finite(rep, "auto_healer_report")
        assert_json_valid(rep)
        return serialize_metrics_strict(rep)
