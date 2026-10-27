"""Deribit options and orderflow ingestion."""

from datetime import datetime
from typing import List

from ..data.schemas import (
    Liquidation,
    OptionContract,
    OptionQuote,
    OptionsChain,
    OrderflowSnapshot,
    Trade,
)
from .base import BaseOptionsIngestion, BaseOrderflowIngestion


class DeribitOptionsIngestion(BaseOptionsIngestion):
    def __init__(self):
        super().__init__("deribit")

    def fetch_options_chain(self, underlying: str) -> OptionsChain:
        # Structure for real implementation - returns empty chain as placeholder
        # for API integration
        return OptionsChain(
            underlying=underlying,
            venue=self.venue,
            quotes=[],
            timestamp=datetime.utcnow(),
        )

    def fetch_available_expiries(self, underlying: str) -> List[datetime]:
        return []


class DeribitOrderflowIngestion(BaseOrderflowIngestion):
    def __init__(self):
        super().__init__("deribit")

    def fetch_trades(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        return OrderflowSnapshot(
            symbol=symbol,
            venue=self.venue,
            trades=[],
            timestamp=datetime.utcnow(),
        )

    def fetch_liquidations(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        return OrderflowSnapshot(
            symbol=symbol,
            venue=self.venue,
            liquidations=[],
            timestamp=datetime.utcnow(),
        )
