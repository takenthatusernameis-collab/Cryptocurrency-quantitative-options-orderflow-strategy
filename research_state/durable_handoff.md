# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T07:15:30Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 216 TESTS PASSING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T07:15:30Z (NO DRIFT)
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION (PRIORITIZED - DO NOT DEVIATE)

"Cryptocurrency-quantitative-options-orderflow-strategy" — enforce this strict order of priority for every change:

1. **Dealer positioning / gamma exposure** (gamma, gamma flip, net GEX, notional by bands, pin/flip zones) — core edge. Numerically correct and vectorized.
2. **Orderflow microstructure** (signed volume, cumulative delta, VPIN/toxicity, absorption, aggressive/passive flow) — flow confirmation. Adversarially robust.
3. **Volatility surface dynamics** (skew/term structure/RR, ATM term structure, calendar spreads, max pain) — regime/context. Guard degenerate surfaces.
4. **Regime-aware signal engineering** (cross-features, calibration, normalization, leakage prevention) — actionable signals. Determinism required.
5. **Rigorous backtesting** (fills/slippage/costs/partial fills, round lots, walk-forward/OOS, stress, transaction costs) — ground truth. No lookahead. Metrics sanitized.

Everything must serve (1)-(5). Mathematical correctness > elegance. Numerical stability required. Vectorize where sensible. No shortcuts.

## BOTTLENECK REMOVAL (APPLIED)

- **Single source of truth**: Both canonical handoff files (`research_state/INITIAL_TASK_HANDOFF.md`, `research_state/durable_handoff.md`) are byte-for-byte mirrors of this document.
- **Ambiguity eliminated**: Exactly two canonical handoff files exist. All future agents must read both or treat either as canonical.
- **Types enforced**: `python -m mypy src/ --disallow-untyped-defs --warn-return-any` is clean.
- **Tests current**: `216 passed, 1 warning (deprecation in test_schemas only)`. Do not trust older numbers.
- **Clean tree**: Working tree clean, no untracked junk, no TODO/FIXME/PLACEHOLDER/HACK/XXX.
- **Stale history ignored**: Historical Kilo run failures (Oct 27) are irrelevant. Proceed strictly from the verified state below.

## VERIFIED STATE (RE-VERIFIED 2026-10-29T07:15:30Z)

- `python -m pytest -q` → 216 passed, 1 warning (deprecation in test_schemas only)
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → Success: no issues found in 28 source files
- `git status` → On branch main, working tree clean
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → no matches
- No untracked files. No placeholder scaffolding.

## COMPLETED (PREVIOUS SESSION)
- **Phase 1 hardened end-to-end**: `src/features/gamma_exposure.py` — `calculate_pin_zone`, `calculate_flip_zones` made adversarial-safe (NaN/Inf/spot<=0/degenerate/all-same-sign GEX), caps enforced (width_pct<=0.1, band_pct<=0.15), finite-guarded fallbacks. Safe chain-aware integration into `src/signals/composite.py` with try/except and metadata. Mypy clean + full suite passing.

## INITIAL TASK MESSAGE — FOR NEXT AGENTIC WORK SESSION (MANDATORY, NON-OPTIONAL)

Session start: 2026-10-29T07:15:30Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

### ABSOLUTE FIRST ACTION (HEAVY, END-TO-END)
**START PHASE 2 — ORDERFLOW MICROSTRUCTURE. HARDEN TO PRODUCTION-GRADE.**

Pick **EXACTLY ONE** coherent heavy deliverable from the concrete targets below, take it **ALL THE WAY TO DONE** (implementation + adversarial tests + mypy clean + full test suite passing). Do **NOT** scaffold multiple subsystems at once. Leave the rest explicitly specified for the next agent. **NEVER AVOID HEAVY QUANTITATIVE WORK.**

### CONCRETE TARGETS (MUST HIT) — FOCUS: `src/features/orderflow.py`
Harden and verify the following with adversarial safety, numerical stability, and vectorized paths where applicable:

