"""Pydantic schemas for options chains, trades, and orderflow data."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OptionContract(BaseModel):
    """Canonical option contract descriptor shared across all venues.

    Encodes the static terms of an option: underlying, strike, expiry, option
    type (call or put), and contract size. The ``symbol`` is the venue-specific
    instrument identifier used for ingestion. All monetary/quantity fields are
    denominated in the contract's notional units (e.g. BTC for crypto options).
    """

    symbol: str
    underlying: str
    strike: float
    expiry: datetime
    option_type: str  # 'call' or 'put'
    venue: str
    contract_size: float = 1.0


class OptionQuote(BaseModel):
    """Market data and Greeks for a single option contract at a point in time.

    Prices (bid/ask/last/mark) are in the option's premium units. IV fields
    (bid_iv/ask_iv/mark_iv) are in decimal form (e.g. 0.65 = 65% implied
    volatility). Greeks (delta, gamma, theta, vega) follow the standard
    convention: delta is in [-1, 1] (positive for calls, negative for puts);
    gamma is positive for both calls and puts; theta is typically negative
    (time decay); vega is positive for both (price sensitivity to IV). Optional
    fields default to ``None`` when the venue does not supply them.
    """

    contract: OptionContract
    bid: float
    ask: float
    last: Optional[float] = None
    mark: Optional[float] = None
    bid_iv: Optional[float] = None
    ask_iv: Optional[float] = None
    mark_iv: Optional[float] = None
    delta: Optional[float] = None
    gamma: Optional[float] = None
    theta: Optional[float] = None
    vega: Optional[float] = None
    open_interest: float = 0.0
    volume: float = 0.0
    timestamp: datetime


class OptionsChain(BaseModel):
    """A collection of :class:`OptionQuote` for a single underlying and venue.

    Represents a full cross-section of strikes and expiries at a snapshot in
    time. ``quotes`` is unindexed; consumers are expected to filter by strike,
    expiry, or option type as needed for feature calculations.
    """

    underlying: str
    venue: str
    quotes: List[OptionQuote]
    timestamp: datetime


class Trade(BaseModel):
    """An individual executed trade on a venue.

    ``side`` is ``'buy'`` or ``'sell'`` from the perspective of the taker:
    a ``'buy'`` trade means the taker bought (aggressive buyer), a ``'sell'``
    means the taker sold (aggressive seller). This convention is used
    consistently in orderflow features (cumulative delta, imbalance).
    """

    trade_id: str
    symbol: str
    venue: str
    price: float
    size: float
    side: str  # 'buy' or 'sell'
    timestamp: datetime


class Liquidation(BaseModel):
    """A forced liquidation event from a leveraged position.

    ``side`` is ``'long'`` or ``'short'`` referring to the position that was
    liquidated. A long liquidation sells into the market (bearish pressure);
    a short liquidation buys to cover (bullish pressure).
    """

    liquidation_id: str
    symbol: str
    venue: str
    price: float
    size: float
    side: str  # 'long' or 'short'
    timestamp: datetime


class FundingRate(BaseModel):
    """Perpetual-swap funding rate observation.

    ``funding_rate`` is the periodic payment rate (e.g. 0.0001 = 0.01% of
    notional) paid by the side paying the other. Positive rates indicate longs
    pay shorts (bearish bias); negative rates indicate shorts pay longs
    (bullish bias).
    """

    symbol: str
    venue: str
    funding_rate: float
    funding_time: datetime
    timestamp: datetime


class OrderflowSnapshot(BaseModel):
    """Normalized container for all orderflow microstructure data for a symbol.

    Aggregates trades, liquidations, and funding rates observed over a window
    into a single object so feature functions can compute orderflow imbalance,
    toxicity, and delta divergence from one source.
    """

    symbol: str
    venue: str
    trades: List[Trade] = Field(default_factory=list)
    liquidations: List[Liquidation] = Field(default_factory=list)
    funding_rates: List[FundingRate] = Field(default_factory=list)
    timestamp: datetime
