# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-12T16:40:19Z (UTC). EVAL-06 sealed NO-GO; EVAL-07 is the ACTIVE task below.
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are pointers/stubs — do not action them or create new handoff files.

---

## INITIAL TASK MESSAGE (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-12T16:40:19Z-STRATEGY-EVAL-07-CAPACITY-AWARE-TCA`
**STATUS:** ACTIVE. This is the single next task. Do not pick a different task.

> Execute EVAL-07 end-to-end this session: capacity/liquidity-aware TCA. EVAL-06 (net-of-cost
> falsification) is SEALED NO-GO (3/5 seeds pass; artifacts
> `research_state/STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`); its signal series and
> walk-forward engine are verified and must be REUSED, not rewritten.
>
> **Deliverable 1 — module `src/analytics/capacity_aware_tca.py` (build, do not stub):**
> - Participation-rate cost model: realized cost bps as a monotone-increasing function of
>   participation rate (order qty / available venue liquidity). Use a square-root or quadratic
>   impact law with a linear spread component; document the formula in the module docstring.
> - Per-venue capacity constraints: max participation (e.g. <= 20% of observed bar liquidity);
>   clamp/raise `InsufficientCapacity`-style errors deterministically, never silently fill more
>   than capacity.
> - Cost budget: a per-window USD/bps budget; the sizer must scale target notional down to fit
>   the budget and report realized cost bps + utilization.
> - Turnover accounting: per-window turnover (gross traded notional / NAV) and its cost drag.
> - Net-of-cost OOS: run the EVAL-06 signal series through this capacity-aware sizer inside the
>   walk-forward OOS and report net return/Sharpe/max-DD per seed and aggregate, vs the EVAL-06
>   flat-cost baseline. Reuse `src/analytics/strategy_evaluation.py` metrics helpers and the
>   walk-forward engine (`src/backtest/engine.py`); do not duplicate bootstrap/permutation logic.
> - CLI: `python3 src/analytics/capacity_aware_tca.py --seeds 1 2 3 4 5 --write` writing
>   `research_state/CAPACITY_AWARE_TCA_<UTC>.json` + `.md`, strict-serializable, never emits
>   `{"valid": True}`.
>
> **Deliverable 2 — tests `tests/test_capacity_aware_tca.py`:** determinism across two processes,
> cost monotone in participation rate, capacity clamp invariant (never exceeds cap), budget
> scaling invariant (spend <= budget), turnover in [0, 2], finite/nonzero metrics on real run
> seeds, CLI entry test. All must pass.
>
> **Exit gate (ALL must be true before sealing):**
> - `python3 -m pytest tests/test_capacity_aware_tca.py tests/test_strategy_falsification.py
>   tests/test_oos_walkforward.py tests/test_integrated_campaign.py -q` → all pass.
> - `python3 -m py_compile src/analytics/capacity_aware_tca.py` clean.
> - Real run `--seeds 1 2 3 4 5 --write` produced nonzero windows/trades and finite
>   net-of-cost metrics for every seed; artifact paths cited in this handoff.
> - `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; next9_unblocked=false.
> - No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper.
> - Update this handoff in place: mark EVAL-07 COMPLETE with verified numbers, then set the new
>   active task to `INIT-<UTC>-STRATEGY-EVAL-08-CROSS-VENUE-NETTING`.
>
> **EVAL-06 sealed record (do not re-run unless doing a seeds 1..10 sweep):**
> NO-GO | pass_fraction 0.60 (3/5, need >=0.7) | mean_net_sharpe 8.860771 | mean_net_return
> 0.025482 | cost grid net Sharpe 8.9946/8.8608/8.0745/7.3734 at 0/1/5/10 bps | mean_permutation_p
> 0.752 | failing_conditions: seed 1 bootstrap_or_permutation, seed 4 bootstrap_or_permutation.
> Engine fix (chained per-window OOS equity) and `src/analytics/strategy_falsification.py` are
> COMPLETE and test-locked.

**Focus campaign queue (strictly sequential; heavy work is mandatory at each step):**
- `EVAL-07` — **ACTIVE:** capacity/liquidity-aware TCA (`src/analytics/capacity_aware_tca.py`) with
  participation-rate cost model, cost budget, turnover, realized cost bps, net-of-cost OOS
  (see INITIAL TASK MESSAGE above for the full heavy-work spec and exit gate).
- `EVAL-08` — Cross-venue delta netting (`src/analytics/cross_venue_netting.py`): gross vs net
  notional, cost saved, net-of-cost OOS vs no-netting baseline, with its own test file and CLI.
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

**Tree verified 2026-11-12T16:40Z (this session):** working tree clean; `pytest
tests/test_strategy_falsification.py tests/test_oos_walkforward.py` → 31 passed;
`pytest tests/test_integrated_campaign.py tests/test_regime_sizing.py
tests/test_portfolio_scaling.py tests/test_portfolio_walkforward_correlation_adversarial.py
tests/test_walkforward_robustness_adversarial.py tests/test_integrated_signal_series.py` → 76
passed. No other session is blocked; EVAL-07 is the only open item.

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
- Work the queue strictly in order: EVAL-07 (capacity-aware TCA, ACTIVE) → EVAL-08 (cross-venue netting) → EVAL-09 (gamma/inventory hedge + toxicity gating). Each task must ship a real module, a numeric-invariant test file, a CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If context/time runs out: commit/push the partial new module and leave this file pointing at the exact next line to write. Never leave the tree clean with the task "pending."
- A final response containing only "verified env / will start next session" is a **failed session**.
- Final responses must not ask follow-up questions.