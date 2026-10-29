"""Structured error logging helpers for domain exceptions.

Provides thin wrappers around :class:`StructuredLogger` that ensure every
domain error (RiskLimitError, OrderError, SerializationError, etc.) is logged
with a consistent context payload: module, symbol, timestamp, operation, and
the original exception's context. Callers in hot paths should use these helpers
rather than constructing ad-hoc log lines.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Optional

from ..errors import StrategyError, get_logger

_logger = get_logger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_strategy_error(
    exc: BaseException,
    *,
    operation: str,
    module: Optional[str] = None,
    symbol: Optional[str] = None,
    venue: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Log a :class:`StrategyError` (or any exception) with structured context.

    The log line includes the exception type/message, the original error's
    context (if any), and the caller-supplied fields. Designed to be called from
    ``except`` blocks where the exception is already in hand.
    """
    ctx: Dict[str, Any] = {
        "operation": operation,
        "timestamp": _now_iso(),
    }
    if module is not None:
        ctx["module"] = module
    if symbol is not None:
        ctx["symbol"] = symbol
    if venue is not None:
        ctx["venue"] = venue
    if extra:
        ctx.update(extra)

    if isinstance(exc, StrategyError) and exc.context:
        # Merge strategy error context without clobbering explicit fields.
        merged = dict(exc.context)
        merged.update(ctx)
        ctx = merged

    _logger.exception(
        f"{type(exc).__name__}: {exc}",
        exc,
        **ctx,
    )


def log_error_with_context(
    message: str,
    *,
    operation: str,
    exc: Optional[BaseException] = None,
    module: Optional[str] = None,
    symbol: Optional[str] = None,
    venue: Optional[str] = None,
    extra: Optional[Dict[str, Any]] = None,
) -> None:
    """Log a free-form error with structured context and optional exception."""
    ctx: Dict[str, Any] = {
        "operation": operation,
        "timestamp": _now_iso(),
    }
    if module is not None:
        ctx["module"] = module
    if symbol is not None:
        ctx["symbol"] = symbol
    if venue is not None:
        ctx["venue"] = venue
    if extra:
        ctx.update(extra)
    if exc is not None:
        _logger.exception(message, exc, **ctx)
    else:
        _logger.error(message, **ctx)


__all__ = ["log_strategy_error", "log_error_with_context"]