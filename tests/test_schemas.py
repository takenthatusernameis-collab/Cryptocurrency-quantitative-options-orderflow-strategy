"""Tests for data schemas."""

from datetime import datetime, timezone

from src.data.schemas import OptionContract, OptionQuote, OptionsChain, Trade


def test_option_contract_creation():
    contract = OptionContract(
        symbol="BTC-28OCT22-20000-C",
        underlying="BTC",
        strike=20000.0,
        expiry=datetime(2022, 10, 28),
        option_type="call",
        venue="deribit",
    )
    assert contract.underlying == "BTC"
    assert contract.strike == 20000.0
    assert contract.option_type == "call"


def test_trade_creation():
    trade = Trade(
        trade_id="123",
        symbol="BTC-PERPETUAL",
        venue="deribit",
        price=20000.0,
        size=0.1,
        side="buy",
        timestamp=datetime.now(timezone.utc),
    )
    assert trade.price == 20000.0
    assert trade.size == 0.1
    assert trade.side == "buy"
