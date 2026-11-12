# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy* — real pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **quantitative, statistically-defensible evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Single durable handoff/task source:** this file only. `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/durable_handoff.md` are redirect stubs — do not action them or create new handoff files.
**Handoff refreshed:** 2026-11-12T15:15:00Z (UTC).

> **ANTI-STALL — READ BEFORE DOING ANYTHING ELSE.**
> EVAL-03 (regime-conditional sizing) is **COMPLETE**: `src/analytics/regime_sizing.py` +
> `tests/test_regime_sizing.py` (7 tests) pass; `scripts`/`main` run produced a real GO verdict:
> **50 windows, 460 OOS trades, regime Sharpe 0.042420205551953624 vs flat 0.026375107502127727,
> Sharpe delta +0.016045098049825898**, artifact `research_state/REGIME_SIZING_2026-11-12T151421.312990Z.json`.
> **Do NOT re-run environment verification, re-write EVAL-03, or re-run the phase-clone loop.**
> - Do NOT re-run `pytest --collect-only`, re-import deps, or re-verify the environment. Proven.
> - Go straight to **EVAL-04 + EVAL-05 below** and **write code this turn**.
> - Session is NOT complete until EVAL-04 **and** EVAL-05 each have real strategy-advancing code,
>   numeric-invariant tests, and cited nonzero numbers.
> - If you are about to run out of context/time: commit/push the partial new module(s) and leave this
>   handoff pointing at the exact next line to write — never leave the tree clean with the task "pending."
> - A final response that contains only "verified env / will start next session" is a **failed session**.

