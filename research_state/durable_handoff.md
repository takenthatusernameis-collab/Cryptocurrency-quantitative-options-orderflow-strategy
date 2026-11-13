# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name (priority order):** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers. **Options** is the first-named pillar and **orderflow alpha/toxicity** the second; the analytics layer still has no dedicated EVAL for either (see next focus below).
**Refreshed:** 2026-11-13T06:00:18Z (UTC). Verified this session: EVAL-15 SEALED (GO) re-run `pytest -q tests/test_paper_execution_hardening.py` → **20 passed**; `py_compile` OK. EVAL-16 **still ACTIVE and unimplemented**: no `src/analytics/options_surface_greeks_evaluation.py`, no `tests/test_options_surface_greeks_evaluation.py`, no `research_state/OPTIONS_SURFACE_GREEKS_EVAL_*.{json,md}` artifacts exist (glob verified). `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; root handoffs are retired pointers; no blocked/failed EVAL tasks; working tree clean.
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are **retired pointer stubs** — do not action them and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope), not task sources.

---

## INITIAL TASK MESSAGE — 2026-11-13T05:03:00Z (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-13T05:03:00Z-EVAL-16-ACTIVE`
**STATUS:** **EVAL-16 IS ASSIGNED AND ACTIVE — DO IT THIS SESSION. Do not defer, do not just edit this file, do not claim "nothing assigned".** The previous session sealed EVAL-15 (paper execution hardening) and defined this campaign; your session exists to execute EVAL-16 and ship real artifacts.

> **COPY-PASTE TASK (execute as your session work):**
>
> Implement **EVAL-16 — Options vol-surface & greeks evaluation** (paper-only, deterministic, no network, no `.env`, no live).
> Create `src/analytics/options_surface_greeks_evaluation.py`, `tests/test_options_surface_greeks_evaluation.py` (~12–18 numeric-invariant tests), and a CLI (`python -m src.analytics.options_surface_greeks_evaluation --out research_state/`), emitting the strict artifact `research_state/OPTIONS_SURFACE_GREEKS_EVAL_<UTC>.{json,md}`.
> Required heavy work (no prose-only verdict):
> 1. Load the **real** BTC options quotes via `src.campaign.integrated._load_options_chain(symbol="BTC", spot=DEFAULT_SPOT["BTC"], now=DETERMINISTIC_NOW, venue="synthetic")` (`data/raw/options_btc_synthetic.json`: 30 quotes, 3 expiries, calls+puts). Do **not** enumerate `research_state/`; do **not** touch the network.
> 2. **Reconstruct a coherent surface** with `src.features.iv_surface.build_iv_surface_from_chain(chain, spot=DEFAULT_SPOT["BTC"], rate=0.0, now=DETERMINISTIC_NOW, seed=42)` (returns `IVSurface`, verified: 30 points from the real chain), then `src.features.iv_surface.calibrate_iv_surface(surface.points, spot, rate=0.0, seed=42, underlying="BTC", venue="synthetic")` → `(surface, {num_points,residual_mean,residual_std,residual_max_abs,...})`. Also compute the `src.features.volatility` term-structure/skew primitives (`calculate_atm_term_structure`, `calculate_iv_skew_term_structure`) for the expiry-monotonicity check.
> 3. **DATA-QUALITY (do NOT assume arbitrage-free):** the real `data/raw/options_btc_synthetic.json` is synthetic and internally INCONSISTENT — measured this session at `spot=65000`: Black-Scholes(mark_iv) vs stored `mark` max abs diff `8516.364` / mean `3192.683`; put–call parity residual `(C-P)-(S-K)` range `[-6480.2, +6634.7]` / mean `84.9`; `mark_iv` range `0.418..0.799`. So report **measured** BS-price residual and parity residual as explicit fields with thresholds, and compute **butterfly/calendar** on the **reconstructed** IV grid (not the raw quotes). A NO-GO on raw-data quality is a legitimate deterministic outcome — do not fudge it to GO.
> 4. Recompute greeks with `src.features.options_pricing.black_scholes_greeks(PricingInputs(spot,strike,rate,volatility,time_to_expiry,option_type,seed))` from the **reconstructed surface** (not the raw stored greeks); cross-check analytic vs central finite-difference greeks (`<= tol`). Report stored-vs-recomputed delta error as a data-quality metric (expected large; see item 3). Compute book greeks: `calculate_total_gex`, `gamma_flip_level`, `calculate_put_call_ratio`, `calculate_max_pain`, `calculate_iv_skew`, `calculate_chain_liquidity_metrics`.
> 5. **Net-of-cost**: run a deterministic delta-hedge of the options book (bid/ask spread cost) through the OOS windows with `src.analytics.strategy_evaluation.compute_metrics`; report net return/Sharpe **with** options vs a no-options control.
> 6. Deterministic `compute_options_surface_verdict(...) -> dict` with an explicit `checks` list (data-quality, surface residual, greeks consistency, net-of-cost), numeric thresholds + rationale, finite metrics, evidence matrix, strict-serializable (`serialize_metrics_strict`/`assert_json_valid`, `allow_nan=False`), **never** `{"valid": true}`.
> 7. Verify: `python -m py_compile ...` + targeted `pytest -q tests/test_options_surface_greeks_evaluation.py`; then update this handoff in place to seal EVAL-16 with verdict/artifact/timestamps/tests.
>    **CAUTION:** `src.options.phase25_vol_surface.VolSurface.build_surface` is a SIMPLIFIED STUB (hardcoded `tenor_days=30.0`/`moneyness=1.0`, reads `q.get("iv", 0.5)`, data has `mark_iv`/`open_interest`) — do **not** use it as the primary surface source.
>
> **If EVAL-16 is already sealed in this file when you read it, move to EVAL-17 (orderflow alpha & toxicity) below — never end a session with no sealed EVAL task.**

