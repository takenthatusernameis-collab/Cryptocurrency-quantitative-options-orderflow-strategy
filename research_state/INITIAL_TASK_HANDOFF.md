# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T08:31:15Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 216 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T08:31:15Z

Session start: 2026-10-29T08:31:15Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. The codebase has Phases 1-3 hardened and verified green (216 tests passing, mypy clean). **CURRENT MANDATE: PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING.**

**COMPLETED THIS SESSION (END-TO-END):** Hardened `src/signals/composite.py` as ONE coherent heavy deliverable — regime detection hardened against NaN/Inf/extreme values/degenerate PCR, weights normalized defensively with deterministic ordering, all component signals and composite/confidence clamped to finite ranges, conflict resolution made robust, feature-leakage-safe (only uses passed values; chain integration guarded), exports added in `src/signals/__init__.py`. Verified 216 tests passing, mypy clean, git status clean, no TODO/FIXME/PLACEHOLDER/HACK/XXX.

**NEXT MANDATE:** Pick EXACTLY ONE new coherent heavy deliverable for Phase 4 (or move to Phase 5 only if no heavy Phase 4 work remains) and take it ALL THE WAY TO DONE.

## Immediate Objectives (FIRST ACTIONS)

1. **Verify green baseline**: Run `python -m pytest -q` → must be 216 passing. Run `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean. Confirm `git status` clean and zero TODO/FIXME/PLACEHOLDER/HACK/XXX.
2. **Continue Phase 4 with precision**: Focus on remaining heavy Phase 4 work. Candidates: strengthen cross-feature regime transitions (hysteresis/stability across regimes), improve calibration against adversarial disagreement patterns, add vectorized/batched signal generation paths if missing with parity, or harden integration points. Pick EXACTLY ONE coherent heavy item.
3. **Harden & test**: Add focused adversarial tests if coverage gaps exist; maintain determinism. Update both handoff files with fresh timestamp if leaving heavy work unfinished.

### ABSOLUTE FIRST ACTION (HEAVY, END-TO-END)
**PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING (IN PROGRESS):** First heavy deliverable (`src/signals/composite.py`) COMPLETED end-to-end with adversarial hardening, normalization, calibration, determinism, exports. Do NOT regress. Next: pick EXACTLY ONE remaining heavy Phase 4 item and take it ALL THE WAY TO DONE. If Phase 4 has no more heavy uncompleted items, move to **PHASE 5 — RIGOROUS BACKTESTING** with one heavy deliverable.

### CONCRETE TARGETS (COMPLETED THIS SESSION)
- `src/signals/composite.py`: Regime detection hardened (NaN/Inf/extreme GEX/skew/PCR), normalized regime weights, component normalization/clamps, conflict resolution robust, confidence calibration hardened, deterministic sorted-weight aggregation, safe chain integration.
- `src/signals/__init__.py`: Exports added (`CompositeSignalGenerator`, `Signal`).

### NEXT CONCRETE TARGETS (MUST HIT)
Pick EXACTLY ONE:
1. **Regime stability/hysteresis** in `src/signals/composite.py` (or new `src/signals/regime.py`) — prevent rapid regime flipping on noisy inputs; add smoothing with guards, tests for stability, deterministic behavior.
2. **Vectorized/batched composite signals** — add vectorized path with parity to scalar, numerical guards, tests.
3. **Phase 5 start** if Phase 4 complete — `src/backtesting/engine.py` or similar: fills/slippage/costs/partial fills/round lots/walk-forward/OOS/stress with no-lookahead, hardened.

### VERIFICATION (REQUIRED BEFORE HANDOFF)
- `python -m pytest` → must be >= 216 passing (do not regress; fix any regressions immediately).
- `python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean, no new issues.
- `git status` → clean working tree. No untracked junk.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero matches.
- If **ANY** heavy work remains after completing exactly one item end-to-end, **UPDATE BOTH** `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` with a fresh UTC timestamp, a concise summary of what was done, exact remaining targets with file paths, and concrete next steps. Keep them byte-for-byte identical.

## Next Focus Campaign (Strict Priority - Execute In Order)
Project-name priority is law. Do not reorder.

1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED
2. **Phase 2 — Orderflow microstructure**: ✅ COMPLETED
3. **Phase 3 — Volatility surface dynamics**: ✅ COMPLETED
4. **Phase 4 — Regime-aware signal engineering**: IN PROGRESS (first heavy item DONE). Continue with exactly one heavy item.
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
