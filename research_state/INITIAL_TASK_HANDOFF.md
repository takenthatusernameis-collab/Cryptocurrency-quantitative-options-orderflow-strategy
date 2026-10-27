# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-27T22:44:42Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

## Initial Task Message (for next agentic session)

**PRIORITY: BUILD THE CRYPTOCURRENCY QUANTITATIVE OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, NO PLACEHOLDERS**

You are tasked with building the cryptocurrency quantitative options orderflow strategy from scratch, prioritized by the project name. The strategy must ingest crypto options chain data and orderflow (trades, liquidations, funding), compute quantitative features (gamma exposure, delta-adjusted flow, IV skew, put/call ratio, max pain, orderflow imbalance), generate tradable signals, and backtest them with realistic execution, fees, slippage, and risk metrics.

Focus on heavy engineering work with no placeholders — implement production-quality, tested Python code that can process real options/orderflow data. Do not stop at scaffolding.

### Immediate Objectives:
1. **Data Layer**: Create modules for options chain ingestion (Deribit/OKX/Binance options), orderflow data (trades, liquidations), and normalization across venues
2. **Feature Engineering**: Implement gamma exposure (GEX), delta-adjusted flow, volatility skew analysis, put/call ratios, max pain, and orderflow imbalance metrics
3. **Signal Generation**: Build quantitative signals combining orderflow toxicity, dealer positioning, and volatility surface features
4. **Backtesting**: Create a robust backtesting harness with realistic execution, fees, slippage, and performance metrics (Sharpe, Sortino, max drawdown)
5. **Infrastructure**: Add configuration, logging, data validation, and diagnostics

### Requirements:
- Write clean, tested Python code (follow existing patterns)
- Add unit tests for core logic — no placeholder tests
- Ensure all tests pass
- Make meaningful commits as you progress
- Focus on end-to-end functionality over perfection

**Do not stop at scaffolding. Implement working, testable code that can process real options/orderflow data.**

## Bottlenecks Removed

- Restored the 4 missing CI test files deleted in commit 59b5b04: `tests/test_controller_progress_accounting.py`, `tests/test_workflow_diagnostics_scanner.py`, `tests/test_nonfinite_result_serialization.py`, `tests/test_campaign_resume.py`. The diagnostics-only activation step now has tests to run so CI is not blocked.
- Created `scripts/controller_progress.py` for workflow checkpoint validation (enables checkpoint/persistence gating).

## Next Focus Campaign (Execute in Order — MANDATORY)

Future agents must not avoid this campaign. Every phase below is required before the strategy is considered functional.

### Phase 1: Foundation (Critical Path) — MUST COMPLETE FIRST
- [ ] **Project structure**: Create `src/`, `data/`, `config/`, `notebooks/` directories with proper `__init__.py` files
- [ ] **Configuration**: Build config system for API keys, venues, parameters (pydantic/dataclass)
- [ ] **Data schemas**: Define Pydantic models for options chains, trades, orderbooks, candles

### Phase 2: Data Ingestion (Heavy Work)
- [ ] **Options data**: Implement connectors for crypto options (start with public APIs, add structure for authenticated)
- [ ] **Orderflow data**: Ingest trades, liquidations, funding rates
- [ ] **Normalization**: Unified data models with timestamps, symbols, moneyness calculations

### Phase 3: Quantitative Signals (Core Alpha)
- [ ] **Gamma Exposure (GEX)**: Calculate dealer gamma exposure by strike/expiry
- [ ] **Volatility Surface**: IV skew, term structure, smile analysis
- [ ] **Orderflow Imbalance**: Cumulative delta, signed volume, aggressive flow detection
- [ ] **Composite Signals**: Combine signals with regime detection

### Phase 4: Backtesting & Validation
- [ ] **Backtest engine**: Event-driven backtester with position sizing
- [ ] **Risk management**: Stop loss, take profit, position limits
- [ ] **Metrics**: Sharpe, Sortino, Calmar, win rate, profit factor, max DD
- [ ] **Walk-forward**: Out-of-sample validation framework

### Phase 5: Testing & Diagnostics
- [ ] **Unit tests**: Replace/extend tests with real tests for calculations (no `assert True` placeholders)
- [ ] **Integration tests**: End-to-end data pipeline tests
- [ ] **Diagnostics**: Add performance tracking and strategy analytics

**MANDATE**: This is a quantitative trading strategy project. Prioritize mathematical correctness, vectorized operations where appropriate, and realistic assumptions. No toy implementations — build something that could be extended to production. All phases above are mandatory; skipping phases is not permitted.
