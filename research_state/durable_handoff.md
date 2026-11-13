# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-13T00:02:49Z (UTC). Re-verified this session against the tree: `src/analytics/eval10_final_gonogo.py` and `tests/test_eval10_final_gonogo.py` **present**; `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}` **present** (7.6 KB JSON / 3.6 KB MD). EVAL-10 sealed **NO-GO** (pass_fraction 0.0/5). `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; root handoffs remain retired pointers. **All bottlenecks cleared — see BOTTLENECKS REMOVED.**
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are **retired pointer stubs** — do not action them and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope), not task sources.

---

## INITIAL TASK MESSAGE — 2026-11-13T00:02:49Z (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-13T00:02:49Z-EVAL-11-HEDGE-COST-OPTIMIZER`
**STATUS:** ACTIVE. This is the single next task. Do not pick a different task. Do not re-verify the environment (deps installed; `.env` absent; safety flags set; EVAL-10 sealed NO-GO). Build `src/analytics/hedge_cost_optimizer.py` per the EVAL-11 spec below, run it against the EVAL-09 engine, surface the net-Sharpe cost/hedge-size grid, seal the best feasible config, then continue to EVAL-12 in the same session if time allows.

---

## SEALED EVALUATIONS (do not re-open)

> **EVAL-09 is DONE and sealed (do not re-open EVAL-02/03/06/07/08/09).** `src/analytics/gamma_inventory_hedge.py` (1061 lines) + `tests/test_gamma_inventory_hedge.py` (16 tests) + CLI shipped; canonical artifact `research_state/GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}` (7.2 MB JSON). Aggregate `mean_oos_return_with_hedge=-0.5580107668605527`, `mean_oos_return_without_hedge=0.2590709968068878`, `mean_oos_sharpe_with_hedge=-22.765929562035716`, `mean_oos_sharpe_without_hedge=5.586740988848094`, `total_cost_usd=1429.6848986289629`, `mean_toxicity_score=0.713277330797748`, `toxic_gate_active_fraction=0.3333333333333333`.
>
> **EVAL-10 is DONE and sealed (do not re-open).** `src/analytics/eval10_final_gonogo.py` + `tests/test_eval10_final_gonogo.py` (10 tests) + CLI shipped; canonical artifact `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}`. Verdict **NO-GO**: `pass_fraction = 0/5 = 0.0` (need >= 0.70). Mean net return @1 bp −0.5580107668605527 vs without-hedge +0.2590709968068878; mean net Sharpe −22.765929562035716. Cost grid monotone nonincreasing: 0 bps −0.5576407 / −22.7598773, 1 bps −0.5580108 / −22.7659296, 5 bps −0.5594883 / −22.7902305, 10 bps −0.5613291 / −22.8208139. Paired permutation with-vs-without `observed_difference≈−0.2306`, `p=0.0005` (significant). Bootstrap CI mean net return [−0.6421, −0.5057], mean net Sharpe [−36.7466, −11.1379]. All 10 numeric-invariant tests pass; full gate **152 passed / ~362 s**.

**Reuse points (verified on disk):** EVAL-09 engine `src/analytics/gamma_inventory_hedge.py::evaluate_gamma_inventory_hedge(seeds=[1,2,3,4,5])` (18.5 s for 5 seeds, in-process). Per-window series: `report["per_seed"][i]["symbols"][<sym>]["with_hedge"]["window_returns"]` (list of 10 floats) and `["windows"][*]` with `window_return`, `window_traded_notional`, `window_nav_start`, `window_cost_usd`, `window_hedges`, `window_trades`. Bootstrap/permutation/metrics primitives live in `src/analytics/strategy_evaluation.py`; serialization via `serialize_metrics_strict` + `assert_json_valid` (never `{"valid": True}`). EVAL-06 flat-cost baseline reference: `research_state/STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}` (present; do not re-run).

---

## FOCUS CAMPAIGN (strictly sequential; heavy work is mandatory at every step — do not stop after EVAL-10)

