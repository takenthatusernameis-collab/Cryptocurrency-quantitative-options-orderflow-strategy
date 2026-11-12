# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-12T15:19:24Z (UTC).
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are pointers/stubs — do not action them or create new handoff files.

---

## INITIAL TASK MESSAGE (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-12T15:19:24Z-STRATEGY-EVAL-06-NET-OF-COST-FALSIFICATION`
**STATUS:** ACTIVE — start immediately, write code this turn.

> You are continuing the cryptocurrency quantitative OPTIONS + ORDERFLOW strategy repo.
> Read this file first, then execute **EVAL-06** end-to-end. No stubs, no placeholders,
> no partial completion, no follow-up questions, no environment re-verification.
> Do NOT return to the archived Phase 272–291 `*_post_attribution_seal_orchestrator`
> clone treadmill. Do NOT accept 0 windows / 0 trades / 0 return as a pass.
>
> **EVAL-06 — Net-of-cost OOS falsification + performance certification**
>
> 1. **Fix the aggregate OOS return metric.** `WalkForwardBacktest` concatenates each
>    window's equity curve, but every window restarts at `initial_capital`; the aggregate
>    `overall_out_of_sample_return` is then taken from the **last window's terminal equity**,
>    which can be exactly `initial_capital` even when trades occurred (observed: BTC/ETH
>    report 0.0 return with 72/59 trades and nonzero Sharpe). Fix it in
>    `src/backtest/engine.py` so the aggregate OOS return compounds per-window returns
>    (e.g. `prod(1 + r_w) - 1`) or chains window curves to the prior terminal equity.
>    Add a numeric-invariant test proving nonzero trades cannot yield a 0.0 aggregate
>    return unless every window truly had 0.0 return. This is the highest-priority blocker:
>    all downstream evaluation is meaningless while the headline return is structurally 0.
>
> 2. **New module `src/analytics/strategy_falsification.py`** (real implementation, no `pass`/
>    `NotImplementedError`/`TODO`, finite-guarded, strict-serializable via
>    `serialize_metrics_strict` / `assert_json_valid`):
>    - Run the integrated campaign's walk-forward OOS across **seeds 1..10** (minimum 1..5)
>      for BTC/ETH/SOL using the time-varying signal series now produced by
>      `src/campaign/integrated.py`.
>    - Report **gross and net-of-cost** return/Sharpe/max-DD. Costs must include
>      `fee_rate`, `slippage_bps`, and the regime-dependent cost profile.
>    - Cost sensitivity grid: transaction cost = 0, 1, 5, 10 bps; report net Sharpe at each.
>    - Statistical falsification: stationary/iid bootstrap 95% CI for mean net return and
>      Sharpe; **deflated Sharpe ratio**; **permutation test** (>=1000 shuffles of the
>      signal series) with p-value; minimum track-record length.
>    - Regime-conditioned performance using the campaign's detected regimes
>      (trend / range / high_vol_chop / thin), not a single pooled number.
>    - Pre-registered **GO / NO-GO** gate: GO only if (a) net Sharpe > 0, (b) bootstrap lower
>      bound > 0 or permutation p < 0.05, (c) net return > 0, and (d) this holds for >= 7/10
>      seeds. Otherwise NO-GO with the exact failing condition. Never emit `{"valid": True}`.
>
> 3. **New `tests/test_strategy_falsification.py`** asserting numeric invariants:
>    bootstrap CI contains the point estimate; p-value in [0, 1]; deflated Sharpe finite;
>    net return = gross − cost within tolerance; cost increases monotonically with bps;
>    determinism across two runs; `num_windows > 0`, `oos_trade_count > 0`, nonzero OOS
>    return for every symbol/seed.
>
> 4. **Real run:** `PYTHONPATH=. python3 src/analytics/strategy_falsification.py --seeds 1 2 3 4 5 --write`.
>    Paste the actual GO/NO-GO verdict, per-seed net Sharpe/return, bootstrap CI, permutation
>    p-value, deflated Sharpe, and the advancement delta vs the flat-cost/no-netting baseline.
>    Write `research_state/STRATEGY_FALSIFICATION_<UTC>.json` and `.md` (explicit filenames;
>    never enumerate `research_state/`).
>
> 5. **Exit gate (hard stop; do not end the turn until ALL true):**
>    - `PYTHONPATH=. python3 -m pytest -q tests/test_strategy_falsification.py` passes — paste the pass line.
>    - `python3 -m py_compile src/analytics/strategy_falsification.py` clean.
>    - Real run cites nonzero windows/trades/return and finite metrics for every seed.
>    - `.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`.
>    - No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper.
>    - This handoff is updated in place with verified numbers and the next task
>      `INIT-<UTC>-STRATEGY-EVAL-07-...`.

**Follow-on queue (only after EVAL-06 is sealed):**
- `EVAL-07` — Capacity/liquidity-aware TCA (`src/analytics/capacity_aware_tca.py`) with
  participation-rate cost model, cost budget, turnover, realized cost bps, net-of-cost OOS.
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