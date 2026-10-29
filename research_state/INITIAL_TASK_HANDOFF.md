# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T02:33:00Z
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

- **Single source of truth enforced**: Both canonical handoff files mirror this content exactly.
- **Ambiguity eliminated**: exactly two canonical handoff files exist (INITIAL_TASK_HANDOFF.md, durable_handoff.md).
- **Mypy/type issues cleared**: Strict mypy with --disallow-untyped-defs passes cleanly.
- **Test suite current**: 166 passing, 1 warning (deprecation in test_schemas only). Do not rely on older numbers.
- **Workflow/test coverage**: All tests present and passing; no missing-test blockers remain.
- **No untracked junk, clean working tree**: Ready for immediate heavy engineering.

## VERIFIED STATE (2026-10-29T02:33:00Z — FROZEN SNAPSHOT)

- `python -m pytest -q` → 166 passed, 1 warning (deprecation in test_schemas only)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 27 source files
- `git status` → On branch main, working tree clean
- `grep -rn "TODO|FIXME|PLACEHOLDER|HACK|XXX" src/ tests/ scripts/` → no matches
- No untracked junk. No placeholder scaffolding.

## INITIAL TASK MESSAGE — FOR NEXT AGENTIC WORK SESSION (MANDATORY, NON-OPTIONAL)
Session start: 2026-10-29T02:33:00Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP.**

### ABSOLUTE FIRST ACTION
**START AT: NUMERICAL GUARDS & CONFIG VALIDATION EDGE CASES** (Phase 8 remaining highest-impact item). Pick **EXACTLY ONE** highest-impact uncompleted item and **COMPLETE IT END-TO-END** (implementation + tests + mypy clean). Do **NOT** parallelize across multiple items. Leave remaining heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### JUST COMPLETED (END-TO-END)
- **[CRITICAL] Adversarial stress scenarios across ALL modules** — DONE.
- **[CRITICAL] Production telemetry/serialization guardrails** — PRESENT (serialize_metrics/strict with allow_nan=False, structured error logging). Telemetry end-to-end test exists and passing.
- **[HIGH] OOS & walk-forward robustness** — DONE (src/backtest/engine.py + tests/test_oos_walkforward.py). Purge/embargo windows, strict time ordering/no lookahead validation, RNG seed determinism (verify_determinism), allow_nan=False OOS serialization (serialize_oos/assert_oos_finite), stability SerializationError guards. Tests passing.

### IMMEDIATE OBJECTIVES (STRICT PRIORITY ORDER)
1. **[HIGH] Numerical guards & config validation edge cases — START HERE NOW**
   - **Risk limits**: insufficient cash/short-notional/position limits must raise RiskLimitError/OrderError with full context + structured logging via log_strategy_error (module/symbol/timestamp/operation).
   - **Numerical guards**: division-by-zero, log(<=0), sqrt of negative, pct-change-on-zero across features/signals/backtest. No NaN/Inf leakage. Use safe guards, explicit errors or sanitized values per existing project patterns.
   - **Config validation**: edge cases, safe defaults, invalid-combo rejection with clear errors.
   - **Every path** must be typed (mypy strict), logged where errors occur, and covered by tests.

2. **[HIGH] Telemetry coverage gaps (only if discovered while doing #1)**
   - Ensure all new error paths log via log_strategy_error with module/symbol/timestamp/operation.
   - Extend end-to-end serialization to cover any new aggregates if introduced.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` must be >= 166 passing (maintain/improve).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` must be clean.
- Working tree clean. No untracked junk. No TODO/FIXME/placeholder/HACK/XXX.
- If work remains after completing ONE item end-to-end, update **BOTH** handoff files with a new timestamped message and leave heavy work clearly specified with concrete next steps.

## NEXT FOCUS CAMPAIGN (NEVER AVOID HEAVY WORK)
- Phase 1-7: COMPLETE
- **Phase 8: PRODUCTION TELEMETRY & STRESS COVERAGE — IN PROGRESS (HEAVY QUANTITATIVE WORK MANDATORY)**

**Remaining Phase 8 deliverables (COMPLETE ONE FULLY BEFORE MOVING ON):**
- [x] Stress scenarios across all modules *(COMPLETED)*
- [x] Telemetry/guardrails & serialization end-to-end *(COMPLETED/PRESENT)*
- [x] OOS & walk-forward robustness *(COMPLETED)*
- [ ] Numerical guards & config validation edge cases *(START HERE - HIGHEST IMPACT)*

## MANDATE (NON-NEGOTIABLE)
- Heavy engineering only. Mathematical correctness mandatory.
- Numerical stability required. Vectorize where sensible.
- No placeholders/TODOs/FIXMEs. Full implementation with code AND tests.
- Complete **ONE** major item fully end-to-end; leave heavy work for the next agent.
- Never stop at scaffolding. Prioritize strictly by project name order above (gamma/orderflow/vol/signal/backtest).
- Working tree clean. Do not create untracked junk.
- **DO NOT AVOID HEAVY WORK. EXECUTE IN ORDER WITHOUT SKIPPING.**

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes: `python -m pytest` (maintain >= 166 passing).
- Run static checks: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains (update BOTH files).
- DO NOT avoid heavy work. Execute in order without skipping.
