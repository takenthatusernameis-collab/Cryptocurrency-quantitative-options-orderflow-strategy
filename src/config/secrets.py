"""Secrets management and secure configuration."""
from __future__ import annotations

import os
import re
from typing import Any, Dict, Optional

from ..errors import ConfigError, get_logger

_logger = get_logger(__name__)


class SecretsManager:
    def __init__(self, provider: str = "env"):
        self.provider = provider
        self._cache: Dict[str, str] = {}

    def get_secret(self, key: str, required: bool = False) -> Optional[str]:
        if key in self._cache:
            return self._cache[key]
        value = os.environ.get(key)
        if value is None:
            for prefix in ["DERIBIT_", "OKX_", "BINANCE_", "API_"]:
                alt_key = prefix + key if not key.startswith(prefix) else key
                value = os.environ.get(alt_key)
                if value:
                    break
        if value is None and required:
            raise ConfigError(f"Required secret {key} not found", context={"key": key})
        if value:
            self._cache[key] = value
        return value

    def get_venue_credentials(self, venue: str) -> Dict[str, Optional[str]]:
        venue_upper = venue.upper()
        creds = {
            "api_key": self.get_secret(f"{venue_upper}_API_KEY"),
            "api_secret": self.get_secret(f"{venue_upper}_API_SECRET"),
        }
        if venue_upper == "OKX":
            creds["passphrase"] = self.get_secret(f"{venue_upper}_PASSPHRASE")
        return creds

    def redact(self, data: Any) -> Any:
        if isinstance(data, str):
            if re.match(r'^[A-Za-z0-9+/]{32,}$', data) or re.match(r'^[a-f0-9]{32,64}$', data):
                return "[REDACTED]"
            return data
        elif isinstance(data, dict):
            redacted = {}
            for k, v in data.items():
                if any(secret_word in k.lower() for secret_word in ['key', 'secret', 'password', 'passphrase', 'token']):
                    redacted[k] = "[REDACTED]" if v is not None else None
                else:
                    redacted[k] = self.redact(v)
            return redacted
        elif isinstance(data, (list, tuple)):
            return type(data)(self.redact(item) for item in data)
        return data


def load_secrets_config() -> Dict[str, Any]:
    sm = SecretsManager()
    return {
        "deribit": sm.get_venue_credentials("deribit"),
        "okx": sm.get_venue_credentials("okx"),
        "binance": sm.get_venue_credentials("binance"),
        "trading_mode": os.environ.get("TRADING_MODE", "paper"),
        "live_trading_enabled": os.environ.get("LIVE_TRADING_ENABLED", "false").lower() == "true",
    }
