"""Production telemetry: serialization guardrails and structured error logging.

This module centralizes metric serialization with ``allow_nan=False`` enforcement
and provides helpers for logging domain errors with full context. All numeric
outputs flowing out of the pipeline must pass through :func:`serialize_metrics`
so that non-finite values cannot leak into JSON.
"""

from .error_logging import log_error_with_context, log_strategy_error
from .serialization import (
    SerializationError,
    sanitize_for_json,
    serialize_metrics,
    serialize_metrics_strict,
)

__all__ = [
    "SerializationError",
    "sanitize_for_json",
    "serialize_metrics",
    "serialize_metrics_strict",
    "log_error_with_context",
    "log_strategy_error",
]