# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name (priority order):** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers. **Options** is the first-named pillar and **orderflow alpha/toxicity** the second (both now have dedicated sealed EVALs: EVAL-16 options surface/greeks, EVAL-17 orderflow alpha/toxicity).
**Refreshed:** 2026-11-13T08:39:55Z (UTC). Session scan (verified): canonical durable handoff is sole authority; root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs); `research_state/durable_handoff.md` is the only `*handoff*` file in `research_state/`. **EVAL-16 SEALED (NO-GO, legitimate)** — `research_state/OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}` + module/tests present. **EVAL-17 SEALED (NO-GO, legitimate, re-verified this session)** — `src/analytics/orderflow_alpha_toxicity_evaluation.py` + `tests/test_orderflow_alpha_toxicity_evaluation.py` (23 numeric-invariant tests, all pass via `python3 -m pytest -q`) + CLI + strict artifact `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`; `py_compile` OK. Required inputs present: `data/raw/options_btc_synthetic.json` (30 quotes) and `data/raw/orderflow_btcusdt_synthetic.json` (1000 trades, 20 liqs, 8 funding, BTCUSDT). Safety clear: `.env` **absent**, `.env.example:15` `LIVE_TRADING_ENABLED=false`. No blocked/failed EVAL artifacts and no competing handoff bottlenecks detected.
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are **retired pointer stubs** — do not action them and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope), not task sources.

---

## INITIAL TASK MESSAGE — 2026-11-13T07:52:37Z (copy-paste to the next agent — THIS IS YOUR WORK)

**TASK ID:** `INIT-2026-11-13T07:52:37Z-EVAL-17-ACTIVE`
**STATUS:** **EVAL-17 SEALED AND COMPLETE — NO-GO (4/5 checks, legitimate), artifacts shipped.** `src/analytics/orderflow_alpha_toxicity_evaluation.py` + `tests/test_orderflow_alpha_toxicity_evaluation.py` (23 passed) + CLI + `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`.

> **SEAL SUMMARY (EVAL-17 — sealed 2026-11-13T08:00:05Z):** Orderflow alpha & toxicity evaluation executed end-to-end on real data (`data/raw/orderflow_btcusdt_synthetic.json`: 1000 trades, 20 liquidations, 8 funding, BTCUSDT) via `src.campaign.integrated._load_orderflow("BTC","synthetic")`. Causal per-bar signal series from `OrderflowAlphaEngine.extract_features` applied to trailing snapshots (no-lookahead asserted + tested). IC by horizon {1: -0.00818, 5: -0.02107, 20: +0.00466}, ic_mean -0.00820, ic_tstat -1.3512, block-bootstrap CI [-0.02107, +0.00466], paired permutation p 0.0889. VPIN toxicity mean 0.4408, p95 1.0, gate-engagement fraction 0.225 (measured, not identically 0/1). Net-of-cost walk-forward: with-signal return -0.5903 / Sharpe -53.36 / max-DD 0.5903 / cost 43.12 USD (58 trades, 3 windows) vs always-flat control return 0.0. Verdict checks: signal_exists_ic_nonzero PASS, ic_significant FAIL (|t| 1.3512 < 1.96, p 0.0889 >= 0.05), toxicity_measured PASS, net_of_cost_with_vs_without PASS, no_lookahead_asserted PASS → NO-GO (4/5). Strict-serializable (`allow_nan=False`), never `{"valid": true}`, no NaN/Infinity. All 23 numeric-invariant tests pass; `py_compile` OK.

