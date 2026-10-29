# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T08:26:58Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 216 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T08:26:58Z

Session start: 2026-10-29T08:26:58Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. The codebase has Phases 1-3 hardened and verified green (216 tests passing, mypy clean). **CURRENT MANDATE: PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING.** Pick EXACTLY ONE coherent heavy deliverable in `src/signals/composite.py` (cross-features, calibration, normalization, feature leakage prevention, determinism), harden it end-to-end against degenerate inputs (NaN/Inf, extreme GEX, zero totals, non-finite components), enforce finite outputs/clamps, vectorize where sensible with parity, add/strengthen adversarial tests if needed, verify exports in `src/signals/__init__.py`, run full suite + mypy, keep working tree clean. Do NOT regress Phases 1-3. Complete that ONE item fully before handing off with concrete remaining targets.

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

### Immediate Objectives (FIRST ACTIONS)

1. **Verify green baseline**: Run `python -m pytest -q` → must be 216 passing. Run `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean. Confirm `git status` clean and zero TODO/FIXME/PLACEHOLDER/HACK/XXX.
2. **Attack Phase 4 with precision**: Focus on `src/signals/composite.py`. Strengthen regime detection / cross-features / calibration / normalization against adversarial cases (NaN/Inf inputs, extreme GEX, zero totals, non-finite components, regime weight divergence). Ensure numerical guards, finite checks, no feature leakage, deterministic outputs throughout.
3. **Harden & test**: Add focused adversarial tests if coverage gaps exist; maintain determinism. Update both handoff files with fresh timestamp if leaving heavy work unfinished.

### ABSOLUTE FIRST ACTION (HEAVY, END-TO-END)

**PHASE 3 — VOLATILITY SURFACE DYNAMICS: COMPLETED (VERIFIED).** `src/features/volatility.py` already implements ATM term structure, skew/RR term structures, calendar-spread coherence via term structures, max pain — all with scalar+vectorized parity, numerical guards (safe_divide, finite checks, NaN/Inf/clamp), degenerate-surface handling (sparse strikes/expiries, all-equal values, zero totals), and full exports in `src/features/__init__.py`. Tests green, mypy clean. Do **NOT** regress Phase 3; keep defenses intact. Move to **PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING** as next heavy deliverable. Pick **EXACTLY ONE** coherent heavy deliverable for Phase 4 and take it **ALL THE WAY TO DONE**.

### CONCRETE TARGETS (COMPLETED) — FOCUS: `src/features/volatility.py`
Phase 3 completed and verified. ATM/term structure & skew (put-call skew, risk reversal, skew/RR/IV skew term structures), calendar spread coherence via tenor-sorted term structures, max pain — all adversarially hardened with scalar+vectorized parity, finite-output clamps, degenerate-surface guards. Exports/integration verified; tests passing.

### CONCRETE TARGETS (COMPLETED) — FOCUS: `src/features/orderflow.py`
Phase 2 completed and verified. Adversarial hardening in place for signed volume/cumulative delta (scalar+vectorized parity), VPIN/toxicity (bucket guards, capping, clamping), absorption/aggressive flow (degenerate/NaN/Inf), multi-horizon orderflow with decay weighting (finite/clamp guarantees). Exports/integration verified; tests passing.

### NEXT CONCRETE TARGETS (MUST HIT) — FOCUS: `src/signals/composite.py`
Start **Phase 4 — Regime-aware signal engineering** with exactly one heavy item, end-to-end:

1. **Cross-features / regime detection hardening** — Harden `_detect_regime` against degenerate inputs (NaN/Inf GEX/skew/PCR, extreme magnitudes, zero totals); ensure finite regime labels and stable boundaries; prevent feature leakage (no forward-looking inputs).
2. **Calibration & normalization** — Normalize component signals to stable ranges; calibrate confidence so it reflects true component agreement/dispersion; clamp all outputs finite.
3. **Determinism** — Ensure no hidden global state, no nondeterministic ordering, reproducible outputs for identical inputs across runs.
4. **Exports/integration** — Verify `src/signals/__init__.py` remains correct; no API changes unless strictly necessary with full regression.
5. **Adversarial tests** — Add/strengthen focused tests covering degenerate inputs, NaN/Inf, extreme GEX, regime boundary stability, determinism; keep suite green.

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
3. **Phase 3 — Volatility surface dynamics**: ✅ COMPLETED (ATM term structure, skew/RR term structures, calendar-spread coherence, max pain; degenerate-surface guards, scalar+vectorized parity, numerical stability).
4. **Phase 4 — Regime-aware signal engineering (CURRENT MANDATE)**: cross-features, calibration, normalization, feature leakage prevention, determinism. **HEAVY WORK REQUIRED.**
5. **Phase 5 — Rigorous backtesting**: fills/slippage/costs/partial fills, round lots, walk-forward/OOS, stress, transaction costs, sanitized metrics, strict no-lookahead.

## MANDATE (Non-Negotiable)
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
