# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission (inferred priority):** cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation**. The deliverable is the strategy and a *trustworthy* measurement of its performance, not orchestrator wrappers and not a favourable-looking number produced by a broken harness.

**Refreshed:** 2026-11-13T15:48:00Z (UTC) — EVAL-20 **SEALED** (NO-GO, 7/8 PASS; only `sample_adequate_declared` FAIL on 239 returns / 3 windows). **EVAL-21 is ACTIVE** — the only task that can convert the honest "no verdict possible" into a real net-of-cost verdict. `src/analytics/measurement_validity_evaluation.py` + 26 tests are the frozen reuse primitives for EVAL-21.

**Authority:** this file is the only actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope, never unblock NEXT9).

---

## INITIAL TASK MESSAGE — 2026-11-13T15:48:00Z (copy-paste to the next agent — EVAL-21 ACTIVE, DATA ACQUISITION)

**TASK ID:** `INIT-2026-11-13T15:48:00Z-EVAL-21-SAMPLE-ADEQUACY`
**STATUS:** **ACTIVE, not started.** EVAL-20 is SEALED (do not re-open). EVAL-02..EVAL-20 are all sealed. EVAL-21 is the **only** thing that can turn the honest "no verdict possible" into a real net-of-cost verdict.

### Why EVAL-21 exists (measured this session, 2026-11-13T12:51–12:53Z)

EVAL-20 proved the harness is now valid and that the **only** remaining blocker is the **sample**, not the code. The current tape is 1,000 BTCUSDT trades over **20 minutes** → **240 bars / 239 returns / 3 walk-forward windows**. The pre-declared adequacy floor is `n_returns >= 1000` **and** `n_windows >= 20`. At n=3 the minimum detectable |IC| is **1.62** — larger than any plausible crypto-alpha IC — so **no net-of-cost GO/NO-GO can ever be drawn** until a longer tape exists. The previous handoff explicitly forbade "widening walk-forward parameters to manufacture windows" and "fabricating a longer series" — correct, but it left no path forward. EVAL-21 is that path.

### The EVAL-21 mission (heavy-work floor — no handoff-only work, no no-ops)

> A session that ends without a new EVAL-21 artifact (module + tests + CLI output + verification log) is **FAILED**. Do not re-open sealed EVALs (incl. EVAL-20). Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers. Do not enumerate `research_state/`. Do not run the full test suite. Do not edit `.github/workflows/main.yml`.

1. **Real acquisition module:** `src/analytics/sample_adequacy_acquisition.py` — deterministic, paper-only, fully offline. It must:
   - **Reuse the EVAL-20 primitives unchanged** (`build_pillar_signals`, `simulate_pillar`, `adequacy_report`, `periods_per_year`, `sharpe_from_returns` from `measurement_validity_evaluation.py`). Do **not** fork them.
   - **Load a longer tape if one exists**; if not, **build a reproducible, offline, strictly-causal synthetic tape** that meets or exceeds the adequacy floor (`n_returns >= 1000` **and** `n_windows >= 20`) and is **clearly labelled synthetic** — never presented as real market data, never silently mixed with the real snapshot. The synthetic tape must be seeded and byte-reproducible, and must contain genuine orderflow microstructure (trade sides/sizes/timestamps) so the existing causal signal stack can run on it unchanged.
   - Emit the **same** validity battery as EVAL-20 (adequacy, degeneracy, sizing consistency, per-bar Sharpe, gross/net/turnover/cost, IC+power) **plus** a `data_provenance` block (`real` vs `synthetic`, seed, span, trade count) so the verdict can never be mistaken for a real-data result.
   - Never emit `{"valid": true}`. Strict-serialise with `serialize_metrics_strict` / `assert_json_valid` (`allow_nan=False`).
