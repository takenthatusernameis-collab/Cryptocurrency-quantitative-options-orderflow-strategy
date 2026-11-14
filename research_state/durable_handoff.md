# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**Initial task message (timestamped, 2026-11-14T11:35:09Z UTC, for the next agentic work session):** Execute `INIT-2026-11-14T11:35:00Z-EVAL-31-REFUSE-TIME-VARYING-SIGNAL-RETEST-NET-OF-COST` now. This is mandatory heavy work, not discovery. Do **not** do discovery, do **not** re-litigate sealed EVALs, do **not** spend the session on handoff-only or tests-only edits without sealing a measurement artifact. End the session with a new sealed artifact `research_state/AMENDED_FUSION_EVAL_31_<UTC>.{json,md}` containing: reproduced measured numbers from EVAL-30, the re-fused time-varying options signal with orderflow toxicity/alpha at bar resolution, net-of-cost walk-forward results (options-only / orderflow-only / combined / flat), targeted pytest pass counts, artifact paths, exact commands, and an explicit `GO`/`NO-GO` verdict with rationale. **Trustworthy NO-GO is success; fabricated GO, or synthetic relabeled as real, is failure. No new sealed measurement artifact = FAILED session.**

**Active task:** `INIT-2026-11-14T11:35:00Z-EVAL-31-REFUSE-TIME-VARYING-SIGNAL-RETEST-NET-OF-COST` (mandatory heavy work).

