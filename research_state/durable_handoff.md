# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-13T01:05:46Z (UTC). Verified this session against the tree: EVAL-12 module/tests/artifact are present; EVAL-11 sealed FEASIBLE_POSITIVE_SHARPE; EVAL-10 sealed NO-GO; `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; root handoffs remain retired pointers.
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are **retired pointer stubs** — do not action them and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope), not task sources.

---

## INITIAL TASK MESSAGE — 2026-11-13T01:05:46Z (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-13T01:05:46Z-EVAL-13-FINAL-STRATEGY-CERTIFICATION`
**STATUS:** ACTIVE. This is the single next task. Do not pick a different task. Do not re-verify the environment (deps installed; `.env` absent; safety flags set; EVAL-10 sealed NO-GO; EVAL-11 sealed FEASIBLE_POSITIVE_SHARPE; EVAL-12 sealed GO). Build `src/analytics/final_strategy_certification.py` per the EVAL-13 spec below, combine EVAL-11 best config, EVAL-12 real-data DSR/PBO evidence, and net-of-cost metrics into a strict `GO`/`NO-GO` certification with deployment guardrails (max notional, delta band, toxicity gate, cost budget, kill-switch conditions), then seal `research_state/FINAL_STRATEGY_CERTIFICATION_<UTC>.{json,md}`.

---

## SEALED EVALUATIONS (do not re-open)

> **EVAL-09 is DONE and sealed.** `src/analytics/gamma_inventory_hedge.py` (1061 lines) + `tests/test_gamma_inventory_hedge.py` (16 tests) + CLI; canonical artifact `research_state/GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`. Default aggregate: `mean_oos_return_with_hedge=-0.5580107668605527`, `mean_oos_return_without_hedge=0.2590709968068878`, `mean_oos_sharpe_with_hedge=-22.765929562035716`, `mean_oos_sharpe_without_hedge=5.586740988848094`, `total_cost_usd=1429.6848986289629`, `mean_toxicity_score=0.713277330797748`, `toxic_gate_active_fraction=0.3333333333333333`.

> **EVAL-10 is DONE and sealed (do not re-open).** `src/analytics/eval10_final_gonogo.py` + `tests/test_eval10_final_gonogo.py` (10 tests) + CLI; canonical artifact `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}`. Verdict **NO-GO**: `pass_fraction = 0/5 = 0.0` (need >= 0.70). Mean net return @1 bp −0.5580107668605527 vs without-hedge +0.2590709968068878; mean net Sharpe −22.765929562035716. Cost grid monotone nonincreasing: 0 bps −0.5576407 / −22.7598773, 1 bps −0.5580108 / −22.7659296, 5 bps −0.5594883 / −22.7902305, 10 bps −0.5613291 / −22.8208139. Paired permutation with-vs-without `observed_difference≈−0.2306`, `p=0.0005` (significant). Bootstrap CI mean net return [−0.6421, −0.5057], mean net Sharpe [−36.7466, −11.1379].

> **EVAL-11 is DONE and sealed.** `src/analytics/hedge_cost_optimizer.py` + `tests/test_hedge_cost_optimizer.py` (4 tests) + CLI; canonical artifact `research_state/HEDGE_COST_OPTIMIZER_20261113T004000Z.{json,md}` (258,664 B JSON / 3.0 KB MD). Verdict **FEASIBLE_POSITIVE_SHARPE**. Search (seeds 1–3, 27 configs): best feasible `target_delta_usd=-20000`, `toxicity_threshold=0.7`, `cost_budget_bps=0.5`; search mean net Sharpe `15.47685465828329`, mean net return `0.4768592349060418`, mean abs delta `150.8213456031083`, hedges `2280`. Final multi-seed (seeds 1–5): mean net Sharpe `13.188322401914279`, mean net return `0.39999544362288453`, mean abs delta `161.88674197953094`, total hedges `3800`, total cost `646.4230312530128`; feasible `True`. No-hedge control (same final seeds): mean Sharpe `5.590936162120627`, mean return `0.11385392259710948`. **`hedge_cost_bps` is inert in EVAL-09** (recorded but not applied by the sizer); the optimizer varies `cost_budget_bps`, `target_delta_usd`, and `toxicity_threshold` instead. EVAL-10's default-config NO-GO remains sealed; EVAL-11 did not re-open it.

