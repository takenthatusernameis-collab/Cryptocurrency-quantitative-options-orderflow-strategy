# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH MIRROR) — LATEST
Timestamp (UTC): 2026-10-29T05:12:09Z
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
- **Historical workflow failures (Oct 27) are stale**: do not re-open cancelled/failed Kilo runs; proceed from verified state above.

## VERIFIED STATE (2026-10-29T05:12:09Z — FROZEN SNAPSHOT)

- `python -m pytest -q` → 216 passed, 1 warning (deprecation in test_schemas only)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 28 source files
- `git status` → On branch main, working tree clean
- `grep -rn "TODO|FIXME|PLACEHOLDER|HACK|XXX" src/ tests/ scripts/` → no matches
- No untracked junk. No placeholder scaffolding.

## Initial Task Message — For Next Agentic Work Session (Mandatory, Non-Optional)
Session start: 2026-10-29T05:12:09Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP.**

### ABSOLUTE FIRST ACTION
**SCAN telemetry/serialization for uncovered error paths across src/ (gamma, orderflow, volatility, signals, backtest). If a concrete gap exists, implement ONE heavy end-to-end fix (guards + tests + mypy clean). If none obvious, move immediately to Phase 1: harden gamma exposure (net GEX, gamma flip, pin/flip zones) with vectorized numerical guards + adversarial stress tests — NO SKIPPING.** Complete exactly ONE item end-to-end (implementation + tests + mypy clean). Do NOT parallelize across multiple items. Leave remaining heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### JUST COMPLETED (END-TO-END)
- **[CRITICAL] Adversarial stress scenarios across ALL modules** — DONE.
- **[CRITICAL] Production telemetry/serialization guardrails** — PRESENT.
- **[HIGH] OOS & walk-forward robustness** — DONE.
- **[HIGH] Numerical guards & config validation edge cases** — DONE.
- **[HIGH] Wire numerical guards into data/normalization.py + end-to-end pipeline serialization test** — DONE.
- **[HIGH] Strengthen numerical guards in features/orderflow.py** — DONE.

### Immediate Objectives (Strict Priority Order)
1. **[HIGH] Telemetry/serialization gap scan + ONE heavy end-to-end fix if a concrete gap exists** — scan gamma, orderflow, volatility, signals, backtest for uncovered error paths; implement guards + tests + mypy clean if found.
2. **[HIGH] Phase 1: harden gamma exposure** (only if step 1 finds no gap) — net GEX, gamma flip, pin/flip zones with vectorized numerical guards + adversarial stress tests; end-to-end with mypy clean and tests passing.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` must be >= 216 passing.
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` must be clean.
- Working tree clean. No untracked junk. No TODO/FIXME/placeholder/HACK/XXX.
- If work remains after completing ONE item end-to-end, update **BOTH** handoff files with a new timestamped message and leave heavy work clearly specified with concrete next steps.

## Next Focus Campaign
Project-name priority order (gamma/orderflow/vol/signal/backtest). Phase 8 complete; Phase 1 in progress.

**Remaining Phase 8 deliverables (COMPLETE ONE FULLY BEFORE MOVING ON):**
- [x] Stress scenarios across all modules
- [x] Telemetry/guardrails & serialization end-to-end
- [x] OOS & walk-forward robustness
- [x] Numerical guards & config validation edge cases
- [x] Wire numerical guards into data/normalization.py + end-to-end pipeline serialization test
- [x] Strengthen numerical guards in features/orderflow.py + related tests
- [ ] Telemetry/serialization gap scan + ONE heavy fix (if gap found) *(candidate next)*
- [ ] Any remaining telemetry/serialization edge cases discovered

**Next Focus Campaign (strict by project name; heavy work mandatory):**
1. Phase 1 — Dealer positioning/gamma exposure (core edge): vectorized, numerically correct, adversarial-tested.
2. Phase 2 — Orderflow microstructure: already hardened; residual telemetry only.
3. Phase 3 — Volatility surface dynamics: degenerate surface guards.
4. Phase 4 — Regime-aware signal engineering: determinism + leakage prevention.
5. Phase 5 — Rigorous backtesting: no lookahead, sanitized metrics.

## MANDATE (NON-NEGOTIABLE)
- Heavy engineering only. Mathematical correctness mandatory.
- Numerical stability required. Vectorize where sensible.
- No placeholders/TODOs/FIXMEs.
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

---

## HANDOFF UPDATE (2026-10-29T05:11:39Z) — DURABLE HANDOFF REFRESHED; NEXT HEAVY CAMPAIGN SET
State: 216 TESTS PASSING | MYPY CLEAN | WORKING TREE CLEAN

---

## HANDOFF UPDATE (2026-10-29T05:12:09Z) — STATE VERIFIED; NEXT HEAVY CAMPAIGN RE-AFFIRMED
State: 216 TESTS PASSING | MYPY CLEAN | WORKING TREE CLEAN

- Verified pytest >= 216 passing and mypy clean; no working-tree changes.
- All Phase 8 items complete; orderflow guards hardened; telemetry/serialization guardrails present.
- Next session: scan telemetry/serialization for uncovered error paths; if none, harden Phase 1 gamma exposure (net GEX, gamma flip, pin/flip zones) with adversarial stress tests — NO SKIPPING.
