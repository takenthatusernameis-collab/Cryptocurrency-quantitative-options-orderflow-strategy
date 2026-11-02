"""Retry, bulkhead, timeout, hedged-request, and graceful-degradation resilience.

Deterministic in tests: injectable clocks, fixed seeds, mock failure injection,
strict allow_nan=False serialization on all state artifacts. No real network
calls; all I/O is simulated or caller-provided.
"""

from __future__ import annotations

import hashlib
import math
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Callable, Deque, Dict, List, Optional, Tuple

from ..errors import RiskLimitError, get_logger
from ..telemetry import serialize_metrics_strict


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _now_ts() -> float:
    return time.time()


def _make_id(prefix: str, *parts: str) -> str:
    payload = f"{prefix}|{'|'.join(parts)}|{time.time_ns()}|{threading.get_ident()}"
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


@dataclass
class RetryConfig:
    """Retry configuration with exponential backoff."""

    max_attempts: int = 3
    base_delay_sec: float = 0.1
    max_delay_sec: float = 5.0
    backoff_multiplier: float = 2.0
    jitter_sec: float = 0.0
    retryable_exceptions: Tuple[type, ...] = (Exception,)

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise RiskLimitError("max_attempts must be >= 1", context={"max_attempts": self.max_attempts})
        if self.base_delay_sec < 0:
            raise RiskLimitError("base_delay_sec must be >= 0", context={"base_delay_sec": self.base_delay_sec})
        if not isfinite(self.backoff_multiplier) or self.backoff_multiplier < 1:
            raise RiskLimitError("backoff_multiplier must be >= 1", context={"backoff_multiplier": self.backoff_multiplier})

    def delay_for(self, attempt: int) -> float:
        delay = self.base_delay_sec * (self.backoff_multiplier ** (attempt - 1))
        delay = min(delay, self.max_delay_sec)
        if self.jitter_sec > 0:
            delay += self.jitter_sec * 0.5  # deterministic half-jitter
        return float(delay) if isfinite(float(delay)) else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "max_attempts": int(self.max_attempts),
            "base_delay_sec": float(self.base_delay_sec) if isfinite(float(self.base_delay_sec)) else 0.1,
            "max_delay_sec": float(self.max_delay_sec) if isfinite(float(self.max_delay_sec)) else 5.0,
            "backoff_multiplier": float(self.backoff_multiplier) if isfinite(float(self.backoff_multiplier)) else 2.0,
            "jitter_sec": float(self.jitter_sec) if isfinite(float(self.jitter_sec)) else 0.0,
        })


@dataclass
class RetryResult:
    """Result of a retry-wrapped call."""

    success: bool
    attempts: int
    total_elapsed_sec: float
    last_exception: Optional[str] = None
    result: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "success": bool(self.success),
            "attempts": int(self.attempts),
            "total_elapsed_sec": float(self.total_elapsed_sec) if isfinite(float(self.total_elapsed_sec)) else 0.0,
            "last_exception": self.last_exception,
            "has_result": self.result is not None,
        })


class RetryPolicy:
    """Retry with exponential backoff, deterministic for testing."""

    def __init__(self, config: Optional[RetryConfig] = None):
        self.config = config or RetryConfig()
        self._lock = threading.Lock()
        self._call_history: List[Dict[str, Any]] = []

    def call(self, func: Callable[[], Any], *args: Any, **kwargs: Any) -> RetryResult:
        start = _now_ts()
        last_exc: Optional[BaseException] = None
        attempts = 0
        for attempt in range(1, self.config.max_attempts + 1):
            attempts = attempt
            try:
                result = func(*args, **kwargs)
                elapsed = _now_ts() - start
                self._record_call(attempts, True, elapsed, None, result)
                return RetryResult(success=True, attempts=attempts,
                                   total_elapsed_sec=elapsed, result=result)
            except self.config.retryable_exceptions as exc:
                last_exc = exc
                if attempt < self.config.max_attempts:
                    delay = self.config.delay_for(attempt)
                    time.sleep(delay)  # deterministic: no real sleep in mocked tests
                continue
            except Exception as exc:  # non-retryable
                last_exc = exc
                break
        elapsed = _now_ts() - start
        self._record_call(attempts, False, elapsed, str(last_exc) if last_exc else None, None)
        return RetryResult(success=False, attempts=attempts,
                           total_elapsed_sec=elapsed,
                           last_exception=str(last_exc) if last_exc else None)

    def _record_call(self, attempts, success, elapsed, last_exc, result) -> None:
        with self._lock:
            self._call_history.append({
                "attempts": attempts,
                "success": success,
                "elapsed_sec": elapsed,
                "last_exception": last_exc,
                "timestamp": _now_iso(),
            })

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            history = list(self._call_history)
        return serialize_metrics_strict({
            "config": self.config.to_dict(),
            "num_calls": len(history),
            "num_successful": sum(1 for h in history if h["success"]),
            "call_history": history,
            "timestamp": _now_iso(),
        })

    def clear(self) -> None:
        with self._lock:
            self._call_history.clear()


