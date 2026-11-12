# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-12T20:12:00Z (UTC). **EVAL-08 (cross-venue delta netting) sealed COMPLETE this session.** EVAL-09 is the ACTIVE task below. Exit gate re-run green: **92 passed** (`test_cross_venue_netting.py` 21 + `test_capacity_aware_tca.py` 20 + `test_strategy_falsification.py` + `test_oos_walkforward.py` + `test_integrated_campaign.py`). `src/analytics/gamma_inventory_hedge.py` does not exist — EVAL-09 not started.
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are **retired pointer stubs** — do not action them and do not create new handoff files.

---

## INITIAL TASK MESSAGE (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-12T20:12:00Z-STRATEGY-EVAL-09-GAMMA-INVENTORY-TOXICITY`
**STATUS:** ACTIVE. This is the single next task. Do not pick a different task. Do not re-verify the environment. Build the module, run the real evaluation, and seal it.

> Execute **EVAL-09 gamma/inventory-aware hedge sizing + orderflow-toxicity gating** end-to-end this
> session. EVAL-08 (cross-venue delta netting) is shipped COMPLETE — artifact
> `research_state/CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`.
> Its venue-split, netting-cost, and walk-forward machinery is verified and must be **REUSED, not
> rewritten**.
>
> **Why this task, from the repo name:** the repo is a crypto **options + orderflow** strategy. After
> delta is netted across venues (EVAL-08), the remaining capital-efficiency and risk levers are
> **gamma/inventory** (how much of the book's convexity to hedge, and how inventory skews quoting) and
> **orderflow toxicity** (whether incoming flow is informed — toxic flow must widen spreads or stand
> down, benign flow should be absorbed). These are the last two layers before the final net-of-cost
> GO/NO-GO (EVAL-10). This is heavy, real work — not a wrapper, not a stub, not an env check.
>
> ### Deliverable 1 — `src/analytics/gamma_inventory_hedge.py` (build, do not stub)
> Create a real, deterministic, strict-serializable module with:
> - **Dataclasses:** `HedgeLeg(symbol, venue, instrument, signed_contracts, delta_usd, gamma_usd,
>   vega_usd, theta_usd, notional_usd)`; `InventorySnapshot(bar_index, timestamp, net_delta_usd,
>   net_gamma_usd, net_vega_usd, inventory_skew, target_delta_usd, hedge_notional_usd,
>   hedge_cost_usd, toxicity_score, toxic_gate_active, orders_quoted, orders_skipped, regime)`;
>   `SeedHedgeResult(seed, snapshots, mean_abs_delta_usd, mean_inventory_skew,
>   mean_hedge_cost_usd, mean_toxicity_score, toxic_gate_active_fraction,
>   oos_return_with_hedge, oos_sharpe_with_hedge, oos_max_drawdown_with_hedge,
>   oos_return_without_hedge, oos_sharpe_without_hedge, oos_max_drawdown_without_hedge,
>   num_hedges, num_bars, num_skipped_due_to_toxicity)`;
>   `GammaInventoryReport(report_id, generated_at, config, per_seed, aggregate, never_valid_true)`.
> - **Gamma/inventory hedge sizing:** for each symbol/bar, read the static greeks snapshot from
>   EVAL-07's `_static_context_capacity` (`greeks_summary.delta/gamma/vega/theta`) and the
>   EVAL-06 time-varying signal series. Compute net delta/gamma/vega inventory from the current
>   position; size a **delta hedge** to bring net delta toward a target (default 0, or a small band),
>   capped by EVAL-08's per-venue capacity and cost model (reuse `CapacityAwareSizer`,
>   `price_legs_with_capacity`, `_leg_liquidity`). `hedge_notional = min(abs(net_delta - target),
>   capacity_cap)`; `hedge_cost_usd = hedge_notional * realized_cost_bps / 1e4`. Deterministic,
>   no network, no venue API, no credentials.
> - **Orderflow toxicity gate:** compute a deterministic `toxicity_score` in `[0, 1]` from the
>   EVAL-06 `_load_orderflow` trade flow (e.g. signed-volume imbalance / VPIN-style bucketed
>   imbalance, causal trailing window only — no lookahead). When `toxicity_score >= threshold`
>   (default 0.7), `toxic_gate_active=True` and quoting is reduced/skipped (`orders_skipped`
>   increments); otherwise quote normally. Report `toxic_gate_active_fraction` per seed.
> - **Net-of-cost OOS:** run the EVAL-06/07/08 signal + netting series through the gamma/inventory
>   hedge and the toxicity gate inside the walk-forward OOS and report net return / Sharpe / max-DD
>   **per seed and aggregate, WITH hedge+gate vs WITHOUT**. Reuse
>   `src/analytics/strategy_evaluation.py::compute_metrics`,
>   `src/backtest/engine.py::WalkForwardBacktest`, and the EVAL-08 `_run_netting_walkforward` /
>   `_equity_from_returns` patterns. Do **not** duplicate bootstrap/permutation logic (EVAL-06 owns
>   it).
> - **CLI:** `python3 src/analytics/gamma_inventory_hedge.py --seeds 1 2 3 4 5 --write` writing
>   `research_state/GAMMA_INVENTORY_HEDGE_<UTC>.json` + `.md`. Strict-serializable via
>   `serialize_metrics_strict` / `assert_json_valid`; never emits `{"valid": True}`.
>
> ### Deliverable 2 — `tests/test_gamma_inventory_hedge.py` (numeric invariants; all must pass)
> - determinism across two separate processes (byte-identical report / metric equality);
> - `0 <= abs(net_delta_after_hedge) <= abs(net_delta_before_hedge) + tol` (hedge reduces |delta|);
> - `hedge_cost_usd >= 0` and `hedge_notional <= capacity_cap` (never exceeds venue capacity);
> - `0 <= toxicity_score <= 1` and `toxic_gate_active` is a strict deterministic function of the
>   score vs threshold;
> - finite/nonzero snapshots, hedges, return, Sharpe on the real seeds `1..5`;
> - CLI entry test (`main(["--seeds","1","2","--write", ...])` returns 0 and writes both artifacts);
> - explicitly assert the report is not `{"valid": True}`.
>
> ### Exit gate (ALL must be true before sealing)
> - `python3 -m pytest tests/test_gamma_inventory_hedge.py tests/test_cross_venue_netting.py tests/test_capacity_aware_tca.py tests/test_strategy_falsification.py tests/test_oos_walkforward.py tests/test_integrated_campaign.py -q` → **all pass**.
> - `python3 -m py_compile src/analytics/gamma_inventory_hedge.py` → clean.
> - Real run `--seeds 1 2 3 4 5 --write` produced **>= 10 windows and > 0 trades/hedges per seed**
>   and finite net-of-cost metrics for every seed; cite the exact artifact paths in the sealed
>   record below.
> - `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`.
> - No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper; no legacy-phase edits.
> - **Update this handoff in place:** mark EVAL-09 COMPLETE with verified numbers, then set the new
>   active task to `INIT-<UTC>-STRATEGY-EVAL-10-FINAL-GONOGO`.
>
> ### Anti-vacuous gates (a report that trips any of these is a FAILED session, not a pass)
> - all snapshots zero / all hedges zero / `oos_return == 0` and `oos_sharpe == 0`;
> - `toxic_gate_active_fraction` identically 0.0 across every seed (gate never engages);
> - `abs(net_delta_after_hedge)` never below `abs(net_delta_before_hedge)` (hedge never reduces
>   inventory);
> - any negative `hedge_cost_usd` or `NaN`/`Infinity` in the JSON, or a report containing
>   `{"valid": true}`.
>
> ### Reuse map (exact symbols; do not reimplement)
> - `src/campaign/integrated.py`: `DEFAULT_SYMBOLS`, `DEFAULT_SPOT`, `DETERMINISTIC_NOW`,
>   `IntegratedConfig`, `_generate_price_paths`, `_features_for_symbol`, `_load_options_chain`,
>   `_load_orderflow`, `_time_varying_signal_series`, `_stable_seed`.
> - `src/analytics/capacity_aware_tca.py`: `CapacityAwareSizer`, `VenueLiquidity`,
>   `_build_signal_series_capacity`, `_static_context_capacity`, `COST_GRID_BPS`, `INITIAL_CAPITAL`.
> - `src/analytics/cross_venue_netting.py`: `VENUES`, `venue_mix`, `split_venue_legs`,
>   `price_legs_with_capacity`, `_leg_liquidity`, `net_notional_of`, `_run_netting_walkforward`,
>   `_equity_from_returns`, `_window_price_return`, `_realized_vol`, `INITIAL_CAPITAL`.
> - `src/analytics/strategy_evaluation.py`: `compute_metrics`.
> - `src/backtest/engine.py`: `WalkForwardBacktest`, `BacktestConfig`, `RiskConfig`,
>   `detect_regime_from_window`, `BacktestEngine`.
> - `src/telemetry/serialization.py`: `serialize_metrics_strict`, `assert_json_valid`.

