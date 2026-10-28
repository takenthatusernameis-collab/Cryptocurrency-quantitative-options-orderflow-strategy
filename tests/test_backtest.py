"""Tests for backtesting engine."""

from datetime import datetime, timezone

from src.backtest.engine import BacktestEngine
from src.config import BacktestConfig


def test_backtest_engine_init():
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    assert engine.cash == 100000.0
    assert len(engine.trades) == 0


def test_execute_buy_trade():
    config = BacktestConfig(initial_capital=100000.0, fee_rate=0.001, slippage_bps=0)
    engine = BacktestEngine(config)
    trade = engine.execute_trade("BTC", 1.0, 50000.0, "buy", datetime.now(timezone.utc))
    assert trade.side == "buy"
    assert engine.cash < 100000.0
    assert "BTC" in engine.positions


def test_calculate_metrics():
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    engine.equity_curve = [100000.0, 101000.0, 100500.0]
    results = engine.calculate_metrics()
    assert results.total_return > 0


def test_short_selling_within_position_limit():
    config = BacktestConfig(initial_capital=100000.0, fee_rate=0.001, slippage_bps=0)
    engine = BacktestEngine(config)
    # Open short within max_position_pct (0.1): 0.2 BTC @ 50000 = 10000 notional == cap
    trade = engine.execute_trade("BTC", 0.2, 50000.0, "sell", datetime.now(timezone.utc))
    assert trade.side == "sell"
    assert "BTC" in engine.positions
    assert engine.positions["BTC"].side == "short"
    # Short proceeds credited to cash
    assert engine.cash > 100000.0
    # Cover short at lower price for profit
    trade2 = engine.execute_trade("BTC", 0.2, 49000.0, "buy", datetime.now(timezone.utc))
    assert trade2.pnl > 0
    assert "BTC" not in engine.positions


def test_position_sizing_and_metrics():
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    qty = engine.calculate_position_size(50000.0)
    assert qty > 0
    engine.equity_curve = [100000, 102000, 101000, 103000]
    res = engine.calculate_metrics()
    assert res.calmar_ratio >= 0
    assert res.max_drawdown >= 0