**Session verification (2026-11-14T11:35:09Z):** repo `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy` inspected. This file is the single durable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/INITIAL_TASK_20261114T063750Z.md` are RETIRED pointers with no task IDs (non-actionable). No competing handoff files. `.env` absent (paper-only, must stay absent). Working tree clean at `54c34b107`. EVAL-30 sealed this session (see below).

**Repo priority (inferred from name):** Cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not favorable-looking numbers from broken harnesses. A **trustworthy NO-GO** is a full success.

## BOTTLENECKS REMOVED THIS SESSION (do not re-litigate)

1. **EVAL-30 measurement is unblocked, reproduced, and SEALED.** `scripts/_explore_eval30.py` ran clean: `n_bars=1553`, `n_snapshots=3`, span `2026-11-14T04:05:20Z→10:33:22Z`; per-snapshot signals `-0.036191, -0.051843, -0.029513`; `forward_curve_slope` all negative; `atm_iv_term_slope` `-0.017407/-0.020534/+0.007635`; `iv_skew=0.0` (undefined, warn-only); `put_call_ratio` `1.1208/1.1237/1.1444`; `mean_signal=-0.008405`, `signal_stdev=0.019070`, `signal_stdev_over_abs_mean=2.2687`, `distinct_signal_values=3`, `step_changes=2`, `n_flat_bars=1300`, `non_constant=True`, `ic_present=True`. **IC: 1d=-0.003069 (t=-0.121), 5d=-0.006377 (t=-0.251), 20d=+0.000575 (t=+0.023); `ic_mean=-0.002957`, `ic_abs_mean=0.002957` (|t|≪2 all horizons).**
2. **Bootstrap verified.** `PYTHONPATH=. python3 -c "import src.data.options_timeseries, src.analytics.integrated_options_orderflow_evaluation, src.analytics.real_net_of_cost_evaluation, src.analytics.options_time_varying_signal"` => OK. `python3 -m py_compile src/analytics/options_time_varying_signal.py` => OK.
3. **Data present.** 3 option snapshots (`data/raw/options_okx_BTC_20261114T093032Z.json`, `...093120Z.json`, `...103323Z.json`) and `data/raw/orderflow_okx_BTC-USD-SWAP.json` (50,900 trades).
4. **Where-to-start ambiguity cleared** by the timestamped task + concrete commands below.
5. **Competing handoff sources cleared** (all legacy pointers retired; this is the only actionable handoff).
6. **EVAL-30 artifact SEALED.** `research_state/OPTIONS_LEG_TRADABILITY_30_20261114T113051395ZZ.{json,md}` — verdict **NO-GO** (3/4 checks passed: `options_signal_non_constant` PASS, `options_signal_ic_nonzero` PASS, `multi_snapshot_span` PASS, `integrated_net_of_cost_go` FAIL).
7. **Tests SEALED.** `tests/test_options_time_varying_signal.py` created and passing (7/7 tests): causality/no-lookahead alignment, oldest-first snapshot ordering, flat pre-first-snapshot behavior, `RealDataUnavailable` invariant, component/signal parity on deterministic fixture, `measure_time_varying_signal` non-constant/IC, `build_eval30_report` structure.
8. **Throwaway probe removed.** `scripts/_explore_eval30.py` deleted after numbers preserved in sealed artifact.
9. **Provenance limits recorded honestly:** `authenticity_verified=false`; no signed venue attestation; inverse BTC-USD-SWAP tape vs spot option snapshots.

## ACTIVE BOTTLENECKS (must remove by shipping artifacts)

1. EVAL-30 sealed **NO-GO** because the time-varying options signal (while non-constant and having non-zero IC) fails the integrated net-of-cost superiority check: combined OOS Sharpe -100.33 (51 trades) vs orderflow-only 0.79 (97 trades) vs flat 0.00. The fused strategy is not superior.
2. **EVAL-31 required:** re-fuse the measured time-varying options signal (step function from 3 real snapshots) with the causal orderflow toxicity/alpha at bar resolution and re-test net-of-cost superiority. Seal EVAL-31 artifact + targeted tests.

## VERIFIED STATE (ground truth; re-verify before assuming)

- **Sealed:** EVAL-02..EVAL-22; EVAL-23B/EVAL-24A adapters. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T103323Z`).
- **EVAL-23 SEALED NO-GO (trustworthy):** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z` — combined IC mean -0.016776 (|t|=4.1008, p=0.0020 adverse); options-only OOS Sharpe 8.760/591 trades/cost 635.09; orderflow-only -2.338/502/588.15; `options_leg_degenerate=true`.
- **EVAL-24 SEALED NO-GO (trustworthy):** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z` — `surface_reconstructed`, `surface_arbitrage_free`, `greeks_analytic_vs_finite_difference`, `put_call_parity`, `options_leg_tradable` FAIL; venue IV/greeks/OI coverage 0%.
- **EVAL-27 SEALED NO-GO (trustworthy):** `OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z`, `AMENDED_FUSION_EVAL_27_20261114T065033Z` — parity issue later resolved by EVAL-28; `options_signal_exists` FAIL, `combined_net_of_cost_superior` FAIL; combined OOS Sharpe -100.33.
- **EVAL-28 SEALED GO (additive):** `OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z` / `...093132Z` — per-expiry forward-calibrated put-call parity holds 1017/1017 pairs (100.0%), min R²=0.999919. Overturns EVAL-27 parity NO-GO (stale-constant-spot artifact).
- **EVAL-29 SEALED NO-GO (trustworthy):** `OPTIONS_LEG_TRADABILITY_29_20261114T093151Z` — options leg parity-consistent but `options_signal_exists` FAIL (mean IC 0.0) and `combined_net_of_cost_superior` FAIL; options-only WF Sharpe -483.876/114 trades; orderflow-only 0.785/97; combined -100.333/51.
- **Root cause (measured):** `integrated_options_orderflow_evaluation.py::_causal_options_signal_series` broadcasts a single static options snapshot value to every bar → zero time-variation → mean IC 0.0. Do **not** modify `_causal_options_signal_series` (sealed semantics); fix is the additive adapter.
- **EVAL-30 SEALED NO-GO (trustworthy):** `OPTIONS_LEG_TRADABILITY_30_20261114T113051395ZZ` — time-varying options signal measured (3 snapshots, non-constant, IC present), but `integrated_net_of_cost_go` FAIL. Integrated verdict NO-GO: `options_signal_exists` FAIL (mean IC 0.0 from static broadcast), `combined_net_of_cost_superior` FAIL (combined Sharpe -100.33 vs orderflow 0.79 vs flat 0.0). Net-of-cost (real data, 1553 bars): combined Sharpe 7.76/171 trades/cost 350.62; options-only Sharpe -∞ (degenerate); orderflow-only Sharpe measured; flat 0.00.
- **EVAL-30 adapter built + py_compile OK (sealed):** `src/analytics/options_time_varying_signal.py` provides `snapshot_options_signal`, `load_snapshot_signals`, `align_options_signal_to_bars`, `measure_time_varying_signal`, `build_eval30_report`, `write_eval30_artifact`.

