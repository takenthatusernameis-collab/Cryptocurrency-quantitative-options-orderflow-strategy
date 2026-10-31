# RESULTS SUMMARY

Generated: 2026-10-31T09:53:47.393300+00:00

## Method
timeseries_windowed (window_size=50)

## Flow correlation
orderflow_imbalance vs forward return: -0.4583478199902648

## Metrics
```json
{
  "total_return": 0.008528115600650636,
  "sharpe_ratio": 2.9339455635350435,
  "sortino_ratio": 5.096959574071529,
  "max_drawdown": 0.0035523077933785254,
  "win_rate": 0.7142857142857143,
  "profit_factor": 1.7482756498436962,
  "calmar_ratio": 2.400725414770358,
  "total_trades": 20,
  "winning_trades": 5,
  "losing_trades": 2,
  "equity_final": 100852.81156006506
}
```


## Phase 4 - Walk-forward/OOS & Portfolio/Options Hedging (2026-10-31T12:06:26Z)
- Walk-forward (rolling, purge=10/embargo=5): research_state/WALKFORWARD_rolling_20261031T120626Z.json (10 windows, OOS Sharpe ~0.047 overall, mean OOS Sharpe ~0.627)
- Walk-forward (anchored): research_state/WALKFORWARD_anchored_20261031T120626Z.json
- Portfolio walk-forward (BTC/ETH): research_state/PORTFOLIO_WALKFORWARD_20261031T120626Z.json
- Options hedging demo/integration artifacts: research_state/OPTIONS_HEDGING_DEMO_20261031T120626Z.json, research_state/OPTIONS_HEDGING_INTEGRATED_20261031T120626Z.json
- All tests green: 364 passed
