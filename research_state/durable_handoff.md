# SINGLE DURABLE HANDOFF — READ FIRST

**Repo (priority context):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**Mission (inferred priority):** Cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and a **statistically-defensible, net-of-cost evaluation**. The deliverable is the strategy and a *trustworthy* measurement of its performance, not orchestrator wrappers and not a favorable-looking number produced by a broken harness.

**Handoff refreshed:** 2026-11-13T16:52:00Z (UTC) — **EVAL-21 SEALED (GO)** this session with real module + 19 tests + CLI + strict artifact. EVAL-02..EVAL-21 are all SEALED. Next campaign is **EVAL-22 (REAL-TAPE REPLICATION)**.
**Authority:** This file is the only actionable handoff. `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action and do not create new handoff files. `research_state/NEXT9_APPROVAL_VALIDATION_*.json` are human-only NEXT9 artifacts (out of scope, never unblock NEXT9).

---

## INITIAL TASK MESSAGE — 2026-11-13T16:52:00Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-13T16:52:00Z-EVAL-22-REAL-TAPE-REPLICATION`
**STATUS:** **ACTIVE, not started.** EVAL-02..EVAL-21 are **SEALED — do not re-open**. EVAL-22 is the **only** next task: it converts EVAL-21's synthetic-provenance GO into a real-data verdict (or an honest NO-GO) and is the sole remaining gate before any capital discussion.

### What EVAL-21 proved (measured; do not re-litigate)
- **EVAL-21 SEALED (GO, 2026-11-13T16:51:08Z).** Module `src/analytics/sample_adequacy_acquisition.py` (deterministic, offline, paper-only) acquires an adequate tape and runs the sealed EVAL-20 battery unchanged.
- Evidence: `tests/test_sample_adequacy_acquisition.py` (**19 passed**); `tests/test_measurement_validity_evaluation.py` (**26 passed**, unchanged — no fork); CLI `python -m src.analytics.sample_adequacy_acquisition --out research_state/` emitted `research_state/SAMPLE_ADEQUACY_ACQUISITION_20261113T165108Z.{json,md}`.
- Measured: **9/9 checks PASS**, `data_provenance="synthetic"`, **n_bars 3400 / n_returns 3399 / n_windows 82 / n_trades 40800**, orderflow IC mean **0.375** (t **6.54**, h=1 IC 0.42), MDE@3399 **0.048** ≤ 0.05, sizing consistent (0 rejections), net = gross − cost, flat control exactly 0, strict JSON (`allow_nan=False`), never `{"valid": true}`.
- **Crucial caveat (do not hide):** EVAL-21's GO is on a **synthetic** tape with a *documented, deliberately-injected* orderflow→return edge (latent AR(1) flow, drift=1.6·persisted_flow·σ). It validates the **measurement battery and pipeline** at adequate n — it is **NOT** evidence of real market alpha and **MUST** be re-confirmed on a real tape before any capital decision.

### EVAL-22 mission (heavy-work floor — NO handoff-only work, NO no-ops)
> **A session that ends without new EVAL-22 artifacts (real-tape acquisition + module + tests + CLI output + verification evidence) is FAILED.** Do not re-open sealed EVALs (incl. EVAL-21). Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers/scripts/tests. Do not enumerate `research_state/`. Do not run the full test suite. Do not modify `.github/workflows/main.yml`. Do not fabricate a real exchange feed or relabel synthetic as real.

Deliverables (all required):
1. **Module:** `src/analytics/real_tape_ingestion.py` (deterministic, offline, paper-only) — **extend, do not fork**, the EVAL-21 acquisition contract.
   - **Auto-detect and load real orderflow tapes** from `data/raw/` (and any new `data/raw/orderflow_*.json` the user adds), parse via the existing `DataLoader`/`OrderflowSnapshot` path (no new network code).
   - **Validate** each real tape against adequacy floors (`n_returns >= 1000`, `n_windows >= 20`), causal no-lookahead, and microstructure sanity (positive prices/sizes, valid sides, monotone timestamps). Emit per-tape `data_provenance="real"` with path/span/trade/bar/return/window counts and a content fingerprint.
   - If a real tape meets floors, run the **sealed EVAL-20 battery** on it and emit the same validity battery + verdict; if none does, emit an explicit `NO-GO (no adequate real tape)` with the exact shortfall — **do not substitute synthetic silently**.
   - Reuse EVAL-20/EVAL-21 primitives (`build_pillar_signals`, `simulate_pillar`, `adequacy_report`, `ic_report`, serialization helpers). Never emit `{"valid": true}`. Strict JSON `allow_nan=False`.
