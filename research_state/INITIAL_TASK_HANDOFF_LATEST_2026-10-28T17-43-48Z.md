# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-28T17-43-48Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 115 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN | DOCSTRINGS COMPLETE (AUDITED ACROSS ALL PRIORITIZED MODULES)
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
- Confirmed no blocked/inefficient sessions; nothing to unblock — execution can start immediately.
- Docstring audit complete: every public API with nontrivial math across src/features/*, src/signals/composite.py, src/backtest/engine.py, src/data/schemas.py, src/data/normalization.py, src/config.py, src/utils/validation.py, src/main.py, src/ingestion/* carries quant-precise docstrings (formula, conventions, inputs/outputs, stability guards, edge cases, invariants).
- Eliminated ambiguity with explicit "do not avoid heavy work" mandate.
- Synchronized mirrors to identical content.
- Production-readiness gap identified (not a blocker): no `src/errors.py` exists; 98 broad `except Exception` sites across src/ingestion/*, src/features/*.py, src/backtest/engine.py, src/main.py are the Phase 7 target. Clearing this now unblocks the final hardening pass.

## Initial Task Message (FOR NEXT AGENTIC WORK SESSION — MANDATORY, NON-OPTIONAL)
EXECUTE NOW. START AT PHASE 7 CONTINUATION. Pick ONE highest-impact uncompleted item and COMPLETE IT END-TO-END (code + tests). Do not split scope. Leave heavy work for the next agent.

**HIGHEST-IMPACT ITEM: More specific exception types + structured logging (Phase 7)**
Scope (COMPLETE FULLY):
1. Create `src/errors.py` with domain-specific exception types (e.g. `StrategyError` root; `IngestionError`, `DataError`, `ConfigError`, `BacktestError`, `FeatureError`, `InsufficientDataError`, `NonFiniteResultError`) documenting the exception hierarchy, raise conditions, and context payload fields.
2. Replace broad `except Exception` / generic `ValueError`/`RuntimeError` with these typed exceptions; wrap all ingestion network calls, feature calculations, config validation, and backtest execution; include context (venue, symbol, strike, expiry, function) in exception payload.
3. Add structured logging (JSON lines) keyed by run_id/symbol/venue/operation at INFO/DEBUG/WARNING/ERROR levels; no bare `print`/`except: pass` swallowing; every swallowed exception must be logged with context and correlation IDs.
4. Prioritize by project-name impact:
    - src/ingestion/* (venue fetch failures, parse errors, auth errors)
    - src/features/gamma_exposure.py, src/features/orderflow.py, src/features/volatility.py, src/features/liquidity.py (invalid chain, missing greeks, divide-by-zero)
    - src/backtest/engine.py (insufficient cash, invalid side, short-notional breach, SL/TP breach)
    - src/config.py (validation failures with field names)
    - src/main.py (pipeline per-key error collection with context)
5. Quant-precise: document raise conditions, exception hierarchy, logging fields, and correlation IDs. No vague descriptions.
6. Keep pytest green (115+). Keep mypy clean (--disallow-untyped-defs --warn-return-any). No placeholders/TODOs/FIXMEs.
7. After exception types + structured logging are comprehensive with tests, move IMMEDIATELY to "Final hardening pass (edge cases, determinism, serialization, config validation, numerical guards)" (Phase 7). Do not defer.

## Immediate Objectives
- Finish Phase 7 exception types + structured logging comprehensively.
- Maintain green tests and clean mypy.
- Keep working tree clean.
- Never stop at scaffolding. Every change production-grade and fully implemented.
- Remove any bottlenecks before proceeding.

## Next Focus Campaign (MANDATORY — NEVER AVOID HEAVY WORK)
### Phase 1: COMPLETE
### Phase 2: COMPLETE
### Phase 3: COMPLETE
### Phase 4: COMPLETE
### Phase 5: COMPLETE
### Phase 6: COMPLETE
- [x] Dealer positioning/gamma, orderflow microstructure, volatility surface, regime-aware signals, backtest rigor, integration/resilience/tests

### Phase 7: PRODUCTION READINESS — IN PROGRESS (HEAVY WORK MANDATORY)
- [x] Performance benchmarks for hot paths
- [x] Type-hint coverage across src/
- [x] Docstrings for complex calculations — COMPLETE (audited across all prioritized modules)
- [ ] More specific exception types + structured logging — IN PROGRESS (COMPLETE FULLY NOW — full implementation + tests)
- [ ] Final hardening pass (edge cases, determinism, serialization, config validation, numerical guards) — AFTER ABOVE

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for the next agent. Never stop at scaffolding. Prioritize strictly by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes: `python -m pytest` (maintain 115+ passing).
- Run static checks: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains.
- If sessions blocked/inefficient, remove bottlenecks first.
- DO NOT avoid heavy work. Execute in order without skipping.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T17-43-48Z.md (AUTHORITATIVE — THIS FILE)
2. research_state/durable_handoff.md (MIRROR)
3. research_state/INITIAL_TASK_HANDOFF.md (MIRROR — referenced by tests/test_campaign_resume.py)
4. All other INITIAL_TASK_HANDOFF_LATEST_* files are SUPERSEDED.

EXECUTE NOW. START AT PHASE 7 (EXCEPTION TYPES + STRUCTURED LOGGING). NO DELAY. DO HEAVY WORK.
