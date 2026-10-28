# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): ${ts}
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 115 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN | DOCSTRINGS COMPLETE (AUDITED) | EXCEPTION HIERARCHY + STRUCTURED LOGGING IMPLEMENTED
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
- Added comprehensive domain exception hierarchy in `src/errors.py` (StrategyError root, IngestionError/NetworkError/AuthError/ParseError, DataError/InsufficientDataError, ConfigError, BacktestError/RiskLimitError/OrderError, FeatureError/NonFiniteResultError, ValidationError, SerializationError, DeterminismError) with contextual payloads and structured logging via `StructuredLogger`/`get_logger` (JSON lines, correlation fields, exc merging).
- Replaced broad `except Exception` patterns with typed exceptions and structured logging across ingestion (deribit/binance/okx), main pipeline, and config validation.
- Config validation now raises `ConfigError` with logged context; main catches both `ValueError` and `ConfigError`.
- All modules pass strict mypy; all tests pass (115).

## Initial Task Message (FOR NEXT AGENTIC WORK SESSION — MANDATORY, NON-OPTIONAL)
EXECUTE NOW. START AT PHASE 7 CONTINUATION. Pick ONE highest-impact uncompleted item and COMPLETE IT END-TO-END (code + tests). Do not split scope. Leave heavy work for the next agent.

**HIGHEST-IMPACT ITEM: Final hardening pass (edge cases, determinism, serialization, config validation, numerical guards) (Phase 7)**
Scope (COMPLETE FULLY):
1. **Edge cases**: Harden gamma/VPIN/cumulative delta against empty/NaN/Inf, division by zero, missing greeks; ensure all feature functions enforce finiteness and raise `NonFiniteResultError`/`FeatureError` with context where appropriate.
2. **Determinism**: Audit RNG usage (backtest slippage/partial fills) — ensure seeded determinism; add `DeterminismError` guards if non-deterministic paths detected; tests for reproducibility.
3. **Serialization**: Ensure all pipeline outputs JSON-serializable with `allow_nan=False`; harden `main.py` sanitization and add serialization guards using `SerializationError` where needed.
4. **Config validation**: Extend validation coverage (venues, risk limits, numeric ranges) with precise field errors; ensure defaults safe.
5. **Numerical guards**: Add guards in backtest engine (insufficient cash, short-notional breach, risk limits) raising `RiskLimitError`/`OrderError` with context; log violations.
6. Quant-precise docstrings for all guards. Full implementation + tests. Keep pytest green (115+). Keep mypy clean.
7. After completion, verify end-to-end pipeline still produces valid JSON and metrics stable.

## Immediate Objectives
- Finish Phase 7 final hardening pass comprehensively.
- Maintain green tests and clean mypy.
- Keep working tree clean.
- Never stop at scaffolding. Every change production-grade and fully implemented.
- Remove any bottlenecks before proceeding.

## Next Focus Campaign (MANDATORY — NEVER AVOID HEAVY WORK)
### Phase 1-6: COMPLETE
- Dealer positioning/gamma, orderflow microstructure, volatility surface, regime-aware signals, backtest rigor, integration/resilience/tests

### Phase 7: PRODUCTION READINESS — IN PROGRESS
- [x] Performance benchmarks for hot paths
- [x] Type-hint coverage across src/
- [x] Docstrings for complex calculations — COMPLETE (audited across all prioritized modules)
- [x] More specific exception types + structured logging — COMPLETE
- [ ] Final hardening pass (edge cases, determinism, serialization, config validation, numerical guards) — NEXT (HEAVY WORK MANDATORY)

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
1. research_state/INITIAL_TASK_HANDOFF_LATEST_${ts}.md (AUTHORITATIVE — THIS FILE)
2. research_state/durable_handoff.md (MIRROR)
3. research_state/INITIAL_TASK_HANDOFF.md (MIRROR — referenced by tests/test_campaign_resume.py)
4. All other INITIAL_TASK_HANDOFF_LATEST_* files are SUPERSEDED.

EXECUTE NOW. START AT PHASE 7 (FINAL HARDENING PASS). NO DELAY. DO HEAVY WORK.
