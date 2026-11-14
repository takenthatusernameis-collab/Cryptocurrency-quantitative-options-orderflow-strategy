# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**Initial task message (timestamped, for the next agentic work session): 2026-11-14T10:38:38Z (UTC).**
**Active task:** `INIT-2026-11-14T10:38:38Z-EVAL-30-SEAL-MEASURED-TIME-VARYING-SIGNAL` (mandatory heavy work — execute to a **sealed artifact + tests**, not analysis-only).

**Session verification (2026-11-14T10:38:38Z):** repo inspected from `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`. This file is the single durable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/INITIAL_TASK_20261114T063750Z.md` are RETIRED pointers with no task IDs (non-actionable). No competing handoff files. `.env` absent (paper-only, must stay absent). `AGENTS.md` absent. Working tree clean; latest commit `44bf972ad`.

**Bootstrap (verified this session):** `PYTHONPATH=. python3 -c "import src.data.options_timeseries, src.analytics.integrated_options_orderflow_evaluation, src.analytics.real_net_of_cost_evaluation, src.analytics.options_time_varying_signal"` succeeds; `python3 -m py_compile src/analytics/options_time_varying_signal.py` OK.

**Real data verified present and richer than the prior handoff claimed (this is the corrected ground truth):**
- Option snapshots: **3** — `data/raw/options_okx_BTC_20261114T093032Z.json`, `..._20261114T093120Z.json`, `..._20261114T103323Z.json` (last acquired 10:33Z, 817 quotes / 14 expiries). Discovered oldest-first via `discover_all_real_options_exports`.
- Orderflow tape: `data/raw/orderflow_okx_BTC-USD-SWAP.json` — **50,900 trades / 1,553 bars / span 23,281.8s (~6.5h)**, loaded via `load_real_orderflow`/`load_btc_orderflow` (was previously reported as only 1,000 trades).
- **The stale "2 snapshots / span ~48s / unmeasured adapter" description in the prior handoff is OBSOLETE — do not re-litigate it. The data is sufficient and the measurement already runs.**

**Repo priority (inferred from name):** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

## VERIFIED STATE (ground truth; re-verify before assuming)

- **Sealed gates:** EVAL-02..EVAL-22 **SEALED**. EVAL-23B/EVAL-24A adapters **SEALED**. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T103323Z` latest).
- **EVAL-23 SEALED (NO-GO, trustworthy)** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z` (8/11 checks). Combined IC mean -0.016776 (|t|=4.1008, p=0.0020, adverse); options-only OOS Sharpe 8.760/591 trades/cost 635.09; orderflow-only -2.338/502/588.15; `options_leg_degenerate=true`.
- **EVAL-24 SEALED (NO-GO, trustworthy)** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z` (3/8): `surface_reconstructed`, `surface_arbitrage_free`, `greeks_analytic_vs_finite_difference`, `put_call_parity`, `options_leg_tradable` FAIL; venue IV/greeks/OI coverage 0%.
- **EVAL-27 SEALED (NO-GO, trustworthy):** Path A `OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z` (parity "violations" later resolved by EVAL-28); Path B `AMENDED_FUSION_EVAL_27_20261114T065033Z` (5/7, `options_signal_exists` FAIL, `combined_net_of_cost_superior` FAIL; combined OOS Sharpe -100.33).
- **EVAL-28 SEALED (GO, additive):** `OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z` (re-confirmed `..._20261114T093132Z`). Per-expiry forward-calibrated put-call parity holds on 1017/1017 pairs (100.0%), min R²=0.999919. **Overturns EVAL-27 parity NO-GO (stale-constant-spot artifact).**
- **EVAL-29 SEALED (NO-GO, trustworthy):** `OPTIONS_LEG_TRADABILITY_29_20261114T093151Z` (seal `scripts/eval29_options_tradability_seal.py`). Options leg parity-consistent but `options_signal_exists` FAIL (mean IC 0.0) and `combined_net_of_cost_superior` FAIL; integrated 5/7. Options-only WF Sharpe -483.876/114 trades; orderflow-only 0.785/97; combined -100.333/51.
- **Measured root cause (EVAL-29):** `integrated_options_orderflow_evaluation.py::_causal_options_signal_series` broadcasts a single static options snapshot value to every bar → zero time-variation → mean IC 0.0. **EVAL-30 fixes this via the additive time-varying adapter.**
- **EVAL-30 ADAPTER BUILT + COMMITTED + NOW MEASURED THIS SESSION (2026-11-14T10:38:38Z):** `src/analytics/options_time_varying_signal.py` (32 KB; `py_compile` OK). Provides `snapshot_options_signal`, `load_snapshot_signals` (oldest-first; raises `RealDataUnavailable`, never synthetic), `align_options_signal_to_bars` (newest snapshot with `timestamp <= bar_end`, flat before first), `measure_time_varying_signal`, `build_eval30_report`, `write_eval30_artifact`.
  **Measured this session (throwaway probe `scripts/_explore_eval30.py`, output recorded here as ground truth):**
  - `n_bars=1553`, `n_snapshots=3`, span 2026-11-14T04:05:20Z → 10:33:22Z.
  - Per-snapshot raw signals: `-0.036191`, `-0.051843`, `-0.029513`; `forward_curve_slope` all negative; `atm_iv_term_slope` `-0.017407 / -0.020534 / +0.007635`; `iv_skew=0.0` (undefined — missing call/put ATM IV, warn-only); `put_call_ratio` `1.1208 / 1.1237 / 1.1444`.
  - `mean_signal=-0.008405`, `signal_stdev=0.019070`, `signal_stdev_over_abs_mean=2.2687`, `distinct_signal_values=3`, `step_changes=2`, `n_flat_bars=1300`, **`non_constant=True`, `ic_present=True`** (the EVAL-29 zero-variance failure is FIXED).
  - **IC by horizon: 1d=-0.003069 (t=-0.121), 5d=-0.006377 (t=-0.251), 20d=+0.000575 (t=+0.023); `ic_mean=-0.002957`, `ic_abs_mean=0.002957`.** → time-variation exists but is **not predictive** (|t|≪2 every horizon). This points to another **trustworthy NO-GO**.
  - **The signal is non-constant now, but still has no edge — the seal must say so honestly.**

