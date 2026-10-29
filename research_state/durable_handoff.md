# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T10:00:04Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 224 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T10:00:04Z

Session start: 2026-10-29T10:00:04Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Phases 1-3 complete. **PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING** hardened with adversarial regime transition calibration and disagreement-pattern tests. **CURRENT MANDATE: PHASE 5 — RIGOROUS BACKTESTING (HEAVY, END-TO-END).**

**BASELINE (VERIFIED):** Regime hysteresis/stability, batched/vectorized composite signals with parity, and regime transition calibration with adversarial disagreement tracking are in place. Added `tests/test_signals_regime_calibration_adversarial.py` covering disagreement across regimes, rapid transitions, hysteresis stability, and calibration behavior. All 224 tests pass, mypy clean, working tree clean.

**ABSOLUTE NEXT ACTION (HEAVY, END-TO-END):** Harden **stress testing** in `src/backtest/engine.py` with deterministic, no-lookahead safe scenarios (gap/crash/vol spike/liquidity crunch) covering fills/slippage/costs/partial fills/round lots, while preserving walk-forward/OOS/purge/embargo invariants. Add focused adversarial stress tests (e.g. `tests/test_backtest_stress_adversarial.py`) with strict numerical stability and serialization safety. If stress coverage is exhaustively complete with no remaining heavy gaps, harden **walk-forward/OOS robustness** further (purge/embargo edge cases, anchored/rolling parity, time-ordering) or add **round-lot/partial-fill** adversarial invariants. Do exactly one coherent heavy item fully end-to-end.

## Immediate Objectives (FIRST ACTIONS)
1. **Verify green baseline**: Run `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` → must be >=224 passing. Run `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean. Confirm `git status` clean and `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` returns zero.
2. **Target the single heavy item**: Inspect `src/backtest/engine.py`, `src/config.py` (BacktestConfig/RiskConfig), and existing backtest tests for gaps. Add deterministic stress scenarios with strict no-lookahead, preserve purge/embargo, validate round lots/partial fills/slippage/costs, ensure finite metrics and serialization safety.
3. **Harden & test end-to-end**: Run tests and mypy after changes. Update **BOTH** handoff files with a fresh UTC timestamp, concrete summary of what was done, exact remaining targets with file paths, and next steps if any heavy work remains. Keep them byte-for-byte identical.

## Concrete Targets
- **Primary:** `src/backtest/engine.py` — stress testing (crash/gap/vol spike/liquidity crunch) with deterministic scenarios, strict no-lookahead, fills/slippage/costs/partial fills/round lots. Enforce finite metrics and serialization safety.
- **Supporting (if touched):** `src/config.py` — only if minimal config needed for stress scenarios.
- **Tests:** Add focused adversarial stress tests (e.g. `tests/test_backtest_stress_adversarial.py`) covering gap/crash/vol spike, liquidity crunch (partial fills), round-lot constraints, slippage/costs, no-lookahead invariants, and walk-forward/OOS stability.

## Verification (REQUIRED BEFORE HANDOFF)
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` → >=224 passing (no regressions).
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean.
- `git status` → clean working tree. No untracked junk.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero matches.
- If **ANY** heavy work remains after completing exactly one item end-to-end, **UPDATE BOTH** `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` with fresh timestamp, summary, exact remaining targets with file paths, and concrete next steps. Keep them byte-for-byte identical.

## Next Focus Campaign (Strict Priority - Execute In Order)
1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED
2. **Phase 2 — Orderflow microstructure**: ✅ COMPLETED
3. **Phase 3 — Volatility surface dynamics**: ✅ COMPLETED
4. **Phase 4 — Regime-aware signal engineering**: ✅ COMPLETED (regime transition calibration/adversarial disagreement hardening + adversarial tests)
5. **Phase 5 — Rigorous backtesting**: IN PROGRESS — **DO EXACTLY ONE HEAVY ITEM:** add deterministic stress testing (gap/crash/vol spike/liquidity crunch) with fills/slippage/costs/partial fills/round lots, no-lookahead, and focused adversarial tests in `src/backtest/engine.py`. If exhaustively complete, harden walk-forward/OOS/purge/embargo or add serialization/stability invariants.

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
- After any change: run `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` and `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any`.
- Keep changes minimal and correct. Prefer hardening over refactoring.
- If you must hand off mid-campaign, update **BOTH** files with timestamp + concrete next steps before stopping.
