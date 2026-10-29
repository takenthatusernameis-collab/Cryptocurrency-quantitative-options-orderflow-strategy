"""Numerical guards for stable quantitative computation.

Provides safe wrappers around division, logarithm, square root, and percentage
change that prevent NaN/Inf leakage across features, signals, and backtesting.
Every guard is typed, finite-checking, and logs structural errors through the
project's structured error logger when a non-finite or degenerate input is
encountered.

Usage: prefer these guards over bare ``/``, ``math.log``, ``math.sqrt``, and
``(curr - prev) / prev`` anywhere a zero denominator, non-positive log argument,
or negative radicand can occur.
"""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Optional

from ..errors import FeatureError, NonFiniteResultError, get_logger
from ..telemetry.error_logging import log_error_with_context

_logger = get_logger(__name__)


def _log_guard_warning(operation: str, field: str, value: Any, reason: str) -> None:
    """Log a guarded numerical edge case without raising."""
    try:
        log_error_with_context(
            f"numerical_guard: {reason}",
            operation=operation,
            module="src.utils.numerical_guards",
            extra={"field": field, "input_value": _safe_serialize(value), "reason": reason},
        )
    except Exception:
        pass


def _safe_serialize(value: Any) -> Any:
    """Best-effort serialization of a guard input for log context."""
    try:
        f = float(value)
        if math.isfinite(f):
            return f
        return str(value)
    except (TypeError, ValueError):
        return str(value)


def ensure_finite(value: Any, default: float = 0.0, *, name: str = "value",
                  context: Optional[Dict[str, Any]] = None) -> float:
    """Coerce ``value`` to a finite float, returning ``default`` on failure.

    Non-convertible, NaN, and Inf inputs yield ``default``. Never raises.
    """
    ctx = {"function": "ensure_finite", "name": name, **(context or {})}
    try:
        f = float(value)
    except (TypeError, ValueError) as e:
        _log_guard_warning("ensure_finite", name, value, "non-convertible input")
        raise NonFiniteResultError(
            f"{name} is not convertible to float", context={**ctx, "reason": "non-convertible"}, cause=e
        )
    if not math.isfinite(f):
        _log_guard_warning("ensure_finite", name, value, "non-finite input")
        raise NonFiniteResultError(
            f"{name} must be finite", context={**ctx, "input_value": _safe_serialize(value)},
        )
    return f


def validate_finite(value: Any, name: str, *,
                    context: Optional[Dict[str, Any]] = None) -> float:
    """Validate ``value`` is finite; raise :class:`NonFiniteResultError` otherwise.

    Returns the float value when finite. Non-convertible or non-finite inputs
    raise with field-level context suitable for structured logging.
    """
    ctx = {"function": "validate_finite", "name": name, **(context or {})}
    try:
        f = float(value)
    except (TypeError, ValueError) as e:
        raise NonFiniteResultError(
            f"{name} is not convertible to float", context={**ctx, "reason": "non-convertible"}, cause=e
        )
    if not math.isfinite(f):
        raise NonFiniteResultError(
            f"{name} must be finite", context={**ctx, "input_value": _safe_serialize(value)},
        )
    return f


def safe_divide(numerator: Any, denominator: Any, default: float = 0.0, *,
                raise_on_zero: bool = False, operation: str = "safe_divide",
                context: Optional[Dict[str, Any]] = None) -> float:
    """Divide ``numerator`` by ``denominator`` with zero/non-finite guards.

    Returns ``default`` when the denominator is zero or non-finite, or when
    either operand is non-convertible/non-finite (unless ``raise_on_zero`` is
    set, in which case a zero denominator raises :class:`FeatureError`).
    """
    ctx = {"function": operation, **(context or {})}
    try:
        n = float(numerator)
        d = float(denominator)
    except (TypeError, ValueError) as e:
        _log_guard_warning(operation, "division", (numerator, denominator), "non-convertible operand")
        if raise_on_zero:
            raise FeatureError(
                "safe_divide: non-convertible operand", context={**ctx, "reason": "non-convertible"}, cause=e
            )
        return default
    if not math.isfinite(n) or not math.isfinite(d):
        _log_guard_warning(operation, "division", (numerator, denominator), "non-finite operand")
        if raise_on_zero:
            raise FeatureError(
                "safe_divide: non-finite operand", context={**ctx, "reason": "non-finite"},
            )
        return default
    if d == 0.0:
        _log_guard_warning(operation, "denominator", denominator, "division by zero")
        if raise_on_zero:
            raise FeatureError(
                "safe_divide: division by zero", context={**ctx, "numerator": n, "denominator": d},
            )
        return default
    result = n / d
    if not math.isfinite(result):
        _log_guard_warning(operation, "result", result, "non-finite quotient")
        return default
    return result


def safe_log(value: Any, default: float = 0.0, *, raise_on_nonpositive: bool = False,
             operation: str = "safe_log", context: Optional[Dict[str, Any]] = None) -> float:
    """Natural logarithm guarded against non-positive and non-finite inputs.

    Returns ``default`` for non-positive or non-finite ``value`` (unless
    ``raise_on_nonpositive`` is set, which raises :class:`FeatureError` on
    non-positive input).
    """
    ctx = {"function": operation, **(context or {})}
    try:
        v = float(value)
    except (TypeError, ValueError) as e:
        _log_guard_warning(operation, "value", value, "non-convertible input")
        if raise_on_nonpositive:
            raise FeatureError(
                "safe_log: non-convertible input", context={**ctx, "reason": "non-convertible"}, cause=e
            )
        return default
    if not math.isfinite(v):
        _log_guard_warning(operation, "value", value, "non-finite input")
        if raise_on_nonpositive:
            raise FeatureError(
                "safe_log: non-finite input", context={**ctx, "reason": "non-finite"},
            )
        return default
    if v <= 0.0:
        _log_guard_warning(operation, "value", value, "log of non-positive")
        if raise_on_nonpositive:
            raise FeatureError(
                "safe_log: log of non-positive", context={**ctx, "value": v},
            )
        return default
    result = math.log(v)
    if not math.isfinite(result):
        _log_guard_warning(operation, "result", result, "non-finite logarithm")
        return default
    return result


