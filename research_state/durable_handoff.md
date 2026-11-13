# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission inferred from repo name:** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. The deliverable is the **strategy and its measured performance**, not orchestrator wrappers.
**Refreshed:** 2026-11-13T03:54:46Z (UTC). Verified: EVAL-13 SEALED (GO) `FINAL_STRATEGY_CERTIFICATION_20261113T015226Z.{json,md}`; EVAL-14 SEALED (GO) `PAPER_DEPLOYMENT_READINESS_20261113T030007Z.{json,md}` (10/10 checks, 9 guardrails wired). EVAL-12/EVAL-11/EVAL-10/EVAL-09/EVAL-08/EVAL-07/EVAL-06/EVAL-03/EVAL-02 sealed. `.env` absent; `.env.example:15` `LIVE_TRADING_ENABLED=false`; root handoffs retired pointers. **Campaign advanced:** EVAL-14 complete; starting **EVAL-15 (Paper execution + live-monitoring hardening)**. Bottlenecks removed: no competing handoffs, all prior evaluations sealed, P0 safety clear.
**Authority:** this file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are **retired pointer stubs** — do not action them and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope), not task sources.

---

## INITIAL TASK MESSAGE — 2026-11-13T03:54:46Z (copy-paste to the next agent)

**TASK ID:** `INIT-2026-11-13T03:54:46Z-EVAL-15-PAPER-EXEC-MONITOR-HARDEN`
**STATUS:** ACTIVE — EVAL-13 and EVAL-14 SEALED (GO). Start EVAL-15 now. Do not re-open EVAL-13/EVAL-14. Do not implement Phase 292+ or any `phaseNN_*_post_attribution_seal_orchestrator` wrapper. Do not create new handoff files.

**EVAL-15 OBJECTIVE (Paper execution + live-monitoring hardening, paper-only):**
Build a deterministic, testable paper-execution harness that operationalizes EVAL-14 readiness: enforce guardrails in execution, add monitoring/alerting with kill-switch logic, track PnL/positions/greeks/toxicity/costs in real-time simulation, and emit auditable artifacts with strict serialization. Must integrate with sealed strategy outputs (EVAL-11 best config) and remain `live_trading_enabled=false` with zero venue/credential mutation.

**HEAVY-WORK FLOOR (must satisfy):**
1. **Integrate sealed evidence.** Read/use `research_state/PAPER_DEPLOYMENT_READINESS_20261113T030007Z.json`, `research_state/FINAL_STRATEGY_CERTIFICATION_20261113T015226Z.json`, `research_state/REAL_WF_CERTIFICATION_20261113T010508Z.json`, `research_state/HEDGE_COST_OPTIMIZER_20261113T004000Z.json`, and checkpoints `research_state/PAPER_TRADING_PRE_LIVE_READINESS_latest.json`, `research_state/CONTINUOUS_VALIDATION_AND_MONITORING_latest.json`. Cite key numbers in artifact.
2. **Module:** Create `src/analytics/paper_execution_hardening.py` with CLI + programmatic entrypoint. Deterministic `compute_paper_execution_verdict` combining guardrail enforcement, kill-switch conditions, alert thresholds (watch vs block), slippage/cost tracking, PnL reconciliation, and freshness checks. Wire all 9 EVAL-13 guardrails + EVAL-14 monitoring fields.
3. **Execution model (paper-only):** Simulate orderflow-driven signals/hedges using existing interfaces (`src/analytics/gamma_inventory_hedge.evaluate_gamma_inventory_hedge`, loaders in `src/campaign/integrated`). Track `notional_usd`, `net_delta_usd` vs band `±323.77` around `target_delta_usd=-20000.0`, `toxicity_score`, `cost_bps`, `daily_loss_usd`, `drawdown`. Apply kill-switch: halt on `drawdown>=0.20`, `toxicity>=0.80`, `cost>=5.00 bps`, `daily_loss>=50000.0` or breach of hard caps. Alerts on watch levels.
4. **Verification & artifacts:** Emit strict-serializable artifact `research_state/PAPER_EXECUTION_HARDENING_<UTC>.{json,md}` (never `{"valid": true}`, no NaN/Infinity, `allow_nan=False`). Include evidence matrix, guardrail status (pass/fail), kill-switch status, alert log, reconciliation metrics, explicit pass/fail reasons list, verdict consistent with function.
5. **Tests:** Add `tests/test_paper_execution_hardening.py` with numeric-invariant tests (>=10) covering guardrail breaches, kill-switch triggers, band enforcement, toxicity/cost caps, daily loss, serialization validity.
6. **Verify:** Run `python3 -m py_compile` on new/changed files and targeted pytest for EVAL-15. Avoid full suite.
7. **Handoff:** Update this `research_state/durable_handoff.md` in place to seal EVAL-15 with verdict/artifact/timestamps/tests when complete.

