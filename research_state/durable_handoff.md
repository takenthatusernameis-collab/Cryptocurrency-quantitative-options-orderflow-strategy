# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission (inferred priority):** Cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation**. The deliverable is the strategy and a *trustworthy* measurement of its performance, not orchestrator wrappers and not a favorable-looking number produced by a broken harness.

**Handoff refreshed:** 2026-11-13T19:10:37Z (UTC) — re-verified repo state: EVAL-02..EVAL-21 **SEALED**. **EVAL-22 is ACTIVE and UNSTARTED** (no `src/analytics/real_tape_ingestion.py`, no `tests/test_real_tape_ingestion.py`, no `research_state/REAL_TAPE_INGESTION_*`; `.env` absent). Root handoff files are retired pointers. Session-gate dependencies present/compile. Next campaign: **EVAL-22 (REAL-TAPE INGESTION GATE)** → EVAL-23 (REAL NET-OF-COST VERDICT) → EVAL-24 (OPTIONS-LEG VALIDITY) → EVAL-25 (REAL-TAPE FALSIFICATION); **EVAL-23B is the unblocked fallback**. No other blocked/inefficient session bottlenecks found in-repo beyond the documented data absence and sealed-module constraints.

**Authority:** This file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope, never unblock NEXT9).

---

## INITIAL TASK MESSAGE — 2026-11-13T19:10:37Z (copy-paste for the next agentic work session)

**TASK ID:** `INIT-2026-11-13T19:10:37Z-EVAL-22-REAL-TAPE-GATE`
**STATUS:** **ACTIVE, not started.** EVAL-02..EVAL-21 are **SEALED — do not re-open**. EVAL-22 is the active task; EVAL-23..EVAL-25 are the sequential campaign queue below (EVAL-23B is the fallback if EVAL-23 is data-blocked).

> **Start here (no discovery needed).** Re-verified at 2026-11-13T19:02:13Z: no EVAL-22 module/tests/artifacts exist; `.env` absent; only synthetic tape in `data/raw/`. The previous session(s) ended handoff-only — that is the one forbidden outcome. Produce real artifacts this session.