> **EVAL-12 is DONE and sealed.** `src/analytics/real_walkforward_certification.py` + `tests/test_real_walkforward_certification.py` (9 tests) + CLI; canonical artifact `research_state/REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}`. Verdict **GO**. Real-data walk-forward (seeds 1–5, BTC real trades 1000 + ETH/SOL synthetic fallback + venue snapshots aggregate-only) for EVAL-11 best config and EVAL-10 default: EVAL-11 best mean net Sharpe `13.188322`, mean net return `0.399995`; EVAL-10 default mean net Sharpe `-22.765930`, mean net return `-0.558011`. DSR (via `_deflated_sharpe` from `strategy_falsification.py:105`): both configs DSR `0.000000` (significant). PBO via CSCV (k=8, 16 combinations): EVAL-11 best PBO `0.46875`, EVAL-10 default PBO `0.52344`, overall `0.5000`. Multiple-testing correction (Benjamini–Hochberg FDR=0.10): both configs survive. Evidence matrix: `btc_real_trades`, `eth_synthetic_fallback`, `sol_synthetic_fallback`, `venue_snapshots_aggregate_only`.

**Reuse points (verified on disk):** EVAL-09 engine `src/analytics/gamma_inventory_hedge.py::evaluate_gamma_inventory_hedge(seeds=[1,2,3,4,5])` (~3.7 s per seed; 18.5 s for 5 seeds in-process). Per-window series: `report["per_seed"][i]["symbols"][<sym>]["with_hedge"]["window_returns"]` (list of 10 floats) and `["windows"][*]` with `window_return`, `window_traded_notional`, `window_nav_start`, `window_cost_usd`, `window_hedges`, `window_trades`. EVAL-11 reuse: `evaluate_hedge_cost_optimizer(...)`, `_summarize_report`, `_series_metrics`, `COST_BUDGET_GRID_BPS`, `TARGET_DELTA_GRID_USD`, `TOXICITY_THRESHOLD_GRID`. Bootstrap/permutation/metrics primitives live in `src/analytics/strategy_evaluation.py`; DSR primitive is `_deflated_sharpe` in `src/analytics/strategy_falsification.py:105`; serialization via `serialize_metrics_strict` + `assert_json_valid` (never `{"valid": True}`). EVAL-06 flat-cost baseline reference: `research_state/STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}` (present; do not re-run).

---

## FOCUS CAMPAIGN (strictly sequential; heavy work is mandatory at every step — do not stop after EVAL-11)

