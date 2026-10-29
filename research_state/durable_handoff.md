# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T09:27:55Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 220 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T09:27:55Z

Session start: 2026-10-29T09:27:55Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Phases 1-3 are hardened and verified green (220 tests passing, mypy clean). **CURRENT MANDATE: PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING.**

**BASELINE (VERIFIED):** Regime hysteresis/stability in place. Batched/vectorized composite signals (`generate_signals_batch`, `generate_signals_vectorized`) added with deterministic ordering, sequential regime state preservation, parity to scalar `generate_signal`, and exception-safe neutral fallbacks for malformed/non-finite inputs. All 220 tests pass, mypy clean, working tree clean.

**ABSOLUTE NEXT ACTION (HEAVY, END-TO-END):** Harden regime transition calibration against adversarial disagreement patterns in `src/signals/composite.py`. This is the single remaining coherent heavy Phase 4 deliverable. If after deep inspection you find Phase 4 is already exhaustively complete with no remaining heavy work, move to **PHASE 5 — RIGOROUS BACKTESTING** starting with fills/slippage/costs/partial fills/round lots/walk-forward/OOS/stress with strict no-lookahead in `src/backtest/engine.py`. **Do exactly one of these, fully end-to-end.**

## Immediate Objectives (FIRST ACTIONS)
1. **Verify green baseline**: Run `python -m pytest -q` → must be 220 passing. Run `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean. Confirm `git status` clean and `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` returns zero.
2. **Target the single heavy item**: Inspect `src/signals/composite.py`, `src/signals/regime.py` (and related conflict resolution), and existing tests for gaps. Enhance conflict resolution with regime-aware calibration and stability metrics. Add focused adversarial tests. Maintain parity, determinism, numerical stability, and exception safety.
3. **Harden & test end-to-end**: Run tests and mypy after changes. Update **BOTH** handoff files with a fresh UTC timestamp, concrete summary of what was done, exact remaining targets with file paths, and next steps if any heavy work remains. Keep them byte-for-byte identical.

## Concrete Targets
- **Primary:** `src/signals/composite.py` — regime transition calibration/adversarial disagreement hardening (conflict resolution, regime-aware calibration, stability metrics). Preserve sequential hysteresis behavior.
- **Supporting (if touched):** `src/signals/regime.py`, `src/signals/conflict.py` (or equivalent) — only if necessary to make the above correct and minimal.
- **Tests:** Add/extend focused adversarial tests (e.g. `tests/test_signals_batch_parity.py` or new `tests/test_signals_regime_calibration_adversarial.py`) covering disagreement across regimes, rapid transitions, hysteresis stability, and calibration behavior.

## Verification (REQUIRED BEFORE HANDOFF)
- `python -m pytest` → >= 220 passing (no regressions).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean.
- `git status` → clean working tree. No untracked junk.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero matches.
- If **ANY** heavy work remains after completing exactly one item end-to-end, **UPDATE BOTH** `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` with fresh timestamp, summary, exact remaining targets with file paths, and concrete next steps. Keep them byte-for-byte identical.

## Next Focus Campaign (Strict Priority - Execute In Order)
1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED
2. **Phase 2 — Orderflow microstructure**: ✅ COMPLETED
3. **Phase 3 — Volatility surface dynamics**: ✅ COMPLETED
4. **Phase 4 — Regime-aware signal engineering**: IN PROGRESS — **DO EXACTLY ONE HEAVY ITEM:** regime transition calibration/adversarial disagreement patterns hardening in `src/signals/composite.py` (add tests). If exhaustively complete, go to Phase 5.
5. **Phase 5 — Rigorous backtesting**: PENDING

## MANDATE (Non-Negotiable)
- **Heavy engineering only.** Mathematical correctness mandatory.
- **Numerical stability required.** Vectorize where sensible. Defend all public paths.
- **No placeholders/TODOs/FIXMEs/HACKs/XXX.** Production-grade only.
- **Complete ONE major item fully end-to-end.** Leave concrete instructions if handing off.
- **Never stop at scaffolding.** Never avoid heavy quantitative work.
- **Bottlenecks removed by default.** Fix imports/types/tests immediately.
- **Determinism where relevant.** No hidden global state breaking reproducibility.
- **Working tree must remain clean.** No untracked junk.

## Execution Rules
- Read this handoff first. Treat both canonical files as identical.
- Work only in service of the project priority order.
- After any change: run `python -m pytest` and `python -m mypy src/ --disallow-untyped-defs --warn-return-any`.
- Keep changes minimal and correct. Prefer hardening over refactoring.
- If you must hand off mid-campaign, update **BOTH** files with timestamp + concrete next steps before stopping.
