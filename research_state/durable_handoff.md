# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH MIRROR) — LATEST
Timestamp (UTC): 2026-10-29T05:19:27Z
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

## VERIFIED STATE (2026-10-29T05:19:27Z — FROZEN SNAPSHOT)

- `python -m pytest -q` → 216 passed, 1 warning (deprecation in test_schemas only)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 28 source files
- `git status` → On branch main, working tree clean
- `grep -rn "TODO|FIXME|PLACEHOLDER|HACK|XXX" src/ tests/ scripts/` → no matches
- No untracked junk. No placeholder scaffolding.

## Initial Task Message — For Next Agentic Work Session (Mandatory, Non-Optional)
Session start: 2026-10-29T05:19:27Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP.**

### ABSOLUTE FIRST ACTION
**HARDEN PHASE 1 (DEALER POSITIONING/GAMMA EXPOSURE) END-TO-END.** Focus on pin/flip zones with vectorized numerical guards, adversarial stress coverage, and full integration into signals/backtest paths. Complete exactly ONE coherent heavy item end-to-end (implementation + tests + mypy clean). Do NOT parallelize across multiple items. Leave remaining heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### JUST COMPLETED (END-TO-END)
- **[HIGH] Gamma exposure: added pin/flip zones (calculate_pin_zone/calculate_flip_zones) with vectorized guards and aliases exported** — DONE (2026-10-29T05:19:27Z).
- **[CRITICAL] Adversarial stress scenarios across ALL modules** — DONE.
- **[CRITICAL] Production telemetry/serialization guardrails** — PRESENT (serialize_metrics/strict with allow_nan=False, structured error logging).
- **[HIGH] OOS & walk-forward robustness** — DONE.
- **[HIGH] Numerical guards & config validation edge cases** — DONE.
- **[HIGH] Wire numerical guards into data/normalization.py + end-to-end pipeline serialization test** — DONE.
- **[HIGH] Strengthen numerical guards in features/orderflow.py** — DONE.

### Immediate Objectives (Strict Priority Order)
1. **[CRITICAL] Phase 1: Harden gamma exposure/pin-flip zones** — Expand adversarial coverage (all-same-sign, NaN/Inf, zero-OI, extreme strikes/expiries), ensure vectorized paths robust, add/strengthen tests in `tests/test_phase1_gamma_invariants.py` or new adversarial tests; verify signals/composite.py gamma handling remains safe; mypy clean + tests passing.
2. **[HIGH] Telemetry/serialization gap scan** — Only if time remains after (1) or if concrete gap discovered; implement ONE fix end-to-end.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` must be >= 216 passing.
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` must be clean.
- Working tree clean. No untracked junk. No TODO/FIXME/placeholder/HACK/XXX.
- If work remains after completing ONE item end-to-end, update **BOTH** handoff files with a new timestamped message and leave heavy work clearly specified with concrete next steps.

## Next Focus Campaign
Project-name priority order (gamma/orderflow/vol/signal/backtest). Phase 8 telemetry hardening substantially complete.

**Remaining heavy work (strict priority):**
1. **Phase 1 — Dealer positioning/gamma exposure (CORE EDGE)**: pin zones, flip zones, net GEX by bands, vectorized + adversarial-tested. Strengthen invariants and cross-checks.
2. Phase 2 — Orderflow microstructure: residual telemetry only.
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

## HANDOFF UPDATE (2026-10-29T05:19:27Z) — GAMMA PIN/FLIP ZONES ADDED; PHASE 1 HARDENING NEXT
State: 216 TESTS PASSING | MYPY CLEAN | WORKING TREE CLEAN

### Completed (end-to-end)
- **[HIGH] Gamma exposure extensions**: Added `calculate_pin_zone`/`calculate_flip_zones` with aliases, exported from `src.features`, numerical guards and fallbacks; mypy clean, all tests passing.

### Absolute First Action (Next Session)
**HARDEN PHASE 1 (GAMMA EXPOSURE/PIN-FLIP ZONES) END-TO-END.** Add/strengthen adversarial tests for pin/flip zones (all-same-sign GEX, NaN/Inf, zero-OI, missing delta, extreme strikes), ensure vectorized paths are robust, verify integration with signals; run tests+mypy. Complete ONE coherent heavy item fully; update both handoffs if more remains.

### Verification
- pytest >= 216 passing; mypy clean; working tree clean; no TODO/FIXME/placeholder/HACK/XXX.
