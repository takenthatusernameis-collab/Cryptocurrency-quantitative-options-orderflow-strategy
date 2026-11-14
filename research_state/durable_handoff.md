# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**Initial task message (timestamped, 2026-11-14T11:42:00Z UTC, for the next agentic work session):** Execute `INIT-2026-11-14T11:42:00Z-EVAL-31-TIME-VARYING-OPTIONS-FUSION-NET-OF-COST` now. This is mandatory heavy measurement work, not discovery. Do **not** re-run discovery, do **not** re-litigate any sealed EVAL, do **not** edit sealed artifacts, do **not** spend the session on handoff-only or tests-only edits. The single deliverable is a new sealed artifact `research_state/AMENDED_FUSION_EVAL_31_<UTC>.{json,md}` containing: reproduced EVAL-30 numbers, the new fused-signal walk-forward results (combined / options-only / orderflow-only / flat: OOS Sharpe, return, drawdown, trade count, cost, turnover, toxicity engagement), targeted pytest pass counts, exact commands, and an explicit `GO`/`NO-GO` verdict with rationale. **A trustworthy NO-GO is a full success. Fabricated GO, or synthetic relabeled as real, is failure. No new sealed measurement artifact = FAILED session.**

**Active task:** `INIT-2026-11-14T11:42:00Z-EVAL-31-TIME-VARYING-OPTIONS-FUSION-NET-OF-COST` (mandatory heavy work).

**Session verification (2026-11-14T11:42:00Z):** repo `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy` inspected. This file is the single durable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/INITIAL_TASK_20261114T063750Z.md` are RETIRED pointers with **no task IDs** (non-actionable). No competing handoff files. `.env` absent (paper-only; must stay absent). Working tree clean at `dcc41673f`. EVAL-30 sealed prior session.

**Verified this session (2026-11-14T11:42:00Z):** EVAL-30 artifact, adapter, and tests all present; `PYTHONPATH=. python3 -c "import src.data.options_timeseries, src.analytics.integrated_options_orderflow_evaluation, src.analytics.real_net_of_cost_evaluation, src.analytics.options_time_varying_signal"` => `IMPORTS OK`; `python3 -m pytest -q tests/test_options_time_varying_signal.py` => **7 passed**; `scripts/_explore_eval30.py` deleted. All EVAL-31 building blocks import cleanly (`_build_bars`, `_causal_signal_series`, `_toxicities_per_bar`, `_signal_positions`, `_fuse_positions`, `_run_walkforward`, `CapacityAwareSizer`, `IntegratedConfig`, plus every `DEFAULT_*` constant).

**Repo priority (inferred from name):** Cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not favorable-looking numbers from broken harnesses. A **trustworthy NO-GO** is a full success.

## BOTTLENECKS ALREADY REMOVED (do not re-litigate, do not re-derive)

1. **EVAL-30 measurement unblocked, reproduced, and SEALED.** `scripts/_explore_eval30.py` (deleted, numbers preserved): `n_bars=1553`, `n_snapshots=3`, span `2026-11-14T04:05:20Z→10:33:22Z`; per-snapshot signals `-0.036191, -0.051843, -0.029513`; `mean_signal=-0.008405`, `signal_stdev=0.019070`, `distinct_signal_values=3`, `step_changes=2`, `n_flat_bars=1300`, `non_constant=True`, `ic_present=True`. **IC: 1d=-0.003069 (t=-0.121), 5d=-0.006377 (t=-0.251), 20d=+0.000575 (t=+0.023); `ic_mean=-0.002957`.**
2. **Bootstrap verified.** Imports OK above; `python3 -m py_compile src/analytics/options_time_varying_signal.py` => OK.
3. **Data present.** 3 option snapshots (`data/raw/options_okx_BTC_20261114T093032Z.json`, `...093120Z.json`, `...103323Z.json`) and `data/raw/orderflow_okx_BTC-USD-SWAP.json` (50,900 trades).
4. **EVAL-30 adapter sealed.** `src/analytics/options_time_varying_signal.py` provides `snapshot_options_signal`, `load_snapshot_signals`, `align_options_signal_to_bars` (causal step function, bar `i` uses newest snapshot `<= bar_end[i]`, pre-first-snapshot = 0.0), `measure_time_varying_signal`, `build_eval30_report`, `write_eval30_artifact`.
5. **Where-to-start ambiguity cleared** by the timestamped task + exact commands below.
6. **Competing handoff sources cleared** (all legacy pointers retired; this is the only actionable handoff).
7. **Root cause of prior NO-GO recorded (do NOT re-fix):** `integrated_options_orderflow_evaluation.py::_causal_options_signal_series` broadcasts a single static options value to every bar → zero time-variation → mean IC 0.0. Do **not** modify that sealed function. EVAL-31 must instead inject the *time-varying* `SnapshotSignal` series through the existing public adapter — no changes to sealed semantics.

## ACTIVE BOTTLENECK (the only one left; shipping the artifact removes it)

No EVAL-31 harness exists in `scripts/` or `tests/`. That cold-start is the last bottleneck. It is removed by following the exact plan below — everything it references is verified importable and runnable.

## VERIFIED STATE (ground truth; re-verify only if an import fails)

- **Sealed:** EVAL-02..EVAL-22; EVAL-23B/EVAL-24A adapters. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T103323Z`).
- **EVAL-23 SEALED NO-GO:** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z` — combined IC mean -0.016776 (|t|=4.1008, p=0.0020 adverse); options-only OOS Sharpe 8.760/591/cost 635.09; orderflow-only -2.338/502/588.15; `options_leg_degenerate=true`.
- **EVAL-24 SEALED NO-GO:** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z` — parity-consistent but `options_leg_tradable` FAIL; venue IV/greeks/OI coverage 0%.
- **EVAL-27 SEALED NO-GO:** `OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z`, `AMENDED_FUSION_EVAL_27_20261114T065033Z` — `options_signal_exists` FAIL, `combined_net_of_cost_superior` FAIL; combined OOS Sharpe -100.33.
- **EVAL-28 SEALED GO (additive):** `OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z` / `...093132Z` — per-expiry forward-calibrated put-call parity 1017/1017 pairs (100.0%), min R²=0.999919. Overturns EVAL-27 stale-spot parity artifact.
- **EVAL-29 SEALED NO-GO:** `OPTIONS_LEG_TRADABILITY_29_20261114T093151Z` — parity-consistent but static-broadcast signal → mean IC 0.0; options-only WF Sharpe -483.876/114; orderflow-only 0.785/97; combined -100.333/51.
- **EVAL-30 SEALED NO-GO (trustworthy):** `OPTIONS_LEG_TRADABILITY_30_20261114T113051395ZZ.{json,md}` — time-varying options signal measured (3 snapshots, non-constant, IC present) but `integrated_net_of_cost_go` FAIL. Integrated verdict NO-GO: `options_signal_exists` FAIL (mean IC 0.0 from static broadcast), `combined_net_of_cost_superior` FAIL (combined Sharpe -100.33 vs orderflow 0.79 vs flat 0.0). Net-of-cost real data 1553 bars: combined Sharpe 7.76/171/cost 350.62; options-only Sharpe -∞ (degenerate); orderflow-only measured; flat 0.00.

