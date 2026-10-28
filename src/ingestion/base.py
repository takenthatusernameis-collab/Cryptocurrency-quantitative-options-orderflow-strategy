"""Base ingestion classes for options and orderflow data."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from ..data.schemas import OptionsChain, OrderflowSnapshot


class BaseOptionsIngestion(ABC):
    """Abstract base class for venue-specific options-chain ingestion.

    Concrete subclasses implement venue API details (authentication, request
    formatting, response parsing) while exposing a uniform interface to the
    rest of the pipeline. All methods are network-dependent and may raise on
    connectivity or API errors; callers are expected to handle exceptions.
    """

    def __init__(self, venue: str) -> None:
        self.venue = venue

    @abstractmethod
    def fetch_options_chain(self, underlying: str) -> OptionsChain:
        """Fetch the full options chain (all strikes/expiries) for an underlying.

        Args:
            underlying: Underlying asset identifier (e.g. ``BTC``).

        Returns:
            An :class:`OptionsChain` containing quotes for all available
            strikes and expiries. May be empty on failure.
        """
        pass

    @abstractmethod
    def fetch_available_expiries(self, underlying: str) -> List[datetime]:
        """Return sorted list of expiry datetimes for an underlying.

        Args:
            underlying: Underlying asset identifier (e.g. ``BTC``).

        Returns:
            Sorted list of expiry :class:`datetime` objects (UTC). May be empty
            on failure.
        """
        pass


class BaseOrderflowIngestion(ABC):
    """Abstract base class for venue-specific orderflow microstructure ingestion.

    Concrete subclasses implement venue API details while exposing a uniform
    interface for fetching trades and liquidations. All methods are
    network-dependent and may raise on connectivity or API errors.
    """

    def __init__(self, venue: str) -> None:
        self.venue = venue

    @abstractmethod
    def fetch_trades(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        """Fetch recent trades for a symbol.

        Args:
            symbol: Venue-specific instrument identifier.
            limit: Maximum number of trades to retrieve.

        Returns:
            An :class:`OrderflowSnapshot` whose ``trades`` list contains the
            fetched trades. May be empty on failure.
        """
        pass

    @abstractmethod
    def fetch_liquidations(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        """Fetch recent liquidations for a symbol.

        Args:
            symbol: Venue-specific instrument identifier.
            limit: Maximum number of liquidations to retrieve.

        Returns:
            An :class:`OrderflowSnapshot` whose ``liquidations`` list contains
            the fetched liquidations. May be empty on failure or when the
            venue does not expose liquidation data.
        """
        pass
