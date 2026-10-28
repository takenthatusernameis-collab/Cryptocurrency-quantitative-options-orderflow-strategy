"""Numeric regression tests for backtest engine correctness."""

from datetime import datetime, timezone
from math import isinf

from src.backtest.engine import BacktestEngine
from src.config import BacktestConfig, RiskConfig


def test_short_equity_math_on_price_move():
    config = BacktestConfig(initial_capital=100000.0, fee_rate=0.0, slippage_bps=0)
    engine = BacktestEngine(config)
    # Open short within limit: 0.2 BTC @ 50000 = 10000 notional (10%)
    engine.execute_trade("BTC", 0.2, 50000.0, "sell", datetime.now(timezone.utc))
    assert engine.positions["BTC"].side == "short"
    # Cash credited with proceeds: 100000 + 10000 = 110000.
    # Equity = cash - qty*current_price (liability) = 110000 - 0.2*49000 = 100200
    eq = engine.get_equity({"BTC": 49000.0})
    assert abs(eq - 100200.0) < 1e-9


def test_stop_loss_trigger_on_long():
    config = BacktestConfig(initial_capital=100000.0, fee_rate=0.0, slippage_bps=0)
    risk = RiskConfig(stop_loss_pct=0.02)
    engine = BacktestEngine(config, risk)
    engine.execute_trade("BTC", 1.0, 50000.0, "buy", datetime.now(timezone.utc))
    # Price drops below stop
    trades = engine.check_risk_controls({"BTC": 48900.0}, datetime.now(timezone.utc))
    assert len(trades) >= 1
    assert "BTC" not in engine.positions


def test_take_profit_trigger_on_short():
    config = BacktestConfig(initial_capital=100000.0, fee_rate=0.0, slippage_bps=0)
    risk = RiskConfig(take_profit_pct=0.04)
    engine = BacktestEngine(config, risk)
    engine.execute_trade("BTC", 0.2, 50000.0, "sell", datetime.now(timezone.utc))
    # Price drops to hit take profit for short (TP at entry*(1-take_profit_pct))
    trades = engine.check_risk_controls({"BTC": 47900.0}, datetime.now(timezone.utc))
    assert len(trades) >= 1
    assert "BTC" not in engine.positions


def test_profit_factor_inf_when_no_losses():
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    engine.equity_curve = [100000.0, 101000.0, 102000.0]
    # Simulate closed winning trades
    from src.backtest.engine import Trade
    engine.trades = [
        Trade("BTC", 1.0, 50000.0, "sell", datetime.now(timezone.utc), commission=0.0, pnl=500.0, is_win=True),
        Trade("BTC", 1.0, 50000.0, "sell", datetime.now(timezone.utc), commission=0.0, pnl=500.0, is_win=True),
    ]
    res = engine.calculate_metrics()
    assert isinf(res.profit_factor)
    assert res.profit_factor > 0


def test_max_position_pct_enforced_on_short():
    config = BacktestConfig(initial_capital=100000.0)
    risk = RiskConfig(max_position_pct=0.1)
    engine = BacktestEngine(config, risk)
    # 0.3 BTC @ 50000 = 15000 notional > 10% of 100000
    try:
        engine.execute_trade("BTC", 0.3, 50000.0, "sell", datetime.now(timezone.utc))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_short_cover_realizes_pnl_to_cash():
    config = BacktestConfig(initial_capital=100000.0, fee_rate=0.0, slippage_bps=0)
    engine = BacktestEngine(config)
    # Open short 0.2 BTC @ 50000 -> cash = 110000
    engine.execute_trade("BTC", 0.2, 50000.0, "sell", datetime.now(timezone.utc))
    assert abs(engine.cash - 110000.0) < 1e-9
    # Cover 0.2 BTC @ 49000 -> cost = 9800; cash = 110000 - 9800 = 100200; pnl = (50000-49000)*0.2 = 200
    trade = engine.execute_trade("BTC", 0.2, 49000.0, "buy", datetime.now(timezone.utc))
    assert abs(trade.pnl - 200.0) < 1e-9
    assert abs(engine.cash - 100200.0) < 1e-9
    assert "BTC" not in engine.positions


def test_long_equity_math_on_price_move():
    config = BacktestConfig(initial_capital=100000.0, fee_rate=0.0, slippage_bps=0)
    engine = BacktestEngine(config)
    # Open long 1.0 BTC @ 50000 -> cash = 50000
    engine.execute_trade("BTC", 1.0, 50000.0, "buy", datetime.now(timezone.utc))
    assert abs(engine.cash - 50000.0) < 1e-9
    # Price rises to 51000: equity = 50000 + 1*51000 = 101000
    eq = engine.get_equity({"BTC": 51000.0})
    assert abs(eq - 101000.0) < 1e-9


def test_max_drawdown_limit_closes_all_positions():
    config = BacktestConfig(initial_capital=100000.0, fee_rate=0.0, slippage_bps=0)
    risk = RiskConfig(max_drawdown_limit=0.05)
    engine = BacktestEngine(config, risk)
    engine.execute_trade("BTC", 1.0, 50000.0, "buy", datetime.now(timezone.utc))
    # Equity at entry = 50000 (cash) + 50000 (position) = 100000, peak=100000
    # Drop to 94000 -> drawdown = 6% > 5% -> close all
    triggered = engine.check_risk_controls({"BTC": 44000.0}, datetime.now(timezone.utc))
    assert len(triggered) >= 1
    assert "BTC" not in engine.positions


def test_profit_factor_zero_when_no_trades():
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    res = engine.calculate_metrics()
    assert res.profit_factor == 0.0
    assert res.winning_trades == 0
    assert res.losing_trades == 0


def test_calmar_ratio_zero_when_no_drawdown():
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    engine.equity_curve = [100000.0, 110000.0, 120000.0]
    res = engine.calculate_metrics()
    assert res.calmar_ratio == 0.0
    assert res.max_drawdown == 0.0


def test_metrics_non_finite_safe():
    config = BacktestConfig(initial_capital=100000.0)
    engine = BacktestEngine(config)
    engine.equity_curve = [float("nan"), float("inf"), 100000.0]
    res = engine.calculate_metrics()
    assert res.total_return == 0.0
    assert res.sharpe_ratio == 0.0
    assert res.sortino_ratio == 0.0
    assert res.max_drawdown == 0.0


def test_position_size_respects_max_position_pct():
    config = BacktestConfig(initial_capital=100000.0)
    risk = RiskConfig(max_position_pct=0.1, stop_loss_pct=0.02)
    engine = BacktestEngine(config, risk)
    qty = engine.calculate_position_size(50000.0)
    # max_capital = 100000 * 0.1 = 10000; qty_by_capital = 10000/50000 = 0.2
    # risk_amount = 100000 * 0.02 = 2000; qty_by_risk = 2000/50000 = 0.04
    # min = 0.04
    assert abs(qty - 0.04) < 1e-9
