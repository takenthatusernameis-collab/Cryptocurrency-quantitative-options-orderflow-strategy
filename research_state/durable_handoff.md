# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**Initial task message (timestamped, 2026-11-14T10:43:21Z UTC, for the next agentic work session):** Execute `INIT-2026-11-14T10:43:21Z-EVAL-30-SEAL-MEASURED-TIME-VARYING-SIGNAL` now. Do **not** do discovery, do **not** re-litigate sealed EVALs, do **not** edit handoffs/tests-only without sealing. End the session with a new sealed artifact `research_state/OPTIONS_LEG_TRADABILITY_30_<UTC>.{json,md}` (or `AMENDED_FUSION_EVAL_30_<UTC>.{json,md}` if partially measured) containing reproduced measured numbers, net-of-cost walk-forward results (options-only/orderflow-only/combined/flat), targeted pytest pass counts, artifact paths, exact commands, and an explicit GO/NO-GO verdict. **Trustworthy NO-GO is success; fabricated GO or synthetic relabeled as real is failure. No new sealed measurement artifact = FAILED session.**

**Active task:** `INIT-2026-11-14T10:43:21Z-EVAL-30-SEAL-MEASURED-TIME-VARYING-SIGNAL` (mandatory heavy work).

**Session verification (2026-11-14T10:43:21Z):** repo `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy` inspected. This file is the single durable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/INITIAL_TASK_20261114T063750Z.md` are RETIRED pointers with no task IDs (non-actionable). No competing handoff files found. `.env` absent (paper-only, must stay absent). `AGENTS.md` absent. Working tree contains unrelated uncommitted state; latest commit `ec8d190ea`. `research_state/workflow_run_diagnostics.jsonl` tail shows recent scheduled loop runs completed/succeeded but included recurring environment/tool-noise signals (e.g. missing deps/pytest in some runs, edit-tool invalid-arg excerpts) — do not spend session time spelunking old logs; focus on EVAL-30 deliverables below.

**Bootstrap verified (2026-11-14T10:41:10Z):**
- `PYTHONPATH=. python3 -c "import src.data.options_timeseries, src.analytics.integrated_options_orderflow_evaluation, src.analytics.real_net_of_cost_evaluation, src.analytics.options_time_varying_signal"` => OK
- `python3 -m py_compile src/analytics/options_time_varying_signal.py` => OK
- Real data present: 3 option snapshots `data/raw/options_okx_BTC_20261114T093032Z.json`, `...093120Z.json`, `...103323Z.json` (817 quotes / 14 expiries; discovered oldest-first via `discover_all_real_options_exports`) and `data/raw/orderflow_okx_BTC-USD-SWAP.json` (50,900 trades / 1,553 bars / ~6.5h span, loaded via `load_real_orderflow`/`load_btc_orderflow`).
- **EVAL-30 not yet sealed:** no `research_state/OPTIONS_LEG_TRADABILITY_30_*` or `AMENDED_FUSION_EVAL_30_*`; no `tests/test_options_time_varying_signal.py`; throwaway probe `scripts/_explore_eval30.py` still present (remove only after its numbers are preserved in sealed artifact).

**Repo priority (inferred from name):** Cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not favorable-looking numbers from broken harnesses. A **trustworthy NO-GO** is a full success.

## VERIFIED STATE (ground truth; re-verify before assuming)

- **Sealed:** EVAL-02..EVAL-22; EVAL-23B/EVAL-24A adapters. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T103323Z`).
- **EVAL-23 SEALED NO-GO (trustworthy):** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z` — combined IC mean -0.016776 (|t|=4.1008, p=0.0020 adverse); options-only OOS Sharpe 8.760/591 trades/cost 635.09; orderflow-only -2.338/502/588.15; `options_leg_degenerate=true`.
- **EVAL-24 SEALED NO-GO (trustworthy):** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z` — `surface_reconstructed`, `surface_arbitrage_free`, `greeks_analytic_vs_finite_difference`, `put_call_parity`, `options_leg_tradable` FAIL; venue IV/greeks/OI coverage 0%.
- **EVAL-27 SEALED NO-GO (trustworthy):** `OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z`, `AMENDED_FUSION_EVAL_27_20261114T065033Z` — parity issue later resolved by EVAL-28; `options_signal_exists` FAIL, `combined_net_of_cost_superior` FAIL; combined OOS Sharpe -100.33.
- **EVAL-28 SEALED GO (additive):** `OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z` / `...093132Z` — per-expiry forward-calibrated put-call parity holds 1017/1017 pairs (100.0%), min R²=0.999919. Overturns EVAL-27 parity NO-GO (stale-constant-spot artifact).
- **EVAL-29 SEALED NO-GO (trustworthy):** `OPTIONS_LEG_TRADABILITY_29_20261114T093151Z` — options leg parity-consistent but `options_signal_exists` FAIL (mean IC 0.0) and `combined_net_of_cost_superior` FAIL; options-only WF Sharpe -483.876/114 trades; orderflow-only 0.785/97; combined -100.333/51.
- **Root cause (measured):** `integrated_options_orderflow_evaluation.py::_causal_options_signal_series` broadcasts a single static options snapshot value to every bar → zero time-variation → mean IC 0.0. Do **not** modify `_causal_options_signal_series` (sealed semantics); fix is additive adapter.
- **EVAL-30 adapter built + py_compile OK (unsealed):** `src/analytics/options_time_varying_signal.py` provides `snapshot_options_signal`, `load_snapshot_signals`, `align_options_signal_to_bars`, `measure_time_varying_signal`, `build_eval30_report`, `write_eval30_artifact`.
- **Measured probe ground truth (2026-11-14T10:38:38Z, `scripts/_explore_eval30.py`, must be reproduced and sealed):** `n_bars=1553`, `n_snapshots=3`, span 2026-11-14T04:05:20Z→10:33:22Z; per-snapshot signals `-0.036191, -0.051843, -0.029513`; `forward_curve_slope` all negative; `atm_iv_term_slope` `-0.017407 / -0.020534 / +0.007635`; `iv_skew=0.0` (undefined, warn-only); `put_call_ratio` `1.1208 / 1.1237 / 1.1444`; `mean_signal=-0.008405`, `signal_stdev=0.019070`, `signal_stdev_over_abs_mean=2.2687`, `distinct_signal_values=3`, `step_changes=2`, `n_flat_bars=1300`, `non_constant=True`, `ic_present=True`. **IC: 1d=-0.003069 (t=-0.121), 5d=-0.006377 (t=-0.251), 20d=+0.000575 (t=+0.023); `ic_mean=-0.002957`, `ic_abs_mean=0.002957` (|t|≪2 all horizons).** Time-variation exists but is not predictive — expected outcome is a **trustworthy NO-GO** unless net-of-cost walk-forward proves otherwise.

