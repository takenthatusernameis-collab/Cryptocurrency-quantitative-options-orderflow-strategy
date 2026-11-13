# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission (inferred priority):** Cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation**. The deliverable is the strategy and a *trustworthy* measurement of its performance, not orchestrator wrappers and not a favorable-looking number produced by a broken harness.

**Handoff refreshed:** 2026-11-13T17:34:00Z (UTC) — EVAL-02..EVAL-21 are **SEALED**. Next campaign: **EVAL-22 (REAL-TAPE INGESTION GATE)** → EVAL-23 (REAL NET-OF-COST VERDICT) → EVAL-24 (OPTIONS-LEG VALIDITY) → EVAL-25 (REAL-TAPE FALSIFICATION).
**Authority:** This file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope, never unblock NEXT9).

---

## INITIAL TASK MESSAGE — 2026-11-13T17:34:00Z (copy-paste for the next agentic work session)

**TASK ID:** `INIT-2026-11-13T17:34:00Z-EVAL-22-REAL-TAPE-GATE`
**STATUS:** **ACTIVE, not started.** EVAL-02..EVAL-21 are **SEALED — do not re-open**. EVAL-22 is the active task; EVAL-23..EVAL-25 are the sequential campaign queue below (EVAL-23B is the fallback if EVAL-23 is data-blocked).

### Why this task (measured; do not re-litigate)
- **EVAL-21 SEALED (GO, 2026-11-13T16:51:08Z)** on a **synthetic** tape: 9/9 checks, n_bars 3400, n_returns 3399, n_windows 82, n_trades 40800, orderflow IC **0.375126** (t **6.5444**), MDE@3399 **0.048054** ≤ 0.05, sizing 0 rejections, net = gross − cost, flat control 0, strict JSON, never `{"valid": true}`. This validates the **measurement battery and pipeline**, not real alpha.
- **Re-verified 2026-11-13T17:34:00Z:** `tests/test_sample_adequacy_acquisition.py` + `tests/test_measurement_validity_evaluation.py` = **45 passed**.
- **The only tape in `data/raw/` is synthetic:** `orderflow_btcusdt_synthetic.json` = 1000 trades, span 2026-10-31T06:16:23Z–07:16:21Z (~1 h), venue `synthetic`, symbol `BTCUSDT` → **240 bars / 239 returns / 3 walk-forward windows** at 15 s bars (train 120 / test 40 / step 40). `data/processed/*.json` are derived from the same synthetic tape (1000 trades, identical cumulative delta), **not real data**. **No real tape exists.**
- **EVAL-21 defect to avoid (do NOT fix the sealed file):** `sample_adequacy_acquisition.acquire_tape()` iterates `data/raw/orderflow_*.json` but loads via `load_btc_orderflow()` (the canonical synthetic path) and accepts only filenames ending in `orderflow_btcusdt_synthetic.json`. It therefore (a) **cannot detect an arbitrary real tape** and (b) **would set `data_provenance="real"` for the synthetic file if it ever met the floors**. It does not misfire today only because the synthetic tape has 239 returns < 1000. EVAL-22 must implement strict real-only discovery and a regression test that the canonical synthetic file is never accepted as real.
- **Bottleneck removed:** real-data absence is no longer a silent blocker. EVAL-22 seals with an explicit, measured `NO-GO (no adequate real tape)` plus the exact data contract; EVAL-23B supplies unblocked fallback work if no tape exists.

### Mission (heavy-work floor — NO handoff-only work, NO no-ops)
> **A session that ends without new EVAL-22 artifacts (module + tests + CLI output + verification evidence) is FAILED.** Do not re-open sealed EVALs (incl. EVAL-21). Do not modify `src/analytics/sample_adequacy_acquisition.py` or `src/analytics/measurement_validity_evaluation.py`. Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers/scripts/tests. Do not enumerate `research_state/`. Do not run the full test suite. Do not modify `.github/workflows/main.yml`. Do not fabricate a real exchange feed or relabel synthetic as real.