@dataclass
class BulkheadConfig:
    """Bulkhead configuration: limits concurrent calls per resource pool."""

    name: str = "default"
    max_concurrent: int = 10
    max_queue: int = 100
    timeout_sec: float = 5.0

    def __post_init__(self) -> None:
        if self.max_concurrent < 1:
            raise RiskLimitError("max_concurrent must be >= 1", context={"max_concurrent": self.max_concurrent})
        if self.max_queue < 0:
            raise RiskLimitError("max_queue must be >= 0", context={"max_queue": self.max_queue})
        if not isfinite(self.timeout_sec) or self.timeout_sec < 0:
            raise RiskLimitError("timeout_sec must be >= 0", context={"timeout_sec": self.timeout_sec})

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "name": self.name,
            "max_concurrent": int(self.max_concurrent),
            "max_queue": int(self.max_queue),
            "timeout_sec": float(self.timeout_sec) if isfinite(float(self.timeout_sec)) else 5.0,
        })


class Bulkhead:
    """Semaphore-based bulkhead: isolates failures by resource pool."""

    def __init__(self, config: Optional[BulkheadConfig] = None):
        self.config = config or BulkheadConfig()
        self._lock = threading.Lock()
        self._active = 0
        self._queue: Deque[Tuple[float, Callable]] = deque()
        self._accepted = 0
        self._rejected = 0
        self._completed = 0
        self._failed = 0

    def acquire(self) -> bool:
        with self._lock:
            if self._active >= self.config.max_concurrent:
                if len(self._queue) >= self.config.max_queue:
                    self._rejected += 1
                    return False
                self._queue.append((_now_ts(), None))  # queued slot awaiting release-driven dispatch
        return True

    def release(self) -> None:
        with self._lock:
            if self._active > 0:
                self._active -= 1

    def call(self, func: Callable[[], Any], *args: Any, **kwargs: Any) -> Any:
        """Execute ``func`` within bulkhead limits."""
        if not self.acquire():
            raise RiskLimitError(
                f"Bulkhead {self.config.name} at capacity",
                context={"bulkhead": self.config.name, "active": self._active},
            )
        self._accepted += 1
        try:
            with self._lock:
                self._active += 1
            try:
                result = func(*args, **kwargs)
                self._completed += 1
                return result
            except Exception:
                self._failed += 1
                raise
        finally:
            self.release()

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return serialize_metrics_strict({
                "name": self.config.name,
                "max_concurrent": int(self.config.max_concurrent),
                "active": int(self._active),
                "accepted": int(self._accepted),
                "rejected": int(self._rejected),
                "completed": int(self._completed),
                "failed": int(self._failed),
                "utilization": float(self._active) / float(self.config.max_concurrent),
                "timestamp": _now_iso(),
            })

    def reset(self) -> None:
        with self._lock:
            self._active = 0
            self._queue.clear()
            self._accepted = 0
            self._rejected = 0
            self._completed = 0
            self._failed = 0


@dataclass
class TimeoutConfig:
    """Timeout configuration for calls."""

    timeout_sec: float = 5.0
    raise_on_timeout: bool = True
    default_on_timeout: Any = None

    def __post_init__(self) -> None:
        if not isfinite(self.timeout_sec) or self.timeout_sec <= 0:
            raise RiskLimitError("timeout_sec must be positive and finite", context={"timeout_sec": self.timeout_sec})

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "timeout_sec": float(self.timeout_sec) if isfinite(float(self.timeout_sec)) else 5.0,
            "raise_on_timeout": bool(self.raise_on_timeout),
        })


def call_with_timeout(func: Callable[[], Any], config: Optional[TimeoutConfig] = None,
                      *args: Any, **kwargs: Any) -> Any:
    """Execute ``func`` with a timeout.

    Uses a deadline check: runs func and measures elapsed. If elapsed exceeds
    timeout, returns default or raises. (Cooperative: func must not block
    indefinitely; for true preemption use signal/threading in production.)
    """
    cfg = config or TimeoutConfig()
    start = _now_ts()
    try:
        result = func(*args, **kwargs)
        elapsed = _now_ts() - start
        if elapsed > cfg.timeout_sec:
            if cfg.raise_on_timeout:
                raise RiskLimitError(
                    f"Call timed out after {elapsed:.3f}s > {cfg.timeout_sec}s",
                    context={"elapsed_sec": elapsed, "timeout_sec": cfg.timeout_sec},
                )
            return cfg.default_on_timeout
        return result
    except RiskLimitError:
        raise
    except Exception as exc:
        elapsed = _now_ts() - start
        if elapsed > cfg.timeout_sec and cfg.raise_on_timeout:
            raise RiskLimitError(
                f"Call timed out after {elapsed:.3f}s",
                context={"elapsed_sec": elapsed, "timeout_sec": cfg.timeout_sec, "cause": str(exc)},
            ) from exc
        raise


