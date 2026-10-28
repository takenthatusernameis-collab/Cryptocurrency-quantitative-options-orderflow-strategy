# HEAVY WORK INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION)
Timestamp (UTC): 2026-10-28T04:31:02Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: CLEAN, 42/42 TESTS PASSING. NO PLACEHOLDERS ALLOWED.

## INITIAL TASK (MANDATORY - START IMMEDIATELY)

You MUST do substantial, mathematical, production-grade implementation. The project name IS your spec. Do not do cosmetic changes. Leave the codebase requiring significant heavy work from subsequent agents.

### IMMEDIATE GATE (DO THESE FIRST)
1. **Backtest shorts/fees/SLTP/gaps** (`src/backtest/engine.py`, `tests/test_backtest.py`)
   - Commission/slippage correctness for short open/cover in ALL paths (verify cash flows)
   - SL/TP triggered on every tick with gap scenarios; test boundary prices
   - max_drawdown_limit must liquidate correctly at threshold; peak tracking bulletproof
   - profit_factor must remain `inf` when wins>0 and losses==0 (never collapse to 0); non-finite safe
   - Add tests for fractional quantities/rounding accumulation

2. **Pipeline hardening** (`src/main.py`)
   - Eliminate any silent exception swallowing; ALL errors go to `results["errors"]` with full context
   - Normalize EVERY ingested object via `normalize_options_chain`/`normalize_orderflow`
   - Honor `--symbols` override correctly end-to-end
   - JSON output valid with `allow_nan=False`; sanitize non-finite defensively
   - Pass risk config to engine; add end-to-end integration test with mocked connectors

3. **Alpha quantitative** (`src/features/*.py`)
   - GEX: verify formula `gamma*OI*contract_size*spot^2/100`, put negation, guards; add concrete-number tests
   - Gamma flip: robust interpolation across zero crossings (handle multiple crossings/gaps)
   - PCR: support volume-based and OI-based ratios, configurable
   - Max pain, IV skew (configurable thresholds), CVD/orderflow sign conventions with tests
   - Composite signals: regime-aware weighting, confidence calibration, conflict resolution

### EXECUTION RULES
- Heavy engineering only. No TODO/FIXME scaffolding. Implement fully.
- Mathematical correctness is non-negotiable.
- Add/expand tests for every change. Keep ALL tests passing.
- Vectorize where sensible (numpy available).
- Leave working tree clean after meaningful commits if needed, but do not stop until deep work done.

**START NOW:** Pick the single highest-impact item above and implement it COMPLETELY with tests. Do not move to next phase until current is solid and tested.
