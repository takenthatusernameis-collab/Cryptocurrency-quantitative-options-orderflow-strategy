# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T13:26:04Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 97 TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting. Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- No blocked/inefficient sessions detected. Working tree clean (git status: nothing to commit, branch up-to-date with origin/main).
- 97/97 tests passing (pytest, 0.56s). No TODO/FIXME/HACK/PLACEHOLDER markers in src/ or tests/.
- Phases 1-5 complete: gamma exposure, orderflow microstructure, volatility/skew, regime-aware signals, backtest rigor (fill/slippage, walk-forward/rolling, drawdown controls, stress/tx costs/partial fills/round lots).
- Walk-forward/rolling-window backtest already implemented in src/backtest/engine.py (WalkForwardBacktest, run_walk_forward, run_rolling_window_backtest) with tests — do NOT re-implement.
- Phase 6 substantially complete: end-to-end pipeline integration tests (tests/test_pipeline_integration.py), campaign resume/handoff integrity (tests/test_campaign_resume.py), non-finite serialization guards (tests/test_nonfinite_result_serialization.py), JSON allow_nan=False sanitization (src/main.py:282), config validation (src/config.py:validate_config).

## Initial Task Message (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

START IMMEDIATELY AT PHASE 6 COMPLETION. Pick ONE highest-impact uncompleted item and implement it FULLY with tests. Do NOT split; complete end-to-end. Leave heavy work for the next agent.

HIGHEST-IMPACT ITEM: Vectorization audit + Phase 6 closure (features/signals/backtest)
- Scope (COMPLETE FULLY):
  1. Vectorization audit: survey src/features/*.py, src/signals/composite.py, src/backtest/engine.py for remaining Python loops; vectorize with numpy where semantics unchanged and the win is meaningful (features are already vectorized; backtest is event-driven by design — document that the per-tick loop is intrinsic, not a gap).
  2. Add tests for any behavior change from vectorization; assert numerical equivalence vs scalar path where both exist.
  3. Confirm all public vectorized entry points are exported via relevant __init__.py files; follow existing style.
  4. No placeholders/TODOs/FIXMEs. All new code tested. Keep 97+ tests passing.
  5. Once the vectorization audit is green, Phase 6 is CLOSED; the next agent begins Phase 7 (production readiness: performance benchmarks, type-hint coverage, docstrings for complex calculations, error-handling specificity).

## Immediate Objectives
- Complete the vectorization audit end-to-end with tests.
- Close Phase 6 (integration, resilience & tests).
- Maintain 97+ tests passing; working tree clean; no scaffolding.

## Next Focus Campaign (MANDATORY — NEVER AVOID HEAVY WORK)
### Phase 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING — COMPLETE
- [x] Net gamma exposure, gamma notional by delta bands, gamma flip, invariants/tests
### Phase 2: DEEP ORDERFLOW MICROSTRUCTURE — COMPLETE
- [x] Cumulative delta robust, VWAP-adjusted delta, signed volume; multi-horizon imbalance with decay weighting; VPIN-style toxicity; absorption/detection
### Phase 3: VOLATILITY SURFACE & SKEW QUANTIFICATION — COMPLETE
- [x] IV skew term structure, put-call skew, risk reversal, max pain, ATM term structure
### Phase 4: REGIME-AWARE SIGNAL ENGINEERING — COMPLETE
- [x] Cross-feature interactions, confidence calibration, regime detection, normalization
### Phase 5: BACKTEST RIGOR & RISK — COMPLETE
- [x] Realistic fill/slippage, walk-forward/rolling/OOS stability, drawdown controls, SL/TP, stress, tx costs, partial fills, round lots
### Phase 6: INTEGRATION, RESILIENCE & TESTS — IN PROGRESS (FINAL ITEM)
- [x] End-to-end pipeline tests (ingestion->features->signals->backtest)
- [x] Property-based/numeric invariant tests + explicit finite checks across features
- [x] Campaign resume + non-finite serialization guards
- [ ] Vectorization audit (FINAL ITEM — START NOW)
### Phase 7: PRODUCTION READINESS (NEXT AFTER PHASE 6 CLOSES)
- [ ] Performance benchmarks for hot paths (GEX, orderflow, backtest equity curve)
- [ ] Type-hint coverage across src/
- [ ] Docstrings for complex calculations
- [ ] More specific exception types + structured logging

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent. Never stop at scaffolding.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes (python -m pytest). Maintain passing state (currently 97 passing).
- Fix inefficiencies/blockers immediately before moving on.
- Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T13-26-04Z.md (AUTHORITATIVE - THIS FILE)
2. research_state/durable_handoff.md (MIRROR - UPDATE TO SAME CONTENT)
3. research_state/INITIAL_TASK_HANDOFF.md (MIRROR - UPDATE TO SAME CONTENT; referenced by tests/test_campaign_resume.py)
4. Prior LATEST files superseded.

EXECUTE NOW. START AT PHASE 6 FINAL ITEM (VECTORIZATION AUDIT). NO DELAY. DO HEAVY WORK.
