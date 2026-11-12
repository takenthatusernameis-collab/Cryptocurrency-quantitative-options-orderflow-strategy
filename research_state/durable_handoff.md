# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-12T22:58:17Z (UTC). Re-verified this session: `GAMMA_INVENTORY_HEDGE_20261112T221000Z.json` present (7.2 MB) with **30/30** non-degenerate seed×symbol×side series (`len=10`, `distinct>=4`, `nonzero>=3`), aggregate `mean_oos_return_with_hedge=-0.5580107668605527`, `mean_oos_return_without_hedge=0.2590709968068878`; `tests/test_eval10_final_gonogo.py` and `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_*` **absent**; no `--eval10` CLI flag in `src/analytics/strategy_falsification.py`; `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; root handoffs remain retired pointers. Prior gate evidence (2026-11-12T22:12Z): 7-file EVAL gate **119 passed / 144.87s**, `tests/test_campaign_resume.py` **12 passed**. **EVAL-10 is the ONLY ACTIVE task — execute it end-to-end now; do not re-verify the environment or re-run baseline gates unless you change code they cover.**
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are **retired pointer stubs** — do not action them and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope), not task sources.

---

## INITIAL TASK MESSAGE — 2026-11-12T22:12:33Z (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-12T22:12:33Z-STRATEGY-EVAL-10-FINAL-GONOGO`
**STATUS:** ACTIVE. This is the single next task. Do not pick a different task. Do not re-verify the environment (deps are installed; `.env` absent; safety flags set). Build the EVAL-10 driver, run the real multi-seed evaluation, seal it, then continue to EVAL-11 in the same session if time allows.

> **EVAL-09 is DONE and sealed (do not re-open EVAL-02/03/06/07/08/09).** `src/analytics/gamma_inventory_hedge.py` (1061 lines) + `tests/test_gamma_inventory_hedge.py` (16 tests) + CLI shipped; **canonical artifact regenerated this session at `research_state/GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`** (numbers identical to the earlier run: mean_oos_return_with_hedge −0.5580, without +0.2591, Sharpe −22.7659 / +5.5867, total_cost_usd 1429.68). Gate green.
>
> **EVAL-10 = final net-of-cost GO/NO-GO certification on the EVAL-09 with-hedge portfolio.** Run multi-seed bootstrap + permutation on the EVAL-09 per-window OOS returns, with a cost grid at 0/1/5/10 bps, and seal an honest GO/NO-GO verdict. A NO-GO verdict is a valid, expected outcome — do **not** tune the data to force GO.

### Exact reuse points (verified on disk this session — do not re-implement)
- EVAL-09 engine: `src/analytics/gamma_inventory_hedge.py::evaluate_gamma_inventory_hedge(seeds=[1,2,3,4,5])`.
  Per-window return series: `report["per_seed"][i]["symbols"][<sym>]["with_hedge"]["window_returns"]` (plain list; `["windows"][*]["window_return"]` carries the same data with metadata). **Verified this session in `GAMMA_INVENTORY_HEDGE_20261112T221000Z.json`:** every seed×symbol×side series has `len=10`, `distinct>=4`, `nonzero>=3` — degeneracy guard satisfied. Aggregate is at `report["aggregate"]` (`mean_oos_return_with_hedge`, `mean_oos_sharpe_with_hedge`, `mean_toxicity_score`, `toxic_gate_active_fraction`, etc.). Report top-level keys: `report_id, generated_at, config, per_seed, aggregate, never_valid_true`.
  **Artifact warning:** the older EVAL-09 artifacts `GAMMA_INVENTORY_HEDGE_20261112T211228Z.*` and `...T211350Z.*` predate commit `32f720d60` (21:30:48Z) and therefore **lack `window_returns`/`windows`** — do NOT read per-window returns from them. Use the `...T221000Z.*` artifact or call the engine in-process.