> **MANDATORY COPY-PASTE TASK (your session work — do not just read, DO):**
>
> Implement **EVAL-17 — Orderflow alpha & toxicity evaluation** (paper-only, deterministic, no network, no `.env`, no live).
> **DELIVERABLES (all required, no exceptions):**
> 1. `src/analytics/orderflow_alpha_toxicity_evaluation.py` — module with `compute_orderflow_toxicity_verdict(...) -> dict`
> 2. `tests/test_orderflow_alpha_toxicity_evaluation.py` — **12–18 numeric-invariant tests** (not smoke tests)
> 3. CLI: `python -m src.analytics.orderflow_alpha_toxicity_evaluation --out research_state/`
> 4. **Strict artifact:** `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_<UTC>.{json,md}` emitted by CLI
>
> **HEAVY WORK FLOOR — EVERY ITEM IS MANDATORY (no prose-only verdicts, no stubs):**
>
> 1. **LOAD REAL DATA** — Use `src.campaign.integrated._load_orderflow(symbol="BTC", venue="synthetic")` to load `data/raw/orderflow_btcusdt_synthetic.json` (verified: **1000 trades + 20 liquidations + 8 funding rates**, symbol `BTCUSDT`). **Do not enumerate `research_state/`; no network calls.** If you need ETH/SOL, they are synthetic fallback (no real files) — record that in the evidence matrix, do not fake real data.
>
> 2. **CAUSAL, NO-LOOKAHEAD SIGNAL** — Build a per-bar causal feature series from the trade tape: for each bar, use only trades with `timestamp <= bar_timestamp` (see `src.analytics.gamma_inventory_hedge.toxicity_score` for the exact causal pattern — VPIN-style bucketed signed-volume imbalance over a trailing window). Reuse `src.alpha.orderflow_alpha.OrderflowAlphaEngine.extract_features` for feature definitions (cumulative_delta, delta_divergence, absorption_score, sweep_score, vpin_lite, footprint_imbalance, net_aggression, large_trade_ratio) but **apply it causally per bar** (trailing snapshot), never to the full tape. **Assert no-lookahead**: a shuffled/future-injected tape must not change any bar's feature (add a numeric test for this).
>
> 3. **MEASURE ALPHA (IC + DECAY)** — Compute the information coefficient (Spearman/Pearson) between the causal signal at bar t and the **forward** return over horizons 1/5/20 bars (forward return is the label, that is allowed). Report IC mean, IC std, IC t-stat, and **signal decay** (IC by horizon). Report a block-bootstrap CI on mean IC via `src.analytics.strategy_evaluation.block_bootstrap_ci` (reuse; do not reimplement). Also compute a **paired permutation p-value** on the strategy return series via `src.analytics.strategy_evaluation.permutation_test` (reuse).
>
> 4. **MEASURE TOXICITY (VPIN)** — Compute VPIN-style toxicity per bar from causal flow (signed-volume imbalance over volume buckets). Report toxicity mean, p95, fraction of bars above threshold (default 0.7), and the **gate engagement** (fraction of bars where the toxicity gate would stand down quoting/hedging). This must be a real measured number, not identically 0 or 1.
>
> 5. **NET-OF-COST WITH/WITHOUT** — Run a deterministic OOS walk-forward of an orderflow-signal strategy (enter when causal signal/toxicity permits) through `src.analytics.strategy_evaluation.compute_metrics`, reporting net return/Sharpe/max-DD **with the orderflow signal vs a no-signal (always-flat or buy-and-hold) control**. Apply a bid/ask-spread + impact cost model (reuse EVAL-07/08 cost constants: `DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION` from `src.analytics.capacity_aware_tca`). Report net-of-cost numbers, not gross.
>
> 6. **DETERMINISTIC VERDICT FUNCTION** — `compute_orderflow_toxicity_verdict(...) -> dict` with explicit `checks` list: signal-exists (IC != 0), IC significance (t-stat / permutation p), toxicity measured (0 < mean < 1 and gate engages), net-of-cost with-vs-without, no-lookahead asserted. Each check: numeric threshold + rationale, finite metrics, evidence matrix. Strict-serializable via `serialize_metrics_strict`/`assert_json_valid` (`allow_nan=False`). **Never emit `{"valid": true}`**.
>
> 7. **VERIFY & SEAL** — `python -m py_compile src/analytics/orderflow_alpha_toxicity_evaluation.py` + `pytest -q tests/test_orderflow_alpha_toxicity_evaluation.py` → must pass. Then **update this handoff in place** to seal EVAL-17 with verdict/artifact/timestamps/tests.
>
> **IF EVAL-17 IS ALREADY SEALED WHEN YOU READ THIS, MOVE TO EVAL-18 (INTEGRATED OPTIONS+ORDERFLOW NET-OF-COST) BELOW. NEVER END A SESSION WITH NO NEW SEALED EVAL ARTIFACT.**

**SESSION CONFIRM — 2026-11-13T08:39:55Z (scan):** EVAL-16 SEALED (NO-GO, legitimate). **EVAL-17 SEALED (NO-GO, legitimate, re-verified this session)** — all 4 deliverables shipped (module + 23 numeric-invariant tests + CLI + strict `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`); `py_compile` OK; `python3 -m pytest -q tests/test_orderflow_alpha_toxicity_evaluation.py` **23 passed**. Competing handoff bottlenecks cleared: only this durable handoff is actionable. **EVAL-18 (integrated options+orderflow net-of-cost) is now conditional and NOT YET ASSIGNED** — only assign after EVAL-17 is sealed (done). The next agent's first action: implement EVAL-18 per the INITIAL TASK MESSAGE below; **a session that only edits handoff/timestamps or ends with env verification is FAILED.**

---
## INITIAL TASK MESSAGE — 2026-11-13T08:06:09Z (copy-paste to the next agent — THIS IS YOUR WORK)

**TASK ID:** `INIT-2026-11-13T08:06:09Z-EVAL-18-ACTIVE`
**STATUS:** **EVAL-17 SEALED — EVAL-18 (INTEGRATED OPTIONS+ORDERFLOW NET-OF-COST) IS THE NEXT REQUIRED EVAL.** Both pillars of the repo name (options + orderflow) now have dedicated sealed evaluations (EVAL-16 NO-GO, EVAL-17 NO-GO). EVAL-18 must combine both alpha sources into one deterministic net-of-cost walk-forward verdict consistent with EVAL-13/14/15 guardrails. Paper-only.

