"""Base ingestion classes for options and orderflow data."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from ..data.schemas import OptionsChain, OrderflowSnapshot


class BaseOptionsIngestion(ABC):
    def __init__(self, venue: str):
        self.venue = venue

    @abstractmethod
    def fetch_options_chain(self, underlying: str) -> OptionsChain:
        pass

    @abstractmethod
    def fetch_available_expiries(self, underlying: str) -> List[datetime]:
        pass


class BaseOrderflowIngestion(ABC):
    def __init__(self, venue: str):
        self.venue = venue

    @abstractmethod
    def fetch_trades(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        pass

    @abstractmethod
    def fetch_liquidations(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        pass
