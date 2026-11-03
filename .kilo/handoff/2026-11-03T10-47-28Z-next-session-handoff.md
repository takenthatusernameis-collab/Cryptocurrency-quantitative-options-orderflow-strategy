# DURABLE HANDOFF | 2026-11-03T10:47:28Z
Repository: `Cryptocurrency-quantitative-options-orderflow-strategy`
State: Empty working tree. Only `chore(kilo): checkpoint agent session` commits exist. No source code, configs, data schemas, or strategy logic present.

## Bottlenecks To Remove (Do First)
- [ ] **Bootstrap gap** - No project structure. Create a minimal, testable scaffold before any strategy work.
- [ ] **Data gap** - No defined data sources for crypto options/orderflow. Pick concrete sources and schemas.
- [ ] **Infra gap** - No backtesting, logging, or risk controls. These must exist before iterating on signals.
- [ ] **Context gap** - No existing decisions. Treat this as greenfield and document assumptions in code/config.

## Next Focus Campaign (Cannot Avoid Heavy Work)
Mission: Bootstrap an end-to-end, backtestable skeleton for a crypto options orderflow quantitative strategy. Prioritize deterministic, testable components over premature optimization.

### Phase 1: Scaffold (P0)
- [ ] Create base layout: `src/`, `configs/`, `data/`, `tests/`, `scripts/`, `notebooks/`
- [ ] Add project config (`pyproject.toml` or `package.json` depending on chosen stack). Default to Python + `pandas`/`numpy`/`pyarrow` unless repo conventions emerge.
- [ ] Add `README.md` with setup, data requirements, and quickstart
- [ ] Add `.env.example` for API keys/endpoints
- [ ] Add basic linting/type checking config

### Phase 2: Data Model & Ingestion (P0)
- [ ] Define schemas: options chain, trades, orderbook, liquidations, open interest, greeks, funding (as available)
- [ ] Implement connectors for at least one viable source (e.g., Deribit, OKX, Binance) with rate limiting/retries
- [ ] Normalize to unified `DataFrame`/parquet with UTC timestamps and symbol normalization
- [ ] Add data validation and sample fixtures for offline tests

### Phase 3: Orderflow Features & Signals (P1)
- [ ] Implement core features: trade flow imbalance, CVD, signed volume, book imbalance, delta-adjusted flow
- [ ] Compute surface/greeks context where available (or use market data + approximations)
- [ ] Define candidate signals with clear hypotheses and unit tests

### Phase 4: Backtester + Risk (P0)
- [ ] Event/time-based backtester with commission/slippage, position sizing, and PnL attribution
- [ ] Risk controls: max notional, delta/gamma limits, drawdown stops, position caps
- [ ] Metrics: Sharpe, Sortino, max DD, win rate, turnover, fee drag
- [ ] Reproducible runs via config files

### Phase 5: Validation (P1)
- [ ] Unit tests for features, normalization, and PnL
- [ ] Integration test with small fixture dataset
- [ ] Deterministic run artifact (parquet + metrics JSON)

## Concrete First Action (Start Here)
1. `git status` and inspect any hidden files (`ls -la`)
2. Decide stack and scaffold files above
3. Commit scaffold with a clear message
4. Create a minimal fixture dataset and a smoke test to prove the pipeline runs end-to-end

## Notes For Next Agent
- Do not over-engineer abstractions. Build vertical slices that produce testable outputs.
- All timestamps must be UTC. All monetary/notional values must be explicit.
- Prefer offline fixtures first; live API calls must be behind feature flags.
- Document assumptions in `configs/` and update `README.md` as you go.
- Treat "no explicit directions" as mandate to execute the campaign above with heavy, verifiable work.
