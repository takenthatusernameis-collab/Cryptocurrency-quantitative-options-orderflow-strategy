# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-12T17:45:00Z (UTC). EVAL-06 sealed NO-GO; EVAL-07 shipped COMPLETE; EVAL-08 is the ACTIVE task below. (handoff confirmed this session; no new bottlenecks found)
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are pointers/stubs — do not action them or create new handoff files.

---

## INITIAL TASK MESSAGE (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-12T17:45:00Z-STRATEGY-EVAL-08-CROSS-VENUE-NETTING`
**STATUS:** ACTIVE. This is the single next task. Do not pick a different task.

> Execute EVAL-08 end-to-end this session: cross-venue delta netting. EVAL-07 (capacity/liquidity-aware TCA)
> is shipped COMPLETE — artifact `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`; its signal
> series, walk-forward engine, and cost model are verified and must be REUSED, not rewritten.
>
> **Deliverable 1 — module `src/analytics/cross_venue_netting.py` (build, do not stub):**
> - Gross vs net notional: for each symbol/window, track gross traded notional (sum of |notional| across
>   all legs/venues) and net notional (|sum of signed notionals|). Delta netting = gross − net; report
>   net-notional ratio and gross/net per venue per window.
> - Cost saved: compare realized cost under netting vs no-netting (flat-cost baseline at 1 bp one-way,
>   matching EVAL-07/EVAL-06). Report cost saved bps and USD per window and aggregate.
> - Per-venue capacity: reuse the EVAL-07 participation-rate cost model + capacity cap (<= 20% of bar
>   liquidity) so netting never silently exceeds venue capacity; clamp/raise `InsufficientCapacity`
>   deterministically.
> - Net-of-cost OOS: run the EVAL-06/EVAL-07 signal series through the netting sizer inside the
>   walk-forward OOS and report net return/Sharpe/max-DD per seed and aggregate, WITH netting vs WITHOUT
>   netting (no-netting baseline). Reuse `src/analytics/strategy_evaluation.py` metrics helpers and the
>   walk-forward engine (`src/backtest/engine.py`); do not duplicate bootstrap/permutation logic.
> - CLI: `python3 src/analytics/cross_venue_netting.py --seeds 1 2 3 4 5 --write` writing
>   `research_state/CROSS_VENUE_NETTING_<UTC>.json` + `.md`, strict-serializable, never emits
>   `{"valid": True}`.
>
> **Deliverable 2 — tests `tests/test_cross_venue_netting.py`:** determinism across two processes,
> net-notional <= gross-notional invariant, netting cost-saved >= 0 invariant, capacity clamp invariant,
> turnover in [0, 2], finite/nonzero metrics on real-run seeds, CLI entry test. All must pass.
>
> **Exit gate (ALL must be true before sealing):**
> - `python3 -m pytest tests/test_cross_venue_netting.py tests/test_capacity_aware_tca.py
>   tests/test_strategy_falsification.py tests/test_oos_walkforward.py tests/test_integrated_campaign.py -q` → all pass.
> - `python3 -m py_compile src/analytics/cross_venue_netting.py` clean.
> - Real run `--seeds 1 2 3 4 5 --write` produced nonzero windows/trades and finite net-of-cost metrics
>   for every seed; artifact paths cited in this handoff.
> - `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; next9_unblocked=false.
> - No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper.
> - Update this handoff in place: mark EVAL-08 COMPLETE with verified numbers, then set the new active
>   task to `INIT-<UTC>-STRATEGY-EVAL-09-GAMMA-INVENTORY-TOXICITY`.
>
> **EVAL-07 sealed record (do not re-run unless doing a seeds 1..10 sweep):**
> SHIPPED | seeds 1..5 all pass | mean_capacity_net_sharpe 8.250491 | mean_capacity_net_return 0.267855 |
> mean_baseline_net_sharpe 9.197960 | mean_baseline_net_return 0.323307 | capacity_vs_baseline_sharpe -0.947469 |
> capacity_vs_baseline_return -0.055452 | cost grid mean net Sharpe 9.1980/9.1571/8.9929/8.7863 at
> 0/1/5/10 bps (monotone decreasing) | 294 capacity-limited + 294 budget-limited orders across seeds |
> artifact `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}` | exit gate 71 tests passed.
> Module `src/analytics/capacity_aware_tca.py` + `tests/test_capacity_aware_tca.py` COMPLETE and test-locked.
>
> **EVAL-06 sealed record (do not re-run unless doing a seeds 1..10 sweep):**
> NO-GO | pass_fraction 0.60 (3/5, need >=0.7) | mean_net_sharpe 8.860771 | mean_net_return
> 0.025482 | cost grid net Sharpe 8.9946/8.8608/8.0745/7.3734 at 0/1/5/10 bps | mean_permutation_p
> 0.752 | failing_conditions: seed 1 bootstrap_or_permutation, seed 4 bootstrap_or_permutation.
> Engine fix (chained per-window OOS equity) and `src/analytics/strategy_falsification.py` are
> COMPLETE and test-locked.

**Focus campaign queue (strictly sequential; heavy work is mandatory at each step):**
- `EVAL-07` — **COMPLETE (shipped this session):** capacity/liquidity-aware TCA
  (`src/analytics/capacity_aware_tca.py` + tests + CLI); artifact
  `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. Sealed record above.
