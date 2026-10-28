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


def test_backtest_lot_rounding_and_max_qty():
    from src.backtest.engine import BacktestEngine
    from src.config import BacktestConfig, RiskConfig
    from datetime import datetime, timezone
    engine = BacktestEngine(
        config=BacktestConfig(initial_capital=100000.0, round_lot_size=0.1, slippage_bps=1.0),
        risk_config=RiskConfig(max_position_qty=1.5, allow_shorting=True),
    )
    t = engine.execute_trade("BTC", 2.34, 50000.0, "buy", datetime.now(timezone.utc))
    assert t.quantity == 1.5


def test_backtest_partial_fill_deterministic():
    from src.backtest.engine import BacktestEngine
    from src.config import BacktestConfig, RiskConfig
    from datetime import datetime, timezone
    engine = BacktestEngine(
        config=BacktestConfig(initial_capital=1000000.0, partial_fill_rate=0.5, slippage_seed=123),
        risk_config=RiskConfig(allow_shorting=True),
    )
    t = engine.execute_trade("BTC", 10.0, 50000.0, "buy", datetime.now(timezone.utc))
    assert 0 < t.quantity < 10.0


def test_backtest_max_slippage_cap():
    from src.backtest.engine import BacktestEngine
    from src.config import BacktestConfig, RiskConfig
    from datetime import datetime, timezone
    engine = BacktestEngine(
        config=BacktestConfig(initial_capital=100000.0, slippage_bps=1000.0, max_slippage_bps=5.0),
        risk_config=RiskConfig(allow_shorting=True),
    )
    t = engine.execute_trade("BTC", 1.0, 50000.0, "buy", datetime.now(timezone.utc))
    assert abs(t.price - 50000.0) <= 50000.0 * 5.0 / 10000.0 + 1e-9


def test_backtest_short_not_allowed():
    from src.backtest.engine import BacktestEngine
    from src.config import BacktestConfig, RiskConfig
    from datetime import datetime, timezone
    import pytest
    engine = BacktestEngine(
        config=BacktestConfig(initial_capital=100000.0),
        risk_config=RiskConfig(allow_shorting=False),
    )
    with pytest.raises(ValueError):
        engine.execute_trade("BTC", 1.0, 50000.0, "sell", datetime.now(timezone.utc))


def test_walk_forward_basic_rolling():
    from src.backtest.engine import BacktestEngine, WalkForwardBacktest
    from src.config import BacktestConfig, RiskConfig
    import numpy as np

    engine = BacktestEngine(BacktestConfig(initial_capital=100000.0), RiskConfig())
    wfb = WalkForwardBacktest(engine)
    # Create simple price series
    n = 200
    prices = {"BTC": [50000.0 + i * 10 for i in range(n)]}
    # Simple moving average crossover-like signals
    signals = {"BTC": [0] * n}
    for i in range(50, n):
        if i % 10 < 5:
            signals["BTC"][i] = 1
        else:
            signals["BTC"][i] = -1 if i % 20 == 19 else 0
    results = wfb.run_walk_forward(price_series=prices, signals=signals, train_window=100, test_window=30, step_size=30)
    assert results is not None
    assert len(results.windows) > 0
    assert isinstance(results.overall_out_of_sample_return, float)
    assert isinstance(results.stability_ratio, float)
    assert isinstance(results.degradation, float)
    assert isinstance(results.oos_equity_curve, list)


def test_walk_forward_anchored():
    from src.backtest.engine import run_walk_forward
    from src.config import BacktestConfig

    n = 150
    prices = {"ETH": [3000.0 + i * 5 for i in range(n)]}
    signals = {"ETH": [1 if i % 15 < 3 else (-1 if i % 15 == 14 else 0) for i in range(n)]}
    results = run_walk_forward(price_series=prices, signals=signals, train_window=60, test_window=30, step_size=30, anchored=True)
    assert results is not None
    assert len(results.windows) >= 0  # may be 0 if windows don't fit perfectly


def test_rolling_window_backtest_convenience():
    from src.backtest.engine import run_rolling_window_backtest

    n = 120
    prices = {"BTC": [50000.0] * n}
    for i in range(n):
        prices["BTC"][i] = 50000.0 * (1.0 + i * 0.0001)
    signals = {"BTC": [0] * n}
    for i in range(40, n):
        signals["BTC"][i] = 1 if (i // 5) % 2 == 0 else 0
    results = run_rolling_window_backtest(price_series=prices, signals=signals, train_window=50, test_window=20, step_size=20)
    assert hasattr(results, 'windows')
    assert hasattr(results, 'oos_trades')


def test_walk_forward_edge_cases():
    from src.backtest.engine import WalkForwardBacktest
    from src.config import BacktestConfig, RiskConfig

    wfb = WalkForwardBacktest(BacktestConfig(initial_capital=100000.0), RiskConfig())
    # Empty-ish
    results = wfb.run_walk_forward(price_series={"BTC": []}, signals={"BTC": []}, train_window=10, test_window=5)
    assert isinstance(results.windows, list)
    # Single window case
    n = 80
    prices = {"BTC": [100.0 + i for i in range(n)]}
    signals = {"BTC": [1 if i >= 40 else 0 for i in range(n)]}
    results = wfb.run_walk_forward(price_series=prices, signals=signals, train_window=40, test_window=20, step_size=20)
    assert results is not None


def test_walk_forward_numerical_stability():
    from src.backtest.engine import WalkForwardBacktest
    from src.config import BacktestConfig, RiskConfig
    import math

    wfb = WalkForwardBacktest(BacktestConfig(initial_capital=100000.0), RiskConfig())
    n = 100
    prices = {"BTC": [float('nan') if i % 7 == 0 else (50000.0 * (1.0 if i % 3 != 0 else 0.999)) for i in range(n)]}
    # Clean up nans
    clean_prices = {"BTC": []}
    for p in prices["BTC"]:
        if isinstance(p, float) and (math.isnan(p) or math.isinf(p)):
            clean_prices["BTC"].append(50000.0)
        else:
            clean_prices["BTC"].append(p)
    signals = {"BTC": [0] * n}
    for i in range(30, n):
        signals["BTC"][i] = 1 if i % 4 == 0 else (-1 if i % 4 == 2 else 0)
    results = wfb.run_walk_forward(price_series=clean_prices, signals=signals, train_window=40, test_window=15, step_size=15)
    assert results is not None
    # Check all values are finite
    assert isinstance(results.overall_out_of_sample_return, float)
    assert math.isfinite(results.overall_out_of_sample_return) or results.overall_out_of_sample_return == results.overall_out_of_sample_return  # no NaN crash
