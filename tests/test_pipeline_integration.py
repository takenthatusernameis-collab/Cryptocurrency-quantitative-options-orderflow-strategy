"""Integration tests for the full pipeline with mocked connectors."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from src.data.schemas import (
    OptionContract,
    OptionQuote,
    OptionsChain,
    Trade,
    OrderflowSnapshot,
)
from src.main import run_pipeline


def _make_chain(venue="deribit", underlying="BTC"):
    contract_call = OptionContract(
        symbol="BTC-28OCT22-50000-C",
        underlying=underlying,
        strike=50000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="call",
        venue=venue,
    )
    contract_put = OptionContract(
        symbol="BTC-28OCT22-50000-P",
        underlying=underlying,
        strike=50000.0,
        expiry=datetime(2022, 10, 28, tzinfo=timezone.utc),
        option_type="put",
        venue=venue,
    )
    quotes = [
        OptionQuote(
            contract=contract_call,
            bid=100.0,
            ask=110.0,
            gamma=0.0001,
            open_interest=1000.0,
            volume=100.0,
            mark_iv=0.6,
            timestamp=datetime.now(timezone.utc),
        ),
        OptionQuote(
            contract=contract_put,
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


def _make_orderflow(venue="deribit", symbol="BTC"):
    trades = [
        Trade(trade_id="1", symbol=symbol, venue=venue, price=50000.0, size=1.0, side="buy", timestamp=datetime.now(timezone.utc)),
        Trade(trade_id="2", symbol=symbol, venue=venue, price=50000.0, size=0.5, side="sell", timestamp=datetime.now(timezone.utc)),
    ]
    return OrderflowSnapshot(symbol=symbol, venue=venue, trades=trades, timestamp=datetime.now(timezone.utc))


def test_pipeline_wires_alpha_features():
    """Pipeline must compute iv_skew, of_imbalance, max_pain from real features (not hardcoded 0.0)."""
    chain = _make_chain()
    of = _make_orderflow()
    config = {
        "venues": ["deribit"],
        "data": {"symbols": ["BTC"]},
        "backtest": {"initial_capital": 100000.0, "fee_rate": 0.0, "slippage_bps": 0},
        "risk": {"max_position_pct": 0.1, "max_drawdown_limit": 0.2, "stop_loss_pct": 0.02, "take_profit_pct": 0.04},
    }
    with patch("src.main.DeribitOptionsIngestion") as MockOpt, \
         patch("src.main.DeribitOrderflowIngestion") as MockOf:
        MockOpt.return_value.fetch_options_chain.return_value = chain
        MockOf.return_value.fetch_trades.return_value = of
        res = run_pipeline(config, symbols=["BTC"])

    assert "errors" in res
    sigs = res.get("signals", {})
    assert "deribit:BTC" in sigs
    sig = sigs["deribit:BTC"]
    # Alpha features must be wired (not hardcoded 0.0)
    assert sig["iv_skew"] != 0.0  # put_iv > call_iv => positive skew
    assert sig["orderflow_imbalance"] != 0.0  # buy 1.0 vs sell 0.5 => 0.333...
    assert sig["max_pain"] == 50000.0
    assert sig["cumulative_delta"] == 0.5
    assert "gamma_flip" in sig


def test_pipeline_json_serializable():
    """Full pipeline output must be JSON-serializable with allow_nan=False."""
    import json
    import math
    chain = _make_chain()
    of = _make_orderflow()
    config = {
        "venues": ["deribit"],
        "data": {"symbols": ["BTC"]},
        "backtest": {"initial_capital": 100000.0, "fee_rate": 0.0, "slippage_bps": 0},
        "risk": {"max_position_pct": 0.1, "max_drawdown_limit": 0.2, "stop_loss_pct": 0.02, "take_profit_pct": 0.04},
    }
    with patch("src.main.DeribitOptionsIngestion") as MockOpt, \
         patch("src.main.DeribitOrderflowIngestion") as MockOf:
        MockOpt.return_value.fetch_options_chain.return_value = chain
        MockOf.return_value.fetch_trades.return_value = of
        res = run_pipeline(config, symbols=["BTC"])
    # Should serialize without raising
    json.dumps(res, indent=2, default=str, allow_nan=False)


def test_pipeline_collects_feature_errors():
    """Per-key feature errors must be collected in results['errors'] with context."""
    chain = _make_chain()
    config = {
        "venues": ["deribit"],
        "data": {"symbols": ["BTC"]},
        "backtest": {"initial_capital": 100000.0, "fee_rate": 0.0, "slippage_bps": 0},
        "risk": {"max_position_pct": 0.1, "max_drawdown_limit": 0.2, "stop_loss_pct": 0.02, "take_profit_pct": 0.04},
    }
    # Force an exception in feature computation by making calculate_total_gex raise
    with patch("src.main.DeribitOptionsIngestion") as MockOpt, \
         patch("src.main.DeribitOrderflowIngestion") as MockOf, \
         patch("src.main.calculate_total_gex", side_effect=RuntimeError("boom")):
        MockOpt.return_value.fetch_options_chain.return_value = chain
        MockOf.return_value.fetch_trades.return_value = _make_orderflow()
        res = run_pipeline(config, symbols=["BTC"])
    # The error must be captured with context
    assert any("signal_generation_deribit:BTC" in e or "RuntimeError" in e or "boom" in e for e in res["errors"])