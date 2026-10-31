# DURABLE HANDOFF - 2026-10-31T09:09:13Z
Repo: Cryptocurrency-quantitative-options-orderflow-strategy
Goal: Stop checkpoint-only loops. Force heavy, measurable implementation work on the crypto options orderflow strategy.

## STATUS (verified 2026-10-31T09:09:13Z)
- 360 tests pass (`python -m pytest tests/ -q`). No failing tests — code is green.
- Phase 1 (data ingestion): DONE — `src/data/loader.py`, `schemas.py`, `validators.py`, `tests/test_data_loader_and_validation.py`, synthetic raw data (`data/raw/orderflow_btcusdt_synthetic.json` 1000 trades, `data/raw/options_btc_synthetic.json` 30 quotes), `research_state/DATA_INVENTORY.md`.
- Phase 2 (orderflow features): DONE — `src/features/orderflow.py` (+ liquidity, gamma_exposure, iv_surface, volatility, options_pricing), `src/pipelines/build_features.py`, `tests/test_features.py`, `data/processed/features_latest.json` materialized.
- Phase 3 (strategy + backtest): PARTIAL — `src/backtest/engine.py`, `src/strategy/orderflow_signal.py`, `scripts/run_backtest.py`, `scripts/run_backtest_synthetic.py`, `research_state/BACKTEST_*.json` + `RESULTS_SUMMARY.md` exist, BUT metrics are TRIVIAL: 1 trade, `win_rate=0.0`, `sharpe_ratio=0.0`, `total_return≈0`. Single-snapshot signal (`of_imb > 0.01` required) fires at most once. DATA IS NOT MISSING — do NOT redo Phase 1; the bottleneck is the single-bar signal/backtest driver.

## BOTTLENECK REMOVED / IDENTIFIED
Blocker: backtest runs one trade on one snapshot → trivial, non-publishable metrics. Fix: convert the backtest into a time-ordered walk through the orderflow (multiple bars/windows, multiple trades, position sizing, SL/TP exits, equity curve, flow-correlation) so `BACKTEST_*.json` contains real metrics (multiple trades, non-zero win rate/sharpe/drawdown).

## NEXT FOCUS CAMPAIGN (execute in strict order — heavy work, no skipping)
### Phase 3 completion: Time-series backtest with real metrics
1. **Time-ordered backtest driver**: Modify/extend `scripts/run_backtest.py` (or add `scripts/run_backtest_timeseries.py`) to iterate the orderflow trades sorted by timestamp in windows (e.g. 50-trade tumbling windows), compute orderflow signal per window, size position via `engine.calculate_position_size`, execute buy/sell with SL/TP, call `update_equity_curve` per window, then `calculate_metrics`. Must produce multiple trades (>1) and a non-degenerate equity curve.
2. **Flow-correlation metric**: Compute correlation between orderflow imbalance / cumulative delta and forward returns; add to backtest output. If uncomputable, fix the driver, not the data.
3. **Run baseline**: Execute the time-series backtest headlessly. Write `research_state/BACKTEST_TIMESERIES_<UTC>.json` with real metrics and update `research_state/RESULTS_SUMMARY.md` (signal + metrics blocks).
4. **Tests**: Add `tests/test_backtest_timeseries.py` covering multi-trade execution, SL/TP exits, determinism (same seed → same result), and non-trivial metrics (total_trades > 1).
5. **Feature materialization (optional but recommended)**: `src/pipelines/build_features.py` already materializes `data/processed/`; ensure a features manifest accompanies the backset run.

### FIRST ACTION (do this immediately, no debate)
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q

# 2) Inspect current trivial metrics
cat research_state/RESULTS_SUMMARY.md

# 3) Implement time-ordered backtest driver (edit scripts/run_backtest.py or add run_backtest_timeseries.py)
#    - sort of.trades by timestamp
#    - tumbling windows of ~50 trades
#    - generate_orderflow_signal per window -> execute_trade with SL/TP
#    - update_equity_curve per window -> calculate_metrics
#    - add flow-correlation (of_imb vs forward price change)
#    - write research_state/BACKTEST_TIMESERIES_<UTC>.json + update RESULTS_SUMMARY.md

# 4) Add tests/test_backtest_timeseries.py (multi-trade, determinism, non-trivial metrics)

# 5) Verify
python -m pytest tests/ -q
python scripts/run_backtest_timeseries.py   # or run_backtest.py
cat research_state/RESULTS_SUMMARY.md
```
After the time-series backtest produces real metrics, do NOT declare done until `total_trades > 1` and metrics are non-degenerate (win_rate/sharpe/drawdown computable and non-trivial).

## HARD CONSTRAINTS
- **No more checkpoint spam**: Do not commit unless you added executable code, tests, data artifacts, or passing validation.
- **Heavy work required**: Prefer implementing over summarizing. If tempted to write another status update, write code instead.
- **Deterministic**: All scripts must be runnable headlessly with clear args; write artifacts to disk.
- **Fail-forward**: Missing data is a task to create fixtures/loaders, not an excuse to stop.
- **Single focus**: Complete Phase 3 (time-series backtest with real metrics) fully before any speculative new phase. Do not jump ahead.
- **Every session must ship**: new module, tests, data loader, features, backtest artifact, or passing checks.

## SUCCESS CRITERIA (must hit before next handoff)
- [ ] `research_state/BACKTEST_TIMESERIES_<UTC>.json` exists with real metrics (total_trades > 1)
- [ ] `research_state/RESULTS_SUMMARY.md` updated with signal + non-trivial metrics (win_rate, sharpe_ratio, max_drawdown computable)
- [ ] `tests/test_backtest_timeseries.py` added with >=1 passing test (multi-trade + determinism)
- [ ] `python -m pytest tests/ -q` fully green
- [ ] Flow-correlation (orderflow vs forward return) computed and reported
