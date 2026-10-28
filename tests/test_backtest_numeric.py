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
    # Price falls to 49000: equity = cash + qty*(entry - current) = (100000+10000) + 0.2*(50000-49000)=110000 + 200 = 110200
    eq = engine.get_equity({"BTC": 49000.0})
    assert abs(eq - 110200.0) < 1e-9


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