---

## FOCUS CAMPAIGN (strictly sequential; heavy work is mandatory at each step)

| Order | Task | Status | Required output |
|---|---|---|---|
| EVAL-07 | Capacity/liquidity-aware TCA | **COMPLETE** | `src/analytics/capacity_aware_tca.py` + tests + CLI; artifact `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`; gate green. |
| EVAL-08 | **Cross-venue delta netting** | **COMPLETE** | `src/analytics/cross_venue_netting.py` (1091 lines) + `tests/test_cross_venue_netting.py` (21 tests) + CLI; artifact `research_state/CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`; 92-test gate green. |
| EVAL-09 | **Gamma/inventory-aware hedge sizing + orderflow-toxicity gating** | **ACTIVE** | `src/analytics/gamma_inventory_hedge.py` + tests + CLI + real-run artifact; net-of-cost OOS with/without toxicity gate; reuse EVAL-08 netting. See INITIAL TASK MESSAGE for full spec and exit gate. |
| EVAL-10 | Final net-of-cost GO/NO-GO certification | QUEUED | Re-run EVAL-06 falsification on the EVAL-09 portfolio; seal GO/NO-GO with multi-seed bootstrap/permutation; update this handoff. |

**Rule:** do not skip EVAL-09. Do not advance EVAL-10 until EVAL-09 is sealed with a real artifact. Do
not re-open EVAL-02/03/06/07/08 (sealed and test-locked). Do not implement or advance Phase 292+.

