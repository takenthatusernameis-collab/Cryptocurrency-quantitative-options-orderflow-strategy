"""Shared utilities for production-grade exchange adapters."""
from __future__ import annotations

import time
import random
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from ..errors import AuthError, IngestionError, NetworkError, get_logger

_logger = get_logger(__name__)


@dataclass
class RateLimitConfig:
    requests_per_second: float = 10.0
    burst: int = 20
    max_retries: int = 5
    base_backoff: float = 0.2
    max_backoff: float = 30.0


class TokenBucket:
    def __init__(self, rate: float = 10.0, burst: int = 20):
        self.rate = float(rate)
        self.burst = int(burst)
        self.tokens = float(burst)
        self.updated_at = time.monotonic()

    def consume(self, tokens: int = 1) -> bool:
        now = time.monotonic()
        elapsed = now - self.updated_at
        self.updated_at = now
        self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def wait_for_token(self, tokens: int = 1) -> None:
        while not self.consume(tokens):
            time.sleep(0.01)


class RetryPolicy:
    def __init__(self, max_retries: int = 5, base_backoff: float = 0.2, max_backoff: float = 30.0):
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.max_backoff = max_backoff

    def call_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        last_exc = None
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except AuthError:
                raise
            except Exception as exc:
                last_exc = exc
                _logger.debug("adapter_retry", attempt=attempt + 1, exc_type=type(exc).__name__)
                if attempt < self.max_retries - 1:
                    sleep_time = min(self.max_backoff, self.base_backoff * (2 ** attempt) * (0.5 + random.random() * 0.5))
                    time.sleep(sleep_time)
        if last_exc:
            raise NetworkError("Request failed after retries", cause=last_exc)
        raise IngestionError("Request failed after retries")


class WebSocketReconnectManager:
    def __init__(self, max_reconnects: int = 10, reconnect_delay: float = 1.0):
        self.max_reconnects = max_reconnects
        self.reconnect_delay = reconnect_delay
        self.reconnect_count = 0
        self.connected = False

    def reconnect(self, connect_func: Callable) -> bool:
        while self.reconnect_count < self.max_reconnects:
            try:
                connect_func()
                self.connected = True
                self.reconnect_count = 0
                return True
            except Exception as exc:
                self.reconnect_count += 1
                _logger.warning("ws_reconnect_attempt", count=self.reconnect_count, exc_type=type(exc).__name__)
                time.sleep(self.reconnect_delay * self.reconnect_count)
        self.connected = False
        return False

    def reset(self):
        self.reconnect_count = 0
        self.connected = False
