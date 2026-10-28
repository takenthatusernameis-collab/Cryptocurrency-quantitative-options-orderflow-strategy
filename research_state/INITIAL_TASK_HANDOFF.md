# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T13:32:59Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 110 TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting. Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- No blocked/inefficient sessions detected. Working tree clean (git status: nothing to commit, branch up-to-date with origin/main).
- Removed handoff-format bottleneck: research_state/INITIAL_TASK_HANDOFF.md now carries the required "Initial Task Message", "Immediate Objectives", "Next Focus Campaign", and "MANDATE" sections (tests/test_campaign_resume.py green).
- Phases 1-5 complete. Phase 6 CLOSED: vectorization audit fully implemented with equivalence tests (tests/test_vectorization_audit.py) asserting numerical parity between vectorized and scalar paths for gamma exposure, orderflow, volatility surface, and liquidity hot paths; all public vectorized entry points exported via src/features/__init__.py; backtest per-tick loop documented as intrinsic/event-driven (not a gap) — walk-forward/rolling-window backtest already implemented in src/backtest/engine.py, do NOT re-implement.
- No TODO/FIXME/HACK/PLACEHOLDER markers in src/ or tests/.

## IMMEDIATE TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

START IMMEDIATELY AT PHASE 7. Pick ONE highest-impact uncompleted item and implement it FULLY with tests. Do NOT split; complete end-to-end. Leave heavy work for the next agent.

HIGHEST-IMPACT ITEM: Performance benchmarks for hot paths (GEX, orderflow, backtest equity curve) — Phase 7 opener
- Scope (COMPLETE FULLY):
  1. Add a benchmark suite measuring throughput/latency of calculate_total_gex, calculate_total_delta_weighted_gex, calculate_orderflow_imbalance_multi_horizon, calculate_iv_skew_term_structure, and BacktestEngine equity-curve walk-forward over realistic chain/trade sizes.
  2. Assert benchmarks complete within defined SLOs (e.g., GEX over 10k quotes < 50ms; orderflow over 100k trades < 100ms; walk-forward 252/63 windows < 5s) and record baseline timings.
  3. No regressions: keep 97+ tests passing; run pytest after changes.
  4. No placeholders/TODOs/FIXMEs. All new code tested.
  5. Once benchmarks are green, Phase 7 continues: type-hint coverage across src/, docstrings for complex calculations, more specific exception types + structured logging.

## IMMEDIATE OBJECTIVES
- Close Phase 6 (DONE — vectorization audit green).
- Open Phase 7 production readiness starting with performance benchmarks for hot paths.
- Keep working tree clean; run pytest after every change; maintain 97+ passing tests.

## NEXT FOCUS CAMPAIGN (MANDATORY — NEVER AVOID HEAVY WORK)
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
### Phase 6: INTEGRATION, RESILIENCE & TESTS — CLOSED
- [x] End-to-end pipeline tests (ingestion->features->signals->backtest)
- [x] Property-based/numeric invariant tests + explicit finite checks across features
- [x] Campaign resume + non-finite serialization guards
- [x] Vectorization audit (FINAL ITEM — COMPLETE; equivalence tests in tests/test_vectorization_audit.py)
### Phase 7: PRODUCTION READINESS (NEXT FOCUS CAMPAIGN — START NOW)
- [ ] Performance benchmarks for hot paths (GEX, orderflow, backtest equity curve) — START NOW
- [ ] Type-hint coverage across src/
- [ ] Docstrings for complex calculations
- [ ] More specific exception types + structured logging

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent. Never stop at scaffolding.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes (python -m pytest). Maintain passing state (currently 110 passing).
- Fix inefficiencies/blockers immediately before moving on.
- Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T13-29-28Z.md (AUTHORITATIVE — mirror content here)
2. research_state/durable_handoff.md (MIRROR — UPDATE TO SAME CONTENT)
3. research_state/INITIAL_TASK_HANDOFF.md (MIRROR — UPDATE TO SAME CONTENT; referenced by tests/test_campaign_resume.py)
4. Prior LATEST files superseded.

EXECUTE NOW. START AT PHASE 7 (PERFORMANCE BENCHMARKS). NO DELAY. DO HEAVY WORK.
