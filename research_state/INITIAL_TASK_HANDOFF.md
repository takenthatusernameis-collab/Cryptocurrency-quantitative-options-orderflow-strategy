# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T07:21:01Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 215 TESTS PASSING | 1 FAILING (test_campaign_resume.py::test_handoff_has_required_sections — handoff section format bottleneck) | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T07:21:01Z
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## Initial Task Message — FOR NEXT AGENTIC WORK SESSION (MANDATORY, NON-OPTIONAL)

Session start: 2026-10-29T07:21:01Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

### IMMEDIATE OBJECTIVES (FIRST ACTIONS)

1. **Remove the handoff format bottleneck**: Update `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` to include the exact required section headers (`Initial Task Message`, `Immediate Objectives`, `Next Focus Campaign`, `MANDATE`) so `tests/test_campaign_resume.py::test_handoff_has_required_sections` passes. Keep both files byte-for-byte identical with a fresh UTC timestamp.
2. **Verify green suite**: After the handoff fix, run `python -m pytest -q` → must be 216 passing (back to the verified green state). Run `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean.
3. **Confirm clean tree**: `git status` clean, zero `TODO/FIXME/PLACEHOLDER/HACK/XXX` matches.

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

## Next Focus Campaign (Strict Priority - Execute In Order)
Project-name priority is law. Do not reorder.

1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED (hardened pin/flip zones, adversarial-safe, safely integrated).
2. **Phase 2 — Orderflow microstructure (CURRENT MANDATE)**: signed volume, cumulative delta, VPIN/toxicity, absorption, aggressive/passive flow with adversarial guards. **HEAVY WORK REQUIRED.**
3. **Phase 3 — Volatility surface dynamics**: skew/term structure/RR, ATM term structure, calendar spreads, max pain. Degenerate-surface guards, numerical stability.
4. **Phase 4 — Regime-aware signal engineering**: cross-features, calibration, normalization, feature leakage prevention, determinism.
5. **Phase 5 — Rigorous backtesting**: fills/slippage/costs/partial fills, round lots, walk-forward/OOS, stress, transaction costs, sanitized metrics, strict no-lookahead.

## Mandate (Non-Negotiable)
- **Heavy engineering only.** Mathematical correctness is mandatory.
- **Numerical stability required.** Vectorize where sensible. Defend all public paths.
- **No placeholders/TODOs/FIXMEs/HACKs/XXX.** If you add code, it must be production-grade.
- **Complete ONE major item fully end-to-end.** Leave heavy work for the next agent with concrete instructions.
- **Never stop at scaffolding.** Never avoid heavy quantitative work.
- **Bottlenecks removed by default.** If anything blocks forward progress (imports/types/tests), fix it immediately.
- **Determinism where relevant.** No hidden global state that breaks reproducibility.
- **Working tree must remain clean.** No untracked junk.

## Execution Rules
- Read this handoff first. Treat both canonical files as identical.
- Work only in service of the project priority order.
- After any change: run `python -m pytest` and `python -m mypy src/ --disallow-untyped-defs --warn-return-any`.
- Keep changes minimal and correct. Prefer hardening over refactoring.
- If you must hand off mid-campaign, update **BOTH** files with timestamp + concrete next steps before stopping.
