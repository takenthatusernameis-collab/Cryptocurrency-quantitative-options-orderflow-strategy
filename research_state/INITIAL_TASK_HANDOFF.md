# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T11:22:28Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 239 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T11:22:28Z

Session start: 2026-10-29T11:22:28Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Phases 1-3 complete. **PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING** hardened. **PHASE 5 — RIGOROUS BACKTESTING: STRESS-TESTING + WALK-FORWARD/OOS ROBUSTNESS HARDENING COMPLETE.**

**BASELINE (VERIFIED):** Stress scenarios (crash/gap-down/vol-spike/liquidity-crunch) with deterministic replay, no-lookahead, finite metrics, serialization safety, round-lot/partial-fill invariants. Walk-forward/OOS hardened with strict time ordering across tz-aware/naive datetimes (normalized to UTC), purge/embargo clamping/overrides, anchored expanding windows, rolling parity, determinism verification, and strict OOS serialization (`serialize_oos`/`assert_oos_finite`). Added `tests/test_walkforward_robustness_adversarial.py`. All 239 tests pass, mypy clean, working tree clean, zero TODO/FIXME/PLACEHOLDER/HACK/XXX.

## Immediate Objectives (FIRST ACTIONS)
1. **Verify green baseline**: Run `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` → must be >=239 passing. Run `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean. Confirm `git status` clean and `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` returns zero.
2. **Assess remaining gaps**: Phases 1-5 heavy items complete (dealer positioning/gamma, orderflow microstructure, volatility surface dynamics, regime-aware signal engineering, rigorous backtesting with stress + walk-forward/OOS robustness). If extending, pick exactly one coherent heavy quantitative item end-to-end (e.g. additional hardening of cross-symbol walk-forward with regime-dependent costs/latency, or portfolio-level walk-forward with correlation constraints and serialization invariants) without scaffolding.
3. **Handoff if stopping**: Update **BOTH** handoff files with fresh UTC timestamp, concrete summary, exact remaining targets with file paths, and next steps. Keep byte-for-byte identical.

## Concrete Targets
- **Completed:** `src/backtest/engine.py` — stress scenarios + walk-forward/OOS with purge/embargo, anchored/rolling, strict time-ordering (tz-normalized), determinism, finite/serialization invariants. `tests/test_backtest_stress_adversarial.py`, `tests/test_walkforward_robustness_adversarial.py`.
- **Next heavy item (if continuing):** portfolio-level walk-forward/OOS with cross-symbol correlation constraints, regime-dependent transaction costs/slippage, and strict serialization/stability invariants in `src/backtest/engine.py` + `tests/` (exactly one item, end-to-end).

## Verification (REQUIRED BEFORE HANDOFF)
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` → >=239 passing.
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean.
- `git status` → clean working tree. No untracked junk.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero matches.
- If **ANY** heavy work remains after completing exactly one item end-to-end, **UPDATE BOTH** `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` with fresh timestamp, summary, exact remaining targets with file paths, and concrete next steps. Keep them byte-for-byte identical.

## Next Focus Campaign (Strict Priority - Execute In Order)
1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED
2. **Phase 2 — Orderflow microstructure**: ✅ COMPLETED
3. **Phase 3 — Volatility surface dynamics**: ✅ COMPLETED
4. **Phase 4 — Regime-aware signal engineering**: ✅ COMPLETED
5. **Phase 5 — Rigorous backtesting**: ✅ COMPLETED (stress-testing + walk-forward/OOS purge/embargo/anchored-rolling/time-ordering/serialization/determinism hardening)

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
- After any change: run verification commands above.
- Keep changes minimal and correct. Prefer hardening over refactoring.
- If you must hand off mid-campaign, update **BOTH** files with timestamp + concrete next steps before stopping.