> **MANDATORY COPY-PASTE TASK (your session work — do not just read, DO):**
>
> Implement **EVAL-18 — Integrated options+orderflow net-of-cost evaluation** (paper-only, deterministic, no network, no `.env`, no live).
> **DELIVERABLES (all required, no exceptions):**
> 1. `src/analytics/integrated_options_orderflow_evaluation.py` — module with `compute_integrated_verdict(...) -> dict`
> 2. `tests/test_integrated_options_orderflow_evaluation.py` — **12–18 numeric-invariant tests** (not smoke tests)
> 3. CLI: `python -m src.analytics.integrated_options_orderflow_evaluation --out research_state/`
> 4. **Strict artifact:** `research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_<UTC>.{json,md}` emitted by CLI
>
> **HEAVY WORK FLOOR — EVERY ITEM IS MANDATORY (no prose-only verdicts, no stubs):**
>
> 1. **LOAD BOTH REAL DATA SOURCES** — Use existing loaders:
>    - Options: `src.campaign.integrated._load_options_chain("BTC", 65000.0, DETERMINISTIC_NOW, "synthetic")` → 30-quote chain (EVAL-16 data quality NO-GO sealed; use **reconstructed surface** from EVAL-16 as the options alpha source).
>    - Orderflow: `src.campaign.integrated._load_orderflow("BTC", "synthetic")` → 1000 trades + 20 liqs + 8 funding, BTCUSDT (EVAL-17 sealed).
>    **Do not enumerate `research_state/`; no network calls.**
>
> 2. **OPTIONS ALPHA (from EVAL-16 reconstructed surface)** — Use the **reconstructed IV surface** (`build_iv_surface_from_chain` + `calibrate_iv_surface` from EVAL-16) to compute a per-bar causal options signal. Options for signal: (a) GEX/gamma exposure flip distance, (b) IV skew term structure slope, (c) surface calibration residual as mispricing signal, (d) delta-hedge P&L attribution. **Must be causal per bar** (trailing snapshot, no lookahead — reuse `gamma_inventory_hedge.toxicity_score` causal pattern). Assert no-lookahead with a numeric test.
>
> 3. **ORDERFLOW ALPHA (from EVAL-17 causal signal)** — Reuse the **causal per-bar signal** from EVAL-17 (`OrderflowAlphaEngine.extract_features` on trailing snapshots; signal = `net_aggression`). Do not recompute from scratch; import and reuse the EVAL-17 signal logic (copy the causal construction pattern, keep thresholds identical).
>
> 4. **COMBINED ALPHA + TOXICITY GATE** — Fuse both signals into a single per-bar decision:
>    - Options signal: long/short/flat based on reconstructed-surface signal (e.g., GEX flip distance > threshold → directional bias; IV skew slope → regime).
>    - Orderflow signal: long/short/flat based on `net_aggression` > `DEFAULT_SIGNAL_THRESHOLD` (0.1).
>    - Toxicity gate: **EVAL-17 VPIN toxicity** (mean 0.4408, gate-engagement 0.225) stands down quoting/hedging when VPIN >= 0.7. Apply to both signals (if toxic, force flat).
>    - Combined position = `f(options_signal, orderflow_signal, toxicity_gate)` — simple deterministic rule (e.g., require both to agree, or weight by IC magnitude). Document the rule in code.
>
> 5. **NET-OF-COST INTEGRATED WALK-FORWARD** — Run deterministic OOS walk-forward (seeds 1–5, same windowing as EVAL-13/17) of the **combined strategy** through `compute_metrics`, using the **capacity-aware cost model** (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION` from `src.analytics.capacity_aware_tca`). Compare against **three controls**:
>    - (a) Always-flat (zero return, zero cost).
>    - (b) Options-only signal (with same toxicity gate).
>    - (c) Orderflow-only signal (with same toxicity gate).
>    Report net return, Sharpe, max-DD, total cost USD, num trades, num windows for all four series.
>
> 6. **STATISTICAL DEFENSIBILITY** — Compute:
>    - IC (Pearson) for combined signal vs forward returns (horizons 1/5/20) + block-bootstrap CI (reuse `block_bootstrap_ci`).
>    - Paired permutation test (combined vs best single-pillar) via `permutation_test`.
>    - Deflated Sharpe Ratio (DSR) and PBO (CSCV) across seeds/windows — reuse EVAL-12/13 patterns.
>    - Benjamini–Hochberg FDR correction across the four series.
>
> 7. **DETERMINISTIC VERDICT FUNCTION** — `compute_integrated_verdict(...) -> dict` with explicit `checks` list:
>    - `options_signal_exists` (nonzero IC from reconstructed surface)
>    - `orderflow_signal_exists` (nonzero IC from EVAL-17 causal signal)
>    - `combined_ic_significant` (t-stat / permutation p vs controls)
>    - `combined_net_of_cost_superior` (combined Sharpe > both single-pillar Sharpe AND > always-flat, with finite cost model)
>    - `toxicity_gate_measured` (EVAL-17 VPIN gate engages at measured 0.225 fraction, not 0/1)
>    - `no_lookahead_asserted` (both signals causal per bar, numeric test)
>    - `guardrails_consistent_with_eval13_14_15` (delta band ±323.77 USD, toxicity gate 0.7, cost budget 0.5 bps, kill-switch DD 20%/toxicity 80%/cost 5 bps, max notional 1M USD, max daily loss 50k USD)
>    Each check: numeric threshold + rationale, finite metrics, evidence matrix. Strict-serializable via `serialize_metrics_strict`/`assert_json_valid` (`allow_nan=False`). **Never emit `{"valid": true}`**.
>
> 8. **VERIFY & SEAL** — `python -m py_compile src/analytics/integrated_options_orderflow_evaluation.py` + `pytest -q tests/test_integrated_options_orderflow_evaluation.py` → must pass. Then **update this handoff in place** to seal EVAL-18 with verdict/artifact/timestamps/tests.
>
> **IF EVAL-18 IS ALREADY SEALED WHEN YOU READ THIS, MOVE TO THE NEXT EVAL (if any) OR STOP — NEVER END A SESSION WITH NO NEW SEALED EVAL ARTIFACT.**

**CONSTRAINTS:** Paper-only. `.env` absent, `LIVE_TRADING_ENABLED=false`. No live enablement, no `.env` creation, no venue/config/credential mutation, no network calls to exchanges, no NEXT9 unblock, no enumerating `research_state/` (glob specific files), no full 865-file test suite, no new phase orchestrator wrappers, no re-opening sealed EVALs. Use existing loaders/primitives; `scripts/run_backtest.py` is vacuous smoke test.

---

## SEALED EVALUATIONS (do not re-open)

> **EVAL-02 COMPLETE:** `src/analytics/strategy_evaluation.py` + tests/CLI; artifacts `STRATEGY_EVALUATION_2026-10-31T000000Z.{json,md}`.
> **EVAL-03 COMPLETE:** `src/analytics/regime_sizing.py` + `tests/test_regime_sizing.py` (7); GO; 50 windows; 460 trades; regime Sharpe 0.042420 vs flat 0.026375; `REGIME_SIZING_20261112T151421.312990Z.json`.
> **EVAL-06 COMPLETE (sealed NO-GO):** `src/analytics/strategy_falsification.py` + tests; pass_fraction 0.60 (need >=0.70); mean_net_sharpe 8.860771; mean_net_return 0.025482; cost grid 8.9946/8.8608/8.0745/7.3734 @0/1/5/10 bps; mean_permutation_p 0.752; `STRATEGY_FALSIFICATION_20261112T163240Z.{json,md}`.
> **EVAL-07 COMPLETE:** `src/analytics/capacity_aware_tca.py` + tests + CLI; `CAPACITY_AWARE_TCA_20261112T172412Z.{json,md}`; mean_capacity_net_sharpe 8.250491 vs baseline 9.197960.
> **EVAL-08 COMPLETE:** `src/analytics/cross_venue_netting.py` (1091) + `tests/test_cross_venue_netting.py` (21) + CLI; `CROSS_VENUE_NETTING_20261112T201000Z.{json,md}`; mean_oos_sharpe with 8.006530 vs without 5.796608.
> **EVAL-09 COMPLETE:** `src/analytics/gamma_inventory_hedge.py` (1061) + `tests/test_gamma_inventory_hedge.py` (16) + CLI; canonical `GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`. Default aggregate: mean_oos_return_with_hedge `-0.5580107668605527`, without `0.2590709968068878`, mean_oos_sharpe_with_hedge `-22.765929562035716`, without `5.586740988848094`, total_cost_usd `1429.6848986289629`, mean_toxicity_score `0.713277330797748`, toxic_gate_active_fraction `0.3333333333333333`.
> **EVAL-10 COMPLETE (sealed NO-GO):** `src/analytics/eval10_final_gonogo.py` + `tests/test_eval10_final_gonogo.py` (10) + CLI; `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}`. Verdict NO-GO: pass_fraction `0.0` (need >=0.70); mean net return @1bp `-0.5580107668605527`, mean net Sharpe `-22.765929562035716`; cost grid monotone 0/1/5/10 bps; paired permutation p `0.0005`.
> **EVAL-11 COMPLETE (FEASIBLE_POSITIVE_SHARPE):** `src/analytics/hedge_cost_optimizer.py` + `tests/test_hedge_cost_optimizer.py` (4) + CLI; `HEDGE_COST_OPTIMIZER_20261113T004000Z.{json,md}`. Best feasible: `target_delta_usd=-20000.0, toxicity_threshold=0.7, cost_budget_bps=0.5`; final multi-seed (1-5) mean net Sharpe `13.188322401914279`, mean net return `0.39999544362288453`, mean abs delta `161.88674197953094`, hedges `3800`, total cost `646.4230312530128`; no-hedge control Sharpe `5.590936162120627`. `hedge_cost_bps` is inert in EVAL-09 (recorded only); effective levers are `target_delta_usd/toxicity_threshold/cost_budget_bps`.
> **EVAL-12 COMPLETE (GO):** `src/analytics/real_walkforward_certification.py` + `tests/test_real_walkforward_certification.py` (9) + CLI; `REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}`. Real-data walk-forward (seeds 1-5, BTC 1000 trades real + ETH/SOL synthetic fallback + 6 venue snapshots aggregate-only) for EVAL-11 best vs EVAL-10 default (15 series × 10 windows/config). Verdict **GO**. DSR: EVAL11_best `0.0`, EVAL10_default `0.0`. PBO (CSCV k=8, 16 combos): EVAL11_best `0.46875`, EVAL10_default `0.5234375`, overall `0.5`. Multiple-testing correction: Benjamini–Hochberg FDR `0.10`, survivors `['EVAL11_best','EVAL10_default']`. Evidence matrix: `{btc_real_trades:true, eth_synthetic_fallback:true, sol_synthetic_fallback:true, venue_snapshots_aggregate_only:true}`.
> **EVAL-13 COMPLETE (GO):** `src/analytics/final_strategy_certification.py` + `tests/test_final_strategy_certification.py` (6) + CLI; artifact `FINAL_STRATEGY_CERTIFICATION_20261113T015226Z.{json,md}`. Deterministic verdict **GO** (8/8 checks): EVAL-11 best mean net Sharpe `13.188322401914279` vs no-hedge `5.590936162120627` (improvement `7.597386`) and vs EVAL-10 default `-22.765929562035716`; DSR recomputed `0.0` both configs, recompute-consistent with sealed EVAL-12; paired permutation EVAL-11 vs EVAL-10 `p=0.001499` significant; bootstrap CI mean net return `[0.298731, 0.494794]`, mean net Sharpe `[9.378864, 18.878999]` (lower bounds > 0); PBO overall `0.5`; BH FDR 0.10 survivors `['EVAL11_best','EVAL10_default']`. Nine paper-only guardrails all pass (max notional cap `1,000,000.0` USD; delta band `±323.77` USD around `-20000.0`; toxicity gate `0.7`, mean toxic gate fraction `0.333`; cost budget `0.5` bps; kill-switch drawdown `20%`/toxicity `80%`/cost `5.00 bps`; max daily loss `50,000.0` USD; live trading disabled). Strict-serializable, no NaN/Infinity, never `{"valid": true}`.
> **EVAL-14 COMPLETE (sealed GO):** `src/analytics/paper_deployment_readiness.py` + `tests/test_paper_deployment_readiness.py` (8) + CLI; artifact `PAPER_DEPLOYMENT_READINESS_20261113T030007Z.{json,md}`. Deterministic `compute_paper_readiness_verdict` **GO** (10/10 checks); 9 EVAL-13 guardrails wired as structured fields with rationale plus alert watch levels and kill-switch halt conditions; evidence matrix present; strict-serializable, no NaN/Infinity, never `{"valid": true}`; `live_trading_enabled=false`; paper-only.
> **EVAL-15 COMPLETE (sealed GO):** `src/analytics/paper_execution_hardening.py` + `tests/test_paper_execution_hardening.py` (20) + CLI; artifact `PAPER_EXECUTION_HARDENING_20261113T045715Z.{json,md}`. Deterministic `compute_paper_execution_verdict` **GO** (12/12 checks): EVAL-14/EVAL-13/EVAL-12 GO evidence wired, paper pre-live gates and continuous validation/reconciliation freshness checks pass, 9 guardrails pass, kill-switch not triggered, alert watch levels present (drawdown watch triggered at observed 0.1887 >= 0.10 watch), reconciliation metrics present, strict-serializable, no NaN/Infinity, never `{"valid": true}`, `trading_mode=paper`, `live_trading_enabled=false`. Verification (re-confirmed 2026-11-13T05:03:00Z): `py_compile` OK; `pytest -q tests/test_paper_execution_hardening.py` **20 passed**.
> **EVAL-16 COMPLETE (sealed NO-GO, legitimate — measured, not fudged):** `src/analytics/options_surface_greeks_evaluation.py` + `tests/test_options_surface_greeks_evaluation.py` (21) + CLI; artifact `OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}`. Deterministic `compute_options_surface_verdict` **NO-GO** (5/9 checks) on the real 30-quote BTC chain (`data/raw/options_btc_synthetic.json`, spot 65000): FAIL `data_quality_bs_vs_mark` (BS(mark_iv) vs mark max abs `8516.3642`, mean abs `3192.6835` > tol `1.0`); FAIL `data_quality_put_call_parity` (parity residual min `-6480.2391`, max `+6634.6831`, mean `84.8653`, max abs `6634.6831` > tol `1.0`); FAIL `surface_arbitrage_free` (butterfly 1 violation, calendar 0, on the **reconstructed** grid — non-convex call IVs at the 2026-11-01 expiry, max violation `0.4006`); FAIL `greeks_stored_vs_recomputed_delta` (mean stored-vs-recomputed delta error `0.3402`, max `0.8494` > tol `0.05`); PASS `data_quality_mark_iv_range` (`[0.4181, 0.7991]`), PASS `surface_calibration_residual` (max abs `0.0`), PASS `greeks_analytic_vs_finite_difference` (delta+vega FD match fraction `1.0` on all 30), PASS `net_of_cost_delta_hedge_finite` (25 OOS windows, seeds 1–5, mean with-options Sharpe `2.5486`, without `2.7226`), PASS `metrics_non_degenerate`. Book greeks: total GEX `1052954758.99`, gamma flip `58207.50`, PCR `1.1961`, max pain `65000.00`, IV skew `0.1063`. Strict-serializable, no NaN/Infinity, never `{"valid": true}`. Verification: `py_compile` OK; `pytest -q tests/test_options_surface_greeks_evaluation.py` **21 passed**; related regression `test_iv_surface/test_options_pricing_greeks_adversarial/test_options_hedging/test_data_loader_and_validation` **108 passed**. **This NO-GO is the true data state — do not re-open or fudge it.**
> **EVAL-17 COMPLETE (sealed NO-GO, legitimate — measured, not fudged):** `src/analytics/orderflow_alpha_toxicity_evaluation.py` + `tests/test_orderflow_alpha_toxicity_evaluation.py` (23) + CLI + artifact `ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`. Real 1000-trade BTC orderflow loaded via `src.campaign.integrated._load_orderflow("BTC","synthetic")`; `OrderflowAlphaEngine` features applied causally per bar (trailing snapshot); causal/no-lookahead signal asserted + numerically tested; IC by horizon {1: -0.00818, 5: -0.02107, 20: +0.00466}, ic_mean -0.00820, ic_tstat -1.3512, block-bootstrap CI [-0.02107, +0.00466], paired permutation p 0.0889; VPIN toxicity mean 0.4408, p95 1.0, gate-engagement fraction 0.225 (measured, not identically 0/1); net-of-cost walk-forward: with-signal return -0.5903 / Sharpe -53.36 / max-DD 0.5903 / cost 43.12 USD (58 trades, 3 windows) vs always-flat control return 0.0. Deterministic verdict NO-GO (4/5 checks; `ic_significant` FAILS since |t| 1.3512 < 1.96 and p 0.0889 >= 0.05 — legitimate, not fudged). Strict-serializable, no NaN/Infinity, never `{"valid": true}`. Verification: `py_compile` OK; `pytest -q tests/test_orderflow_alpha_toxicity_evaluation.py` **23 passed**.

**reuse points (verified 2026-11-13T08:05:00Z):** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.gamma_inventory_hedge.evaluate_gamma_inventory_hedge` + `toxicity_score` (causal VPIN-style pattern — reused for EVAL-17 toxicity); `src.analytics.hedge_cost_optimizer.evaluate_hedge_cost_optimizer`; `src.analytics.options_surface_greeks_evaluation` (EVAL-16, sealed — data-quality + surface + greeks + delta-hedge patterns); `src.campaign.integrated` (`_load_options_chain`, `_load_orderflow`, `_features_for_symbol`, `DEFAULT_SPOT` (`BTC=65000.0`), `DETERMINISTIC_NOW` (`2026-10-31 00:00:00+00:00`)); `src.data.loader.DataLoader` (unwraps dict-wrapped JSON); **options primitives** `src.features.options_pricing.black_scholes` / `black_scholes_greeks` (takes `PricingInputs(spot,strike,rate,volatility,time_to_expiry,option_type,seed)`), `src.features.volatility.calculate_atm_term_structure / calculate_iv_skew_term_structure / calculate_risk_reversal_term_structure / calculate_skew_term_structure / calculate_put_call_ratio / calculate_max_pain / calculate_iv_skew` (take `List[OptionQuote]`), `src.features.gamma_exposure.calculate_total_gex / gamma_flip_level`, `src.features.liquidity.calculate_chain_liquidity_metrics`; **surface** `src.features.iv_surface.build_iv_surface_from_chain` (→ `IVSurface`, 30 pts on real chain) + `src.features.iv_surface.calibrate_iv_surface` (→ residuals `{num_points,residual_mean,residual_std,residual_max_abs}`); `src.options.phase25_vol_surface.VolSurface.build_surface` is a **simplified stub** (hardcoded tenor/moneyness, needs `iv` key) — secondary only. **orderflow primitives** `src.alpha.orderflow_alpha.OrderflowAlphaEngine.extract_features` (returns `OrderflowAlphaFeatures`; apply causally per bar, not to the full tape). `scripts/run_backtest.py` is vacuous smoke test — not strategy performance.