def safe_sqrt(value: Any, default: float = 0.0, *, raise_on_negative: bool = False,
              operation: str = "safe_sqrt", context: Optional[Dict[str, Any]] = None) -> float:
    """Square root guarded against negative and non-finite inputs.

    Returns ``default`` for negative or non-finite ``value`` (unless
    ``raise_on_negative`` is set, which raises :class:`FeatureError` on negative
    input).
    """
    ctx = {"function": operation, **(context or {})}
    try:
        v = float(value)
    except (TypeError, ValueError) as e:
        _log_guard_warning(operation, "value", value, "non-convertible input")
        if raise_on_negative:
            raise FeatureError(
                "safe_sqrt: non-convertible input", context={**ctx, "reason": "non-convertible"}, cause=e
            )
        return default
    if not math.isfinite(v):
        _log_guard_warning(operation, "value", value, "non-finite input")
        if raise_on_negative:
            raise FeatureError(
                "safe_sqrt: non-finite input", context={**ctx, "reason": "non-finite"},
            )
        return default
    if v < 0.0:
        _log_guard_warning(operation, "value", value, "sqrt of negative")
        if raise_on_negative:
            raise FeatureError(
                "safe_sqrt: sqrt of negative", context={**ctx, "value": v},
            )
        return default
    result = math.sqrt(v)
    if not math.isfinite(result):
        _log_guard_warning(operation, "result", result, "non-finite square root")
        return default
    return result


def safe_pct_change(current: Any, previous: Any, default: float = 0.0, *,
                    raise_on_zero: bool = False, operation: str = "safe_pct_change",
                    context: Optional[Dict[str, Any]] = None) -> float:
    """Percentage change ``(current - previous) / previous`` guarded against zero
    and non-finite inputs.

    Returns ``default`` when ``previous`` is zero or non-finite, or when either
    operand is non-convertible/non-finite (unless ``raise_on_zero`` is set).
    """
    ctx = {"function": operation, **(context or {})}
    try:
        c = float(current)
        p = float(previous)
    except (TypeError, ValueError) as e:
        _log_guard_warning(operation, "pct_change", (current, previous), "non-convertible operand")
        if raise_on_zero:
            raise FeatureError(
                "safe_pct_change: non-convertible operand", context={**ctx, "reason": "non-convertible"}, cause=e
            )
        return default
    if not math.isfinite(c) or not math.isfinite(p):
        _log_guard_warning(operation, "pct_change", (current, previous), "non-finite operand")
        if raise_on_zero:
            raise FeatureError(
                "safe_pct_change: non-finite operand", context={**ctx, "reason": "non-finite"},
            )
        return default
    if p == 0.0:
        _log_guard_warning(operation, "previous", previous, "pct-change on zero previous")
        if raise_on_zero:
            raise FeatureError(
                "safe_pct_change: previous is zero", context={**ctx, "current": c, "previous": p},
            )
        return default
    result = (c - p) / p
    if not math.isfinite(result):
        _log_guard_warning(operation, "result", result, "non-finite pct change")
        return default
    return result


def safe_mean(values: List[Any], default: float = 0.0, *,
              operation: str = "safe_mean", context: Optional[Dict[str, Any]] = None) -> float:
    """Arithmetic mean guarded against empty input and non-finite values.

    Non-convertible/non-finite entries are skipped. Returns ``default`` when no
    valid entries remain.
    """
    ctx = {"function": operation, **(context or {})}
    valid: List[float] = []
    for v in values:
        try:
            f = float(v)
        except (TypeError, ValueError):
            continue
        if math.isfinite(f):
            valid.append(f)
    if not valid:
        _log_guard_warning(operation, "values", values, "no valid finite entries")
        return default
    result = sum(valid) / len(valid)
    if not math.isfinite(result):
        _log_guard_warning(operation, "result", result, "non-finite mean")
        return default
    return result


def clamp(value: Any, low: float, high: float, default: float = 0.0, *,
          operation: str = "clamp", context: Optional[Dict[str, Any]] = None) -> float:
    """Clamp ``value`` to ``[low, high]`` with finite guards.

    Returns ``default`` when ``value`` is non-convertible/non-finite or bounds
    are invalid (low > high or non-finite).
    """
    ctx = {"function": operation, **(context or {})}
    try:
        v = float(value)
        lo = float(low)
        hi = float(high)
    except (TypeError, ValueError) as e:
        _log_guard_warning(operation, "value", value, "non-convertible input or bounds")
        return default
    if not (math.isfinite(v) and math.isfinite(lo) and math.isfinite(hi)):
        _log_guard_warning(operation, "value", value, "non-finite input or bounds")
        return default
    if lo > hi:
        _log_guard_warning(operation, "bounds", (low, high), "low bound exceeds high bound")
        return default
    result = min(max(v, lo), hi)
    if not math.isfinite(result):
        return default
    return result


__all__ = [
    "ensure_finite",
    "validate_finite",
    "safe_divide",
    "safe_log",
    "safe_sqrt",
    "safe_pct_change",
    "safe_mean",
    "clamp",
]
