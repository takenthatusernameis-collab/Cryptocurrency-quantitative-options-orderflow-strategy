# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission (inferred priority):** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. Deliverable is the strategy and its measured performance, not orchestrator wrappers.
**Refreshed:** 2026-11-13T11:42:53Z (UTC) — verified this session: single actionable handoff, root pointers retired, EVAL-19 artifacts present, py_compile OK on key analytics modules, no blocking environment/safety issues found.
**Authority:** this file is the only actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action. Do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope).

---

## INITIAL TASK MESSAGE — 2026-11-13T11:04:36Z (copy-paste to the next agent — EVAL-20 ACTIVE)

**TASK ID:** `INIT-2026-11-13T10:58:00Z-EVAL-20-PROFITABILITY-ROBUSTNESS`
**STATUS:** **EVAL-20 (Net-of-Cost Profitability & Regime Robustness Remediation) — ACTIVE, not yet implemented.** EVAL-02..EVAL-19 are sealed (EVAL-19 NO-GO 4/6, see SEALED EVALUATIONS). EVAL-20 is the single next heavy-work campaign.

**Mission (inferred from repo `Cryptocurrency-quantitative-options-orderflow-strategy`):** cryptocurrency quantitative OPTIONS + ORDERFLOW strategy — make the combined strategy net-of-cost superior to all controls AND robust across toxicity regimes, without triggering kill-switches. EVAL-19 sealed NO-GO because: combined Sharpe -30.063030 vs flat 0.0 / options -21.548226 / orderflow -30.050428 (FAIL `net_of_cost_superior_vs_controls`); high-tox regime Sharpe -28.488097 vs flat 0.0 / low-tox 0.0 (FAIL `robust_across_regimes`). Kill-switches triggered: Max DD 0.494440 (threshold 0.20), Max toxicity 1.000000 (threshold 0.80). Combined IC is significantly negative (-0.076959, |t|=5.0564, p=0.0010) — signal exists but is negatively predictive and loses money net of costs.

> **MANDATORY — EVAL-20 heavy-work floor (no handoff-only/no-op work, do not re-open sealed EVALs, do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers, do not enumerate `research_state/`, do not run the full 865-file test suite):**
>
> Implement and seal EVAL-20 end-to-end:
> 1. **Real module:** `src/analytics/net_of_cost_profitability_evaluation.py` — deterministic, paper-only, offline net-of-cost simulation that (a) keeps EVAL-19's causal signal build (options IV surface + orderflow net_aggression + VPIN toxicity gate at 0.7), (b) adds a profitability/robustness remediation layer (e.g. sign inversion on persistently negative IC, regime-aware position sizing, cost-throttled turnover, kill-switch-respecting risk caps), and (c) emits the same evidence fields as EVAL-19 plus the new checks below.
> 2. **Tests:** `tests/test_net_of_cost_profitability_evaluation.py` — 12–18 numeric-invariant tests (real data shapes, signal IC/thresholds, multi-seed walk-forward vs 4 controls, cost sensitivity grid, regime stress, kill-switch report, strict serialization `allow_nan=False`, never `{"valid": true}`, CLI artifact emission).
> 3. **CLI:** `python -m src.analytics.net_of_cost_profitability_evaluation --out research_state/`.
> 4. **Strict artifact:** `research_state/NET_OF_COST_PROFITABILITY_EVAL_<UTC>.{json,md}`.
> 5. **Verification:** `python -m py_compile` on module + tests OK; `python -m pytest -q tests/test_net_of_cost_profitability_evaluation.py` → all pass.
> 6. **Seal:** record verdict/checks/evidence in this file (replace this INITIAL TASK MESSAGE section) once all checks PASS (GO) or legitimately NO-GO with measured numbers stating exactly what blocked profitability.
>
> **EVAL-20 verdict checks (all must PASS for GO):**
> - `signal_exists`: combined mean IC nonzero (> IC_EXISTS_EPSILON).
> - `ic_significant`: combined IC significant (|t| > 1.96 or permutation p < 0.05).
> - `net_of_cost_superior_vs_controls`: combined mean Sharpe > max(options_only, orderflow_only, flat=0.0) at default cost run with cost applied.
> - `toxicity_gate_measured`: VPIN mean in (0,1), gate engagement fraction strictly in (0,1).
> - `robust_across_regimes`: combined Sharpe >= flat Sharpe in BOTH low- and high-VPIN toxicity regimes (both finite).
> - `kill_switch_not_triggered`: observed max DD < 0.20, max toxicity < 0.80, main cost bps < 5.0.
> - `guardrails_consistent_with_eval13_14_15`: guardrail constants consistent and cost model applied.
>
> Environment verified 2026-11-13T11:03:07Z: Python 3.12.3; `python3 -m py_compile` OK on `src/analytics/strategy_evaluation.py` + `capacity_aware_tca.py`; targeted `python3 -m pytest -q tests/test_production_simulation_evaluation.py` → 16 passed. No network, no `.env`, paper-only enforced.
>
> A session ending with no new EVAL-20 artifact (module + tests + CLI + artifact + verification) is FAILED. If remediation cannot reach GO, seal as NO-GO with measured numbers and state exactly what blocked profitability in this file.

