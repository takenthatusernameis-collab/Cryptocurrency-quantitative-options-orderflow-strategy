# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T09:40:45Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 87 TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- Confirmed clean working tree (git status: nothing to commit, branch up-to-date with origin/main).
- Verified 87/87 tests pass in 0.52s. No TODO/FIXME/HACK/PLACEHOLDER markers remain in src/ or tests/.
- Confirmed Phase 2 first major item (deep orderflow microstructure) is fully implemented and tested.
- No blocked or inefficient sessions remain. Ready for next heavy engineering campaign.

## Initial Task Message (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

START IMMEDIATELY AT PHASE 2 - NEXT ITEM.
Pick the HIGHEST-IMPACT uncompleted item in Phase 2 and implement it FULLY with tests.
HIGHEST-IMPACT ITEM: Orderflow imbalance at multiple horizons with decay weighting — EXTEND AND HARDEN. Functions exist (orderflow_imbalance_multi_horizon/imbalance_multi_horizon) but need deeper property/invariant tests (normalization, decay behavior, empty/edge cases), ensure numerical stability, and add any missing aggregations/aliases. Also consider cross-consistency with calculate_orderflow_imbalance. YOUR JOB: extend tests + harden implementation (guards, finite checks, clamping) as needed. NO cosmetic changes. NO placeholders/TODOs/FIXMEs. NO scaffolding.
Mathematical correctness is MANDATORY. Numerical stability is MANDATORY. Vectorize where sensible. Complete ONE major item fully; leave heavy work for next agent.

## Immediate Objectives
- Extend and harden orderflow imbalance at multiple horizons with decay weighting.
- Add property/invariant tests for normalization, decay behavior, empty/edge cases.
- Ensure numerical stability, finite checks, clamping; add missing aggregations/aliases.
- Maintain 87+ tests passing; no placeholders/TODOs/FIXMEs.

## Next Focus Campaign (MANDATORY — NEVER AVOID HEAVY WORK)
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

## VERIFIED CODEBASE STATE
- src/features/orderflow.py:360 — all orderflow functions, hardened, aliases present.
- src/features/gamma_exposure.py:330 — full GEX stack, delta bands, gamma flip interpolation.
- src/features/volatility.py:80 — put/call ratio, IV skew, max pain (basic; needs Phase 3).
- src/features/liquidity.py:127 — spread, mid, relative/effective spread, liquidity score, chain metrics.
- src/signals/composite.py:200 — regime-aware composite signal generator with confidence calibration.
- src/backtest/engine.py:439 — event-driven backtest engine.
- src/data/schemas.py:78 — Pydantic schemas.
- tests/test_features.py:399 — comprehensive feature tests including orderflow invariants.
- 87 tests total, all passing.

## MANDATE
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent.

## SOURCE OF TRUTH HIERARCHY
1. research_state/durable_handoff.md (AUTHORITATIVE, TIMESTAMPED 2026-10-28T09:40:45Z)
2. Earlier LATEST files superseded.

EXECUTE NOW. START AT PHASE 2 NEXT ITEM. NO DELAY.
