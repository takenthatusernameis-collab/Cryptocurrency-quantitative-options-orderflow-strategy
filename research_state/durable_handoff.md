# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-12T16:36:00Z (UTC). EVAL-06 sealed NO-GO; ready for EVAL-07.
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are pointers/stubs — do not action them or create new handoff files.

---

## INITIAL TASK MESSAGE (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-12T15:19:24Z-STRATEGY-EVAL-06-NET-OF-COST-FALSIFICATION`
**STATUS:** COMPLETE — sealed 2026-11-12T16:35:37Z. Verdict: **NO-GO** (3/5 seeds pass; need >= 0.7).

> EVAL-06 executed end-to-end. Do not re-run unless context/time allow a seeds-1..10 sweep.
> **Engine fix (COMPLETE):** `WalkForwardBacktest` aggregate OOS now chains per-window equity
> curves to prior terminal equity (`prod(1+r_w)-1`) instead of last-window terminal equity.
> Fixed in `src/backtest/engine.py` for both anchored + rolling `WalkForwardBacktest.run_walk_forward`
> branches and `PortfolioWalkForwardBacktest.run_portfolio_walk_forward`. `window_oos_curves`
> collected per window; `results.oos_equity_curve = chained`; return/sharpe/maxdd derived from
> chained curve. Smoke-tested: aggregate return matches compounded per-window returns exactly.
> Verified with `tests/test_oos_walkforward.py` (no zero-return-with-trades regression).
>
> **Module (COMPLETE):** `src/analytics/strategy_falsification.py` — cost grid bps (0,1,5,10),
> fee_rate + slippage_bps + regime-dependent cost multipliers, block-bootstrap 95% CI
> (clamped lo<=point<=hi), deflated Sharpe (scipy kurtosis fisher=False), permutation test
> (>=1000 shuffles default), regime-conditioned performance, regime-dependent cost profile.
> GO iff >=0.7 seeds pass (net sharpe>0, bootstrap lo>0 or perm p<0.05, net return>0,
> track record>=5 windows). Never emits `{"valid": True}`.
> CLI `--seeds ... --write` writes `research_state/STRATEGY_FALSIFICATION_<UTC>.json` + `.md`.
>
> **Tests (COMPLETE):** `tests/test_strategy_falsification.py` — 6 tests: determinism,
> per-seed invariants, cost-grid levels/monotonicity, regime performance, engine nonzero-trades
> invariant, CLI entry. All pass.
>
> **Real run result (VERIFIED):** `PYTHONPATH=. python3 src/analytics/strategy_falsification.py
> --seeds 1 2 3 4 5 --write` (2026-11-12T16:35:37Z):
>   verdict NO-GO | pass_fraction 0.60 (3/5) | need >=0.7
>   mean_net_sharpe 8.860771301305718 | mean_net_return 0.025482060068668044
>   mean_gross_sharpe 8.99456039326873 | mean_gross_return 0.025916152477790933
>   sharpe_advancement_vs_gross -0.13378909196301159
>   return_advancement_vs_gross -0.00043409240912288885
>   mean_bootstrap_lower_bound 0.0005288765105698277
>   mean_permutation_p_value 0.752 | mean_deflated_sharpe 0.0
>   failing_conditions: seed 1 bootstrap_or_permutation; seed 4 bootstrap_or_permutation
>   cost grid net Sharpe: bps0 8.9946 | bps1 8.8608 | bps5 8.0745 | bps10 7.3734
>   cost grid net return: bps0 0.025916 | bps1 0.025482 | bps5 0.023146 | bps10 0.020983
>   Artifacts: `research_state/STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`
>   Gate checks: net_sharpe_positive pass | net_return_positive pass | bootstrap_or_permutation
>    (aggregate) pass | seed_majority FAIL (0.60 < 0.70)
>
> **Exit gate (ALL TRUE):**
> - `pytest tests/test_strategy_falsification.py` → 6 passed
> - `pytest tests/test_oos_walkforward.py tests/test_integrated_campaign.py
>   tests/test_regime_sizing.py tests/test_portfolio_scaling.py
>   tests/test_portfolio_walkforward_correlation_adversarial.py
>   tests/test_walkforward_robustness_adversarial.py tests/test_integrated_signal_series.py` → 107 passed (55.22s)
> - `pytest tests/test_pipeline_determinism.py tests/test_pipeline_integration.py
>   tests/test_pipeline_serialization_end_to_end.py tests/test_nonfinite_result_serialization.py
>   tests/test_campaign_resume.py` → 25 passed (1.30s)
> - `python3 -m py_compile src/analytics/strategy_falsification.py` clean.
> - Real run: nonzero windows (10)/trades/return and finite metrics for every seed.
> - `.env` absent; `.env.example:15` LIVE_TRADING_ENABLED=false; next9_unblocked=false.
> - No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper.
> - This handoff updated in place with verified numbers and next task below.

**Follow-on queue (only after EVAL-06 is sealed):**
- `EVAL-07` — Capacity/liquidity-aware TCA (`src/analytics/capacity_aware_tca.py`) with
  participation-rate cost model, cost budget, turnover, realized cost bps, net-of-cost OOS.
  **Next task:** `INIT-2026-11-12T16:36:00Z-STRATEGY-EVAL-07-CAPACITY-AWARE-TCA`
  (capacity-aware TCA / cross-venue netting per EVAL-07 outline).
- `EVAL-08` — Cross-venue delta netting (`src/analytics/cross_venue_netting.py`): gross vs net
  notional, cost saved, net-of-cost OOS vs no-netting baseline.
- `EVAL-09` — Gamma/inventory-aware hedge sizing and orderflow-toxicity gating.

These were previously EVAL-04/05 but are **demoted**: TCA/netting on a vacuous signal is
meaningless, so EVAL-06 (real signal + net-of-cost falsification) must come first.

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
  - **Known remaining defect:** per-symbol `overall_out_of_sample_return` is still 0.0 for BTC/ETH (72/59 trades, nonzero Sharpe) because the aggregate is taken from the last window's terminal equity, and each window restarts at `initial_capital` (BTC's last three equity points are exactly 100000.0; window returns include exact 0.0 values). EVAL-06 step 1 fixes this.
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
| Per-symbol OOS return excludes open-position MTM | **DIAGNOSED; fix assigned to EVAL-06 step 1.** |
| `research_state/` ~5 GB / ~75k files can stall naive globbing | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit filenames/globs. |
| Phase 272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` clone treadmill | **CLOSED.** Do not implement/seal/advance Phase 292+. |

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
- After EVAL-06 is sealed (tests green + nonzero numbers cited), replace the active task with `INIT-<UTC>-STRATEGY-EVAL-07-...` (capacity-aware TCA), then EVAL-08 (cross-venue netting), then EVAL-09 (gamma/inventory-aware hedge sizing + toxicity gating).
- If context/time runs out: commit/push the partial new module and leave this file pointing at the exact next line to write. Never leave the tree clean with the task "pending."
- A final response containing only "verified env / will start next session" is a **failed session**.
- Final responses must not ask follow-up questions.