| Order | Task | Status | Required output |
|---|---|---|---|
| EVAL-07 | Capacity/liquidity-aware TCA | **COMPLETE** | `src/analytics/capacity_aware_tca.py` + tests + CLI; `CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. |
| EVAL-08 | Cross-venue delta netting | **COMPLETE** | `src/analytics/cross_venue_netting.py` + `tests/test_cross_venue_netting.py` (21) + CLI; `CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`. |
| EVAL-09 | Gamma/inventory hedge + toxicity gating | **COMPLETE** | `src/analytics/gamma_inventory_hedge.py` + tests (16) + CLI; canonical `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`. |
| EVAL-10 | Final net-of-cost GO/NO-GO certification | **COMPLETE** | `src/analytics/eval10_final_gonogo.py` + `tests/test_eval10_final_gonogo.py` (10) + CLI; artifact `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}`; verdict NO-GO (pass_fraction 0.0/5). |
| EVAL-11 | **Hedge-drag / cost-efficiency optimizer** (after EVAL-10) | **ACTIVE** | EVAL-10 is NO-GO (with-hedge −0.558 vs without +0.259), so build `src/analytics/hedge_cost_optimizer.py`: grid-search hedge sizing + toxicity threshold + hedge-cost bps to maximize **net** Sharpe subject to `mean_abs_delta_usd <= target` and `cost >= 0`; emit a net-Sharpe surface and the best feasible config; tests + CLI + artifact `HEDGE_COST_OPTIMIZER_<UTC>.{json,md}`. **Note:** `evaluate_gamma_inventory_hedge(..., hedge_cost_bps=0)` and `hedge_cost_bps=10` produced **identical** aggregate returns this session — verify the parameter actually changes hedge sizing before trusting a cost-bps axis; if it is inert, vary `cost_budget_bps` / `toxicity_threshold` / `target_delta_usd` instead and document it. |
| EVAL-12 | **Real-data walk-forward certification (DSR + PBO)** (after EVAL-11) | **QUEUED** | Using the real `DataLoader` (not synthetic), run BTC/ETH × 3 venues walk-forward; compute **Deflated Sharpe Ratio** (reuse `_deflated_sharpe` in `strategy_falsification.py:105`) and **Probability of Backtest Overfitting** (no PBO helper exists — implement one, e.g. CSCV, or fail loudly); multiple-testing correction across configs; `src/analytics/real_walkforward_certification.py` + tests + CLI + artifact `REAL_WF_CERTIFICATION_<UTC>.{json,md}`. **Data reality check:** `data/raw/orderflow_btcusdt_synthetic.json` has **1000 trades** and loads via `DataLoader.load_trades` after the fix below. **There is NO `orderflow_ethusdt_synthetic.json`** — ETH orderflow only exists via the engine's deterministic synthesis fallback (`_load_orderflow` in `src/campaign/integrated.py:184`), not as a file. `data/raw/options_btc_synthetic.json` has 30 quotes; no ETH options file. `data/processed/*_{venue}_{sym}_*.json` are **snapshots with no trade arrays** (aggregate blocks only). **Consequence:** "BTC/ETH × 3 venues" cannot be built from on-disk trade files alone — use BTC real trades + the deterministic synthesis path for the rest, and state that limitation explicitly in the artifact. |

**Rule:** work strictly in order. Do not skip EVAL-11. Do not advance EVAL-12 until EVAL-11 is sealed with a real artifact. Do not re-open EVAL-02/03/06/07/08/09/10. Do not implement or advance Phase 292+ or any `phaseNN_*_post_attribution_seal_orchestrator` wrapper.

---

## HEAVY-WORK FLOOR (a session that does less is a FAILED session)

Future agents cannot avoid heavy compute by producing a thin wrapper, a stub, or an env-only report. Every task in this campaign must, at minimum:

1. **Run real computation on real data paths** — the EVAL-09 engine (or the real `DataLoader` for EVAL-12), never a synthetic toy whose numbers are trivially good. Bootstrap + permutation + cost-grid / grid-search must actually execute, not be hard-coded or skipped.
2. **Ship a module + numeric-invariant test file + CLI + a written artifact** with the exact filename pattern in the campaign table. No `{"valid": True}` reports; no NaN/Infinity.
3. **Assert non-degeneracy** (e.g. >=2 distinct nonzero per-window returns, >=2 seeds, CIs that straddle the point estimate, verdict not constant unless the data warrants it).
4. **Seal with a deterministic verdict** (`GO`/`NO-GO`, or the optimizer's best feasible config) computed by a strict function — not prose, not a coin flip, not tuned to a desired answer.
5. **Cite exact artifact paths and key numbers** in this handoff when advancing, and update this file in place (never create a competing handoff).
6. **No handoff-maintenance loop for the next agent.** If you are the next agent and this file still shows EVAL-11 ACTIVE while `src/analytics/hedge_cost_optimizer.py` is absent, do **not** merely refresh this timestamp, re-run the gate, or re-verify the environment. Your first code change must add the EVAL-11 optimizer and execute the real computation. A future agent session that only edits this handoff while EVAL-11 remains unstarted is a **FAILED session**.

The floor applies to EVAL-11 and EVAL-12 equally. If a task cannot meet the floor, **fail loudly** with the specific blocker rather than emit a vacuous artifact.

---

## VERIFIED STATE — ground truth (build on it; do not re-verify environment)

- **Environment:** Python 3.12.3; deps installed (`numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pydantic 2.14.3, pytest 9.2.0, PyYAML 6.0.1, requests 2.31.0`). If a fresh container lacks deps, re-run `python3 -m pip install --break-system-packages -r requirements.txt` first. **`mypy`, `ruff`, `flake8` are NOT installed** — `mypy.ini` exists but is unenforceable here; verify with `python3 -m py_compile` and pytest only.
- **Gate re-verified this session:** `tests/test_eval10_final_gonogo.py tests/test_strategy_falsification.py tests/test_gamma_inventory_hedge.py tests/test_cross_venue_netting.py tests/test_capacity_aware_tca.py tests/test_oos_walkforward.py tests/test_integrated_campaign.py tests/test_strategy_evaluation.py tests/test_data_loader_and_validation.py` → **152 passed / ~362 s** (142 base + 10 EVAL-10). Fast subsets: `test_strategy_evaluation.py` 16 passed; `test_data_loader_and_validation.py` 6 passed; `test_campaign_resume.py` 12 passed.
- **EVAL-10 state:** COMPLETE. `src/analytics/eval10_final_gonogo.py`, `tests/test_eval10_final_gonogo.py`, and `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}` present; verdict NO-GO.
- **EVAL-02 COMPLETE:** `src/analytics/strategy_evaluation.py` + `tests/test_strategy_evaluation.py` + `scripts/evaluate_strategy.py` + `tests/test_evaluate_strategy.py`. Artifacts `STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}`.
- **EVAL-03 COMPLETE:** `src/analytics/regime_sizing.py` + `tests/test_regime_sizing.py` (7). GO; 50 windows; 460 trades; regime Sharpe 0.042420 vs flat 0.026375. Artifact `REGIME_SIZING_20261112T151421.312990Z.json`.
- **EVAL-06 COMPLETE (sealed NO-GO):** `src/analytics/strategy_falsification.py` + tests. pass_fraction 0.60 (need >=0.70); mean_net_sharpe 8.860771; mean_net_return 0.025482; cost grid 8.9946/8.8608/8.0745/7.3734 at 0/1/5/10 bps; mean_permutation_p 0.752. Artifact `STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`.
- **EVAL-07 COMPLETE:** `src/analytics/capacity_aware_tca.py` + tests + CLI. Artifact `CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. mean_capacity_net_sharpe 8.250491 vs baseline 9.197960.
- **EVAL-08 COMPLETE:** `src/analytics/cross_venue_netting.py` (1091) + tests (21) + CLI. Artifact `CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`. mean_oos_sharpe with 8.006530 vs without 5.796608.
- **EVAL-09 COMPLETE:** `src/analytics/gamma_inventory_hedge.py` (1061) + tests (16) + CLI. Canonical artifact `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}` (`generated_at` 2026-11-12T22:04:02Z). Earlier `211228Z`/`211350Z` artifacts lack `window_returns` — do not use them.
- **Reusable real code (do not rewrite):** `src/backtest/engine.py`, `src/backtest/options_hedging.py`, `src/features/*`, `src/signals/*`, `src/campaign/integrated.py`, `src/analytics/*`, `src/orderflow/`, `src/execution/*`, `src/risk/*`. Legacy Phase 15–19 and Phase 21 modules are reference only.
- **`scripts/run_backtest.py` is a vacuous smoke test** (single trade, Sharpe≈6.3 from 2 marks). Do not treat its numbers as strategy performance.
- **Signal data is synthetic-deterministic.** `_generate_price_paths` in `src/campaign/integrated.py:147` builds seeded GBM paths; `data/raw/*.json` are synthetic fixtures. "Real data" in this repo means `data/processed/` venue snapshots, which are aggregate (no trade arrays).

---

## BOTTLENECKS REMOVED (this session — 2026-11-13T00:02:49Z)

| Bottleneck | Resolution |
|---|---|
| **EVAL-10 not built** (sole active task — no artifact/test/CLI). | **RESOLVED.** Built `src/analytics/eval10_final_gonogo.py` + `tests/test_eval10_final_gonogo.py` + CLI; real multi-seed run produced NO-GO (pass_fraction 0.0/5); artifact `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}` sealed. |
| **No permutation primitive existed.** Prior handoff told the next agent to get permutation p-values from `block_bootstrap_ci` (a CI) — does not do permutation, so EVAL-10 was unimplementable as specified. | **FIXED (prior session).** Added `permutation_test(...)` to `src/analytics/strategy_evaluation.py` (paired/unpaired, `(1+extreme)/(1+n)` p-value, deterministic) + 5 tests. Verified: paired with-vs-without `diff=-0.230609, p=0.0015`. |
| **`DataLoader.load_trades` silently returned 0 trades** on dict-wrapped JSON (would block EVAL-12's real-DataLoader requirement). | **FIXED (prior session).** `load_trades` unwraps `{"trades"|"data"|"items"|"results": [...]}` and bare lists. Verified: `data/raw/orderflow_btcusdt_synthetic.json` now yields **1000 trades** (was 0). +4 regression tests. |
| **Cost-grid spec was wrong** (double-counted the 1 bp already in EVAL-09 returns). | **CLARIFIED (prior session).** Incremental formula `r_b = window_return - (window_traded_notional * (b - 1) / 1e4) / window_nav_start`; verified grid −0.557641 / −0.558011 / −0.559488 / −0.561329. |
| Four competing handoffs / stale stubs | **CLEARED (prior session).** Root stubs are pure "RETIRED — read durable_handoff.md" pointers with no task ID. |
| Cross-process non-determinism (salted `hash()`) | **FIXED earlier** with `_stable_seed()` (SHA-256); verified across two processes. |
| All-zero signal series → 0 windows/trades | **FIXED earlier** with time-varying causal momentum z-scores. |
| Naive full `pytest` on 865 test files (clone treadmill) | **AVOID THE TRAP.** Run only the named EVAL test files; never `pytest tests/` wholesale. |
| `research_state/` ~5 GB / ~77k files can stall naive globbing | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit filenames/globs. |
| Phase 272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` clone treadmill | **CLOSED.** Do not implement/seal/advance Phase 292+. |
| `hedge_cost_bps` may be inert in the EVAL-09 engine | **OPEN — carried into EVAL-11.** `hedge_cost_bps=0` and `=10` gave identical aggregate returns; verify before building a cost-bps axis in the optimizer; vary `cost_budget_bps` / `toxicity_threshold` / `target_delta_usd` instead if inert and document it. |

**Tree verified 2026-11-13T00:02:49Z:** EVAL-02/03/06/07/08/09/10 sealed with artifacts present; `src/analytics/eval10_final_gonogo.py` and `tests/test_eval10_final_gonogo.py` present; `.env` absent. Modified this session: `src/analytics/eval10_final_gonogo.py` (new), `tests/test_eval10_final_gonogo.py` (new). No active blockers besides executing EVAL-11.

---

## P0 SAFETY — CLEAR

- `.env` **ABSENT**. `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO network calls to exchanges, NO NEXT9 unblock.**

---

## SCOPE & HARD GUARDS (non-negotiable)

- **Allowed:** `src/`, `scripts/`, `tests/`, `research_state/` (explicit files only). Additive, deterministic, bounded, paper-only, guarded.
- **Forbidden:** live trading, `.env` creation, venue/config/credential mutation, NEXT9 unblock, any new `phaseNN_*_post_attribution_seal_orchestrator` wrapper, refactoring sealed legacy phases, and enumerating `research_state/` or running the full 865-file test suite.
- Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`.

---

## HANDOFF DISCIPLINE

- Replace stale state in place with verified facts/timestamps/paths/commands; no duplicate READ FIRST blocks.
- Work the queue strictly in order: EVAL-11 (ACTIVE) → EVAL-12 (queued).
- Each task must ship a real module, a numeric-invariant test file, a CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If context/time runs out: commit/push the partial new module and leave this file pointing at the exact next line to write. Never leave the tree clean with the task "pending."
- A final response containing only "verified env / will start next session" is a **failed session**.
- Final responses must not ask follow-up questions.