---

## VERIFIED STATE — ground truth (do not re-verify; build on it)

- **Environment:** Python 3.12.3. **Dependencies were missing at session start** (no `numpy`,
  `pandas`, `scipy`, `pydantic`, `pytest`) — **FIXED** this session via
  `python3 -m pip install --break-system-packages -r requirements.txt` (installs numpy 2.5.4,
  pandas 3.1.1, scipy 1.18.1, pydantic 2.14.3, pytest). All modules import; `pytest` works. If a
  fresh container reproduces the missing deps, re-run that exact pip command first (network is
  available).
- **Baseline exit gate (re-run this session):** `tests/test_capacity_aware_tca.py tests/test_strategy_falsification.py
  tests/test_oos_walkforward.py tests/test_integrated_campaign.py tests/test_integrated_signal_series.py
  tests/test_campaign_resume.py` → **86 passed in 67.59s** (pre-EVAL-08 baseline).
- **EVAL-08 exit gate (this session):** `tests/test_cross_venue_netting.py tests/test_capacity_aware_tca.py
  tests/test_strategy_falsification.py tests/test_oos_walkforward.py tests/test_integrated_campaign.py`
  → **92 passed in 105.50s**; `python3 -m py_compile src/analytics/cross_venue_netting.py` clean.
- **EVAL-02 COMPLETE:** `src/analytics/strategy_evaluation.py`, `tests/test_strategy_evaluation.py` (11 tests), `scripts/evaluate_strategy.py`, `tests/test_evaluate_strategy.py` (6 tests) green. Artifacts `research_state/STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}`.
- **EVAL-03 COMPLETE:** `src/analytics/regime_sizing.py` + `tests/test_regime_sizing.py` (7 tests). GO; 50 windows; 460 trades; regime Sharpe 0.042420205551953624 vs flat 0.026375107502127727; delta +0.016045098049825898; max-DD 0.004157360290141191. Artifact `research_state/REGIME_SIZING_2026-11-12T151421.312990Z.json`.
- **EVAL-06 COMPLETE (sealed NO-GO; do not re-run unless doing a seeds 1..10 sweep):** `src/analytics/strategy_falsification.py` + `tests/test_strategy_falsification.py`. pass_fraction 0.60 (3/5, need >=0.7); mean_net_sharpe 8.860771; mean_net_return 0.025482; cost grid net Sharpe 8.9946/8.8608/8.0745/7.3734 at 0/1/5/10 bps; mean_permutation_p 0.752; failing_conditions: seed 1 bootstrap_or_permutation, seed 4 bootstrap_or_permutation. Artifact `research_state/STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`.
- **EVAL-07 COMPLETE:** `src/analytics/capacity_aware_tca.py` + `tests/test_capacity_aware_tca.py` + CLI. Artifact `research_state/CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. Seeds 1..5 all pass; mean_capacity_net_sharpe 8.250491; mean_capacity_net_return 0.267855; mean_baseline_net_sharpe 9.197960; mean_baseline_net_return 0.323307; capacity_vs_baseline_sharpe -0.947469; capacity_vs_baseline_return -0.055452; cost grid mean net Sharpe 9.1980/9.1571/8.9929/8.7863 at 0/1/5/10 bps (monotone decreasing); 294 capacity-limited + 294 budget-limited orders across seeds.
- **EVAL-08 COMPLETE (sealed this session):** `src/analytics/cross_venue_netting.py` + `tests/test_cross_venue_netting.py` + CLI. Artifact `research_state/CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`. Seeds 1..5, 10 windows/seed, 612 total trades, 1839 capacity-limited orders. Aggregate: mean_gross_notional 2,534,948.05; mean_net_notional 904,597.70; **mean_net_notional_ratio 0.355666** (netting genuinely engages; NOT identically 1.0); mean_cost_saved_usd 163.04; mean_cost_saved_bps 1.6304; **mean_oos_sharpe_with_netting 8.006530 vs without 5.796608 (delta +2.209922)**; mean_oos_return_with_netting 0.088702 vs without 0.217640; mean_oos_max_drawdown_with_netting 0.014245 vs without 0.030161 (netting roughly halves max-DD). Per-seed netting ratio: 0.3288 / 0.3897 / 0.3043 / 0.3375 / 0.4180 (all distinct, all < 1).
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
| **Missing Python dependencies** (no `numpy`/`pandas`/`scipy`/`pydantic`/`pytest` — every session would have failed at import) | **CLEARED.** `pip install --break-system-packages -r requirements.txt`; all deps import, `pytest` runs. |
| Stale task IDs in the 3 pointer stubs | **CLEARED earlier.** All three are pure "RETIRED — read `research_state/durable_handoff.md`" pointers with no competing task ID. |
| Four competing handoffs / stale stubs | **CLEARED.** This file is the single source of truth. |
| `tests/test_campaign_resume.py::test_durable_handoff_is_source_of_truth` | **PASSING** with this file's `SINGLE DURABLE HANDOFF` / `INITIAL TASK MESSAGE` markers and the required Phase reference. |
| Cross-process non-determinism (salted `hash()`) | **FIXED** with `_stable_seed()` (SHA-256); verified across two processes. |
| All-zero signal series → 0 windows/trades/return | **FIXED** with time-varying causal momentum z-scores; real run now has 10 windows and nonzero return/Sharpe. |
| Per-symbol OOS return excluded open-position MTM | **FIXED in EVAL-06** via chained per-window OOS equity; test-locked. |
| Naive full `pytest` on 863 test files (clone treadmill) | **AVOID THE TRAP.** Run only the named EVAL test files in the exit gate; never `pytest tests/` wholesale. |
| `research_state/` ~5 GB / ~107k files can stall naive globbing | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit filenames/globs. |
| Phase 272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` clone treadmill | **CLOSED.** Do not implement/seal/advance Phase 292+. |
| EVAL-08 netting not built | **SHIPPED.** Module + tests + CLI + artifact; 92-test gate green. |
| EVAL-09 gamma/inventory hedge not built | **ACTIVE.** Full spec above; no blocker. |

**Tree verified 2026-11-12T20:12:00Z (this session):** EVAL-08 shipped COMPLETE; `src/analytics/cross_venue_netting.py` and `tests/test_cross_venue_netting.py` present; canonical artifact `research_state/CROSS_VENUE_NETTING_20261112T201000Z.{json,md}` present; EVAL-06/07 sealed artifacts present. `src/analytics/gamma_inventory_hedge.py` does **not** exist yet (EVAL-09 ACTIVE). No active blockers; EVAL-09 is the only open item.

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
- Work the queue strictly in order: EVAL-09 (gamma/inventory hedge + toxicity gating, ACTIVE) → EVAL-10 (final net-of-cost GO/NO-GO).
- Each task must ship a real module, a numeric-invariant test file, a CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If context/time runs out: commit/push the partial new module and leave this file pointing at the exact next line to write. Never leave the tree clean with the task "pending."
- A final response containing only "verified env / will start next session" is a **failed session**.
- Final responses must not ask follow-up questions.