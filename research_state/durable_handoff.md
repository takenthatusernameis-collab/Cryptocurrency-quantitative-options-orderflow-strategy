# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission (inferred priority):** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation**. The deliverable is the strategy and a *trustworthy* measurement of its performance, not orchestrator wrappers and not a favourable-looking number produced by a broken harness.

**Refreshed:** 2026-11-13T12:44:33Z (UTC) — this session verified: single actionable handoff; root pointers retired; `.env` absent; EVAL-19 tests 16/16 pass; **the EVAL-19/18/17/16 benchmarks are structurally invalid (measured evidence below)**; EVAL-20 as previously written was therefore unsatisfiable and has been **withdrawn and replaced**. **EVAL-20 module/tests not yet created — task remains not started.**

**Authority:** this file is the only actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope, never unblock NEXT9).

---

## INITIAL TASK MESSAGE — 2026-11-13T11:56:00Z (copy-paste to the next agent — EVAL-20 ACTIVE, REDEFINED)

**TASK ID:** `INIT-2026-11-13T11:56:00Z-EVAL-20-MEASUREMENT-VALIDITY`
**STATUS:** **ACTIVE, not started.** EVAL-02..EVAL-19 are sealed (do not re-open). The previous EVAL-20 ("Net-of-Cost Profitability & Regime Robustness Remediation", `INIT-2026-11-13T10:58:00Z-EVAL-20-PROFITABILITY-ROBUSTNESS`) is **WITHDRAWN — DO NOT ACTION IT.** It was written on the assumption that EVAL-19's NO-GO numbers were trustworthy. They are not: the harness that produced them is invalid. Chasing "profitability remediation" on top of invalid measurements is what caused five consecutive sessions (10:57–11:43Z) to end with handoff-only commits and zero artifacts.

### Why the previous EVAL-20 was a trap (measured this session, 2026-11-13T11:44–11:55Z)

All of the following are reproducible from the committed EVAL-19 artifact `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.json` and from re-running the module.

1. **The sample is 240 bars / 20 minutes, not a strategy backtest.** `_build_bars` slices the 1,000-trade tape (`data/raw/orderflow_btcusdt_synthetic.json`, span `2026-10-31T06:32:42Z` → `06:52:48Z`) at 15 s → 240 bars, **239 usable returns**. Tape return mean `0.148 bps/bar`, std `31.26 bps`, **t = 0.073** — the underlying price series has no drift and no exploitable structure at this frequency.
2. **Only 3 walk-forward windows exist.** `train=120 / test=40 / step=40` over 240 bars → **3 windows**. Any Sharpe computed from 3 observations is noise.
3. **Sharpe is annualised at 252 from those 3 window returns.** Observed `combined -45.27`, `options_only -152.98`, `orderflow_only -195.62`, `flat 0.00`. These are arithmetic artefacts of dividing a 3-point mean by a 3-point std — they are **not** evidence of a −30 Sharpe strategy, and they are not comparable across strategies.
4. **The sizing path silently rejects two thirds of intended notional.** `_run_walkforward` is called with `max_position_pct=0.20` but constructs `RiskConfig()` whose default is `0.10`. The engine then raises `RiskLimitError: Position size exceeds limit` (`notional 16036.82 vs max_notional 8002.12` = exactly 2×), and the wrapper swallows it (`except Exception: pass`) while still booking `res.cost_usd` and still advancing `cur_qty`. Wrapper state and engine state diverge → phantom trades (91–117 booked) and phantom cost.
5. **One alpha pillar is a constant.** `_causal_options_signal_series` broadcasts a single static value to every bar: `Counter({0.3333: 240})`. IC of the options leg is exactly `0.0` at every horizon. The "combined" signal is a pure AND-gate of a constant and a noise signal → `181 flat / 59 long / 0 short` bars. It cannot be long/short-robust by construction.
6. **The orderflow alpha is not significant.** `IC mean -0.008195`, `t -1.3512`, `p 0.0889`. Even the best simple remediation measured this session — sign-flip on the orderflow leg, gated by VPIN<0.7 — nets `+1.267 bps/bar gross` against `0.724 bps/bar` of turnover cost → **`+0.543 bps/bar` net, Sharpe 0.28, i.e. ≈breakeven, not a GO**. Causal in-sample-IC sign flips (windows 40/60/80/100/120) were all **negative net** at 1.39 bps.