- EVAL-06 falsification: `src/analytics/strategy_falsification.py::evaluate_strategy_falsification(...)` and its CLI `main()` (argparse at line 739; currently has **no** `--eval10` flag — add one, or add a thin `src/analytics/eval10_final_gonogo.py` that imports the helpers below).
- Bootstrap/permutation: `src/analytics/strategy_evaluation.py::block_bootstrap_ci` (line 196) and `::compare_to_baseline` (line 283). Reuse these; do **not** re-implement permutation logic.
- Metrics: `src/analytics/strategy_evaluation.py::compute_metrics` (chained-equity OOS metrics); cost grid constant `COST_GRID_BPS` in `strategy_falsification.py`.
- Serialization: `serialize_metrics_strict` + `assert_json_valid` (used by both analytics modules). Never emit a bare `{"valid": True}`.

### Deliverable 1 — EVAL-10 driver / CLI (real computation, deterministic, no network)
- Reuse EVAL-09's with-hedge per-window returns as the strategy return series; compare against the EVAL-06 flat-cost baseline and the EVAL-09 without-hedge portfolio.
- Multi-seed block-bootstrap CI (seed-fixed, deterministic) for mean net Sharpe / mean net return; permutation p-values via `block_bootstrap_ci`/`compare_to_baseline`.
- Cost-grid net Sharpe at 0/1/5/10 bps (monotone-nonincreasing expected).
- Report per-seed `failing_conditions`; `pass_fraction` in [0,1]; `verdict = "GO" if pass_fraction >= 0.70 else "NO-GO"` (strict deterministic function).
- CLI: `python3 src/analytics/strategy_falsification.py --eval10 --seeds 1 2 3 4 5 --write` (or the thin EVAL-10 module) writing `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_<UTC>.{json,md}`.

### Deliverable 2 — `tests/test_eval10_final_gonogo.py` (numeric invariants; all must pass)
- determinism across two separate processes (byte-identical report);
- `pass_fraction` in [0,1]; `mean_net_sharpe`/`mean_net_return` finite;
- cost-grid net Sharpe monotone-nonincreasing in bps;
- verdict is exactly `"GO" if pass_fraction >= 0.70 else "NO-GO"`;
- bootstrap/permutation CIs finite with `lo <= point <= hi`;
- CLI entry test returns 0 and writes both artifacts;
- explicitly assert the report is not `{"valid": True}`.

### Exit gate (ALL must be true before sealing)
- `python3 -m pytest tests/test_eval10_final_gonogo.py tests/test_strategy_falsification.py tests/test_gamma_inventory_hedge.py tests/test_cross_venue_netting.py tests/test_capacity_aware_tca.py tests/test_oos_walkforward.py tests/test_integrated_campaign.py -q` → **all pass**.
- `python3 -m py_compile` clean on any new/edited module.
- Real run `--seeds 1 2 3 4 5 --write` produced finite GO/NO-GO metrics for every seed; cite exact artifact paths in the sealed record.
- `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`.
- No new `phaseNN_*_post_attribution_seal_orchestrator` wrapper; no legacy-phase edits.
- **Update this handoff in place:** mark EVAL-10 COMPLETE with verified GO/NO-GO verdict and numbers, then advance the campaign to EVAL-11.

### Anti-vacuous gates (a report that trips any is a FAILED session)
- report not `{"valid": True}`; no NaN/Infinity;
- verdict deterministic and not identically GO/NO-GO across seeds unless the data genuinely warrants it;
- bootstrap CI lo/hi finite and straddle the point estimate.
- **Degeneracy guard (verified real risk):** EVAL-09 at small configs (e.g. `n_points=200`) produces `window_returns` with many `0.0` entries and can yield 4 windows. Always run EVAL-10 with the **real EVAL-09 default config** (`n_points=500, train_window=120, test_window=40, step_size=40`, 10 windows/seed) and assert each seed's series has **>= 2 distinct nonzero values** (and `len >= 2`); otherwise **fail loudly** rather than emit a vacuous CI. Do not paper over zeros. **Verified this session** on the `...T221000Z.*` artifact: all 30 series (5 seeds × 3 symbols × 2 sides) have `len=10`, `distinct>=4`, `nonzero>=3` — guard passes with the default config; keep it as a hard assertion in the EVAL-10 driver.