### Why this task (measured; do not re-litigate)
- **EVAL-21 SEALED (GO, 2026-11-13T16:51:08Z)** on a **synthetic** tape: 9/9 checks, n_bars 3400, n_returns 3399, n_windows 82, n_trades 40800, orderflow IC **0.375126** (t **6.5444**), MDE@3399 **0.048054** ≤ 0.05, sizing 0 rejections, net = gross − cost, flat control 0, strict JSON, never `{"valid": true}`. Validates the **measurement battery and pipeline**, not real alpha.
- **Re-verified 2026-11-13T17:41:22Z:** `tests/test_sample_adequacy_acquisition.py` + `tests/test_measurement_validity_evaluation.py` = **45 passed** (83.8 s). This is the regression baseline.
- **The only tape in `data/raw/` is synthetic:** `data/raw/orderflow_btcusdt_synthetic.json`, SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`, 1000 trades + 20 liquidations + 8 funding rates, span 2026-10-31T06:16:23Z–07:16:21Z (~1 h), venue `synthetic`, symbol `BTCUSDT` → **240 bars / 239 returns / 3 walk-forward windows** at 15 s bars (train 120 / test 40 / step 40). `data/processed/*.json` are derived from the same synthetic tape — **not real data**. **No real tape exists.**
- **Confirmed EVAL-21 defect (do NOT fix the sealed file):** `src/analytics/sample_adequacy_acquisition.py:346` `acquire_tape()` iterates `data/raw/orderflow_*.json` but loads each candidate via `load_btc_orderflow()` (imported at `:86` from `production_simulation_evaluation`, which delegates to `src/campaign/integrated.py:184` `_load_orderflow`). That loader **hardcodes** `data/raw/orderflow_<symbol>usdt_synthetic.json` (`:188`) and never reads the iterated path, and `acquire_tape` only accepts filenames ending in `orderflow_btcusdt_synthetic.json` (`:369`). Consequences: (a) **no arbitrary real tape can ever be discovered or loaded**; (b) **if the synthetic tape ever met the floors, it would be labeled `provenance="real"`** — it does not misfire today only because the synthetic tape has 239 returns < 1000. EVAL-22 must implement strict real-only discovery via `DataLoader().load_orderflow(path, ...)` (`src/data/loader.py:103`) and a regression test that the canonical synthetic file is never accepted as real.
- **Confirmed second defect:** `src/analytics/measurement_validity_evaluation.py:751` `evaluate_measurement_validity()` calls `load_btc_orderflow()` with **no snapshot parameter** — it cannot be pointed at a real tape. Do not call it for real-data verdicts; drive the lower-level primitives instead.
- **Bottleneck removed:** real-data absence is no longer a silent blocker. EVAL-22 seals with an explicit, measured `NO-GO (no adequate real tape)` plus the exact data contract; EVAL-23B supplies unblocked fallback work if no tape exists.

### Mission (heavy-work floor — NO handoff-only work, NO no-ops)
> **A session that ends without new EVAL-22 artifacts (module + tests + CLI output + verification evidence) is FAILED.** Do not re-open sealed EVALs (incl. EVAL-21). Do not modify `src/analytics/sample_adequacy_acquisition.py` or `src/analytics/measurement_validity_evaluation.py`. Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers/scripts/tests. Do not enumerate `research_state/`. Do not run the full test suite. Do not modify `.github/workflows/main.yml`. Do not fabricate a real exchange feed or relabel synthetic as real.

### Deliverables (all required)
1. **Module:** `src/analytics/real_tape_ingestion.py` (deterministic, offline, paper-only).
   - `discover_real_orderflow_tapes(data_raw_dir: Path = Path("data/raw")) -> List[Path]`: glob `orderflow_*.json`; **exclude** any name containing `synthetic`; deterministic sort.
   - `load_real_tape(path) -> dict`: load via `DataLoader().load_orderflow(path, venue=<from filename>, symbol=<from filename>)` (see `src/data/loader.py:103`); reject if venue is `synthetic`/empty or the filename/content matches the canonical synthetic tape; record path, venue, symbol, content SHA-256, span, n_trades, n_bars, n_returns, n_windows.
   - `validate_real_tape(...)`: adequacy (`n_returns >= 1000` **and** `n_windows >= 20`), causal no-lookahead (bars from `_build_bars`; no trade after `bar_end[t]` may affect bar `t`), microstructure sanity (price > 0, size > 0, side in {buy,sell}, timestamps monotone non-decreasing), symbol/venue consistency.
   - If an adequate real tape is found: drive the **same sealed EVAL-20 primitives** (`build_pillar_signals`, `simulate_pillar`, `adequacy_report`, `ic_report`, `compute_verdict`, `pillar_metrics`, ...) with the real snapshot, following `sample_adequacy_acquisition.py:428` `evaluate_sample_adequacy`'s pattern. **Do NOT call `evaluate_measurement_validity()`** (defect above). If none: emit `NO-GO (no adequate real tape)` with per-candidate counts and the exact shortfall.
   - Reuse (import, do not fork): `_build_bars` (`src/analytics/integrated_options_orderflow_evaluation.py:288`), `per_bar_returns`, `adequacy_report`, `ic_report`, `periods_per_year`, `sharpe_from_returns`, `compute_verdict`, `serialize_metrics_strict`, `assert_json_valid`; `_count_windows_for_bars` / `_tape_adequacy` (`sample_adequacy_acquisition.py:137` / `:147`) may be reused as helpers.
   - Never substitute synthetic for real; never emit `{"valid": true}`; strict JSON `allow_nan=False`; no network/exchange calls.
2. **Tests:** `tests/test_real_tape_ingestion.py` — **10–16 numeric-invariant tests** covering:
   - discovery excludes `*_synthetic.json` and includes `orderflow_<venue>_<symbol>_<UTC>.json`;
   - adequate real fixture → `data_provenance="real"`, path recorded;
   - inadequate real fixture → `NO-GO` with exact shortfall (`n_returns`, `n_windows`, `n_trades`);
   - malformed/empty tape rejected (not silently accepted);
   - `venue="synthetic"` / filename containing `synthetic` rejected as real;
   - causal no-lookahead on the real fixture (mutating a future trade must not change earlier bars);
   - microstructure rejects negative price/size, bad side, non-monotone timestamps;
   - adequacy counts match `_build_bars` / `per_bar_returns` / window helper;
   - strict serialization (`allow_nan=False`), no `{"valid": true}`;
   - determinism (two runs byte-identical);
   - content fingerprint changes when the tape changes;
   - CLI writes both `.json` and `.md`.
3. **CLI:** `python -m src.analytics.real_tape_ingestion --out research_state/ [--data-dir data/raw]`.
4. **Strict artifacts:** `research_state/REAL_TAPE_INGESTION_<UTC>.{json,md}`.
5. **Verification (run and record outputs):**
   - `python3 -m py_compile src/analytics/real_tape_ingestion.py tests/test_real_tape_ingestion.py`
   - `python3 -m pytest -q tests/test_real_tape_ingestion.py`
   - `python3 -m pytest -q tests/test_sample_adequacy_acquisition.py tests/test_measurement_validity_evaluation.py` (expect **45 passed**; proves no regression).
6. **Seal:** update this handoff in place: mark EVAL-22 sealed with verdict/checks/evidence (real numbers, artifact paths), and set the next active task (EVAL-23 if an adequate real tape was found; otherwise EVAL-23B).

### EVAL-22 verdict checks
The sealed `compute_verdict` (`measurement_validity_evaluation.py:650`) emits **exactly these 8 checks** — use them verbatim; do not invent new check names (the artifact must be comparable to EVAL-20/21). It returns `{"checks": [...], "n_checks": 8, "n_passed": N, "all_checks_pass": bool, "verdict": "GO"|"NO-GO"}`.

| # | Check (verbatim) | EVAL-22 requirement |
|---|---|---|
| 1 | `measurement_reproducible` | two consecutive EVAL-22 runs byte-identical |
| 2 | `sample_adequate_declared` | `n_returns >= 1000` **and** `n_windows >= 20`; both counts emitted (NO-GO legitimate if unmet) |
| 3 | `sizing_consistent` | requested `max_position_pct == RiskConfig.max_position_pct`; zero swallowed `RiskLimitError`; rejections counted/reported |
| 4 | `sharpe_basis_valid` | per-bar Sharpe reproducible; annualisation = `periods_per_year(bar_duration_seconds)` |
| 5 | `non_degenerate_pillars_reported` | degeneracy report emitted for every pillar |
| 6 | `net_of_cost_honest` | `cost_detail["complete"] and cost_detail["non_negative"]` both true |
| 7 | `ic_reported_with_power` | `ic_detail` contains keys `ic_mean` and `min_detectable_ic_at_n` |
| 8 | `strict_serialization` | `allow_nan=False`; no `{"valid": true}` |

**Exact `compute_verdict` call** (positional order matters): `compute_verdict(adequacy, sizing_consistent, sizing_detail, sharpe_ok, sharpe_detail, degeneracy, cost_detail, ic_detail, determinism_ok, never_valid_true)`.

Required dict keys (verified from the sealed driver):
- `adequacy` ← `adequacy_report(n_returns, n_windows, bar_returns, ic_observations)`.
- `sizing_detail`: `requested_max_position_pct`, `risk_config_max_position_pct`, `rejections`, `max_drawdown_limit`, `sizing_consistent` (true iff `|enforced − requested| <= 1e-12` **and** `rejections == 0`).
- `sharpe_detail`: `annualisation`, `expected_annualisation`, `sharpe`, `abs_error`; `sharpe_ok` iff `|annualisation − expected| <= 1e-12` and `|sharpe − sharpe_from_returns(net, annualisation)| <= 1e-9`.
- `degeneracy` ← `degeneracy_report(...)`; needs `any_degenerate` (must not be `None`).
- `cost_detail`: `complete` (all of `gross_return_total`, `net_return_total`, `turnover`, `total_cost_bps` present in each series) and `non_negative` (`total_cost_bps >= 0` for all series). `pillar_metrics()` (`:613`) already emits exactly these keys.
- `ic_detail`: `{"ic_mean": ..., "min_detectable_ic_at_n": ...}` — must contain both keys.

Additional EVAL-22-specific assertions (**module-level, not** `compute_verdict` checks — put them in the artifact's `real_tape_*` block and in tests):
- `real_tape_discovery`: `discover_real_orderflow_tapes` returns only non-synthetic candidates; the canonical synthetic file is never accepted.
- `real_tape_loaded`: at least one candidate loaded with provenance `"real"`, path + venue + symbol + fingerprint.
- `causal_no_lookahead`: asserted and tested on real data.
- `microstructure_sane`: prices > 0, sizes > 0, sides in {buy,sell}, timestamps monotone non-decreasing.

**On `ic_reported_with_power`:** the sealed check only requires the two keys to be present — it is a *reporting* check, not a significance gate. Do **not** invent an `MDE <= 0.05` gate: MDE `= (z_{0.975}+z_{0.80})/sqrt(n)` (`min_detectable_ic`, `:221`) is `0.0886` at the adequacy floor `n=1000` and only reaches `0.05` at `n >= 3140` (measured), so that gate is unsatisfiable for a just-adequate tape. The honest form for the *artifact narrative* (not the sealed check): report MDE at observed `n`, declare an effect only when `|IC| >= MDE(n)`, and report power at the observed `n`.

- **If no adequate real tape exists:** the session must still ship module + tests + an explicit `NO-GO (no adequate real tape)` artifact with the measured shortfall and the exact data request. This is a legitimate, sealable outcome.

### Data contract for the user (exact request)
Drop a real orderflow tape at `data/raw/orderflow_<venue>_<symbol>_<UTC>.json` (or `data/raw/orderflow_<venue>_<symbol>.json`) with either a bare list or `{"trades":[...], "liquidations":[...], "funding_rates":[...], "symbol":..., "venue":...}`. Each trade needs `timestamp`, `price`, `size`, `side` (buy/sell); optional `trade_id`. Adequacy requires **>= 1000 per-bar returns** and **>= 20 walk-forward windows** (≈ >= 1000 bars at 15 s, i.e. >= ~4.2 h of continuous prints). Without that, no net-of-cost verdict is possible; EVAL-22 will seal NO-GO with the exact shortfall.

### Session completion gate (all boxes must be true)
- [ ] `src/analytics/real_tape_ingestion.py` exists and `py_compile` passes.
- [ ] `tests/test_real_tape_ingestion.py` has >= 10 tests and passes.
- [ ] `research_state/REAL_TAPE_INGESTION_<UTC>.{json,md}` exists with `verdict` and `verdict_checks`.
- [ ] 45-test regression baseline still passes.
- [ ] This handoff is updated with measured numbers and the next task.
- [ ] `git status` shows the new files; partial work is committed or explicitly recorded here.

### Hard constraints
- Paper-only: `.env` **absent** and must stay absent; `.env.example` has `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`. No live enablement, no `.env` creation, no venue/config/credential mutation, no exchange network calls.
- Do not re-open sealed EVALs (incl. EVAL-21). Do not widen WF params to manufacture windows or fabricate longer series as "real".
- `scripts/run_backtest.py` is a vacuous smoke test — not evidence of edge.
- If incomplete, commit partial module+tests and record measured numbers/blockers/next line here; never leave a clean tree with EVAL-22 pending and never produce a handoff-only session.

---

## NEXT FOCUS CAMPAIGN (heavy-work floor per session)

| Eval | Focus | Dependency | Heavy-work floor | If data absent |
|---|---|---|---|---|
| **EVAL-22 (ACTIVE)** | Real-tape ingestion gate | none | `real_tape_ingestion.py` + 10–16 tests + CLI + strict artifact; NO-GO if no real tape | n/a — NO-GO is the seal |
| **EVAL-23** | Real net-of-cost verdict | EVAL-22 finds adequate real tape | drive sealed EVAL-20 primitives on real tape (not the hardcoded top-level function); GO only if net-of-cost + multiple-testing corrected; artifact | go to EVAL-23B |
| **EVAL-23B** | Exchange export adapters (fallback) | none | `src/data/exchange_exports.py`: deterministic OKX/Binance/Deribit trade-export parsers → `OrderflowSnapshot`; fixtures + 12 tests + CLI; no network | n/a |
| **EVAL-24** | Options-leg validity | real option chain | `src/analytics/options_chain_validation.py`: quote sanity, put-call parity, no-arb bounds, greeks/IV surface; tests + CLI; NO-GO with exact chain shortfall | ship validator + tests |
| **EVAL-25** | Real-tape falsification | EVAL-23 | parameter perturbation, placebo/label shuffle, subperiod stability, Benjamini-Hochberg correction; artifact | n/a |

**Campaign rule:** each session must ship at least one new module + numeric-invariant tests + CLI artifact. Handoff-only sessions, wrappers, stubs, and re-litigating sealed EVALs are FAILED. If a data-gated eval cannot run, execute its fallback; never idle.

---

## BOTTLENECK REMOVAL — ACTIONS THIS REFRESH (2026-11-13T19:02:13Z)
- **Single actionable handoff enforced:** confirmed `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers; this file remains the only task source.
- **EVAL-22 still unstarted (handoff-only drift risk):** re-verified absent module/tests/artifacts and refreshed the initial task message timestamp/ID to `INIT-2026-11-13T19:02:13Z-EVAL-22-REAL-TAPE-GATE` so the next session has an unambiguous, current directive.
- **Bottlenecks preserved from prior analysis (still true):** no real tape in `data/raw/` (only synthetic, SHA-256 `c75ced1994a78a2b...`); sealed EVAL-21 real-tape discovery defect (`sample_adequacy_acquisition.py:346` + hardcoded synthetic loader) and `evaluate_measurement_validity()` no-snapshot defect — EVAL-22 must implement strict real-only discovery and drive lower-level primitives, not modify sealed modules.
- **Safety/invariants re-verified:** `.env` absent, `.env.example` `LIVE_TRADING_ENABLED=false`, paper-only, NEXT9 out of scope; no live enablement/credentials/workflow edits; `research_state/` bloat and phase-wrapper/test-suite sprawl remain contained (no deletions/history rewrites, targeted tests only).
- **No additional in-repo blocked sessions found:** session-gate scripts (`scripts/run_session_gate.py`, `check_paper_ops_readiness.py`, `validate_next9_approval_artifact.py`) exist and compile; workflow diagnostics live in `research_state/` (not in-repo actionable from this session).

## BOTTLENECK REMOVAL — ACTIONS PRIOR REFRESH (2026-11-13T17:41:22Z)
- **Handoff-only session (the live bottleneck):** the prior refresh (17:34Z) restated EVAL-22 but no code was written — EVAL-22 was ACTIVE and UNSTARTED at 17:41:22Z. **Fixed by making this message zero-discovery:** the task now carries exact file:line reuse points, verified constants, the measured baseline (45 passed), the confirmed EVAL-21 defect location, and the synthetic tape's SHA-256 so "is this real?" needs no exploration. Start coding from the Deliverables section directly.
- **Real-tape detection defect** (`sample_adequacy_acquisition.py:346` loads the canonical synthetic path; would label synthetic as `"real"` if it met floors): **scoped to EVAL-22**. Sealed EVAL-21 is not modified; EVAL-22 implements strict real-only discovery + a regression test that the synthetic file is never accepted.
- **Hardcoded synthetic loader** (`measurement_validity_evaluation.py:751` `evaluate_measurement_validity()` takes no snapshot): **documented as unusable for real data**; EVAL-22 drives the lower-level primitives instead. Do not fork it.
- **No real tape** (`data/raw/` = one synthetic orderflow tape, 239 returns / 3 windows; `data/processed/` derived from it): **converted from a silent blocker into an explicit, sealable NO-GO** with exact shortfall and a user data contract; EVAL-23B is the unblocked fallback.
- **Stale/competing handoff text**: the superseded EVAL-21 task message was removed from the active queue (kept only as a sealed record); root files are retired pointers. **Single durable handoff enforced.**
- **Full-suite / `research_state/` bloat**: constraints restated (targeted tests only, no enumeration, no new `phase*` wrappers).
- **Impossible power gate**: the prior EVAL-22 text required "MDE ≤ 0.05" as a verdict check, but `min_detectable_ic` is 0.0886 at the adequacy floor `n=1000` and only reaches 0.05 at `n >= 3140` (measured) — the check was unsatisfiable for a just-adequate tape. **Fixed:** EVAL-22 now requires reporting MDE at the observed `n` and declaring an effect only when `|IC| >= MDE(n)` (the statistically honest form), plus power at observed `n`.
- **Safety**: `.env` absent, `LIVE_TRADING_ENABLED=false`, paper-only — unchanged.

---

## SEALED EVALUATIONS (do not re-open)

- **EVAL-02..EVAL-15:** sealed per prior campaign (EVAL-12/13/14/15 GO; EVAL-06/10 NO-GO legitimate).
- **EVAL-16 SEALED (NO-GO, 2026-11-13T07:04:26Z):** `research_state/OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.*` — real 30-quote BTC chain data-quality/greeks failures are true state.
- **EVAL-17 SEALED (NO-GO, 2026-11-13T08:00:05Z):** `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.*` — IC -0.00820, t -1.3512, p 0.0889.
- **EVAL-18 SEALED (NO-GO, 2026-11-13T08:10:00Z):** `research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z.*` — harness invalidities later fixed by EVAL-20.
- **EVAL-19 SEALED (NO-GO, 2026-11-13T10:52:00Z):** `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.*` — measured on invalid harness; seal stands historically.
- **EVAL-20 SEALED (NO-GO, 2026-11-13T12:53:00Z):** `research_state/MEASUREMENT_VALIDITY_EVAL_20261113T125227Z.*`; module + **26 tests**. 7/8 (only `sample_adequate_declared` FAIL: 239 returns / 3 windows). Harness defects fixed and locked; sole blocker was sample size.
- **EVAL-21 SEALED (GO, 2026-11-13T16:51:08Z):** `research_state/SAMPLE_ADEQUACY_ACQUISITION_20261113T165108Z.{json,md}`; module + **19 tests**. 9/9 checks; `data_provenance="synthetic"`; n_bars 3400 / n_returns 3399 / n_windows 82 / n_trades 40800; IC 0.375126 (t 6.5444); MDE@3399 0.048054; sizing 0 rejections; net = gross − cost; flat 0; strict JSON; never `{"valid": true}`. **Synthetic only — not real-market evidence.**
- **SUPERSEDED (not sealed):** `INIT-2026-11-13T16:52:00Z-EVAL-22-REAL-TAPE-REPLICATION` — active, not started; replaced by the EVAL-22 gate above.
- **SUPERSEDED (not sealed):** `INIT-2026-11-13T17:34:00Z-EVAL-22-REAL-TAPE-GATE` — restatement that produced no artifacts (handoff-only session); replaced by `INIT-2026-11-13T17:41:22Z-EVAL-22-REAL-TAPE-GATE`.

---

## BOTTLENECKS — STATUS

| Bottleneck | Status |
|---|---|
| Handoff-only session (EVAL-22 restated at 17:34Z with no code written) | **FIXED.** Task message is now zero-discovery: exact reuse file:line, verified constants, 45-passed baseline, defect location, synthetic SHA-256. |
| Real-tape detection defect in sealed EVAL-21 (`acquire_tape` loads canonical synthetic path; would label synthetic as real if adequate) | **SCOPED TO EVAL-22.** Do not modify sealed EVAL-21; EVAL-22 implements strict real-only discovery + regression test. |
| Hardcoded synthetic loader in `evaluate_measurement_validity()` (no snapshot param) | **DOCUMENTED.** Not usable for real data; drive lower-level primitives. |
| No real tape (`data/raw/` = 1 synthetic orderflow tape, 239 returns / 3 windows; `data/processed/` derived from it) | **CONVERTED TO EXPLICIT GATE.** EVAL-22 seals `NO-GO (no adequate real tape)` with exact shortfall; user data contract above; EVAL-23B fallback work. |
| Options leg degenerate (constant signal; single 30-quote synthetic chain; EVAL-16 chain inconsistency) | **REPORTED; EVAL-24 scope.** Flag, never hide. |
| Competing/stale handoff files | **CLEARED.** Only this file actionable; root handoffs are retired pointers (no task IDs). |
| `research_state/` bloat (5.0 GB / 106,688 tracked files; 188 `phase*` dirs) | **CONTAINED.** `.gitignore` blocks new `research_state/phase*/`; do not delete/rewrite history. |
| Phase orchestrator/wrapper clutter + 5,297-test corpus | **CONTAINED.** Forbidden to add more; targeted tests only. |
| Workflow edit-tool invalid-argument failures (`research_state/workflow_run_diagnostics.jsonl`) | **NOT in-repo actionable.** Do not attempt to fix from an agent session. |
| Safety/live-trading risk | **CLEARED.** `.env` absent, `LIVE_TRADING_ENABLED=false`, paper-only. |

## VERIFIED STATE / REUSE POINTS (ground truth, re-checked 2026-11-13T17:41:22Z)

- **Data:** `data/raw/orderflow_btcusdt_synthetic.json` = SHA-256 `c75ced1994a78a2b7038885be0d49bdcdeeca51d36f91ecbfb952338ba7bcef7`, 1000 trades / 20 liquidations / 8 funding rates, span 2026-10-31T06:16:23Z–07:16:21Z (~1 h), venue `synthetic`, BTCUSDT → 240 bars / 239 returns / 3 windows (15 s bars; train 120 / test 40 / step 40). `data/raw/options_btc_synthetic.json` = 30 BTC quotes, 3 expiries (internally inconsistent — EVAL-16). No ETH/SOL raw options/orderflow. `data/processed/*.json` are derived from the synthetic tape, not real.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`, `CapacityAwareSizer`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders; `src.config_settings.RiskConfig` (default `max_position_pct=0.1` — always pass explicitly; EVAL-20 default is 0.20); `src.backtest.engine.WalkForwardBacktest` / `BacktestEngine`.
- **EVAL-20 battery (sealed, import not fork):** `src.analytics.measurement_validity_evaluation` — `build_pillar_signals` (:230), `simulate_pillar` (:319), `adequacy_report` (:465), `periods_per_year` (:154), `sharpe_from_returns` (:162), `per_bar_returns` (:173), `min_detectable_ic` (:221), `power_for_ic` (:205), `degeneracy_report` (:285), `ic_report` (:501), `cost_grid_report` (:551), `pillar_metrics` (:613), `compute_verdict` (:650), `evaluate_measurement_validity` (:751), helpers. **Caveat:** `evaluate_measurement_validity()` calls `load_btc_orderflow()` and takes no snapshot — drive the lower-level primitives with the real snapshot instead.
- **EVAL-21 acquisition helpers (reuse, do not fork):** `src.analytics.sample_adequacy_acquisition` — `_orderflow_candidates` (:130), `_count_windows_for_bars` (:137), `_tape_adequacy` (:147), `_snapshot_to_orderflow_dict` (:315), `_fingerprint_tape` (:331), `build_synthetic_orderflow_tape` (:181), `acquire_tape` (:346), `evaluate_sample_adequacy` (:428). **Do not call `acquire_tape()` for real-data verdicts** (defect above).
- **Bar builder:** `_build_bars` at `src/analytics/integrated_options_orderflow_evaluation.py:288` — slices `(bar_start, bar_end]`, causal close = last trade `<= bar_end[i]`, carried forward. Returns `bar_ends`, `bar_ends_dt`, `bar_closes`, `bar_trades`, `n_bars`, `start_timestamp`, `end_timestamp`, `bar_duration_seconds`.
- **Loader:** `DataLoader().load_orderflow(path, venue=..., symbol=...)` at `src/data/loader.py:103` — accepts bare list or dict with `trades`/`liquidations`/`funding_rates`; returns `OrderflowSnapshot` (`src/data/schemas.py:122`). Module-level wrapper `src.data.loader.load_orderflow(*args, **kwargs)` at :255.
- **Constants (verified):** `DEFAULT_BAR_DURATION_SECONDS=15.0`, `DEFAULT_TRAIN_WINDOW=120`, `DEFAULT_TEST_WINDOW=40`, `DEFAULT_STEP_SIZE=40`, `DEFAULT_MIN_RETURNS=1000`, `DEFAULT_MIN_WINDOWS=20`, `DEFAULT_MAX_POSITION_PCT=0.20`, `POWER_ALPHA=0.05`, `POWER_TARGET=0.80`, `DEFAULT_SPOT={"BTC":65000.0,"ETH":3400.0,"SOL":145.0}`, `DETERMINISTIC_NOW=2026-10-31T00:00:00Z`.
- **Environment:** Python 3.12.3; numpy/pandas/scipy/pydantic/pytest/PyYAML/requests installed. No mypy/ruff/flake8 → verify with `python3 -m py_compile` + **targeted** pytest only. Never run the full suite (5,297 tests / ~17 s collection). Never enumerate `research_state/`.
- **Verification baseline:** 45 passed (EVAL-20 26 + EVAL-21 19) at 2026-11-13T17:41:22Z (**83.8 s** wall). The cost is two `scope="module"` heavy fixtures — `tests/test_sample_adequacy_acquisition.py:50` (`evaluate_sample_adequacy`) and `tests/test_measurement_validity_evaluation.py:56` (`evaluate_measurement_validity`) — each running one full 3400-bar evaluation, not the test count. Budget ~90 s for this gate; it is not a hang.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Work queue: **EVAL-02..EVAL-21 SEALED. EVAL-22 ACTIVE (`INIT-2026-11-13T19:02:13Z-EVAL-22-REAL-TAPE-GATE`).**
- New EVALs must ship real module + numeric-invariant tests + CLI + strict artifact (no wrappers/stubs/no-ops). Handoff-only session = FAILED.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.