- `EVAL-08` — **ACTIVE:** cross-venue delta netting (`src/analytics/cross_venue_netting.py`): gross vs net
  notional, cost saved, net-of-cost OOS vs no-netting baseline, with its own test file and CLI
  (see INITIAL TASK MESSAGE above for the full heavy-work spec and exit gate).
- `EVAL-09` — Gamma/inventory-aware hedge sizing and orderflow-toxicity gating
  (`src/analytics/gamma_inventory_hedge.py` + tests + CLI), closing the loop back to a final
  net-of-cost GO/NO-GO.

These were previously EVAL-04/05 but were **demoted**: TCA/netting on a vacuous signal was
meaningless, so EVAL-06 (real signal + net-of-cost falsification) ran first and is now sealed.

---

## VERIFIED STATE — ground truth (do not re-verify; build on it)

- **Environment:** Python 3.12.3; `pydantic, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, yaml, pytest` present. `pytest` works.
- **EVAL-02 COMPLETE:** `src/analytics/strategy_evaluation.py`, `tests/test_strategy_evaluation.py` (11 tests), `scripts/evaluate_strategy.py`, `tests/test_evaluate_strategy.py` (6 tests) green. Artifacts `research_state/STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}`.
- **EVAL-03 COMPLETE:** `src/analytics/regime_sizing.py` + `tests/test_regime_sizing.py` (7 tests). GO; 50 windows; 460 trades; regime Sharpe 0.042420205551953624 vs flat 0.026375107502127727; delta +0.016045098049825898; max-DD 0.004157360290141191. Artifact `research_state/REGIME_SIZING_2026-11-12T151421.312990Z.json`.
- **EVAL-07 COMPLETE (shipped this session):** `src/analytics/capacity_aware_tca.py` + `tests/test_capacity_aware_tca.py` + CLI. Artifact
  `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. 5 seeds (1-5), 10 windows each, nonzero trades (134-240), finite metrics:
  mean_capacity_net_sharpe 8.250491, mean_capacity_net_return 0.267855 vs flat baseline 9.197960/0.323307; cost grid monotone
  9.1980/9.1571/8.9929/8.7863 at 0/1/5/10 bps; 294 capacity-limited + 294 budget-limited orders across seeds. Exit gate 71 tests passed.
- **ROOT-CAUSE FIX #1 (DONE this session) — non-determinism:** `_load_orderflow` and `_load_options_chain` used salted `hash((symbol, venue))`, so synthetic fallbacks changed every process. Replaced with `_stable_seed()` (SHA-256). Verified: two separate processes produce byte-identical feature dicts.
- **ROOT-CAUSE FIX #2 (DONE this session) — vacuous all-zero signals:** `_step_feature_engineering` repeated one static feature snapshot across all steps (`[f] * n`), so every signal was 0 and OOS return/Sharpe were structurally 0.0. Replaced with `_time_varying_signal_series()` + `_rolling_realized_vol()`: causal trailing fast/slow momentum z-scores blended with the static options/orderflow snapshot through `CompositeSignalGenerator`.
- **Post-fix real run (seed 42, 500 points, purge 10 / embargo 5, 10 windows):**
  - Portfolio OOS return **0.010296791740144254**, Sharpe **0.1741937230265782**, stability 0.6405971890324178.
  - Per-symbol OOS trade counts: BTC 72, ETH 59, SOL 185.
  - Signal coverage (long/short/flat): BTC 134/0/366, ETH 112/0/388, SOL 312/0/188.
  - **Per-symbol OOS return defect:** FIXED in EVAL-06 step 1 — `WalkForwardBacktest` now chains per-window equity curves (`prod(1+r_w)-1`); aggregate return/Sharpe/max-DD derive from the chained curve in both anchored/rolling branches and `PortfolioWalkForwardBacktest`. Test-locked by `tests/test_oos_walkforward.py`.
- **Regression tests added this session:** `tests/test_integrated_signal_series.py` (3 passed) locks `_stable_seed` stability, non-all-zero signals, and causality (truncating future prices cannot change earlier signals).
- **Real data loaders work:** `DataLoader().load_orderflow(...)` → 1000 trades / 20 liquidations / 8 funding; `load_options_chain(...)` → 30 quotes.
- **Reusable real code (do not rewrite from scratch):** `src/backtest/engine.py`, `src/backtest/options_hedging.py`, `src/features/*`, `src/signals/*`, `src/campaign/integrated.py`, `src/analytics/*`, `src/orderflow/` (incl. legacy Phase 23 orderflow alpha), `src/execution/*`, `src/risk/*`. Legacy Phase 15–19 and Phase 21 execution/risk/observability modules remain available as reference implementations; do not extend them.
- **`scripts/run_backtest.py` is a vacuous smoke test** (single trade, Sharpe≈6.3 from 2 marks). Do not treat its numbers as strategy performance.

## BOTTLENECKS REMOVED (this session)
| Bottleneck | Resolution |
|---|---|
| Four competing handoffs / stale stubs | **CLEARED.** `research_state/durable_handoff.md` is the single source of truth; root + NEXT_SESSION files are pointers. |
| `tests/test_campaign_resume.py::test_durable_handoff_is_source_of_truth` failing | **FIXED** by restoring this file as the authoritative handoff with the required `SINGLE DURABLE HANDOFF` / `INITIAL TASK MESSAGE` markers. |
| Cross-process non-determinism (salted `hash()`) | **FIXED** with `_stable_seed()` (SHA-256); verified across two processes. |
| All-zero signal series → 0 windows/trades/return | **FIXED** with time-varying causal momentum z-scores; real run now has 10 windows and nonzero portfolio return/Sharpe. |
| Per-symbol OOS return excluded open-position MTM | **FIXED in EVAL-06** via chained per-window OOS equity; test-locked. |
| `research_state/` ~5 GB / ~75k files can stall naive globbing | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit filenames/globs. |
| Phase 272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` clone treadmill | **CLOSED.** Do not implement/seal/advance Phase 292+. |
| EVAL-07 capacity-aware TCA not yet built | **SHIPPED.** `src/analytics/capacity_aware_tca.py` + `tests/test_capacity_aware_tca.py` + CLI built, real-run artifact written, 71-test exit gate green. |

**Tree verified 2026-11-12T17:45:00Z (this session):** EVAL-07 shipped COMPLETE; new files `src/analytics/capacity_aware_tca.py`, `tests/test_capacity_aware_tca.py` present; artifacts
`research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}` written; EVAL-06 sealed NO-GO artifacts present
`research_state/STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`. `src/analytics/cross_venue_netting.py` not yet started
(EVAL-08 ACTIVE). No active blockers; EVAL-08 is the only open item. Working tree has uncommitted new files (commit before
handing off per discipline).

## P0 SAFETY — CLEAR
- `.env` **ABSENT**. `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO NEXT9 unblock.**

## SCOPE & HARD GUARDS (non-negotiable)
- **Allowed:** `src/`, `scripts/`, `tests/`, `research_state/` (explicit files only). Additive, deterministic, bounded, paper-only, guarded.
- **Forbidden:** live trading, `.env` creation, venue/config/credential mutation, NEXT9 unblock, any new `phaseNN_*_post_attribution_seal_orchestrator` wrapper, and refactoring sealed legacy phases.
- Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`.

## HANDOFF DISCIPLINE
- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- Work the queue strictly in order: EVAL-07 (capacity-aware TCA, COMPLETE) → EVAL-08 (cross-venue netting, ACTIVE) → EVAL-09 (gamma/inventory hedge + toxicity gating). Each task must ship a real module, a numeric-invariant test file, a CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If context/time runs out: commit/push the partial new module and leave this file pointing at the exact next line to write. Never leave the tree clean with the task "pending."
- A final response containing only "verified env / will start next session" is a **failed session**.
- Final responses must not ask follow-up questions.