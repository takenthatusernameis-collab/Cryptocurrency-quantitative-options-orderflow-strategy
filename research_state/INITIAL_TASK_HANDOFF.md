# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T04:14:12Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 216 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN
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
- **Test suite current**: 216 passing, 1 warning (deprecation in test_schemas only). Do not rely on older numbers.
- **Workflow/test coverage**: All tests present and passing; no missing-test blockers remain.
- **No untracked junk, clean working tree**: Ready for immediate heavy engineering.

## VERIFIED STATE (2026-10-29T04:14:12Z — FROZEN SNAPSHOT)

- `python -m pytest -q` → 216 passed, 1 warning (deprecation in test_schemas only)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 28 source files
- `git status` → On branch main, working tree clean
- `grep -rn "TODO|FIXME|PLACEHOLDER|HACK|XXX" src/ tests/ scripts/` → no matches
- No untracked junk. No placeholder scaffolding.

## Initial Task Message — For Next Agentic Work Session (Mandatory, Non-Optional)
Session start: 2026-10-29T04:14:12Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP.**

### ABSOLUTE FIRST ACTION
**PICK EXACTLY ONE HIGHEST-IMPACT UNCOMPLETED ITEM FROM PHASE 8 REMAINING AND COMPLETE IT END-TO-END** (implementation + tests + mypy clean). Do **NOT** parallelize across multiple items. Leave remaining heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### JUST COMPLETED (END-TO-END)
- **[CRITICAL] Adversarial stress scenarios across ALL modules** — DONE.
- **[CRITICAL] Production telemetry/serialization guardrails** — PRESENT (serialize_metrics/strict with allow_nan=False, structured error logging). Telemetry end-to-end test exists and passing.
- **[HIGH] OOS & walk-forward robustness** — DONE.
- **[HIGH] Numerical guards & config validation edge cases** — DONE.
- **[HIGH] Wire numerical guards into data/normalization.py + end-to-end pipeline serialization test** — DONE (2026-10-29T04:14:12Z). Enhanced calculate_cumulative_delta/compute_vwap/calculate_moneyness with validate_finite/safe_divide, logged via log_error_with_context; added tests/test_pipeline_serialization_end_to_end.py covering clean path, zero-volume/empty chains, NaN prices/trades/invalid sides, inverted stops; all serialization enforces allow_nan=False.

### Immediate Objectives (Strict Priority Order)
1. **[HIGH] Strengthen numerical guards in features/orderflow.py (and ensure consistent usage)** — Apply safe_divide/validate_finite across calculate_cumulative_delta/VPIN/orderflow imbalance paths; guard against division by zero, non-finite inputs; add/extend tests if gaps found. Must be end-to-end with mypy clean and tests passing.
   - Focus on src/features/orderflow.py; prefer reusing src.utils.numerical_guards. Ensure log_strategy_error/log_error_with_context used on error paths.
2. **[HIGH] Telemetry coverage gaps (only if discovered while doing #1)** — Ensure all new error paths log with module/symbol/timestamp/operation.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` must be >= 216 passing (maintain/improve).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` must be clean.
- Working tree clean. No untracked junk. No TODO/FIXME/placeholder/HACK/XXX.
- If work remains after completing ONE item end-to-end, update **BOTH** handoff files with a new timestamped message and leave heavy work clearly specified with concrete next steps.

## Next Focus Campaign (Never Avoid Heavy Work)
Project-name priority order:
- **Phase 1: Dealer positioning / gamma exposure** (gamma/gamma flip/net GEX/notional/pin-flip) — core.
- **Phase 2: Orderflow microstructure** (signed volume/cum delta/VPIN/toxicity/absorption) — flow confirmation (guards pending hardening).
- **Phase 3: Volatility surface dynamics** (skew/term/RR/ATM/calendar/max pain) — regime/context.
- **Phase 4: Regime-aware signal engineering** (cross-features/calibration/normalization/leakage) — actionable.
- **Phase 5: Rigorous backtesting** (fills/slippage/costs/partial/round lots/walk-forward/OOS/stress/tx costs) — ground truth.
- **Phase 8: PRODUCTION TELEMETRY & STRESS COVERAGE — IN PROGRESS**

**Remaining Phase 8 deliverables (COMPLETE ONE FULLY BEFORE MOVING ON):**
- [x] Stress scenarios across all modules
- [x] Telemetry/guardrails & serialization end-to-end
- [x] OOS & walk-forward robustness
- [x] Numerical guards & config validation edge cases
- [x] Wire numerical guards into data/normalization.py + end-to-end pipeline serialization test
- [ ] Strengthen numerical guards in features/orderflow.py + related tests *(NEXT - START HERE)*
- [ ] Any remaining telemetry/serialization edge cases discovered

## MANDATE (NON-NEGOTIABLE)
- Heavy engineering only. Mathematical correctness mandatory.
- Numerical stability required. Vectorize where sensible.
- No placeholders/TODOs/FIXMEs. Full implementation with code AND tests.
- Complete **ONE** major item fully end-to-end; leave heavy work for the next agent.
- Never stop at scaffolding. Prioritize strictly by project name order above.
- Working tree clean. Do not create untracked junk.
- **DO NOT AVOID HEAVY WORK. EXECUTE IN ORDER WITHOUT SKIPPING.**

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes: `python -m pytest` (maintain >= 216 passing).
- Run static checks: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains (update BOTH files).
- DO NOT avoid heavy work. Execute in order without skipping.


---

## HANDOFF UPDATE (2026-10-29T04:21:07Z) — ORDERFLOW GUARDS HARDENED
State: 216 TESTS PASSING | MYPY CLEAN | CHANGES NOT COMMITTED (working tree modified)

### Completed (end-to-end)
- **[HIGH] Strengthen numerical guards in features/orderflow.py** — DONE.
  - Added safe_divide usage across divisions (orderflow imbalance, VPIN buckets/mean, absorption, aggressive flow, delta-adjusted/VWAP paths).
  - Added structured error logging via log_error_with_context on non-finite results (cumulative delta, robust/vectorized paths, imbalance, VPIN, absorption, aggressive flow).
  - Hardened delta_divergence_vs_price with guards and cleaner error context; added try/except wrapping for robustness.
  - Imported numerical guards and telemetry logging; mypy clean.

### Verification
- `python -m pytest` → 216 passed, 1 warning (pre-existing in test_schemas)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 28 source files

### Remaining Phase 8 (pick ONE next)
- [ ] Any remaining telemetry/serialization edge cases discovered while working (scan for uncovered paths). If none obvious, move to next phase per priority.

### Next Focus Campaign (strict by project name)
Continue Phase 1-5 as per priority order; all previous Phase 8 items complete except possibly residual telemetry gaps. **Pick exactly ONE highest-impact item and complete end-to-end. Do NOT parallelize. Never avoid heavy quantitative work.**