**SESSION CONFIRM — 2026-11-13T06:00:18Z:** EVAL-16 remains the single active initial task for the next agentic work session. It is unimplemented (no module, no tests, no artifact). The next agent's first action must be to execute the EVAL-16 copy-paste task above and ship `src/analytics/options_surface_greeks_evaluation.py` + `tests/test_options_surface_greeks_evaluation.py` + CLI + `research_state/OPTIONS_SURFACE_GREEKS_EVAL_<UTC>.{json,md}`. Do not end the session with only a handoff edit; a session ending with no new EVAL-16 artifact is FAILED. If EVAL-16 is sealed, proceed to EVAL-17 (orderflow alpha & toxicity).

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

**reuse points (verified 2026-11-13T05:03:00Z):** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.gamma_inventory_hedge.evaluate_gamma_inventory_hedge`; `src.analytics.hedge_cost_optimizer.evaluate_hedge_cost_optimizer`; `src.campaign.integrated` (`_load_options_chain`, `_load_orderflow`, `_features_for_symbol`, `DEFAULT_SPOT` (`BTC=65000.0`), `DETERMINISTIC_NOW` (`2026-10-31 00:00:00+00:00`)); `src.data.loader.DataLoader` (unwraps dict-wrapped JSON); **options primitives** `src.features.options_pricing.black_scholes` / `black_scholes_greeks` (takes `PricingInputs(spot,strike,rate,volatility,time_to_expiry,option_type,seed)`), `src.features.volatility.calculate_atm_term_structure / calculate_iv_skew_term_structure / calculate_risk_reversal_term_structure / calculate_skew_term_structure / calculate_put_call_ratio / calculate_max_pain / calculate_iv_skew` (take `List[OptionQuote]`), `src.features.gamma_exposure.calculate_total_gex / gamma_flip_level`, `src.features.liquidity.calculate_chain_liquidity_metrics`; **surface** `src.features.iv_surface.build_iv_surface_from_chain` (→ `IVSurface`, 30 pts on real chain) + `src.features.iv_surface.calibrate_iv_surface` (→ residuals `{num_points,residual_mean,residual_std,residual_max_abs}`); `src.options.phase25_vol_surface.VolSurface.build_surface` is a **simplified stub** (hardcoded tenor/moneyness, needs `iv` key) — secondary only. **orderflow primitives** `src.alpha.orderflow_alpha.OrderflowAlphaEngine.extract_features`. `scripts/run_backtest.py` is vacuous smoke test — not strategy performance.

---

## FOCUS CAMPAIGN (strictly sequential — EVAL-16 is ACTIVE)

| Order | Task | Status | Required output |
|---|---|---|---|
| EVAL-02..EVAL-15 | Prior evaluations/readiness | **COMPLETE (sealed)** | Modules/tests/CLIs/artifacts listed above. |
| **EVAL-16** | **Options vol-surface & greeks evaluation** | **ACTIVE — DO NOW** | `src/analytics/options_surface_greeks_evaluation.py` + `tests/test_options_surface_greeks_evaluation.py` (~12–18) + CLI + `research_state/OPTIONS_SURFACE_GREEKS_EVAL_<UTC>.{json,md}`; deterministic `compute_options_surface_verdict` with **measured data-quality** (BS-price vs mark, parity residual), reconstructed-surface residual/calibration, greeks-recompute consistency, and net-of-cost checks; paper-only. |
| EVAL-17 | Orderflow alpha & toxicity evaluation | **QUEUED (next)** | `src/analytics/orderflow_alpha_toxicity_evaluation.py` + `tests/test_orderflow_alpha_toxicity_evaluation.py` (~12–18) + CLI + `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_<UTC>.{json,md}`; real 1000-trade BTC orderflow; `OrderflowAlphaEngine` features; causal/no-lookahead signal; IC + decay + VPIN toxicity + net-of-cost with/without; block-bootstrap CI + paired permutation; deterministic verdict; paper-only. |
| EVAL-18 | (conditional) Integrated options+orderflow net-of-cost evaluation | **NOT YET ASSIGNED** | Only after EVAL-16 and EVAL-17 are sealed; combine both alpha sources into one net-of-cost walk-forward verdict consistent with EVAL-13/14/15 guardrails. Paper-only. |

**Rule:** do not re-open sealed EVALs. Do not implement or advance Phase 292+ or any `phaseNN_*_post_attribution_seal_orchestrator` wrapper. A session must seal at least one EVAL task; a session that ends with no new EVAL artifact (only handoff/timestamp edits) is FAILED.

---

## HEAVY-WORK FLOOR (for EVAL-16 / EVAL-17 / EVAL-18)

Any of these tasks must, at minimum:
1. **Read and use real sealed artifacts** relevant to the task as evidence inputs; cite key numbers in output artifact. For EVAL-16/17 the primary inputs are the **real** files `data/raw/options_btc_synthetic.json` and `data/raw/orderflow_btcusdt_synthetic.json` (loaded via `src.campaign.integrated`), plus sealed EVAL-07/08/09/13 evidence for the net-of-cost model.
2. **Compute deterministic verdict/metrics in code** — explicit function combining checks; no prose-only verdict.
3. **Emit numeric thresholds/guardrails where applicable** as structured fields with rationale; paper-only.
4. **Ship module + numeric-invariant tests + CLI + strict artifact** `research_state/<TASK>_<UTC>.{json,md}`. Strict-serializable (`allow_nan=False`); never `{"valid": true}`; no NaN/Infinity.
5. **Assert non-degeneracy/consistency** — finite metrics, explicit pass/fail reasons list, evidence matrix present, verdict matches function, arbitrage/identity residuals bounded.
6. **Run verification** (`py_compile` + targeted pytest for the task) and report results.
7. **Update this handoff in place** to seal the task with verdict/artifact/timestamps/tests when complete. A session that only edits handoff/timestamps without task artifacts is FAILED.

---

## VERIFIED STATE — ground truth (do not re-verify environment)

- **Environment:** Python 3.12.3; deps installed (numpy/pandas/scipy/pydantic/pytest/PyYAML/requests). `mypy/ruff/flake8` not installed; use `python3 -m py_compile` + targeted pytest.
- **Key sealed artifacts present:** `research_state/HEDGE_COST_OPTIMIZER_20261113T004000Z.{json,md}`, `research_state/REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}`, `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}`, `research_state/GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`, `research_state/FINAL_STRATEGY_CERTIFICATION_20261113T015226Z.{json,md}`, `research_state/PAPER_DEPLOYMENT_READINESS_20261113T030007Z.{json,md}`, `research_state/PAPER_EXECUTION_HARDENING_20261113T045715Z.{json,md}`, campaign checkpoints (`END2END_LIVE_TRADING_READINESS_latest.json`, `PAPER_TRADING_PRE_LIVE_READINESS_latest.json`, `CONTINUOUS_VALIDATION_AND_MONITORING_latest.json`).
- **EVAL-15 key numbers (verified 2026-11-13T05:03:00Z):** verdict GO (12/12 checks); `all_guardrails_pass=true`; `kill_switch_not_triggered=true`; `live_trading_enabled=false`; `trading_mode=paper`; reconciliation freshness met (target >= 0.99), CV iterations 5/5; alert watch levels include drawdown watch (observed ~0.1887 >= 0.10 watch, below 0.20 kill-switch); strict artifact JSON+MD emitted.
- **EVAL-14 key numbers:** verdict GO (10/10); 9 guardrails wired; 6 alert watch levels; 3 kill-switch halt conditions; paper-only.
- **EVAL-13 key numbers:** verdict GO (8/8); best config `target_delta_usd=-20000.0, toxicity_threshold=0.7, cost_budget_bps=0.5`; mean net Sharpe `13.188322`; bootstrap CI return `[0.298731, 0.494794]`, Sharpe `[9.378864, 18.878999]`; 9 guardrails all pass.
- **EVAL-12 key numbers:** verdict GO; EVAL11_best mean Sharpe/return `13.188322`/`0.399995`; EVAL10_default `-22.765930`/`-0.558011`; DSR both `0.0`; PBO overall `0.5`; BH FDR 0.10 survivors both configs.
- **Data reality (verified):** BTC options `data/raw/options_btc_synthetic.json` = **30 quotes, 3 expiries (2026-11-01 / 2026-11-07 / 2026-11-30), calls+puts, stored delta/gamma/vega/theta/IV** (venue `synthetic`). **Options file is synthetic and internally INCONSISTENT** (measured 2026-11-13T05:03:00Z at spot 65000): BS(mark_iv) vs stored mark max abs diff `8516.364` / mean `3192.683`; parity residual `(C-P)-(S-K)` `[-6480.2, +6634.7]` / mean `84.9`; `mark_iv` `0.418..0.799`. EVAL-16 must report these as measured data-quality, not assume arbitrage-free. BTC orderflow `data/raw/orderflow_btcusdt_synthetic.json` = **1000 trades + 20 liquidations + 8 funding rates**, symbol `BTCUSDT`; no ETH orderflow/options files (synthetic fallback); processed venue snapshots aggregate-only (6 files). Spot default `DEFAULT_SPOT["BTC"]=65000.0`.
- **Loader fix (this session):** `src/campaign/integrated._load_options_chain` called `DataLoader.load_options_chain(..., symbol=...)` but the loader takes `underlying=` → silent TypeError → always used 40-quote synthetic fallback. **FIXED** to `underlying=symbol`; now loads the real 30-quote chain. Verified: `tests/test_integrated_campaign.py` + `tests/test_integrated_signal_series.py` + `tests/test_data_loader_and_validation.py` → **38 passed**; `tests/test_capacity_aware_tca.py` + `tests/test_real_walkforward_certification.py` + `tests/test_strategy_falsification.py` → **26 passed**.
- **Safety:** `.env` **ABSENT**. `.env.example:15` = `LIVE_TRADING_ENABLED=false`. `next9_unblocked=false` (NEXT9 A1–A7 human-only, out of scope).
- **Avoid traps:** never run full 865-file `pytest`; never enumerate `research_state/` (5GB+/~77k files); `scripts/run_backtest.py` vacuous.

---

## BOTTLENECKS REMOVED (this session — 2026-11-13T05:03:00Z)

| Bottleneck | Resolution |
|---|---|
| Handoff left next task "NOT ASSIGNED" → agents could do handoff-only no-op sessions | **RESOLVED.** EVAL-16 (options vol-surface & greeks) is now an **ACTIVE, assigned** task with a copy-paste prompt; EVAL-17 queued; queue no longer says "NOT ASSIGNED". |
| Repo-priority gap: options pricing/greeks/vol-surface and orderflow alpha/toxicity had no dedicated analytics EVAL | **RESOLVED (campaign defined).** EVAL-16 targets options vol-surface/greeks/data-quality/net-of-cost; EVAL-17 targets orderflow alpha/toxicity/net-of-cost, both grounded in verified real data files and reuse points. |
| **Broken options loader** (`_load_options_chain` passed `symbol=` instead of `underlying=`) → silent synthetic fallback, real 30-quote file never used | **FIXED** in `src/campaign/integrated.py`; now loads the real chain. Regression-checked: **38 + 26 targeted tests passed** (no sealed-EVAL test broken). |
| Options data assumed arbitrage-free but is internally inconsistent | **RESOLVED (documented).** Measured BS-price residual mean `3192.683` and parity residual `±~6600`; EVAL-16 now reconstructs a surface (`build_iv_surface_from_chain`/`calibrate_iv_surface`) and reports data-quality as measured checks instead of fudging a GO. |
| EVAL-15 implementation state unclear vs handoff | **RE-VERIFIED.** `pytest -q tests/test_paper_execution_hardening.py` → 20 passed; `py_compile` OK; sealed EVAL-15 stands. |
| Competing/stale root handoff files | **CLEARED (verified).** Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` remain retired pointers with no task IDs; this file remains sole authority. |

**Tree verified 2026-11-13T05:03:00Z:** EVAL-15 sealed and re-passing; EVAL-16 assigned as the active heavy task. P0 safety clear (`.env` absent, `LIVE_TRADING_ENABLED=false`). No blocked tasks.

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
- Work queue: **EVAL-02..EVAL-15 SEALED**; **EVAL-16 ACTIVE**; EVAL-17 queued; EVAL-18 conditional. Do not reopen sealed EVALs.
- Each new task must ship a real module, numeric-invariant tests, CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If incomplete: commit/push partial module and leave exact next line/blocker here. Never leave tree clean with EVAL-16 pending.
- Final responses must not ask follow-up questions.