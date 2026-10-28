# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T16:29:36Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 115 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting. Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- No blocked/inefficient sessions detected. Working tree clean.
- Fixed missing implementations for `calculate_iv_skew_term_structure` and gamma flip helpers to satisfy tests; all 115 tests passing.
- Mypy/type coverage maintained clean per project policy.

## Initial Task Message (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

START IMMEDIATELY AT PHASE 7 (NEXT ITEM). Pick ONE highest-impact uncompleted item and implement it FULLY with tests. Do NOT split; complete end-to-end. Leave heavy work for the next agent.

HIGHEST-IMPACT ITEM: Docstrings for complex calculations (Phase 7)
- Scope (COMPLETE FULLY):
  1. Audit all public functions/classes in src/ for missing/incomplete docstrings on complex calculations (GEX/gamma flip, orderflow/VPIN/cumulative delta, surface/skew/term structure/max pain, regime/signals, backtesting, data/schemas, utils). Add rigorous docstrings explaining math, conventions (signs), inputs/outputs, edge cases, and numerical-stability guards.
  2. Focus especially on: src/features/gamma_exposure.py, src/features/orderflow.py, src/features/volatility.py, src/features/signals.py, src/backtesting/*.py, src/regime/*.py, src/data/*.py, src/main.py (public APIs).
  3. Keep pytest green (115+ passing) and mypy --disallow-untyped-defs --warn-return-any clean. No placeholders/TODOs/FIXMEs.
  4. After docstrings complete, continue Phase 7: more specific exception types + structured logging.

## Immediate Objectives
- Close Phase 7 docstrings fully with tests/static checks green.
- Maintain 115+ tests passing; mypy clean; working tree clean.
- Eliminate any future ambiguity by keeping this handoff as the single source of truth.

## Next Focus Campaign (MANDATORY — NEVER AVOID HEAVY WORK)
### Phase 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING — COMPLETE
- [x] Net gamma exposure, gamma notional by delta bands, gamma flip, invariants/tests
### Phase 2: DEEP ORDERFLOW MICROSTRUCTURE — COMPLETE
- [x] Cumulative delta robust, VWAP-adjusted delta, signed volume; multi-horizon imbalance; VPIN; absorption
### Phase 3: VOLATILITY SURFACE & SKEW QUANTIFICATION — COMPLETE
- [x] IV skew term structure, put-call skew, risk reversal, max pain, ATM term structure
### Phase 4: REGIME-AWARE SIGNAL ENGINEERING — COMPLETE
- [x] Cross-feature interactions, confidence calibration, regime detection, normalization
### Phase 5: BACKTEST RIGOR & RISK — COMPLETE
- [x] Realistic fill/slippage, walk-forward/rolling/OOS stability, drawdown controls, SL/TP, stress, tx costs, partial fills, round lots
### Phase 6: INTEGRATION, RESILIENCE & TESTS — CLOSED
- [x] End-to-end pipeline tests; property-based/numeric invariant tests; campaign resume + non-finite serialization guards; vectorization audit
### Phase 7: PRODUCTION READINESS — IN PROGRESS
- [x] Performance benchmarks for hot paths (GEX, orderflow, backtest equity curve) — COMPLETE
- [x] Type-hint coverage across src/ — COMPLETE
- [ ] Docstrings for complex calculations — START NOW (HEAVIEST IMPACT NEXT)
- [ ] More specific exception types + structured logging — AFTER DOCSTRINGS

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for the next agent. Never stop at scaffolding. Prioritize strictly by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes (python -m pytest). Maintain passing state (currently 115 passing).
- Run static type checks (python -m mypy src/ --disallow-untyped-defs --warn-return-any). Keep clean.
- Fix inefficiencies/blockers immediately before moving on.
- Leave a clear, timestamped handoff for the next agent if work remains.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T16-29-36Z.md (AUTHORITATIVE — THIS FILE)
2. research_state/durable_handoff.md (MIRROR — UPDATE TO SAME CONTENT)
3. research_state/INITIAL_TASK_HANDOFF.md (MIRROR — UPDATE TO SAME CONTENT; referenced by tests/test_campaign_resume.py)
4. Prior LATEST files superseded.

EXECUTE NOW. START AT PHASE 7 (DOCSTRINGS FOR COMPLEX CALCULATIONS). NO DELAY. DO HEAVY WORK.
