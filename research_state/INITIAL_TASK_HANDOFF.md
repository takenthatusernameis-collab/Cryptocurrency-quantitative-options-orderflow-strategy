# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T07:26:23Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 216 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T07:26:23Z

Session start: 2026-10-29T07:26:23Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. The codebase has Phases 1-2 hardened and verified green (216 tests passing, mypy clean). **CURRENT MANDATE: PHASE 3 — VOLATILITY SURFACE DYNAMICS.** Pick EXACTLY ONE coherent heavy deliverable in `src/features/volatility.py` (skew/term structure/RR, ATM term structure, calendar spreads, max pain), harden it end-to-end against degenerate surfaces (sparse strikes/expiries, NaN/Inf, all-equal values, zero totals), vectorize where sensible with parity to scalar paths, enforce finite outputs/clamps, add/strengthen adversarial tests if needed, verify exports in `src/features/__init__.py`, run full suite + mypy, keep working tree clean. Do NOT regress Phases 1-2. Complete that ONE item fully before handing off with concrete remaining targets.

**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

### Immediate Objectives (FIRST ACTIONS)

1. **Verify green baseline**: Run `python -m pytest -q` → must be 216 passing. Run `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean. Confirm `git status` clean and zero TODO/FIXME/PLACEHOLDER/HACK/XXX.
2. **Attack Phase 3 with precision**: Focus on `src/features/volatility.py`. Strengthen ATM term structure / skew term structure / calendar spread coherence / max pain against adversarial cases (few points, NaN/Inf, inverted curves, division by zero). Ensure numerical guards, safe_divide, finite checks throughout.
3. **Harden & test**: Add focused adversarial tests if coverage gaps exist for degenerate surfaces; maintain parity between scalar/vectorized paths. Update both handoff files with fresh timestamp if leaving heavy work unfinished.

### ABSOLUTE FIRST ACTION (HEAVY, END-TO-END)

**PHASE 2 — ORDERFLOW MICROSTRUCTURE: COMPLETED (HARDENED).** All orderflow paths are adversarially hardened. 216 tests passing, mypy clean. Move to **PHASE 3 — VOLATILITY SURFACE DYNAMICS** as next heavy deliverable. Do **NOT** regress Phase 2; keep defenses intact. Pick **EXACTLY ONE** coherent heavy deliverable for Phase 3 and take it **ALL THE WAY TO DONE**.

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
