"""Mock ingestion for offline testing and pipeline validation.

Provides deterministic, network-free implementations of the options and
orderflow ingestion interfaces so the full pipeline can run without
external API access. Useful for CI, local development, and backtesting.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from ..data.schemas import (
    Liquidation,
    OptionContract,
    OptionQuote,
    OptionsChain,
    OrderflowSnapshot,
    Trade,
)
from .base import BaseOptionsIngestion, BaseOrderflowIngestion


def _dt(ts: Optional[datetime] = None) -> datetime:
    return ts if ts is not None else datetime.now(timezone.utc)


def _make_quote(strike: float, spot: float, option_type: str, i: int, venue: str) -> OptionQuote:
    """Generate a deterministic quote around the spot price."""
    # Moneyness drift so we get OTM/ITM variety
    offset = (i % 5) - 2  # -2..2
    actual_strike = spot + offset * (spot * 0.02)
    expiry = _dt(datetime(2026, 12, 31))
    contract = OptionContract(
        symbol=f"{venue}-{int(actual_strike)}-{option_type[0].upper()}",
        underlying="BTC",
        strike=float(actual_strike),
        expiry=expiry,
        option_type=option_type,
        venue=venue,
        contract_size=1.0,
    )
    # Basic greeks approximation for testing
    moneyness = actual_strike / spot if spot > 0 else 1.0
    gamma = 0.0001 if 0.95 < moneyness < 1.05 else 0.00005
    return OptionQuote(
        contract=contract,
        bid=max(0.0, spot - actual_strike + 100.0) if option_type == "call" else max(0.0, actual_strike - spot + 100.0),
        ask=max(0.0, spot - actual_strike + 110.0) if option_type == "call" else max(0.0, actual_strike - spot + 110.0),
        last=None,
        mark=None,
        bid_iv=0.6 + (0.05 if option_type == "put" else -0.02),
        ask_iv=0.61 + (0.05 if option_type == "put" else -0.02),
        mark_iv=0.6 + (0.05 if option_type == "put" else -0.02),
        delta=0.5 if option_type == "call" else -0.5,
        gamma=gamma,
        theta=-50.0,
        vega=80.0,
        open_interest=float(1000 + i * 50),
        volume=float(100 + i * 10),
        timestamp=_dt(),
    )


class MockOptionsIngestion(BaseOptionsIngestion):
    """Deterministic options chain generator for offline use."""

    def __init__(self, venue: str = "mock", spot_price: float = 50000.0, num_strikes: int = 6):
        super().__init__(venue)
        self.spot_price = float(spot_price)
        self.num_strikes = int(num_strikes)

    def fetch_available_expiries(self, underlying: str) -> List[datetime]:
        return [_dt(datetime(2026, 12, 31)), _dt(datetime(2027, 1, 28))]

    def fetch_options_chain(self, underlying: str) -> OptionsChain:
        quotes: List[OptionQuote] = []
        for i in range(self.num_strikes):
            quotes.append(_make_quote(self.spot_price, self.spot_price, "call", i, self.venue))
            quotes.append(_make_quote(self.spot_price, self.spot_price, "put", i, self.venue))
        return OptionsChain(
            underlying=underlying.upper(),
            venue=self.venue,
            quotes=quotes,
            timestamp=_dt(),
        )


class MockOrderflowIngestion(BaseOrderflowIngestion):
    """Deterministic orderflow generator for offline use."""

    def __init__(self, venue: str = "mock", num_trades: int = 20, spot_price: float = 50000.0):
        super().__init__(venue)
        self.num_trades = int(num_trades)
        self.spot_price = float(spot_price)

    def fetch_trades(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        trades: List[Trade] = []
        n = min(self.num_trades, limit)
        for i in range(n):
            # Alternate buy/sell with slight buy bias
            side = "buy" if i % 3 != 2 else "sell"
            size = 0.1 * (1 + (i % 5))
            price = self.spot_price + (50.0 if side == "buy" else -50.0)
            trades.append(
                Trade(
                    trade_id=f"{self.venue}-{symbol}-{i}",
                    symbol=symbol,
                    venue=self.venue,
                    price=float(price),
                    size=float(size),
                    side=side,
                    timestamp=_dt(),
                )
            )
        return OrderflowSnapshot(symbol=symbol, venue=self.venue, trades=trades, timestamp=_dt())

    def fetch_liquidations(self, symbol: str, limit: int = 1000) -> OrderflowSnapshot:
        return OrderflowSnapshot(symbol=symbol, venue=self.venue, liquidations=[], timestamp=_dt())


def make_mock_venue(name: str = "mock"):
    """Return a tuple of (options_ingestion, orderflow_ingestion) for a venue."""
    return MockOptionsIngestion(venue=name), MockOrderflowIngestion(venue=name)