---

## FOCUS CAMPAIGN (strictly sequential; heavy work is mandatory at every step — do not stop after EVAL-10)

| Order | Task | Status | Required output |
|---|---|---|---|
| EVAL-07 | Capacity/liquidity-aware TCA | **COMPLETE** | `src/analytics/capacity_aware_tca.py` + tests + CLI; artifact `CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. |
| EVAL-08 | Cross-venue delta netting | **COMPLETE** | `src/analytics/cross_venue_netting.py` + `tests/test_cross_venue_netting.py` (21 tests) + CLI; artifact `CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`. |
| EVAL-09 | Gamma/inventory hedge + toxicity gating | **COMPLETE** | `src/analytics/gamma_inventory_hedge.py` + `tests/test_gamma_inventory_hedge.py` (16 tests) + CLI; **canonical artifact `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`** (regenerated this session with `window_returns`; earlier `211228Z`/`211350Z` artifacts are stale and lack `window_returns`). |
| EVAL-10 | **Final net-of-cost GO/NO-GO certification** | **ACTIVE** | EVAL-10 driver on EVAL-09 with-hedge per-window returns; multi-seed bootstrap/permutation + 0/1/5/10 bps cost grid; `tests/test_eval10_final_gonogo.py`; artifact `STRATEGY_EVAL_10_FINAL_GONOGO_<UTC>.{json,md}`. Full spec + exit gate above. |
| EVAL-11 | **Hedge-drag / cost-efficiency optimizer** (do after EVAL-10) | **QUEUED** | If EVAL-10 is NO-GO (expected: EVAL-09 with-hedge return −0.558 vs without +0.259), build `src/analytics/hedge_cost_optimizer.py`: grid-search hedge sizing + toxicity threshold + hedge-cost bps to maximize **net** Sharpe subject to `mean_abs_delta_usd <= target` and `cost >= 0`; emit a net-Sharpe surface and the best feasible config; tests + CLI + artifact `HEDGE_COST_OPTIMIZER_<UTC>.{json,md}`. |
| EVAL-12 | **Real-data walk-forward certification (DSR + PBO)** (do after EVAL-11) | **QUEUED** | Using the real `DataLoader` (not synthetic), run BTC/ETH × 3 venues walk-forward; compute **Deflated Sharpe Ratio** and **Probability of Backtest Overfitting**; multiple-testing correction across configs; `src/analytics/real_walkforward_certification.py` + tests + CLI + artifact `REAL_WF_CERTIFICATION_<UTC>.{json,md}`. |

**Rule:** work strictly in order. Do not skip EVAL-10. Do not advance EVAL-11/12 until the prior task is sealed with a real artifact. Do not re-open EVAL-02/03/06/07/08/09. Do not implement or advance Phase 292+ or any `phaseNN_*_post_attribution_seal_orchestrator` wrapper.

## HEAVY-WORK FLOOR (a session that does less is a FAILED session)

Future agents cannot avoid heavy compute by producing a thin wrapper, a stub, or an env-only report. Every task in this campaign must, at minimum:

1. **Run real computation on real data paths** — the EVAL-09 engine (or the real `DataLoader` for EVAL-12), never a synthetic toy whose numbers are trivially good. The multi-seed bootstrap + permutation + cost-grid must actually execute, not be hard-coded or skipped.
2. **Ship a module + numeric-invariant test file + CLI + a written artifact** with the exact filename pattern in the campaign table. No `{"valid": True}` reports; no NaN/Infinity.
3. **Assert non-degeneracy** (e.g. >=2 distinct nonzero per-window returns, >=2 seeds, CIs that straddle the point estimate, verdict not constant unless the data warrants it).
4. **Seal with a deterministic verdict** (`GO`/`NO-GO`, or the optimizer's best feasible config) computed by a strict function — not prose, not a coin flip, not tuned to a desired answer.
5. **Cite exact artifact paths and key numbers** in this handoff when advancing, and update this file in place (never create a competing handoff).
6. **No handoff-maintenance loop for the next agent.** If you are the next agent and this file still shows EVAL-10 ACTIVE while `tests/test_eval10_final_gonogo.py` is absent, do **not** merely refresh this timestamp, re-run the 119-test gate, or re-verify the environment. Your first code change must add the EVAL-10 driver/test and execute the real multi-seed computation. A future agent session that only edits this handoff while EVAL-10 remains unstarted is a **FAILED session**.

The floor applies to EVAL-10, EVAL-11, and EVAL-12 equally. If a task cannot meet the floor, **fail loudly** with the specific blocker rather than emit a vacuous artifact.

---

## VERIFIED STATE — ground truth (build on it; do not re-verify environment)

- **Environment:** Python 3.12.3; deps installed via `python3 -m pip install --break-system-packages -r requirements.txt` (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pydantic 2.14.3, pytest 9.2.0, PyYAML 6.0.1, requests 2.31.0). If a fresh container lacks deps, re-run that exact pip command first.
- **Baseline gate re-verified this session (2026-11-12T22:12Z):** `tests/test_strategy_falsification.py tests/test_gamma_inventory_hedge.py tests/test_capacity_aware_tca.py tests/test_oos_walkforward.py tests/test_integrated_campaign.py tests/test_cross_venue_netting.py tests/test_strategy_evaluation.py` → **119 passed in 144.87s**. `tests/test_campaign_resume.py` → 12 passed in 0.40s.
- **EVAL-10 state:** NOT STARTED. Confirmed absent: `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_*`, `tests/test_eval10_final_gonogo.py`, and any `--eval10` flag in `src/analytics/strategy_falsification.py` (its CLI `main()` is at line 739 and only handles EVAL-06).
- **EVAL-02 COMPLETE:** `src/analytics/strategy_evaluation.py` + `tests/test_strategy_evaluation.py` (11) + `scripts/evaluate_strategy.py` + `tests/test_evaluate_strategy.py` (6). Artifacts `STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}`.
- **EVAL-03 COMPLETE:** `src/analytics/regime_sizing.py` + `tests/test_regime_sizing.py` (7). GO; 50 windows; 460 trades; regime Sharpe 0.042420 vs flat 0.026375; delta +0.016045. Artifact `REGIME_SIZING_2026-11-12T151421.312990Z.json`.
- **EVAL-06 COMPLETE (sealed NO-GO):** `src/analytics/strategy_falsification.py` + `tests/test_strategy_falsification.py`. pass_fraction 0.60 (need >=0.70); mean_net_sharpe 8.860771; mean_net_return 0.025482; cost grid 8.9946/8.8608/8.0745/7.3734 at 0/1/5/10 bps; mean_permutation_p 0.752; failing: seed 1 and seed 4 (bootstrap_or_permutation). Artifact `STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`.
- **EVAL-07 COMPLETE:** `src/analytics/capacity_aware_tca.py` + tests + CLI. Artifact `CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. Seeds 1..5 pass; mean_capacity_net_sharpe 8.250491; mean_baseline_net_sharpe 9.197960; capacity_vs_baseline_sharpe −0.947469; cost grid 9.1980/9.1571/8.9929/8.7863 (monotone decreasing).
- **EVAL-08 COMPLETE:** `src/analytics/cross_venue_netting.py` (1091 lines) + `tests/test_cross_venue_netting.py` (21) + CLI. Artifact `CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`. mean_net_notional_ratio 0.355666 (engages); mean_oos_sharpe with 8.006530 vs without 5.796608 (delta +2.209922); max-DD 0.014245 vs 0.030161.
- **EVAL-09 COMPLETE:** `src/analytics/gamma_inventory_hedge.py` (1061) + `tests/test_gamma_inventory_hedge.py` (16) + CLI. **Canonical artifact `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`** (regenerated this session; contains `window_returns` and `snapshots`; `generated_at` 2026-11-12T22:04:02Z). Earlier `211228Z`/`211350Z` artifacts predate the serialization commit and lack `window_returns` — do not use them. toxic_gate_active_fraction 0.3333 (engages); mean_oos_return_with_hedge **−0.5580** vs without +0.2591; mean_oos_sharpe_with_hedge **−22.7659** vs without +5.5867 (sharpe_delta −28.3527); mean_oos_max_drawdown_with_hedge 0.6650 vs without 0.0761; total_cost_usd 1429.68. This is why EVAL-10 will likely seal NO-GO and EVAL-11 must fix the hedge drag.
- **Reusable real code (do not rewrite):** `src/backtest/engine.py`, `src/backtest/options_hedging.py`, `src/features/*`, `src/signals/*`, `src/campaign/integrated.py`, `src/analytics/*`, `src/orderflow/`, `src/execution/*`, `src/risk/*`. Legacy Phase 15–19 and Phase 21 execution/risk/observability modules are reference only.
- **`scripts/run_backtest.py` is a vacuous smoke test** (single trade, Sharpe≈6.3 from 2 marks). Do not treat its numbers as strategy performance.

