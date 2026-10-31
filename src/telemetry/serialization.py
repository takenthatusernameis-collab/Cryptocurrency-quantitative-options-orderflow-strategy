"""Serialization guardrails for strategy metrics.

All aggregate results (backtest metrics, signal payloads, pipeline outputs) must
pass through :func:`serialize_metrics` before JSON emission. The function enforces
``allow_nan=False`` semantics by raising :class:`SerializationError` on any
non-finite value, and provides a non-strict variant that sanitizes in place.
"""

from __future__ import annotations

import json
import math
from typing import Any, Dict, List, Mapping, Optional, Tuple, Union

from ..errors import SerializationError, get_logger

_logger = get_logger(__name__)

# Numeric types we consider "metric-like" for serialization purposes.
_FiniteFloat = float
_NumpyFloatLike = Any  # numpy scalars duck-typed via float()/isnan


def _is_nonfinite(value: Any) -> bool:
    """Return True if ``value`` is a non-finite float (NaN or Inf)."""
    try:
        # Check for numpy scalars
        if hasattr(value, 'dtype') and hasattr(value, 'item'):
            try:
                f = float(value.item())
            except Exception:
                try:
                    f = float(value)
                except Exception:
                    return False
        else:
            f = float(value)
    except (TypeError, ValueError):
        return False
    return not math.isfinite(f)


def _sanitize_value(value: Any) -> Any:
    """Recursively replace non-finite floats with ``None``.

    Dicts, lists/tuples, and nested containers are traversed. Non-numeric types
    are returned unchanged. This is the non-strict path used when callers prefer
    a best-effort payload over an exception.
    """
    if isinstance(value, Mapping):
        return {k: _sanitize_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        sanitized = [_sanitize_value(v) for v in value]
        # Preserve tuple-ness for callers that rely on it.
        if isinstance(value, tuple):
            return tuple(sanitized)
        return sanitized
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        return value
    if isinstance(value, (int, bool)) or value is None:
        return value
    # Numpy float scalars (float64, etc.) are not isinstance float, so handle them
    # via duck-typing: try float() and check finiteness.
    try:
        # Handle numpy scalars
        if hasattr(value, 'dtype'):
            try:
                f = float(value)
            except Exception:
                return value
            # Avoid treating ints as floats
            if isinstance(value, (int, bool)) or value is None:
                return value
            if not math.isfinite(f):
                return None
            # Keep as python float for JSON serialization cleanliness
            return f
        f = float(value)
    except (TypeError, ValueError):
        return value
    # Only treat as numeric if the original was not a bool/str/etc.
    if isinstance(value, (str, bytes, bool)) or value is None:
        return value
    if not math.isfinite(f):
        return None
    return f


def sanitize_for_json(obj: Any) -> Any:
    """Sanitize ``obj`` so it is JSON-serializable with ``allow_nan=False``.

    Non-finite floats become ``None``. Returns a new object; the input is not
    mutated. Best-effort: never raises.
    """
    return _sanitize_value(obj)


def _collect_nonfinite_paths(
    value: Any, path: str = "$"
) -> List[str]:
    """Walk ``value`` and return JSON-pointer-like paths to non-finite floats."""
    bad: List[str] = []
    if isinstance(value, Mapping):
        for k, v in value.items():
            bad.extend(_collect_nonfinite_paths(v, f"{path}/{k}"))
    elif isinstance(value, (list, tuple)):
        for i, v in enumerate(value):
            bad.extend(_collect_nonfinite_paths(v, f"{path}[{i}]"))
    elif isinstance(value, float):
        if not math.isfinite(value):
            bad.append(path)
        return bad
    elif isinstance(value, (int, bool)) or value is None:
        return bad
    else:
        # Check for numpy/scalar floats
        if hasattr(value, 'dtype'):
            try:
                f = float(value)
                if not math.isfinite(f):
                    bad.append(path)
                return bad
            except Exception:
                pass
        try:
            f = float(value)
        except (TypeError, ValueError):
            return bad
        if isinstance(value, (str, bytes, bool)) or value is None:
            return bad
        if not math.isfinite(f):
            bad.append(path)
    return bad


def serialize_metrics(metrics: Mapping[str, Any]) -> Dict[str, Any]:
    """Serialize metrics dict, raising :class:`SerializationError` on non-finite values.

    This is the strict path: any NaN/Inf anywhere in the structure (including
    nested dicts/lists) triggers an error with the offending JSON-pointer paths
    in the context. Use :func:`serialize_metrics_strict` for the same behavior
    with an explicit ``allow_nan=False`` JSON round-trip check.
    """
    if metrics is None:
        return {}
    if not isinstance(metrics, Mapping):
        raise SerializationError(
            "metrics must be a mapping",
            context={"operation": "serialize_metrics", "type": type(metrics).__name__},
        )
    bad_paths = _collect_nonfinite_paths(metrics)
    if bad_paths:
        raise SerializationError(
            "Non-finite values detected in metrics; refusing to serialize with allow_nan=False",
            context={
                "operation": "serialize_metrics",
                "nonfinite_paths": bad_paths,
                "allow_nan": False,
            },
        )
    # Deep-copy through JSON round-trip to normalize numpy types and ensure a plain dict.
    try:
        return dict(json.loads(json.dumps(dict(metrics), default=str)))  # type: ignore[no-any-return]
    except (TypeError, ValueError) as e:
        raise SerializationError(
            "Failed to JSON-round-trip metrics",
            context={"operation": "serialize_metrics"},
            cause=e,
        )


def serialize_metrics_strict(metrics: Mapping[str, Any]) -> Dict[str, Any]:
    """Strict serialization that also verifies JSON emission with ``allow_nan=False``.

    Behaves like :func:`serialize_metrics` but additionally performs
    ``json.dumps(..., allow_nan=False)`` to guarantee the result is strictly
    JSON-valid. Raises :class:`SerializationError` on any failure.
    """
    sanitized = serialize_metrics(metrics)
    try:
        json.dumps(sanitized, allow_nan=False)
    except (ValueError, OverflowError) as e:
        raise SerializationError(
            "Serialized metrics are not JSON-valid with allow_nan=False",
            context={"operation": "serialize_metrics_strict"},
            cause=e,
        )
    return sanitized


def assert_json_valid(obj: Any) -> None:
    """Raise :class:`SerializationError` if ``obj`` cannot be serialized with ``allow_nan=False``."""
    try:
        json.dumps(obj, allow_nan=False)
    except (ValueError, OverflowError) as e:
        raise SerializationError(
            "Object is not JSON-serializable with allow_nan=False",
            context={"operation": "assert_json_valid"},
            cause=e,
        )


__all__ = [
    "SerializationError",
    "sanitize_for_json",
    "serialize_metrics",
    "serialize_metrics_strict",
    "assert_json_valid",
]