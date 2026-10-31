# DURABLE HANDOFF - 2026-10-31T07:12:41Z
Repo: Cryptocurrency-quantitative-options-orderflow-strategy
Goal: Stop checkpoint-only loops. Force heavy, measurable implementation work.

## PRIORITY 1: Remove bottlenecks (do first)
- [ ] **Inventory reality**: Enumerate `data/` fully (formats, sizes, coverage). If empty/missing critical feeds, do not wait - generate realistic synthetic fixtures and log assumptions.
- [ ] **Schema lock-in**: Define canonical schemas for options trades/orderbook, perps/spot, funding/liquidations in `src/data/schema.py` (or equivalent). Validate on load.
- [ ] **Kill passivity**: Any session that ends with only "chore(kilo): checkpoint" is wasteful. Every session must produce at least one of: new module, tests, data loader, features, backtest artifact, or passing checks.

## NEXT FOCUS CAMPAIGN (execute in strict order)
### Phase 1: Data ingestion (BLOCKING, heavy)
1. **Audit**: `find data -type f | sort` and inspect headers/samples for each file. Document in `research_state/DATA_INVENTORY.md`.
2. **Loader**: Implement a robust loader in `src/data/loader.py` with timestamp normalization (UTC), exchange normalization, validation, and caching.
3. **Contracts**: Add `src/data/validators.py` + unit tests in `tests/test_data_*.py`. Fail fast on schema drift.
4. **Fixture**: If no usable options orderflow exists, write `scripts/generate_synthetic_orderflow.py` to produce realistic trades/orderbook snapshots and wire it to tests.

### Phase 2: Orderflow features (CORE ALPHA, heavy)
1. **Microstructure**: Implement signed volume, trade aggression (aggressive/passive), VWAP, orderflow imbalance, delta/flow toxicity in `src/features/orderflow.py`.
2. **Options-aware**: Add delta/gamma/vega exposure proxies, OI change, liquidity, spread/impact in `src/features/options_flow.py`.
3. **Pipeline**: Create `src/pipelines/build_features.py` that materializes features to `data/processed/` with deterministic keys and manifest.
4. **Tests**: Cover edge cases (crossing, partial fills) in `tests/test_features_*.py`.

### Phase 3: Strategy + backtest (VALIDATION, heavy)
1. **Signal**: Implement a first-pass signal in `src/strategy/orderflow_signal.py` (hypothesis-driven, simple first, extensible). Must read only processed features.
2. **Engine**: Build/extend backtester in `src/backtest/` with fees/slippage, position sizing, risk limits, and PnL attribution.
3. **Run**: Execute a baseline backtest via `scripts/run_backtest.py`. Write results to `research_state/BACKTEST_*.json` + summary to `research_state/RESULTS_SUMMARY.md`.
4. **Metrics**: Compute Sharpe, drawdown, hit rate, turnover, flow-correlation. If metrics are trivial/uncomputable due to missing data, fix Phase 1 first.

## FIRST ACTION (do this immediately, no debate)
```bash
# 1) See what actually exists
find . -type f \( -path "./data/*" -o -path "./src/*" -o -path "./scripts/*" -o -path "./config/*" \) | sort | head -80

# 2) Inspect data reality
find data -type f 2>&1 | head -40
ls -la data/ 2>&1

# 3) Understand existing code entrypoints
grep -rn "def main\|if __name__" src scripts 2>&1 | head -30
```
After inventory, write `research_state/DATA_INVENTORY.md` with concrete paths/sizes/formats. Then implement the loader. Do not stop at inventory.

## HARD CONSTRAINTS
- **No more checkpoint spam**: Do not commit unless you added executable code, tests, data artifacts, or passing validation.
- **Heavy work required**: Prefer implementing over summarizing. If tempted to write another status update, write code instead.
- **Deterministic**: All scripts must be runnable headlessly with clear args; write artifacts to disk.
- **Fail-forward**: Missing data is a task to create fixtures/loaders, not an excuse to stop.
- **Single focus**: Complete Phase 1 fully before moving to Phase 2. Do not jump ahead speculatively.

## SUCCESS CRITERIA (must hit)
- [ ] `research_state/DATA_INVENTORY.md` exists with actionable findings
- [ ] Working data loader + validators with >=1 passing test
- [ ] At least one processed feature set materialized OR synthetic fixtures generated and used
- [ ] A baseline backtest runs and produces `research_state/BACKTEST_*.json` with real metrics
