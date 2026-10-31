#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import List

import numpy as np

from src.backtest.engine import BacktestEngine
from src.config import BacktestConfig, RiskConfig
from src.data.loader import DataLoader
from src.data.normalization import normalize_options_chain, normalize_orderflow
from src.data.schemas import OrderflowSnapshot, OptionsChain
from src.strategy.orderflow_signal import generate_orderflow_signal


def compute_flow_correlation(trades, window_size: int = 50) -> float:
    if not trades or len(trades) < window_size * 2:
        return 0.0
    sorted_trades = sorted(trades, key=lambda t: t.timestamp)
    of_imbs = []
    fwd_rets = []
    for i in range(0, len(sorted_trades) - window_size - 1, window_size):
        window = sorted_trades[i : i + window_size]
        buys = sum(t.size for t in window if t.side == "buy")
        sells = sum(t.size for t in window if t.side == "sell")
        total = buys + sells
        of_imb = (buys - sells) / total if total > 0 else 0.0
        of_imbs.append(of_imb)
        curr_mid = np.mean([t.price for t in window])
        next_window = sorted_trades[i + window_size : i + window_size * 2]
        if not next_window:
            break
        next_mid = np.mean([t.price for t in next_window])
        fwd_ret = (next_mid - curr_mid) / curr_mid if curr_mid != 0 else 0.0
        fwd_rets.append(fwd_ret)
    if len(of_imbs) < 2 or len(fwd_rets) < 2:
        return 0.0
    try:
        corr = np.corrcoef(of_imbs, fwd_rets)[0, 1]
        if np.isnan(corr) or np.isinf(corr):
            return 0.0
        return float(corr)
    except Exception:
        return 0.0


def main():
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
    spot_ref = 65000.0
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
            try:
                eq = engine.get_equity({"BTCUSDT": spot})
                engine.equity_curve.append(eq)
            except Exception:
                pass

    try:
        if sorted_trades:
            engine.update_equity_curve({"BTCUSDT": sorted_trades[-1].price})
    except Exception:
        pass

    res = engine.calculate_metrics()
    flow_corr = compute_flow_correlation(sorted_trades, window_size=50)

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": "timeseries_windowed",
        "window_size": window_size,
        "spot_final": sorted_trades[-1].price if sorted_trades else spot_ref,
        "flow_correlation_ofimb_vs_fwdret": flow_corr,
        "metrics": {
            "total_return": res.total_return,
            "sharpe_ratio": res.sharpe_ratio,
            "sortino_ratio": res.sortino_ratio,
            "max_drawdown": res.max_drawdown,
            "win_rate": res.win_rate,
            "profit_factor": res.profit_factor,
            "calmar_ratio": res.calmar_ratio,
            "total_trades": res.total_trades,
            "winning_trades": res.winning_trades,
            "losing_trades": res.losing_trades,
            "equity_final": res.equity_curve[-1] if res.equity_curve else engine.initial_capital,
        },
    }
    Path("research_state").mkdir(parents=True, exist_ok=True)
    fname = f"research_state/BACKTEST_TIMESERIES_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    with open(fname, "w") as f:
        json.dump(out, f, indent=2)
    summary = f"# RESULTS SUMMARY\n\nGenerated: {out['timestamp']}\n\n## Method\n{out['method']} (window_size={out['window_size']})\n\n## Flow correlation\norderflow_imbalance vs forward return: {flow_corr}\n\n## Metrics\n```json\n{json.dumps(out['metrics'], indent=2)}\n```\n"
    with open("research_state/RESULTS_SUMMARY.md", "w") as f:
        f.write(summary)
    print(json.dumps(out["metrics"], indent=2))
    print(f"flow_correlation={flow_corr}")
    print(f"Wrote {fname}")


if __name__ == "__main__":
    main()
