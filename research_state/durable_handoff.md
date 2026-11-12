# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-12T23:07:17Z (UTC). Re-verified this session against the tree (not copied from the prior handoff): `tests/test_eval10_final_gonogo.py` and `src/analytics/eval10_final_gonogo.py` **absent**; no `--eval10` flag in `src/analytics/strategy_falsification.py`; `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_*` **absent**; `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; root handoffs remain retired pointers. **Two real blockers were found and fixed this session — see BOTTLENECKS REMOVED.**
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are **retired pointer stubs** — do not action them and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope), not task sources.

---

## INITIAL TASK MESSAGE — 2026-11-12T23:07:17Z (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-12T23:07:17Z-STRATEGY-EVAL-10-FINAL-GONOGO`
**STATUS:** ACTIVE. This is the single next task. Do not pick a different task. Do not re-verify the environment (deps are installed; `.env` absent; safety flags set). Build the EVAL-10 driver, run the real multi-seed evaluation, seal it, then continue to EVAL-11 in the same session if time allows.

> **EVAL-09 is DONE and sealed (do not re-open EVAL-02/03/06/07/08/09).** `src/analytics/gamma_inventory_hedge.py` (1061 lines) + `tests/test_gamma_inventory_hedge.py` (16 tests) + CLI shipped; canonical artifact `research_state/GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}` (7.2 MB JSON). **Re-verified this session:** all 30 seed×symbol×side series have `len=10`, `distinct>=4`, `nonzero>=3`; aggregate `mean_oos_return_with_hedge=-0.5580107668605527`, `mean_oos_return_without_hedge=0.2590709968068878`, `mean_oos_sharpe_with_hedge=-22.765929562035716`, `mean_oos_sharpe_without_hedge=5.586740988848094`, `total_cost_usd=1429.6848986289629`, `mean_toxicity_score=0.713277330797748`, `toxic_gate_active_fraction=0.3333333333333333`. Gate green (34 passed / 61.5s on `test_strategy_falsification.py test_gamma_inventory_hedge.py test_campaign_resume.py`).
>
> **EVAL-10 = final net-of-cost GO/NO-GO certification on the EVAL-09 with-hedge portfolio.** Multi-seed block bootstrap + paired permutation on the EVAL-09 per-window OOS returns, with a cost grid at 0/1/5/10 bps, sealed with an honest GO/NO-GO verdict. **A NO-GO verdict is the expected and valid outcome — do NOT tune data to force GO.** **Pre-computed with the verified formulas below (do not re-derive): `pass_fraction = 0/5 = 0.0 → NO-GO`.** Per-seed, every seed fails because BTC and SOL fail in all 5 seeds; only ETH passes and only in seeds 1/3/5. If your implementation yields GO, your conditions or aggregation are wrong, not the data.
>
> **Aggregation warning (this exact mistake was made once already):** `pass_fraction` is **seed-level**, `seeds_passing / num_seeds`, where a seed passes only if **all** of its symbols pass — that is **0/5 = 0.0**. Do **not** report a per-series (seed×symbol) pass fraction such as `3/15 = 0.2` or `4/15 = 0.2667` and call it `pass_fraction`; those are diagnostics, not the verdict. `GO_SEED_FRACTION = 0.70`, so with 5 seeds at least 4 seeds must fully pass. Per-series with-hedge net return @1 bp (for reference): seed1 BTC −0.9209 / ETH +0.3638 / SOL −0.9992; seed2 −0.9500 / −0.2064 / −0.9986; seed3 −0.9716 / +0.4065 / −0.9888; seed4 −0.8017 / +0.2393 / −0.9969; seed5 −0.9603 / +0.4136 / −0.9991. Bootstrap CI lower bounds on ETH: +0.0032 / −0.0377 / +0.0090 / −0.0043 / +0.0176 (seeds 1–5), so a `bootstrap_lower_positive` condition is met by ETH only in seeds 1/3/5.

