# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-28T21-41-47Z
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
- **Single source of truth enforced**: All handoffs consolidated to `research_state/durable_handoff.md` and `research_state/INITIAL_TASK_HANDOFF.md`. Duplicate timestamped `INITIAL_TASK_HANDOFF_LATEST_*`, `HEAVY_WORK_HANDOFF_*`, and `HEAVY_WORK_INITIAL_TASK_*` files are superseded and removed to eliminate ambiguity and clutter.
- **Ambiguity eliminated**: exactly two canonical handoff files exist; both mirror this content and are updated together.
- **No idle scaffolding**: Next session MUST complete ONE major item end-to-end (implementation + tests). No TODO/FIXME/placeholder.
- **Determinism enforced**: Seeds must propagate through features, signals, and backtests.
- **Numerical hygiene**: All metric serialization must pass through sanitization with `allow_nan=False` and raise `SerializationError` on invalid values.

## Initial Task Message — FOR NEXT AGENTIC WORK SESSION (MANDATORY, NON-OPTIONAL)
EXECUTE NOW. START AT PHASE 8 (PRODUCTION TELEMETRY & STRESS COVERAGE). Pick **ONE** highest-impact uncompleted item and **COMPLETE IT END-TO-END** (code + tests + mypy clean). Do not split scope. Leave heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### Immediate Objectives (do in this order)
1. **Adversarial stress scenarios** across gamma/orderflow/surface/backtest: empty/degenerate frames, NaN/Inf cascades, extreme sizes, all-same-side flow, zero liquidity, duplicate timestamps. Assert no NaN/Inf propagation; quant-precise error context on all exceptions.
2. **Telemetry/guardrails & serialization end-to-end**: structured logging for RiskLimitError/OrderError/SerializationError (module, symbol, timestamp); `SerializationError` raised on non-finite values; JSON validity verified in tests; end-to-end path ingestion -> features -> signals -> backtest -> serialization tested.
3. **OOS & walk-forward robustness**: strict time ordering/no lookahead, purge/embargo, RNG seed determinism with reproducibility tests, `allow_nan=False` metric sanitization.
4. **Numerical guards & config validation edge cases**: insufficient cash/short-notional/position limits -> RiskLimitError/OrderError; division-by-zero, log(<=0), sqrt of negative, pct-change-on-zero guarded; safe defaults and invalid-combo rejection.

### Verification (REQUIRED)
`python -m pytest` must reach >= 115 passing (incl. handoff-integrity tests). `python -m mypy src/ --disallow-untyped-defs --warn-return-any` clean. Working tree clean. No untracked junk.

## Next Focus Campaign (Never Avoid Heavy Work)
- Phase 1: COMPLETE - Data ingestion/resilience
- Phase 2: COMPLETE - Normalization & canonical schemas
- Phase 3: COMPLETE - Features (gamma, orderflow, volatility, max pain)
- Phase 4: COMPLETE - Regime-aware signal engineering
- Phase 5: COMPLETE - Rigorous backtesting
- Phase 6: COMPLETE - Integration/resilience/tests
- Phase 7: COMPLETE - Production readiness (final hardening pass)
- **Phase 8: PRODUCTION TELEMETRY & STRESS COVERAGE — IN PROGRESS (HEAVY WORK MANDATORY)**

Remaining Phase 8 deliverables (complete ONE fully before moving on):
- [ ] Stress scenarios across all modules (highest priority — start here)
- [ ] OOS & walk-forward robustness
- [ ] Telemetry/guardrails & serialization end-to-end
- [ ] Numerical guards & config validation edge cases

## MANDATE
- Heavy engineering only. Mathematical correctness mandatory.
- Numerical stability required. Vectorize where sensible.
- No placeholders/TODOs/FIXMEs. Full implementation with code AND tests.
- Complete ONE major item fully; leave heavy work for the next agent.
- Never stop at scaffolding. Prioritize strictly by project name order above.
- Working tree clean. Do not create untracked junk.
- DO NOT avoid heavy work. Execute in order without skipping.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes: `python -m pytest` (maintain >= 115 passing).
- Run static checks: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains (update this file or create new LATEST with timestamp).
- DO NOT avoid heavy work. Execute in order without skipping.
