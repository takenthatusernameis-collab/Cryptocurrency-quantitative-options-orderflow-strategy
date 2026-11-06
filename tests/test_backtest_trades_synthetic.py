from __future__ import annotations

from datetime import datetime, timezone

from src.backtest.engine import BacktestEngine
from src.config import BacktestConfig, RiskConfig
from src.data.loader import DataLoader
from src.data.normalization import normalize_options_chain, normalize_orderflow
from src.features.orderflow import calculate_cumulative_delta, calculate_orderflow_imbalance


def test_synthetic_backtest_produces_trades() -> None:
    loader = DataLoader(cache=False)
    of = loader.load_orderflow("data/raw/orderflow_btcusdt_synthetic.json", venue="synthetic", symbol="BTCUSDT")
    oc = loader.load_options_chain("data/raw/options_btc_synthetic.json", venue="synthetic", underlying="BTC")
    of = normalize_orderflow(of)
    oc = normalize_options_chain(oc)

    spot = 65000.0
    cum_delta = calculate_cumulative_delta(of.trades)
    of_imb = calculate_orderflow_imbalance(of.trades)
    assert isinstance(cum_delta, float)
    assert isinstance(of_imb, float)

    engine = BacktestEngine(
        config=BacktestConfig(initial_capital=100000.0, fee_rate=0.0005, slippage_bps=1.0),
        risk_config=RiskConfig(),
    )
    now = datetime.now(timezone.utc)
    imb_threshold = 0.001
    if abs(of_imb) >= imb_threshold:
        qty = engine.calculate_position_size(spot) * min(1.0, max(0.1, abs(of_imb)))
        if qty > 0:
            side = "buy" if of_imb > 0 else "sell"
            engine.execute_trade("BTCUSDT", qty, spot, side, now)
    engine.update_equity_curve({"BTCUSDT": spot})
    mark = spot * (1.0 + (0.002 if of_imb >= 0 else -0.002))
    if "BTCUSDT" in engine.positions:
        pos = engine.positions["BTCUSDT"]
        close_side = "sell" if pos.side == "long" else "buy"
        engine.execute_trade("BTCUSDT", pos.quantity, mark, close_side, now)
    engine.update_equity_curve({"BTCUSDT": mark})
    res = engine.calculate_metrics()

    assert res.total_trades > 0
    equity_final = res.equity_curve[-1] if res.equity_curve else engine.initial_capital
    assert equity_final != engine.initial_capital
    assert res.sharpe_ratio == res.sharpe_ratio  # finite check pattern; engine may return 0
    assert res.max_drawdown >= 0.0