## P0 SAFETY — VERIFIED 2026-11-12T15:15:00Z — CLEAR
- `.env` **ABSENT**. `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- Runtime deps present on Python 3.12.3: `pydantic, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, yaml, pytest`.
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO NEXT9 unblock.**

## VERIFIED STATE — ground truth (DO NOT RE-VERIFY; go build EVAL-04/EVAL-05)
- **EVAL-02 COMPLETE:** `src/analytics/strategy_evaluation.py`, `tests/test_strategy_evaluation.py` (11 tests), `scripts/evaluate_strategy.py`, `tests/test_evaluate_strategy.py` (6 tests) all green. Artifacts `research_state/STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}`.
- **EVAL-03 COMPLETE (2026-11-12T15:15:00Z):** `src/analytics/regime_sizing.py` (687 lines, real implementation), `tests/test_regime_sizing.py` (**7 passed**). Real run: `PYTHONPATH=. python3 src/analytics/regime_sizing.py --seeds 1 2 3 4 5 --write` → **GO**, windows 50, trades 460, regime Sharpe 0.042420205551953624, flat Sharpe 0.026375107502127727, delta +0.016045098049825898, max-dd 0.004157360290141191. Artifact written.
- **CRITICAL root cause (still true, never repeat):** `src/campaign/integrated.py:694` builds signals as `[features] * n` (static snapshot repeated per step) → all signals `0` → OOS return/sharpe structurally `0.0`. New work must use **time-varying** signals and **never** accept 0-window/0-trade/0-return output as a pass.
- **Real code exists (do not rewrite from scratch):** `src/backtest/engine.py`, `src/backtest/options_hedging.py`, `src/features/*`, `src/signals/*`, `src/campaign/integrated.py`, `src/analytics/*`, `src/orderflow/`, `src/execution/*`, `src/risk/*`.
- **Real data loaders work:** `DataLoader().load_orderflow(...)` → 1000 trades / 20 liquidations / 8 funding; `load_options_chain(...)` → 30 quotes.
- **`scripts/run_backtest.py` is a vacuous smoke test** (single trade, Sharpe≈6.3 from 2 marks). Do not treat its numbers as strategy performance.
- **Phase272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` chain: ARCHIVED — LOW VALUE.** Do NOT re-implement, re-seal, extend, or "advance" this chain (Phase292+ closed).

## BOTTLENECKS REMOVED (this handoff)
| Bottleneck | Resolution |
|---|---|
| **Three competing handoffs / stale stubs** | **CLEARED.** Only this file is actionable; the other three are redirect stubs. |
| **`src/analytics/regime_sizing.py` did not compile** (`for r rows` SyntaxError at line 550) | **FIXED.** `python3 -m py_compile` clean; full EVAL-03 run now succeeds. |
| **EVAL-03 had no tests** | **ADDED.** `tests/test_regime_sizing.py` (7 numeric-invariant tests) passes. |
| **Vacuous green pipeline (all-zero signals)** | **DIAGNOSED.** Root cause pinned to `integrated.py:694`. All new tasks require time-varying signals and nonzero OOS. |
| **`research_state/` ~1 GB / 75k+ files can stall naive globbing** | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit paths/globs. |
| **Prior oversized "STRATEGY-EVAL-01 ACTIVE" never executed** | **RESCOPED.** Tasks below are dependency-ordered, falsifiable, and smaller. |

## NEXT FOCUS CAMPAIGN — ACTIVE TASK (mandatory, timestamped, heavy work required)

**`INIT-2026-11-12T15:15:00Z-STRATEGY-EVAL-04-CAPACITY-TCA-AND-EVAL-05-CROSS-VENUE-NETTING` — ACTIVE. START IMMEDIATELY. WRITE CODE THIS TURN.**

**Directive:** Execute **both** EVAL-04 and EVAL-05 end-to-end **in this session**. No deferral, no stubs, no placeholders, no partial completion, no follow-up questions, and no fallback to the archived phase-clone loop. If a required input is missing, *build* it deterministically from the existing data layer — do not stop to ask. Record exact commands/results/caveats.

### EVAL-04 — Capacity / liquidity-aware execution TCA (do this FIRST)
1. New module `src/analytics/capacity_aware_tca.py`: model slippage/fee as a function of **participation rate** and **orderflow imbalance**; size trades to keep expected transaction cost below a configurable budget; report turnover, realized cost bps, and **net-of-cost OOS return**. Deterministic, finite-guarded, strict-serializable via `serialize_metrics_strict` / `assert_json_valid`. No `pass`, `NotImplementedError`, or `TODO`.
2. New `tests/test_capacity_aware_tca.py` asserting **numeric invariants** (cost increases with participation rate; net return = gross − cost within tolerance; budget respected; finite metrics; determinism).
3. Real run vs a naive/flat-cost baseline across **seeds 1–5** using `WalkForwardBacktest` with **time-varying** signals. Cite `num_windows>0`, `oos_trade_count>0`, nonzero `oos_return`, and advancement delta vs baseline. Zero windows/trades/return = **failure**.

### EVAL-05 — Cross-venue netting (do this SECOND, same session)
1. New module `src/analytics/cross_venue_netting.py`: net BTC/ETH/SOL delta across a **synthetic multi-venue** layer before executing; report gross vs net notional and cost saved. Deterministic, finite-guarded, strict-serializable. No placeholders.
2. New `tests/test_cross_venue_netting.py` asserting **numeric invariants** (net notional ≤ gross; cost saved ≥ 0; offsetting positions reduce absolute net; reconciliation to tolerance; determinism).
3. Real run: report gross notional, net notional, cost saved, and net-of-cost OOS return vs no-netting baseline. Nonzero and finite required.

### CAMPAIGN EXIT GATE (hard stop; do not end the turn until ALL true)
1. `src/analytics/capacity_aware_tca.py` + `tests/test_capacity_aware_tca.py` exist; `PYTHONPATH=. python3 -m pytest -q tests/test_capacity_aware_tca.py` passes — paste the pass line.
2. `src/analytics/cross_venue_netting.py` + `tests/test_cross_venue_netting.py` exist; `PYTHONPATH=. python3 -m pytest -q tests/test_cross_venue_netting.py` passes — paste the pass line.
3. Real EVAL-04 and EVAL-05 runs produce **nonzero** windows/trades/return and finite metrics; paste the actual numbers + advancement delta vs baseline.
4. `python3 -m py_compile` clean on all new files.
5. P0 intact: `.env` absent, `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`.
6. No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper added.
7. Write artifacts under `research_state/` (explicit filenames, never enumerate the dir) and update **this** handoff in place with the new verified numbers and the next task `INIT-<UTC>-STRATEGY-EVAL-06-...`.

**Anti-cheat:** do not return `{"valid": True}` or empty dicts. Tests must assert *numeric invariants*. A `valid=true` assertion is a failure. Never accept all-zero-signal output as a pass.

## HANDOFF DISCIPLINE
- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- After EVAL-04/EVAL-05 are sealed (tests green + nonzero numbers cited), replace the active task with **`INIT-<UTC>-STRATEGY-EVAL-06-...`** continuing to advance the strategy (e.g. regime-conditional execution, gamma/inventory-aware hedging sizing, orderflow-toxicity gating) — **never** return to the archived phase-clone loop, and **never** accept all-zero-signal output as a pass.
- Final responses must not ask follow-up questions.

## SCOPE & HARD GUARDS (non-negotiable)
- **Allowed:** `src/`, `scripts/`, `tests/`, `research_state/`. Additive, deterministic, bounded, paper-only, guarded.
- **Forbidden:** live trading, `.env` creation, venue/config/credential mutation, NEXT9 unblock, and any new `phaseNN_*_post_attribution_seal_orchestrator` wrapper.
- Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Do not refactor sealed legacy phases.