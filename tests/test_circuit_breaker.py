"""Adversarial tests for circuit breaker under orderflow/IV shocks."""

from __future__ import annotations

import json
import math
from datetime import datetime, timedelta, timezone

import pytest

from src.errors import RiskLimitError
from src.risk.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerState
from src.risk.limits import RiskLimits, RiskManager


def test_circuit_breaker_config_validation():
    with pytest.raises(RiskLimitError):
        CircuitBreakerConfig(failure_threshold=0)
    with pytest.raises(RiskLimitError):
        CircuitBreakerConfig(timeout_seconds=0)
    with pytest.raises(RiskLimitError):
        CircuitBreakerConfig(half_open_max_calls=0)
    with pytest.raises(RiskLimitError):
        CircuitBreakerConfig(error_rate_threshold=-0.1)
    with pytest.raises(RiskLimitError):
        CircuitBreakerConfig(error_rate_threshold=1.1)
    with pytest.raises(RiskLimitError):
        CircuitBreakerConfig(error_rate_window=0)


def test_circuit_breaker_basic_open_close_flow():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3, timeout_seconds=1, half_open_max_calls=2))
    assert cb.can_execute() is True
    assert cb.state == CircuitBreakerState.CLOSED
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitBreakerState.CLOSED
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    assert cb.can_execute() is False
    cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=5)
    assert cb.can_execute() is True
    assert cb.state == CircuitBreakerState.HALF_OPEN
    cb.can_execute()
    cb.can_execute()
    cb.record_success()
    cb.record_success()
    s = cb.snapshot()
    json.dumps(s, allow_nan=False)


def test_circuit_breaker_half_open_failure_reopens():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=1, timeout_seconds=1, half_open_max_calls=3))
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    assert cb.can_execute() is True
    assert cb.state == CircuitBreakerState.HALF_OPEN
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN


def test_circuit_breaker_error_rate_threshold_adversarial_orderflow_shock():
    cb = CircuitBreaker(CircuitBreakerConfig(error_rate_threshold=0.5, error_rate_window=10, failure_threshold=100))
    for i in range(9):
        cb.record_failure()
    cb.record_failure()  # 10th failure in window
    assert cb.state == CircuitBreakerState.OPEN


def test_circuit_breaker_error_rate_window_sliding():
    cb = CircuitBreaker(CircuitBreakerConfig(error_rate_threshold=0.4, error_rate_window=5, failure_threshold=1000))
    cb.record_success()
    cb.record_success()
    cb.record_success()
    cb.record_success()
    cb.record_success()
    assert cb.state == CircuitBreakerState.CLOSED
    cb.record_failure()
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN


def test_circuit_breaker_iv_shock_bursts_deterministic():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=2, timeout_seconds=60, half_open_max_calls=2, error_rate_threshold=0.8, error_rate_window=20))
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    assert cb.can_execute() is False
    cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=61)
    assert cb.can_execute() is True
    assert cb.state == CircuitBreakerState.HALF_OPEN
    cb.can_execute()
    cb.can_execute()
    cb.record_success()
    cb.record_success()
    assert cb.state == CircuitBreakerState.CLOSED


def test_circuit_breaker_persistence_across_shocks():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=3, timeout_seconds=5, half_open_max_calls=1))
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    cb.can_execute()
    assert cb.state == CircuitBreakerState.HALF_OPEN
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=10)
    cb.can_execute()
    assert cb.state == CircuitBreakerState.HALF_OPEN
    cb.record_success()
    assert cb.state in (CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN)


def test_circuit_breaker_snapshot_get_status_serialization_strict():
    cb = CircuitBreaker(CircuitBreakerConfig())
    cb.record_success()
    cb.record_failure()
    s = cb.snapshot()
    st = cb.get_status()
    json.dumps(s, allow_nan=False)
    json.dumps(st, allow_nan=False)
    assert isinstance(s["state"], str)
    assert isinstance(st["config"], dict)
    for k, v in st["config"].items():
        if isinstance(v, float):
            assert math.isfinite(v)


def test_circuit_breaker_reset_clears_all_state():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=1))
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    cb.reset()
    assert cb.state == CircuitBreakerState.CLOSED
    assert cb.failure_count == 0
    assert cb.success_count == 0
    assert cb.last_failure_time is None
    assert cb.half_open_calls == 0
    assert cb.call_history == []
    assert cb.can_execute() is True


def test_risk_manager_kill_switch_wired_with_circuit_breaker_under_shock():
    rm = RiskManager(RiskLimits(max_daily_loss=1000.0, max_drawdown_pct=0.1, max_drawdown_absolute=50000.0))
    rm.current_equity = 100000.0
    rm.peak_equity = 100000.0
    rm.daily_pnl = -1500.0
    triggered = rm.check_kill_switch()
    assert triggered is True
    assert rm.kill_switch_state.value == "triggered"
    violations = rm.check_order("BTC", "buy", 1.0, 50000.0, positions={})
    assert len(violations) > 0
    assert violations[0].violation_type == "kill_switch_active"
    json.dumps(violations[0].to_dict(), allow_nan=False)


def test_adversarial_combined_orderflow_iv_shock_stress():
    cb = CircuitBreaker(CircuitBreakerConfig(failure_threshold=4, timeout_seconds=2, half_open_max_calls=2, error_rate_threshold=0.6, error_rate_window=10))
    for _ in range(4):
        cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=3)
    cb.can_execute()
    cb.can_execute()
    cb.can_execute()
    cb.record_failure()
    assert cb.state == CircuitBreakerState.OPEN
    cb.last_failure_time = datetime.now(timezone.utc) - timedelta(seconds=5)
    cb.half_open_calls = 0
    cb.can_execute()
    cb.record_success()
    if cb.state == CircuitBreakerState.HALF_OPEN:
        cb.can_execute()
    cb.record_success()
    json.dumps(cb.snapshot(), allow_nan=False)
    json.dumps(cb.get_status(), allow_nan=False)


def test_circuit_breaker_no_nan_inf_propagation():
    cb = CircuitBreaker(CircuitBreakerConfig())
    cb.record_success()
    cb.record_failure()
    s = cb.snapshot()
    for k, v in s.items():
        if isinstance(v, float):
            assert math.isfinite(v)
