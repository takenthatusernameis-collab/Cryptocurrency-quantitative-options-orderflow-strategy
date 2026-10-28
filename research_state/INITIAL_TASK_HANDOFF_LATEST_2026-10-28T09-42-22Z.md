# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T09:42:22Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 87 TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- Confirmed clean working tree (git status: nothing to commit, branch up-to-date with origin/main).
- Verified 87/87 tests pass in 0.53s. No TODO/FIXME/HACK/PLACEHOLDER markers remain in src/ or tests/.
- All existing infrastructure is hardened and tested. No blocked or inefficient sessions remain.
- Ready for next heavy engineering campaign with zero friction.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MANDATORY - EXECUTE IMMEDIATELY)

START AT PHASE 2 - NEXT UNCOMPLETED ITEM. DO NOT DEVIATE. NO COSMETIC CHANGES.

TARGET: **Orderflow imbalance at multiple horizons with decay weighting — EXTEND AND HARDEN TO PRODUCTION GRADE**

### Context
Functions exist in `src/features/orderflow.py:143-250` (`orderflow_imbalance_multi_horizon`, aliases) and are tested in `tests/test_features.py:235-320`. Current implementation is solid but needs deeper hardening and more comprehensive property testing.

### MANDATORY DELIVERABLES (COMPLETE THIS ITEM FULLY)
1. **Deepen implementation hardening** in `src/features/orderflow.py`:
- Strengthen input validation for `trades`, `horizons`, `decay` (handle NaN/inf, non-numeric types, empty iterables)
- Ensure all horizon values are sanitized (positive ints only), deduplicate if needed, handle large horizons gracefully
- Harden decay weighting: clamp decay to reasonable range [0, large), handle exp overflow/underflow
- Ensure every returned value is finite and clamped to [-1,1] with explicit guards
- Add defensive handling for cross-consistency calculations
- Consider vectorization where sensible (numpy) while keeping API compatible
- Add missing aliases if any useful aggregations are missing

2. **Extend property/invariant tests** in `tests/test_features.py` (or add focused tests):
- Normalization invariants: all outputs in [-1,1], finite
- Decay behavior: verify shorter horizons get higher weight when decay>0 (with horizons ordered as given); test different decay values
- Empty/edge cases: empty trades, None inputs, horizons with all invalid values, single horizon
- Cross-consistency: each `imb_h` equals `calculate_orderflow_imbalance(trades, window=h)` exactly (within float precision)
- All-buys/all-sells give values near ±1 across horizons
- Mixed NaN/inf in trades are filtered correctly
- Window/horizon edge cases (horizon larger than number of trades)
- Decay weighting normalization (weights sum to 1)

3. **Verification**: All tests must pass (maintain >=87 passing). No placeholders/TODOs/FIXMEs/HACKs.

### Engineering Requirements
- Mathematical correctness MANDATORY
- Numerical stability MANDATORY (explicit finite checks, guards against division by zero/overflow)
- Vectorize where sensible
- No cosmetic changes, no scaffolding
- Full implementation + tests in ONE coherent change set
- Leave heavy work for next agent - complete THIS item fully

## NEXT FOCUS CAMPAIGN (MANDATORY - NEVER AVOID HEAVY WORK)

### Phase 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING — COMPLETE
- [x] Net gamma exposure, gamma notional by delta bands, gamma flip, invariants/tests

### Phase 2: DEEP ORDERFLOW MICROSTRUCTURE (CRITICAL) — IN PROGRESS
- [x] Cumulative delta with trade classification robustness, VWAP-adjusted delta, signed volume (FULL TEST COVERAGE + HARDENING)
- [ ] **Orderflow imbalance at multiple horizons with decay weighting (EXTEND TESTS + HARDEN) ← CURRENT TARGET**
- [ ] Footprint/orderflow divergence metrics (deepen tests beyond current)
- [ ] VPIN-style toxicity proxy with finite-sample guards (deepen property tests)
- [ ] Harden all orderflow functions against division by zero/non-finite; comprehensive property/invariant tests

### Phase 3: VOLATILITY SURFACE & SKEW QUANTIFICATION (CRITICAL)
- [ ] IV skew term structure, put-call skew, risk reversal, butterfly spread metrics, max pain improvements
- [ ] Term structure analysis across expiries
- [ ] Realized vs implied volatility relationships

### Phase 4: REGIME-AWARE SIGNAL ENGINEERING (CRITICAL)
- [ ] Cross-feature interactions (gamma x orderflow x liquidity)
- [ ] Confidence calibration with proper scoring
- [ ] Regime detection (volatility regimes, liquidity regimes)
- [ ] Feature normalization and robustness

### Phase 5: BACKTEST RIGOR & RISK (HIGH)
- [ ] Realistic fills (slippage models), commission/fees
- [ ] Drawdown controls, position sizing, Kelly criterion
- [ ] Walk-forward analysis, out-of-sample testing
- [ ] Stress tests, transaction cost sensitivity

### Phase 6: INTEGRATION, RESILIENCE & TESTS (HIGH)
- [ ] Wire features into end-to-end pipeline
- [ ] Property-based tests across modules
- [ ] Explicit finite checks everywhere
- [ ] Vectorization optimization
- [ ] Comprehensive e2e tests

## VERIFIED CODEBASE STATE
- `src/features/orderflow.py:360` — all orderflow functions, hardened, aliases present
- `src/features/gamma_exposure.py:330` — full GEX stack, delta bands, gamma flip interpolation
- `src/features/volatility.py:80` — put/call ratio, IV skew, max pain (needs Phase 3 expansion)
- `src/features/liquidity.py:127` — spread, mid, relative/effective spread, liquidity score, chain metrics
- `src/signals/composite.py:200` — regime-aware composite signal generator
- `src/backtest/engine.py:439` — event-driven backtest engine
- `src/data/schemas.py:78` — Pydantic schemas
- `tests/test_features.py:399` — comprehensive feature tests
- `tests/test_phase1_gamma_invariants.py` — gamma exposure property tests
- **87 tests total, all passing** (0.53s)

## MANDATE
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent.

## SOURCE OF TRUTH HIERARCHY
1. `research_state/durable_handoff.md` (THIS FILE - AUTHORITATIVE, TIMESTAMPED 2026-10-28T09:42:22Z)
2. `research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T09-42-22Z.md` (this snapshot)
3. Earlier handoff files superseded.

EXECUTE NOW. START AT PHASE 2 NEXT ITEM. NO DELAY.