1. **Signed volume / cumulative delta** — Make `calculate_signed_volume_vectorized` / `calculate_cumulative_delta_vectorized` and scalar equivalents fully robust to zero/NaN/Inf prices/volumes, missing keys/columns, extreme values. Enforce scalar<->vectorized parity. Never leak NaN/Inf. Guard divide-by-zero and degenerate ticks.
2. **VPIN/toxicity** — Harden `vpin_style_toxicity` / `vpin_toxicity`. Handle small bucket counts, all-zero volumes, NaN/Inf, and pathological distributions. Clamp to valid ranges. Deterministic. Avoid division by zero and log of non-positive in unsafe forms.
3. **Absorption / aggressive flow** — Harden `absorption_detection`, `detect_aggressive_flow`. Defensive against empty/degenerate inputs. Preserve semantics, add finite guards and sensible fallbacks.
4. **Exports/integration** — Verify `src/features/__init__.py` exports remain correct. Ensure no consumer of orderflow breaks; add minimal guards only if strictly necessary (no API changes).
5. **Adversarial coverage** — Add/strengthen focused tests (e.g. `tests/test_pipeline_integration.py`, `tests/test_signals_regime.py`, or a new tight test) covering NaN/Inf, zeros, all-equal, tiny windows, large spikes. Do not bloat tests unnecessarily.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` → must be >= 216 passing (do not regress; fix any regressions immediately).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean, no new issues.
- `git status` → clean working tree. No untracked junk.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero matches.
- If **ANY** heavy work remains after completing exactly one item end-to-end, **UPDATE BOTH** `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` with a fresh UTC timestamp, a concise summary of what was done, exact remaining targets with file paths, and concrete next steps. Keep them byte-for-byte identical.

## NEXT FOCUS CAMPAIGN (STRICT PRIORITY - EXECUTE IN ORDER)
Project-name priority is law. Do not reorder.

1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED (hardened pin/flip zones, adversarial-safe, safely integrated).
2. **Phase 2 — Orderflow microstructure (CURRENT MANDATE)**: signed volume, cumulative delta, VPIN/toxicity, absorption, aggressive/passive flow with adversarial guards. **HEAVY WORK REQUIRED.**
3. **Phase 3 — Volatility surface dynamics**: skew/term structure/RR, ATM term structure, calendar spreads, max pain. Degenerate-surface guards, numerical stability.
4. **Phase 4 — Regime-aware signal engineering**: cross-features, calibration, normalization, feature leakage prevention, determinism.
5. **Phase 5 — Rigorous backtesting**: fills/slippage/costs/partial fills, round lots, walk-forward/OOS, stress, transaction costs, sanitized metrics, strict no-lookahead.

## MANDATE (NON-NEGOTIABLE)
- **Heavy engineering only.** Mathematical correctness is mandatory.
- **Numerical stability required.** Vectorize where sensible. Defend all public paths.
- **No placeholders/TODOs/FIXMEs/HACKs/XXX.** If you add code, it must be production-grade.
- **Complete ONE major item fully end-to-end.** Leave heavy work for the next agent with concrete instructions.
- **Never stop at scaffolding.** Never avoid heavy quantitative work.
- **Bottlenecks removed by default.** If anything blocks forward progress (imports/types/tests), fix it immediately.
- **Determinism where relevant.** No hidden global state that breaks reproducibility.
- **Working tree must remain clean.** No untracked junk.

## EXECUTION RULES
- Read this handoff first. Treat both canonical files as identical.
- Work only in service of the project priority order.
- After any change: run `python -m pytest` and `python -m mypy src/ --disallow-untyped-defs --warn-return-any`.
- Keep changes minimal and correct. Prefer hardening over refactoring.
- If you must hand off mid-campaign, update **BOTH** files with timestamp + concrete next steps before stopping.