### Deliverables (all required)
1. **Module:** `src/analytics/real_tape_ingestion.py` (deterministic, offline, paper-only).
   - `discover_real_orderflow_tapes(data_raw_dir=Path("data/raw")) -> List[Path]`: glob `orderflow_*.json`; **exclude** any name containing `synthetic`; deterministic sort.
   - `load_real_tape(path) -> dict`: load via `DataLoader.load_orderflow(path, venue=<from filename>, symbol=<from filename>)`; reject if venue is `synthetic`/empty or the filename/content matches the canonical synthetic tape; record path, venue, symbol, content SHA-256, span, n_trades, n_bars, n_returns, n_windows.
   - `validate_real_tape(...)`: adequacy (`n_returns >= 1000` **and** `n_windows >= 20`), causal no-lookahead (bars from `_build_bars`; no trade after `bar_end[t]` may affect bar `t`), microstructure sanity (price > 0, size > 0, side in {buy,sell}, timestamps monotone non-decreasing), symbol/venue consistency.
   - If an adequate real tape is found: drive the **same sealed EVAL-20 primitives** (`build_pillar_signals`, `simulate_pillar`, `adequacy_report`, `ic_report`, `compute_verdict`, `pillar_metrics`, ...) with the real snapshot, following EVAL-21's `evaluate_sample_adequacy` pattern. **Do NOT call `evaluate_measurement_validity()`** — it hardcodes `load_btc_orderflow()` (the synthetic canonical path) and is not snapshot-parameterized. If none: emit `NO-GO (no adequate real tape)` with per-candidate counts and the exact shortfall.
   - Reuse (import, do not fork): `_build_bars`, `per_bar_returns`, `adequacy_report`, `ic_report`, `periods_per_year`, `sharpe_from_returns`, `compute_verdict`, `serialize_metrics_strict`, `assert_json_valid`; `_count_windows_for_bars`/`_tape_adequacy` may be reused as helpers.
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
- `real_tape_discovery`: `discover_real_orderflow_tapes` returns only non-synthetic candidates; the canonical synthetic file is never accepted.
- `real_tape_loaded`: at least one candidate loaded with provenance `"real"`, path + venue + symbol + fingerprint.
- `sample_adequate_declared`: `n_returns >= 1000` **and** `n_windows >= 20`; both counts emitted.
- `causal_no_lookahead`: asserted and tested on real data.
- `microstructure_sane`: prices > 0, sizes > 0, sides in {buy,sell}, timestamps monotone non-decreasing.
- `sizing_consistent`: requested `max_position_pct == RiskConfig.max_position_pct`; zero swallowed `RiskLimitError`; rejections counted/reported.
- `sharpe_basis_valid`: per-bar Sharpe reproducible; annualisation = `periods_per_year(bar_duration_seconds)`.
- `net_of_cost_honest`: gross, net, turnover, cost bps for all series; cost non-negative; `net == gross − cost` within 1e-9.
- `ic_reported_with_power`: IC mean, t-stat, n, MDE at return count emitted; MDE at `n_returns` ≤ 0.05.
- `strict_serialization`: `allow_nan=False`; no `{"valid": true}`.
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

## BOTTLENECK REMOVAL — ACTIONS THIS REFRESH
- **Real-tape detection defect** (sealed EVAL-21 `acquire_tape` loads the canonical synthetic path; would label synthetic as `"real"` if it met floors): **scoped to EVAL-22**. Sealed EVAL-21 is not modified; EVAL-22 implements strict real-only discovery + a regression test that the synthetic file is never accepted.
- **No real tape** (`data/raw/` = one synthetic orderflow tape, 239 returns / 3 windows; `data/processed/` derived from it): **converted from a silent blocker into an explicit, sealable NO-GO** with exact shortfall and a user data contract; EVAL-23B is the unblocked fallback.
- **Stale/competing handoff text**: the superseded EVAL-21 task message was removed from the active queue (kept only as a sealed record); root files are retired pointers. **Single durable handoff enforced.**
- **Full-suite / `research_state/` bloat**: constraints restated (targeted tests only, no enumeration, no new `phase*` wrappers).
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
- **SUPERSEDED (not sealed):** `INIT-2026-11-13T16:52:00Z-EVAL-22-REAL-TAPE-REPLICATION` — active, not started; replaced by the EVAL-22 gate above (same eval number, refreshed with measured data, the EVAL-21 defect, and fallback work).

---

## BOTTLENECKS — STATUS

