"""Tests for time-series backtesting."""
from datetime import datetime, timezone
from pathlib import Path

from src.backtest.engine import BacktestEngine
from src.config import BacktestConfig, RiskConfig
from src.data.loader import DataLoader
from src.data.normalization import normalize_options_chain, normalize_orderflow
from src.data.schemas import OrderflowSnapshot
from src.strategy.orderflow_signal import generate_orderflow_signal


def test_timeseries_multi_trade_execution():
    loader = DataLoader(cache=False)
    of = loader.load_orderflow("data/raw/orderflow_btcusdt_synthetic.json", venue="synthetic", symbol="BTCUSDT")
    oc = loader.load_options_chain("data/raw/options_btc_synthetic.json", venue="synthetic", underlying="BTC")
    of = normalize_orderflow(of)
    oc = normalize_options_chain(oc)

    sorted_trades = sorted(of.trades, key=lambda t: t.timestamp)
    engine = BacktestEngine(
        config=BacktestConfig(initial_capital=100000.0, fee_rate=0.0005, slippage_bps=1.0),
        risk_config=RiskConfig(),
    )

    window_size = 50
    trades_executed = 0
    for i in range(0, len(sorted_trades), window_size):
        window_trades = sorted_trades[i : i + window_size]
        if len(window_trades) < 10:
            continue
        window_of = OrderflowSnapshot(
            symbol=of.symbol,
            venue=of.venue,
            trades=window_trades,
            liquidations=[],
            funding_rates=[],
            timestamp=window_trades[-1].timestamp,
        )
        spot = window_trades[-1].price
        try:
            signal = generate_orderflow_signal(window_of, oc, spot, threshold=0.001)
        except Exception:
            continue
        if signal["signal"] == 1 and signal["strength"] > 0:
            qty = engine.calculate_position_size(spot) * min(1.0, signal["strength"])
            if qty > 0 and engine.cash > 100:
                try:
                    engine.execute_trade("BTCUSDT", qty, spot, "buy", window_trades[-1].timestamp)
                    trades_executed += 1
                except Exception:
                    pass
        elif signal["signal"] == -1 and signal["strength"] > 0:
            qty = engine.calculate_position_size(spot) * min(1.0, signal["strength"])
            if qty > 0:
                try:
                    engine.execute_trade("BTCUSDT", qty, spot, "sell", window_trades[-1].timestamp)
                    trades_executed += 1
                except Exception:
                    pass
        try:
            engine.update_equity_curve({"BTCUSDT": spot})
        except Exception:
            pass

    res = engine.calculate_metrics()
    assert res.total_trades > 1
    assert trades_executed >= 1


def test_timeseries_determinism():
    loader = DataLoader(cache=False)
    of = loader.load_orderflow("data/raw/orderflow_btcusdt_synthetic.json", venue="synthetic", symbol="BTCUSDT")
    oc = loader.load_options_chain("data/raw/options_btc_synthetic.json", venue="synthetic", underlying="BTC")
    of = normalize_orderflow(of)
    oc = normalize_options_chain(oc)
    sorted_trades = sorted(of.trades, key=lambda t: t.timestamp)

    def run_once():
        engine = BacktestEngine(
            config=BacktestConfig(initial_capital=100000.0, fee_rate=0.0005, slippage_bps=1.0),
            risk_config=RiskConfig(),
        )
        window_size = 50
        for i in range(0, len(sorted_trades), window_size):
            window_trades = sorted_trades[i : i + window_size]
            if len(window_trades) < 10:
                continue
            window_of = OrderflowSnapshot(
                symbol=of.symbol,
                venue=of.venue,
                trades=window_trades,
                liquidations=[],
                funding_rates=[],
                timestamp=window_trades[-1].timestamp,
            )
            spot = window_trades[-1].price
            try:
                signal = generate_orderflow_signal(window_of, oc, spot, threshold=0.001)
            except Exception:
                continue
            if signal["signal"] == 1 and signal["strength"] > 0:
                qty = engine.calculate_position_size(spot) * min(1.0, signal["strength"])
                if qty > 0 and engine.cash > 100:
                    try:
                        engine.execute_trade("BTCUSDT", qty, spot, "buy", window_trades[-1].timestamp)
                    except Exception:
                        pass
            elif signal["signal"] == -1 and signal["strength"] > 0:
                qty = engine.calculate_position_size(spot) * min(1.0, signal["strength"])
                if qty > 0:
                    try:
                        engine.execute_trade("BTCUSDT", qty, spot, "sell", window_trades[-1].timestamp)
                    except Exception:
                        pass
            try:
                engine.update_equity_curve({"BTCUSDT": spot})
            except Exception:
                pass
        return engine.calculate_metrics()

    r1 = run_once()
    r2 = run_once()
    assert abs(r1.total_return - r2.total_return) < 1e-10
    assert r1.total_trades == r2.total_trades