### Exact reuse points (verified on disk 2026-11-12T23:0x Z — do not re-implement)
- EVAL-09 engine: `src/analytics/gamma_inventory_hedge.py::evaluate_gamma_inventory_hedge(seeds=[1,2,3,4,5])`. Runtime **18.5 s for 5 seeds** (3.8 s/seed) — cheap; run it in-process rather than parsing the 7 MB artifact. Per-window series: `report["per_seed"][i]["symbols"][<sym>]["with_hedge"]["window_returns"]` (plain list of 10 floats) and the richer `["windows"][*]` list with `window_return`, `window_traded_notional`, `window_nav_start`, `window_cost_usd`, `window_hedges`, `window_trades`.
- Bootstrap: `src/analytics/strategy_evaluation.py::block_bootstrap_ci(values, statistic, *, n_bootstrap=2000, block_size=20, confidence=0.95, seed=0) -> (point, lo, hi)`. Use `block_size=min(3, len(values))` as EVAL-06 does. **It is a CI, not a p-value — see the permutation primitive below.**
- **Permutation: `src/analytics/strategy_evaluation.py::permutation_test(sample_a, sample_b, *, statistic, n_permutations=1000, paired=True, alternative="two-sided", seed=0)` — ADDED THIS SESSION.** Returns `observed_difference, null_mean, p_value, n_permutations, paired, alternative, significant_at_05, statistic_a, statistic_b`. p-value uses `(1+extreme)/(1+n_permutations)`, so it is in `(0,1]` and never 0. `paired=True` swaps labels within matched pairs (use for with-hedge vs without-hedge); `paired=False` pools+reshuffles. **The prior handoff wrongly told you to get permutation p-values from `block_bootstrap_ci`/`compare_to_baseline`; those do not do permutation. Use `permutation_test`.**
- Metrics: `src/analytics/strategy_evaluation.py::compute_metrics(equity_curve, *, periods_per_year=252, risk_free=0.0, trades=None)`. **It takes an EQUITY CURVE, not a return list** — build `eq=[100000.0]`, append `eq[-1]*(1+r)`, then call it (otherwise `total_return` is meaningless and `n_periods` is off by one).
- Cost grid: `COST_GRID_BPS = (0, 1, 5, 10)` in `src/analytics/strategy_falsification.py:65`. **EVAL-09 `window_returns` are already net of the 1 bp hedge cost** (verified: chaining raw `window_return` reproduces the reported `oos_return` exactly). So the grid must be applied **incrementally**, not by re-costing from zero:
  `r_b = window_return - (window_traded_notional * (b - 1) / 1e4) / window_nav_start`, then chain `prod(1+r_b) - 1`.
  Verified aggregate mean net return: **0 bps −0.557641 / 1 bps −0.558011 / 5 bps −0.559488 / 10 bps −0.561329** (monotone nonincreasing, as required). Mean net Sharpe: −22.759877 / −22.765930 / −22.790230 / −22.820814.
- Serialization: `serialize_metrics_strict` + `assert_json_valid` (`src/telemetry/serialization.py`). Never emit a bare `{"valid": True}`.

### Deliverable 1 — EVAL-10 driver / CLI (real computation, deterministic, no network)
Add `src/analytics/eval10_final_gonogo.py` (thin, imports the helpers above) **or** a `--eval10` flag in `src/analytics/strategy_falsification.py`. Either way:
- Strategy series = EVAL-09 with-hedge per-window returns, aggregated per seed×symbol into a chained net return and a Sharpe; baselines = EVAL-09 **without-hedge** portfolio and the EVAL-06 flat-cost baseline (`STRATEGY_FALSIFICATION_20261112T163240Z.json` if present, else re-run `evaluate_strategy_falsification(seeds=[1,2,3,4,5])`).
- Multi-seed block-bootstrap CI (seed-fixed, deterministic) for mean net return and mean net Sharpe over the 15 seed×symbol series.
- Paired permutation p-value for with-hedge vs without-hedge (`paired=True`, `statistic=np.mean`, `n_permutations>=1000`).
- Cost-grid net Sharpe / net return at 0/1/5/10 bps via the incremental formula above.
- Per-seed `failing_conditions` (list every failing symbol/condition, e.g. `"BTC: net_sharpe_positive"`); `pass_fraction = seeds_passing / num_seeds` in [0,1] — **seed-level only**, see the aggregation warning above; `verdict = "GO" if pass_fraction >= 0.70 else "NO-GO"` (strict deterministic function; `GO_SEED_FRACTION=0.70` at `strategy_falsification.py:67`). Also emit `series_pass_fraction` as a separate diagnostic field (expected `0.2`), never as `pass_fraction`.
- CLI: `python3 src/analytics/eval10_final_gonogo.py --seeds 1 2 3 4 5 --write` writing `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_<UTC>.{json,md}`.

