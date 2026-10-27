"""Tests for backtesting engine."""

from datetime import datetime

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
    trade = engine.execute_trade("BTC", 1.0, 50000.0, "buy", datetime.utcnow())
    assert trade.side == "buy"
    assert engine.cash < 100000.0
    assert "BTC" in engine.positions


def test_calculate_metrics():
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    engine.equity_curve = [100000.0, 101000.0, 100500.0]
    results = engine.calculate_metrics()
    assert results.total_return > 0