| Bottleneck | Status |
|---|---|
| Real-tape detection defect in sealed EVAL-21 (`acquire_tape` loads canonical synthetic path; would label synthetic as real if adequate) | **SCOPED TO EVAL-22.** Do not modify sealed EVAL-21; EVAL-22 implements strict real-only discovery + regression test. |
| No real tape (`data/raw/` = 1 synthetic orderflow tape, 239 returns / 3 windows; `data/processed/` derived from it) | **CONVERTED TO EXPLICIT GATE.** EVAL-22 seals `NO-GO (no adequate real tape)` with exact shortfall; user data contract above; EVAL-23B fallback work. |
| Options leg degenerate (constant signal; single 30-quote synthetic chain; EVAL-16 chain inconsistency) | **REPORTED; EVAL-24 scope.** Flag, never hide. |
| Competing/stale handoff files | **CLEARED.** Only this file actionable; root handoffs are retired pointers (no task IDs). |
| `research_state/` bloat (5.0 GB / 106,688 tracked files; 188 `phase*` dirs) | **CONTAINED.** `.gitignore` blocks new `research_state/phase*/`; do not delete/rewrite history. |
| Phase orchestrator/wrapper clutter + 5,297-test corpus | **CONTAINED.** Forbidden to add more; targeted tests only. |
| Workflow edit-tool invalid-argument failures (`research_state/workflow_run_diagnostics.jsonl`) | **NOT in-repo actionable.** Do not attempt to fix from an agent session. |
| Safety/live-trading risk | **CLEARED.** `.env` absent, `LIVE_TRADING_ENABLED=false`, paper-only. |

## VERIFIED STATE / REUSE POINTS (ground truth, re-checked 2026-11-13T17:34:00Z)

- **Data:** `data/raw/orderflow_btcusdt_synthetic.json` = 1000 trades, span 2026-10-31T06:16:23Z–07:16:21Z (~1 h), venue `synthetic`, BTCUSDT → 240 bars / 239 returns / 3 windows (15 s bars; train 120 / test 40 / step 40). `data/raw/options_btc_synthetic.json` = 30 BTC quotes, 3 expiries (internally inconsistent — EVAL-16). No ETH/SOL raw options/orderflow. `data/processed/*.json` are derived from the synthetic tape, not real.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`, `CapacityAwareSizer`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders; `src.config_settings.RiskConfig` (default `max_position_pct=0.1` — always pass explicitly); `src.backtest.engine.WalkForwardBacktest` / `BacktestEngine`.
- **EVAL-20 battery (sealed, import not fork):** `src.analytics.measurement_validity_evaluation` — `build_pillar_signals`, `simulate_pillar`, `adequacy_report`, `periods_per_year`, `sharpe_from_returns`, `per_bar_returns`, `min_detectable_ic`, `power_for_ic`, `degeneracy_report`, `ic_report`, `cost_grid_report`, `pillar_metrics`, `compute_verdict`, `evaluate_measurement_validity`, helpers. **Caveat:** `evaluate_measurement_validity()` hardcodes `load_btc_orderflow()` and is not snapshot-parameterized — drive the lower-level primitives with the real snapshot instead of calling it.
- **EVAL-21 acquisition helpers (reuse, do not fork):** `src.analytics.sample_adequacy_acquisition` — `_orderflow_candidates`, `_tape_adequacy`, `_count_windows_for_bars`, `_snapshot_to_orderflow_dict`, `_fingerprint_tape`, `build_synthetic_orderflow_tape`. **Do not call `acquire_tape()` for real-data verdicts** (see defect above).
- **Environment:** Python 3.12.3; numpy/pandas/scipy/pydantic/pytest/PyYAML/requests installed. No mypy/ruff/flake8 → verify with `python3 -m py_compile` + **targeted** pytest only. Never run the full suite (5,297 tests / ~17 s collection, measured 2026-11-13T17:34:00Z). Never enumerate `research_state/`.
- **Verification baseline:** 45 passed (EVAL-20 26 + EVAL-21 19) at 2026-11-13T17:34:00Z.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Work queue: **EVAL-02..EVAL-21 SEALED. EVAL-22 ACTIVE (`INIT-2026-11-13T17:34:00Z-EVAL-22-REAL-TAPE-GATE`).**
- New EVALs must ship real module + numeric-invariant tests + CLI + strict artifact (no wrappers/stubs/no-ops). Handoff-only session = FAILED.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.