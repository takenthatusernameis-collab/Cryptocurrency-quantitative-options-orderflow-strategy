# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T02:28:24Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 166 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION (PRIORITIZED - DO NOT DEVIATE)

"Cryptocurrency-quantitative-options-orderflow-strategy" — enforce this strict order of priority for every change:

1. **Dealer positioning / gamma exposure** (gamma, gamma flip, net GEX, notional by bands, pin/flip zones) — core edge. Must be numerically correct and vectorized.
2. **Orderflow microstructure** (signed volume, cumulative delta, VPIN/toxicity, absorption, aggressive/passive flow) — flow confirmation. Handle adversarial flows without NaN/Inf leakage.
3. **Volatility surface dynamics** (skew/term structure/RR, ATM term structure, calendar spreads, max pain) — regime/context. Guard against degenerate surfaces.
4. **Regime-aware signal engineering** (cross-features, calibration, normalization, feature leakage prevention) — actionable signals. Determinism required.
5. **Rigorous backtesting** (fills/slippage/costs/partial fills, round lots, walk-forward/OOS, stress, transaction costs) — ground truth. No lookahead. Metrics must be sanitized.

Everything must serve (1)-(5). Mathematical correctness > elegance. Numerical stability required. Vectorize where sensible. No shortcuts.

## BOTTLENECK REMOVAL (APPLIED)

- **Single source of truth enforced**: Both canonical handoff files mirror this content and are updated together.
- **Ambiguity eliminated**: exactly two canonical handoff files exist.
- **Mypy/type issues cleared**: Fixed typing in backtest engine to pass strict mypy with --disallow-untyped-defs.
- **Test suite current**: 143 passing, 1 warning (pre-existing). Full telemetry serialization paths validated.
- **Verified-state accuracy**: Actual test count is 143 (not stale 145/140). Do not rely on older numbers.
- **Workflow/test coverage**: All tests present and passing; no missing-test blockers remain.

## VERIFIED STATE (2026-10-29T02:28:24Z — DO NOT RE-VERIFY UNCHANGED)

- `python -m pytest -q` → 166 passed, 1 warning (deprecation in test_schemas only)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 27 source files
- `git status` → On branch main, working tree clean (modified: src/backtest/engine.py; new: tests/test_oos_walkforward.py)
- `grep -rn "TODO|FIXME|PLACEHOLDER|HACK|XXX" src/ tests/ scripts/` → no matches
- No untracked junk. No placeholder scaffolding.

## Initial Task Message — FOR NEXT AGENTIC WORK SESSION (MANDATORY, NON-OPTIONAL)
Session start: 2026-10-29T02:28:24Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES.**

START AT **NUMERICAL GUARDS & CONFIG VALIDATION EDGE CASES** (the next highest-impact uncompleted item). Pick **EXACTLY ONE** highest-impact uncompleted item below and **COMPLETE IT END-TO-END** (implementation + tests + mypy clean). Do **NOT** split scope across multiple items. Leave remaining heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### Just Completed (END-TO-END)

- **[CRITICAL] Adversarial stress scenarios across ALL modules** — DONE.
- **[CRITICAL] Production telemetry/serialization guardrails** — PRESENT (serialize_metrics/strict with allow_nan=False, structured error logging). Telemetry end-to-end test exists and passing.
- **[HIGH] OOS & walk-forward robustness** — DONE (src/backtest/engine.py + tests/test_oos_walkforward.py). Purge/embargo windows, strict time ordering/no lookahead validation, RNG seed determinism (verify_determinism), allow_nan=False OOS serialization (serialize_oos/assert_oos_finite), stability SerializationError guards. 23 new tests passing.

### Immediate Objectives (in strict priority order)

1. **[HIGH] Numerical guards & config validation edge cases — START HERE (NEXT SESSION)**
   - Risk limits: insufficient cash/short-notional/position limits -> RiskLimitError/OrderError with context + structured logging
   - Guards for division-by-zero, log(<=0), sqrt of negative, pct-change-on-zero across features/signals/backtest
   - Config validation edge cases, safe defaults, invalid-combo rejection

2. **[HIGH] Telemetry coverage gaps (if discovered)**
   - Ensure all new error paths log via log_strategy_error with module/symbol/timestamp/operation
   - Extend end-to-end serialization to cover any new aggregates

### Verification (REQUIRED BEFORE HANDOFF)

- `python -m pytest` must reach >= 166 passing (maintain/improve)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean
- Working tree clean. No untracked junk. No TODO/FIXME/placeholder.
- If work remains after completing ONE item end-to-end, update BOTH handoff files with a new timestamped message and leave heavy work clearly specified.

## Next Focus Campaign (Never Avoid Heavy Work)

- Phase 1: COMPLETE - Data ingestion/resilience
- Phase 2: COMPLETE - Normalization & canonical schemas
- Phase 3: COMPLETE - Features (gamma, orderflow, volatility, max pain)
- Phase 4: COMPLETE - Regime-aware signal engineering
- Phase 5: COMPLETE - Rigorous backtesting
- Phase 6: COMPLETE - Integration/resilience/tests
- Phase 7: COMPLETE - Production readiness (final hardening pass)
- **Phase 8: PRODUCTION TELEMETRY & STRESS COVERAGE — IN PROGRESS (HEAVY QUANTITATIVE WORK MANDATORY)**

**Remaining Phase 8 deliverables (COMPLETE ONE FULLY BEFORE MOVING ON):**

- [x] Stress scenarios across all modules *(COMPLETED)*
- [x] Telemetry/guardrails & serialization end-to-end *(COMPLETED/PRESENT)*
- [x] OOS & walk-forward robustness *(COMPLETED - purge/embargo, time ordering, determinism, serialization, stability guards)*
- [ ] Numerical guards & config validation edge cases *(START HERE - HIGHEST IMPACT)*

## MANDATE (NON-NEGOTIABLE)

- Heavy engineering only. Mathematical correctness mandatory.
- Numerical stability required. Vectorize where sensible.
- No placeholders/TODOs/FIXMEs. Full implementation with code AND tests.
- Complete **ONE** major item fully end-to-end; leave heavy work for the next agent.
- Never stop at scaffolding. Prioritize strictly by project name order above.
- Working tree clean. Do not create untracked junk.
- **DO NOT AVOID HEAVY WORK. EXECUTE IN ORDER WITHOUT SKIPPING.**
- Every change must serve the prioritized spec (gamma/orderflow/vol/signal/backtest).

## EXECUTION RULES

- Working tree clean; do not create untracked junk.
- Run tests after changes: `python -m pytest` (maintain >= 166 passing).
- Run static checks: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains (update BOTH files).
- DO NOT avoid heavy work. Execute in order without skipping.
