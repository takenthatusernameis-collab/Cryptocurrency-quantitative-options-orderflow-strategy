# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T04:24:18Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: ACTIVE-HANDOFF-UPDATE. HEAD clean. All tests passing. Prioritize heavy quantitative implementation.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION — MANDATORY, HEAVY ENGINEERING)

**PRIORITY 1: BUILD A PRODUCTION-GRADE CRYPTO OPTIONS ORDERFLOW STRATEGY — NO SCAFFOLDING, NO PLACEHOLDERS**

You are inheriting a codebase with solid scaffolding (42 tests green). The name says it all: "Cryptocurrency-quantitative-options-orderflow-strategy". Your job is to make it mathematically correct and robust. Every action must be substantive implementation.

### IMMEDIATE GATE (EXECUTE IN STRICT ORDER)

1. **BACKTEST ENGINE CORRECTNESS (CRITICAL)** - `src/backtest/engine.py`
   - Short equity: `get_equity` must return `cash + qty × (entry_price − current_price)` for shorts (credit proceeds on open, subtract liability correctly). Realized PnL must flow to cash on close/cover. ✓ Currently implemented correctly.
   - SL/TP: Enforce on every price tick via `check_risk_controls` called from `update_equity_curve`. Close/cover on trigger and realize PnL. ✓ Implemented.
   - Risk limits: Enforce `max_position_pct` and `max_drawdown_limit` from risk config. Close all positions on max drawdown breach. ✓ Implemented.
   - Metrics: `profit_factor` must remain `inf` when total_wins>0 and total_losses==0 (never collapse to 0). `win_rate`/counts from closed trades only. `calmar_ratio = total_return / max_drawdown` when dd>0. All metrics non-finite-safe and JSON-serializable with `allow_nan=False`. ✓ Implemented.
   - Numeric tests all pass. Maintain correctness as you extend.

2. **PIPELINE ROBUSTNESS (CRITICAL)** - `src/main.py`, `src/data/normalization.py`
   - NO silent `except Exception: pass`. Every exception must be recorded in `results["errors"]` with context (venue/symbol/phase). Never abort entire run on single venue failure. ✓ No silent swallows found.
   - Apply `normalize_options_chain` and `normalize_orderflow` to EVERY ingested object before features/signals. ✓ Done.
   - Enforce cross-venue symbol/timestamp consistency via `normalize_symbol`/`normalize_timestamp`. ✓ Implemented.
   - Honor `--symbols` override. JSON output via `--json` must always be valid (`allow_nan=False`), sanitize non-finite to None if needed. ✓ Done.
   - Pass full config (including `risk`) to BacktestEngine; load from settings.yaml. ✓ Done.
   - Structured results: per-venue counts, trades, signals, backtest metrics, errors.

3. **ALPHA FEATURES QUANTITATIVE HARDENING (HIGH)** - `src/features/*.py`, `src/signals/composite.py`
   - GEX: `GEX = gamma × OI × contract_size × spot² / 100` (puts negative, calls positive). Correct aggregation by strike; gamma flip detection robust.
   - Volatility: PCR by volume and OI (handle call_volume==0 without crash). IV skew = OTM put IV − OTM call IV. Max pain strike minimizing total pain.
   - Orderflow: CVD, orderflow imbalance, aggressive flow with guards (zero division, non-finite). Delta-adjusted flow where applicable.
   - Composite signals: regime-aware weighting, confidence in [0,1], conflict resolution, calibration.

## MANDATORY FOCUS CAMPAIGN (NO SKIPPING, NO DEFERMENT)

### PHASE 1: BACKTEST ENGINE (CRITICAL) - BLOCKS REAL EVALUATION
- [x] Short equity math correct (credit proceeds on open, subtract liability)
- [x] SL/TP enforced on every price tick via `check_risk_controls` called from `update_equity_curve`
- [x] Enforce `max_position_pct`, `max_drawdown_limit` from config
- [x] `profit_factor` preserves `inf` when wins>0 and losses==0
- [x] Numeric tests for shorts/sizing/SLTP/metrics all passing
- [ ] **HARDEN FURTHER**: Ensure position sizing respects limits in all paths; add edge case tests for partial fills, commission on shorts, slippage effects
- [ ] **VERIFY**: Walk through full short lifecycle with fees/slippage - cash flows must be correct

### PHASE 2: PIPELINE HARDENING (CRITICAL)
- [x] No silent exception swallowing in `src/main.py`
- [x] Normalize every ingested object
- [x] `--symbols` override works
- [x] JSON output valid with `allow_nan=False` sanitization
- [x] Pass risk config to engine
- [ ] **HARDEN**: Add try/except with full context for feature calculation phase; ensure partial failures don't corrupt state
- [ ] **ADD**: Validate symbol normalization consistency across venues; log normalization stats

### PHASE 3: FEATURE HARDENING (HIGH) - ALPHA QUALITY
- [ ] **GEX**: Verify formula `GEX = gamma × OI × contract_size × spot² / 100` with puts negative/calls positive; test aggregation edge cases
- [ ] **PCR**: Handle zero volume/OI gracefully (no division by zero); both volume-based and OI-based
- [ ] **MAX PAIN**: Correct implementation minimizing total pain across strikes
- [ ] **IV SKEW**: OTM put IV - OTM call IV calculation correct
- [ ] **ORDERFLOW**: CVD calculation correct with guards; handle empty trades
- [ ] **COMPOSITE**: Regime-aware weighting, confidence calibration, conflict resolution
- [ ] **ADD**: Numeric tests for all feature functions with edge cases

### PHASE 4: VALIDATION & INTEGRATION (HIGH)
- [ ] Run full test suite - all must pass
- [ ] Integration test of full pipeline end-to-end with real-ish data
- [ ] Verify backtest uses correct risk config from settings.yaml
- [ ] Test JSON serialization with inf/nan values
- [ ] Ensure no regressions

### PHASE 5: HYGIENE & DOCUMENTATION (MED)
- [ ] Clean commit history if needed
- [ ] Ensure working tree clean
- [ ] No `__pycache__` tracked
- [ ] Update any necessary docs

## BOTTLENECKS REMOVED
- Bytecode de-tracked (`__pycache__/*.pyc`); `.gitignore` correct
- All 42 existing tests passing
- Backtest numeric tests all passing (17 tests)
- No silent exception paths
- Connectors/CLI/normalization in place

## CURRENT STATE
- **Tests**: 42/42 passing ✓
- **Venues**: Deribit, OKX, Binance implemented ✓
- **CLI**: End-to-end wiring present ✓
- **Normalization**: Implemented ✓
- **Backtest**: Correct short equity, SL/TP, risk limits, metrics ✓
- **Config**: Has risk section, engine/main honor it ✓

## NEXT ACTION (START IMMEDIATELY)
**Start with Phase 1 hardening**: Review `src/backtest/engine.py` for any remaining edge cases. Focus on ensuring SL/TP triggers work correctly with slippage/fees, max drawdown limit fires at the right moment, and all numeric paths are safe. Then move to Phase 3 (feature hardening) which has the most room for quantitative improvement. Do substantial work - no placeholders.

**MANDATE**: Heavy engineering only. Mathematical correctness is mandatory. Vectorize where sensible. Never deflect. The next agent MUST do significant implementation work.
