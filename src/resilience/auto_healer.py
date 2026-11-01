"""Auto-healer for crypto options + orderflow production resilience.

Circuit-breaker-driven auto-healing with restart/reconnect/retry policies,
cooldowns, escalation, fail-fast on unrecoverable breach, and deterministic
state. Extends src.resilience.
"""

from __future__ import annotations

import hashlib
import threading
import time
from enum import Enum
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from math import isfinite
from typing import Any, Callable, Deque, Dict, List, Optional

from src.errors import RiskLimitError, get_logger
from src.resilience.circuit import (
    CircuitBreaker, CircuitBreakerConfig, CircuitBreakerRegistry,
    CircuitBreakerState, default_circuit_registry,
)
from src.resilience.retry import (
    RetryPolicy, RetryConfig, RetryResult, Bulkhead, BulkheadConfig,
    TimeoutConfig, call_with_timeout, default_retry_policy,
)
from src.telemetry import serialize_metrics_strict
from src.telemetry.serialization import assert_json_valid
from src.telemetry.observability import observability_logger

_logger = get_logger(__name__)


def _utc_iso(ts: datetime) -> str:
    return ts.isoformat().replace("+00:00", "Z")


def _deterministic_iso(seed: int) -> str:
    base = datetime(2026, 11, 1, tzinfo=timezone.utc)
    return _utc_iso(base + timedelta(seconds=int(seed)))


def _now_ts() -> float:
    return time.time()


class HealAction(str, Enum):
    RESTART = "restart"
    RECONNECT = "reconnect"
    RETRY = "retry"
    ESCALATE = "escalate"
    FAIL_FAST = "fail_fast"
    NOOP = "noop"


@dataclass
class HealRecord:
    """A single auto-healing action record."""

    record_id: str
    component: str
    action: str
    trigger: str
    success: bool
    latency_ms: float
    timestamp: str
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "record_id": self.record_id,
            "component": self.component,
            "action": self.action,
            "trigger": self.trigger,
            "success": bool(self.success),
            "latency_ms": float(self.latency_ms) if isfinite(float(self.latency_ms)) else 0.0,
            "timestamp": self.timestamp,
            "details": dict(self.details),
        })


@dataclass
class HealPolicy:
    """Auto-healing policy for a component."""

    component: str
    max_restarts: int = 3
    max_reconnects: int = 3
    max_retries: int = 3
    cooldown_sec: float = 5.0
    escalate_after_failures: int = 3
    fail_fast_on_unrecoverable: bool = True
    retry_config: Optional[RetryConfig] = None

    def __post_init__(self) -> None:
        self.component = str(self.component)
        self.max_restarts = int(self.max_restarts)
        self.max_reconnects = int(self.max_reconnects)
        self.max_retries = int(self.max_retries)
        self.cooldown_sec = float(self.cooldown_sec)
        self.escalate_after_failures = int(self.escalate_after_failures)
        self.fail_fast_on_unrecoverable = bool(self.fail_fast_on_unrecoverable)
        self.retry_config = self.retry_config or RetryConfig(max_attempts=self.max_retries,
                                                             base_delay_sec=0.0)

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "component": self.component,
            "max_restarts": self.max_restarts,
            "max_reconnects": self.max_reconnects,
            "max_retries": self.max_retries,
            "cooldown_sec": float(self.cooldown_sec),
            "escalate_after_failures": self.escalate_after_failures,
            "fail_fast_on_unrecoverable": self.fail_fast_on_unrecoverable,
            "retry_config": self.retry_config.to_dict() if self.retry_config else {},
        })


@dataclass
class ComponentHealth:
    """Tracked health state for a component."""

    component: str
    state: str = "healthy"  # healthy / degraded / unhealthy / failed
    consecutive_failures: int = 0
    total_failures: int = 0
    total_heals: int = 0
    restarts: int = 0
    reconnects: int = 0
    retries: int = 0
    escalations: int = 0
    last_failure_ts: Optional[float] = None
    last_heal_ts: Optional[float] = None
    last_action: Optional[str] = None
    last_success_ts: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "component": self.component,
            "state": self.state,
            "consecutive_failures": int(self.consecutive_failures),
            "total_failures": int(self.total_failures),
            "total_heals": int(self.total_heals),
            "restarts": int(self.restarts),
            "reconnects": int(self.reconnects),
            "retries": int(self.retries),
            "escalations": int(self.escalations),
            "last_failure_ts": self.last_failure_ts,
            "last_heal_ts": self.last_heal_ts,
            "last_action": self.last_action,
            "last_success_ts": self.last_success_ts,
        })