**CONSTRAINTS:** Paper-only. `.env` absent, `LIVE_TRADING_ENABLED=false`. No live enablement, no `.env` creation, no venue/config/credential mutation, no network calls to exchanges, no NEXT9 unblock, no enumerating `research_state/` (glob specific files), no full test suite, no new phase orchestrator wrappers, no re-opening sealed EVALs. Use existing loaders/primitives; `scripts/run_backtest.py` is vacuous smoke test.


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
> **EVAL-14 COMPLETE (sealed GO):** `src/analytics/paper_deployment_readiness.py` + `tests/test_paper_deployment_readiness.py` (8) + CLI; artifact `PAPER_DEPLOYMENT_READINESS_20261113T030007Z.{json,md}`. Deterministic `compute_paper_readiness_verdict` **GO** (10/10 checks); 9 EVAL-13 guardrails wired as structured fields with rationale plus alert (not block) watch levels and kill-switch halt conditions; evidence matrix present; strict-serializable, no NaN/Infinity, never `{"valid": true}`; `live_trading_enabled=false`; paper-only.

**Reuse points (verified):** `src/analytics/gamma_inventory_hedge.evaluate_gamma_inventory_hedge`, `src/analytics/hedge_cost_optimizer.evaluate_hedge_cost_optimizer`, `src/analytics/strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`), `src/analytics/strategy_falsification._deflated_sharpe` (`:105`), `src/campaign/integrated` loaders/paths, `src/data.loader.DataLoader.load_trades` (unwraps dict-wrapped JSON). `scripts/run_backtest.py` is vacuous smoke test — not strategy performance.

---

## FOCUS CAMPAIGN (strictly sequential)

| Order | Task | Status | Required output |
|---|---|---|---|
| EVAL-02..EVAL-12 | Prior evaluations | **COMPLETE** | Sealed artifacts/modules/tests listed above. |
| EVAL-13 | Final strategy certification + risk guardrails | **COMPLETE** | `src/analytics/final_strategy_certification.py` + `tests/test_final_strategy_certification.py` (6) + CLI + `research_state/FINAL_STRATEGY_CERTIFICATION_20261113T015226Z.{json,md}`; deterministic `GO` from EVAL-11/12/10 evidence; 9 paper-only deployment guardrails (max notional, delta band, toxicity gate, cost budget, kill-switch); all 8 verdict checks pass. |
| EVAL-14 | Paper deployment readiness package | **COMPLETE** | `src/analytics/paper_deployment_readiness.py` + `tests/test_paper_deployment_readiness.py` (8) + CLI + `research_state/PAPER_DEPLOYMENT_READINESS_20261113T030007Z.{json,md}`; deterministic GO (10/10 checks). |
| EVAL-15 | Paper execution + live-monitoring hardening | **ACTIVE** | `src/analytics/paper_execution_hardening.py` + `tests/test_paper_execution_hardening.py` (>=10) + CLI + `research_state/PAPER_EXECUTION_HARDENING_<UTC>.{json,md}`; deterministic verdict with guardrail enforcement, kill-switch, alerts, reconciliation. |

**Rule:** do not re-open sealed EVALs. Do not advance beyond EVAL-13 until sealed with real artifact. Do not implement or advance Phase 292+ or any `phaseNN_*_post_attribution_seal_orchestrator` wrapper.

---

## HEAVY-WORK FLOOR (a session that does less is FAILED)

EVAL-13 must, at minimum:
1. **Read and use real sealed artifacts** (`HEDGE_COST_OPTIMIZER_20261113T004000Z.json`, `REAL_WF_CERTIFICATION_20261113T010508Z.json`, `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.json`) as evidence inputs; cite key numbers in output artifact.
2. **Compute deterministic certification in code** — explicit verdict function combining DSR/PBO/BH-survival, net-of-cost performance, and guardrail checks; no prose-only verdict.
3. **Emit numeric deployment guardrails** (max notional, delta band, toxicity gate, cost budget bps, kill-switch conditions) as structured fields with rationale; paper-only.
4. **Ship module + numeric-invariant tests + CLI + artifact** `FINAL_STRATEGY_CERTIFICATION_<UTC>.{json,md}`. Strict-serializable; never `{"valid": true}`; no NaN/Infinity.
5. **Assert non-degeneracy/consistency** — finite metrics, explicit pass/fail reasons list, evidence matrix present, guardrails numeric, verdict matches function.
6. **Run verification** (`py_compile` + targeted pytest for EVAL-13) and report results.
7. **Update this handoff in place** to seal EVAL-13 (or leave exact next line/blocker if genuinely incomplete). A future session that only edits handoff/timestamps without EVAL-13 artifacts is FAILED.

## EVAL-14 HEAVY-WORK FLOOR — SEALED (GO, completed 2026-11-13T03:52:00Z)