**Conclusion:** the honest state is "no net-of-cost edge demonstrable on this dataset with this harness". EVAL-20 must therefore first make the *measurement* trustworthy. A GO in EVAL-20 means "the harness is valid and the verdict is defensible", **not** "the strategy prints money".

### MANDATORY — EVAL-20 heavy-work floor (no handoff-only work, no no-ops)

> A session that ends without a new EVAL-20 artifact (module + tests + CLI output + verification log) is **FAILED**. Do not re-open sealed EVALs. Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers. Do not enumerate `research_state/`. Do not run the full test suite. Do not edit `.github/workflows/main.yml` (maintainer-managed; the controller reverts it).

1. **Real module:** `src/analytics/measurement_validity_evaluation.py` — deterministic, paper-only, fully offline. It must:
   - Rebuild the causal signal stack from the existing primitives (reuse `_build_causal_signals`, `load_btc_options_chain`, `load_btc_orderflow` from `production_simulation_evaluation.py`; do **not** fork them).
   - **Fix the sizing inconsistency:** construct `RiskConfig(max_position_pct=<requested>, max_drawdown_limit=0.20)` and pass it explicitly; count and surface engine-side rejections instead of `except Exception: pass`.
   - **Fix the Sharpe basis:** compute Sharpe from **per-bar** returns with an annualisation factor derived from `bar_duration_seconds` (not a hard-coded 252 on 3 window returns); additionally report a window-level Sharpe with its window count so the small-sample nature is visible.
   - **Add a power/adequacy analysis:** report `n_bars`, `n_returns`, `n_windows`, minimum detectable IC at 80 % power, and an explicit `sample_adequate` boolean.
   - Emit **both** `gross` and `net` (capacity-model cost) PnL for `combined`, `options_only`, `orderflow_only`, `flat`, plus turnover and cost bps.
   - Detect and report the **degenerate-leg** condition (any pillar with <2 unique signal values) as a first-class finding.
   - Never emit `{"valid": true}`. Strict-serialise with `serialize_metrics_strict` / `assert_json_valid` (`allow_nan=False`).