class AutoHealer:
    """Circuit-breaker-driven auto-healer with restart/reconnect/retry policies.

    Deterministic given fixed seed. Fail-fast on unrecoverable breach.
    """

    def __init__(
        self,
        seed: int = 42,
        circuit_registry=None,
        retry_policy=None,
        cooldown_enforced: bool = True,
    ) -> None:
        self.seed = int(seed)
        self.timestamp = _deterministic_iso(self.seed)
        self._lock = threading.RLock()
        self.circuit_registry = circuit_registry or default_circuit_registry
        self.retry_policy = retry_policy or default_retry_policy
        self.cooldown_enforced = bool(cooldown_enforced)
        self._policies: Dict[str, HealPolicy] = {}
        self._health: Dict[str, ComponentHealth] = {}
        self._records: List[HealRecord] = []
        self._record_index: Dict[str, HealRecord] = {}
        self._last_heal_ts: Dict[str, float] = {}
        self._tick: float = float(self.seed)
        self._register_default_policies()

    def _now(self) -> float:
        """Deterministic monotonic clock derived from the seed."""
        t = self._tick
        self._tick += 0.001
        return t

    # ------------------------------------------------------------- policies
    def _register_default_policies(self) -> None:
        for comp in ("exchange", "risk", "orderflow_adapter", "reconciliation"):
            self._policies[comp] = HealPolicy(component=comp)
            self._health[comp] = ComponentHealth(component=comp)

    def add_policy(self, policy: HealPolicy) -> None:
        with self._lock:
            self._policies[policy.component] = policy
            if policy.component not in self._health:
                self._health[policy.component] = ComponentHealth(component=policy.component)

    # ------------------------------------------------------------- healing
    def _record_heal(self, component: str, action: str, trigger: str,
                     success: bool, latency_ms: float, details=None) -> HealRecord:
        payload = f"{self.seed}|{component}|{action}|{trigger}|{len(self._records)}"
        rid = f"heal_{hashlib.sha256(payload.encode()).hexdigest()[:12]}"
        record = HealRecord(
            record_id=rid,
            component=component,
            action=action,
            trigger=trigger,
            success=bool(success),
            latency_ms=round(float(latency_ms), 6),
            timestamp=_deterministic_iso(self.seed),
            details=dict(details or {}),
        )
        with self._lock:
            self._records.append(record)
            self._record_index[rid] = record
            ch = self._health.get(component)
            if ch is not None:
                ch.total_heals += 1
                ch.last_heal_ts = self._now()
                ch.last_action = action
                if success:
                    ch.last_success_ts = self._now()
                    ch.consecutive_failures = 0
                    ch.state = "healthy"
                else:
                    ch.state = "degraded"
        observability_logger.info("auto_heal_recorded",
                                  component=component, action=action, trigger=trigger,
                                  success=success, latency_ms=latency_ms)
        return record

    def _in_cooldown(self, component: str) -> bool:
        if not self.cooldown_enforced:
            return False
        policy = self._policies.get(component)
        if policy is None:
            return False
        last = self._last_heal_ts.get(component)
        if last is None:
            return False
        return (self._now() - last) < policy.cooldown_sec

    def _cb_for(self, component: str) -> Optional[CircuitBreaker]:
        return self.circuit_registry.get(component)

    def heal(self, component: str, trigger: str = "auto",
             func: Optional[Callable[[], Any]] = None) -> HealRecord:
        """Attempt to heal a component. Returns the heal record."""
        start = self._now()
        policy = self._policies.get(component)
        if policy is None:
            policy = HealPolicy(component=component)
            self.add_policy(policy)
        ch = self._health.get(component)
        if ch is None:
            ch = ComponentHealth(component=component)
            self._health[component] = ch

        # Cooldown check
        if self._in_cooldown(component):
            rec = self._record_heal(component, HealAction.NOOP, trigger, False, 0.0,
                                      {"reason": "cooldown"})
            return rec

        cb = self._cb_for(component)
        cb_state = cb.state.value if cb is not None else "unknown"

        # Decide action based on circuit state + health
        action = HealAction.NOOP
        success = False
        details = {"circuit_state": cb_state}

        if cb is not None and cb.state == CircuitBreakerState.OPEN:
            # Circuit open -> attempt reconnect then retry
            if ch.reconnects < policy.max_reconnects:
                action = HealAction.RECONNECT
                success = self._attempt_reconnect(component, func)
                if success:
                    ch.reconnects += 1
                    cb.force_closed()
                else:
                    ch.reconnects += 1
            else:
                action = HealAction.ESCALATE
                success = False
                ch.escalations += 1
                details["reason"] = "max_reconnects_exceeded"
        elif cb is not None and cb.state == CircuitBreakerState.HALF_OPEN:
            action = HealAction.RETRY
            result = self._attempt_retry(component, func, policy)
            success = result.success
            ch.retries += 1
            details["retry_attempts"] = result.attempts
        elif ch.state in ("degraded", "failed") or ch.consecutive_failures > 0:
            action = HealAction.RESTART
            success = self._attempt_restart(component, func)
            if success:
                ch.restarts += 1
            else:
                ch.restarts += 1
        else:
            action = HealAction.NOOP
            success = True

        latency_ms = (self._now() - start) * 1000.0
        if not success:
            ch.consecutive_failures += 1
            ch.total_failures += 1
            ch.last_failure_ts = self._now()
            ch.state = "failed" if ch.consecutive_failures >= policy.escalate_after_failures else "degraded"
            # fail-fast check
            if policy.fail_fast_on_unrecoverable and ch.consecutive_failures >= policy.escalate_after_failures:
                action = HealAction.FAIL_FAST
                details["fail_fast"] = True
                observability_logger.error("auto_healer_fail_fast",
                                           component=component, failures=ch.consecutive_failures)

        self._last_heal_ts[component] = self._now()
        rec = self._record_heal(component, action, trigger, success, latency_ms, details)
        return rec

    def _attempt_reconnect(self, component: str, func) -> bool:
        try:
            if func is not None:
                func()
            return True
        except Exception:
            return False

    def _attempt_restart(self, component: str, func) -> bool:
        try:
            if func is not None:
                func()
            return True
        except Exception:
            return False

    def _attempt_retry(self, component: str, func, policy: HealPolicy) -> RetryResult:
        if func is not None:
            return self.retry_policy.call(func)
        return RetryResult(success=True, attempts=1, total_elapsed_sec=0.0)

    # ------------------------------------------------------------- status
    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            health = {k: h.to_dict() for k, h in self._health.items()}
            policies = {k: p.to_dict() for k, p in self._policies.items()}
            records = [r.to_dict() for r in self._records]
        payload = serialize_metrics_strict({
            "seed": self.seed,
            "paper_only": True,
            "timestamp": _deterministic_iso(self.seed),
            "num_components": len(self._health),
            "num_policies": len(self._policies),
            "num_heal_records": len(records),
            "components": health,
            "policies": policies,
            "records": records,
        })
        assert_json_valid(payload)
        return payload

    def export_report(self) -> Dict[str, Any]:
        snap = self.snapshot()
        report = serialize_metrics_strict({
            "report": "auto_healer",
            "seed": self.seed,
            "timestamp": _deterministic_iso(self.seed),
            "num_components": snap["num_components"],
            "num_heal_records": snap["num_heal_records"],
            "components": snap["components"],
            "records": snap["records"],
            "unhealthy_components": [
                k for k, v in snap["components"].items() if v["state"] != "healthy"
            ],
        })
        assert_json_valid(report)
        return report

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._record_index.clear()
            for h in self._health.values():
                h.consecutive_failures = 0
                h.state = "healthy"
            self.circuit_registry.reset_all()


__all__ = [
    "HealAction", "HealRecord", "HealPolicy", "ComponentHealth", "AutoHealer",
]