EVAL-14 shipped, at minimum:
1. **Read and used real sealed artifacts** (`FINAL_STRATEGY_CERTIFICATION_20261113T015226Z.json`, `REAL_WF_CERTIFICATION_20261113T010508Z.json`, `PAPER_TRADING_PRE_LIVE_READINESS_latest.json`, `CONTINUOUS_VALIDATION_AND_MONITORING_latest.json`) as evidence inputs; cited key numbers in output artifact.
2. **Wired monitoring/alert thresholds to EVAL-13 guardrails** — structured numeric fields (max notional, delta band, toxicity gate, cost budget bps, kill-switch drawdown/toxicity/cost, max daily loss, `live_trading_enabled=false`) with rationale; paper-only; no live enablement.
3. **Computed deterministic paper-readiness verdict in code** — explicit verdict function; no prose-only verdict.
4. **Shipped module + numeric-invariant tests + CLI + artifact** `PAPER_DEPLOYMENT_READINESS_20261113T030007Z.{json,md}`. Strict-serializable; never `{"valid": true}`; no NaN/Infinity.
5. **Asserted non-degeneracy/consistency** — finite metrics/thresholds, explicit pass/fail reasons list, evidence matrix present, verdict matches function.
6. **Ran verification** (`py_compile` + targeted pytest for EVAL-14: 8 passed) and reported results.
7. **Updated this handoff in place** to seal EVAL-14.

---

## VERIFIED STATE — ground truth (do not re-verify environment)

- **Environment:** Python 3.12.3; deps installed (numpy/pandas/scipy/pydantic/pytest/PyYAML/requests). `mypy/ruff/flake8` not installed; use `python3 -m py_compile` + targeted pytest.
- **Key sealed artifacts present:** `research_state/HEDGE_COST_OPTIMIZER_20261113T004000Z.{json,md}`, `research_state/REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}`, `research_state/STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z.{json,md}`, `research_state/GAMMA_INVENTORY_HEDGE_20261112T221000Z.{json,md}`, campaign checkpoints (`END2END_LIVE_TRADING_READINESS_latest.json`, `PAPER_TRADING_PRE_LIVE_READINESS_latest.json`, `CONTINUOUS_VALIDATION_AND_MONITORING_latest.json`).
- **EVAL-12 key numbers:** verdict GO; EVAL11_best mean Sharpe/return `13.188322`/`0.399995` (15 series); EVAL10_default `-22.765930`/`-0.558011`; DSR both `0.0`; PBO EVAL11_best `0.46875`, EVAL10_default `0.5234375`, overall `0.5`; BH FDR 0.10 survivors both configs.
- **Data reality:** BTC real trades `data/raw/orderflow_btcusdt_synthetic.json` (1000); BTC options 30 quotes; no ETH orderflow/options files (synthetic fallback); processed venue snapshots aggregate-only (6 files).
- **Avoid traps:** never run full 865-file `pytest`; never enumerate `research_state/` (5GB+/~77k files); `scripts/run_backtest.py` vacuous.

---

## BOTTLENECKS REMOVED (this session — 2026-11-13T01:14:00Z)

| Bottleneck | Resolution |
|---|---|
| Stale handoff showing EVAL-12 ACTIVE after it was sealed | **RESOLVED.** Verified EVAL-12 module/tests/artifacts present (`REAL_WF_CERTIFICATION_20261113T010508Z.{json,md}`, verdict GO, DSR/PBO/BH evidence) and advanced queue to EVAL-13 with explicit heavy-work spec/guardrails. |
| Competing/stale root handoff files | **CLEARED (verified).** Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers with no task IDs; this file remains sole authority. |
| Prior data/primitive blockers (load_trades unwrap, permutation, cost-grid semantics, inert hedge_cost_bps) | **RESOLVED in prior sessions** and documented above; EVAL-13/EVAL-14 must build on sealed evidence, not reopen. |
| EVAL-14 start clearance | **CLEAR.** EVAL-13 sealed (GO); P0 safety clear (`.env` absent, `LIVE_TRADING_ENABLED=false`, no live trading); no data/primitive blockers; EVAL-14 context artifacts present (`PAPER_TRADING_PRE_LIVE_READINESS_latest.json`, `CONTINUOUS_VALIDATION_AND_MONITORING_latest.json`, `END2END_LIVE_TRADING_READINESS_latest.json`). |

**Tree verified 2026-11-13T03:52:00Z:** EVAL-13 sealed with real artifacts; **EVAL-14 sealed (GO)** with real artifacts (`src/analytics/paper_deployment_readiness.py`, `tests/test_paper_deployment_readiness.py` (8), CLI, `research_state/PAPER_DEPLOYMENT_READINESS_20261113T030007Z.{json,md}`). P0 safety clear (`.env` absent, `LIVE_TRADING_ENABLED=false`); required evidence artifacts/checkpoints present; no active blockers. Focus campaign complete — no pending work.


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
- Work queue strictly in order: **EVAL-13 SEALED** (then **EVAL-14 ACTIVE**). Do not advance beyond EVAL-14 until sealed with real artifact.
- Each task must ship a real module, numeric-invariant tests, CLI, and a real-run artifact — no wrappers, no stubs, no "verified env only" sessions.
- If incomplete: commit/push partial module and leave exact next line/blocker here. Never leave tree clean with task pending.
- Final responses must not ask follow-up questions.