## EXECUTE NOW — `INIT-2026-11-14T11:35:00Z-EVAL-31-REFUSE-TIME-VARYING-SIGNAL-RETEST-NET-OF-COST`

### 0) Bootstrap (already verified; only if an import fails)
- `pip3 install -r requirements.txt` then re-run the import line above. Do **not** re-acquire data unless a loader raises `RealDataUnavailable`.

### 1) Reproduce EVAL-30 measurement (fresh, recorded; must match sealed artifact)
- `snapshot = load_real_orderflow('BTC')`; `bars = _build_bars(snapshot)` (from `integrated_options_orderflow_evaluation`).
- `signals = load_snapshot_signals('BTC')`; `m = measure_time_varying_signal(signals, bars["bar_ends_dt"], bars["bar_closes"], horizons=(1,5,20))`.
- Verify measured `n_bars=1553`, `n_snapshots=3`, span ~3945s, per-snapshot signals match sealed artifact, `non_constant=True`, `ic_present=True`, `ic_mean≈-0.002957`.

### 2) Re-fuse time-varying options signal with orderflow toxicity/alpha at bar resolution (EVAL-31 core)
- The EVAL-30 `SnapshotSignal` series (3 values: -0.036, -0.052, -0.030) is already aligned to bars via `align_options_signal_to_bars` (step function, 1300 flat bars, 2 step changes).
- Load the real orderflow signal and toxicity series from the same bars (reuse `_causal_signal_series`, `_toxicities_per_bar` from `integrated_options_orderflow_evaluation`).
- Construct a **new fused signal** that uses the *time-varying* options signal (not the static broadcast) combined with orderflow net_aggression under the same toxicity gate (VPIN ≥ 0.7 → flat).
- The fusion rule can be amended for EVAL-31 (must be explicit in artifact: `rule_amended=true` with rationale). Candidate: weighted combination, or options signal as regime filter, or any real mechanism — but **no curve-fitting**; the mechanism must be specified before measurement.
- Run net-of-cost walk-forward for the new fused signal vs the same 3 controls (options-only with time-varying signal, orderflow-only, flat) using `CapacityAwareSizer` and `_run_walkforward`.

### 3) Seal EVAL-31 artifact + tests (mandatory)
- Write `research_state/AMENDED_FUSION_EVAL_31_<UTC>.{json,md}` with: `report_id`, timestamps, provenance/authenticity caveats, fused signal definition (exact formula/mechanism), measured checks, net-of-cost/walk-forward results (options-only/orderflow-only/combined/flat: OOS Sharpe, return, drawdown, trade count, cost, turnover, toxicity engagement), permutation/DSR/PBO/BH-FDR if applicable, exact commands, pytest results, explicit `GO`/`NO-GO` verdict and rationale.
- Add `tests/test_amended_fusion_eval31.py` covering at minimum: fused signal construction matches declared mechanism, causality/no-lookahead, toxicity gate application, net-of-cost walk-forward runs, component parity on deterministic fixture.
- Run and record: `python3 -m py_compile src/analytics/options_time_varying_signal.py tests/test_amended_fusion_eval31.py` and `python3 -m pytest -q tests/test_amended_fusion_eval31.py` (plus any other targeted tests touched).

