from datetime import datetime, timezone

from src.data.schemas import OptionContract, OptionQuote, OptionsChain, Trade
from src.features.gamma_exposure import (
    calculate_gamma_exposure,
    calculate_gex_by_strike,
    calculate_delta_weighted_gex,
    calculate_total_delta_weighted_gex,
    gamma_flip_level_weighted,
)
from src.features.liquidity import (
    calculate_bid_ask_spread,
    calculate_mid_price,
    calculate_relative_spread,
    calculate_liquidity_score,
    calculate_chain_liquidity_metrics,
)
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


def test_delta_weighted_gex_uses_delta():
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
        gamma=0.0002,
        delta=0.5,
        open_interest=500.0,
        volume=50.0,
        timestamp=datetime.now(timezone.utc),
    )
    gex = calculate_gamma_exposure(quote, 20000.0)
    gex_dw = calculate_delta_weighted_gex(quote, 20000.0)
    assert isinstance(gex_dw, float)
    assert gex_dw != 0.0 or gex == 0.0


def test_gamma_exposure_chain_delta_weighted_total():
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
        delta=0.6,
        open_interest=2000.0,
        volume=200.0,
        timestamp=datetime.now(timezone.utc),
    )
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[quote], timestamp=datetime.now(timezone.utc))
    total_dw = calculate_total_delta_weighted_gex(chain, 20000.0)
    assert isinstance(total_dw, float)
    assert total_dw >= 0.0  # call gives positive contribution in magnitude convention


def test_gamma_flip_level_weighted():
    c1 = OptionContract(symbol="BTC-C1", underlying="BTC", strike=19000.0, expiry=datetime(2022, 10, 28, tzinfo=timezone.utc), option_type="call", venue="deribit")
    c2 = OptionContract(symbol="BTC-P1", underlying="BTC", strike=21000.0, expiry=datetime(2022, 10, 28, tzinfo=timezone.utc), option_type="put", venue="deribit")
    q1 = OptionQuote(contract=c1, bid=500, ask=510, gamma=0.0001, delta=0.8, open_interest=1000, volume=10, timestamp=datetime.now(timezone.utc))
    q2 = OptionQuote(contract=c2, bid=400, ask=410, gamma=0.00015, delta=-0.3, open_interest=1500, volume=20, timestamp=datetime.now(timezone.utc))
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[q1, q2], timestamp=datetime.now(timezone.utc))
    flip = gamma_flip_level_weighted(chain, 20000.0, weighted="delta")
    assert isinstance(flip, float)


def test_liquidity_metrics():
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
        last=105.0,
        open_interest=1000.0,
        volume=500.0,
        timestamp=datetime.now(timezone.utc),
    )
    spread = calculate_bid_ask_spread(quote)
    mid = calculate_mid_price(quote)
    rel = calculate_relative_spread(quote)
    score = calculate_liquidity_score(quote)
    assert spread == 10.0
    assert mid == 105.0
    assert rel > 0
    assert 0 <= score <= 1
    chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[quote], timestamp=datetime.now(timezone.utc))
    metrics = calculate_chain_liquidity_metrics(chain)
    assert "avg_bid_ask_spread" in metrics
    assert "avg_liquidity_score" in metrics
    assert metrics["total_oi"] == 1000.0


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
