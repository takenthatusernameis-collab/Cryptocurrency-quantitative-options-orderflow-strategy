# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission (inferred priority):** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. Deliverable is the strategy and its measured performance, not orchestrator wrappers.
**Refreshed:** 2026-11-13T10:56:03Z (UTC)
**Authority:** this file is the only actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action. Do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope).

---

## INITIAL TASK MESSAGE — 2026-11-13T10:56:03Z (copy-paste to the next agent — STOP STATE)

**TASK ID:** `INIT-2026-11-13T10:56:03Z-EVAL-19-SEALED-STOP`
**STATUS:** **EVAL-19 (Net-of-Cost Production Simulation & Robustness Certification) IS SEALED (NO-GO, legitimate). EVAL-02..EVAL-19 are sealed. No next EVAL is defined.**

> **MANDATORY — STOP (do not do handoff-only/no-op work, do not invent new EVALs/wrappers):**
>
> EVAL-19 was implemented, verified, and sealed in-place. If you read this and EVAL-19 remains sealed, **STOP**. Do not re-open sealed EVALs, do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers, do not enumerate `research_state/`, and do not run the full 865-file test suite.
>
> **If a human explicitly defines a new heavy-work EVAL (with scope/deliverables),** replace this section in place with that single timestamped actionable task (new TASK ID), keep this file the only actionable handoff, and execute the full heavy-work floor (module + 12–18 numeric-invariant tests + CLI + strict artifact + verification + seal). A session ending with no new EVAL artifact is FAILED.

**EVAL-19 seal (2026-11-13T10:52:00Z, measured):**
- **Verdict:** **NO-GO (legitimate, measured)** — 4/6 checks pass; failed `net_of_cost_superior_vs_controls`, `robust_across_regimes`.
- **Checks:** PASS `signal_exists` (combined IC mean -0.076959, |IC|>1e-9), PASS `ic_significant` (|t|=5.0564, permutation p=0.0010), FAIL `net_of_cost_superior_vs_controls` (mean Sharpe combined -30.063030 vs options-only -21.548226, orderflow-only -30.050428, flat 0.0; cost applied), PASS `toxicity_gate_measured` (mean VPIN 0.4408, gate engagement 0.2250 non-degenerate), FAIL `robust_across_regimes` (low-tox Sharpe 0.0, high-tox Sharpe -28.488097 vs flat 0.0), PASS `guardrails_consistent_with_eval13_14_15` (delta band ±323.77 USD, toxicity gate 0.7, cost budget 0.5 bps, kill-switch DD 20%/tox 80%/cost 5 bps, max notional 1M USD, max daily loss 50k USD).
- **Walk-forward (seeds 1–10, 3 windows, BTC synthetic, capacity-aware costs):** combined return -0.396136, Sharpe -30.063030, max-DD 0.396136, cost 13.916 USD, 95 trades; flat 0.0/0.0/0.0/0.0 USD/0 trades; options-only return -0.270734, Sharpe -21.548226, max-DD 0.270734, cost 14.456 USD, 119.5 trades; orderflow-only return -0.398124, Sharpe -30.050428, max-DD 0.398124, cost 13.916 USD, 95 trades.
- **Robustness:** cost sensitivity grid [0.0, 0.5, 1.0, 5.0] bps reported; kill-switch observed max DD 0.398124 (DD trigger true at 20% threshold), max toxicity 0.565912 (tox trigger false), main cost ~1.3916 bps (cost trigger false). DSR/PBO/BH-FDR and permutation pairs computed.
- **Data/evidence:** real loaders only — `data/raw/options_btc_synthetic.json` (30 quotes) and `data/raw/orderflow_btcusdt_synthetic.json` (1000 trades, 20 liqs, 8 funding), deterministic, no network; paper-only (`live_trading_enabled=false`, no `.env`), strict serialization (`allow_nan=False`, never `{"valid": true}`).
- **Deliverables (present):** `src/analytics/production_simulation_evaluation.py`, `tests/test_production_simulation_evaluation.py` (16 numeric-invariant tests), CLI `python -m src.analytics.production_simulation_evaluation --out research_state/`, artifacts `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.{json,md}` (latest).
- **Verification:** `python -m py_compile src/analytics/production_simulation_evaluation.py` OK; `python -m py_compile tests/test_production_simulation_evaluation.py` OK; `python -m pytest -q tests/test_production_simulation_evaluation.py` → **16 passed** (2026-11-13T10:52:00Z).

