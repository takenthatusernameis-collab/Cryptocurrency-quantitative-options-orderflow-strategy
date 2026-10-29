# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T09:22:04Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 220 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T09:22:04Z

Session start: 2026-10-29T09:22:04Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. The codebase has Phases 1-3 hardened and verified green (220 tests passing, mypy clean). **CURRENT MANDATE: PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING.**

**COMPLETED THIS SESSION (END-TO-END):** Added batched/vectorized composite signal generation in `src/signals/composite.py` (`generate_signals_batch`, `generate_signals_vectorized`) with deterministic ordering, parity to scalar `generate_signal` across regime hysteresis, NaN/Inf/malformed input guards returning safe neutral signals without breaking sequence, and adversarial batch tests. Regime hysteresis/stability already in place. Verified 220 tests passing, mypy clean, git status clean.

**NEXT MANDATE:** Pick EXACTLY ONE new coherent heavy deliverable for Phase 4 (or move to Phase 5 only if no heavy Phase 4 work remains) and take it ALL THE WAY TO DONE.

## Immediate Objectives (FIRST ACTIONS)

1. **Verify green baseline**: Run `python -m pytest -q` → must be 220 passing. Run `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean. Confirm `git status` clean and zero TODO/FIXME/PLACEHOLDER/HACK/XXX.
2. **Continue Phase 4 with precision**: Focus on remaining heavy Phase 4 work. Pick EXACTLY ONE coherent heavy item from targets below.
3. **Harden & test**: Add focused adversarial tests if coverage gaps exist; maintain determinism. Update both handoff files with fresh timestamp if leaving heavy work unfinished.

### ABSOLUTE FIRST ACTION (HEAVY, END-TO-END)
**PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING:** Regime hysteresis/stability COMPLETED. Batched/vectorized signals with parity/guards COMPLETED. Remaining heavy options: (1) regime transition calibration/adversarial disagreement patterns hardening; (2) if Phase 4 truly complete, move to **PHASE 5 — RIGOROUS BACKTESTING** starting with fills/slippage/costs/partial fills/round lots/walk-forward/OOS/stress with no-lookahead.

### CONCRETE TARGETS (COMPLETED THIS SESSION)
- `src/signals/composite.py`: Added `generate_signals_batch()` and `generate_signals_vectorized()` with deterministic ordering, sequential regime state preservation, parity to scalar, and exception-safe neutral fallback for malformed/non-finite entries.
- `tests/test_signals_batch_parity.py`: Added adversarial batch tests (parity, hysteresis across sequence, deterministic ordering, NaN/Inf/malformed handling).

### NEXT CONCRETE TARGETS (MUST HIT)
Pick EXACTLY ONE:
1. **Regime calibration against adversarial disagreement** — enhance conflict resolution with regime-aware calibration, stability metrics, tests in `src/signals/composite.py` (and add focused tests).
2. **Phase 5 start** if Phase 4 complete — `src/backtest/engine.py`: fills/slippage/costs/partial fills/round lots/walk-forward/OOS/stress with no-lookahead, hardened end-to-end.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` → must be >= 220 passing (do not regress).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean.
- `git status` → clean working tree. No untracked junk.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero matches.
- If **ANY** heavy work remains after completing exactly one item end-to-end, **UPDATE BOTH** `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` with a fresh UTC timestamp, summary, exact remaining targets with file paths, and concrete next steps. Keep them byte-for-byte identical.

## Next Focus Campaign (Strict Priority - Execute In Order)
1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED
2. **Phase 2 — Orderflow microstructure**: ✅ COMPLETED
3. **Phase 3 — Volatility surface dynamics**: ✅ COMPLETED
4. **Phase 4 — Regime-aware signal engineering**: IN PROGRESS (regime hardening + hysteresis + batched/vectorized parity DONE). Continue with exactly one heavy item.
5. **Phase 5 — Rigorous backtesting**: PENDING

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
