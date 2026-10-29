"""End-to-end determinism tests for the full pipeline."""

import json
from datetime import datetime, timezone
from unittest.mock import patch

from src.data.schemas import (
    OptionContract,
    OptionQuote,
    OptionsChain,
    Trade,
    OrderflowSnapshot,
)
from src.main import run_pipeline
from src.telemetry import serialize_metrics


def _make_chain(venue="deribit", underlying="BTC"):
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
    contract_call_otm = OptionContract(
        symbol="BTC-28OCT22-54000-C",
        underlying=underlying,
        strike=54000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="call",
        venue=venue,
    )
    contract_put_otm = OptionContract(
        symbol="BTC-28OCT22-46000-P",
        underlying=underlying,
        strike=46000.0,
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
            timestamp=datetime(2022, 10, 27, 12, 0, 0, tzinfo=timezone.utc),
        ),
        OptionQuote(
            contract=contract_put_atm,
            bid=90.0,
            ask=100.0,
            gamma=0.0001,
            open_interest=500.0,
            volume=50.0,
            mark_iv=0.65,
            timestamp=datetime(2022, 10, 27, 12, 0, 0, tzinfo=timezone.utc),
        ),
        OptionQuote(
            contract=contract_call_otm,
            bid=50.0,
            ask=55.0,
            gamma=0.0001,
            open_interest=200.0,
            volume=20.0,
            mark_iv=0.62,
            timestamp=datetime(2022, 10, 27, 12, 0, 0, tzinfo=timezone.utc),
        ),
        OptionQuote(
            contract=contract_put_otm,
            bid=45.0,
            ask=50.0,
            gamma=0.0001,
            open_interest=300.0,
            volume=30.0,
            mark_iv=0.68,
            timestamp=datetime(2022, 10, 27, 12, 0, 0, tzinfo=timezone.utc),
        ),
    ]
    return OptionsChain(underlying=underlying, venue=venue, quotes=quotes, timestamp=datetime(2022, 10, 27, 12, 0, 0, tzinfo=timezone.utc))


def _make_orderflow(venue="deribit", symbol="BTC"):
    trades = [
        Trade(trade_id="1", symbol=symbol, venue=venue, price=50000.0, size=1.0, side="buy", timestamp=datetime(2022, 10, 27, 12, 0, 0, tzinfo=timezone.utc)),
        Trade(trade_id="2", symbol=symbol, venue=venue, price=50000.0, size=0.5, side="sell", timestamp=datetime(2022, 10, 27, 12, 0, 0, tzinfo=timezone.utc)),
    ]
    return OrderflowSnapshot(symbol=symbol, venue=venue, trades=trades, timestamp=datetime(2022, 10, 27, 12, 0, 0, tzinfo=timezone.utc))


def test_pipeline_run_twice_deterministic_json():
    chain = _make_chain()
    of = _make_orderflow()
    config = {
        "venues": ["deribit"],
        "data": {"symbols": ["BTC"], "spot_price": 50000.0},
        "backtest": {"initial_capital": 100000.0, "fee_rate": 0.0, "slippage_bps": 0},
        "risk": {"max_position_pct": 0.1, "max_drawdown_limit": 0.2, "stop_loss_pct": 0.02, "take_profit_pct": 0.04},
    }
    with patch("src.main.DeribitOptionsIngestion") as MockOpt, \
         patch("src.main.DeribitOrderflowIngestion") as MockOf:
        MockOpt.return_value.fetch_options_chain.return_value = chain
        MockOf.return_value.fetch_trades.return_value = of
        res1 = run_pipeline(config, symbols=["BTC"])
        res2 = run_pipeline(config, symbols=["BTC"])

    res1_s = serialize_metrics(res1)
    res2_s = serialize_metrics(res2)
    # Normalize timestamps for determinism check
    def _norm(d):
        if isinstance(d, dict):
            out = {}
            for k, v in d.items():
                if k == "timestamp":
                    out[k] = "1970-01-01T00:00:00+00:00"
                else:
                    out[k] = _norm(v)
            return out
        elif isinstance(d, list):
            return [_norm(x) for x in d]
        return d

    s1 = json.dumps(_norm(res1_s), sort_keys=True, default=str, allow_nan=False)
    s2 = json.dumps(_norm(res2_s), sort_keys=True, default=str, allow_nan=False)
    assert s1 == s2
