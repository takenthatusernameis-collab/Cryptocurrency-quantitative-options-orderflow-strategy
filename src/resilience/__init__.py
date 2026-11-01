"""Resilience package: circuit breakers, retry, bulkhead, timeout, hedged requests, auto-healing."""

from .circuit import (
    CircuitBreaker, CircuitBreakerConfig, CircuitBreakerRegistry,
    CircuitBreakerState, default_circuit_registry,
)
from .retry import (
    Bulkhead, BulkheadConfig, DegradationConfig, GracefulDegradation,
    HedgedRequestResult, RetryConfig, RetryPolicy, RetryResult,
    TimeoutConfig, call_with_timeout, default_bulkheads, default_retry_policy,
    get_bulkhead, hedged_request,
)
from .auto_healer import (
    AutoHealer, HealAction, HealRecord, HealPolicy, ComponentHealth,
)

__all__ = [
    "CircuitBreaker", "CircuitBreakerConfig", "CircuitBreakerRegistry",
    "CircuitBreakerState", "default_circuit_registry",
    "Bulkhead", "BulkheadConfig", "DegradationConfig", "GracefulDegradation",
    "HedgedRequestResult", "RetryConfig", "RetryPolicy", "RetryResult",
    "TimeoutConfig", "call_with_timeout", "default_bulkheads", "default_retry_policy",
    "get_bulkhead", "hedged_request",
    "AutoHealer", "HealAction", "HealRecord", "HealPolicy", "ComponentHealth",
]