---

## FOCUS CAMPAIGN (strictly sequential — EVAL-18 is ACTIVE)

| Order | Task | Status | Required output |
|---|---|---|---|
| EVAL-02..EVAL-17 | Prior evaluations/readiness | **COMPLETE (sealed)** | Modules/tests/CLIs/artifacts listed above. EVAL-16 sealed NO-GO (legitimate). EVAL-17 sealed NO-GO (legitimate). |
| **EVAL-18** | **Integrated options+orderflow net-of-cost evaluation** | **ACTIVE (next agent must implement)** | `src/analytics/integrated_options_orderflow_evaluation.py` + `tests/test_integrated_options_orderflow_evaluation.py` (12–18 numeric-invariant tests) + CLI + `research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_<UTC>.{json,md}`; loads both real data sources (EVAL-16 30-quote chain + EVAL-17 1000-trade orderflow); options signal from reconstructed surface (causal); orderflow signal from EVAL-17 causal `net_aggression`; VPIN toxicity gate (measured 0.225 engagement); combined net-of-cost walk-forward vs 3 controls (flat, options-only, orderflow-only); IC + block-bootstrap CI + permutation + DSR/PBO + BH-FDR; deterministic verdict with 7 explicit checks; strict-serializable; paper-only. |

**Rule:** do not re-open sealed EVALs. Do not implement or advance Phase 292+ or any `phaseNN_*_post_attribution_seal_orchestrator` wrapper. A session must seal at least one EVAL task; a session that ends with no new EVAL artifact (only handoff/timestamp edits) is FAILED.