2. **Tests:** `tests/test_real_tape_ingestion.py` — **10–16 numeric-invariant tests** covering: real-tape auto-detection, adequacy verdict on an adequate vs inadequate real fixture, `data_provenance="real"` correctness, causal no-lookahead on real data, rejection of malformed/empty tapes, strict serialization, and `never {"valid": true}`.
3. **CLI:** `python -m src.analytics.real_tape_ingestion --out research_state/`
4. **Strict artifacts:** `research_state/REAL_TAPE_INGESTION_<UTC>.{json,md}`.
5. **Verification (run and record):** `python3 -m py_compile src/analytics/real_tape_ingestion.py tests/test_real_tape_ingestion.py` and `python3 -m pytest -q tests/test_real_tape_ingestion.py`.
6. **Seal:** update this handoff in-place: mark EVAL-22 sealed with verdict/checks/evidence (real numbers, artifact paths), and set the next single active task (or state campaign complete only if defensibly proven on real data).

### EVAL-22 verdict checks (all must PASS for GO)
- `real_tape_detected`: at least one real orderflow tape is discovered and loaded; provenance `"real"` with path + span.
- `sample_adequate_declared`: `n_returns >= 1000` **and** `n_windows >= 20`; both counts emitted.
- `causal_no_lookahead`: asserted and tested (no future-trade leakage on real data).
- `microstructure_sane`: prices > 0, sizes > 0, sides in {buy,sell}, timestamps monotone non-decreasing.
- `sizing_consistent`: requested `max_position_pct == RiskConfig.max_position_pct`; zero swallowed `RiskLimitError`; rejections counted/reported.
- `sharpe_basis_valid`: per-bar Sharpe reproducible from emitted returns; annualisation = `periods_per_year(bar_duration_seconds)`.
- `net_of_cost_honest`: gross, net, turnover, cost bps for all series; cost non-negative; `net == gross − cost` within 1e-9.
- `ic_reported_with_power`: IC mean, t-stat, n, MDE at return count emitted; MDE at n_returns ≤ 0.05.
- `strict_serialization`: `allow_nan=False`; no `{"valid": true}`.
- **If no adequate real tape exists:** the session must still ship the module + tests + an explicit `NO-GO (no adequate real tape)` artifact with the measured shortfall — this is a legitimate, sealable outcome, not a failure, provided real work was done.

**Sealing rules:** A GO on real data is a genuine net-of-cost verdict. A `NO-GO` because no adequate real tape exists is honest and sealable, but must state exactly what data is missing (e.g. "need >= 1000 returns / >= 20 windows of real BTCUSDT trade prints; current tape = N trades / M bars"). Do not fabricate a real exchange feed. Do not present synthetic as real.

### Hard constraints
- Paper-only: `.env` **absent** and must stay absent; `.env.example` has `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`. No live enablement, no `.env` creation, no venue/config/credential mutation, no exchange network calls.
- Do not re-open sealed EVALs (incl. EVAL-21). Do not widen WF params to manufacture windows or fabricate longer series as "real".
- `scripts/run_backtest.py` is a vacuous smoke test — not evidence of edge.
- If incomplete, commit partial module+tests and record measured numbers/blockers/next line here; never leave a clean tree with EVAL-22 pending and never produce a handoff-only session.

---

## SEALED EVAL-21 (GO) — DO NOT RE-OPEN

**EVAL-21 SEALED (GO, 2026-11-13T16:51:08Z)** — `research_state/SAMPLE_ADEQUACY_ACQUISITION_20261113T165108Z.{json,md}`.
- Module: `src/analytics/sample_adequacy_acquisition.py`; Tests: `tests/test_sample_adequacy_acquisition.py` (**19 passed**); EVAL-20 suite unchanged (**26 passed**).
- 9/9 checks PASS; `data_provenance="synthetic"`; n_returns 3399 / n_windows 82; orderflow IC 0.375 (t 6.54); MDE@3399 0.048 ≤ 0.05; sizing consistent; net = gross − cost; flat == 0; strict JSON; never `{"valid": true}`.
- **Scope:** validates measurement battery + pipeline on an adequate **synthetic** sample with a documented injected edge. **Not** real-market evidence. Real replication = EVAL-22.

