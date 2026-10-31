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


## Phase 4b - Walk-forward/OOS with purge/embargo (2026-10-31T13:05:38Z)
- Walk-forward (rolling, purge=10/embargo=5): research_state/WALKFORWARD_purge_embargo_20261031T130538Z.json
  - Windows: 5, OOS return: 4.13e-05, OOS Sharpe: 0.437, OOS maxDD: 0.00010, stability_ratio: inf? reported in file, degradation computed
- Portfolio walk-forward (BTC/ETH/SOL, correlation-aware): research_state/PORTFOLIO_WALKFORWARD_20261031T130553Z.json
  - Multi-symbol correlation constraint applied, purge/embargo enforced
- Options hedging integrated into backtest path: research_state/OPTIONS_HEDGING_INTEGRATED_20261031T130606Z.json
- Tests remain green: `python -m pytest tests/ -q` passes (all existing tests)


## Phase 5: Regime OOS (2026-10-31T14:45:13Z)
- Regime-stratified walk-forward with strict purge/embargo (purge=10/embargo=5)
- Artifacts (crypto-realistic orderflow/gamma/IV/liquidity microstructure):
  - research_state/WALKFORWARD_regime_trending_20261031T144510Z.json
  - research_state/WALKFORWARD_regime_ranging_20261031T144510Z.json
  - research_state/WALKFORWARD_regime_high_vol_chop_20261031T144510Z.json
  - research_state/WALKFORWARD_regime_liquidity_thin_20261031T144513Z.json
- Module: src/backtest/regime_stress.py (generates regimes, runs per-regime walk-forward, serializes artifacts)
- IS/OOS metrics logged per window; tests extended/added as needed


## Phase 5: Portfolio Scaling (2026-10-31T15:52:43Z)
- Bottleneck removed: `src/backtest/engine.py` `PortfolioWalkForwardBacktest` called `self._compute_allocation_weights` / `self._compute_turnover` (engine.py:2343/:2359) but neither was defined, so the portfolio walk-forward silently fell back to equal weights and `turnover_cap`/`vol_target`/`risk_parity` never applied. Implemented both methods plus turnover-cap enforcement (blend-to-cap on breach) and per-run `_last_portfolio_weights` reset for determinism.
- `src/backtest/engine.py`: added `_compute_turnover`, `_train_window_vols`, `_portfolio_vol`, `_compute_allocation_weights`; `allocation_mode` (equal_weight / risk_parity / vol_target), `vol_target`, `turnover_cap`, `risk_parity` now actually applied; weights computed on train data only (no lookahead), applied out-of-sample; vol_target holds a cash buffer (sum <= 1) instead of leverage; risk_parity/equal_weight sum to 1.
- `tests/test_portfolio_scaling.py`: 14 tests (weight sums/finiteness, turnover cap enforcement breach + under-cap, no-lookahead from train window, regime stability, strict serialization allow_nan=False, determinism run-twice-identical, invalid-mode fallback).
- Artifact: research_state/PORTFOLIO_SCALING_20261031T155243Z.json (4 modes: risk_parity, risk_parity+turnover_cap, vol_target, vol_target+turnover_cap; per-window weights, turnover, OOS metrics, correlation matrices).
- Gate: `python -m pytest tests/ -q` = 380 passed, 0 failed (was 366).