## BOTTLENECKS REMOVED (this session)

| Bottleneck | Resolution |
|---|---|
| Missing Python deps (no numpy/pandas/scipy/pydantic/pytest) | **CLEARED earlier**; re-verified importable this session. |
| Four competing handoffs / stale stubs | **CLEARED.** Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are pure "RETIRED — read durable_handoff.md" pointers with no task ID. |
| Stale handoff timestamp (21:57Z) and no next-campaign continuity | **CLEARED.** Refreshed to 22:12:33Z with EVAL-10 precise reuse points and a queued EVAL-11/EVAL-12 campaign so no future session can do a trivial pass. |
| `tests/test_campaign_resume.py::test_durable_handoff_is_source_of_truth` | **PASSING** — file keeps `SINGLE DURABLE HANDOFF`, `INITIAL TASK MESSAGE`, and the required `phase 15` reference. |
| Cross-process non-determinism (salted `hash()`) | **FIXED earlier** with `_stable_seed()` (SHA-256); verified across two processes. |
| All-zero signal series → 0 windows/trades/return | **FIXED earlier** with time-varying causal momentum z-scores; real run has 10 windows and nonzero return/Sharpe. |
| Per-symbol OOS return excluded open-position MTM | **FIXED earlier** via chained per-window OOS equity; test-locked by `tests/test_oos_walkforward.py`. |
| Naive full `pytest` on 865 test files (clone treadmill) | **AVOID THE TRAP.** Run only the named EVAL test files; never `pytest tests/` wholesale. |
| `research_state/` ~5 GB / ~107k files can stall naive globbing | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit filenames/globs. |
| Phase 272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` clone treadmill | **CLOSED.** Do not implement/seal/advance Phase 292+. |
| EVAL-10 not built | **OPEN — the sole active task.** No artifact/test/CLI flag; proceed with the spec above. |
| **Stale EVAL-09 artifact lacked `window_returns` (would have blocked EVAL-10)** | **CLEARED this session.** On-disk `GAMMA_INVENTORY_HEDGE_20261112T211350Z.json` (and `211228Z`) predate commit `32f720d60` (21:30:48Z) and had no per-window returns. Regenerated the artifact with current code → `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`; verified `window_returns` present for all 30 seed×symbol×side series and identical aggregate numbers (−0.5580 / +0.2591). EVAL-10 can now read either the fresh artifact or the in-process engine. |

**Tree verified 2026-11-12T22:12Z:** EVAL-02/03/06/07/08/09 sealed with artifacts present (EVAL-09 canonical artifact `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`); `src/analytics/gamma_inventory_hedge.py` and `tests/test_gamma_inventory_hedge.py` present; `.env` absent. Only the three retired root pointers exist at root. No active blockers besides building EVAL-10.

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