2. **Tests:** `tests/test_measurement_validity_evaluation.py` — 12–18 numeric-invariant tests: bar count/return count, non-degenerate detection, sizing-cap agreement (no swallowed rejection), Sharpe basis equals per-bar recomputation, annualisation factor matches bar duration, sample-adequacy thresholds, cost monotonicity in spread bps, strict serialization, artifact shape, CLI emission, determinism (two runs byte-identical), `never {"valid": true}`.
3. **CLI:** `python -m src.analytics.measurement_validity_evaluation --out research_state/`.
4. **Strict artifact:** `research_state/MEASUREMENT_VALIDITY_EVAL_<UTC>.{json,md}`.
5. **Verification (run and paste output into the artifact's `verification` block):**
   - `python3 -m py_compile src/analytics/measurement_validity_evaluation.py tests/test_measurement_validity_evaluation.py`
   - `python3 -m pytest -q tests/test_measurement_validity_evaluation.py`
6. **Seal:** replace this INITIAL TASK MESSAGE section with the verdict/checks/evidence, with real numbers.

> **EVAL-20 verdict checks — all must PASS for GO:**
> - `measurement_reproducible`: two runs produce byte-identical artifacts (determinism).
> - `sample_adequate_declared`: `n_returns` and `n_windows` reported, and `sample_adequate` correctly reflects a pre-declared threshold (default: `n_returns >= 1000` **and** `n_windows >= 20`); if inadequate, verdict is `NO-GO (sample inadequate)` with the measured counts — that is a **legitimate, sealable** outcome.
> - `sizing_consistent`: requested `max_position_pct` equals `RiskConfig.max_position_pct`; zero swallowed `RiskLimitError`; rejections counted and equal to zero.
> - `sharpe_basis_valid`: Sharpe is computed from per-bar returns; recomputing from the emitted returns reproduces the emitted Sharpe to 1e-9; annualisation factor equals `periods_per_year(bar_duration_seconds)`.
> - `non_degenerate_pillars_reported`: any pillar with <2 unique signal values is explicitly flagged (`options_leg_degenerate: true` expected on the current dataset).
> - `net_of_cost_honest`: gross, net, turnover, and cost bps emitted for all four series; cost strictly non-negative; net = gross − cost within 1e-9.
> - `ic_reported_with_power`: IC mean, t-stat, n, and minimum detectable effect emitted.
> - `strict_serialization`: artifact validates under `assert_json_valid` with `allow_nan=False`; no `{"valid": true}` anywhere.

> **Sealing rules:** If the dataset is inadequate (expected: 239 returns, 3 windows), seal **`NO-GO — SAMPLE INADEQUATE`** with the measured counts and state plainly that no net-of-cost verdict can be drawn until a longer tape exists. **Do not** fabricate a longer series, **do not** widen the walk-forward parameters to manufacture windows, and **do not** declare the strategy profitable or unprofitable on 239 bars. `NO-GO — SAMPLE INADEQUATE` is a **successful** session if the harness fixes and the evidence are real.

**Constraints:** paper-only; `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no network calls to exchanges, no NEXT9 unblock, no enumerating `research_state/`, no full test suite, no new `phaseNN_*` wrappers, do not re-open sealed EVALs, do not modify `.github/workflows/main.yml`. `scripts/run_backtest.py` is a vacuous smoke test.

---

## SEALED EVALUATIONS (do not re-open)

- **EVAL-02..EVAL-15:** sealed per prior campaign. EVAL-12/13/14/15 GO; EVAL-06/10 NO-GO (legitimate).
- **EVAL-16 SEALED (NO-GO, legitimate, 2026-11-13T07:04:26Z):** `src/analytics/options_surface_greeks_evaluation.py` + tests (21) + `research_state/OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}`. NO-GO 5/9 on the real 30-quote BTC chain (spot 65000): BS-vs-mark max abs 8516.3642; parity max abs 6634.6831; delta err mean 0.3402/max 0.8494; butterfly violation max 0.4006. Data-quality/greeks failures are true data state — do not fudge.
- **EVAL-17 SEALED (NO-GO, legitimate, 2026-11-13T08:00:05Z):** `src/analytics/orderflow_alpha_toxicity_evaluation.py` + tests (23) + `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`. 1000 trades/20 liqs/8 funding. `IC -0.00820`, `t -1.3512`, `p 0.0889` (FAIL `ic_significant`); VPIN mean 0.4408, gate engagement 0.225. NO-GO 4/5.
- **EVAL-18 SEALED (NO-GO, legitimate, 2026-11-13T08:10:00Z):** `src/analytics/integrated_options_orderflow_evaluation.py` + tests (28) + `research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z.{json,md}`. Combined −37.07 / options-only −63.79 / orderflow-only −37.28 / flat 0.0. NO-GO 5/7. **Shares the invalid harness described above.**
- **EVAL-19 SEALED (NO-GO, legitimate, 2026-11-13T10:52:00Z):** `src/analytics/production_simulation_evaluation.py` + tests (16, all pass) + `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.{json,md}`. NO-GO 4/6; failed `net_of_cost_superior_vs_controls` and `robust_across_regimes`; kill-switches triggered (DD 0.494440, tox 1.000000). **Its numbers are invalid for the reasons in the section above; the seal stands as "measured on an invalid harness", and EVAL-20 supersedes the profitability question.**

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Safety:** `.env` **absent**; `.env.example:15` `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`. Paper-only.
- **Data:** `data/raw/options_btc_synthetic.json` = 30 BTC quotes, 3 expiries, calls+puts, stored greeks/IV (synthetic, internally inconsistent — EVAL-16). `data/raw/orderflow_btcusdt_synthetic.json` = 1000 trades + 20 liquidations + 8 funding, BTCUSDT, **20-minute span**. No ETH/SOL raw options or orderflow files (synthetic fallback). `DEFAULT_SPOT["BTC"]=65000.0`, `DETERMINISTIC_NOW=2026-10-31T00:00:00Z`.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`, `CapacityAwareSizer`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders (`_load_options_chain`, `_load_orderflow`, `_generate_price_paths` → `(dict, list[datetime])`); `src.config_settings.RiskConfig` (**default `max_position_pct=0.1` — the EVAL-20 sizing bug**); `src.backtest.engine.WalkForwardBacktest` / `BacktestEngine`.
- **Key sealed artifacts:** `HEDGE_COST_OPTIMIZER_20261113T004000Z`, `REAL_WF_CERTIFICATION_20261113T010508Z`, `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z`, `GAMMA_INVENTORY_HEDGE_20261112T221000Z`, `FINAL_STRATEGY_CERTIFICATION_20261113T015226Z`, `PAPER_DEPLOYMENT_READINESS_20261113T030007Z`, `PAPER_EXECUTION_HARDENING_20261113T045715Z`, `OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z`, `ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z`, `INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z`, `PRODUCTION_SIMULATION_EVAL_20261113T104657Z`.
- **Environment:** Python 3.12.3; numpy/pandas/scipy/pydantic/pytest/PyYAML/requests installed. No mypy/ruff/flake8 → use `python3 -m py_compile` + targeted pytest. Never run the full suite (5,252 tests / 26 s collection). Never enumerate `research_state/`.

