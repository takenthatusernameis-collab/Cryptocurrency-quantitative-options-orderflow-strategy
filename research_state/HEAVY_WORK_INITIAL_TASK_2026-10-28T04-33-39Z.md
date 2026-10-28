# HEAVY WORK INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION)

Timestamp (UTC): 2026-10-28T04:33:39Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: CLEAN, 42/42 TESTS PASSING. WORKING TREE CLEAN (pycache de-tracked). NO PLACEHOLDERS ALLOWED.

## Project-name-derived spec
The project name IS the spec: "Cryptocurrency-quantitative-options-orderflow-strategy". The codebase must be a mathematically correct, production-grade crypto options orderflow strategy. Scaffolding is complete; remaining work is deep quantitative integration and validation. Every next action must be substantive implementation. Future agents MUST do heavy implementation work - leave this codebase in a state where minimal changes are not enough.

## Current Verified State (ALL DONE - do not re-litigate)
- **Tests**: 42 passed, 0 failed (pytest green).
- **Backtest Engine** (`src/backtest/engine.py`): Short equity correct (cash credited on open, liability subtracted at valuation), SL/TP enforced per tick via `check_risk_controls`, `max_position_pct`/`max_drawdown_limit` enforced, `profit_factor` preserves `inf` when wins>0/losses==0, non-finite safe.
- **Pipeline** (`src/main.py`): No silent exception swallowing - all errors collected in `results["errors"]` with context, normalization applied to every ingested object, `--symbols` override, JSON valid with `allow_nan=False` sanitization, risk config passed to engine.
- **Features** (`src/features/*.py`): GEX formula `gamma*OI*contract_size*spot^2/100` with put negation; PCR volume and OI; IV skew; max pain; CVD/orderflow sign convention; all with zero-division/non-finite guards.
- **Connectors**: Deribit/OKX/Binance for options + orderflow implemented; CLI wires all three venues; mock connector available.
- **Config**: `config/settings.yaml` has full risk/backtest config.

## Bottlenecks Removed This Session
- De-tracked 17 `__pycache__/*.pyc` files from git index (were still tracked despite `.gitignore`); working tree now clean.
- Verified 42/42 tests green.

## NEXT FOCUS CAMPAIGN (MANDATORY - HEAVY QUANTITATIVE WORK)
The prior scaffolding phases are complete. The gap now is that the alpha features exist but are NOT wired into the live pipeline, and there is no regime-aware signal logic, no config validation, no integration tests, and no property-based tests. Future agents cannot avoid this work.

### PHASE 1: WIRE ALPHA FEATURES INTO PIPELINE (CRITICAL)
`src/main.py:99-127` hardcodes `iv_skew=0.0` and `of_imbalance=0.0`; `calculate_max_pain` is never called. Connect the implemented features end-to-end.
- Wire `calculate_iv_skew(chain, spot_price)` into `iv_skew` argument of `generate_signal`.
- Wire `calculate_orderflow_imbalance(ingested_orderflows[key].trades)` into `of_imbalance`.
- Wire `calculate_max_pain(chain)` into results and into signal components.
- Add per-key try/except around feature computation with full context in `results["errors"]` (currently outer try only).
- Add unit/integration tests verifying skew/imbalance/max-pain flow through the pipeline with concrete numbers.

### PHASE 2: REGIME-AWARE COMPOSITE SIGNAL + CONFIDENCE CALIBRATION (CRITICAL - MOST IMPACT)
`src/signals/composite.py` uses static weights and `confidence = abs(composite)` with no regime awareness, no calibration, no conflict resolution.
- Implement regime detection (e.g., GEX sign/magnitude + skew regime) and regime-aware weight adjustment.
- Add confidence calibration (confidence must reflect component agreement, not just |composite|).
- Add conflict resolution rule when gamma/orderflow/skew/PCR disagree.
- Add concrete-number unit tests for each regime and conflict case.

### PHASE 3: FEATURE ENRICHMENT (HIGH)
- Delta-weighted GEX (uses `quote.delta`).
- Vanna/charm if greeks available in schema.
- Liquidity metrics (bid-ask spread, OI/volume ratio).
- Each with guards and tests.

### PHASE 4: CONFIG VALIDATION + INTEGRATION TESTS (HIGH)
- `src/config.py`: validate required config fields (symbols non-empty, fee_rate in [0,1], risk limits in (0,1]), raise clear `ValueError` with field names if missing/invalid.
- Add end-to-end integration test (`tests/test_pipeline_integration.py`) that runs `run_pipeline` with mocked connectors/fixtures and validates result structure, error collection, JSON serializability (`allow_nan=False`).

### PHASE 5: PROPERTY-BASED + NUMERIC TESTS (MED)
- Property-based tests (hypothesis if available, else manual) for numeric invariants: equity conservation on short open/cover, profit_factor inf-preservation, GEX sign convention (puts negative), max_pain within strike range, drawdown limit boundary.
- Maintain 100% pass rate.

## EXECUTION RULES
- Heavy engineering only. No TODO/FIXME scaffolding. Implement fully.
- Mathematical correctness is non-negotiable.
- Add/expand tests for every change. Keep ALL tests passing.
- Vectorize where sensible (numpy available).
- Leave working tree clean; do not stop until deep work done. Do NOT "finish" everything - leave significant work for the following agent.

## STARTING INSTRUCTION FOR NEXT AGENT
**IMMEDIATELY START AT PHASE 1.** Pick the highest-impact uncompleted item and implement it fully with tests. Do NOT do cosmetic changes. Every change must improve mathematical correctness, robustness, or test coverage in a measurable way. The codebase must be left in a state that REQUIRES significant work from the following agent.

**GOLDEN RULE**: Heavy engineering only. Mathematical correctness is mandatory. Vectorize where sensible. Never deflect from implementation.

(End of file)