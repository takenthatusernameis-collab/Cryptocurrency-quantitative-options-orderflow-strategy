"""Tests for feature engineering."""

from datetime import datetime, timezone

from src.data.schemas import OptionContract, OptionQuote, OptionsChain, Trade
from src.features.gamma_exposure import calculate_gamma_exposure, calculate_gex_by_strike
from src.features.orderflow import calculate_cumulative_delta, calculate_orderflow_imbalance
from src.features.volatility import calculate_put_call_ratio, calculate_max_pain


def test_gamma_exposure_calculation():
    contract = OptionContract(
        symbol="BTC-28OCT22-20000-C",
        underlying="BTC",
        strike=20000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="call",
        venue="deribit",
    )
    quote = OptionQuote(
        contract=contract,
        bid=100.0,
        ask=110.0,
        gamma=0.0001,
        open_interest=1000.0,
        volume=100.0,
        timestamp=datetime.now(timezone.utc),
    )
    gex = calculate_gamma_exposure(quote, 20000.0)
    assert isinstance(gex, float)


def test_cumulative_delta():
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20000.0, size=0.5, side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    delta = calculate_cumulative_delta(trades)
    assert delta == 0.5


def test_orderflow_imbalance():
    trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=20000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=20000.0, size=0.5, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="3", symbol="BTC", venue="deribit", price=20000.0, size=0.5, side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    imb = calculate_orderflow_imbalance(trades)
    assert imb == 0.5  # (1.5 - 0.5) / 2.0 = 0.5


def test_put_call_ratio():
    contracts_call = OptionContract(
        symbol="BTC-C", underlying="BTC", strike=20000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc), option_type="call", venue="deribit"
    )
    contracts_put = OptionContract(
        symbol="BTC-P", underlying="BTC", strike=20000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc), option_type="put", venue="deribit"
    )
    quotes = [
        OptionQuote(contract=contracts_call, bid=100, ask=110, volume=1000, timestamp=datetime.now(timezone.utc)),
        OptionQuote(contract=contracts_put, bid=90, ask=100, volume=500, timestamp=datetime.now(timezone.utc)),
    ]
    pcr = calculate_put_call_ratio(quotes)
    assert pcr == 0.5