---

## (SUPERSEDED) INITIAL TASK MESSAGE — 2026-11-13T16:27:19Z

**TASK ID:** `INIT-2026-11-13T16:27:19Z-EVAL-21-SAMPLE-ADEQUACY` — **SEALED (GO), see above. Do not action.**

### Why EVAL-21 is required (measured; do not re-litigate)
- EVAL-20 fixed and test-locked the measurement harness (per-bar Sharpe + bar-duration annualisation, degenerate-leg detection, explicit sizing with counted rejections, position-weighted PnL so flat==0). Evidence: `src/analytics/measurement_validity_evaluation.py`, `tests/test_measurement_validity_evaluation.py` (**26 passed**), `research_state/MEASUREMENT_VALIDITY_EVAL_20261113T125227Z.{json,md}` (NO-GO 7/8; only `sample_adequate_declared` FAIL).
- Current tape: `data/raw/orderflow_btcusdt_synthetic.json` = 1000 trades / ~20 min → **240 bars / 239 returns / 3 walk-forward windows**. Adequacy floor: `n_returns >= 1000` **and** `n_windows >= 20`. At n=3, MDE|IC| ≈ **1.62** (impossible for plausible alpha) → no defensible net-of-cost GO/NO-GO is possible on this sample.
- Sealed findings to carry forward (not hide): options leg degenerate (constant signal, `n_unique==1` on current tape) — report as data limitation; combined/orderflow not demonstrably net-positive on current tape; flat control must remain 0.

### EVAL-21 mission (heavy-work floor — NO handoff-only work, NO no-ops)
> **A session that ends without new EVAL-21 artifacts (module + tests + CLI output + verification evidence) is FAILED.** Do not re-open sealed EVALs. Do not create `phaseNN_*_post_attribution_seal_orchestrator` wrappers/scripts/tests. Do not enumerate `research_state/`. Do not run the full test suite. Do not modify `.github/workflows/main.yml`.

Deliverables (all required):
1. **Module:** `src/analytics/sample_adequacy_acquisition.py` (deterministic, paper-only, fully offline).
   - **Reuse EVAL-20 primitives unchanged** from `src.analytics.measurement_validity_evaluation` (`build_pillar_signals`, `simulate_pillar`, `adequacy_report`, `periods_per_year`, `sharpe_from_returns`, serialization/validation helpers, etc.). **Do not fork them.**
   - **Prefer a real longer tape if present** under `data/raw/` (auto-detect). If none exists, **build a reproducible, offline, seeded, strictly-causal synthetic tape** that meets/exceeds adequacy floors (`n_returns >= 1000` and `n_windows >= 20`) with genuine orderflow microstructure (timestamps/sides/sizes) so the existing causal signal stack runs unchanged.
   - Emit the same validity battery as EVAL-20 (adequacy, degeneracy, sizing consistency, per-bar Sharpe, gross/net/turnover/cost, IC+power) **plus** `data_provenance` (`real` vs `synthetic`, seed, span, trade/bar/return/window counts). **Never present synthetic as real or mix silently.** Never make network/exchange calls.
   - Never emit `{"valid": true}`. Strict JSON serialization with `allow_nan=False` (`serialize_metrics_strict` / `assert_json_valid` or equivalent reused helpers).
2. **Tests:** `tests/test_sample_adequacy_acquisition.py` — **12–18 numeric-invariant tests** covering: adequacy floors met on acquired/constructed tape, byte-identical reproducibility (two builds), causal no-lookahead (signal at bar `t` uses only trades `<= bar_end[t]`), degeneracy handling/reporting, sizing consistency, per-bar Sharpe recomputable, `data_provenance` correctness, strict serialization, and `never {"valid": true}`.
3. **CLI:** `python -m src.analytics.sample_adequacy_acquisition --out research_state/`
4. **Strict artifacts:** `research_state/SAMPLE_ADEQUACY_ACQUISITION_<UTC>.{json,md}` (written by CLI/module).
5. **Verification (run and record outputs in artifact/notes):**
   - `python3 -m py_compile src/analytics/sample_adequacy_acquisition.py tests/test_sample_adequacy_acquisition.py`
   - `python3 -m pytest -q tests/test_sample_adequacy_acquisition.py`