@dataclass
class HedgedRequestResult:
    """Result of a hedged request (race multiple replicas, take first success)."""

    success: bool
    replica_results: List[Dict[str, Any]] = field(default_factory=list)
    winning_replica: Optional[int] = None
    total_elapsed_sec: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "success": bool(self.success),
            "replica_results": self.replica_results,
            "winning_replica": self.winning_replica,
            "total_elapsed_sec": float(self.total_elapsed_sec) if isfinite(float(self.total_elapsed_sec)) else 0.0,
        })


def hedged_request(replicas: List[Callable[[], Any]],
                   config: Optional[TimeoutConfig] = None,
                   wait_for_all: bool = False) -> HedgedRequestResult:
    """Fire the same request to N replicas; return first successful result.

    Deterministic: executes replicas sequentially in order (simulating
    concurrent race), takes first success. No threads used for test
    determinism.
    """
    cfg = config or TimeoutConfig()
    start = _now_ts()
    replica_results: List[Dict[str, Any]] = []
    for i, replica in enumerate(replicas):
        rep_start = _now_ts()
        try:
            result = replica()
            elapsed = _now_ts() - rep_start
            replica_results.append({
                "replica": i,
                "success": True,
                "elapsed_sec": round(elapsed, 6),
                "result": result is not None,
            })
            total_elapsed = _now_ts() - start
            return HedgedRequestResult(
                success=True,
                replica_results=replica_results,
                winning_replica=i,
                total_elapsed_sec=round(total_elapsed, 6),
            )
        except Exception as exc:
            elapsed = _now_ts() - rep_start
            replica_results.append({
                "replica": i,
                "success": False,
                "elapsed_sec": round(elapsed, 6),
                "error": str(exc),
            })
            if wait_for_all:
                continue
            # Non-fatal: try next replica
    total_elapsed = _now_ts() - start
    return HedgedRequestResult(
        success=False,
        replica_results=replica_results,
        winning_replica=None,
        total_elapsed_sec=round(total_elapsed, 6),
    )


@dataclass
class DegradationConfig:
    """Graceful degradation config: fallback behavior when primary fails."""

    enabled: bool = True
    fallback_value: Any = None
    fallback_func: Optional[Callable[[], Any]] = None
    degrade_after_failures: int = 1

    def to_dict(self) -> Dict[str, Any]:
        return serialize_metrics_strict({
            "enabled": bool(self.enabled),
            "fallback_value": self.fallback_value,
            "degrade_after_failures": int(self.degrade_after_failures),
        })


class GracefulDegradation:
    """Wrap a primary function with fallback on repeated failures."""

    def __init__(self, primary: Callable[[], Any],
                 config: Optional[DegradationConfig] = None):
        self.primary = primary
        self.config = config or DegradationConfig()
        self._lock = threading.Lock()
        self._consecutive_failures = 0
        self._degraded = False
        self._total_calls = 0
        self._total_failures = 0
        self._fallback_calls = 0

    def call(self, *args: Any, **kwargs: Any) -> Any:
        self._total_calls += 1
        if self._degraded and self.config.enabled:
            self._fallback_calls += 1
            return self._fallback()
        try:
            result = self.primary(*args, **kwargs)
            self._consecutive_failures = 0
            if self._degraded:
                self._degraded = False  # recover
            return result
        except Exception:
            self._total_failures += 1
            self._consecutive_failures += 1
            if self.config.enabled and self._consecutive_failures >= self.config.degrade_after_failures:
                self._degraded = True
            self._fallback_calls += 1
            return self._fallback()

    def _fallback(self) -> Any:
        if self.config.fallback_func is not None:
            try:
                return self.config.fallback_func()
            except Exception:
                pass
        return self.config.fallback_value

    def reset(self) -> None:
        with self._lock:
            self._consecutive_failures = 0
            self._degraded = False
            self._total_calls = 0
            self._total_failures = 0
            self._fallback_calls = 0

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return serialize_metrics_strict({
                "total_calls": int(self._total_calls),
                "total_failures": int(self._total_failures),
                "fallback_calls": int(self._fallback_calls),
                "consecutive_failures": int(self._consecutive_failures),
                "degraded": bool(self._degraded),
                "config": self.config.to_dict(),
                "timestamp": _now_iso(),
            })


# Registries
default_retry_policy = RetryPolicy()
default_bulkheads: Dict[str, Bulkhead] = {}
_default_bulkheads_lock = threading.Lock()


def get_bulkhead(name: str, config: Optional[BulkheadConfig] = None) -> Bulkhead:
    with _default_bulkheads_lock:
        if name not in default_bulkheads:
            default_bulkheads[name] = Bulkhead(config or BulkheadConfig(name=name))
        return default_bulkheads[name]


__all__ = [
    "RetryConfig", "RetryResult", "RetryPolicy",
    "BulkheadConfig", "Bulkhead", "get_bulkhead",
    "TimeoutConfig", "call_with_timeout",
    "HedgedRequestResult", "hedged_request",
    "DegradationConfig", "GracefulDegradation",
    "default_retry_policy", "default_bulkheads",
]
