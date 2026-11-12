# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-12T19:53:33Z (UTC). EVAL-07 sealed COMPLETE; EVAL-08 is the ACTIVE task below. Baseline exit-gate tests re-run green this session (74 passed, 67s). `src/analytics/cross_venue_netting.py` does not exist — EVAL-08 not started.
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are **retired pointer stubs** — do not action them and do not create new handoff files.

---

## INITIAL TASK MESSAGE (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-12T17:46:00Z-STRATEGY-EVAL-08-CROSS-VENUE-NETTING`
**STATUS:** ACTIVE. This is the single next task. Do not pick a different task. Do not re-verify the environment. Build the module, run the real evaluation, and seal it.

> Execute **EVAL-08 cross-venue delta netting** end-to-end this session. EVAL-07 (capacity/liquidity-aware
> TCA) is shipped COMPLETE — artifact `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`.
> Its signal series, walk-forward engine, and cost model are verified and must be **REUSED, not rewritten**.
>
> **Why this task, from the repo name:** the repo is a crypto **options + orderflow** strategy. Cross-venue
> delta netting is the capital-efficiency layer that makes the options book's net-of-cost evaluation
> realistic: the same delta exposure is often quoted on multiple venues, so gross notional overstates
> trading and cost. Netting is the prerequisite for EVAL-09's gamma/inventory hedge and for the final
> net-of-cost GO/NO-GO. This is heavy, real work — not a wrapper, not a stub, not an env check.
>
> ### Deliverable 1 — `src/analytics/cross_venue_netting.py` (build, do not stub)
> Create a real, deterministic, strict-serializable module with:
> - **Dataclasses:** `VenueLeg(symbol, venue, signed_notional_usd, abs_notional_usd)`;
>   `NettingWindow(window_index, test_start, test_end, gross_notional, net_notional, netting_benefit,
>   net_notional_ratio, cost_no_net_usd, cost_net_usd, cost_saved_usd, cost_saved_bps, turnover,
>   num_trades, capacity_limited_orders, regime)`; `SeedNettingResult(seed, windows, gross_notional,
>   net_notional, net_notional_ratio, cost_saved_usd, cost_saved_bps, oos_return_with_netting,
>   oos_sharpe_with_netting, oos_max_drawdown_with_netting, oos_return_without_netting,
>   oos_sharpe_without_netting, oos_max_drawdown_without_netting, num_trades, num_windows)`;
>   `CrossVenueNettingReport(report_id, generated_at, config, per_seed, aggregate, never_valid_true)`.
> - **Gross vs net notional:** for each symbol/window, model 3 deterministic synthetic venues
>   (`synthetic_a/b/c`) via `_stable_seed` — **no network, no venue API, no credentials**. Track
>   `gross_notional = sum(abs(leg.notional))` and `net_notional = abs(sum(leg.signed_notional))`;
>   `netting_benefit = gross - net`; `net_notional_ratio = net / gross` (guard gross==0 -> 1.0).
>   Report per-venue gross/net per window.
> - **Cost saved:** price both books with the EVAL-07 cost model (default 1 bp one-way baseline, same as
>   EVAL-06/EVAL-07). `cost_no_net = gross_notional * cost_bps / 1e4`,
>   `cost_net = net_notional * cost_bps / 1e4`, `cost_saved = cost_no_net - cost_net` (must be >= 0),
>   `cost_saved_bps = cost_saved / nav * 1e4`. Report USD and bps per window and aggregate.
> - **Per-venue capacity:** reuse `CapacityAwareSizer` + `VenueLiquidity` from
>   `src/analytics/capacity_aware_tca.py` (max participation <= 20% of bar liquidity). Clamp/raise
>   `InsufficientCapacity` deterministically; netting must never silently exceed venue capacity.
> - **Net-of-cost OOS:** run the EVAL-06/EVAL-07 signal series through the netting sizer inside the
>   walk-forward OOS and report net return / Sharpe / max-DD **per seed and aggregate, WITH netting vs
>   WITHOUT netting**. Reuse `src/analytics/strategy_evaluation.py::compute_metrics`,
>   `src/backtest/engine.py::WalkForwardBacktest`, and the EVAL-07 `_build_signal_series_capacity` /
>   `_static_context_capacity` / `_run_capacity_aware_walkforward` patterns. Do **not** duplicate
>   bootstrap/permutation logic (EVAL-06 already owns it).
> - **CLI:** `python3 src/analytics/cross_venue_netting.py --seeds 1 2 3 4 5 --write` writing
>   `research_state/CROSS_VENUE_NETTING_<UTC>.json` + `.md`. Strict-serializable via
>   `serialize_metrics_strict` / `assert_json_valid`; never emits `{"valid": True}`.
>
> ### Deliverable 2 — `tests/test_cross_venue_netting.py` (numeric invariants; all must pass)
> - determinism across two separate processes (byte-identical report / metric equality);
> - `0 <= net_notional <= gross_notional` invariant (per window and aggregate);
> - `cost_saved >= 0` invariant (per window and aggregate);
> - capacity clamp invariant (filled notional never exceeds `max_participation * liquidity`);
> - turnover in `[0, 2]`;
> - finite/nonzero windows, trades, return, Sharpe on the real seeds `1..5`;
> - CLI entry test (`main(["--seeds","1","2","--write", ...])` returns 0 and writes both artifacts);
> - explicitly assert the report is not `{"valid": True}`.
>
> ### Exit gate (ALL must be true before sealing)
> - `python3 -m pytest tests/test_cross_venue_netting.py tests/test_capacity_aware_tca.py tests/test_strategy_falsification.py tests/test_oos_walkforward.py tests/test_integrated_campaign.py -q` → **all pass**.
> - `python3 -m py_compile src/analytics/cross_venue_netting.py` → clean.
> - Real run `--seeds 1 2 3 4 5 --write` produced **>= 10 windows and > 0 trades per seed** and finite
>   net-of-cost metrics for every seed; cite the exact artifact paths in the sealed record below.
> - `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`.
> - No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper; no legacy-phase edits.
> - **Update this handoff in place:** mark EVAL-08 COMPLETE with verified numbers, then set the new active
>   task to `INIT-<UTC>-STRATEGY-EVAL-09-GAMMA-INVENTORY-TOXICITY`.
>
> ### Anti-vacuous gates (a report that trips any of these is a FAILED session, not a pass)
> - all windows zero / all trades zero / `oos_return == 0` and `oos_sharpe == 0`;
> - `net_notional_ratio` identically 1.0 across every window (netting never engages);
> - any negative `cost_saved` or negative `turnover`;
> - any `NaN`/`Infinity` in the JSON, or a report containing `{"valid": true}`.
>
> ### Reuse map (exact symbols; do not reimplement)
> - `src/campaign/integrated.py`: `DEFAULT_SYMBOLS`, `DEFAULT_SPOT`, `DETERMINISTIC_NOW`,
>   `IntegratedConfig`, `_generate_price_paths`, `_features_for_symbol`, `_load_options_chain`,
>   `_load_orderflow`, `_time_varying_signal_series`, `_stable_seed`.
> - `src/analytics/capacity_aware_tca.py`: `CapacityAwareSizer`, `VenueLiquidity`,
>   `_build_signal_series_capacity`, `_static_context_capacity`, `_run_capacity_aware_walkforward`,
>   `COST_GRID_BPS`, `INITIAL_CAPITAL`.
> - `src/analytics/strategy_evaluation.py`: `compute_metrics`.
> - `src/backtest/engine.py`: `WalkForwardBacktest`, `BacktestConfig`, `RiskConfig`,
>   `detect_regime_from_window`.
> - `src/telemetry/serialization.py`: `serialize_metrics_strict`, `assert_json_valid`.

