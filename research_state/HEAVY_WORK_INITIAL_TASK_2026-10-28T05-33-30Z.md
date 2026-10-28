# HEAVY WORK INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION)

Timestamp (UTC): 2026-10-28T05-33-30Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: CLEAN, 57/57 TESTS PASSING. PYCACHE DE-TRACKED. NO PLACEHOLDERS ALLOWED.

## Project-name-derived spec
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy. Scaffolding complete; remaining work is deep quantitative integration and validation. Every next action must be substantive implementation.

## Bottlenecks Removed This Session
- Removed tracked __pycache__ modifications from working tree; .gitignore excludes them.
- Verified 57/57 tests green.
- Consolidated prior handoffs; this is the latest durable initial task message.

## NEXT FOCUS CAMPAIGN (MANDATORY - HEAVY QUANTITATIVE WORK)
Gap: alpha features exist but are NOT wired into the live pipeline; no regime-aware signal logic, no config validation, no integration/property tests. Future agents cannot avoid this work.

### PHASE 1: WIRE ALPHA FEATURES INTO PIPELINE (CRITICAL) — START HERE
- Wire `calculate_iv_skew(chain, spot_price)` into `iv_skew` arg of `generate_signal`.
- Wire `calculate_orderflow_imbalance(ingested_orderflows[key].trades)` into `of_imbalance`.
- Wire `calculate_max_pain(chain)` into results and signal components.
- Per-key try/except around feature computation with full context in `results["errors"]`.
- Unit/integration tests with concrete numbers.

### PHASE 2: REGIME-AWARE COMPOSITE SIGNAL + CONFIDENCE CALIBRATION (CRITICAL)
- Regime detection (GEX sign/magnitude + skew regime) with regime-aware weight adjustment.
- Confidence calibration reflecting component agreement.
- Conflict resolution when gamma/orderflow/skew/PCR disagree.
- Concrete-number tests per regime/conflict case.

### PHASE 3: FEATURE ENRICHMENT (HIGH)
- Delta-weighted GEX (uses quote.delta), vanna/charm if greeks available, liquidity metrics (bid-ask spread, OI/volume ratio); guards + tests.

### PHASE 4: CONFIG VALIDATION + INTEGRATION TESTS (HIGH)
- `src/config.py`: validate required fields (symbols non-empty, fee_rate in [0,1], risk limits in (0,1]), raise clear ValueError with field names.
- End-to-end integration test in `tests/test_pipeline_integration.py` with mocked connectors, result structure, error collection, JSON serializability (allow_nan=False).

### PHASE 5: PROPERTY-BASED + NUMERIC TESTS (MED)
- Property-based tests (hypothesis if available) for numeric invariants: short equity conservation, profit_factor inf-preservation, GEX sign (puts negative), max_pain within strike range, drawdown boundary. Maintain 100% pass.

## EXECUTION RULES
- Heavy engineering only. No TODO/FIXME scaffolding. Implement fully.
- Mathematical correctness non-negotiable. Vectorize where sensible (numpy available).
- Add/expand tests per change. Keep ALL tests passing.
- Leave working tree clean; do not stop until deep work done. Do NOT "finish" everything - leave significant work for the following agent.

## STARTING INSTRUCTION FOR NEXT AGENT
IMMEDIATELY START AT PHASE 1. Pick highest-impact uncompleted item and implement fully with tests. Do NOT do cosmetic changes. Every change must improve mathematical correctness, robustness, or test coverage measurably. Leave codebase requiring significant work from the following agent.

GOLDEN RULE: Heavy engineering only. Mathematical correctness mandatory. Vectorize where sensible. Never deflect from implementation.
