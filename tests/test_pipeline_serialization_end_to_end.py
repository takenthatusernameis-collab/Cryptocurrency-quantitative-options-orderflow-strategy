"""End-to-end pipeline serialization test with adversarial/edge cases.

Ensures src.main.run_pipeline -> signal generation -> backtest -> serialization
never emits NaN/Inf and raises SerializationError on leaks.
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from unittest.mock import patch

from src.data.schemas import OptionContract, OptionQuote, OptionsChain, OrderflowSnapshot, Trade
from src.errors import SerializationError
from src.main import run_pipeline
from src.telemetry import serialize_metrics, serialize_metrics_strict


def _make_chain(venue: str = "deribit", underlying: str = "BTC") -> OptionsChain:
    contract_call_atm = OptionContract(
        symbol="BTC-28OCT22-50000-C",
        underlying=underlying,
        strike=50000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="call",
        venue=venue,
    )
    contract_put_atm = OptionContract(
        symbol="BTC-28OCT22-50000-P",
        underlying=underlying,
        strike=50000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="put",
        venue=venue,
    )
    quotes = [
        OptionQuote(
            contract=contract_call_atm,
            bid=100.0,
            ask=110.0,
            gamma=0.0001,
            open_interest=1000.0,
            volume=100.0,
            mark_iv=0.6,
            timestamp=datetime.now(timezone.utc),
        ),
        OptionQuote(
            contract=contract_put_atm,
            bid=90.0,
            ask=100.0,
            gamma=0.0001,
            open_interest=500.0,
            volume=50.0,
            mark_iv=0.65,
            timestamp=datetime.now(timezone.utc),
        ),
    ]
    return OptionsChain(underlying=underlying, venue=venue, quotes=quotes, timestamp=datetime.now(timezone.utc))


def _make_orderflow(venue: str = "deribit", symbol: str = "BTC") -> OrderflowSnapshot:
    trades = [
        Trade(trade_id="1", symbol=symbol, venue=venue, price=50000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol=symbol, venue=venue, price=50000.0, size=0.5, side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    return OrderflowSnapshot(symbol=symbol, venue=venue, trades=trades, timestamp=datetime.now(timezone.utc))


def test_pipeline_end_to_end_serialization_clean() -> None:
    chain = _make_chain()
    of = _make_orderflow()
    config = {
        "venues": ["deribit"],
        "data": {"symbols": ["BTC"], "spot_price": 50000.0},
        "backtest": {"initial_capital": 100000.0, "fee_rate": 0.0, "slippage_bps": 0},
        "risk": {"max_position_pct": 0.1, "max_drawdown_limit": 0.2, "stop_loss_pct": 0.02, "take_profit_pct": 0.04},
    }
    with patch("src.main.DeribitOptionsIngestion") as MockOpt, patch("src.main.DeribitOrderflowIngestion") as MockOf:
        MockOpt.return_value.fetch_options_chain.return_value = chain
        MockOf.return_value.fetch_trades.return_value = of
        res = run_pipeline(config, symbols=["BTC"])

    serialized = serialize_metrics(res)
    json.dumps(serialized, allow_nan=False)
    strict = serialize_metrics_strict(res)
    json.dumps(strict, allow_nan=False)


def test_pipeline_serialization_zero_volume_empty_chain() -> None:
    config = {
        "venues": ["deribit"],
        "data": {"symbols": ["BTC"], "spot_price": 50000.0},
        "backtest": {"initial_capital": 100000.0, "fee_rate": 0.0, "slippage_bps": 0},
        "risk": {"max_position_pct": 0.1, "max_drawdown_limit": 0.2, "stop_loss_pct": 0.02, "take_profit_pct": 0.04},
    }
    empty_chain = OptionsChain(underlying="BTC", venue="deribit", quotes=[], timestamp=datetime.now(timezone.utc))
    zero_trades = OrderflowSnapshot(symbol="BTC", venue="deribit", trades=[], timestamp=datetime.now(timezone.utc))
    with patch("src.main.DeribitOptionsIngestion") as MockOpt, patch("src.main.DeribitOrderflowIngestion") as MockOf:
        MockOpt.return_value.fetch_options_chain.return_value = empty_chain
        MockOf.return_value.fetch_trades.return_value = zero_trades
        res = run_pipeline(config, symbols=["BTC"])
    serialized = serialize_metrics(res)
    json.dumps(serialized, allow_nan=False)
    strict = serialize_metrics_strict(res)
    json.dumps(strict, allow_nan=False)


def test_pipeline_serialization_nan_prices_trades() -> None:
    config = {
        "venues": ["deribit"],
        "data": {"symbols": ["BTC"], "spot_price": 50000.0},
        "backtest": {"initial_capital": 100000.0, "fee_rate": 0.0, "slippage_bps": 0},
        "risk": {"max_position_pct": 0.1, "max_drawdown_limit": 0.2, "stop_loss_pct": 0.02, "take_profit_pct": 0.04},
    }
    bad_trades = [
        Trade(trade_id="1", symbol="BTC", venue="deribit", price=float("nan"), size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol="BTC", venue="deribit", price=50000.0, size=float("nan"), side="sell", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="3", symbol="BTC", venue="deribit", price=50000.0, size=1.0, side="badside", timestamp=datetime.now(timezone.utc)),
    ]
    bad_of = OrderflowSnapshot(symbol="BTC", venue="deribit", trades=bad_trades, timestamp=datetime.now(timezone.utc))
    with patch("src.main.DeribitOptionsIngestion") as MockOpt, patch("src.main.DeribitOrderflowIngestion") as MockOf:
        MockOpt.return_value.fetch_options_chain.return_value = _make_chain()
        MockOf.return_value.fetch_trades.return_value = bad_of
        res = run_pipeline(config, symbols=["BTC"])
    serialized = serialize_metrics(res)
    json.dumps(serialized, allow_nan=False)
    strict = serialize_metrics_strict(res)
    json.dumps(strict, allow_nan=False)


def test_pipeline_serialization_inverted_stops() -> None:
    bad_risk_cfg = {
        "venues": ["deribit"],
        "data": {"symbols": ["BTC"], "spot_price": 50000.0},
        "backtest": {"initial_capital": 100000.0, "fee_rate": 0.0, "slippage_bps": 0},
        "risk": {"max_position_pct": 0.1, "max_drawdown_limit": 0.2, "stop_loss_pct": 0.05, "take_profit_pct": 0.02},
    }
    res = run_pipeline(bad_risk_cfg, symbols=["BTC"])
    serialized = serialize_metrics(res)
    json.dumps(serialized, allow_nan=False)
    strict = serialize_metrics_strict(res)
    json.dumps(strict, allow_nan=False)


def test_serialize_metrics_raises_on_leak() -> None:
    try:
        serialize_metrics({"bad": float("inf")})
        assert False, "Expected SerializationError"
    except SerializationError:
        pass
    try:
        serialize_metrics({"nested": {"x": float("nan")}})
        assert False, "Expected SerializationError"
    except SerializationError:
        pass
