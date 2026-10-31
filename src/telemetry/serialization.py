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
        # Check for numpy arrays/scalars
        try:
            import numpy as _np  # type: ignore

            if isinstance(value, _np.ndarray):
                if value.size == 0:
                    return False
                # Check all elements
                try:
                    if _np.isnan(value).any() or _np.isinf(value).any():
                        return True
                except Exception:
                    pass
                # Try to convert elementwise
                try:
                    flat = value.ravel()
                    for v in flat:
                        try:
                            if not math.isfinite(float(v)):
                                return True
                        except Exception:
                            pass
                    return False
                except Exception:
                    return False
        except Exception:
            pass
        if hasattr(value, 'dtype') and hasattr(value, 'item'):
            try:
                # For scalar
                f = float(value)
            except Exception:
                try:
                    f = float(value.item())
                except Exception:
                    return False
        else:
            f = float(value)
    except (TypeError, ValueError):
        return False
    try:
        return not math.isfinite(f)
    except Exception:
        return False


def _sanitize_value(value: Any) -> Any:
    """Recursively replace non-finite floats with ``None``.

    Dicts, lists/tuples, and nested containers are traversed. Non-numeric types
    are returned unchanged. This is the non-strict path used when callers prefer
    a best-effort payload over an exception.
    """
    # Handle numpy arrays
    try:
        import numpy as _np  # type: ignore

        if isinstance(value, _np.ndarray):
            try:
                if value.size == 0:
                    return []
                # If contains non-finite, sanitize to list with None
                try:
                    arr = value.astype(float)
                    if _np.isnan(arr).any() or _np.isinf(arr).any():
                        res = []
                        for v in arr.ravel():
                            if _np.isnan(v) or _np.isinf(v):
                                res.append(None)
                            else:
                                # keep as python float
                                try:
                                    res.append(float(v))
                                except Exception:
                                    res.append(None)
                        # try to reshape back? keep as list
                        return res
                    # all finite
                    res = []
                    for v in arr.ravel():
                        res.append(float(v))
                    if arr.ndim == 1 and len(res) == value.size:
                        # return list of floats
                        return res
                    return res
                except Exception:
                    pass
                # fallback
                res = []
                try:
                    for v in value.ravel():
                        try:
                            fv = float(v)
                            if not math.isfinite(fv):
                                res.append(None)
                            else:
                                res.append(fv)
                        except Exception:
                            res.append(str(v))
                except Exception:
                    return str(value)
                return res
            except Exception:
                return value
    except Exception:
        pass

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
                # try item
                try:
                    if hasattr(value, 'item'):
                        f = float(value.item())
                    else:
                        return value
                except Exception:
                    return value
            # Avoid treating ints as floats
            if isinstance(value, (int, bool)) or value is None:
                return value
            try:
                if not math.isfinite(f):
                    return None
            except Exception:
                return None
            # Keep as python float for JSON serialization cleanliness
            return f
        f = float(value)
    except (TypeError, ValueError):
        return value
    # Only treat as numeric if the original was not a bool/str/etc.
    if isinstance(value, (str, bytes, bool)) or value is None:
        return value
    try:
        if not math.isfinite(f):
            return None
    except Exception:
        return value
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
    # Handle numpy arrays
    try:
        import numpy as _np  # type: ignore

        if isinstance(value, _np.ndarray):
            try:
                if value.size == 0:
                    return bad
                arr = value.astype(float)
                if _np.isnan(arr).any() or _np.isinf(arr).any():
                    bad.append(path)
                return bad
            except Exception:
                pass
    except Exception:
        pass
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
                # For 0-d arrays
                try:
                    import numpy as _np  # type: ignore

                    if isinstance(value, _np.ndarray):
                        try:
                            arr = value.astype(float)
                            if _np.isnan(arr).any() or _np.isinf(arr).any():
                                bad.append(path)
                            return bad
                        except Exception:
                            pass
                except Exception:
                    pass
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
        try:
            if not math.isfinite(f):
                bad.append(path)
        except Exception:
            pass
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
        # Sanitize first to handle numpy arrays safely
        sanitized = _sanitize_value(dict(metrics))
        bad_paths2 = _collect_nonfinite_paths(sanitized)
        if bad_paths2:
            raise SerializationError(
                "Non-finite values detected in metrics; refusing to serialize with allow_nan=False",
                context={
                    "operation": "serialize_metrics",
                    "nonfinite_paths": bad_paths2,
                    "allow_nan": False,
                },
            )
        # Ensure no NaN/Inf in sanitized structure
        s = json.dumps(sanitized, default=str, allow_nan=False)
        res = dict(json.loads(s))
        # Final check
        bad_paths3 = _collect_nonfinite_paths(res)
        if bad_paths3:
            raise SerializationError(
                "Non-finite values detected in metrics; refusing to serialize with allow_nan=False",
                context={
                    "operation": "serialize_metrics",
                    "nonfinite_paths": bad_paths3,
                    "allow_nan": False,
                },
            )
        return res  # type: ignore[no-any-return]
    except SerializationError:
        raise
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