6. **Seal:** update this handoff in-place: mark EVAL-21 sealed with verdict/checks/evidence (real numbers, artifact paths), and set the next single active task (or state campaign complete only if defensibly proven).

### EVAL-21 verdict checks (all must PASS for GO)
- `measurement_reproducible`: two runs byte-identical (determinism).
- `sample_adequate_declared`: `n_returns >= 1000` **and** `n_windows >= 20`; both counts emitted.
- `causal_no_lookahead`: asserted and tested (no future-trade leakage).
- `sizing_consistent`: requested `max_position_pct == RiskConfig.max_position_pct`; zero swallowed `RiskLimitError`; rejections counted/reported.
- `sharpe_basis_valid`: per-bar Sharpe reproducible from emitted returns; annualisation = `periods_per_year(bar_duration_seconds)`.
- `non_degenerate_pillars_reported`: degenerate legs flagged (`options_leg_degenerate` may be true if chain remains a single snapshot — report, do not hide).
- `net_of_cost_honest`: gross, net, turnover, cost bps for all series; cost non-negative; `net == gross - cost` within 1e-9.
- `ic_reported_with_power`: IC mean, t-stat, n, MDE emitted; MDE at acquired `n` must be small enough to detect plausible IC (e.g. `<= 0.05`).
- `strict_serialization`: `allow_nan=False`; no `{"valid": true}`.

**Sealing rules:** A `synthetic`-provenance GO is successful **only if** `data_provenance` is unambiguous and the artifact states plainly that the net-of-cost verdict is on **synthetic** data and must be re-confirmed on a real tape before any capital decision. **Do not relabel synthetic as real. Do not fabricate a real exchange feed.** If a real longer tape is added, module must auto-detect, prefer it, and mark `data_provenance: "real"`.

### Hard constraints
- Paper-only: `.env` **absent** and must stay absent; `.env.example` has `LIVE_TRADING_ENABLED=false`; `next9_unblocked=false`. No live enablement, no `.env` creation, no venue/config/credential mutation, no exchange network calls.
- Do not re-open sealed EVALs (incl. EVAL-20). Do not widen WF params to manufacture windows or fabricate longer series as "real".
- `scripts/run_backtest.py` is a vacuous smoke test — not evidence of edge.
- If incomplete, commit partial module+tests and record measured numbers/blockers/next line here; never leave a clean tree with EVAL-21 pending and never produce a handoff-only session.

---

## VERIFIED STATE / REUSE POINTS (ground truth)
- **Data:** `data/raw/options_btc_synthetic.json` (30 BTC quotes, 3 expiries, internally inconsistent — EVAL-16). `data/raw/orderflow_btcusdt_synthetic.json` (1000 trades, 20 liqs, 8 funding, BTCUSDT, ~20-min span → 240 bars/239 returns/3 windows). No ETH/SOL raw options/orderflow. `DEFAULT_SPOT["BTC"]=65000.0`, `DETERMINISTIC_NOW=2026-10-31T00:00:00Z`.
- **Reusable primitives:** `src.analytics.strategy_evaluation` (`compute_metrics`, `block_bootstrap_ci`, `permutation_test`, `assert_json_valid`, `serialize_metrics_strict`); `src.analytics.capacity_aware_tca` (`DEFAULT_SPREAD_BPS`, `DEFAULT_IMPACT_COEFF`, `DEFAULT_MAX_PARTICIPATION`, `CapacityAwareSizer`); `src.analytics.gamma_inventory_hedge.toxicity_score`; `src.campaign.integrated` loaders; `src.config_settings.RiskConfig` (default `max_position_pct=0.1` — always pass explicitly); `src.backtest.engine.WalkForwardBacktest` / `BacktestEngine`.
- **EVAL-20 measurement primitives to reuse for EVAL-21 (do not fork):** `src.analytics.measurement_validity_evaluation` — `build_pillar_signals`, `simulate_pillar`, `adequacy_report`, `periods_per_year`, `sharpe_from_returns`, `per_bar_returns`, `min_detectable_ic`, `power_for_ic`, `degeneracy_report`, `ic_report`, `cost_grid_report`, `pillar_metrics`, `compute_verdict`, `evaluate_measurement_validity`, helpers.
- **Environment:** Python 3.12.3; numpy/pandas/scipy/pydantic/pytest/PyYAML/requests installed. No mypy/ruff/flake8 → verify with `python3 -m py_compile` + **targeted** pytest only. Never run full suite (5,252 tests / ~26s collection). Never enumerate `research_state/`.