## BOTTLENECKS REMOVED (do not re-litigate)

1. "Only 2 snapshots / ~48s span / unmeasured adapter" — **obsolete** (3 snapshots + 1,553-bar/6.5h tape present; measurement ran).
2. Stale-constant-spot parity confound — **resolved** (EVAL-28 GO).
3. Bootstrap/import uncertainty — **cleared** (imports + py_compile OK).
4. Competing handoff sources — **cleared** (root/docs legacy pointers retired; this is the only actionable handoff).
5. "Where to start" ambiguity — **cleared** by this timestamped task and concrete commands/deliverables below.

## ACTIVE BOTTLENECKS (must remove by shipping artifacts)

1. No sealed EVAL-30 artifact (`OPTIONS_LEG_TRADABILITY_30_*` / `AMENDED_FUSION_EVAL_30_*`) — measurement currently only in throwaway probe.
2. No `tests/test_options_time_varying_signal.py` / no recorded targeted pytest pass counts.
3. No net-of-cost walk-forward verdict on the time-varying signal (options-only/orderflow-only/combined/flat) recorded in a sealed artifact.
4. Throwaway probe `scripts/_explore_eval30.py` still present (cleanup after sealing).
5. Provenance limits remain: `authenticity_verified=false`; no signed venue attestation; inverse BTC-USD-SWAP tape vs spot option snapshots (report honestly).

## EXECUTE NOW — `INIT-2026-11-14T10:41:10Z-EVAL-30-SEAL-MEASURED-TIME-VARYING-SIGNAL`

### 0) Bootstrap (only if needed)
- If any import fails: `pip3 install -r requirements.txt`
- Re-verify: `PYTHONPATH=. python3 -c "import src.data.options_timeseries, src.analytics.integrated_options_orderflow_evaluation, src.analytics.real_net_of_cost_evaluation, src.analytics.options_time_varying_signal"`
- Do **not** re-acquire data unless a loader raises `RealDataUnavailable`.

### 1) Reproduce measurement (fresh, recorded)
- Build bars from real tape: `load_real_orderflow('BTC')` then `_build_bars` (`src/analytics/integrated_options_orderflow_evaluation.py`).
- `signals = load_snapshot_signals('BTC')`; run `measure_time_varying_signal(bars, signals, horizons=(1,5,20))` or equivalent.
- Record measured `n_bars`, `n_snapshots`, span, per-snapshot signals/components, `distinct_signal_values`, `step_changes`, `signal_stdev/_over_abs_mean`, IC per horizon (t-stats), and any deviations from probe ground truth (explain if different).

