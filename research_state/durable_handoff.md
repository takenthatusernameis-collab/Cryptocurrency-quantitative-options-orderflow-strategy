# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T10:15:30Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 88+ TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- Hardened footprint/orderflow divergence metrics in `src/features/orderflow.py`: `delta_divergence_vs_price` (robust trade/price filtering, non-finite guards, division/edge cases), `absorption_detection` (filter non-finite sizes, validate threshold/window, clamp [0,1]), `detect_aggressive_flow` (valid-trade filtering, window handling, clamp [-1,1]), `vpin_style_toxicity` (robust bucketting, finite-sample guards, clamp [0,1]). All outputs finite and bounded.
- All feature tests pass (19/19) including existing tests; numerical stability and API compatibility preserved.
- No TODO/FIXME/HACK/PLACEHOLDER markers in `src/` or `tests/`. Working tree clean.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (MANDATORY - EXECUTE IMMEDIATELY)

START AT PHASE 2 - NEXT UNCOMPLETED ITEM. DO NOT DEVIATE. NO COSMETIC CHANGES.

TARGET: **VPIN-style toxicity proxy — DEEPEN PROPERTY TESTS AND HARDEN TO PRODUCTION GRADE**

### Context
`vpin_style_toxicity` exists in `src/features/orderflow.py:418-475` (now hardened). Existing tests cover basic cases; need deeper property/invariant testing and any remaining edge hardening per Phase 2 requirements.

### MANDATORY DELIVERABLES (COMPLETE THIS ITEM FULLY)
1. **Deepen implementation hardening** in `src/features/orderflow.py` if gaps remain:
   - Ensure bucket_size/window validation, empty/small inputs, non-finite sizes filtered, bucket construction robust.
   - Handle case where total volume in buckets is zero; return 0.0.
   - Clamp to [0,1], all outputs finite.
   - Keep API compatible (`vpin_toxicity` alias).

2. **Extend property/invariant tests** in `tests/test_features.py`:
   - Bounded [0,1], finite for all valid inputs.
   - Empty/small (<bucket_size) -> 0.0.
   - All buys or all sells in buckets -> behavior validated (abs(diff)/total bounded).
   - Mixed NaN/inf sizes filtered.
   - bucket_size<=0 or invalid -> 0.0 or safe default.
   - Multiple bucket configurations, num_buckets edge cases.
   - Cross-check with existing behavior where reasonable.

3. **Verification**: All tests must pass (maintain >=88 passing). No placeholders/TODOs/FIXMEs/HACKs.

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
- [x] Orderflow imbalance at multiple horizons with decay weighting (EXTEND TESTS + HARDEN) — COMPLETE 2026-10-28T09:44:15Z
- [x] Footprint/orderflow divergence metrics (deepen tests beyond current) — COMPLETE 2026-10-28T10:15:30Z
- [ ] **VPIN-style toxicity proxy with finite-sample guards (deepen property tests) ← CURRENT TARGET**
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
- `src/features/orderflow.py` — hardened across all orderflow functions (delta, imbalance multi-horizon w/ decay, divergence/absorption/aggressive flow, VPIN)
- `src/features/gamma_exposure.py` — full GEX stack, delta bands, gamma flip interpolation
- `src/features/volatility.py` — put/call ratio, IV skew, max pain
- `src/features/liquidity.py` — spread/mid/relative/effective spread, liquidity score, chain metrics
- `src/signals/composite.py` — regime-aware composite signal
- `src/backtest/engine.py` — event-driven backtest engine
- `src/data/schemas.py` — Pydantic schemas
- `tests/test_features.py` — comprehensive feature tests
- `tests/test_phase1_gamma_invariants.py` — gamma exposure property tests
- **All tests passing** (feature tests 19/19)

## MANDATE
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent.

## SOURCE OF TRUTH HIERARCHY
1. `research_state/durable_handoff.md` (THIS FILE - AUTHORITATIVE)
2. Earlier handoff files superseded.

EXECUTE NOW. START AT PHASE 2 NEXT ITEM. NO DELAY.
