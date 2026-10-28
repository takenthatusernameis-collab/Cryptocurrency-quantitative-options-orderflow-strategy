# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-28T21-39-45Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 115 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION (PRIORITIZED)
"Cryptocurrency-quantitative-options-orderflow-strategy" — prioritize in this strict order:
1. **Dealer positioning / gamma exposure** (gamma, gamma flip, net GEX, notional by bands) — core edge
2. **Orderflow microstructure** (signed volume, cumulative delta, VPIN/toxicity, absorption, aggressive flow) — flow confirmation
3. **Volatility surface dynamics** (skew/term structure/RR, ATM term structure, max pain) — regime/context
4. **Regime-aware signal engineering** (cross-features, calibration, normalization) — actionable signals
5. **Rigorous backtesting** (fills/slippage/costs/partial/round lots/walk-forward/OOS/stress) — ground truth

Everything must serve (1)-(5). Numerical correctness > elegance. No shortcuts.

## Initial Task Message (FOR NEXT AGENTIC WORK SESSION — MANDATORY, NON-OPTIONAL)
EXECUTE NOW. START AT PHASE 8 (PRODUCTION TELEMETRY & STRESS COVERAGE). Pick ONE highest-impact uncompleted item and COMPLETE IT END-TO-END (code + tests). Do not split scope. Leave heavy work for the next agent.

**HIGHEST-IMPACT ITEM: Expand stress coverage / OOS / walk-forward robustness comprehensively**
Scope (COMPLETE FULLY):
1. **Stress scenarios**: Add adversarial inputs (empty frames, NaN/Inf cascades, extreme sizes, all-same-side flow) across gamma/orderflow/surface/backtest; assert no NaN/Inf propagation and proper error context.
2. **OOS & walk-forward**: Harden walk-forward splits, ensure no lookahead, sanitize metrics with allow_nan=False; determinism seeds propagated; tests for reproducibility.
3. **Telemetry/guardrails**: Structured logging of violations, metrics sanitization, serialization guards (SerializationError) end-to-end; verify JSON validity.
4. **Config validation**: Further harden edge cases for venues/risk/backtest params; defaults safe; dict & object forms.
5. **Numerical guards**: Insufficient cash, short-notional breach, risk limits raising RiskLimitError/OrderError; log via structured logger.
6. **Quant-precise docstrings** for all new guards. Full implementation + tests. Keep pytest green (115+). Keep mypy clean.

## Immediate Objectives
- Finish Phase 8 stress/OOS/walk-forward hardening comprehensively.
- Maintain green tests and clean mypy.
- Keep working tree clean.
- Never stop at scaffolding.

## Next Focus Campaign (MANDATORY — NEVER AVOID HEAVY WORK)
### Phase 1: COMPLETE - Data ingestion/resilience
### Phase 2: COMPLETE - Normalization & canonical schemas
### Phase 3: COMPLETE - Features (gamma, orderflow, volatility, max pain)
### Phase 4: COMPLETE - Regime-aware signal engineering
### Phase 5: COMPLETE - Rigorous backtesting
### Phase 6: COMPLETE - Integration/resilience/tests
### Phase 7: COMPLETE - Production readiness (final hardening pass)
### Phase 8: PRODUCTION TELEMETRY & STRESS COVERAGE — IN PROGRESS (HEAVY WORK MANDATORY)
- [ ] Stress scenarios across all modules
- [ ] OOS & walk-forward robustness
- [ ] Telemetry/guardrails & serialization end-to-end
- [ ] Numerical guards & config validation edge cases

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for the next agent. Never stop at scaffolding. Prioritize strictly by project name.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes: python -m pytest (maintain 115+ passing).
- Run static checks: python -m mypy src/ --disallow-untyped-defs --warn-return-any (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains.
- DO NOT avoid heavy work. Execute in order without skipping.