### 2) Net-of-cost walk-forward (required for defensible verdict)
- Run time-varying options signal through `_run_walkforward` / `evaluate_real_net_of_cost` (`src/analytics/real_net_of_cost_evaluation.py:386`) and integrated eval (`evaluate_integrated_options_orderflow`) as applicable.
- Record options-only / orderflow-only / combined / flat: OOS Sharpe, return, drawdown, trade count, cost, turnover, toxicity engagement, and superiority checks.
- Do not assume GO from non-constant signal; current IC evidence points to NO-GO — seal what is measured.

### 3) Seal artifact + tests (mandatory)
- Write `research_state/OPTIONS_LEG_TRADABILITY_30_<UTC>.{json,md}` via `build_eval30_report(...)` + `write_eval30_artifact(...)` (or equivalent strict schema) with: `report_id`, timestamps, provenance/authenticity caveats, measured checks, probe-vs-rerun comparison, net-of-cost/walk-forward results, exact commands, pytest results, explicit `GO`/`NO-GO` verdict and rationale.
- Add `tests/test_options_time_varying_signal.py` covering at minimum: causality/no-lookahead alignment, oldest-first snapshot ordering, flat pre-first-snapshot behavior, `RealDataUnavailable` invariant, and component/signal parity on a deterministic fixture.
- Run and record: `python3 -m py_compile src/analytics/options_time_varying_signal.py tests/test_options_time_varying_signal.py` and `python3 -m pytest -q tests/test_options_time_varying_signal.py` (plus any other targeted tests touched).
- Remove `scripts/_explore_eval30.py` **after** its numbers are preserved in the sealed artifact.

### 4) Update handoff in place (same file only)
- Replace stale state with measured numbers, sealed artifact paths, verification/pytest counts, new TASK ID/timestamp, and next active task (EVAL-31 if EVAL-30 seals NO-GO with a real mechanism to test; otherwise state measured blocker/next step). No competing handoff files.

## HARD CONSTRAINTS / INVARIANTS

- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- Network only for public read-only market data acquisition with polite rate limiting if truly required (not expected — data present).
- Do not mutate sealed artifacts; append new timestamped artifacts only. `scripts/run_backtest.py` is not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` out of scope.
- Reuse existing modules: `src/analytics/options_time_varying_signal.py`, `src/analytics/integrated_options_orderflow_evaluation.py`, `src/analytics/real_net_of_cost_evaluation.py`, `src/campaign/integrated.py`, `src/data/{public_export_acquisition,loader,schemas,options_exports,options_timeseries}.py`, `src/features/*`, `src/backtest/engine.py`.
- Real loaders must raise `RealDataUnavailable` and never fall back to synthetic. Never relabel synthetic as real. Never emit `{"valid": true}`.
- Prohibited: discovery runs, re-litigating sealed EVALs, enumerating `research_state/` broadly, full test suite runs (~5k), modifying `.github/workflows/main.yml`, creating `phaseNN_*_post_attribution_seal_orchestrator` wrappers, handoff-only sessions.

## CAMPAIGN QUEUE

| Eval | Focus | Status |
|---|---|---|
| EVAL-02..EVAL-22 | Sealed prior gates | **SEALED** |
| EVAL-23B / EVAL-24A | Export adapters | **SEALED** |
| EVAL-25 | Real-data acquisition & falsification | **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`) |
| EVAL-26 | Public real-data acquisition | **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T103323Z`) |
| EVAL-23 | Real net-of-cost verdict | **SEALED NO-GO** |
| EVAL-24 | Options-leg validity | **SEALED NO-GO** |
| EVAL-27 | Options time-series tradability / amended-fusion | **SEALED NO-GO** |
| EVAL-28 | Per-expiry forward-calibrated parity | **SEALED GO** |
| EVAL-29 | Options-leg tradability / net-of-cost (calibrated forwards) | **SEALED NO-GO** (broadcast-static signal) |
| **EVAL-30** | **Seal measured time-varying options signal + targeted tests + net-of-cost walk-forward verdict** | **ACTIVE — adapter measured non-constant (IC |t|≪2); seal + tests + walk-forward required now** |
| EVAL-31 | **If EVAL-30 NO-GO: re-fuse time-varying options signal with orderflow toxicity/alpha at bar resolution and re-test net-of-cost superiority (real mechanism only, no curve-fitting)** | QUEUED (next) |

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands. No timestamped handoff copies.
- Record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.
