# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-28T21-41-33Z
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
- **Single source of truth enforced**: All handoffs consolidated to this file. Previous `INITIAL_TASK_HANDOFF_LATEST_*` are superseded.
- **Ambiguity eliminated**: `research_state/durable_handoff.md` and `research_state/INITIAL_TASK_HANDOFF.md` will be overwritten to point to this document.
- **No idle scaffolding**: Next session MUST complete ONE major item end-to-end (implementation + tests). No TODO/FIXME/placeholder.
- **Determinism enforced**: Seeds must propagate through features, signals, and backtests.
- **Numerical hygiene**: All metric serialization must pass through sanitization with `allow_nan=False` and raise `SerializationError` on invalid values.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION — MANDATORY, NON-OPTIONAL)
EXECUTE NOW. START AT PHASE 8 (PRODUCTION TELEMETRY & STRESS COVERAGE). Pick **ONE** highest-impact uncompleted item below and **COMPLETE IT END-TO-END** (code + tests + mypy clean). Do not split scope. Leave heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### HIGHEST-IMPACT ITEM (COMPLETE FULLY)
**Expand stress coverage / OOS / walk-forward robustness comprehensively**

#### Scope (MANDATORY - NO PARTIALS)
1. **Adversarial stress scenarios** (across gamma/orderflow/surface/backtest)
   - Empty/degenerate frames, NaN/Inf cascades, extreme sizes, all-same-side flow, zero liquidity, duplicate timestamps
   - Assert no NaN/Inf propagation. All exceptions must have quant-precise error context.

2. **OOS & walk-forward robustness**
   - Harden walk-forward splits with strict time ordering (no lookahead). Purge/embargo if applicable.
   - Determinism: propagate RNG seeds through all stochastic paths. Add reproducibility tests.
   - Sanitize all reported metrics with `allow_nan=False`. Block serialization of non-finite values.

3. **Telemetry/guardrails & serialization end-to-end**
   - Structured logging for violations (RiskLimitError/OrderError/SerializationError). Include module, symbol, timestamp context.
   - `SerializationError` must be raised on non-finite values; JSON validity verified in tests.
   - End-to-end telemetry path tested (ingestion -> features -> signals -> backtest -> serialization).

4. **Config validation edge cases**
   - Harden venue/risk/backtest params for dict and object forms. Defaults must be safe.
   - Reject invalid combos with actionable errors. Cover boundary values.

5. **Numerical guards**
   - Insufficient cash, short-notional breach, position limits -> `RiskLimitError`/`OrderError` with structured logging.
   - Division-by-zero, log(<=0), sqrt of negative, pct changes on zeros guarded explicitly.

6. **Quant-precise documentation**
   - Docstrings for all new guards explaining numerical rationale (units, invariants, failure modes).

**Verification (REQUIRED):** `python -m pytest` must stay >= 115 passing. `python -m mypy src/ --disallow-untyped-defs --warn-return-any` must remain clean. Working tree clean.

## PHASE CAMPAIGN (NEVER AVOID HEAVY WORK)
- Phase 1: COMPLETE - Data ingestion/resilience
- Phase 2: COMPLETE - Normalization & canonical schemas
- Phase 3: COMPLETE - Features (gamma, orderflow, volatility, max pain)
- Phase 4: COMPLETE - Regime-aware signal engineering
- Phase 5: COMPLETE - Rigorous backtesting
- Phase 6: COMPLETE - Integration/resilience/tests
- Phase 7: COMPLETE - Production readiness (final hardening pass)
- **Phase 8: PRODUCTION TELEMETRY & STRESS COVERAGE — IN PROGRESS (HEAVY WORK MANDATORY)**

Remaining Phase 8 tasks:
- [ ] Stress scenarios across all modules (highest priority)
- [ ] OOS & walk-forward robustness
- [ ] Telemetry/guardrails & serialization end-to-end
- [ ] Numerical guards & config validation edge cases

## UNCOMPROMISING MANDATE
- Heavy engineering only. Mathematical correctness mandatory.
- Numerical stability required. Vectorize where sensible.
- No placeholders/TODOs/FIXMEs. Full implementation with code AND tests.
- Complete ONE major item fully; leave heavy work for the next agent.
- Never stop at scaffolding. Prioritize strictly by project name order above.
- Working tree clean. Do not create untracked junk.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes: `python -m pytest` (maintain >= 115 passing).
- Run static checks: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` (keep clean).
- Fix inefficiencies/blockers immediately.
- Leave clear timestamped handoff if work remains (update this file or create new LATEST with timestamp).
- DO NOT avoid heavy work. Execute in order without skipping.
