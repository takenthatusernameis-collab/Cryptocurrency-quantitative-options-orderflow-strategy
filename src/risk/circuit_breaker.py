"""Circuit breaker for trading halts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from math import isfinite
from typing import Any, Dict, Optional

from ..errors import RiskLimitError, get_logger
from ..telemetry import serialize_metrics_strict


_logger = get_logger(__name__)


class CircuitBreakerState(str, Enum):
    CLOSED = "closed"  # normal trading
    OPEN = "open"  # halted
    HALF_OPEN = "half_open"  # testing


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5
    timeout_seconds: int = 300
    half_open_max_calls: int = 3
    error_rate_threshold: float = 0.5
    error_rate_window: int = 100

    def __post_init__(self) -> None:
        if self.failure_threshold < 1:
            raise RiskLimitError("failure_threshold must be >= 1", context={"failure_threshold": self.failure_threshold})
        if self.timeout_seconds < 1:
            raise RiskLimitError("timeout_seconds must be >= 1", context={"timeout_seconds": self.timeout_seconds})
        if self.half_open_max_calls < 1:
            raise RiskLimitError("half_open_max_calls must be >= 1", context={"half_open_max_calls": self.half_open_max_calls})
        if not isfinite(self.error_rate_threshold) or self.error_rate_threshold < 0 or self.error_rate_threshold > 1:
            raise RiskLimitError("error_rate_threshold must be in [0,1]", context={"error_rate_threshold": self.error_rate_threshold})
        if self.error_rate_window < 1:
            raise RiskLimitError("error_rate_window must be >= 1", context={"error_rate_window": self.error_rate_window})


class CircuitBreaker:
    """Circuit breaker for protecting against cascading failures."""

    def __init__(self, config: Optional[CircuitBreakerConfig] = None):
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
        self.call_history: list = []  # (timestamp, success)

    def can_execute(self) -> bool:
        if self.state == CircuitBreakerState.CLOSED:
            return True
        if self.state == CircuitBreakerState.OPEN:
            if self.last_failure_time is None:
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                return True
            elapsed = (datetime.now(timezone.utc) - self.last_failure_time).total_seconds()
            if elapsed >= self.config.timeout_seconds:
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        if self.state == CircuitBreakerState.HALF_OPEN:
            if self.half_open_calls < self.config.half_open_max_calls:
                self.half_open_calls += 1
                return True
            return False
        return True

    def record_success(self) -> None:
        self.success_count += 1
        try:
            self.call_history.append((datetime.now(timezone.utc), True))
        except Exception:
            pass
        if self.state == CircuitBreakerState.HALF_OPEN:
            # If we get enough successes, close the breaker
            if self.half_open_calls >= self.config.half_open_max_calls:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
                self.half_open_calls = 0
        # Trim history
        if len(self.call_history) > self.config.error_rate_window * 2:
            self.call_history = self.call_history[-self.config.error_rate_window * 2:]

    def record_failure(self) -> None:
        self.failure_count += 1
        try:
            self.last_failure_time = datetime.now(timezone.utc)
        except Exception:
            self.last_failure_time = datetime.now(timezone.utc)
        try:
            self.call_history.append((datetime.now(timezone.utc), False))
        except Exception:
            pass
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Any failure in half-open reopens
            self.state = CircuitBreakerState.OPEN
            self.half_open_calls = 0
            return
        if self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitBreakerState.OPEN
                try:
                    _logger.warning("circuit_breaker_opened", failure_count=self.failure_count)
                except Exception:
                    pass
        # Check error rate
        if len(self.call_history) >= self.config.error_rate_window:
            try:
                recent = self.call_history[-self.config.error_rate_window:]
                errors = sum(1 for _, s in recent if not s)
                err_rate = errors / len(recent)
                if err_rate >= self.config.error_rate_threshold:
                    self.state = CircuitBreakerState.OPEN
                    try:
                        self.last_failure_time = datetime.now(timezone.utc)
                    except Exception:
                        pass
                    try:
                        _logger.warning("circuit_breaker_opened_error_rate", error_rate=err_rate)
                    except Exception:
                        pass
            except Exception:
                pass
        if len(self.call_history) > self.config.error_rate_window * 2:
            self.call_history = self.call_history[-self.config.error_rate_window * 2:]

    def reset(self) -> None:
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.half_open_calls = 0
        self.call_history = []

    def snapshot(self) -> Dict[str, Any]:
        """Return a deep-copyable, serialization-safe snapshot of current state.

        Used by stress-test harnesses to assert state transitions and to
        record deterministic checkpoints without exposing internal mutable
        references.
        """
        try:
            fc = int(self.failure_count) if isfinite(float(self.failure_count)) else 0
        except Exception:
            fc = 0
        try:
            sc = int(self.success_count) if isfinite(float(self.success_count)) else 0
        except Exception:
            sc = 0
        try:
            hoc = int(self.half_open_calls) if isfinite(float(self.half_open_calls)) else 0
        except Exception:
            hoc = 0
        try:
            chlen = int(len(self.call_history))
        except Exception:
            chlen = 0
        lft = None
        try:
            if self.last_failure_time is not None:
                lft = self.last_failure_time.isoformat()
        except Exception:
            lft = None
        return serialize_metrics_strict({
            "state": str(getattr(self.state, "value", self.state)),
            "failure_count": fc,
            "success_count": sc,
            "last_failure_time": lft,
            "half_open_calls": hoc,
            "call_history_len": chlen,
        })

    def get_status(self) -> Dict[str, Any]:
        try:
            fc = int(self.failure_count) if isfinite(float(self.failure_count)) else 0
        except Exception:
            fc = 0
        try:
            sc = int(self.success_count) if isfinite(float(self.success_count)) else 0
        except Exception:
            sc = 0
        try:
            hoc = int(self.half_open_calls) if isfinite(float(self.half_open_calls)) else 0
        except Exception:
            hoc = 0
        lft = None
        try:
            if self.last_failure_time is not None:
                lft = self.last_failure_time.isoformat()
        except Exception:
            lft = None
        try:
            ert = float(self.config.error_rate_threshold)
            if not isfinite(ert):
                ert = 0.5
        except Exception:
            ert = 0.5
        return serialize_metrics_strict({
            "state": str(getattr(self.state, "value", self.state)),
            "failure_count": fc,
            "success_count": sc,
            "last_failure_time": lft,
            "half_open_calls": hoc,
            "config": {
                "failure_threshold": int(self.config.failure_threshold),
                "timeout_seconds": int(self.config.timeout_seconds),
                "half_open_max_calls": int(self.config.half_open_max_calls),
                "error_rate_threshold": ert,
            },
        })
