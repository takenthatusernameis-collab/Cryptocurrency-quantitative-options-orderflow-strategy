"""Pydantic schemas for options chains, trades, and orderflow data."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OptionContract(BaseModel):
    symbol: str
    underlying: str
    strike: float
    expiry: datetime
    option_type: str  # 'call' or 'put'
    venue: str
    contract_size: float = 1.0


class OptionQuote(BaseModel):
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
    underlying: str
    venue: str
    quotes: List[OptionQuote]
    timestamp: datetime


class Trade(BaseModel):
    trade_id: str
    symbol: str
    venue: str
    price: float
    size: float
    side: str  # 'buy' or 'sell'
    timestamp: datetime


class Liquidation(BaseModel):
    liquidation_id: str
    symbol: str
    venue: str
    price: float
    size: float
    side: str  # 'long' or 'short'
    timestamp: datetime


class FundingRate(BaseModel):
    symbol: str
    venue: str
    funding_rate: float
    funding_time: datetime
    timestamp: datetime


class OrderflowSnapshot(BaseModel):
    symbol: str
    venue: str
    trades: List[Trade] = Field(default_factory=list)
    liquidations: List[Liquidation] = Field(default_factory=list)
    funding_rates: List[FundingRate] = Field(default_factory=list)
    timestamp: datetime
