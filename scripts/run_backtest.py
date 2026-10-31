#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

from src.backtest.engine import BacktestEngine
from src.config import BacktestConfig, RiskConfig
from src.data.loader import DataLoader
from src.data.normalization import normalize_options_chain, normalize_orderflow
from src.strategy.orderflow_signal import generate_orderflow_signal


def main():
    loader = DataLoader(cache=False)
    of = loader.load_orderflow("data/raw/orderflow_btcusdt_synthetic.json", venue="synthetic", symbol="BTCUSDT")
    oc = loader.load_options_chain("data/raw/options_btc_synthetic.json", venue="synthetic", underlying="BTC")

    of = normalize_orderflow(of)
    oc = normalize_options_chain(oc)

    spot = 65000.0
    signal = generate_orderflow_signal(of, oc, spot, threshold=0.001)  # lower threshold for synthetic

    engine = BacktestEngine(
        config=BacktestConfig(initial_capital=100000.0, fee_rate=0.0005, slippage_bps=1.0),
        risk_config=RiskConfig(),
    )

    if signal["signal"] == 1 and signal["strength"] > 0:
        qty = engine.calculate_position_size(spot) * min(1.0, signal["strength"])
        if qty > 0:
            engine.execute_trade("BTCUSDT", qty, spot, "buy", datetime.now(timezone.utc))
    elif signal["signal"] == -1 and signal["strength"] > 0:
        qty = engine.calculate_position_size(spot) * min(1.0, signal["strength"])
        if qty > 0:
            engine.execute_trade("BTCUSDT", qty, spot, "sell", datetime.now(timezone.utc))

    engine.update_equity_curve({"BTCUSDT": spot})
    res = engine.calculate_metrics()

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "spot": spot,
        "signal": signal,
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
    fname = f"research_state/BACKTEST_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    with open(fname, "w") as f:
        json.dump(out, f, indent=2)
    with open("research_state/RESULTS_SUMMARY.md", "w") as f:
        f.write(f"# RESULTS SUMMARY\n\nGenerated: {out['timestamp']}\n\n## Signal\n```json\n{json.dumps(out['signal'], indent=2)}\n```\n\n## Metrics\n```json\n{json.dumps(out['metrics'], indent=2)}\n```\n")
    print(json.dumps(out["metrics"], indent=2))
    print(f"Wrote {fname}")


if __name__ == "__main__":
    main()