**Constraints:** paper-only; `.env` absent, `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no network calls to exchanges, no NEXT9 unblock, no enumerating `research_state/`, no full 865-file test suite, no new `phaseNN_*_post_attribution_seal_orchestrator` wrappers, do not re-open sealed EVALs. `scripts/run_backtest.py` is vacuous smoke test.

---

## SEALED EVALUATIONS (do not re-open)

- **EVAL-02..EVAL-15:** sealed per prior campaign (see key artifacts below). EVAL-12/13/14/15 GO; EVAL-06/10 NO-GO (legitimate).
- **EVAL-16 SEALED (NO-GO, legitimate, measured 2026-11-13T07:04:26Z):** `src/analytics/options_surface_greeks_evaluation.py` + `tests/test_options_surface_greeks_evaluation.py` (21) + `research_state/OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}`. Verdict NO-GO 5/9 on real 30-quote BTC chain (`data/raw/options_btc_synthetic.json`, spot 65000): BS-vs-mark max abs 8516.3642; parity max abs 6634.6831; delta err mean 0.3402/max 0.8494; butterfly violation (max 0.4006) on reconstructed grid. Data-quality/greeks failures are true data state — do not fudge.
- **EVAL-17 SEALED (NO-GO, legitimate, 2026-11-13T08:00:05Z):** `src/analytics/orderflow_alpha_toxicity_evaluation.py` + `tests/test_orderflow_alpha_toxicity_evaluation.py` (23) + `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`. Real BTC orderflow (1000 trades/20 liqs/8 funding). Causal net_aggression; IC mean -0.00820, t -1.3512, p 0.0889 (FAIL ic_significant); VPIN mean 0.4408, gate-engagement 0.225; with-signal Sharpe -53.36 vs flat 0.0. Verdict NO-GO 4/5.
- **EVAL-18 SEALED (NO-GO, legitimate, 2026-11-13T08:10:00Z):** `src/analytics/integrated_options_orderflow_evaluation.py` + `tests/test_integrated_options_orderflow_evaluation.py` (28) + `research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z.{json,md}`. Integrated options+orderflow net-of-cost (seeds 1–5) vs 3 controls; combined Sharpe -37.07, options-only -63.79, orderflow-only -37.28, flat 0.0; toxicity gate engagement 0.225; verdict NO-GO 5/7 (options_signal_exists FAIL due static reconstructed surface; combined_net_of_cost_superior FAIL).
- **EVAL-19 SEALED (NO-GO, legitimate, 2026-11-13T10:52:00Z):** `src/analytics/production_simulation_evaluation.py` + `tests/test_production_simulation_evaluation.py` (16) + `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.{json,md}`. Verdict NO-GO 4/6; combined not superior vs controls and not robust across regimes (see seal above). No next EVAL defined.

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Safety:** `.env` **absent**; `.env.example:15` `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`. Paper-only.
- **Data (verified):** `data/raw/options_btc_synthetic.json` = 30 BTC quotes, 3 expiries, calls+puts, stored greeks/IV (synthetic, internally inconsistent — measured by EVAL-16). `data/raw/orderflow_btcusdt_synthetic.json` = 1000 trades + 20 liquidations + 8 funding, BTCUSDT. No ETH/SOL raw options/orderflow files (synthetic fallback). `DEFAULT_SPOT["BTC"]=65000.0`, `DETERMINISTIC_NOW=2026-10-31 00:00:00+00:00`.
- **Key sealed artifacts:** `HEDGE_COST_OPTIMIZER_20261113T004000Z`, `REAL_WF_CERTIFICATION_20261113T010508Z`, `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z`, `GAMMA_INVENTORY_HEDGE_20261112T221000Z`, `FINAL_STRATEGY_CERTIFICATION_20261113T015226Z`, `PAPER_DEPLOYMENT_READINESS_20261113T030007Z`, `PAPER_EXECUTION_HARDENING_20261113T045715Z`, `OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z`, `ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z`, `INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z`, `PRODUCTION_SIMULATION_EVAL_20261113T104657Z`.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders; EVAL-16/17/18/19 modules for signal/eval patterns; options/orderflow/IV-surface primitives as noted in prior sealed handoff state.
- **Environment:** Python 3.12.3; deps installed (numpy/pandas/scipy/pydantic/pytest/PyYAML/requests). No mypy/ruff/flake8 — use `python3 -m py_compile` + targeted pytest. Never run full 865-file pytest. Never enumerate `research_state/`.

---

## BOTTLENECKS REMOVED / CLEARED (2026-11-13T10:56:03Z)

| Bottleneck | Resolution |
|---|---|
| Conflicting/stale handoff content (mixed EVAL-19 sealed/STOP vs ACTIVE/pending references) | **CLEARED.** Handoff consolidated to single authoritative sealed STOP state for EVAL-19; stale ACTIVE queue/bottleneck references removed. |
| Competing handoff files | **CLEARED (verified).** Root handoffs are retired pointers (no task IDs); only `research_state/durable_handoff.md` is actionable. |
| Ambiguous next work with all defined EVALs sealed | **CLEARED.** Explicit STOP state: no next EVAL defined; any new heavy work requires human-defined scope recorded here as a new timestamped task. |
| Safety ambiguity | **CLEARED.** `.env` absent, `LIVE_TRADING_ENABLED=false`, no NEXT9 unblock — paper-only enforced. |

---

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Work queue: **EVAL-02..EVAL-19 SEALED. No next EVAL defined (STOP until human defines scope).**
- Any new EVAL must ship real module + numeric-invariant tests + CLI + strict artifact (no wrappers/stubs/no-ops). A session ending with no new EVAL artifact (when one is assigned) is FAILED.
- If incomplete: commit/push partial module and leave exact next line/blocker here. Never leave tree clean with a pending assigned EVAL.
- Final responses must not ask follow-up questions.