### Deliverable 2 — `tests/test_eval10_final_gonogo.py` (numeric invariants; all must pass)
- determinism across two separate processes (byte-identical report);
- `pass_fraction` in [0,1]; `mean_net_sharpe` / `mean_net_return` finite;
- cost-grid net Sharpe monotone-nonincreasing in bps (use the verified numbers above as the expectation);
- verdict is exactly `"GO" if pass_fraction >= 0.70 else "NO-GO"`;
- bootstrap CI finite with `lo <= point <= hi`; permutation p in `(0, 1]`;
- CLI entry test returns 0 and writes both artifacts;
- explicitly assert the report is not `{"valid": True}`.

### Exit gate (ALL must be true before sealing)
- `python3 -m pytest tests/test_eval10_final_gonogo.py tests/test_strategy_falsification.py tests/test_gamma_inventory_hedge.py tests/test_cross_venue_netting.py tests/test_capacity_aware_tca.py tests/test_oos_walkforward.py tests/test_integrated_campaign.py tests/test_strategy_evaluation.py tests/test_data_loader_and_validation.py -q` → **all pass**. Verified this session: that list minus the (not-yet-written) EVAL-10 file is **142 passed / 144.32 s**. `test_eval10_final_gonogo.py` is the only missing file and is yours to create.
- `python3 -m py_compile` clean on any new/edited module.
- Real run `--seeds 1 2 3 4 5 --write` produced finite GO/NO-GO metrics for every seed; cite exact artifact paths in the sealed record.
- `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`.
- No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper; no legacy-phase edits.
- **Update this handoff in place:** mark EVAL-10 COMPLETE with verified GO/NO-GO verdict and numbers, then advance the campaign to EVAL-11.

### Anti-vacuous gates (a report that trips any is a FAILED session)
- report not `{"valid": True}`; no NaN/Infinity;
- verdict deterministic and not identically GO/NO-GO across seeds unless the data genuinely warrants it;
- bootstrap CI lo/hi finite and straddle the point estimate;
- **degeneracy guard:** assert each seed×symbol series has `len >= 2` and `>= 2 distinct nonzero values`; with the EVAL-09 default config all 30 series have `len=10, distinct>=4, nonzero>=3`, so this passes — keep it as a hard assertion and **fail loudly** rather than emit a vacuous CI. Do not paper over zeros.
- **aggregation guard:** assert `0.0 <= pass_fraction <= 1.0` and that `pass_fraction == seeds_passing / num_seeds` computed over **seeds**; assert the report carries a distinct `series_pass_fraction` field. A report whose `pass_fraction` equals a seed×symbol ratio is **FAILED** (this is the aggregation mistake called out above).

---

## FOCUS CAMPAIGN (strictly sequential; heavy work is mandatory at every step — do not stop after EVAL-10)