---

## BOTTLENECKS REMOVED / CLEARED

| Bottleneck | Resolution |
|---|---|
| **Unsatisfiable EVAL-20 task (profitability remediation on an invalid benchmark)** — the direct cause of 5 consecutive handoff-only commits (10:57–11:43Z: `04f83f7cc`, `cc4a878a4`, `5c37070e5`, `33291692c`, `608cf2c1d` each touched **only** `research_state/durable_handoff.md`) | **CLEARED.** Old EVAL-20 withdrawn. Replaced by `INIT-2026-11-13T11:56:00Z-EVAL-20-MEASUREMENT-VALIDITY` with an achievable, verifiable definition of done and a legitimate `NO-GO — SAMPLE INADEQUATE` outcome. |
| Sizing-cap inconsistency producing phantom trades/cost (`max_position_pct=0.20` vs `RiskConfig()=0.10`, swallowed `RiskLimitError`) | **DIAGNOSED, fix assigned to EVAL-20 step 1.** Do not silently re-run EVAL-18/19 until fixed. |
| 3-window Sharpe annualised at 252 (artefact magnitudes −45/−153/−196) | **DIAGNOSED, fix assigned to EVAL-20 step 1** (per-bar Sharpe + bar-duration annualisation + window count). |
| Degenerate options pillar (constant `0.3333` × 240 bars) | **DIAGNOSED and reported** as a first-class check (`non_degenerate_pillars_reported`) rather than silently AND-gated away. |
| Conflicting/stale handoff content | **CLEARED.** Single authoritative state; old EVAL-20 reference removed. |
| Competing handoff files | **CLEARED.** Root handoffs are retired pointers (no task IDs); only `research_state/durable_handoff.md` is actionable. |
| Safety ambiguity | **CLEARED.** `.env` absent, `LIVE_TRADING_ENABLED=false`, no NEXT9 unblock — paper-only enforced. |
| Environment/verification bottleneck | **CLEARED.** `py_compile` OK on required analytics modules; EVAL-19 tests 16/16 in 11.3 s; pytest collection 5,252 tests in 25.8 s. EVAL-20 can start immediately. |
| **`research_state/` bloat — 5.0 GB / 106,685 tracked files, of which 48,309 files in 188 `phase*` evidence dirs** (largest single dir 1.6 GB, ~39 near-identical timestamped reports each) | **CONTAINED (not deleted).** `.gitignore` extended so no further `research_state/phase*/` evidence is committed. Existing bulk stays in git history — pruning it is a maintainer decision (history rewrite), **not** an agent task. Do not `git rm -r` it. |
| 248 `scripts/generate_phase*_post_attribution_seal_orchestrator_*.py` + 554 `tests/test_phase*.py` (5,252 collected tests, 26 s) | **NOT a new bottleneck.** Pre-existing clutter; forbidden to create more; do not touch; does not block EVAL-20. |
| Edit-tool invalid-argument failures (364 in `research_state/workflow_run_diagnostics.jsonl`) | **NOT actionable in-repo.** Workflow-level tooling issue; do not attempt to fix from an agent session. |

---

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Work queue: **EVAL-02..EVAL-19 SEALED. EVAL-20 ACTIVE (`INIT-2026-11-13T11:56:00Z-EVAL-20-MEASUREMENT-VALIDITY`).**
- Any new EVAL must ship a real module + numeric-invariant tests + CLI + strict artifact (no wrappers/stubs/no-ops). A session ending with no new EVAL artifact is FAILED.
- **A handoff-only commit is a failed session.** If you cannot finish, commit the partial module + tests and leave the exact next line and blocker here; never leave a clean tree with the EVAL pending.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.