"""Domain-specific exceptions and structured logging utilities.

This module defines a consistent exception hierarchy for the quantitative
options orderflow strategy. All exceptions carry contextual payloads
(venue, symbol, strike, expiry, function, run_id, operation) to support
structured logging and post-mortem analysis.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class StrategyError(Exception):
    """Root exception for all strategy/domain errors."""

    def __init__(
        self,
        message: str,
        *,
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[BaseException] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.context: Dict[str, Any] = dict(context) if context else {}
        if cause is not None:
            self.context.setdefault("cause_type", type(cause).__name__)
            self.context.setdefault("cause_message", str(cause))


class IngestionError(StrategyError):
    """Errors originating from venue data ingestion (network, auth, parse)."""


class AuthError(IngestionError):
    """Authentication/authorization failures when accessing venue endpoints."""


class NetworkError(IngestionError):
    """Network/connectivity failures (timeouts, connection errors)."""


class ParseError(IngestionError):
    """Response parsing/normalization failures from venue payloads."""


class DataError(StrategyError):
    """Data quality/schema/normalization errors."""


class InsufficientDataError(DataError):
    """Not enough data points to compute a metric reliably."""


class ConfigError(StrategyError):
    """Configuration validation/loading errors."""


class BacktestError(StrategyError):
    """Backtesting engine errors (execution, fills, risk)."""


class RiskLimitError(BacktestError):
    """Risk limits breached (position size, drawdown, quantity caps)."""


class OrderError(BacktestError):
    """Invalid order parameters or execution constraints."""


class FeatureError(StrategyError):
    """Feature engineering/calculation errors."""


class NonFiniteResultError(FeatureError):
    """Numerical result is non-finite (NaN/Inf) when finiteness required."""


class ValidationError(StrategyError):
    """Input validation failures with field-level context."""


class SerializationError(StrategyError):
    """Serialization/deserialization failures."""


class DeterminismError(StrategyError):
    """Determinism/integrity errors in reproducibility-sensitive paths."""


def _serialize_context_value(v: Any) -> Any:
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    if isinstance(v, datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        return v.isoformat()
    if is_dataclass(v) and not isinstance(v, type):
        try:
            return asdict(v)
        except Exception:
            return str(v)
    if isinstance(v, dict):
        return {k: _serialize_context_value(val) for k, val in v.items()}
    if isinstance(v, (list, tuple, set)):
        return [_serialize_context_value(x) for x in v]
    # Fallback
    try:
        json.dumps(v, allow_nan=False)
        return v
    except Exception:
        return str(v)


class StructuredLogger:
    """JSON-line structured logger with correlation fields."""

    def __init__(self, name: str) -> None:
        self._logger = logging.getLogger(name)
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)
            self._logger.setLevel(logging.INFO)

    def _emit(self, level: str, msg: str, **ctx: Any) -> None:
        payload: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "logger": self._logger.name,
            "msg": msg,
        }
        for k, v in ctx.items():
            payload[k] = _serialize_context_value(v)
        try:
            line = json.dumps(payload, allow_nan=False)
        except (ValueError, TypeError):
            line = json.dumps(payload, allow_nan=False, default=str)
        log_fn = getattr(self._logger, level.lower(), self._logger.info)
        log_fn(line)

    def debug(self, msg: str, **ctx: Any) -> None:
        self._emit("DEBUG", msg, **ctx)

    def info(self, msg: str, **ctx: Any) -> None:
        self._emit("INFO", msg, **ctx)

    def warning(self, msg: str, **ctx: Any) -> None:
        self._emit("WARNING", msg, **ctx)

    def error(self, msg: str, **ctx: Any) -> None:
        self._emit("ERROR", msg, **ctx)

    def exception(self, msg: str, exc: BaseException, **ctx: Any) -> None:
        c = dict(ctx)
        c.setdefault("exc_type", type(exc).__name__)
        c.setdefault("exc_msg", str(exc))
        if isinstance(exc, StrategyError) and exc.context:
            # merge strategy error context (non-clobbering of explicit ctx)
            merged = dict(exc.context)
            merged.update(c)
            c = merged
        self._emit("ERROR", msg, **c)


def get_logger(name: str) -> StructuredLogger:
    return StructuredLogger(name)


# Additional aliases for compatibility
SchemaError = DataError
