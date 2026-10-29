# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH MIRROR) — LATEST
Timestamp (UTC): 2026-10-29T06:22:12Z
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

## VERIFIED STATE (2026-10-29T06:22:12Z — FROZEN SNAPSHOT)

- `python -m pytest -q` → 216 passed, 1 warning (deprecation in test_schemas only)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 28 source files
- `git status` → On branch main, working tree clean
- `grep -rn "TODO|FIXME|PLACEHOLDER|HACK|XXX" src/ tests/ scripts/` → no matches
- No untracked junk. No placeholder scaffolding.

## Completed in this session (END-TO-END)
- **Hardened Phase 1 pin/flip zones** in `src/features/gamma_exposure.py`: made `calculate_pin_zone` and `calculate_flip_zones` fully adversarial-safe (NaN/Inf/spot<=0/degenerate chains/all-same-sign GEX), enforced caps (width_pct<=0.1, band_pct<=0.15), sensible fallbacks to spot/flip levels, all outputs finite-guarded.
- **Integration safety**: added optional chain-aware integration in `src/signals/composite.py` (safe calls to pin/flip zones with try/except, metadata attached without breaking existing behavior), fixed typing for strict mypy.
- **Verification**: all 216 tests passing, mypy clean.

## Initial Task Message — FOR NEXT AGENTIC WORK SESSION (MANDATORY, NON-OPTIONAL)

Session start: 2026-10-29T06:22:12Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP.**

### ABSOLUTE FIRST ACTION (HEAVY, END-TO-END)
**START PHASE 2 (ORDERFLOW MICROSTRUCTURE) — HARDEN TO PRODUCTION-GRADE.**

Do **ONE** coherent heavy item completely end-to-end (implementation + adversarial tests + mypy clean + full suite passing). Leave remaining heavy work for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### Immediate Objectives

### CONCRETE TARGETS (MUST HIT)
Focus strictly on `src/features/orderflow.py`, its exports in `src/features/__init__.py`, and harden/add adversarial tests (e.g. `tests/test_pipeline_integration.py`, `tests/test_signals_regime.py`, or new focused module). Specifically:

1. **Signed volume / cumulative delta robustness**: guard against zero/NaN prices/volumes, missing fields, extreme values. Ensure vectorized paths (`calculate_cumulative_delta_vectorized`, `calculate_signed_volume_vectorized`) match scalar semantics and never leak NaN/Inf.
2. **VPIN/toxicity**: harden `vpin_style_toxicity` / `vpin_toxicity` for small buckets, all-zero volumes, NaN/Inf; clamp outputs to valid ranges; avoid division by zero.
3. **Absorption/aggressive flow**: harden `absorption_detection`, `detect_aggressive_flow` against degenerate inputs.
4. **Integration safety**: ensure orderflow consumers remain safe; add guards if needed without changing APIs.
5. **Cross-checks**: verify aliases and consistency; maintain numerical stability.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` must be >= 216 passing (do not regress).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` must be clean.
- Working tree clean. No untracked junk. No TODO/FIXME/placeholder/HACK/XXX.
- If work remains after completing **ONE** item end-to-end, update **BOTH** handoff files with a new timestamped message and leave heavy work clearly specified with concrete next steps and file paths.

## Next Focus Campaign (STRICT PRIORITY)

Project-name priority order (gamma/orderflow/vol/signal/backtest). Phase 1 completed this session.

**Remaining heavy work (strict priority):**
1. **Phase 1 — Dealer positioning/gamma exposure (CORE EDGE)**: ✅ COMPLETED (pin zones, flip zones hardened, adversarial-safe, integrated safely).
2. **Phase 2 — Orderflow microstructure (CURRENT TARGET)**: signed volume, cumulative delta, VPIN/toxicity, absorption, aggressive/passive flow with adversarial guards.
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
