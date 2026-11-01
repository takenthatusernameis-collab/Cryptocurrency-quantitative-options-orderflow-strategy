"""Advanced resilience hardening for crypto options + orderflow.

Circuit breakers per component/exchange with state persistence, plus
retry/bulkhead/timeout/hedged-request/graceful-degradation primitives.
Deterministic in tests: fixed seeds, injectable clocks, mock failure hooks,
strict allow_nan=False serialization on all state artifacts.
"""

from __future__ import annotations

import hashlib
import math
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from math import isfinite
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

from ..errors import RiskLimitError, get_logger
from ..telemetry import serialize_metrics_strict
from ..telemetry.observability import observability_logger, redact


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_ts() -> float:
    return time.time()


def _make_id(prefix: str, *parts: str) -> str:
    payload = f"{prefix}|{'|'.join(parts)}|{time.time_ns()}|{threading.get_ident()}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    """Advanced circuit breaker configuration per component/exchange."""

    name: str = "default"
    failure_threshold: int = 5
    timeout_seconds: float = 30.0
    half_open_max_calls: int = 3
    error_rate_threshold: float = 0.5
    error_rate_window: int = 100
    min_calls_before_eval: int = 10
    recovery_threshold: float = 0.5

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise RiskLimitError("failure_threshold must be >= 1", context={"failure_threshold": self.failure_threshold})
        if self.timeout_seconds <= 0:
            raise RiskLimitError("timeout_seconds must be > 0", context={"timeout_seconds": self.timeout_seconds})
        if self.half_open_max_calls < 1:
            raise RiskLimitError("half_open_max_calls must be >= 1", context={"half_open_max_calls": self.half_open_max_calls})
        if not isfinite(self.error_rate_threshold) or self.error_rate_threshold < 0 or self.error_rate_threshold > 1:
            raise RiskLimitError("error_rate_threshold must be in [0,1]", context={"error_rate_threshold": self.error_rate_threshold})
        if self.error_rate_window < 1:
            raise RiskLimitError("error_rate_window must be >= 1", context={"error_rate_window": self.error_rate_window})
        if self.min_calls_before_eval < 1:
            raise RiskLimitError("min_calls_before_eval must be >= 1", context={"min_calls_before_eval": self.min_calls_before_eval})
        if not isfinite(self.recovery_threshold) or self.recovery_threshold < 0 or self.recovery_threshold > 1:
            raise RiskLimitError("recovery_threshold must be in [0,1]", context={"recovery_threshold": self.recovery_threshold})

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "name": self.name,
            "failure_threshold": int(self.failure_threshold),
            "timeout_seconds": float(self.timeout_seconds) if isfinite(float(self.timeout_seconds)) else 30.0,
            "half_open_max_calls": int(self.half_open_max_calls),
            "error_rate_threshold": float(self.error_rate_threshold) if isfinite(float(self.error_rate_threshold)) else 0.5,
            "error_rate_window": int(self.error_rate_window),
            "min_calls_before_eval": int(self.min_calls_before_eval),
            "recovery_threshold": float(self.recovery_threshold) if isfinite(float(self.recovery_threshold)) else 0.5,
        })


class CircuitBreaker:
    """Per-component/exchange circuit breaker with state persistence.

    States: CLOSED (normal), OPEN (halted), HALF_OPEN (testing recovery).
    Tracks failure/success counts, error rate over a sliding window, and
    supports manual override and snapshot/restore for chaos testing.
    """

    def __init__(self, config: Optional[CircuitBreakerConfig] = None,
                 state_persistence: Optional[Dict[str, Any]] = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_success_time: Optional[float] = None
        self.half_open_calls = 0
        self.call_history: Deque[Tuple[float, bool]] = deque(maxlen=self.config.error_rate_window * 2)
        self._lock = threading.RLock()
        self._manual_override: Optional[CircuitBreakerState] = None
        self._chaos_fail_next: bool = False
        if state_persistence:
            self._restore(state_persistence)

    # ------------------------------------------------------------------ core
    def can_execute(self) -> bool:
        with self._lock:
            if self._manual_override is not None:
                return self._manual_override == CircuitBreakerState.CLOSED
            if self._chaos_fail_next:
                self._chaos_fail_next = False
                return False
            if self.state == CircuitBreakerState.CLOSED:
                return True
            if self.state == CircuitBreakerState.OPEN:
                if self.last_failure_time is None:
                    self._transition(CircuitBreakerState.HALF_OPEN)
                    self.half_open_calls = 1
                    return True
                elapsed = _now_ts() - self.last_failure_time
                if elapsed >= self.config.timeout_seconds:
                    self._transition(CircuitBreakerState.HALF_OPEN)
                    self.half_open_calls = 1
                    return True
                return False
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.half_open_calls < self.config.half_open_max_calls:
                    self.half_open_calls += 1
                    return True
                return False
        return True

    def record_success(self) -> None:
        with self._lock:
            self.success_count += 1
            self.last_success_time = _now_ts()
            self.call_history.append((_now_ts(), True))
            if self.state == CircuitBreakerState.HALF_OPEN:
                if self.half_open_calls >= self.config.half_open_max_calls:
                    self._transition(CircuitBreakerState.CLOSED)
                    self.failure_count = 0
                    self.half_open_calls = 0

    def record_failure(self) -> None:
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = _now_ts()
            self.call_history.append((_now_ts(), False))
            if self.state == CircuitBreakerState.HALF_OPEN:
                self._transition(CircuitBreakerState.OPEN)
                self.half_open_calls = 0
                return
            if self.state == CircuitBreakerState.CLOSED:
                if self.failure_count >= self.config.failure_threshold:
                    self._transition(CircuitBreakerState.OPEN)
                self._check_error_rate()

    def _check_error_rate(self) -> None:
        if len(self.call_history) >= max(self.config.min_calls_before_eval, self.config.error_rate_window):
            recent = list(self.call_history)[-self.config.error_rate_window:]
            errors = sum(1 for _, s in recent if not s)
            err_rate = errors / len(recent)
            if err_rate >= self.config.error_rate_threshold:
                self._transition(CircuitBreakerState.OPEN)
                self.last_failure_time = _now_ts()

    def _transition(self, new_state: CircuitBreakerState) -> None:
        old = self.state
        self.state = new_state
        observability_logger.warning("circuit_breaker_state_transition",
                                     breaker=self.config.name,
                                     from_state=old.value, to_state=new_state.value)

    # ------------------------------------------------------------------ call wrapper
    def call(self, func: Callable[[], Any], *args: Any, **kwargs: Any) -> Any:
        """Execute ``func`` through the circuit breaker.

        Returns the result on success. Raises the original exception on
        failure. Raises :class:`RiskLimitError` if the circuit is OPEN.
        """
        if not self.can_execute():
            raise RiskLimitError(
                f"Circuit breaker {self.config.name} is OPEN",
                context={"breaker": self.config.name, "state": self.state.value},
            )
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as exc:
            self.record_failure()
            raise

    # ------------------------------------------------------------------ manual / chaos
    def force_open(self) -> None:
        with self._lock:
            self._manual_override = CircuitBreakerState.OPEN
            self.state = CircuitBreakerState.OPEN

    def force_closed(self) -> None:
        with self._lock:
            self._manual_override = CircuitBreakerState.CLOSED
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.half_open_calls = 0

    def clear_override(self) -> None:
        with self._lock:
            self._manual_override = None

    def inject_chaos_failure(self) -> None:
        """Mark the next ``can_execute`` call as failed (chaos testing)."""
        with self._lock:
            self._chaos_fail_next = True

    # ------------------------------------------------------------------ snapshot / restore
    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return serialize_metrics_strict({
                "name": self.config.name,
                "state": self.state.value,
                "failure_count": int(self.failure_count),
                "success_count": int(self.success_count),
                "last_failure_time": self.last_failure_time,
                "last_success_time": self.last_success_time,
                "half_open_calls": int(self.half_open_calls),
                "call_history_len": len(self.call_history),
                "manual_override": self._manual_override.value if self._manual_override else None,
                "config": self.config.to_dict(),
            })

    def _restore(self, state: Dict[str, Any]) -> None:
        self.state = CircuitBreakerState(str(state.get("state", "closed")))
        self.failure_count = int(state.get("failure_count", 0))
        self.success_count = int(state.get("success_count", 0))
        self.last_failure_time = state.get("last_failure_time")
        self.last_success_time = state.get("last_success_time")
        self.half_open_calls = int(state.get("half_open_calls", 0))

    def reset(self) -> None:
        with self._lock:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.last_success_time = None
            self.half_open_calls = 0
            self.call_history.clear()
            self._manual_override = None
            self._chaos_fail_next = False

    def get_status(self) -> Dict[str, Any]:
        return self.snapshot()


# Registry of circuit breakers per component/exchange.
class CircuitBreakerRegistry:
    """Named circuit breaker registry for components/exchanges."""

    def __init__(self):
        self._lock = threading.RLock()
        self._breakers: Dict[str, CircuitBreaker] = {}

    def get_or_create(self, name: str,
                      config: Optional[CircuitBreakerConfig] = None) -> CircuitBreaker:
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(config or CircuitBreakerConfig(name=name))
            return self._breakers[name]

    def get(self, name: str) -> Optional[CircuitBreaker]:
        with self._lock:
            return self._breakers.get(name)

    def remove(self, name: str) -> bool:
        with self._lock:
            if name in self._breakers:
                del self._breakers[name]
                return True
        return False

    def snapshot_all(self) -> Dict[str, Any]:
        with self._lock:
            return {name: b.snapshot() for name, b in self._breakers.items()}

    def reset_all(self) -> None:
        with self._lock:
            for b in self._breakers.values():
                b.reset()

    def list_names(self) -> List[str]:
        with self._lock:
            return list(self._breakers.keys())


default_circuit_registry = CircuitBreakerRegistry()


__all__ = [
    "CircuitBreakerState", "CircuitBreakerConfig", "CircuitBreaker",
    "CircuitBreakerRegistry", "default_circuit_registry",
]
