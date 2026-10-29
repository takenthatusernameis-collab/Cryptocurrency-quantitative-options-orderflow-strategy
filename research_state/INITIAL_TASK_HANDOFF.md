# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T08:38:40Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 216 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T08:38:40Z

Session start: 2026-10-29T08:38:40Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. The codebase has Phases 1-3 hardened and verified green (216 tests passing, mypy clean). **CURRENT MANDATE: PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING.**

**COMPLETED THIS SESSION (END-TO-END):** Hardened regime detection with hysteresis/stability in `src/signals/composite.py` — added raw regime detection, stateful hysteresis (require N confirmations to flip regimes), regime transition penalties on strength/confidence, `reset_regime_state()` for backtesting independence. All adversarial guards preserved (NaN/Inf/extremes). Verified 216 tests passing, mypy clean, git status clean.

**NEXT MANDATE:** Pick EXACTLY ONE new coherent heavy deliverable for Phase 4 (or move to Phase 5 only if no heavy Phase 4 work remains) and take it ALL THE WAY TO DONE.

## Immediate Objectives (FIRST ACTIONS)

1. **Verify green baseline**: Run `python -m pytest -q` → must be 216 passing. Run `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean. Confirm `git status` clean and zero TODO/FIXME/PLACEHOLDER/HACK/XXX.
2. **Continue Phase 4 with precision**: Focus on remaining heavy Phase 4 work. Pick EXACTLY ONE coherent heavy item from targets below.
3. **Harden & test**: Add focused adversarial tests if coverage gaps exist; maintain determinism. Update both handoff files with fresh timestamp if leaving heavy work unfinished.

### ABSOLUTE FIRST ACTION (HEAVY, END-TO-END)
**PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING:** Regime hysteresis/stability COMPLETED. Remaining heavy options: (1) vectorized/batched composite signal generation with parity to scalar, numerical guards, tests; (2) regime transition calibration/adversarial disagreement patterns hardening; (3) if Phase 4 truly complete, move to **PHASE 5 — RIGOROUS BACKTESTING** starting with fills/slippage/costs/partial fills/round lots/walk-forward/OOS/stress with no-lookahead.

### CONCRETE TARGETS (COMPLETED THIS SESSION)
- `src/signals/composite.py`: Added `_detect_regime_raw()`, stateful hysteresis with confirmation threshold, regime transition penalties on strength and confidence, `reset_regime_state()` method. Deterministic, hardened against noisy regime flips.

### NEXT CONCRETE TARGETS (MUST HIT)
Pick EXACTLY ONE:
1. **Vectorized/batched composite signals** in `src/signals/composite.py` — add vectorized path (e.g., `generate_signals_batch`) with parity to scalar, NaN/Inf guards, deterministic ordering, adversarial tests.
2. **Regime calibration against adversarial disagreement** — enhance conflict resolution with regime-aware calibration, stability metrics, tests.
3. **Phase 5 start** if Phase 4 complete — `src/backtesting/engine.py`: fills/slippage/costs/partial fills/round lots/walk-forward/OOS/stress with no-lookahead, hardened end-to-end.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` → must be >= 216 passing (do not regress).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean.
- `git status` → clean working tree. No untracked junk.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero matches.
- If **ANY** heavy work remains after completing exactly one item end-to-end, **UPDATE BOTH** `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` with a fresh UTC timestamp, summary, exact remaining targets with file paths, and concrete next steps. Keep them byte-for-byte identical.

## Next Focus Campaign (Strict Priority - Execute In Order)
1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED
2. **Phase 2 — Orderflow microstructure**: ✅ COMPLETED
3. **Phase 3 — Volatility surface dynamics**: ✅ COMPLETED
4. **Phase 4 — Regime-aware signal engineering**: IN PROGRESS (regime hardening + hysteresis DONE). Continue with exactly one heavy item.
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