---

## FOCUS CAMPAIGN (strictly sequential; heavy work is mandatory at each step)

| Order | Task | Status | Required output |
|---|---|---|---|
| EVAL-07 | Capacity/liquidity-aware TCA | **COMPLETE** | `src/analytics/capacity_aware_tca.py` + tests + CLI; artifact `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`; 71-test gate green. |
| EVAL-08 | **Cross-venue delta netting** | **ACTIVE** | `src/analytics/cross_venue_netting.py` + `tests/test_cross_venue_netting.py` + CLI + real-run artifact; see INITIAL TASK MESSAGE for the full spec and exit gate. |
| EVAL-09 | Gamma/inventory-aware hedge sizing + orderflow-toxicity gating | QUEUED | `src/analytics/gamma_inventory_hedge.py` + tests + CLI + real-run artifact; net-of-cost OOS with/without toxicity gate; reuse EVAL-08 netting. |
| EVAL-10 | Final net-of-cost GO/NO-GO certification | QUEUED | Re-run EVAL-06 falsification on the EVAL-09 portfolio; seal GO/NO-GO with multi-seed bootstrap/permutation; update this handoff. |

**Rule:** do not skip EVAL-08. Do not advance EVAL-09 until EVAL-08 is sealed with a real artifact. Do not
re-open EVAL-02/03/06/07 (sealed and test-locked). Do not implement or advance Phase 292+.

