# DURABLE HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST
Timestamp (UTC): 2026-10-29T11:13:47Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 230 TESTS PASSING | 0 FAILING | MYPY CLEAN (--disallow-untyped-defs --warn-return-any) | WORKING TREE CLEAN | RE-VERIFIED 2026-10-29T11:13:47Z

Session start: 2026-10-29T11:13:47Z

## Initial Task Message
**EXECUTE IMMEDIATELY. NO EXPLORATION DIVERGENCES. NO SCOPING CREEP. NO SCORCHED-EARTH REWRITES.**

You are picking up the Cryptocurrency-quantitative-options-orderflow-strategy campaign. Phases 1-3 complete. **PHASE 4 — REGIME-AWARE SIGNAL ENGINEERING** hardened with adversarial regime transition calibration and disagreement-pattern tests. **PHASE 5 — RIGOROUS BACKTESTING: STRESS-TESTING ITEM COMPLETE.**

**BASELINE (VERIFIED):** Regime hysteresis/stability, batched/vectorized composite signals with parity, and regime transition calibration with adversarial disagreement tracking are in place. Added `tests/test_signals_regime_calibration_adversarial.py`. **Phase 5 stress testing complete:** added deterministic stress scenarios to `src/backtest/engine.py` (`StressScenario`, `StressTestResult`, `run_stress_scenario`, `run_deterministic_stress_suite`, plus `crash`/`gap_down`/`vol_spike`/`liquidity_crunch` builders) covering gap-down, sustained crash, volatility-spike whipsaw, and liquidity crunch (partial fills / round lots / slippage cap). Each scenario enforces strict no-lookahead (sequential price replay), numerical stability (finite equity/metrics), serialization safety (`serialize_metrics_strict` with `allow_nan=False`), round-lot and partial-fill invariants, and drawdown-limit compliance. Added `tests/test_backtest_stress_adversarial.py` with 6 adversarial tests including a determinism repeat-suite check. All 230 tests pass, mypy clean, working tree clean, zero TODO/FIXME/PLACEHOLDER/HACK/XXX.

## Immediate Objectives (FIRST ACTIONS)
1. **Verify green baseline**: Run `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` → must be >=230 passing. Run `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean. Confirm `git status` clean and `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` returns zero.
2. **Assess remaining Phase 5 gaps**: Stress-testing heavy item is complete end-to-end. If extending Phase 5 further, the next heavy item per the campaign is walk-forward/OOS robustness (purge/embargo edge cases, anchored/rolling parity, time-ordering) or additional serialization/stability invariants — do exactly one coherent heavy item fully end-to-end if continuing.
3. **Handoff if stopping**: Update **BOTH** handoff files with a fresh UTC timestamp, concrete summary of what was done, exact remaining targets with file paths, and next steps. Keep them byte-for-byte identical.

## Concrete Targets
- **Completed:** `src/backtest/engine.py` — deterministic stress testing (crash/gap-down/vol spike/liquidity crunch) with fills/slippage/costs/partial fills/round lots, strict no-lookahead, finite metrics, serialization safety. `tests/test_backtest_stress_adversarial.py` — focused adversarial stress tests.
- **Supporting (only if extending Phase 5):** `src/config.py` — only if minimal config needed for additional stress/walk-forward scenarios.
- **Next heavy item (if continuing Phase 5):** walk-forward/OOS purge/embargo edge cases, anchored/rolling parity, time-ordering invariants, or serialization/stability invariants in `src/backtest/engine.py` + `tests/`.

## Verification (REQUIRED BEFORE HANDOFF)
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m pytest -q` → >=230 passing (no regressions).
- `PYTHONPATH=/home/runner/work/_temp/kilo-home/.local/lib/python3.12/site-packages:/home/runner/work/_temp/kilo-home/.local/bin python -m mypy src/ --disallow-untyped-defs --warn-return-any` → clean.
- `git status` → clean working tree. No untracked junk.
- `grep -rn "TODO\|FIXME\|PLACEHOLDER\|HACK\|XXX" src/ tests/ scripts/` → zero matches.
- If **ANY** heavy work remains after completing exactly one item end-to-end, **UPDATE BOTH** `research_state/INITIAL_TASK_HANDOFF.md` and `research_state/durable_handoff.md` with fresh timestamp, summary, exact remaining targets with file paths, and concrete next steps. Keep them byte-for-byte identical.

## Next Focus Campaign (Strict Priority - Execute In Order)
1. **Phase 1 — Dealer positioning/gamma exposure**: ✅ COMPLETED
2. **Phase 2 — Orderflow microstructure**: ✅ COMPLETED
3. **Phase 3 — Volatility surface dynamics**: ✅ COMPLETED
4. **Phase 4 — Regime-aware signal engineering**: ✅ COMPLETED (regime transition calibration/adversarial disagreement hardening + adversarial tests)
5. **Phase 5 — Rigorous backtesting**: ✅ COMPLETED (stress-testing heavy item: deterministic crash/gap-down/vol-spike/liquidity-crunch scenarios with no-lookahead, finite metrics, serialization safety, round-lot/partial-fill invariants, adversarial tests). If extending, do exactly one heavy item: walk-forward/OOS purge/embargo edge cases or serialization/stability invariants.

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