## BOTTLENECKS — removed / active (do not re-litigate the removed ones)

- **Removed this session (verified 2026-11-14T10:38:38Z, do not re-litigate):**
  1. **"Only 2 snapshots / span ~48s" — obsolete.** 3 snapshots + 1,553-bar / 6.5h tape now present and loadable.
  2. **"Adapter unmeasured / measurement pending" — obsolete.** Measurement ran end-to-end; IC, stdev, step-changes all produced.
  3. **"Where to start / bootstrap" — cleared.** Imports + py_compile OK; entry points named below.
  4. **Stale-constant-spot parity confound (EVAL-28 GO); EVAL-23/24/27/28/29 sealed artifacts.**
- **Active remaining work (the EVAL-30 session's heavy lift):**
  1. **No sealed `OPTIONS_LEG_TRADABILITY_30_*` artifact exists yet** and **no targeted tests** for `options_time_varying_signal.py`. The measurement lives only in a throwaway probe. Sealing it + tests is the mandatory deliverable.
  2. **Signal is non-constant but not predictive** (IC |t|≪2). The sealed verdict must be a measured NO-GO unless the net-of-cost walk-forward (`_run_walkforward` + `evaluate_real_net_of_cost`) shows otherwise — do not assume GO.
  3. **Orderflow-only net-of-cost weak/negative** (EVAL-23 Sharpe -2.338; EVAL-27 0.79). Fusion has not beaten best pillar net-of-cost.
  4. **Provenance limits:** `authenticity_verified=false`; no signed venue attestation; inverse BTC-USD-SWAP tape vs spot option snapshots.
- **Prohibited (time sinks/regressions):** discovery runs, recreating/mutating sealed EVAL artifacts, enumerating `research_state/` (75k+ files), running the full test suite (~5k tests), modifying `.github/workflows/main.yml`, creating `phaseNN_*_post_attribution_seal_orchestrator` wrappers, deleting the throwaway probe before its numbers are preserved in a sealed artifact, ending with no new sealed artifact when work is feasible.

## INITIAL TASK MESSAGE — 2026-11-14T10:38:38Z (execute now)

**TASK ID:** `INIT-2026-11-14T10:38:38Z-EVAL-30-SEAL-MEASURED-TIME-VARYING-SIGNAL`
**STATUS:** **ACTIVE — mandatory heavy-work session.**

> **Hard success/failure floor:** session ends with **>=1 new sealed artifact** `research_state/OPTIONS_LEG_TRADABILITY_30_<UTC>.{json,md}` (or `AMENDED_FUSION_EVAL_30_<UTC>` if only partially measured) containing measured numbers, code paths, tests/verification output, and explicit GO/NO-GO → PASS (trustworthy NO-GO is success). No new sealed artifact / handoff-only / narrative-only / adapter-only → **FAILED**. Fabricated GO or synthetic relabeled as real → **FAILED**.

### 1) Bootstrap (verified this session; re-verify only if an import fails)
- `pip3 install -r requirements.txt` (only if a module import fails).
- Verify: `PYTHONPATH=. python3 -c "import src.data.options_timeseries, src.analytics.integrated_options_orderflow_evaluation, src.analytics.real_net_of_cost_evaluation, src.analytics.options_time_varying_signal"`.
- Real data already present (3 snapshots + 1,553-bar tape). Do **not** re-acquire unless a loader raises `RealDataUnavailable`.

### 2) Execute to a sealed artifact (measurement is done — SEAL it, do not redo it)
1. **Reproduce the measurement** (fresh run, not trusting the probe blindly): build bars from the real tape (`load_real_orderflow('BTC')` then `_build_bars`), load `load_snapshot_signals('BTC')`, run `measure_time_varying_signal(...)`. Expect the numbers above; **if they differ materially, record the new measured values and explain why** (e.g. new snapshot acquired).
2. **Run the net-of-cost walk-forward** on the time-varying signal (options-only / orderflow-only / combined / flat) via `_run_walkforward` (`src/analytics/integrated_options_orderflow_evaluation.py:649`), `evaluate_real_net_of_cost` (`src/analytics/real_net_of_cost_evaluation.py:386`), and `evaluate_integrated_options_orderflow` (:1054); record OOS Sharpe/return/drawdown/trades/cost/turnover + toxicity engagement. This is what turns "non-predictive IC" into a defensible GO/NO-GO.
3. **Seal** `research_state/OPTIONS_LEG_TRADABILITY_30_<UTC>.{json,md}` via `build_eval30_report(orderflow_bars=bars, net_of_cost=..., integrated=...)` + `write_eval30_artifact`, or an equivalent strict artifact with the same measured fields and explicit GO/NO-GO. Include the exact commands run and pytest pass counts.
4. **Add targeted tests** `tests/test_options_time_varying_signal.py`: causality/no-lookahead, oldest-first ordering, flat pre-first-snapshot, `RealDataUnavailable` invariant, parity of signal components vs hand-computed values on a fixture. Run `python3 -m pytest -q tests/test_options_time_varying_signal.py` and record pass counts.
5. **Update this handoff in place** with measured numbers, artifact paths, verification results, and the next TASK ID/timestamp. Remove `scripts/_explore_eval30.py` only after its numbers are preserved in the sealed artifact.

### 3) Required engineering discipline
- **Reuse (do not rewrite):** `src/analytics/options_time_varying_signal.py`, `src/analytics/integrated_options_orderflow_evaluation.py`, `src/analytics/real_net_of_cost_evaluation.py`, `src/campaign/integrated.py`, `src/data/{public_export_acquisition,loader,schemas,options_exports,options_timeseries}.py`, `src/features/*`, `src/backtest/engine.py`.
- **Invariant:** real loaders raise `RealDataUnavailable` and never fall back to synthetic; **do not modify `_causal_options_signal_series`** (sealed EVAL-18/23/27/29 semantics) — the additive adapter is the fix.
- **Verification:** `python3 -m py_compile` on touched modules + targeted `pytest`; record pass counts and exact commands in the artifact and handoff.
- **Artifacts:** strict JSON/MD in `research_state/` with `report_id`, timestamps, provenance, measured checks, explicit GO/NO-GO. Never emit `{"valid": true}`. Never fabricate provenance or relabel synthetic as real.

### 4) Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no venue/config/credential mutation, no order placement.
- Network only for **public read-only** market data acquisition with polite rate limiting; no authenticated calls.
- Do not re-open/mutate sealed artifacts (append new timestamped artifacts only). `scripts/run_backtest.py` is not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` out of scope.

### 5) Traps / invariants
- Options signal is broadcast-static in the sealed EVAL-29 path → mean IC 0.0; the fix is the additive adapter, not re-running EVAL-29.
- The adapter is now **non-constant** (distinct=3, stdev/mean=2.27) but **not predictive** (|t|≪2) — a "fixed variance, still no edge" outcome is a valid, trustworthy NO-GO. Do not fabricate a GO to justify the adapter.
- Do not repeat the constant-spot parity test (EVAL-27 parity NO-GO resolved by EVAL-28).
- Orderflow-only net-of-cost is a measured NO-GO on prior real tapes; do not cherry-pick a favorable window.
- Real data is gitignored — "blocked on data" is invalid; 3 snapshots + tape are present.
- Multi-snapshot consumers must use `discover_all_real_options_exports` (oldest-first).
- The EVAL-30 adapter exists, compiles, and is measured but has **no artifact and no tests** — tests alone or an adapter-only change without the sealed measurement is a failed session.

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
| **EVAL-30** | **Time-varying causal options signal: MEASURE + SEAL + TEST** | **ACTIVE — adapter built, measured (non-constant, IC |t|≪2); sealing + tests + net-of-cost walk-forward are the remaining heavy work** |
| EVAL-31 | **If EVAL-30 seals NO-GO: re-fuse time-varying options signal with orderflow toxicity/alpha at bar resolution and re-test net-of-cost superiority (only if a real mechanism, not curve-fitting, could change the verdict)** | QUEUED (next) |

## FOCUS CAMPAIGN (non-optional heavy work)
Every session must, in order, and may not skip any step: (0) verify bootstrap (imports; `pip3 install -r requirements.txt` only on failure) and real-data presence (3 snapshots + 1,553-bar tape confirmed 2026-11-14T10:38:38Z); (1) **reproduce the EVAL-30 measurement** and run the **net-of-cost walk-forward** (options-only / orderflow-only / combined / flat) — turn the non-predictive IC into a defensible GO/NO-GO; (2) **seal** `research_state/OPTIONS_LEG_TRADABILITY_30_<UTC>.{json,md}` with measured numbers and explicit GO/NO-GO; (3) **add targeted tests** `tests/test_options_time_varying_signal.py` and record pytest pass counts; (4) record pass counts/artifact paths/commands in this handoff; (5) update the queue and next TASK ID/timestamp (EVAL-31 queued). The adapter and measurement already exist — a session that ends without a sealed measurement artifact (only code, tests, or restated intent) is a **failed session**. If measurement is externally blocked, still ship a sealed measured NO-GO artifact documenting the blocker with evidence. Never idle, never ask follow-up questions.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands. Keep it a single file — do not spawn timestamped handoff copies (they become competing task sources and are the bottleneck this consolidation removes).
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Do not create competing handoff files. Final responses must not ask follow-up questions.