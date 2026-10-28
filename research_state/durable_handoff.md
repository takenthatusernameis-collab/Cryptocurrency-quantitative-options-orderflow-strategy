# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-28T22-26-28Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 115 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN
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
- **Single source of truth enforced**: All handoffs consolidated to `research_state/durable_handoff.md` and `research_state/INITIAL_TASK_HANDOFF.md`. Duplicate timestamped handoffs removed to eliminate ambiguity and clutter.
- **Ambiguity eliminated**: exactly two canonical handoff files exist; both mirror this content and are updated together.
- **No idle scaffolding**: Next session MUST complete ONE major item end-to-end (implementation + tests). No TODO/FIXME/placeholder.
- **Determinism enforced**: Seeds must propagate through features, signals, and backtests.
- **Numerical hygiene**: All metric serialization must pass through sanitization with `allow_nan=False` and raise `SerializationError` on invalid values.

## VERIFIED STATE (2026-10-28T22-26-28Z — DO NOT RE-VERIFY UNCHANGED)
- `python -m pytest -q` → 115 passed, 1 warning (deprecation in test_schemas only).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 24 source files.
- `git status` → On branch main, up to date with origin/main, nothing to commit, working tree clean.
- `grep -rn "TODO|FIXME|PLACEHOLDER|HACK|XXX" src/ tests/ scripts/` → no matches.
- No untracked junk. No placeholder scaffolding. Phases 1-7 fully complete.

## Initial Task Message — FOR NEXT AGENTIC WORK SESSION (MANDATORY, NON-OPTIONAL)
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES.**

START AT **PHASE 8 (PRODUCTION TELEMETRY & STRESS COVERAGE)**. Pick **EXACTLY ONE** highest-impact uncompleted item below and **COMPLETE IT END-TO-END** (implementation + tests + mypy clean). Do **NOT** split scope across multiple items. Leave the remaining heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### Immediate Objectives (in strict priority order)
1. **[CRITICAL] Adversarial stress scenarios across ALL modules**
   - Target: gamma/orderflow/surface/backtest + ingestion/normalization/config
   - Cases: empty/degenerate DataFrames/objects, NaN/Inf cascades, extreme sizes, all-same-side flow, zero liquidity, duplicate timestamps, division-by-zero paths, log/sqrt of invalid values
   - Requirement: no NaN/Inf propagation; quant-precise error context on exceptions; deterministic behavior
   - Add comprehensive tests covering each module

2. **[HIGH] Telemetry/guardrails & serialization end-to-end**
   - Structured logging for RiskLimitError/OrderError/SerializationError with context (module, symbol, timestamp, operation)
   - Enforce `SerializationError` on non-finite values in serialization paths; JSON validity with `allow_nan=False`
   - End-to-end test: ingestion -> features -> signals -> backtest -> serialization

3. **[HIGH] OOS & walk-forward robustness**
   - Strict time ordering/no lookahead, purge/embargo correctness
   - RNG seed determinism with reproducibility tests
   - `allow_nan=False` metric sanitization in all aggregate results
   - Stability metrics numerically stable (guard inf/NaN)

4. **[HIGH] Numerical guards & config validation edge cases**
   - Risk limits: insufficient cash/short-notional/position limits -> RiskLimitError/OrderError with context
   - Guards for division-by-zero, log(<=0), sqrt of negative, pct-change-on-zero
   - Config validation edge cases, safe defaults, invalid-combo rejection

### Verification (REQUIRED BEFORE HANDOFF)
- `python -m pytest` must reach >= 115 passing (incl. all existing tests)
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
- [ ] **Stress scenarios across all modules** *(START HERE - HIGHEST IMPACT)*
- [ ] OOS & walk-forward robustness
- [ ] Telemetry/guardrails & serialization end-to-end
- [ ] Numerical guards & config validation edge cases

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
- Run tests after changes: `python -m pytest` (maintain >= 115 passing).
- Run static checks: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains (update BOTH files).
- DO NOT avoid heavy work. Execute in order without skipping.

(End of file - total 92 lines)