## EXECUTE NOW — `INIT-2026-11-14T11:42:00Z-EVAL-31-TIME-VARYING-OPTIONS-FUSION-NET-OF-COST`

### Step 0 — Bootstrap (only if an import below fails)
`pip3 install -r requirements.txt`, then re-run the import line in "Verified this session". Do **not** re-acquire data unless a loader raises `RealDataUnavailable`.

### Step 1 — Reproduce EVAL-30 measurement (fresh; must match sealed artifact)
```python
from src.analytics.integrated_options_orderflow_evaluation import load_btc_orderflow, _build_bars
from src.analytics.options_time_varying_signal import load_snapshot_signals, measure_time_varying_signal
snapshot = load_btc_orderflow("BTC")
bars = _build_bars(snapshot)
signals = load_snapshot_signals("BTC")
m = measure_time_varying_signal(signals, bars["bar_ends_dt"], bars["bar_closes"], horizons=(1,5,20))
```
Verify `n_bars=1553`, `n_snapshots=3`, span ≈3945s, per-snapshot signals match sealed artifact, `non_constant=True`, `ic_present=True`, `ic_mean≈-0.002957`. Record these in the artifact.

### Step 2 — Build the EVAL-31 fused signal (mechanism fixed BEFORE measurement; no curve-fitting)
The EVAL-30 time-varying options signal is a 3-step function over bars: `-0.036191 → -0.051843 → -0.029513` (all **negative**). Because all three values share one sign, a sign-agreement fusion against a zero-mean orderflow signal degenerates (flat most of the time) — this is the *measured* reason the prior static fusion failed, and it must be stated.

Use this **pre-declared** mechanism (choose exactly one; state `fusion_rule` in the artifact):
- **A (default) — options sign as causal regime filter, orderflow for direction/magnitude:** `position[i] = sign(orderflow_signal[i])` gated to flat when `toxicity[i] >= 0.7` **and** flat when `options_signal[i] >= 0` (i.e. trade orderflow direction only while the options step-function is risk-off/negative). Rationale: the options signal is a slow risk regime; the fast orderflow signal supplies timing. This is causal and uses no fitted parameters.
- **B — weighted z-score blend:** standardize both series over an expanding causal window (min 60 bars), `blend = w*z_options + (1-w)*z_orderflow` with fixed `w=0.5`, then sign → position with the same toxicity gate.