---

## HEAVY-WORK FLOOR (for EVAL-17 / EVAL-18)

Any of these tasks must, at minimum:
1. **Read and use real sealed artifacts** relevant to the task as evidence inputs; cite key numbers in output artifact. For EVAL-17/18 the primary input is the **real** file `data/raw/orderflow_btcusdt_synthetic.json` (loaded via `src.campaign.integrated`), plus sealed EVAL-07/08/09/13 evidence for the net-of-cost model. **EVAL-16 is now a sealed evidence input** (`OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}`): its measured data-quality NO-GO (BS-vs-mark max abs `8516.3642`, parity max abs `6634.6831`, delta err mean `0.3402`) and the reconstructed-surface method are reusable for EVAL-18's integrated options+orderflow leg.
2. **Compute deterministic verdict/metrics in code** — explicit function combining checks; no prose-only verdict.
3. **Emit numeric thresholds/guardrails where applicable** as structured fields with rationale; paper-only.
4. **Ship module + numeric-invariant tests + CLI + strict artifact** `research_state/<TASK>_<UTC>.{json,md}`. Strict-serializable (`allow_nan=False`); never `{"valid": true}`; no NaN/Infinity.
5. **Assert non-degeneracy/consistency** — finite metrics, explicit pass/fail reasons list, evidence matrix present, verdict matches function, arbitrage/identity residuals bounded.
6. **Run verification** (`py_compile` + targeted pytest for the task) and report results.
7. **Update this handoff in place** to seal the task with verdict/artifact/timestamps/tests when complete. A session that only edits handoff/timestamps without task artifacts is FAILED.