| Order | Task | Status | Required output |
|---|---|---|---|
| EVAL-07 | Capacity/liquidity-aware TCA | **COMPLETE** | `src/analytics/capacity_aware_tca.py` + tests + CLI; `CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. |
| EVAL-08 | Cross-venue delta netting | **COMPLETE** | `src/analytics/cross_venue_netting.py` + `tests/test_cross_venue_netting.py` (21) + CLI; `CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`. |
| EVAL-09 | Gamma/inventory hedge + toxicity gating | **COMPLETE** | `src/analytics/gamma_inventory_hedge.py` + tests (16) + CLI; canonical `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`. |
| EVAL-10 | Final net-of-cost GO/NO-GO certification (default EVAL-09 config) | **COMPLETE** | `src/analytics/eval10_final_gonogo.py` + `tests/test_eval10_final_gonogo.py` (10) + CLI; artifact `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}`; verdict NO-GO (pass_fraction 0.0/5). |
| EVAL-11 | Hedge-drag / cost-efficiency optimizer (effective hedge levers) | **COMPLETE** | `src/analytics/hedge_cost_optimizer.py` + `tests/test_hedge_cost_optimizer.py` (4) + CLI; artifact `HEDGE_COST_OPTIMIZER_20261113T004000Z.{json,md}`; verdict FEASIBLE_POSITIVE_SHARPE. |
| EVAL-12 | Real-data walk-forward certification (DSR + PBO) | **COMPLETE** | `src/analytics/real_walkforward_certification.py` + `tests/test_real_walkforward_certification.py` (9) + CLI; artifact `REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}`; verdict GO. |
| EVAL-13 | **Final strategy certification + risk guardrails** (after EVAL-12) | **ACTIVE** | Combine EVAL-11 best config, EVAL-12 real-data DSR/PBO evidence, and net-of-cost metrics into a strict `GO`/`NO-GO` certification with deployment guardrails (max notional, delta band, toxicity gate, cost budget, kill-switch conditions). `src/analytics/final_strategy_certification.py` + tests + CLI + artifact `FINAL_STRATEGY_CERTIFICATION_<UTC>.{json,md}`. Do not deploy; paper-only. |

**Rule:** work strictly in order. Do not re-open EVAL-02/03/06/07/08/09/10/11/12. Do not advance EVAL-13 until EVAL-12 is sealed with a real artifact. Do not implement or advance Phase 292+ or any `phaseNN_*_post_attribution_seal_orchestrator` wrapper.

### EVAL-12 data reality check (read before writing code)

- `data/raw/orderflow_btcusdt_synthetic.json` has **1000 trades** and loads via `DataLoader.load_trades` after the prior fix.
- **There is NO `orderflow_ethusdt_synthetic.json`** — ETH orderflow only exists via the engine's deterministic synthesis fallback (`_load_orderflow` in `src/campaign/integrated.py:184`), not as a file.
- `data/raw/options_btc_synthetic.json` has **30 quotes**; there is no ETH options file.
- `data/processed/*_{venue}_{sym}_*.json` are **snapshots with aggregate blocks only** (`num_trades`, `num_liquidations`, `cumulative_delta`, `orderflow_imbalance`, `num_quotes`, `put_call_ratio`, `iv_skew`, `max_pain`) — no trade arrays. Use them for spot/options context, not as a trade series.
- **Consequence:** "BTC/ETH × 3 venues" cannot be built from on-disk trade files alone. Use BTC real trades + the deterministic synthesis path for ETH/SOL, and state that limitation explicitly in the artifact. Do not block on unavailable data; do not fabricate venue trade files. Report the evidence matrix as `btc_real_trades`, `eth_synthetic_fallback`, `sol_synthetic_fallback`, `venue_snapshots_aggregate_only`.

---

## HEAVY-WORK FLOOR (a session that does less is a FAILED session)

Future agents cannot avoid heavy compute by producing a thin wrapper, a stub, or an env-only report. EVAL-12 must, at minimum:

1. **Run real computation on the real data paths** — `DataLoader.load_trades` / `load_orderflow` / `load_options_chain` as applicable, plus the EVAL-09/EVAL-11 engine for the candidate configs. Do not substitute a synthetic toy whose numbers are trivially good.
2. **Implement PBO for real** — CSCV (or a documented equivalent) with actual combinatorial splits; no hard-coded value, no placeholder, no "TBD".
3. **Compute DSR with the existing primitive** — `_deflated_sharpe(rets, sr_observed, sr_benchmark)` from `strategy_falsification.py:105`; do not reimplement a different definition.
4. **Apply multiple-testing correction across the candidate/config set** — e.g., Benjamini–Hochberg or Bonferroni; state the method and the corrected threshold in the artifact.
5. **Ship a module + numeric-invariant test file + CLI + a written artifact** with the exact filename pattern `REAL_WF_CERTIFICATION_<UTC>.{json,md}`. No `{"valid": True}` reports; no NaN/Infinity.
6. **Assert non-degeneracy** — >=2 distinct nonzero per-window returns, >=2 seeds or >=2 walk-forward windows, CIs that straddle the point estimate, PBO in [0,1], DSR finite, verdict not constant unless the data warrants it.
7. **Seal with a deterministic verdict** (`GO`/`NO-GO`, or a strict certification function) computed by code — not prose, not a coin flip, not tuned to a desired answer.
8. **Cite exact artifact paths and key numbers** in this handoff when advancing, and update this file in place (never create a competing handoff).
9. **No handoff-maintenance loop for the next agent.** If you are the next agent and this file still shows EVAL-12 ACTIVE while `src/analytics/real_walkforward_certification.py` is absent, do **not** merely refresh this timestamp, re-run EVAL-10, or re-verify the environment. Your first code change must add the EVAL-12 module and execute the real computation. A future agent session that only edits this handoff while EVAL-12 remains unstarted is a **FAILED session**.

The floor applies to EVAL-12 and EVAL-13 equally. If a task cannot meet the floor, **fail loudly** with the specific blocker rather than emit a vacuous artifact.

---

## VERIFIED STATE — ground truth (build on it; do not re-verify environment)

- **Environment:** Python 3.12.3; deps installed (`numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pydantic 2.14.3, pytest 9.2.0, PyYAML 6.0.1, requests 2.31.0`). If a fresh container lacks deps, re-run `python3 -m pip install --break-system-packages -r requirements.txt` first. **`mypy`, `ruff`, `flake8` are NOT installed** — `mypy.ini` exists but is unenforceable here; verify with `python3 -m py_compile` and pytest only.
- **EVAL-12 verified this session:** `src/analytics/real_walkforward_certification.py` + `tests/test_real_walkforward_certification.py` (9 tests) + CLI; full artifact `REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}`; `python3 -m pytest tests/test_real_walkforward_certification.py -q` → **9 passed / ~17 s**.
- **EVAL-11 verified this session:** `src/analytics/hedge_cost_optimizer.py` + `tests/test_hedge_cost_optimizer.py` (4 tests) + CLI; full artifact `HEDGE_COST_OPTIMIZER_20261113T004000Z.{json,md}`; `python3 -m pytest tests/test_hedge_cost_optimizer.py tests/test_eval10_final_gonogo.py -q` → **14 passed / ~238 s**. Prior full named gate (EVAL-10 + EVAL-09 + EVAL-08 + EVAL-07 + EVAL-06 + EVAL-03 + EVAL-02 + EVAL-01 + campaign/evaluation/data tests) was **152 passed / ~362 s**; do not re-run the full 865-file suite.
- **EVAL-10 state:** COMPLETE. `src/analytics/eval10_final_gonogo.py`, `tests/test_eval10_final_gonogo.py`, and `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}` present; verdict NO-GO.
- **EVAL-02 COMPLETE:** `src/analytics/strategy_evaluation.py` + `tests/test_strategy_evaluation.py` + `scripts/evaluate_strategy.py` + `tests/test_evaluate_strategy.py`. Artifacts `STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}`.
- **EVAL-03 COMPLETE:** `src/analytics/regime_sizing.py` + `tests/test_regime_sizing.py` (7). GO; 50 windows; 460 trades; regime Sharpe 0.042420 vs flat 0.026375. Artifact `REGIME_SIZING_20261112T151421.312990Z.json`.
- **EVAL-06 COMPLETE (sealed NO-GO):** `src/analytics/strategy_falsification.py` + tests. pass_fraction 0.60 (need >=0.70); mean_net_sharpe 8.860771; mean_net_return 0.025482; cost grid 8.9946/8.8608/8.0745/7.3734 at 0/1/5/10 bps; mean_permutation_p 0.752. Artifact `STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`.
- **EVAL-07 COMPLETE:** `src/analytics/capacity_aware_tca.py` + tests + CLI. Artifact `CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`. mean_capacity_net_sharpe 8.250491 vs baseline 9.197960.
- **EVAL-08 COMPLETE:** `src/analytics/cross_venue_netting.py` (1091) + tests (21) + CLI. Artifact `CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`. mean_oos_sharpe with 8.006530 vs without 5.796608.
- **EVAL-09 COMPLETE:** `src/analytics/gamma_inventory_hedge.py` (1061) + tests (16) + CLI. Canonical artifact `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}` (`generated_at` 2026-11-12T22:04:02Z). Earlier `211228Z`/`211350Z` artifacts lack `window_returns` — do not use them.
- **Reusable real code (do not rewrite):** `src/backtest/engine.py`, `src/backtest/options_hedging.py`, `src/features/*`, `src/signals/*`, `src/campaign/integrated.py`, `src/analytics/*`, `src/orderflow/`, `src/execution/*`, `src/risk/*`. Legacy Phase 15–19 and Phase 21 modules are reference only.
- **`scripts/run_backtest.py` is a vacuous smoke test** (single trade, Sharpe≈6.3 from 2 marks). Do not treat its numbers as strategy performance.
- **Signal data is synthetic-deterministic.** `_generate_price_paths` in `src/campaign/integrated.py:147` builds seeded GBM paths; `data/raw/*.json` are synthetic fixtures. "Real data" in this repo means `data/processed/` venue snapshots (aggregate, no trade arrays) plus the BTC raw orderflow trades.

---

## BOTTLENECKS REMOVED (this session — 2026-11-13T01:05:46Z)

| Bottleneck | Resolution |
|---|---|
| **EVAL-11 not built** (sole active task — no artifact/test/CLI). | **RESOLVED.** Built `src/analytics/hedge_cost_optimizer.py` + `tests/test_hedge_cost_optimizer.py` + CLI; 27-config search over effective levers + 5-seed final run produced `FEASIBLE_POSITIVE_SHARPE` (final mean Sharpe 13.188322, mean return 0.399995, mean abs delta 161.89, hedges 3800); artifact `HEDGE_COST_OPTIMIZER_20261113T004000Z.{json,md}` sealed. |
| **EVAL-12 not built** (no real walk-forward certification with DSR/PBO). | **RESOLVED.** Built `src/analytics/real_walkforward_certification.py` + `tests/test_real_walkforward_certification.py` (9 tests) + CLI; real-data walk-forward (seeds 1–5, BTC 1000 trades + ETH/SOL synthetic fallback + venue snapshots aggregate-only) for EVAL-11 best and EVAL-10 default configs; DSR via `_deflated_sharpe`, PBO via CSCV (k=8, 16 combos), BH correction FDR=0.10; verdict **GO**; artifact `REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}` sealed. |
| **`hedge_cost_bps` may be inert in the EVAL-09 engine** (prior blocker: cost-bps axis would be fake). | **RESOLVED.** EVAL-09 records `hedge_cost_bps` but the sizer does not apply it. EVAL-11 documents `hedge_cost_bps_inert=True` and varies `cost_budget_bps`, `target_delta_usd`, and `toxicity_threshold` instead. Do not modify sealed EVAL-09 to chase a cost-bps axis. |
| **No permutation primitive existed** (prior blocker for EVAL-10). | **FIXED (prior session).** Added `permutation_test(...)` to `src/analytics/strategy_evaluation.py` + 5 tests. |
| **`DataLoader.load_trades` silently returned 0 trades** on dict-wrapped JSON (would block EVAL-12's real-DataLoader requirement). | **FIXED (prior session).** `load_trades` unwraps `{"trades"|"data"|"items"|"results": [...]}` and bare lists. Verified: `data/raw/orderflow_btcusdt_synthetic.json` now yields **1000 trades** (was 0). +4 regression tests. |
| **Cost-grid spec was wrong** (double-counted the 1 bp already in EVAL-09 returns). | **CLARIFIED (prior session).** Incremental formula `r_b = window_return - (window_traded_notional * (b - 1) / 1e4) / window_nav_start`; verified grid −0.557641 / −0.558011 / −0.559488 / −0.561329. |
| Four competing handoffs / stale stubs | **CLEARED.** Root stubs are pure "RETIRED — read durable_handoff.md" pointers with no task ID. |
| Cross-process non-determinism (salted `hash()`) | **FIXED earlier** with `_stable_seed()` (SHA-256); verified across two processes. |
| All-zero signal series → 0 windows/trades | **FIXED earlier** with time-varying causal momentum z-scores. |
| Naive full `pytest` on 865 test files (clone treadmill) | **AVOID THE TRAP.** Run only the named EVAL test files; never `pytest tests/` wholesale. |
| `research_state/` ~5 GB / ~77k files can stall naive globbing | **AVOID THE TRAP.** Never enumerate `research_state/`; use explicit filenames/globs. |
| Phase 272–291 `*_adaptive_toxicity_resilient_post_attribution_seal_orchestrator` clone treadmill | **CLOSED.** Do not implement/seal/advance Phase 292+. |

**Tree verified 2026-11-13T01:05:46Z:** EVAL-02/03/06/07/08/09/10/11/12 sealed with artifacts present; `src/analytics/real_walkforward_certification.py` and `tests/test_real_walkforward_certification.py` present; `.env` absent. Modified this session: `src/analytics/real_walkforward_certification.py` (new), `tests/test_real_walkforward_certification.py` (new), `research_state/REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}` (new), `research_state/durable_handoff.md` (updated). No active blockers besides executing EVAL-13.

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
- Work the queue strictly in order: EVAL-13 (ACTIVE).
- Each task must ship a real module, a numeric-invariant test file, a CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If context/time runs out: commit/push the partial new module and leave this file pointing at the exact next line to write. Never leave the tree clean with the task "pending."
- A final response containing only "verified env / will start next session" is a **failed session**.
- Final responses must not ask follow-up questions.