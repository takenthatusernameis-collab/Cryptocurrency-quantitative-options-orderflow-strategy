# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T07:26:00Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 216 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T07:26:00Z

Session start: 2026-10-29T07:26:00Z

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

### IMMEDIATE OBJECTIVES (FIRST ACTIONS)

1. **Remove the handoff format bottleneck**: Update `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` to include the exact required section headers (`Initial Task Message`, `Immediate Objectives`, `Next Focus Campaign`, `MANDATE`) so `tests/test_campaign_resume.py::test_handoff_has_required_sections` passes. Keep both files byte-for-byte identical with a fresh UTC timestamp.
2. **Verify green suite**: After the handoff fix, run `python -m pytest -q` → must be 216 passing (back to the verified green state). Run `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean.
3. **Confirm clean tree**: `git status` clean, zero `TODO/FIXME/PLACEHOLDER/HACK/XXX` matches.

### ABSOLUTE FIRST ACTION (HEAVY, END-TO-END)

**PHASE 2 — ORDERFLOW MICROSTRUCTURE: COMPLETED (HARDENED).** All orderflow paths (signed volume/cumulative delta/vectorized parity, VPIN/toxicity, absorption, aggressive/passive flow) are adversarially hardened with finite guards, clamping, and parity checks. 216 tests passing, mypy clean. Move to **PHASE 3 — VOLATILITY SURFACE DYNAMICS** as next heavy deliverable. Do **NOT** regress Phase 2; keep defenses intact. Pick **EXACTLY ONE** coherent heavy deliverable for Phase 3 and take it **ALL THE WAY TO DONE**.**

### CONCRETE TARGETS (COMPLETED) — FOCUS: `src/features/orderflow.py`
Phase 2 completed and verified. Adversarial hardening in place for signed volume/cumulative delta (scalar+vectorized parity), VPIN/toxicity (bucket guards, capping, clamping), absorption/aggressive flow (degenerate/NaN/Inf), multi-horizon orderflow with decay weighting (finite/clamp guarantees). Exports/integration verified; tests passing.

### NEXT CONCRETE TARGETS (MUST HIT) — FOCUS: `src/features/volatility.py`
Start **Phase 3 — Volatility surface dynamics** with exactly one heavy item, end-to-end:

1. **ATM/term structure & skew** — Harden ATM volatility term structure, skew/RR metrics against degenerate surfaces (few strikes/expiries), NaN/Inf, monotonicity issues. Vectorize where sensible, enforce finite outputs and clamps.
2. **Calendar spreads / surface coherence** — Validate calendar spread consistency, guard against inverted/ill-posed curves, prevent division by zero.
3. **Max pain / edge cases** — Ensure max pain and related helpers are robust to sparse OI/volume, zero totals, extreme strikes.
4. **Exports/integration** — Verify `src/features/__init__.py` remains correct; no API changes unless strictly necessary with full regression.
5. **Adversarial tests** — Add/strengthen focused tests covering sparse/degenerate surfaces, NaN/Inf, all-equal values; keep suite green.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` → must be >= 216 passing (do not regress; fix any regressions immediately).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean, no new issues.
- `git status` → clean working tree. No untracked junk.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero matches.
- If **ANY** heavy work remains after completing exactly one item end-to-end, **UPDATE BOTH** `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` with a fresh UTC timestamp, a concise summary of what was done, exact remaining targets with file paths, and concrete next steps. Keep them byte-for-byte identical.

## Next Focus Campaign (Strict Priority - Execute In Order)
Project-name priority is law. Do not reorder.

1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED (hardened pin/flip zones, adversarial-safe, safely integrated).
2. **Phase 2 — Orderflow microstructure**: ✅ COMPLETED (hardened signed volume/cumulative delta, VPIN/toxicity, absorption/aggressive flow, multi-horizon with decay; adversarial-safe).
3. **Phase 3 — Volatility surface dynamics (CURRENT MANDATE)**: skew/term structure/RR, ATM term structure, calendar spreads, max pain. Degenerate-surface guards, numerical stability. **HEAVY WORK REQUIRED.**
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