## SEALED EVALUATIONS (do not re-open)
- **EVAL-02..EVAL-15:** sealed per prior campaign (EVAL-12/13/14/15 GO; EVAL-06/10 NO-GO legitimate).
- **EVAL-16 SEALED (NO-GO, 2026-11-13T07:04:26Z):** `research_state/OPTIONS_SURFACE_GREEKS_EVAL_20261113T070426Z.*` — real 30-quote BTC chain data-quality/greeks failures are true state.
- **EVAL-17 SEALED (NO-GO, 2026-11-13T08:00:05Z):** `research_state/ORDERFLOW_ALPHA_TOXICITY_EVAL_20261113T080005Z.*` — IC -0.00820, t -1.3512, p 0.0889.
- **EVAL-18 SEALED (NO-GO, 2026-11-13T08:10:00Z):** `research_state/INTEGRATED_OPTIONS_ORDERFLOW_EVAL_20261113T081000Z.*` — harness invalidities later fixed by EVAL-20.
- **EVAL-19 SEALED (NO-GO, 2026-11-13T10:52:00Z):** `research_state/PRODUCTION_SIMULATION_EVAL_20261113T104657Z.*` — measured on invalid harness; seal stands historically.
- **EVAL-20 SEALED (NO-GO, 2026-11-13T12:53:00Z):** `research_state/MEASUREMENT_VALIDITY_EVAL_20261113T125227Z.*`, module+26 tests pass. NO-GO 7/8 (only `sample_adequate_declared` FAIL: 239 returns / 3 windows). Harness defects fixed and locked; sole remaining blocker is sample size → EVAL-21.

## BOTTLENECKS — STATUS
| Bottleneck | Status |
|---|---|
| EVAL-18/19 harness invalidity (3-point Sharpe@252, constant options pillar, swallowed `RiskLimitError`, flat-control echo) | **CLEARED (EVAL-20).** Fixed and locked by 26 tests in `measurement_validity_evaluation`. |
| Sample inadequacy (239 returns / 3 windows; MDE@3=1.62) | **ACTIVE blocker — EVAL-21 scope.** Requires longer real tape or clearly-labelled reproducible synthetic tape meeting adequacy floors. |
| Degenerate options pillar (constant on current tape) | **REPORTED.** Must be flagged, not hidden. |
| Competing/stale handoff files | **CLEARED.** Only this file actionable; root handoffs retired pointers. |
| `research_state/` bloat (5.0GB/106k tracked; 48k files in 188 `phase*` dirs) | **CONTAINED.** `.gitignore` blocks new `research_state/phase*/`; do not delete/rewrite history. |
| Phase orchestrator/wrapper clutter + large test corpus (5252 collected) | **CONTAINED.** Forbidden to add more; do not touch; run targeted tests only. |
| Workflow edit-tool invalid-argument failures (`research_state/workflow_run_diagnostics.jsonl`) | **NOT in-repo actionable.** Do not attempt to "fix" from agent session. |
| Safety/live-trading risk | **CLEARED.** `.env` absent, `LIVE_TRADING_ENABLED=false`, paper-only. |

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- Work queue: **EVAL-02..EVAL-20 SEALED. EVAL-21 ACTIVE (`INIT-2026-11-13T16:27:19Z-EVAL-21-SAMPLE-ADEQUACY`).**
- New EVALs must ship real module + numeric-invariant tests + CLI + strict artifact (no wrappers/stubs/no-ops). Handoff-only session = FAILED.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.
