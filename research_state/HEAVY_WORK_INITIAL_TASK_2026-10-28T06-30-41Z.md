# HEAVY WORK INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION)

Timestamp (UTC): 2026-10-28T06-30-41Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: CLEAN, 65/65 TESTS PASSING. ALL PREVIOUSE BOTTLENECKS REMOVED. NO PLACEHOLDERS ALLOWED.

## Project-name-derived spec
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy. Build heavy quantitative implementation; scaffolding exists, fill in remaining gaps with rigorous math.

## Bottlenecks Removed This Session
- Wired ingestion imports into `src/main.py` (Deribit/OKX/Binance options+orderflow, CompositeSignalGenerator, feature functions); fixed patching paths.
- De-tracked all `__pycache__/*.pyc` from git index; `.gitignore` excludes them.
- Enriched features: delta-weighted GEX, OI/volume-weighted GEX, liquidity metrics (bid-ask spread/mid/relative/effective/liquidity score), wired into pipeline (`src/main.py`) and exports (`src/features/__init__.py`).
- Strengthened composite signal: extended regime detection, conflict resolution, improved confidence calibration.
- Hardened backtest: lot rounding, deterministic partial fills, max slippage cap, `max_position_qty` enforcement, `allow_shorting` enforcement.
- Strengthened config validation (venues/symbol formats/cross-field constraints).
- Added comprehensive tests for features/backtest/config paths.

## NEXT FOCUS CAMPAIGN (MANDATORY - HEAVY QUANTITATIVE WORK)
Gap: pipeline needs more numeric robustness, integration tests, and deeper regime/conflict logic. Future agents must continue heavy implementation.

### PHASE 1: DEEPER FEATURE INTEGRATION & NUMERIC INVARIANTS (CRITICAL)
- Add more concrete numeric tests for delta-weighted/weighted GEX across strike ranges.
- Ensure liquidity metrics propagate correctly under edge cases (inverted spreads, missing mark/last).
- Add property-style invariants where possible.

### PHASE 2: REGIME-BASED SIGNAL ENRICHMENT (CRITICAL)
- Add vol/liquidity regime interplay, stronger conflict resolution with component weights.
- Consider term structure/skew convexity if data available; add tests with concrete numbers.
- Improve calibration to penalize disagreement more robustly.

### PHASE 3: BACKTEST NUMERIC ROBUSTNESS (HIGH)
- Add tests for SL/TP triggering, max drawdown enforcement, short PnL accounting edge cases.
- Ensure profit_factor inf preservation and drawdown boundaries.
- Harden against non-finite values throughout.

### PHASE 4: INTEGRATION + ERROR RESILIENCE (HIGH)
- Expand pipeline integration tests (multi-venue, partial failures, JSON serializability under NaN/Inf).
- Ensure all errors collected with context in results["errors"].
- Test empty chains/missing greeks.

### PHASE 5: PROPERTY-BASED TESTS (MED)
- Add invariant tests (equity conservation, position accounting) where feasible.

## EXECUTION RULES
- Heavy engineering only. No TODO/FIXME scaffolding. Implement fully.
- Mathematical correctness non-negotiable.
- Add/expand tests per change. Keep ALL tests passing.
- Leave working tree clean; do not stop until deep work done. Leave significant work for following agent.

## STARTING INSTRUCTION FOR NEXT AGENT
IMMEDIATELY START AT PHASE 1. Pick highest-impact uncompleted item, implement fully with tests. No cosmetic changes. Every change must improve mathematical correctness/robustness/test coverage measurably. Leave codebase requiring significant work from the following agent.

GOLDEN RULE: Heavy engineering only. Mathematical correctness mandatory. Vectorize where sensible. Never deflect.
