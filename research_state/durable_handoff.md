# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH MIRROR) — LATEST
Timestamp (UTC): 2026-10-29T06:17:25Z
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

## VERIFIED STATE (2026-10-29T06:17:25Z — FROZEN SNAPSHOT)

- `python -m pytest -q` → 216 passed, 1 warning (deprecation in test_schemas only)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 28 source files
- `git status` → On branch main, working tree clean
- `grep -rn "TODO|FIXME|PLACEHOLDER|HACK|XXX" src/ tests/ scripts/` → no matches
- No untracked junk. No placeholder scaffolding.

## Immediate Objectives
1. Harden Phase 1 (dealer positioning/gamma exposure) — pin/flip zones to production-grade with adversarial tests.
2. Maintain mypy clean and all tests passing; leave heavy work for next agent after completing ONE end-to-end item.

## Initial Task Message — FOR NEXT AGENTIC WORK SESSION (MANDATORY, NON-OPTIONAL)

Session start: 2026-10-29T06:17:25Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP.**

### ABSOLUTE FIRST ACTION (HEAVY, END-TO-END)
**HARDEN PHASE 1 (DEALER POSITIONING/GAMMA EXPOSURE) — PIN/FLIP ZONES TO PRODUCTION-GRADE.**

Do **ONE** coherent heavy item completely end-to-end (implementation + adversarial tests + mypy clean + full suite passing). Leave remaining heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### CONCRETE TARGETS (MUST HIT)
Focus strictly on `src/features/gamma_exposure.py`, its exports in `src/features/__init__.py`, integration in `src/signals/composite.py`, and harden `tests/test_phase1_gamma_invariants.py` (or add a new focused adversarial test module). Specifically:

1. **Pin zone robustness** (`calculate_pin_zone`): adversarial cases — all-same-sign GEX, NaN/Inf in strike/GEX, zero-OI across chain, missing delta/gamma, extreme strikes/expiries, spot<=0/NaN. Ensure `center/lower/upper/width_pct/total_gex` all finite-guarded; caps on width_pct enforced; sensible fallbacks (flip→spot) never produce NaN/Inf.
2. **Flip zones robustness** (`calculate_flip_zones`): all-positive/all-negative GEX, multiple crossings, zeros, NaN/Inf, degenerate chains. Interpolation must be stable; band_pct capped; never return NaN.
3. **Vectorized paths**: verify `_vectorized_gex`, `_vectorized_delta_weights`, `_vectorized_oi_vol_weights` sanitize non-finite and match scalar semantics exactly. No leakage of NaN/Inf into sums.
4. **Integration safety**: ensure `src/signals/composite.py` consumes pin/flip zones safely (no crashes on adversarial inputs). Add guards if missing.
5. **Cross-checks**: `calculate_net_gamma_exposure_total` alias consistency, `calculate_gex_by_strike` weighting modes, delta-band classification for calls/puts remain correct.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` must be >= 216 passing (do not regress).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` must be clean.
- Working tree clean. No untracked junk. No TODO/FIXME/placeholder/HACK/XXX.
- If work remains after completing **ONE** item end-to-end, update **BOTH** handoff files with a new timestamped message and leave heavy work clearly specified with concrete next steps and file paths.

## Next Focus Campaign (STRICT PRIORITY)

Project-name priority order (gamma/orderflow/vol/signal/backtest). Phase 1 is the core edge — harden first.

**Remaining heavy work (strict priority):**
1. **Phase 1 — Dealer positioning/gamma exposure (CORE EDGE)**: pin zones, flip zones, net GEX by bands, vectorized + adversarial-tested. Strengthen invariants and cross-checks. *(CURRENT TARGET)*
2. Phase 2 — Orderflow microstructure: signed volume, cumulative delta, VPIN/toxicity, absorption, aggressive/passive flow with adversarial guards.
3. Phase 3 — Volatility surface dynamics: skew/term structure/RR, ATM term structure, calendar spreads, max pain with degenerate-surface guards.
4. Phase 4 — Regime-aware signal engineering: cross-features, calibration, normalization, feature leakage prevention, determinism.
5. Phase 5 — Rigorous backtesting: fills/slippage/costs/partial fills, round lots, walk-forward/OOS, stress, transaction costs, sanitized metrics, no lookahead.

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
