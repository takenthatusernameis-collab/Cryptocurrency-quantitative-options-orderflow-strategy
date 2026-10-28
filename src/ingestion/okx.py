"""OKX ingestion (skeleton with correct interfaces)."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from ..data.schemas import OptionsChain, OrderflowSnapshot
from .base import BaseOptionsIngestion, BaseOrderflowIngestion


class OKXOptionsIngestion(BaseOptionsIngestion):
    def __init__(self):
        super().__init__("okx")

    def fetch_options_chain(self, underlying: str) -> OptionsChain:
        return OptionsChain(
            underlying=underlying,
            venue=self.venue,
            quotes=[],
            timestamp=datetime.now(timezone.utc),
        )

    def fetch_available_expiries(self, underlying: str) -> List[datetime]:
        return []


class OKXOrderflowIngestion(BaseOrderflowIngestion):
    def __init__(self):
        super().__init__("okx")

    def fetch_trades(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        return OrderflowSnapshot(symbol=symbol, venue=self.venue, trades=[], timestamp=datetime.now(timezone.utc))

    def fetch_liquidations(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        return OrderflowSnapshot(symbol=symbol, venue=self.venue, liquidations=[], timestamp=datetime.now(timezone.utc))