2. **Tests:** `tests/test_sample_adequacy_acquisition.py` — 12–18 numeric-invariant tests: adequacy floors met on the synthetic tape, reproducibility (two builds byte-identical), causal signal alignment (no lookahead — signal at bar `t` uses only trades `<= bar_end[t]`), degeneracy handling, sizing consistency, per-bar Sharpe recomputable, `data_provenance` correctness, strict serialization, `never {"valid": true}`.
3. **CLI:** `python -m src.analytics.sample_adequacy_acquisition --out research_state/`.
4. **Strict artifact:** `research_state/SAMPLE_ADEQUACY_ACQUISITION_<UTC>.{json,md}`.
5. **Verification (run and paste output into the artifact's `verification` block):**
   - `python3 -m py_compile src/analytics/sample_adequacy_acquisition.py tests/test_sample_adequacy_acquisition.py`
   - `python3 -m pytest -q tests/test_sample_adequacy_acquisition.py`
6. **Seal:** replace this INITIAL TASK MESSAGE section with the verdict/checks/evidence, with real numbers.

> **EVAL-21 verdict checks — all must PASS for GO:**
> - `measurement_reproducible`: two runs byte-identical (determinism).
> - `sample_adequate_declared`: `n_returns >= 1000` **and** `n_windows >= 20` on the acquired/constructed tape; both counts emitted.
> - `causal_no_lookahead`: signal at each bar uses only trades with `timestamp <= bar_end`; asserted in code and tested.
> - `sizing_consistent`: requested `max_position_pct` == `RiskConfig.max_position_pct`; zero swallowed `RiskLimitError`; rejections counted and reported.
> - `sharpe_basis_valid`: per-bar Sharpe reproducible from emitted returns; annualisation = `periods_per_year(bar_duration_seconds)`.
> - `non_degenerate_pillars_reported`: degenerate legs flagged (`options_leg_degenerate` may be `true` if the chain is still a single snapshot — that is a *data* limitation to be reported, not hidden).
> - `net_of_cost_honest`: gross, net, turnover, cost bps for all four series; cost non-negative; net = gross − cost within 1e-9.
> - `ic_reported_with_power`: IC mean, t-stat, n, and MDE emitted; MDE at the acquired `n` must be small enough to detect a plausible IC (e.g. `<= 0.05`).
> - `strict_serialization`: `allow_nan=False`; no `{"valid": true}`.

> **Sealing rules:** A `synthetic`-provenance GO is a **successful** session **if and only if** the `data_provenance` block is unambiguous and the artifact states plainly that the net-of-cost verdict is on **synthetic** data and must be re-confirmed on a real tape before any capital decision. **Do not** relabel synthetic as real. **Do not** fabricate a real exchange feed or make network calls. If a real longer tape is added to `data/raw/` by a human, the module must auto-detect and prefer it, and mark `data_provenance: "real"`.

**Constraints:** paper-only; `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no `.env` creation, no venue/config/credential mutation, no network calls to exchanges, no NEXT9 unblock, no enumerating `research_state/`, no full test suite, no new `phaseNN_*` wrappers, do not re-open sealed EVALs (incl. EVAL-20), do not modify `.github/workflows/main.yml`. `scripts/run_backtest.py` is a vacuous smoke test.

---

## INITIAL TASK MESSAGE — 2026-11-13T11:56:00Z (copy-paste to the next agent — EVAL-20 SEALED, DO NOT ACTION)

**TASK ID:** `INIT-2026-11-13T11:56:00Z-EVAL-20-MEASUREMENT-VALIDITY`
**STATUS:** **SEALED (NO-GO, legitimate, 2026-11-13T12:53:00Z).** Do not re-open. Evidence below. The task text is retained only as a historical record of the definition of done that was met.

### EVAL-20 seal (measured this session)

- **Module:** `src/analytics/measurement_validity_evaluation.py` (1161 lines).
- **Tests:** `tests/test_measurement_validity_evaluation.py` — **26 passed** (`python3 -m pytest -q tests/test_measurement_validity_evaluation.py`).
- **Artifact:** `research_state/MEASUREMENT_VALIDITY_EVAL_20261113T125227Z.{json,md}`.
- **Verdict:** **NO-GO — 7/8 checks PASS.** The one FAIL is `sample_adequate_declared` (239 returns / 3 windows vs floors 1000/20) — the legitimate "sample inadequate" outcome.
- **Measured numbers (honest, per-bar, bar-duration annualisation = 2,102,400):**
  - combined: gross **−0.033720**, net **−0.033831**, cost **1.1071 bps**, net Sharpe **−130.82**, rejections **0**
  - options_only: gross **0.004714**, net **0.004603**, cost **1.1091 bps**, net Sharpe **8.9341** (driven by the **degenerate** options leg, unique=1 → this is an artefact of a constant, not an edge)
  - orderflow_only: gross **−0.009785**, net **−0.009896**, cost **1.1091 bps**, net Sharpe **−22.59**
  - flat (control): **0.0** gross/net/Sharpe — correct after the PnL fix (previously it erroneously returned the underlying)
- **Degenerate pillar confirmed:** options leg has `n_unique == 1` (`0.3333` × 240 bars).
- **Sizing fixed:** requested `max_position_pct=0.20` == enforced `RiskConfig.max_position_pct=0.20`; **0** swallowed rejections (the EVAL-18/19 pathology is gone; a control test forces a real breach and confirms rejections are counted, not swallowed).
- **Sharpe fixed:** per-bar, annualisation derived from bar duration (2,102,400 = 365·24·3600/15); window-level Sharpe reported with its window count (5 sub-windows over the 3 WF windows).
- **Cost model fixed:** flat control now exactly 0; cost is monotone non-increasing in spread bps (0.0/0.5/1.0/5.0 verified); net = gross − cost within 1e-9.
- **Determinism:** two independent CLI runs produced byte-identical content (only `generated_at` differs).

### What EVAL-20 definitively established

1. The EVAL-18/19 harness invalidity (3-point Sharpe at 252, constant options pillar, swallowed `RiskLimitError`, flat control echoing the underlying) is **fixed and locked by 26 tests**.
2. The honest state is **"no net-of-cost edge demonstrable on the current 20-minute tape"** — and, more fundamentally, **"no verdict is possible on 239 returns / 3 windows"**.
3. **The sole remaining blocker is the sample.** EVAL-21 (`INIT-2026-11-13T12:53:00Z-EVAL-21-SAMPLE-ADEQUACY`) is the only next step that can move this forward without fabricating a verdict.

### Why the previous EVAL-20 was a trap (historical — measured 2026-11-13T11:44–11:55Z)

All of the following are reproducible from the committed EVAL-19 artifact `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.json` and from re-running the module.

1. **The sample is 240 bars / 20 minutes, not a strategy backtest.** `_build_bars` slices the 1,000-trade tape (`data/raw/orderflow_btcusdt_synthetic.json`, span `2026-10-31T06:32:42Z` → `06:52:48Z`) at 15 s → 240 bars, **239 usable returns**. Tape return mean `0.148 bps/bar`, std `31.26 bps`, **t = 0.073** — the underlying price series has no drift and no exploitable structure at this frequency.
2. **Only 3 walk-forward windows exist.** `train=120 / test=40 / step=40` over 240 bars → **3 windows**. Any Sharpe computed from 3 observations is noise.
3. **Sharpe is annualised at 252 from those 3 window returns.** Observed `combined -45.27`, `options_only -152.98`, `orderflow_only -195.62`, `flat 0.00`. These are arithmetic artefacts of dividing a 3-point mean by a 3-point std — they are **not** evidence of a −30 Sharpe strategy, and they are not comparable across strategies.
4. **The sizing path silently rejects two thirds of intended notional.** `_run_walkforward` is called with `max_position_pct=0.20` but constructs `RiskConfig()` whose default is `0.10`. The engine then raises `RiskLimitError: Position size exceeds limit` (`notional 16036.82 vs max_notional 8002.12` = exactly 2×), and the wrapper swallows it (`except Exception: pass`) while still booking `res.cost_usd` and still advancing `cur_qty`. Wrapper state and engine state diverge → phantom trades (91–117 booked) and phantom cost.
5. **One alpha pillar is a constant.** `_causal_options_signal_series` broadcasts a single static value to every bar: `Counter({0.3333: 240})`. IC of the options leg is exactly `0.0` at every horizon. The "combined" signal is a pure AND-gate of a constant and a noise signal → `181 flat / 59 long / 0 short` bars. It cannot be long/short-robust by construction.
6. **The orderflow alpha is not significant.** `IC mean -0.008195`, `t -1.3512`, `p 0.0889`. Even the best simple remediation measured this session — sign-flip on the orderflow leg, gated by VPIN<0.7 — nets `+1.267 bps/bar gross` against `0.724 bps/bar` of turnover cost → **`+0.543 bps/bar` net, Sharpe 0.28, i.e. ≈breakeven, not a GO**. Causal in-sample-IC sign flips (windows 40/60/80/100/120) were all **negative net** at 1.39 bps.

**Conclusion:** the honest state is "no net-of-cost edge demonstrable on this dataset with this harness". EVAL-20 must therefore first make the *measurement* trustworthy. A GO in EVAL-20 means "the harness is valid and the verdict is defensible", **not** "the strategy prints money".

### EVAL-20 sealed record (historical — do not re-open)

EVAL-20 shipped `src/analytics/measurement_validity_evaluation.py` (1161 lines) + `tests/test_measurement_validity_evaluation.py` (26 tests, all pass) + `research_state/MEASUREMENT_VALIDITY_EVAL_20261113T125227Z.{json,md}`. Verdict **NO-GO — 7/8 checks PASS** (only `sample_adequate_declared` failed on 239 returns / 3 windows). The four harness defects it was scoped to fix are **fixed and locked by tests** (per-bar Sharpe + bar-duration annualisation; degenerate-leg detection; explicit `RiskConfig(max_position_pct=requested)` with rejections counted; position-weighted PnL so flat == 0). **Do not re-implement this module. Do not re-run EVAL-20.** The measurement harness is now trustworthy; the only remaining blocker is sample size, which is EVAL-21's scope.


---

## SEALED EVALUATIONS (do not re-open)

- **EVAL-02..EVAL-15:** sealed per prior campaign. EVAL-12/13/14/15 GO; EVAL-06/10 NO-GO (legitimate).
- **EVAL-16 SEALED (NO-GO, legitimate, 2026-11-13T07:04:26Z):** `src/analytics/options_surface_greeks_evaluation.py` + tests (21) + `research_state/OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.{json,md}`. NO-GO 5/9 on the real 30-quote BTC chain (spot 65000): BS-vs-mark max abs 8516.3642; parity max abs 6634.6831; delta err mean 0.3402/max 0.8494; butterfly violation max 0.4006. Data-quality/greeks failures are true data state — do not fudge.
- **EVAL-17 SEALED (NO-GO, legitimate, 2026-11-13T08:00:05Z):** `src/analytics/orderflow_alpha_toxicity_evaluation.py` + tests (23) + `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.{json,md}`. 1000 trades/20 liqs/8 funding. `IC -0.00820`, `t -1.3512`, `p 0.0889` (FAIL `ic_significant`); VPIN mean 0.4408, gate engagement 0.225. NO-GO 4/5.
- **EVAL-18 SEALED (NO-GO, legitimate, 2026-11-13T08:10:00Z):** `src/analytics/integrated_options_orderflow_evaluation.py` + tests (28) + `research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z.{json,md}`. Combined −37.07 / options-only −63.79 / orderflow-only −37.28 / flat 0.0. NO-GO 5/7. **Shares the invalid harness described above.**
- **EVAL-19 SEALED (NO-GO, legitimate, 2026-11-13T10:52:00Z):** `src/analytics/production_simulation_evaluation.py` + tests (16, all pass) + `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.{json,md}`. NO-GO 4/6; failed `net_of_cost_superior_vs_controls` and `robust_across_regimes`; kill-switches triggered (DD 0.494440, tox 1.000000). **Its numbers are invalid for the reasons in the section above; the seal stands as "measured on an invalid harness", and EVAL-20 superseded the measurement-validity question.**
- **EVAL-20 SEALED (NO-GO, legitimate, 2026-11-13T12:53:00Z):** `src/analytics/measurement_validity_evaluation.py` + tests (26, all pass) + `research_state/MEASUREMENT_VALIDITY_EVAL_20261113T125227Z.{json,md}`. NO-GO 7/8 checks; the only FAIL is `sample_adequate_declared` (239 returns / 3 windows). All harness defects (3-point Sharpe@252, constant options pillar, swallowed `RiskLimitError`, flat-control echo) are **fixed and locked by tests**. **The measurement harness is now trustworthy; the sole remaining blocker is the sample size — see EVAL-21.**

---

## VERIFIED STATE / REUSE POINTS (ground truth)

- **Safety:** `.env` **absent**; `.env.example:15` `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`. Paper-only.
- **Data:** `data/raw/options_btc_synthetic.json` = 30 BTC quotes, 3 expiries, calls+puts, stored greeks/IV (synthetic, internally inconsistent — EVAL-16). `data/raw/orderflow_btcusdt_synthetic.json` = 1000 trades + 20 liquidations + 8 funding, BTCUSDT, **20-minute span → 240 bars / 239 returns / 3 windows** (EVAL-20 measured). No ETH/SOL raw options or orderflow files (synthetic fallback). `DEFAULT_SPOT["BTC"]=65000.0`, `DETERMINISTIC_NOW=2026-10-31T00:00:00Z`.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`, `CapacityAwareSizer`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders (`_load_options_chain`, `_load_orderflow`, `_generate_price_paths` → `(dict, list[datetime])`); `src.config_settings.RiskConfig` (**default `max_position_pct=0.1` — pass explicitly to avoid the EVAL-18/19 sizing bug**); `src.backtest.engine.WalkForwardBacktest` / `BacktestEngine`.
- **EVAL-20 reusable measurement primitives (use these for EVAL-21, do NOT fork):** `src.analytics.measurement_validity_evaluation` → `build_pillar_signals`, `simulate_pillar`, `adequacy_report`, `periods_per_year`, `sharpe_from_returns`, `per_bar_returns`, `min_detectable_ic`, `power_for_ic`, `degeneracy_report`, `ic_report`, `cost_grid_report`, `pillar_metrics`, `compute_verdict`, `evaluate_measurement_validity`, `_write_markdown`, `main`.
- **Key sealed artifacts:** `HEDGE_COST_OPTIMIZER_20261113T004000Z`, `REAL_WF_CERTIFICATION_20261113T010508Z`, `STRATEGY_EVAL_10_FINAL_GONOGO_20261113T000249Z`, `GAMMA_INVENTORY_HEDGE_20261112T221000Z`, `FINAL_STRATEGY_CERTIFICATION_20261113T015226Z`, `PAPER_DEPLOYMENT_READINESS_20261113T030007Z`, `PAPER_EXECUTION_HARDENING_20261113T045715Z`, `OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z`, `ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z`, `INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z`, `PRODUCTION_SIMULATION_EVAL_20261113T104657Z`, `MEASUREMENT_VALIDITY_EVAL_20261113T125227Z`.
- **Environment:** Python 3.12.3; numpy/pandas/scipy/pydantic/pytest/PyYAML/requests installed. No mypy/ruff/flake8 → use `python3 -m py_compile` + targeted pytest. Never run the full suite (5,252 tests / 26 s collection). Never enumerate `research_state/`.

---

## BOTTLENECKS REMOVED / CLEARED

| Bottleneck | Resolution |
|---|---|
| **EVAL-18/19 harness invalidity** (3-point Sharpe@252; constant options pillar; swallowed `RiskLimitError` from `RiskConfig()` defaulting to `0.10` vs requested `0.20`; flat control echoing the underlying price series) | **CLEARED in EVAL-20.** `measurement_validity_evaluation.py` fixes all four: per-bar Sharpe + bar-duration annualisation; degenerate-leg detection; explicit `RiskConfig(max_position_pct=requested)` with rejections counted; position-weighted PnL so flat == 0. **26 tests lock these invariants.** |
| **Sample inadequacy (239 returns / 3 windows)** — the sole remaining blocker; MDE at n=3 is 1.62 so no verdict is possible | **DIAGNOSED; fix assigned to EVAL-21** (`INIT-2026-11-13T12:53:00Z-EVAL-21-SAMPLE-ADEQUACY`). Not fixable by widening windows or fabricating a verdict — requires a longer real tape or a clearly-labelled reproducible synthetic tape. |
| Degenerate options pillar (constant `0.3333` × 240 bars) | **REPORTED, not hidden.** EVAL-20 emits `options_leg_degenerate: true` as a first-class finding; the `options_only` Sharpe 8.93 is explicitly flagged as an artefact of the constant leg, not an edge. |
| Conflicting/stale handoff content | **CLEARED.** Single authoritative state; old EVAL-20 reference removed. |
| Competing handoff files | **CLEARED.** Root handoffs are retired pointers (no task IDs); only `research_state/durable_handoff.md` is actionable. |
| Safety ambiguity | **CLEARED.** `.env` absent, `LIVE_TRADING_ENABLED=false`, no NEXT9 unblock — paper-only enforced. |
| Environment/verification bottleneck | **CLEARED.** `py_compile` OK; EVAL-20 tests 26/26 in 2.2 s. EVAL-21 can start immediately. |
| **`research_state/` bloat — 5.0 GB / 106,685 tracked files, of which 48,309 files in 188 `phase*` evidence dirs** | **CONTAINED (not deleted).** `.gitignore` extended so no further `research_state/phase*/` evidence is committed. Existing bulk stays in git history — pruning it is a maintainer decision (history rewrite), **not** an agent task. Do not `git rm -r` it. |
| 248 `scripts/generate_phase*_post_attribution_seal_orchestrator_*.py` + 554 `tests/test_phase*.py` (5,252 collected tests, 26 s) | **NOT a new bottleneck.** Pre-existing clutter; forbidden to create more; do not touch; does not block EVAL-21. |
| Edit-tool invalid-argument failures (364 in `research_state/workflow_run_diagnostics.jsonl`) | **NOT actionable in-repo.** Workflow-level tooling issue; do not attempt to fix from an agent session. |

---

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Work queue: **EVAL-02..EVAL-20 SEALED. EVAL-21 ACTIVE (`INIT-2026-11-13T12:53:00Z-EVAL-21-SAMPLE-ADEQUACY`).**
- Any new EVAL must ship a real module + numeric-invariant tests + CLI + strict artifact (no wrappers/stubs/no-ops). A session ending with no new EVAL artifact is FAILED.
- **A handoff-only commit is a failed session.** If you cannot finish, commit the partial module + tests and leave the exact next line and blocker here; never leave a clean tree with the EVAL pending.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.