| Order | Task | Status | Required output |
|---|---|---|---|
| EVAL-07 | Capacity/liquidity-aware TCA | **COMPLETE** | `src/analytics/capacity_aware_tca.py` + tests + CLI; `CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. |
| EVAL-08 | Cross-venue delta netting | **COMPLETE** | `src/analytics/cross_venue_netting.py` + `tests/test_cross_venue_netting.py` (21) + CLI; `CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`. |
| EVAL-09 | Gamma/inventory hedge + toxicity gating | **COMPLETE** | `src/analytics/gamma_inventory_hedge.py` + tests (16) + CLI; canonical `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`. |
| EVAL-10 | **Final net-of-cost GO/NO-GO certification** | **ACTIVE** | Driver on EVAL-09 with-hedge per-window returns; multi-seed bootstrap + paired permutation + 0/1/5/10 bps incremental cost grid; `tests/test_eval10_final_gonogo.py`; artifact `STRATEGY_EVAL_10_FINAL_GONOGO_<UTC>.{json,md}`. Full spec + exit gate above. |
| EVAL-11 | **Hedge-drag / cost-efficiency optimizer** (after EVAL-10) | **QUEUED** | EVAL-10 is NO-GO (with-hedge −0.558 vs without +0.259), so build `src/analytics/hedge_cost_optimizer.py`: grid-search hedge sizing + toxicity threshold + hedge-cost bps to maximize **net** Sharpe subject to `mean_abs_delta_usd <= target` and `cost >= 0`; emit a net-Sharpe surface and the best feasible config; tests + CLI + artifact `HEDGE_COST_OPTIMIZER_<UTC>.{json,md}`. **Note:** `evaluate_gamma_inventory_hedge(..., hedge_cost_bps=0)` and `hedge_cost_bps=10` produced **identical** aggregate returns this session — verify the parameter actually changes hedge sizing before trusting a cost-bps axis; if it is inert, vary `cost_budget_bps` / `toxicity_threshold` / `target_delta_usd` instead and document it. |
| EVAL-12 | **Real-data walk-forward certification (DSR + PBO)** (after EVAL-11) | **QUEUED** | Using the real `DataLoader` (not synthetic), run BTC/ETH × 3 venues walk-forward; compute **Deflated Sharpe Ratio** (reuse `_deflated_sharpe` in `strategy_falsification.py:105`) and **Probability of Backtest Overfitting** (no PBO helper exists — implement one, e.g. CSCV, or fail loudly); multiple-testing correction across configs; `src/analytics/real_walkforward_certification.py` + tests + CLI + artifact `REAL_WF_CERTIFICATION_<UTC>.{json,md}`. **Data reality check (verified this session):** `data/raw/orderflow_btcusdt_synthetic.json` has **1000 trades** and loads via `DataLoader.load_trades` after the fix below. **There is NO `orderflow_ethusdt_synthetic.json`** — ETH orderflow only exists via the engine's deterministic synthesis fallback (`_load_orderflow` in `src/campaign/integrated.py:184`), not as a file. `data/raw/options_btc_synthetic.json` has 30 quotes; there is no ETH options file. `data/processed/*_{venue}_{sym}_*.json` are **snapshots with no trade arrays** (aggregate `orderflow`/`options` blocks only) — do not expect per-trade walk-forward from them; `data/processed/features_*.json` likewise aggregate. **Consequence for EVAL-12:** "BTC/ETH × 3 venues" cannot be built from on-disk trade files alone — use BTC real trades + the deterministic synthesis path for the rest, and state that limitation explicitly in the artifact rather than pretending it is fully real. |

**Rule:** work strictly in order. Do not skip EVAL-10. Do not advance EVAL-11/12 until the prior task is sealed with a real artifact. Do not re-open EVAL-02/03/06/07/08/09. Do not implement or advance Phase 292+ or any `phaseNN_*_post_attribution_seal_orchestrator` wrapper.

## HEAVY-WORK FLOOR (a session that does less is a FAILED session)

Future agents cannot avoid heavy compute by producing a thin wrapper, a stub, or an env-only report. Every task in this campaign must, at minimum:

1. **Run real computation on real data paths** — the EVAL-09 engine (or the real `DataLoader` for EVAL-12), never a synthetic toy whose numbers are trivially good. The multi-seed bootstrap + permutation + cost-grid must actually execute, not be hard-coded or skipped.
2. **Ship a module + numeric-invariant test file + CLI + a written artifact** with the exact filename pattern in the campaign table. No `{"valid": True}` reports; no NaN/Infinity.
3. **Assert non-degeneracy** (e.g. >=2 distinct nonzero per-window returns, >=2 seeds, CIs that straddle the point estimate, verdict not constant unless the data warrants it).
4. **Seal with a deterministic verdict** (`GO`/`NO-GO`, or the optimizer's best feasible config) computed by a strict function — not prose, not a coin flip, not tuned to a desired answer.
5. **Cite exact artifact paths and key numbers** in this handoff when advancing, and update this file in place (never create a competing handoff).
6. **No handoff-maintenance loop for the next agent.** If you are the next agent and this file still shows EVAL-10 ACTIVE while `tests/test_eval10_final_gonogo.py` is absent, do **not** merely refresh this timestamp, re-run the 142-test gate, or re-verify the environment. Your first code change must add the EVAL-10 driver/test and execute the real multi-seed computation. A future agent session that only edits this handoff while EVAL-10 remains unstarted is a **FAILED session**.

The floor applies to EVAL-10, EVAL-11, and EVAL-12 equally. If a task cannot meet the floor, **fail loudly** with the specific blocker rather than emit a vacuous artifact.

---

## VERIFIED STATE — ground truth (build on it; do not re-verify environment)

- **Environment:** Python 3.12.3; deps installed (`numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pydantic 2.14.3, pytest 9.2.0, PyYAML 6.0.1, requests 2.31.0`). If a fresh container lacks deps, re-run `python3 -m pip install --break-system-packages -r requirements.txt` first. **`mypy`, `ruff`, `flake8` are NOT installed** — `mypy.ini` exists but is unenforceable here; verify with `python3 -m py_compile` and pytest only.
- **Gate re-verified this session (23:1x Z), full 9-file run:** `tests/test_strategy_falsification.py tests/test_gamma_inventory_hedge.py tests/test_cross_venue_netting.py tests/test_capacity_aware_tca.py tests/test_oos_walkforward.py tests/test_integrated_campaign.py tests/test_strategy_evaluation.py tests/test_data_loader_and_validation.py tests/test_campaign_resume.py` → **142 passed in 144.32s** (was 119 across 7 files; +23 from the new `permutation_test` and loader tests). Fast subsets: `test_strategy_evaluation.py` **16 passed / 1.15s** (was 11); `test_data_loader_and_validation.py` **6 passed / 0.37s** (was 2); `test_campaign_resume.py` **12 passed / 0.34s**.
- **EVAL-10 state:** NOT STARTED. Confirmed absent: `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_*`, `tests/test_eval10_final_gonogo.py`, `src/analytics/eval10_final_gonogo.py`, and any `--eval10` flag in `src/analytics/strategy_falsification.py`.
- **EVAL-02 COMPLETE:** `src/analytics/strategy_evaluation.py` + `tests/test_strategy_evaluation.py` + `scripts/evaluate_strategy.py` + `tests/test_evaluate_strategy.py`. Artifacts `STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}`.
- **EVAL-03 COMPLETE:** `src/analytics/regime_sizing.py` + `tests/test_regime_sizing.py` (7). GO; 50 windows; 460 trades; regime Sharpe 0.042420 vs flat 0.026375. Artifact `REGIME_SIZING_20261112T151421.312990Z.json`.
- **EVAL-06 COMPLETE (sealed NO-GO):** `src/analytics/strategy_falsification.py` + tests. pass_fraction 0.60 (need >=0.70); mean_net_sharpe 8.860771; mean_net_return 0.025482; cost grid 8.9946/8.8608/8.0745/7.3734 at 0/1/5/10 bps; mean_permutation_p 0.752. Artifact `STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`.
- **EVAL-07 COMPLETE:** `src/analytics/capacity_aware_tca.py` + tests + CLI. Artifact `CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. mean_capacity_net_sharpe 8.250491 vs baseline 9.197960.
- **EVAL-08 COMPLETE:** `src/analytics/cross_venue_netting.py` (1091) + tests (21) + CLI. Artifact `CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`. mean_oos_sharpe with 8.006530 vs without 5.796608.
- **EVAL-09 COMPLETE:** `src/analytics/gamma_inventory_hedge.py` (1061) + tests (16) + CLI. Canonical artifact `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}` (`generated_at` 2026-11-12T22:04:02Z). Earlier `211228Z`/`211350Z` artifacts lack `window_returns` — do not use them.
- **Reusable real code (do not rewrite):** `src/backtest/engine.py`, `src/backtest/options_hedging.py`, `src/features/*`, `src/signals/*`, `src/campaign/integrated.py`, `src/analytics/*`, `src/orderflow/`, `src/execution/*`, `src/risk/*`. Legacy Phase 15–19 and Phase 21 modules are reference only.
- **`scripts/run_backtest.py` is a vacuous smoke test** (single trade, Sharpe≈6.3 from 2 marks). Do not treat its numbers as strategy performance.
- **Signal data is synthetic-deterministic.** `_generate_price_paths` in `src/campaign/integrated.py:147` builds seeded GBM paths; `data/raw/*.json` are synthetic fixtures. "Real data" in this repo means `data/processed/` venue snapshots, which are aggregate (no trade arrays).

## BOTTLENECKS REMOVED (this session — 2026-11-12T23:07Z)

| Bottleneck | Resolution |
|---|---|
| **No permutation primitive existed.** Prior handoff told the next agent to get permutation p-values from `block_bootstrap_ci` (a CI) and `compare_to_baseline` (a dict-diff) — neither does permutation, so EVAL-10 was **unimplementable as specified**. The only permutation code was private signal-shuffling inside `_evaluate_seed`. | **FIXED.** Added `permutation_test(...)` to `src/analytics/strategy_evaluation.py` (paired/unpaired, three alternatives, `(1+extreme)/(1+n)` p-value, deterministic via `np.random.default_rng(seed)`) + 5 tests. Verified on real EVAL-09 data: paired with-vs-without `diff=-0.230609, p=0.0015` (2000 perms). |
| **`DataLoader.load_trades` silently returned 0 trades** on dict-wrapped JSON (iterated dict keys → every record failed with `'str' object has no attribute 'get'`, swallowed by the try/except). This would have blocked EVAL-12's "use the real DataLoader" requirement. | **FIXED.** `load_trades` now unwraps `{"trades"|"data"|"items"|"results": [...]}` and bare lists. Verified: `data/raw/orderflow_btcusdt_synthetic.json` now yields **1000 trades** (was 0). +4 regression tests. |
| **Cost-grid spec was wrong.** EVAL-09 `window_returns` already include the 1 bp hedge cost, so applying a 0/1/5/10 bps grid by re-costing from zero double-counts and breaks monotonicity. | **CLARIFIED with the verified incremental formula** and pre-computed expected grid values (−0.557641 / −0.558011 / −0.559488 / −0.561329). |
| **`compute_metrics` misused risk.** It takes an equity curve, not a return list. | **CLARIFIED** in the reuse points. |
| Four competing handoffs / stale stubs | **CLEARED (prior session, re-verified).** Root stubs are pure "RETIRED — read durable_handoff.md" pointers with no task ID. |
| `tests/test_campaign_resume.py::test_durable_handoff_is_source_of_truth` | **PASSING** — file keeps `SINGLE DURABLE HANDOFF`, `INITIAL TASK MESSAGE`, and the required `phase 15` reference. |
| Cross-process non-determinism (salted `hash()`) | **FIXED earlier** with `_stable_seed()` (SHA-256); verified across two processes. |
| All-zero signal series → 0 windows/trades | **FIXED earlier** with time-varying causal momentum z-scores. |
| Naive full `pytest` on 865 test files (clone treadmill) | **AVOID THE TRAP.** Run only the named EVAL test files; never `pytest tests/` wholesale. |
| `research_state/` ~5 GB / ~77k files can stall naive globbing | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit filenames/globs. |
| Phase 272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` clone treadmill | **CLOSED.** Do not implement/seal/advance Phase 292+. |
| EVAL-10 not built | **OPEN — the sole active task.** No artifact/test/CLI flag; proceed with the spec above. |
| `hedge_cost_bps` may be inert in the EVAL-09 engine | **OPEN — flagged for EVAL-11.** `hedge_cost_bps=0` and `=10` gave identical aggregate returns this session; verify before building a cost-bps axis in the optimizer. |

**Tree verified 2026-11-12T23:07Z:** EVAL-02/03/06/07/08/09 sealed with artifacts present (EVAL-09 canonical `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`); `src/analytics/gamma_inventory_hedge.py` and `tests/test_gamma_inventory_hedge.py` present; `.env` absent. Modified this session (uncommitted): `src/analytics/strategy_evaluation.py`, `src/data/loader.py`, `tests/test_strategy_evaluation.py`, `tests/test_data_loader_and_validation.py`. No active blockers besides building EVAL-10.

## P0 SAFETY — CLEAR

- `.env` **ABSENT**. `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO network calls to exchanges, NO NEXT9 unblock.**

## SCOPE & HARD GUARDS (non-negotiable)

- **Allowed:** `src/`, `scripts/`, `tests/`, `research_state/` (explicit files only). Additive, deterministic, bounded, paper-only, guarded.
- **Forbidden:** live trading, `.env` creation, venue/config/credential mutation, NEXT9 unblock, any new `phaseNN_*_post_attribution_seal_orchestrator` wrapper, refactoring sealed legacy phases, and enumerating `research_state/` or running the full 865-file test suite.
- Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`.

## HANDOFF DISCIPLINE

- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- Work the queue strictly in order: EVAL-10 (ACTIVE) → EVAL-11 (queued) → EVAL-12 (queued).
- Each task must ship a real module, a numeric-invariant test file, a CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If context/time runs out: commit/push the partial new module and leave this file pointing at the exact next line to write. Never leave the tree clean with the task "pending."
- A final response containing only "verified env / will start next session" is a **failed session**.
- Final responses must not ask follow-up questions.