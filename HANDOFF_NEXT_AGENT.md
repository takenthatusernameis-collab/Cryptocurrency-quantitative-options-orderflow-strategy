# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy* — real pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **quantitative, statistically-defensible evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Single durable handoff/task source:** this file only. `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/durable_handoff.md` are redirect stubs — do not action them or create new handoff files.
**Handoff refreshed:** 2026-11-12T14:18:01Z (UTC).

> **ANTI-STALL — READ BEFORE DOING ANYTHING ELSE.**
> EVAL-02 (STRATEGY-EVAL-02) is **COMPLETE**: `src/analytics/strategy_evaluation.py` and
> `tests/test_strategy_evaluation.py` (11 tests) pass under `python3 -m pytest`;
> `scripts/evaluate_strategy.py` and `tests/test_evaluate_strategy.py` (6 tests) pass;
> `research_state/STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}` written with real
> numbers, block-bootstrap CIs, attribution reconciliation, and a GO/NO-GO verdict.
> A nonzero-OOS backtest was produced and cited (windows 10, oos_ret 0.013256590811846545,
> sharpe 0.18553531464652903, trades 876). Do NOT re-run environment verification or
> re-write the EVAL-02 modules unless they are broken.
> - **DO NOT re-run `pytest --collect-only`, re-import deps, or re-verify the environment.** That is already proven. Re-verifying is the stall.
> - **Go straight to EVAL-03 (below): advance the *strategy* itself** — regime-conditional sizing, capacity/liquidity-aware execution TCA, or cross-venue netting. That is the only thing that moves the needle now.
> - **Session is NOT complete until EVAL-03 produces real, strategy-advancing code with tests and cited nonzero numbers.** Do not fall back to wrappers, orchestrator clones, or "valid=true" placeholders.
> - If you are about to run out of context/time with EVAL-03 incomplete: **commit/push the partial EVAL-03 file** and leave the handoff pointing at the exact next line to write — never leave the tree clean with the task "still pending."
> - A final response that contains only "verified env / will start next session" is a **failed session**.