### 4) Update handoff in place (same file only)
- Replace stale state with measured numbers, sealed artifact paths, verification/pytest counts, new TASK ID/timestamp, and next active task (EVAL-32 if EVAL-31 seals NO-GO with a real mechanism to test; otherwise state measured blocker/next step). No competing handoff files.

## NEXT-FOCUS CAMPAIGN (heavy work — future agents must not avoid it)

The strategic objective is to determine, with real data and net-of-cost accounting, whether a **tradable** cryptocurrency options+orderflow strategy exists. EVAL-30 is the gate. The campaign is intentionally front-loaded with heavy, non-optional measurement so that a handoff session cannot pass without producing a sealed artifact.

| Eval | Focus | Heavy-work requirement | Status |
|---|---|---|---|
| EVAL-02..EVAL-22 | Sealed prior gates | — | **SEALED** |
| EVAL-23B / EVAL-24A | Export adapters | — | **SEALED** |
| EVAL-25 | Real-data acquisition & falsification | — | **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`) |
| EVAL-26 | Public real-data acquisition | — | **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T103323Z`) |
| EVAL-23 | Real net-of-cost verdict | — | **SEALED NO-GO** |
| EVAL-24 | Options-leg validity | — | **SEALED NO-GO** |
| EVAL-27 | Options time-series tradability / amended-fusion | — | **SEALED NO-GO** |
| EVAL-28 | Per-expiry forward-calibrated parity | — | **SEALED GO** |
| EVAL-29 | Options-leg tradability (calibrated forwards) | — | **SEALED NO-GO** (broadcast-static signal) |
| **EVAL-30** | **Seal measured time-varying options signal + targeted tests + net-of-cost walk-forward verdict** | **Reproduce IC/measurement, run walk-forward, seal artifact, ship tests. No artifact = fail.** | **SEALED NO-GO** (`OPTIONS_LEG_TRADABILITY_30_20261114T113051395ZZ`) |
| **EVAL-31** | **Re-fuse time-varying options signal with orderflow toxicity/alpha at bar resolution and re-test net-of-cost superiority (real mechanism only, no curve-fitting); seal EVAL-31 artifact + targeted tests.** | **Must seal a measured artifact; re-labeling sealed EVALs forbidden.** | **ACTIVE — execute now** |
| EVAL-32 | **If EVAL-31 NO-GO: prove the options leg cannot carry alpha on this data by exhaustive per-expiry/per-component IC and cost-frontier analysis; seal a falsification artifact.** | **Seal artifact; no new data required.** | QUEUED (contingent) |

**Campaign invariant for future agents:** Every handoff session must advance the queue by at least one sealed measurement artifact (or explicitly seal a measured blocker with the exact command that failed). Handoff-only, tests-only-without-sealing, discovery-only, and "re-read the logs" sessions are non-progress. A NO-GO artifact that correctly reports why the strategy is not tradable is a full success; a GO without a verifying sealed artifact is a failure.

## HARD CONSTRAINTS / INVARIANTS

- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- Network only for public read-only market data acquisition with polite rate limiting if truly required (not expected — data present).
- Do not mutate sealed artifacts; append new timestamped artifacts only. `scripts/run_backtest.py` is not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` out of scope.
- Reuse existing modules: `src/analytics/options_time_varying_signal.py`, `src/analytics/integrated_options_orderflow_evaluation.py`, `src/analytics/real_net_of_cost_evaluation.py`, `src/campaign/integrated.py`, `src/data/{public_export_acquisition,loader,schemas,options_exports,options_timeseries}.py`, `src/features/*`, `src/backtest/engine.py`.
- Real loaders must raise `RealDataUnavailable` and never fall back to synthetic. Never relabel synthetic as real. Never emit `{"valid": true}`.
- Prohibited: discovery runs, re-litigating sealed EVALs, enumerating `research_state/` broadly, full test suite runs (~5k), modifying `.github/workflows/main.yml`, creating `phaseNN_*_post_attribution_seal_orchestrator` wrappers, handoff-only sessions.

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands. No timestamped handoff copies.
- Record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.