---

## VERIFIED STATE — ground truth (do not re-verify environment)

- **Environment:** Python 3.12.3; deps installed (numpy/pandas/scipy/pydantic/pytest/PyYAML/requests). `mypy/ruff/flake8` not installed; use `python3 -m py_compile` + targeted pytest.
- **Key sealed artifacts present:** `research_state/HEDGE_COST_OPTIMIZER_20261113T004000Z.{json,md}`, `research_state/REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}`, `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}`, `research_state/GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`, `research_state/FINAL_STRATEGY_CERTIFICATION_20261113T015226Z.{json,md}`, `research_state/PAPER_DEPLOYMENT_READINESS_20261113T030007Z.{json,md}`, `research_state/PAPER_EXECUTION_HARDENING_20261113T045715Z.{json,md}`, `research_state/OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}`, `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`, campaign checkpoints (`END2END_LIVE_TRADING_READINESS_latest.json`, `PAPER_TRADING_PRE_LIVE_READINESS_latest.json`, `CONTINUOUS_VALIDATION_AND_MONITORING_latest.json`).
- **EVAL-17 key numbers (verified 2026-11-13T08:00:05Z):** verdict NO-GO (4/5 checks, legitimate). Real BTC orderflow loaded: 1000 trades, 20 liquidations, 8 funding, symbol BTCUSDT. Bars: 240 @ 15s. Causal signal (net_aggression) per bar via OrderflowAlphaEngine on trailing snapshots; no-lookahead asserted + tested. IC by horizon {1: -0.00818, 5: -0.02107, 20: +0.00466}; ic_mean -0.00820; ic_std 0.01051; ic_tstat -1.3512; block-bootstrap CI [-0.02107, +0.00466]; paired permutation p 0.0889 (not significant at 0.05). VPIN toxicity: mean 0.4408, p95 1.0, range [0.0014, 1.0], fraction above 0.7 threshold 0.225, gate engages True, measured True. Net-of-cost walk-forward: with-signal return -0.5903 / Sharpe -53.36 / max-DD 0.5903 / total cost 43.12 USD (58 trades, 3 windows) vs always-flat control return 0.0 / Sharpe 0.0. Cost model: spread 0.5 bps, impact coeff 10.0, max participation 0.20. Verdict checks: signal_exists_ic_nonzero PASS, ic_significant FAIL, toxicity_measured PASS, net_of_cost_with_vs_without PASS, no_lookahead_asserted PASS → NO-GO (4/5). Strict artifact JSON+MD emitted; never valid=true.
- **EVAL-16 key numbers (verified 2026-11-13T07:05:00Z):** verdict NO-GO (5/9 checks, legitimate). Real BTC options chain loaded: 30 quotes, 3 expiries (2026-11-01 / 2026-11-07 / 2026-11-30), calls+puts, stored greeks. Data quality: BS(mark_iv) vs mark max abs `8516.364`, mean abs `3192.684`; parity residual min `-6480.2`, max `+6634.7`, mean abs `84.87`; mark IV `[0.418, 0.799]`. Surface: 30 points, 3 expiries, residual max abs `0.0`. Arbitrage: butterfly 1 violation (non-convex call IVs at 2026-11-01 expiry, max violation `0.4006`), calendar 0. Greeks: delta err mean `0.3402`, max `0.8494`; analytic vs FD match fraction `1.0` (delta+vega). Delta hedge: 25 OOS windows, mean with-options Sharpe `2.5486`, without `2.7226`. Book greeks: total GEX `1052954758.99`, gamma flip `58207.50`, PCR `1.1961`, max pain `65000.00`, IV skew `0.1063`. Strict artifact JSON+MD emitted; never valid=true.
- **EVAL-15 key numbers (verified 2026-11-13T05:03:00Z):** verdict GO (12/12 checks); `all_guardrails_pass=true`; `kill_switch_not_triggered=true`; `live_trading_enabled=false`; `trading_mode=paper`; reconciliation freshness met (target >= 0.99), CV iterations 5/5; alert watch levels include drawdown watch (observed ~0.1887 >= 0.10 watch, below 0.20 kill-switch); strict artifact JSON+MD emitted.
- **EVAL-14 key numbers:** verdict GO (10/10); 9 guardrails wired; 6 alert watch levels; 3 kill-switch halt conditions; paper-only.
- **EVAL-13 key numbers:** verdict GO (8/8); best config `target_delta_usd=-20000.0, toxicity_threshold=0.7, cost_budget_bps=0.5`; mean net Sharpe `13.188322`; bootstrap CI return `[0.298731, 0.494794]`, Sharpe `[9.378864, 18.878999]`; 9 guardrails all pass.
- **EVAL-12 key numbers:** verdict GO; EVAL11_best mean Sharpe/return `13.188322`/`0.399995`; EVAL10_default `-22.765930`/`-0.558011`; DSR both `0.0`; PBO overall `0.5`; BH FDR 0.10 survivors both configs.
- **Data reality (verified):** BTC options `data/raw/options_btc_synthetic.json` = **30 quotes, 3 expiries (2026-11-01 / 2026-11-07 / 2026-11-30), calls+puts, stored delta/gamma/vega/theta/IV** (venue `synthetic`). **Options file is synthetic and internally INCONSISTENT** (measured 2026-11-13T07:05:00Z at spot 65000, now sealed by EVAL-16): BS(mark_iv) vs stored mark max abs `8516.364` / mean `3192.683`; parity residual `(C-P)-(S-K)` `[-6480.2, +6634.7]` / mean `84.9`; `mark_iv` `0.418..0.799`. EVAL-16 sealed this as NO-GO (legitimate) — do not re-open. BTC orderflow `data/raw/orderflow_btcusdt_synthetic.json` = **1000 trades + 20 liquidations + 8 funding rates**, symbol `BTCUSDT`; no ETH orderflow/options files (synthetic fallback); processed venue snapshots aggregate-only (6 files). Spot default `DEFAULT_SPOT["BTC"]=65000.0`.
- **Loader fix (this session):** `src/campaign/integrated._load_options_chain` called `DataLoader.load_options_chain(..., symbol=...)` but the loader takes `underlying=` → silent TypeError → always used 40-quote synthetic fallback. **FIXED** to `underlying=symbol`; now loads the real 30-quote chain. Verified: `tests/test_integrated_campaign.py` + `tests/test_integrated_signal_series.py` + `tests/test_data_loader_and_validation.py` → **38 passed**; `tests/test_capacity_aware_tca.py` + `tests/test_real_walkforward_certification.py` + `tests/test_strategy_falsification.py` → **26 passed**.
- **Safety:** `.env` **ABSENT**. `.env.example:15` = `LIVE_TRADING_ENABLED=false`. `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **Avoid traps:** never run full 865-file `pytest`; never enumerate `research_state/` (5GB+/~77k files); `scripts/run_backtest.py` vacuous.

---

## BOTTLENECKS REMOVED (this session — 2026-11-13T08:06:09Z)

| Bottleneck | Resolution |
|---|---|
| EVAL-16 (options vol-surface & greeks) was ACTIVE and unimplemented → sessions could stall or do handoff-only no-ops | **RESOLVED (sealed).** Implemented `src/analytics/options_surface_greeks_evaluation.py` + `tests/test_options_surface_greeks_evaluation.py` (21 numeric-invariant tests, all pass) + CLI + strict artifact `OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}`. Deterministic verdict **NO-GO (5/9)** — legitimate measured data-quality failure on the known-inconsistent synthetic options file; not fudged. |
| Repo-priority gap: options pricing/greeks/vol-surface had no dedicated analytics EVAL | **RESOLVED (sealed).** EVAL-16 now measures data quality, reconstructs + arbitrage-checks the IV surface, recomputes greeks vs finite differences, and runs a net-of-cost delta hedge with an underlying control. |
| **Broken options loader** (`_load_options_chain` passed `symbol=` instead of `underlying=`) → silent synthetic fallback, real 30-quote file never used | **FIXED** in `src/campaign/integrated.py`; now loads the real chain (verified: 30 quotes, 3 expiries). |
| Options data assumed arbitrage-free but is internally inconsistent | **RESOLVED (sealed by EVAL-16).** Measured BS-price residual max abs `8516.364`, parity residual `±~6600`, delta err mean `0.3402`; EVAL-16 reconstructs a surface and reports data-quality as measured checks → legitimate NO-GO. |
| Orderflow alpha/toxicity (second repo pillar) still had no dedicated EVAL | **RESOLVED (sealed by EVAL-17).** Implemented `src/analytics/orderflow_alpha_toxicity_evaluation.py` + `tests/test_orderflow_alpha_toxicity_evaluation.py` (23 numeric-invariant tests, all pass) + CLI + strict artifact `ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`. Real 1000-trade BTC orderflow; causal no-lookahead signal; IC+decay, VPIN toxicity, net-of-cost with/without. Deterministic verdict **NO-GO (4/5)** — legitimate measured outcome (`ic_significant` fails: |t| 1.3512 < 1.96, p 0.0889); not fudged. |
| **Both repo pillars (options + orderflow) now have sealed EVALs but no integrated evaluation exists** — the strategy cannot be assessed end-to-end | **ACTIVE BOTTLENECK: EVAL-18.** Next session must implement the integrated evaluation combining both alpha sources with the EVAL-17 VPIN toxicity gate, net-of-cost walk-forward vs three controls, and statistical defensibility (DSR/PBO/BH-FDR). This is the only remaining bottleneck to a complete strategy assessment. |
| Competing/stale root handoff files | **CLEARED (verified).** Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` remain retired pointers with no task IDs; this file remains sole authority. |