Build positions with the existing `_signal_positions` / a small explicit loop; apply the toxicity gate exactly as `evaluate_integrated_options_orderflow` does (`0 if tox >= 0.7 else position`).

### Step 3 — Net-of-cost walk-forward vs the 3 controls (reuse sealed machinery)
Reuse `CapacityAwareSizer(spread_bps, impact_coeff, max_participation, cost_budget_bps, seed=42)` and `IntegratedConfig(seed=42, train_window=DEFAULT_TRAIN_WINDOW, test_window=DEFAULT_TEST_WINDOW, step_size=DEFAULT_STEP_SIZE, purge=DEFAULT_PURGE, embargo=DEFAULT_EMBARGO)` and call `_run_walkforward("BTC", bar_closes, positions, bar_ends_dt, sizer, cfg, DEFAULT_N_POINTS, 42, max_position_pct=DEFAULT_MAX_POSITION_PCT)` for:
1. **combined** — the EVAL-31 fused signal
2. **options-only** — time-varying options signal → `_signal_positions` → toxicity-gated
3. **orderflow-only** — causal orderflow signal → `_signal_positions` → toxicity-gated (must reproduce sealed EVAL-30 orderflow-only ≈ Sharpe 0.79/97)
4. **flat** — all zeros (control, Sharpe 0.00)

`combined_net_of_cost_superior` PASS iff combined OOS Sharpe > max(options-only, orderflow-only, flat) **and** combined trades > 0. Record OOS Sharpe, total return, max drawdown, trade count, total cost (USD), turnover, and fraction of bars with toxicity engagement for each.

### Step 4 — Seal EVAL-31 artifact + targeted tests (mandatory)
Write `research_state/AMENDED_FUSION_EVAL_31_<UTC>.{json,md}` with: `report_id`, timestamps, provenance/authenticity caveats (`authenticity_verified=false`; no signed venue attestation; inverse BTC-USD-SWAP tape vs spot option snapshots), the exact fusion mechanism (`fusion_rule`, `rule_amended=true` + rationale, all constants, no fitted parameters), the Step-1 reproduced numbers, the 4-way walk-forward table, statistical defensibility (permutation vs best single pillar, DSR, PBO, BH-FDR) if applicable, exact commands, pytest results, and an explicit `GO`/`NO-GO` verdict with rationale.

Add `tests/test_amended_fusion_eval31.py` covering at minimum: (a) fused-signal construction matches the declared mechanism, (b) causality / no-lookahead (no bar uses a future snapshot), (c) toxicity gate forces flat at `tox >= 0.7`, (d) `_run_walkforward` runs on a deterministic fixture and returns the 4 required keys, (e) component parity on a deterministic fixture.

Record and run:
```
python3 -m py_compile src/analytics/options_time_varying_signal.py tests/test_amended_fusion_eval31.py
python3 -m pytest -q tests/test_amended_fusion_eval31.py
```
Plus any other targeted tests touched.

### Step 5 — Update this handoff in place (same file only)
Replace stale state with measured numbers, sealed artifact paths, pytest counts, a **new TASK ID/timestamp**, and the next active task: **EVAL-32** if EVAL-31 seals NO-GO (prove the options leg cannot carry alpha on this data by exhaustive per-expiry/per-component IC and cost-frontier analysis; seal a falsification artifact; no new data required), otherwise state the measured blocker / next step. No competing handoff files.

## NEXT-FOCUS CAMPAIGN (heavy work — future agents must not avoid it)

The strategic objective is to determine, with real data and net-of-cost accounting, whether a **tradable** cryptocurrency options+orderflow strategy exists. Every handoff session must advance the queue by at least one sealed measurement artifact (or explicitly seal a measured blocker with the exact command that failed). Handoff-only, tests-only-without-sealing, discovery-only, and "re-read the logs" sessions are non-progress. A NO-GO artifact that correctly reports why the strategy is not tradable is a full success; a GO without a verifying sealed artifact is a failure.

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
| EVAL-30 | Seal measured time-varying options signal + net-of-cost verdict | **Reproduce IC, walk-forward, seal artifact, ship tests** | **SEALED NO-GO** (`OPTIONS_LEG_TRADABILITY_30_20261114T113051395ZZ`) |
| **EVAL-31** | **Fuse time-varying options signal with causal orderflow toxicity/alpha at bar resolution; re-test net-of-cost superiority (real mechanism only, no curve-fitting); seal artifact + targeted tests** | **Must seal a measured artifact; re-labeling sealed EVALs forbidden** | **ACTIVE — execute now** |
| EVAL-32 | If EVAL-31 NO-GO: exhaustive per-expiry/per-component IC + cost-frontier analysis to prove the options leg cannot carry alpha on this data; seal a falsification artifact | **Seal artifact; no new data required** | QUEUED (contingent) |

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