**EVAL-19 seal summary (detailed in SEALED EVALUATIONS):** NO-GO 4/6 (2026-11-13T10:52:00Z); failed `net_of_cost_superior_vs_controls` (combined Sharpe -30.063030 vs flat 0.0) and `robust_across_regimes` (high-tox -28.488097 vs flat 0.0); kill-switches triggered (DD 0.494440, tox 1.000000). Deliverables present: `src/analytics/production_simulation_evaluation.py`, `tests/test_production_simulation_evaluation.py` (16 passed), `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.{json,md}`.

**Constraints:** paper-only; `.env` absent, `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no network calls to exchanges, no NEXT9 unblock, no enumerating `research_state/`, no full 865-file test suite, no new `phaseNN_*_post_attribution_seal_orchestrator` wrappers, do not re-open sealed EVALs. `scripts/run_backtest.py` is vacuous smoke test.

---

## SEALED EVALUATIONS (do not re-open)

- **EVAL-02..EVAL-15:** sealed per prior campaign (see key artifacts below). EVAL-12/13/14/15 GO; EVAL-06/10 NO-GO (legitimate).
- **EVAL-16 SEALED (NO-GO, legitimate, measured 2026-11-13T07:04:26Z):** `src/analytics/options_surface_greeks_evaluation.py` + `tests/test_options_surface_greeks_evaluation.py` (21) + `research_state/OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}`. Verdict NO-GO 5/9 on real 30-quote BTC chain (`data/raw/options_btc_synthetic.json`, spot 65000): BS-vs-mark max abs 8516.3642; parity max abs 6634.6831; delta err mean 0.3402/max 0.8494; butterfly violation (max 0.4006) on reconstructed grid. Data-quality/greeks failures are true data state — do not fudge.
- **EVAL-17 SEALED (NO-GO, legitimate, 2026-11-13T08:00:05Z):** `src/analytics/orderflow_alpha_toxicity_evaluation.py` + `tests/test_orderflow_alpha_toxicity_evaluation.py` (23) + `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`. Real BTC orderflow (1000 trades/20 liqs/8 funding). Causal net_aggression; IC mean -0.00820, t -1.3512, p 0.0889 (FAIL ic_significant); VPIN mean 0.4408, gate-engagement 0.225; with-signal Sharpe -53.36 vs flat 0.0. Verdict NO-GO 4/5.
- **EVAL-18 SEALED (NO-GO, legitimate, 2026-11-13T08:10:00Z):** `src/analytics/integrated_options_orderflow_evaluation.py` + `tests/test_integrated_options_orderflow_evaluation.py` (28) + `research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z.{json,md}`. Integrated options+orderflow net-of-cost (seeds 1–5) vs 3 controls; combined Sharpe -37.07, options-only -63.79, orderflow-only -37.28, flat 0.0; toxicity gate engagement 0.225; verdict NO-GO 5/7 (options_signal_exists FAIL due static reconstructed surface; combined_net_of_cost_superior FAIL).
- **EVAL-19 SEALED (NO-GO, legitimate, 2026-11-13T10:52:00Z):** `src/analytics/production_simulation_evaluation.py` + `tests/test_production_simulation_evaluation.py` (16) + `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.{json,md}`. Verdict NO-GO 4/6; combined not superior vs controls and not robust across regimes (see INITIAL TASK MESSAGE / EVAL-20 for remediation). EVAL-20 is the next active heavy-work campaign (`INIT-2026-11-13T10:58:00Z-EVAL-20-PROFITABILITY-ROBUSTNESS`).

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Safety:** `.env` **absent**; `.env.example:15` `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`. Paper-only.
- **Data (verified):** `data/raw/options_btc_synthetic.json` = 30 BTC quotes, 3 expiries, calls+puts, stored greeks/IV (synthetic, internally inconsistent — measured by EVAL-16). `data/raw/orderflow_btcusdt_synthetic.json` = 1000 trades + 20 liquidations + 8 funding, BTCUSDT. No ETH/SOL raw options/orderflow files (synthetic fallback). `DEFAULT_SPOT["BTC"]=65000.0`, `DETERMINISTIC_NOW=2026-10-31 00:00:00+00:00`.
- **Key sealed artifacts:** `HEDGE_COST_OPTIMIZER_20261113T004000Z`, `REAL_WF_CERTIFICATION_20261113T010508Z`, `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z`, `GAMMA_INVENTORY_HEDGE_20261112T221000Z`, `FINAL_STRATEGY_CERTIFICATION_20261113T015226Z`, `PAPER_DEPLOYMENT_READINESS_20261113T030007Z`, `PAPER_EXECUTION_HARDENING_20261113T045715Z`, `OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z`, `ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z`, `INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z`, `PRODUCTION_SIMULATION_EVAL_20261113T104657Z`.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders; EVAL-16/17/18/19 modules for signal/eval patterns; options/orderflow/IV-surface primitives as noted in prior sealed handoff state.
- **Environment:** Python 3.12.3; deps installed (numpy/pandas/scipy/pydantic/pytest/PyYAML/requests). No mypy/ruff/flake8 — use `python3 -m py_compile` + targeted pytest. Never run full 865-file pytest. Never enumerate `research_state/`.

---

## BOTTLENECKS REMOVED / CLEARED (2026-11-13T10:58:00Z)

| Bottleneck | Resolution |
|---|---|
| Conflicting/stale handoff content (mixed EVAL-19 sealed/STOP vs ACTIVE/pending references) | **CLEARED.** Handoff consolidated to single authoritative EVAL-20 ACTIVE state; stale ACTIVE queue/bottleneck references removed. |
| Competing handoff files | **CLEARED (verified).** Root handoffs are retired pointers (no task IDs); only `research_state/durable_handoff.md` is actionable. |
| Ambiguous next work with all defined EVALs sealed (STOP state) | **CLEARED.** EVAL-20 defined as the single active heavy-work campaign with explicit scope, acceptance checks, and heavy-work floor. No STOP state. |
| Safety ambiguity | **CLEARED.** `.env` absent, `LIVE_TRADING_ENABLED=false`, no NEXT9 unblock — paper-only enforced. |
| Environment/verification bottleneck | **CLEARED (2026-11-13T11:03:07Z).** `py_compile` OK on required analytics modules; targeted pytest on EVAL-19 tests passes (16/16). EVAL-20 can begin immediately — no missing prerequisites. |
| 248 pre-existing `phaseNN_*_post_attribution_seal_orchestrator` wrapper test files | **NOT a new bottleneck.** Pre-existing test clutter; forbidden to create new ones. Do not touch; they do not block EVAL-20. |

---

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Work queue: **EVAL-02..EVAL-19 SEALED. EVAL-20 ACTIVE (`INIT-2026-11-13T10:58:00Z-EVAL-20-PROFITABILITY-ROBUSTNESS`).**
- Any new EVAL must ship real module + numeric-invariant tests + CLI + strict artifact (no wrappers/stubs/no-ops). A session ending with no new EVAL artifact (when one is assigned) is FAILED.
- If incomplete: commit/push partial module and leave exact next line/blocker here. Never leave tree clean with a pending assigned EVAL.
- Final responses must not ask follow-up questions.