## P0 SAFETY — VERIFIED 2026-11-12T14:18:01Z — CLEAR
- `.env` **ABSENT** (re-checked 14:18:01Z). `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- Runtime deps present on Python 3.12.3: `pydantic, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, yaml, pytest`. `python3 -m pytest --collect-only -q` → **5017 tests collected in ~12s**.
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO NEXT9 unblock.**

## VERIFIED STATE — ground truth (DO NOT RE-VERIFY; go build EVAL-03)
- **EVAL-02 COMPLETE (this session, 2026-11-12T14:18:01Z):** `src/analytics/strategy_evaluation.py`, `tests/test_strategy_evaluation.py` (11 tests pass), `scripts/evaluate_strategy.py`, `tests/test_evaluate_strategy.py` (6 tests pass) all exist and are green under `python3 -m pytest`. Artifacts `research_state/STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}` written with real numbers, bootstrap CIs, attribution reconciliation, GO/NO-GO.
- **Nonzero-OOS backtest cited:** `WalkForwardBacktest` with time-varying rolling-momentum signals over `_generate_price_paths(IntegratedConfig(seed=42, n_points=400, train_window=100, test_window=30, step_size=30))` → **windows 10, oos_ret 0.013256590811846545, sharpe 0.18553531464652903, trades 876**. `compute_metrics` on that OOS equity curve yields finite metrics (sharpe 0.1855, ann_return 0.0139, max_dd 0.0658).
- **CRITICAL root cause (still true, do not repeat):** `src/campaign/integrated.py:694` builds the signal series as `[features] * n` (static snapshot repeated per step) → **all signals `0`** → OOS return/sharpe structurally `0.0`. EVAL-02 fixed this by driving `WalkForwardBacktest` with time-varying signals. EVAL-03 must *never* accept all-zero-signal output as a pass.
- **Real code exists (do not rewrite from scratch):** `src/backtest/engine.py`, `src/backtest/options_hedging.py`, `src/features/*`, `src/signals/*`, `src/campaign/integrated.py`, `src/analytics/*`, `src/orderflow/`, `src/execution/*`, `src/risk/*`.
- **Real data loaders work:** `DataLoader().load_orderflow(...)` → 1000 trades / 20 liquidations / 8 funding; `load_options_chain(...)` → 30 quotes.
- **`scripts/run_backtest.py` is a vacuous smoke test** (single trade, Sharpe≈6.3 from 2 marks). Do not treat its numbers as strategy performance.
- **Phase272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` chain: ARCHIVED — LOW VALUE.** ~20 near-identical 259-line wrappers. **Do NOT re-implement, re-seal, extend, or "advance" this chain (Phase292+ is closed).**

## BOTTLENECKS REMOVED (this handoff)
| Bottleneck | Resolution |
|---|---|
| **Three competing handoffs / stale stubs** | **CLEARED.** Only this file is actionable; the other three are redirect stubs. |
| **Prior "STRATEGY-EVAL-01 ACTIVE" never executed across multiple sessions** | **ESCALATED & RESCOPED.** New task (below) is smaller, dependency-ordered, and its acceptance is falsifiable. Do not re-declare the old oversized task "active" and then not run it. |
| **Vacuous green pipeline (all-zero signals)** | **DIAGNOSED & REDIRECTED.** Root cause pinned to `integrated.py:694`. New task *requires* fixing signal construction or driving `WalkForwardBacktest`/`BacktestEngine` with time-varying signals, and *forbids* accepting 0-window/0-return output as success. |
| **`research_state/` is ~1 GB / 75k+ files and can stall naive globbing** | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit paths/globs. Generated step/phase dirs are disposable. |
| **No metric/bootstrap utilities exist** | **CONFIRMED** (grep found none). The new `src/analytics/strategy_evaluation.py` must implement them; scipy/numpy bootstrap CI verified feasible this session (block bootstrap → 95% CI). |

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, non-optional)

**`INIT-2026-11-12T14:18:01Z-STRATEGY-EVAL-03-ADVANCE-STRATEGY` — ACTIVE. START IMMEDIATELY. WRITE CODE THIS TURN.**

**Directive:** Execute end-to-end **in this session** (heavy work required). **No deferral, no stubs, no placeholders, no partial completion, no follow-up questions, and do NOT fall back to the archived phase-clone loop.** If a required input is missing, *build* it deterministically from the existing data layer — do not stop to ask. Record exact commands/results/caveats.

**Objective (why this matters):** EVAL-02 produced the repo's first real quantitative verdict and evaluation harness. EVAL-03 must now **advance the strategy itself** so the options+orderflow signal is more than a momentum proxy. Deliver one strategy advancement, fully tested, with real cited numbers. Choose exactly one of:
- **(a) Regime-conditional sizing:** detect volatility regime (low_vol/normal/high_vol/stress) from the training price path and scale position size per regime (e.g. smaller size in stress). Compare OOS Sharpe/max-dd vs flat sizing across seeds 1–5.
- **(b) Capacity/liquidity-aware execution TCA:** model slippage/fee as a function of participation rate and orderflow imbalance; size trades to keep expected transaction cost below a budget; report turnover, realized cost bps, and net-of-cost OOS return.
- **(c) Cross-venue netting:** net BTC/ETH/SOL delta across venues (synthetic multi-venue) before executing; report gross vs net notional and cost saved.

### EVAL-03 REQUIREMENTS (all mandatory)
1. **New module under `src/`** implementing the chosen advancement, deterministic, finite-guarded, strict-serializable via `serialize_metrics_strict` / `assert_json_valid`. No `pass`, no `NotImplementedError`, no `TODO`.
2. **New test file under `tests/`** asserting numeric invariants (finite, correct direction, CI brackets where applicable, reconciliation to tolerance), not `valid=true`.
3. **Real run:** run the strategy advancement vs a flat/naive baseline across seeds 1–5 using `WalkForwardBacktest` with **time-varying** signals. Cite real numbers: `num_windows>0`, `oos_trade_count>0`, nonzero `oos_return`, and the advancement's delta vs baseline (Sharpe, max_dd). If a run yields 0 windows/0 trades/0 return, that is a **failure**, not a pass.
4. **`python3 -m py_compile` clean on all new files.**
5. **`PYTHONPATH=. python3 -m pytest -q <new test file>` passes** — paste the actual pass line + nonzero numbers into your final response.
6. **P0 intact:** `.env` absent, `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`.
7. **No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper.** Do not touch the archived Phase272–291 chain.

**Anti-cheat:** do not return `{"valid": True}` or empty dicts. Tests must assert *numeric invariants*. A `valid=true` assertion is a failure. Never accept all-zero-signal output as a pass.

## DEFINITION OF DONE — SESSION EXIT GATE (hard stop; do not end the turn until satisfied)
This session counts as **successful** only if ALL of the following are true. If any is false, **keep working** — do not end with a plan.
1. New `src/` module for the chosen EVAL-03 advancement exists, imports cleanly, contains real implementations (no `pass`/`NotImplementedError`/`TODO`).
2. New `tests/` file exists and **`PYTHONPATH=. python3 -m pytest -q <new test file>` passes** — paste the actual pass line into your final response.
3. A real EVAL-03 run is produced and its real numbers (`num_windows`, `oos_ret`, `sharpe`, `trades`, plus advancement delta vs baseline) are pasted into your final response.
4. `python3 -m py_compile` clean on all new files.
5. P0 intact: `.env` still absent, `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`.
6. No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper added.

**Anti-cheat:** tests assert numeric invariants only — `valid=true` is a failure. Never accept all-zero-signal output as a pass.

## HANDOFF DISCIPLINE
- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- After EVAL-03 is sealed (tests green + nonzero, strategy-advancing numbers cited), replace the active task with **`INIT-<UTC>-STRATEGY-EVAL-04-...`** continuing to advance the strategy (e.g. if EVAL-03 did regime-conditional sizing, EVAL-04 does capacity-aware TCA or cross-venue netting, and vice versa) — **never** return to the archived phase-clone loop, and **never** accept all-zero-signal output as a pass.
- Final responses must not ask follow-up questions.

## SCOPE & HARD GUARDS (non-negotiable)
- **Allowed:** `src/`, `scripts/`, `tests/`, `research_state/`. Additive, deterministic, bounded, paper-only, guarded.
- **Forbidden:** live trading, `.env` creation, venue/config/credential mutation, NEXT9 unblock, and any new `phaseNN_*_post_attribution_seal_orchestrator` wrapper.
- Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Do not refactor sealed legacy phases.