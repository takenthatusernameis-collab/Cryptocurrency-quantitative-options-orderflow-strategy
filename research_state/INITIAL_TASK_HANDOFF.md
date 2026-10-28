# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-28T17:30:56Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 115 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting. Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- Verified handoff chain intact; all handoff mirrors synchronized.
- Confirmed 115 tests passing, mypy clean across src/ with strict flags.
- Working tree clean; no untracked artifacts blocking agents.
- Eliminated ambiguity by consolidating to single source of truth with explicit next actions.

## Initial Task Message (FOR NEXT AGENTIC WORK SESSION — MANDATORY)
EXECUTE NOW. START AT PHASE 7 CONTINUATION. Pick ONE highest-impact uncompleted item and implement it FULLY with tests. Do NOT split; complete end-to-end. Leave heavy work for the next agent.

HIGHEST-IMPACT ITEM: Complete docstrings for complex calculations (Phase 7 - Docstrings)
- Scope (COMPLETE FULLY — DO NOT LEAVE PARTIAL):
  1. Audit and add rigorous docstrings for all public APIs with nontrivial math. Every complex calculation must document: formula/logic, conventions (signs/units), inputs/outputs, numerical stability guards, edge cases, and references to invariants.
  2. Prioritize by impact: src/features/gamma_exposure.py (GEX, gamma flip, notional by bands), src/features/orderflow.py (cumulative delta, VWAP-adjusted delta, VPIN, absorption), src/features/volatility.py (skew/risk reversal/term structure/max pain/ATM), src/signals/composite.py, src/backtest/engine.py (fills/slippage/costs/walk-forward), src/data/schemas.py, src/data/normalization.py, src/ingestion/*, src/config.py, src/utils/validation.py, src/main.py.
  3. Ensure docstrings are precise for quant audiences (state assumptions, clipping/guards, floating point behavior). No vague "calculates X" descriptions.
  4. Keep pytest green (115+ passing) and mypy --disallow-untyped-defs --warn-return-any clean. No placeholders/TODOs/FIXMEs.
  5. After completing docstrings comprehensively, move to: "More specific exception types + structured logging" (Phase 7 remaining).

## Immediate Objectives
- Finish Phase 7 docstrings to a state where no complex public calculation lacks a rigorous docstring.
- Maintain 115+ tests passing; mypy clean; working tree clean.
- Remove any remaining ambiguity; keep this handoff as single source of truth.

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
### Phase 7: PRODUCTION READINESS — IN PROGRESS (HEAVY WORK MANDATORY)
- [x] Performance benchmarks for hot paths (GEX, orderflow, backtest equity curve)
- [x] Type-hint coverage across src/
- [ ] Docstrings for complex calculations — IN PROGRESS (START/CONTINUE NOW)
- [ ] More specific exception types + structured logging — NEXT AFTER DOCSTRINGS
- [ ] Final hardening pass (edge cases, determinism, serialization, config validation) — AFTER ABOVE

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for the next agent. Never stop at scaffolding. Prioritize strictly by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes (python -m pytest). Maintain passing state (currently 115 passing).
- Run static type checks (python -m mypy src/ --disallow-untyped-defs --warn-return-any). Keep clean.
- Fix inefficiencies/blockers immediately before moving on.
- Leave a clear, timestamped handoff for the next agent if work remains.
- If sessions appear blocked/inefficient, remove bottlenecks (tooling/env/issues) before proceeding.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T17-30-56Z.md (AUTHORITATIVE — THIS FILE)
2. research_state/durable_handoff.md (MIRROR — UPDATE TO SAME CONTENT)
3. research_state/INITIAL_TASK_HANDOFF.md (MIRROR — UPDATE TO SAME CONTENT; referenced by tests/test_campaign_resume.py)
4. Prior LATEST files superseded.

EXECUTE NOW. START AT PHASE 7 (DOCSTRINGS FOR COMPLEX CALCULATIONS). NO DELAY. DO HEAVY WORK.
