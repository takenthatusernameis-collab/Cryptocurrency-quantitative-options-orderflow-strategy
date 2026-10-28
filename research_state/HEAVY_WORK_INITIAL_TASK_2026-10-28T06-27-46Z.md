# HEAVY WORK INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION)

Timestamp (UTC): 2026-10-28T06-27-46Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: CLEAN, 57/57 TESTS PASSING. PYCACHE DE-TRACKED FROM INDEX. INGESTION IMPORTS WIRED INTO src/main.py. NO PLACEHOLDERS ALLOWED.

## Project-name-derived spec
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy. Scaffolding complete; remaining work is deep quantitative integration and validation. Every next action must be substantive implementation.

## Bottlenecks Removed This Session
- Wired missing imports into `src/main.py`: `DeribitOptionsIngestion`/`DeribitOrderflowIngestion`, `OKXOptionsIngestion`/`OKXOrderflowIngestion`, `BinanceOptionsIngestion`/`BinanceOrderflowIngestion`, `CompositeSignalGenerator`, `calculate_cumulative_delta`, `calculate_orderflow_imbalance`, `calculate_iv_skew`, `calculate_max_pain`, `calculate_put_call_ratio`. Tests that patched `src.main.<Class>` now resolve; 57/57 tests pass (was 54 pass / 3 fail).
- De-tracked all 18 tracked `__pycache__/*.pyc` files from the git index (staged deletions; `.gitignore` already excludes them). Working tree now clean except the intentional `src/main.py` edit.
- Consolidated prior handoffs; this is the latest timestamped initial task message. Older `research_state/HEAVY_WORK_INITIAL_TASK_*.md` files are superseded by this one and `research_state/durable_handoff.md`.

## NEXT FOCUS CAMPAIGN (MANDATORY - HEAVY QUANTITATIVE WORK)
Gap: alpha features exist but are not fully regime-aware; no config validation enforcement at runtime boundaries; backtest engine does not yet leverage `partial_fill_rate`/`round_lot_size`/`max_slippage_bps`/`slippage_seed`; integration/property tests need expansion. Future agents cannot avoid this work.

### PHASE 1: FEATURE ENRICHMENT — DELTA-WEIGHTED GEX, LIQUIDITY METRICS (CRITICAL) — START HERE
- Enrich `src/features/gamma_exposure.py`: delta-weighted GEX using `quote.delta` when available (fall back gracefully if missing). Add OI/volume-weighted metrics.
- Add liquidity features (bid-ask spread, mid price, effective spread proxies) in `src/features/` and wire into pipeline results/signals with per-key try/except + concrete tests.
- Add numeric tests with concrete values in `tests/`.

### PHASE 2: REGIME-AWARE COMPOSITE SIGNAL + CONFIDENCE CALIBRATION (CRITICAL)
- Extend regime detection with additional regimes (e.g., vol regime by term structure, liquidity regime).
- Improve confidence calibration to reflect component agreement and signal strength more robustly.
- Add conflict resolution logic when gamma/orderflow/skew/PCR strongly disagree.
- Expand tests in `tests/test_signals_regime.py` with concrete-number cases.

### PHASE 3: CONFIG VALIDATION + BACKTEST HARDENING (HIGH)
- Strengthen `src/config.py` validation (venue validation, symbol format checks, cross-field constraints). Ensure clear ValueError messages with field names.
- Leverage existing BacktestConfig fields (`partial_fill_rate`, `round_lot_size`, `max_slippage_bps`, `slippage_seed`) in `src/backtest/engine.py` (deterministic partial fills, lot rounding, slippage caps). Add tests.
- Enforce `max_position_qty` and `allow_shorting` from RiskConfig in engine.

### PHASE 4: INTEGRATION TESTS + ERROR RESILIENCE (HIGH)
- Expand `tests/test_pipeline_integration.py`: test multi-venue flows, error collection with context, JSON serializability (allow_nan=False) under all paths.
- Ensure all feature computations have guards (zero division, non-finite) and errors are surfaced in `results["errors"]` with context.
- Test edge cases (empty chains, missing greeks, bad data).

### PHASE 5: PROPERTY-BASED + NUMERIC TESTS (MED)
- Add property-based/numeric invariant tests: short equity conservation, profit_factor inf-preservation, GEX sign conventions, max_pain within strike range, drawdown boundary enforcement, SL/TP triggering.
- Maintain 100% pass rate. Vectorize where sensible (numpy available).

## EXECUTION RULES
- Heavy engineering only. No TODO/FIXME scaffolding. Implement fully.
- Mathematical correctness non-negotiable. Vectorize where sensible (numpy available).
- Add/expand tests per change. Keep ALL tests passing.
- Leave working tree clean; do not stop until deep work done. Do NOT "finish" everything - leave significant work for the following agent.

## STARTING INSTRUCTION FOR NEXT AGENT
IMMEDIATELY START AT PHASE 1. Pick the highest-impact uncompleted item and implement fully with tests. Do NOT do cosmetic changes. Every change must improve mathematical correctness, robustness, or test coverage measurably. Leave codebase requiring significant work from the following agent.

GOLDEN RULE: Heavy engineering only. Mathematical correctness mandatory. Vectorize where sensible. Never deflect from implementation.