---

## VERIFIED STATE — ground truth (do not re-verify; build on it)

- **Environment:** Python 3.12.3; `pydantic, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, yaml, pytest` present. `pytest` works.
- **Baseline exit gate (re-run this session):** `tests/test_capacity_aware_tca.py tests/test_strategy_falsification.py
  tests/test_oos_walkforward.py tests/test_integrated_campaign.py tests/test_integrated_signal_series.py` → **74 passed in 67.40s**.
- **EVAL-02 COMPLETE:** `src/analytics/strategy_evaluation.py`, `tests/test_strategy_evaluation.py` (11 tests), `scripts/evaluate_strategy.py`, `tests/test_evaluate_strategy.py` (6 tests) green. Artifacts `research_state/STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}`.
- **EVAL-03 COMPLETE:** `src/analytics/regime_sizing.py` + `tests/test_regime_sizing.py` (7 tests). GO; 50 windows; 460 trades; regime Sharpe 0.042420205551953624 vs flat 0.026375107502127727; delta +0.016045098049825898; max-DD 0.004157360290141191. Artifact `research_state/REGIME_SIZING_2026-11-12T151421.312990Z.json`.
- **EVAL-06 COMPLETE (sealed NO-GO; do not re-run unless doing a seeds 1..10 sweep):** `src/analytics/strategy_falsification.py` + `tests/test_strategy_falsification.py`. pass_fraction 0.60 (3/5, need >=0.7); mean_net_sharpe 8.860771; mean_net_return 0.025482; cost grid net Sharpe 8.9946/8.8608/8.0745/7.3734 at 0/1/5/10 bps; mean_permutation_p 0.752; failing_conditions: seed 1 bootstrap_or_permutation, seed 4 bootstrap_or_permutation. Artifact `research_state/STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`.
- **EVAL-07 COMPLETE (sealed this session):** `src/analytics/capacity_aware_tca.py` + `tests/test_capacity_aware_tca.py` + CLI. Artifact `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. Seeds 1..5 all pass; mean_capacity_net_sharpe 8.250491; mean_capacity_net_return 0.267855; mean_baseline_net_sharpe 9.197960; mean_baseline_net_return 0.323307; capacity_vs_baseline_sharpe -0.947469; capacity_vs_baseline_return -0.055452; cost grid mean net Sharpe 9.1980/9.1571/8.9929/8.7863 at 0/1/5/10 bps (monotone decreasing); 294 capacity-limited + 294 budget-limited orders across seeds.
- **ROOT-CAUSE FIX #1 (DONE) — non-determinism:** `_load_orderflow` / `_load_options_chain` used salted `hash((symbol, venue))`. Replaced with `_stable_seed()` (SHA-256). Two separate processes produce byte-identical feature dicts.
- **ROOT-CAUSE FIX #2 (DONE) — vacuous all-zero signals:** `_step_feature_engineering` repeated one static snapshot (`[f] * n`), so every signal was 0 and OOS return/Sharpe were structurally 0.0. Replaced with `_time_varying_signal_series()` + `_rolling_realized_vol()`: causal trailing fast/slow momentum z-scores blended with the static options/orderflow snapshot through `CompositeSignalGenerator`.
- **Post-fix real run (seed 42, 500 points, purge 10 / embargo 5, 10 windows):** portfolio OOS return **0.010296791740144254**, Sharpe **0.1741937230265782**, stability 0.6405971890324178; per-symbol trades BTC 72 / ETH 59 / SOL 185; signal coverage BTC 134/0/366, ETH 112/0/388, SOL 312/0/188.
- **Per-symbol OOS return defect:** FIXED in EVAL-06 step 1 — `WalkForwardBacktest` chains per-window equity (`prod(1+r_w)-1`); aggregate return/Sharpe/max-DD derive from the chained curve in anchored/rolling and `PortfolioWalkForwardBacktest`. Test-locked by `tests/test_oos_walkforward.py`.
- **Regression tests added:** `tests/test_integrated_signal_series.py` (3 passed) locks `_stable_seed` stability, non-all-zero signals, and causality.
- **Real data loaders work:** `DataLoader().load_orderflow(...)` → 1000 trades / 20 liquidations / 8 funding; `load_options_chain(...)` → 30 quotes.
- **Reusable real code (do not rewrite):** `src/backtest/engine.py`, `src/backtest/options_hedging.py`, `src/features/*`, `src/signals/*`, `src/campaign/integrated.py`, `src/analytics/*`, `src/orderflow/`, `src/execution/*`, `src/risk/*`. Legacy Phase 15–19 and Phase 21 execution/risk/observability modules are reference only; do not extend them.
- **`scripts/run_backtest.py` is a vacuous smoke test** (single trade, Sharpe≈6.3 from 2 marks). Do not treat its numbers as strategy performance.

## BOTTLENECKS REMOVED (this session)

| Bottleneck | Resolution |
|---|---|
| **Stale task IDs in the 3 pointer stubs** (`HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` still named EVAL-06/15:19:24Z) | **CLEARED.** All three rewritten as pure "RETIRED — read `research_state/durable_handoff.md`" pointers with no competing task ID. Only this file is actionable. |
| Four competing handoffs / stale stubs | **CLEARED.** This file is the single source of truth. |
| `tests/test_campaign_resume.py::test_durable_handoff_is_source_of_truth` | **PASSING** with this file's `SINGLE DURABLE HANDOFF` / `INITIAL TASK MESSAGE` markers and the required Phase reference. |
| Cross-process non-determinism (salted `hash()`) | **FIXED** with `_stable_seed()` (SHA-256); verified across two processes. |
| All-zero signal series → 0 windows/trades/return | **FIXED** with time-varying causal momentum z-scores; real run now has 10 windows and nonzero return/Sharpe. |
| Per-symbol OOS return excluded open-position MTM | **FIXED in EVAL-06** via chained per-window OOS equity; test-locked. |
| Naive full `pytest` on 863 test files (clone treadmill) | **AVOID THE TRAP.** Run only the named EVAL test files in the exit gate; never `pytest tests/` wholesale. |
| `research_state/` ~5 GB / ~107k files can stall naive globbing | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit filenames/globs. |
| Phase 272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` clone treadmill | **CLOSED.** Do not implement/seal/advance Phase 292+. |
| EVAL-07 capacity-aware TCA not built | **SHIPPED.** Module + tests + CLI + artifact; 71-test gate green. |
| EVAL-08 not started | **ACTIVE.** Full spec above; no blocker. |

**Tree verified 2026-11-12T19:53:33Z (this session):** EVAL-07 shipped COMPLETE; `src/analytics/capacity_aware_tca.py` and `tests/test_capacity_aware_tca.py` present; artifacts `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}` present; EVAL-06 sealed NO-GO artifacts present `research_state/STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`. `src/analytics/cross_venue_netting.py` does **not** exist yet (EVAL-08 ACTIVE). Working tree is clean. No active blockers; EVAL-08 is the only open item.

## P0 SAFETY — CLEAR

- `.env` **ABSENT**. `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO network calls to exchanges, NO NEXT9 unblock.**

## SCOPE & HARD GUARDS (non-negotiable)

- **Allowed:** `src/`, `scripts/`, `tests/`, `research_state/` (explicit files only). Additive, deterministic, bounded, paper-only, guarded.
- **Forbidden:** live trading, `.env` creation, venue/config/credential mutation, NEXT9 unblock, any new `phaseNN_*_post_attribution_seal_orchestrator` wrapper, refactoring sealed legacy phases, and enumerating `research_state/` or running the full 863-file test suite.
- Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`.

## HANDOFF DISCIPLINE

- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- Work the queue strictly in order: EVAL-08 (cross-venue netting, ACTIVE) → EVAL-09 (gamma/inventory hedge + toxicity gating) → EVAL-10 (final net-of-cost GO/NO-GO).
- Each task must ship a real module, a numeric-invariant test file, a CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If context/time runs out: commit/push the partial new module and leave this file pointing at the exact next line to write. Never leave the tree clean with the task "pending."
- A final response containing only "verified env / will start next session" is a **failed session**.
- Final responses must not ask follow-up questions.