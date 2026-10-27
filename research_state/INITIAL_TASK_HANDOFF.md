# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-27T22:41:32Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy

## Initial Task Message (for next agentic session)

**PRIORITY: BUILD CORE STRATEGY IMPLEMENTATION** 

You are tasked with building the cryptocurrency quantitative options orderflow strategy from scratch. Focus on heavy engineering work with no placeholders - implement production-quality code.

### Immediate Objectives:
1. **Data Layer**: Create modules for options chain ingestion (Deribit/OKX/Binance options), orderflow data (trades, liquidations), and normalization across venues
2. **Feature Engineering**: Implement gamma exposure (GEX), delta-adjusted flow, volatility skew analysis, put/call ratios, max pain, and orderflow imbalance metrics
3. **Signal Generation**: Build quantitative signals combining orderflow toxicity, dealer positioning, and volatility surface features
4. **Backtesting**: Create a robust backtesting harness with realistic execution, fees, slippage, and performance metrics (Sharpe, Sortino, max drawdown)
5. **Infrastructure**: Add configuration, logging, data validation, and diagnostics

### Requirements:
- Write clean, tested Python code (follow existing patterns)
- Add unit tests for core logic - no placeholder tests
- Ensure all tests pass
- Make meaningful commits as you progress
- Focus on end-to-end functionality over perfection

**Do not stop at scaffolding. Implement working, testable code that can process real options/orderflow data.**

## Bottlenecks Removed

- Created missing `scripts/controller_progress.py` for workflow checkpoint validation
- Existing placeholder tests allow CI to pass while core implementation is built

## Next Focus Campaign (Execute in Order)

### Phase 1: Foundation (Critical Path)
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
- [ ] **Unit tests**: Replace placeholders with real tests for calculations
- [ ] **Integration tests**: End-to-end data pipeline tests
- [ ] **Diagnostics**: Add performance tracking and strategy analytics

**MANDATE**: This is a quantitative trading strategy project. Prioritize mathematical correctness, vectorized operations where appropriate, and realistic assumptions. No toy implementations - build something that could be extended to production.
" filePath">
research_state/INITIAL_TASK_HANDOFF.md