# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission (inferred priority):** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation of the strategy**. Deliverable is the strategy and its measured performance, not orchestrator wrappers.
**Refreshed:** 2026-11-13T10:08:00Z (UTC)
**Authority:** this file is the only actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action. Do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope).

---

## INITIAL TASK MESSAGE — 2026-11-13T10:08:00Z (copy-paste to the next agent — THIS IS YOUR WORK)

**TASK ID:** `INIT-2026-11-13T10:08:00Z-EVAL-19-ACTIVE`
**STATUS:** **EVAL-19 (Net-of-Cost Production Simulation & Robustness Certification) IS THE ACTIVE REQUIRED TASK.** EVAL-02..EVAL-18 are sealed (see below). No EVAL-19 implementation/artifacts exist yet (`src/analytics/production_simulation_evaluation.py`, `tests/test_production_simulation_evaluation.py`, `research_state/PRODUCTION_SIMULATION_EVAL_*` absent as of this refresh).

> **MANDATORY — DO THE HEAVY WORK (do not just read, do not handoff-only/no-op):**
>
> Implement **EVAL-19 — Net-of-Cost Production Simulation & Robustness Certification** (paper-only, deterministic, no network, no `.env`, no live). Combine both repo pillars (options + orderflow) into production-grade net-of-cost simulation with robustness stress.
>
> **DELIVERABLES (all required):**
> 1. `src/analytics/production_simulation_evaluation.py` — module with `compute_production_simulation_verdict(...) -> dict`
> 2. `tests/test_production_simulation_evaluation.py` — **12–18 numeric-invariant tests** (not smoke tests)
> 3. CLI: `python -m src.analytics.production_simulation_evaluation --out research_state/`
> 4. Strict artifact: `research_state/PRODUCTION_SIMULATION_EVAL_<UTC>.{json,md}` emitted by CLI
>
> **HEAVY WORK FLOOR (every item mandatory, no prose-only verdicts, no stubs):**
> 1. **Load real data only:** `src.campaign.integrated._load_options_chain("BTC", 65000.0, DETERMINISTIC_NOW, "synthetic")` (30-quote BTC chain, EVAL-16) and `_load_orderflow("BTC","synthetic")` (1000 trades, 20 liqs, 8 funding, BTCUSDT, EVAL-17). No `research_state/` enumeration, no network.
> 2. **Combined signal walk-forward:** reuse EVAL-18 combined pattern — reconstructed-surface options signal + causal EVAL-17 `net_aggression` orderflow signal + VPIN toxicity gate at 0.7. Deterministic multi-seed walk-forward (seeds 1–10) via `src.analytics.strategy_evaluation.compute_metrics` with capacity-aware cost model (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION` from `src.analytics.capacity_aware_tca`).
> 3. **Controls:** report net return, Sharpe, max-DD, total cost USD, num trades, num windows for (a) combined, (b) always-flat, (c) options-only, (d) orderflow-only — same toxicity gate and cost model.
> 4. **Robustness/stress:** regime stress (high vs low VPIN toxicity; high vs low IV skew), cost sensitivity (0 / 0.5 / 1 / 5 bps), kill-switch triggers (DD 20% / toxicity 80% / cost 5 bps). Report per regime/cost setting.
> 5. **Statistical defensibility:** IC (Pearson) combined vs forward returns (horizons 1/5/20) + block-bootstrap CI (`block_bootstrap_ci`); paired permutation (combined vs best single-pillar) via `permutation_test`; DSR and PBO/CSCV across seeds/windows; Benjamini–Hochberg FDR across four series.
> 6. **Deterministic verdict `compute_production_simulation_verdict(...) -> dict`:** explicit checks — `signal_exists`, `ic_significant`, `net_of_cost_superior_vs_controls`, `toxicity_gate_measured` (non-0/1), `robust_across_regimes`, `guardrails_consistent_with_eval13_14_15` (delta band ±323.77 USD, toxicity gate 0.7, cost budget 0.5 bps, kill-switch DD 20%/toxicity 80%/cost 5 bps, max notional 1M USD, max daily loss 50k USD). Each check: numeric threshold + rationale, finite metrics, evidence matrix. Strict-serializable via `serialize_metrics_strict`/`assert_json_valid` (`allow_nan=False`). **Never emit `{"valid": true}`.**
> 7. **Verify & seal:** `python -m py_compile src/analytics/production_simulation_evaluation.py` + targeted `pytest -q tests/test_production_simulation_evaluation.py` must pass. Emit strict artifact, then **update this handoff in place** to seal EVAL-19 (verdict, artifact paths, key numbers, timestamps, test/compile results). If incomplete, commit/push partial module and leave exact next line/blocker here.

**Constraints:** paper-only; `.env` absent, `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no network calls to exchanges, no NEXT9 unblock, no enumerating `research_state/`, no full 865-file test suite, no new `phaseNN_*_post_attribution_seal_orchestrator` wrappers, do not re-open sealed EVALs. `scripts/run_backtest.py` is vacuous smoke test.

**If EVAL-19 is already sealed when you read this:** STOP — no next EVAL defined. Do not re-open sealed EVALs, do not create phase wrappers, do not do handoff-only/no-op work.

---

## SEALED EVALUATIONS (do not re-open)

- **EVAL-02..EVAL-15:** sealed per prior campaign (see key artifacts below). EVAL-12/13/14/15 GO; EVAL-06/10 NO-GO (legitimate).
- **EVAL-16 SEALED (NO-GO, legitimate, measured 2026-11-13T07:04:26Z):** `src/analytics/options_surface_greeks_evaluation.py` + `tests/test_options_surface_greeks_evaluation.py` (21) + `research_state/OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}`. Verdict NO-GO 5/9 on real 30-quote BTC chain (`data/raw/options_btc_synthetic.json`, spot 65000): BS-vs-mark max abs 8516.3642; parity max abs 6634.6831; delta err mean 0.3402/max 0.8494; butterfly violation (max 0.4006) on reconstructed grid. Data-quality/greeks failures are true data state — do not fudge.
- **EVAL-17 SEALED (NO-GO, legitimate, 2026-11-13T08:00:05Z):** `src/analytics/orderflow_alpha_toxicity_evaluation.py` + `tests/test_orderflow_alpha_toxicity_evaluation.py` (23) + `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`. Real BTC orderflow (1000 trades/20 liqs/8 funding). Causal net_aggression; IC mean -0.00820, t -1.3512, p 0.0889 (FAIL ic_significant); VPIN mean 0.4408, gate-engagement 0.225; with-signal Sharpe -53.36 vs flat 0.0. Verdict NO-GO 4/5.
- **EVAL-18 SEALED (NO-GO, legitimate, 2026-11-13T08:10:00Z):** `src/analytics/integrated_options_orderflow_evaluation.py` + `tests/test_integrated_options_orderflow_evaluation.py` (28) + `research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z.{json,md}`. Integrated options+orderflow net-of-cost (seeds 1–5) vs 3 controls; combined Sharpe -37.07, options-only -63.79, orderflow-only -37.28, flat 0.0; toxicity gate engagement 0.225; verdict NO-GO 5/7 (options_signal_exists FAIL due static reconstructed surface; combined_net_of_cost_superior FAIL).

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Safety:** `.env` **absent**; `.env.example:15` `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`. Paper-only.
- **Data (verified):** `data/raw/options_btc_synthetic.json` = 30 BTC quotes, 3 expiries, calls+puts, stored greeks/IV (synthetic, internally inconsistent — measured by EVAL-16). `data/raw/orderflow_btcusdt_synthetic.json` = 1000 trades + 20 liquidations + 8 funding, BTCUSDT. No ETH/SOL raw options/orderflow files (synthetic fallback). `DEFAULT_SPOT["BTC"]=65000.0`, `DETERMINISTIC_NOW=2026-10-31 00:00:00+00:00`.
- **Key sealed artifacts:** `HEDGE_COST_OPTIMIZER_20261113T004000Z`, `REAL_WF_CERTIFICATION_20261113T010508Z`, `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z`, `GAMMA_INVENTORY_HEDGE_20261112T221000Z`, `FINAL_STRATEGY_CERTIFICATION_20261113T015226Z`, `PAPER_DEPLOYMENT_READINESS_20261113T030007Z`, `PAPER_EXECUTION_HARDENING_20261113T045715Z`, `OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z`, `ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z`, `INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z`.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders; EVAL-16/17/18 modules for signal patterns; options/orderflow/IV-surface primitives as noted in prior sealed handoff state.
- **Environment:** Python 3.12.3; deps installed (numpy/pandas/scipy/pydantic/pytest/PyYAML/requests). No mypy/ruff/flake8 — use `python3 -m py_compile` + targeted pytest. Never run full 865-file pytest. Never enumerate `research_state/`.

---

## BOTTLENECKS REMOVED / CLEARED (2026-11-13T10:08:00Z)

| Bottleneck | Resolution |
|---|---|
| Conflicting/stale handoff content (EVAL-18 marked ACTIVE in older blocks while also sealed; "campaign complete" vs pending EVAL-19) | **CLEARED.** Handoff consolidated: single authoritative `INIT-2026-11-13T10:08:00Z-EVAL-19-ACTIVE` block at top; EVAL-02..EVAL-18 marked sealed; stale active blocks removed. |
| Competing handoff files | **CLEARED (verified).** Root handoffs are retired pointers (no task IDs); only `research_state/durable_handoff.md` is actionable. |
| Missing next heavy-work target after EVAL-18 | **CLEARED.** EVAL-19 explicitly defined with mandatory deliverables, heavy-work floor, and seal procedure. |
| Safety ambiguity | **CLEARED.** `.env` absent, `LIVE_TRADING_ENABLED=false`, no NEXT9 unblock — paper-only enforced. |

---

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Work queue: **EVAL-02..EVAL-18 SEALED; EVAL-19 ACTIVE (must be implemented and sealed).**
- Each session must ship real module + numeric-invariant tests + CLI + strict artifact for the active EVAL (no wrappers/stubs/no-ops). A session ending with no new EVAL artifact is FAILED.
- If incomplete: commit/push partial module and leave exact next line/blocker here. Never leave tree clean with a pending EVAL.
- Final responses must not ask follow-up questions.
