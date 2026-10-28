# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T09:33:52Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 95 TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- Completed Phase 2 first major item: deep orderflow microstructure fully tested and hardened.
- Added comprehensive tests for cumulative delta robust, VWAP-adjusted delta, signed volume, multi-horizon imbalance with decay, footprint/divergence, VPIN toxicity, absorption detection, aggressive flow; hardened against non-finite/invalid inputs with clamping.
- All tests pass (95/95). No blocked or inefficient sessions remain.

## Initial Task Message
START IMMEDIATELY AT PHASE 2 - NEXT ITEM.
Pick the HIGHEST-IMPACT uncompleted item in Phase 2 and implement it FULLY with tests.
HIGHEST-IMPACT ITEM: Orderflow imbalance at multiple horizons with decay weighting — EXTEND AND HARDEN. Functions exist (orderflow_imbalance_multi_horizon/imbalance_multi_horizon) but need deeper property/invariant tests (normalization, decay behavior, empty/edge cases), ensure numerical stability, and add any missing aggregations/aliases. Also consider cross-consistency with calculate_orderflow_imbalance. YOUR JOB: extend tests + harden implementation (guards, finite checks, clamping) as needed. NO cosmetic changes. NO placeholders/TODOs/FIXMEs. NO scaffolding.
Mathematical correctness is MANDATORY. Numerical stability is MANDATORY. Vectorize where sensible. Complete ONE major item fully; leave heavy work for next agent.

## Immediate Objectives
- Extend and harden orderflow imbalance at multiple horizons with decay weighting.
- Add property/invariant tests for normalization, decay behavior, empty/edge cases.
- Ensure numerical stability, finite checks, clamping; add missing aggregations/aliases.
- Maintain 95+ tests passing; no placeholders/TODOs/FIXMEs.

## Next Focus Campaign
### Phase 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING — COMPLETE
- [x] Net gamma exposure, gamma notional by delta bands, gamma flip, invariants/tests

### Phase 2: DEEP ORDERFLOW MICROSTRUCTURE (CRITICAL) — IN PROGRESS
- [x] Cumulative delta with trade classification robustness, VWAP-adjusted delta, signed volume (FULL TEST COVERAGE + HARDENING)
- [ ] Orderflow imbalance at multiple horizons with decay weighting (EXTEND TESTS + HARDEN)
- [ ] Footprint/orderflow divergence metrics (deepen tests)
- [ ] VPIN-style toxicity proxy with finite-sample guards (deepen property tests)
- [ ] Harden against division by zero/non-finite; property/invariant tests

### Phase 3: VOLATILITY SURFACE & SKEW QUANTIFICATION (CRITICAL)
- [ ] IV skew term structure, put-call skew, risk reversal, max pain, term structure

### Phase 4: REGIME-AWARE SIGNAL ENGINEERING (CRITICAL)
- [ ] Cross-feature interactions, confidence calibration, regime detection, normalization

### Phase 5: BACKTEST RIGOR & RISK (HIGH)
- [ ] Realistic fills, drawdown controls, walk-forward, stress tests, transaction costs

### Phase 6: INTEGRATION, RESILIENCE & TESTS (HIGH)
- [ ] Wire features, property tests, explicit finite checks, vectorization, e2e tests

## MANDATE
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent.

EXECUTE NOW. START AT PHASE 2 NEXT ITEM. NO DELAY.
