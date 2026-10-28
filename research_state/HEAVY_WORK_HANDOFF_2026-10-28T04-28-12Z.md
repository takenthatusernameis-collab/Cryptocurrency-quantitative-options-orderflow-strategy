# Heavy Work Handoff — Crypto Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T04:28:12Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
State: CLEAN, ALL TESTS PASSING (42/42). READY FOR DEEP QUANTITATIVE WORK.

## Mission (MANDATORY)
Build a production-grade, mathematically correct crypto options orderflow strategy. NO scaffolding, NO placeholders. Every next action must be substantive engineering. Future agents MUST do heavy implementation work - leave this codebase in a state where minimal changes are not enough.

## Current Verified State
- **Tests**: 42 passed, 0 failed (pytest green).
- **Backtest Engine** (`src/backtest/engine.py`): Short equity correct (cash credited on open, liability subtracted), SL/TP enforced per tick via `check_risk_controls`, `max_position_pct`/`max_drawdown_limit` enforced, `profit_factor` preserves `inf` when wins>0/losses==0, non-finite safe.
- **Pipeline** (`src/main.py`): No silent exception swallowing - all errors collected in `results["errors"]` with context, normalization applied to every ingested object, `--symbols` override, JSON valid with `allow_nan=False` sanitization, risk config passed to engine.
- **Features**: GEX formula implemented with put negation, guards for division/inf/nan; PCR handles zero division (returns inf or 0); IV skew/OI/orderflow have guards.
- **Connectors**: Deribit/OKX/Binance for options + orderflow implemented; CLI wires all three venues.
- **Config**: `config/settings.yaml` has full risk/backtest config.

## Bottlenecks To Crush Next (HEAVY WORK)

### PHASE 1: DEEP BACKTEST ROBUSTNESS (CRITICAL)
- [ ] **Commission/Slippage on Shorts**: Verify commission charged correctly on short open and cover in all paths; add tests for fee math on shorts.
- [ ] **Partial Fills & Rounding**: Test fractional quantities, precision edge cases; ensure no accumulation of rounding errors over many trades.
- [ ] **SL/TP Timing**: Verify SL/TP triggers before/at equity update with realistic price paths; test gap scenarios.
- [ ] **Drawdown**: Max drawdown limit must trigger at correct threshold (test boundary conditions). Peak equity tracking must be bulletproof.
- [ ] **Metrics Edge Cases**: Sortino when all positive returns (currently falls back to sharpe) - consider if this is intended or needs adjustment; add more tests.

### PHASE 2: PIPELINE INTEGRATION HARDENING (CRITICAL)
- [ ] **Feature Calculation Errors**: Wrap feature computation in per-key try/except with full context (currently has outer try but could be more granular).
- [ ] **Normalization Coverage**: Ensure every venue's raw response goes through normalization; add validation/assertions.
- [ ] **Symbol Consistency**: Cross-venue normalization must be consistent; test with mixed case/symbol formats.
- [ ] **Config Validation**: Validate required config fields, provide clear errors if missing/invalid.
- [ ] **End-to-End Test**: Add integration test that runs full pipeline with mocked connectors and validates structure.

### PHASE 3: ALPHA QUANTITATIVE HARDENING (HIGH PRIORITY - MOST IMPACT)
- [ ] **GEX Formula Verification**: Validate against known convention. Standard: GEX = Gamma * OI * Contract Size * Spot^2 / 100. Confirm sign convention is correct for puts/calls. Add unit tests with concrete numbers.
- [ ] **Gamma Flip Level**: Improve interpolation/robustness when zero crossing is between strikes; handle multiple crossings.
- [ ] **PCR**: Support both volume and OI based ratios; ensure callers can choose. Add tests for edge cases.
- [ ] **Max Pain**: Verify calculation is correct (pain = max(0, strike - spot)*call_oi + max(0, spot - strike)*put_oi summed appropriately). Current impl looks right but needs verification.
- [ ] **IV Skew**: Current uses moneyness thresholds (<0.95 puts, >1.05 calls). Consider 25-delta approximation if greeks available; make thresholds configurable.
- [ ] **CVD/Orderflow**: Ensure correct sign convention (buy adds, sell subtracts) - looks correct. Add tests with sample trades.
- [ ] **Composite Signals**: Make regime-aware weighting more sophisticated; add confidence calibration; improve conflict resolution.
- [ ] **Feature Enrichment**: Add more features (delta-weighted GEX, vanna/charm if greeks available, liquidity metrics).

### PHASE 4: TESTING & VALIDATION (HIGH)
- [ ] **Numeric Tests**: Expand coverage for backtest edge cases (short covering with fees, multiple positions, etc.)
- [ ] **Feature Tests**: Add comprehensive tests for all feature functions with edge cases
- [ ] **Integration Tests**: Full pipeline tests with fixtures
- [ ] **Property-Based Tests**: Consider using hypothesis for numeric properties (e.g., equity conservation)
- [ ] **All Tests Green**: Must maintain 100% pass rate

### PHASE 5: PRODUCTION READINESS (MEDIUM)
- [ ] **Error Handling**: More specific exception types, better logging
- [ ] **Performance**: Vectorize where sensible (numpy already imported)
- [ ] **Type Hints**: Improve coverage
- [ ] **Documentation**: Add docstrings for complex calculations
- [ ] **Clean State**: Ensure no pycache tracked, working tree clean

## STARTING INSTRUCTION FOR NEXT AGENT
**IMMEDIATELY START AT PHASE 1.** Pick the highest-impact uncompleted item and implement it fully with tests. Do NOT do cosmetic changes. Every change must improve mathematical correctness, robustness, or test coverage in a measurable way. The codebase must be left in a state that REQUIRES significant work from the following agent - do not "finish" everything, do deep work on specific areas.

**GOLDEN RULE**: Heavy engineering only. Mathematical correctness is mandatory. Vectorize where sensible. Never deflect from implementation.