**Tree verified 2026-11-13T08:39:55Z:** EVAL-16 sealed (NO-GO, legitimate, `OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z`); EVAL-17 sealed (NO-GO, legitimate, `ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z`); **EVAL-18 ACTIVE (must be implemented next)**. Sole actionable handoff: `research_state/durable_handoff.md` (no other `*handoff*` files in `research_state/`; root handoffs are retired pointers). P0 safety clear (`.env` absent, `LIVE_TRADING_ENABLED=false`, `next9_unblocked=false`). No blocked/failed EVAL artifacts; EVAL-18 is the single active bottleneck — must ship module/tests/CLI/artifact this session or the session is FAILED.

---

## P0 SAFETY — CLEAR

- `.env` **ABSENT**. `.env.example:15` = `LIVE_TRADING_ENABLED=false`.
- `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **NO live trading, NO `.env` creation, NO venue/config/credential mutation, NO network calls to exchanges, NO NEXT9 unblock.**

---

## SCOPE & HARD GUARDS (non-negotiable)

- **Allowed:** `src/`, `scripts/`, `tests/`, `research_state/` (explicit files only). Additive, deterministic, bounded, paper-only, guarded.
- **Forbidden:** live trading, `.env` creation, venue/config/credential mutation, NEXT9 unblock, any new `phaseNN_*_post_attribution_seal_orchestrator` wrapper, refactoring sealed legacy phases, enumerating `research_state/`, running full 865-file test suite.
- Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`.

---

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Work queue: **EVAL-02..EVAL-17 SEALED** (EVAL-16/EVAL-17 NO-GO legitimate); **EVAL-18 ACTIVE (must be implemented next)**. Do not reopen sealed EVALs.
- Each new task must ship a real module, numeric-invariant tests, CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If incomplete: commit/push partial module and leave exact next line/blocker here. Never leave tree clean with a pending EVAL.
- Final responses must not ask follow-up questions.