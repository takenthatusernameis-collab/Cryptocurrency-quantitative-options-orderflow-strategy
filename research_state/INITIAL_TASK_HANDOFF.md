# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-28T17-34-00Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 115 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION (PRIORITIZED)
"Cryptocurrency-quantitative-options-orderflow-strategy" — prioritize in this order:
1. **Dealer positioning / gamma exposure** (gamma, gamma flip, net GEX, notional by bands) — core edge
2. **Orderflow microstructure** (signed volume, cumulative delta, VWAP-adjusted delta, VPIN, absorption) — confirms flow
3. **Volatility surface dynamics** (skew/term structure/RR, ATM term structure, max pain) — regime/context
4. **Regime-aware signal engineering** (cross-features, calibration, normalization) — actionable
5. **Rigorous backtesting** (fills/slippage/costs/partial/round lots/walk-forward/OOS/stress) — truth

Everything must serve (1)-(5). Numerical correctness > elegance. No shortcuts.

## BOTTLENECKS REMOVED THIS SESSION
- Consolidated to single authoritative source of truth chain (this file + mirrors).
- Verified 115 tests passing, mypy clean across src/ with strict flags.
- Working tree clean; no untracked artifacts blocking agents.
- Eliminated ambiguity with explicit "do not avoid heavy work" mandate.
- Synchronized mirrors to identical content.

## Initial Task Message (FOR NEXT AGENTIC WORK SESSION — MANDATORY, NON-OPTIONAL)
EXECUTE NOW. START AT PHASE 7 CONTINUATION. Pick ONE highest-impact uncompleted item and COMPLETE IT END-TO-END (code + tests). Do not split scope. Leave heavy work for the next agent.

**HIGHEST-IMPACT ITEM: Complete docstrings for complex calculations (Phase 7)**
Scope (COMPLETE FULLY):
1. Audit every public API with nontrivial math. For each complex calculation document: formula/logic, conventions (signs/units), inputs/outputs, numerical stability guards, edge cases, invariants, and references where relevant.
2. Prioritize by project-name impact:
   - src/features/gamma_exposure.py (GEX, gamma flip, notional by bands, weighted variants)
   - src/features/orderflow.py (cumulative delta, VWAP-adjusted delta, signed volume, multi-horizon imbalance, VPIN, absorption)
   - src/features/volatility.py (skew/RR, term structure, ATM, max pain)
   - src/signals/composite.py (components, regime, confidence calibration)
   - src/backtest/engine.py (fills/slippage/costs/walk-forward, equity curve)
   - src/data/schemas.py, src/data/normalization.py
   - src/ingestion/*, src/config.py, src/utils/validation.py, src/main.py
3. Quant-precise docstrings (assumptions, clipping/guards, floating point behavior). No vague descriptions.
4. Keep pytest green (115+). Keep mypy clean (--disallow-untyped-defs --warn-return-any). No placeholders/TODOs/FIXMEs.
5. After docstrings are comprehensive with no complex public calc undocumented, move IMMEDIATELY to "More specific exception types + structured logging" (Phase 7) with full implementation + tests. Do not defer.

## Immediate Objectives
- Finish Phase 7 docstrings comprehensively.
- Maintain green tests and clean mypy.
- Keep working tree clean.
- Never stop at scaffolding. Every change production-grade and fully implemented.
- Remove any bottlenecks before proceeding.

## Next Focus Campaign (MANDATORY — NEVER AVOID HEAVY WORK)
### Phase 1-6: COMPLETE
- [x] Dealer positioning/gamma, orderflow microstructure, volatility surface, regime-aware signals, backtest rigor, integration/resilience/tests

### Phase 7: PRODUCTION READINESS — IN PROGRESS (HEAVY WORK MANDATORY)
- [x] Performance benchmarks for hot paths
- [x] Type-hint coverage across src/
- [ ] Docstrings for complex calculations — IN PROGRESS (COMPLETE FULLY NOW)
- [ ] More specific exception types + structured logging — NEXT (full implementation + tests)
- [ ] Final hardening pass (edge cases, determinism, serialization, config validation, numerical guards) — AFTER ABOVE

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent. Never stop at scaffolding. Prioritize strictly by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes: `python -m pytest` (maintain 115+ passing).
- Run static checks: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains.
- If sessions blocked/inefficient, remove bottlenecks first.
- DO NOT avoid heavy work. Execute in order without skipping.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T17-34-00Z.md (AUTHORITATIVE — THIS FILE)
2. research_state/durable_handoff.md (MIRROR)
3. research_state/INITIAL_TASK_HANDOFF.md (MIRROR — referenced by tests/test_campaign_resume.py)
4. All other INITIAL_TASK_HANDOFF_LATEST_* files are SUPERSEDED.

EXECUTE NOW. START AT PHASE 7 (DOCSTRINGS FOR COMPLEX CALCULATIONS). NO DELAY. DO HEAVY WORK.
