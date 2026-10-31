#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

from src.backtest.engine import BacktestEngine
from src.config import BacktestConfig, RiskConfig
from src.data.loader import DataLoader
from src.data.normalization import normalize_options_chain, normalize_orderflow
from src.features.orderflow import calculate_cumulative_delta, calculate_orderflow_imbalance
from src.features.volatility import calculate_max_pain, calculate_put_call_ratio, calculate_iv_skew


def main():
    loader = DataLoader(cache=False)
    of = loader.load_orderflow("data/raw/orderflow_btcusdt_synthetic.json", venue="synthetic", symbol="BTCUSDT")
    oc = loader.load_options_chain("data/raw/options_btc_synthetic.json", venue="synthetic", underlying="BTC")

    of = normalize_orderflow(of)
    oc = normalize_options_chain(oc)

    spot = 65000.0
    cum_delta = calculate_cumulative_delta(of.trades)
    of_imb = calculate_orderflow_imbalance(of.trades)
    pcr = calculate_put_call_ratio(oc.quotes)
    iv_skew = calculate_iv_skew(oc.quotes, spot)
    max_pain = calculate_max_pain(oc)

    engine = BacktestEngine(
        config=BacktestConfig(initial_capital=100000.0, fee_rate=0.0005, slippage_bps=1.0),
        risk_config=RiskConfig(),
    )

    # Simple signal: follow orderflow if strong
    if cum_delta > 0 and of_imb > 0.01:
        qty = engine.calculate_position_size(spot) * min(1.0, abs(of_imb))
        if qty > 0 and engine.cash > spot * qty * 1.01:
            engine.execute_trade("BTCUSDT", qty, spot, "buy", datetime.now(timezone.utc))
    elif cum_delta < 0 and of_imb < -0.01:
        qty = engine.calculate_position_size(spot) * min(1.0, abs(of_imb))
        if qty > 0:
            engine.execute_trade("BTCUSDT", qty, spot, "sell", datetime.now(timezone.utc))
    engine.update_equity_curve({"BTCUSDT": spot})
    res = engine.calculate_metrics()

    out = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "spot": spot,
        "orderflow": {"trades": len(of.trades), "cum_delta": cum_delta, "imbalance": of_imb},
        "options": {"quotes": len(oc.quotes), "pcr": pcr, "iv_skew": iv_skew, "max_pain": max_pain},
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
    fname = f"research_state/BACKTEST_SYNTHETIC_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    with open(fname, "w") as f:
        json.dump(out, f, indent=2)
    with open("research_state/RESULTS_SUMMARY.md", "w") as f:
        f.write(f"# RESULTS SUMMARY\n\nGenerated: {out['timestamp']}\n\n## Metrics\n```json\n{json.dumps(out['metrics'], indent=2)}\n```\n")
    print(json.dumps(out["metrics"], indent=2))
    print(f"Wrote {fname}")


if __name__ == "__main__":
    main()
