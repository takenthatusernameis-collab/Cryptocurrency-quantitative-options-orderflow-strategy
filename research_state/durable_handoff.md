# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**Initial task message (timestamped, for the next agentic work session): 2026-11-14T10:30:05Z (UTC).**
**Active task:** `INIT-2026-11-14T10:30:05Z-EVAL-30-SEAL-TIME-VARYING-SIGNAL` (mandatory heavy work — execute to a sealed artifact, not analysis-only).

**Session verification (2026-11-14T10:30:05Z):** repo inspected from `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`. This file remains the single durable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` and `research_state/INITIAL_TASK_20261114T063750Z.md` are retired pointers with no task IDs (non-actionable). No other competing handoff files found. `.env` absent (paper-only, must remain absent). `AGENTS.md` absent. Working tree clean; latest commit `a98bc1909`. **Bootstrap verified this session:** `pip3` deps present — `PYTHONPATH=. python3 -c "import src.data.options_timeseries, src.analytics.integrated_options_orderflow_evaluation, src.analytics.real_net_of_cost_evaluation, src.analytics.options_time_varying_signal"` succeeds. **Real data verified present in this checkout:** `data/raw/options_okx_BTC_20261114T093032Z.json` and `data/raw/options_okx_BTC_20261114T093120Z.json` (2 real snapshots, span ~48s; both discovered by `discover_all_real_options_exports` oldest-first) plus `data/raw/orderflow_okx_BTC-USD-SWAP.json` (1000 trades, loads via `load_btc_orderflow`).

**Repo priority (inferred from name):** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

## VERIFIED STATE (ground truth from prior measured sessions; re-verify before assuming)

- **Sealed gates:** EVAL-02..EVAL-22 **SEALED**. EVAL-23B/EVAL-24A adapters **SEALED**. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z.{json,md}`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T064702Z.{json,md}` latest).
- **EVAL-23 SEALED (NO-GO, trustworthy)** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z.{json,md}` (8/11 checks). Combined IC mean -0.016776 (|t|=4.1008, p=0.0020, adverse); options-only OOS Sharpe 8.760 / 591 trades / cost 635.09; orderflow-only Sharpe -2.338 / 502 trades / cost 588.15; `options_leg_degenerate=true`, `options_signal_tradable` FAIL.
- **EVAL-24 SEALED (NO-GO, trustworthy)** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z.{json,md}` (3/8 checks): `surface_reconstructed`, `surface_arbitrage_free`, `greeks_analytic_vs_finite_difference`, `put_call_parity`, `options_leg_tradable` FAIL; venue IV/greeks/OI coverage 0%.
- **EVAL-27 SEALED (NO-GO, trustworthy):**
  - Path A `OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z.{json,md}` — 3 real snapshots, span 10,659.8s, `options_leg_tradable=false`, reason "1017 put-call parity violation(s)" (constant-spot parity; **confound resolved by EVAL-28**).
  - Path B `AMENDED_FUSION_EVAL_27_20261114T065033Z.{json,md}` — 5/7 checks, `options_signal_exists` FAIL, `combined_net_of_cost_superior` FAIL; combined OOS Sharpe -100.33, options-only -483.88, orderflow-only 0.79; IC combined -0.07696 (|t|=5.06); defensible_edge=false.
- **EVAL-28 SEALED (GO, additive):** `OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z.{json,md}` (re-confirmed `..._20261114T093132Z`). Per-expiry forward-calibrated put-call parity holds on **1017/1017 pairs (100.0%)** within bid-ask spread across 3 snapshots / 12 expiries each; **min R² = 0.999919**. Re-confirmed on fresh snapshots: 777/777 pairs (100.0%), min R²=0.999903. **Overturns EVAL-27 parity NO-GO (stale-constant-spot artifact, not arbitrage).**
- **EVAL-29 SEALED (NO-GO, trustworthy):** `OPTIONS_LEG_TRADABILITY_29_20261114T093151Z.{json,md}` (seal script `scripts/eval29_options_tradability_seal.py`). Options leg parity-consistent (GO) but `options_signal_exists` FAIL (mean IC 0.0) and `combined_net_of_cost_superior` FAIL; integrated eval 5/7 checks. Options-only WF Sharpe -483.876 / 114 trades / cost $55.83; orderflow-only Sharpe 0.785 / 97 trades / cost $58.26; combined Sharpe -100.333 / 51 trades / cost $53.35.
- **Measured root cause (EVAL-29):** `src/analytics/integrated_options_orderflow_evaluation.py::_causal_options_signal_series` broadcasts a single static options snapshot value to every bar → zero time-variation → mean IC 0.0. **EVAL-30 must fix this with a time-varying causal options signal.**
- **EVAL-30 adapter BUILT (committed, unmeasured, unsealed):** `src/analytics/options_time_varying_signal.py` — additive, opt-in module providing `snapshot_options_signal` (per-snapshot causal signal: fitted per-expiry forward-curve slope, ATM IV term slope, IV skew, put-call ratio; normalized weighted composite), `load_snapshot_signals` (oldest-first via `discover_all_real_options_exports`, raises `RealDataUnavailable`, never synthetic), `align_options_signal_to_bars` (newest snapshot with `timestamp <= bar_end`, flat before first snapshot), `measure_time_varying_signal` (stdev/mean, IC per horizon, t-stats), `build_eval30_report`, `write_eval30_artifact`. Verified: imports OK, `py_compile` OK. Sealed EVAL-18/23/24/27/29 semantics untouched. **Remaining: measurement wiring + net-of-cost run + targeted tests + sealed artifact (no `OPTIONS_LEG_TRADABILITY_30_*` artifact exists yet; no seal script in `scripts/`).**
- **Real inputs are gitignored and absent in a fresh checkout:** `data/raw/orderflow_okx_BTC-USD-SWAP.json` and `data/raw/options_okx_BTC_<UTC>.json` are `.gitignore`d (fresh clone has only synthetic fixtures `orderflow_btcusdt_synthetic.json`, `options_btc_synthetic.json`). **Synthetic fixtures must never be relabeled as real or used via real loaders.** Re-acquire every session as needed (this checkout already has 2 real snapshots + real tape).
- **Environment bootstrap is a required first step:** in a fresh checkout deps may be missing; every EVAL entry point will fail to import until `pip3 install -r requirements.txt` succeeds. `pytest 9.2.0` was present at verification time but do not assume — verify imports before work (verified OK this session).
- **Provenance limits:** `authenticity_verified=false`; inverse BTC-USD-SWAP tape + spot option snapshots; no signed venue attestation.

## BOTTLENECKS — remove before/while doing heavy work

- **Cleared this session (verified 2026-11-14T10:30:05Z, do not re-litigate):**
  1. **Deps/bootstrap:** imports of all key modules verified OK in this checkout (command in header). Still run `pip3 install -r requirements.txt` first in any fresh checkout.
  2. **Real data:** 2 real option snapshots (093032Z, 093120Z; span ~48s) + real orderflow tape (1000 trades) present and loadable. If a longer span is needed, re-acquire with `PYTHONPATH=. python3 -m src.data.public_export_acquisition --underlying BTC --orderflow-instrument BTC-USD-SWAP --min-bars 1550 --bar-duration-seconds 15` (public read-only, network OK).
- **Active research bottleneck (the EVAL-30 work):**
  1. **Broadcast-static options signal (measured):** `_causal_options_signal_series` → IC 0.0. **Adapter built** (`src/analytics/options_time_varying_signal.py`) but **not yet measured end-to-end**; wiring into the net-of-cost walk-forward and IC measurement is the remaining heavy work.
  2. **Snapshot count:** only 2 real snapshots (~48s apart). The adapter's `multi_snapshot_span` check accepts >=2 snapshots with span>0, so Path A can proceed now; a 3rd snapshot with larger wall-clock separation strengthens the time-variation claim (acquire politely if feasible).
  3. **Orderflow-only net-of-cost weak/negative on current real tapes** (EVAL-23 Sharpe -2.338; EVAL-27 0.79 with negative return).
  4. **Fusion does not beat best pillar net-of-cost** (EVAL-29 combined Sharpe -100.33 vs orderflow-only 0.79).
  5. **Provenance limits:** no signed venue attestation; instrument/basis mismatch remains.
- **Removed (do not re-litigate):** stale-constant-spot parity confound (EVAL-28 GO); EVAL-23/24/27/28/29 sealed artifacts; "where to start" (entry points named below); data acquisition plumbing exists; EVAL-30 signal adapter exists and compiles.
- **Prohibited (time sinks/regressions):** discovery runs, recreating/mutating sealed EVAL artifacts, enumerating `research_state/` (thousands of files), running the full test suite (~5k tests), modifying `.github/workflows/main.yml`, creating `phaseNN_*_post_attribution_seal_orchestrator` wrappers, ending with no new sealed artifact when work is feasible.

## INITIAL TASK MESSAGE — 2026-11-14T10:30:05Z (execute now)

**TASK ID:** `INIT-2026-11-14T10:30:05Z-EVAL-30-SEAL-TIME-VARYING-SIGNAL`
**STATUS:** **ACTIVE — mandatory heavy-work session.**

> **Hard success/failure floor:** session ends with **>=1 new sealed artifact** `research_state/<EVAL-ID>_<UTC>.{json,md}` containing measured numbers, code paths, tests/verification output, and explicit GO/NO-GO → PASS (trustworthy NO-GO is success). No new sealed artifact / handoff-only / narrative-only / adapter-only → **FAILED**. Fabricated GO or synthetic relabeled as real → **FAILED**.

### 1) Bootstrap (non-negotiable, verified once this session — re-verify only if imports fail)
- `pip3 install -r requirements.txt` (only if a module import fails).
- Verify: `PYTHONPATH=. python3 -c "import src.data.options_timeseries, src.analytics.integrated_options_orderflow_evaluation, src.analytics.real_net_of_cost_evaluation, src.analytics.options_time_varying_signal"` (verified OK 2026-11-14T10:30:05Z).
- Real data present (2 snapshots + orderflow tape). Optional strengthening: acquire a 3rd real snapshot with larger wall-clock separation via `PYTHONPATH=. python3 -m src.data.public_export_acquisition --underlying BTC --orderflow-instrument BTC-USD-SWAP --min-bars 1550 --bar-duration-seconds 15` (public read-only, polite; do not block the session on this).

### 2) Execute to a sealed artifact (the adapter exists — the measurement does not)

**Path A — preferred (measure with what is present; 2 snapshots passes the adapter's own `multi_snapshot_span` check):**
1. Build causal bars from the real tape: `snapshot = load_btc_orderflow()` then `bars = _build_bars(snapshot)` (both in `src/analytics/integrated_options_orderflow_evaluation.py`).
2. Load per-snapshot signals oldest-first: `load_snapshot_signals('BTC')` (raises `RealDataUnavailable` if data missing — never synthetic).
3. Measure: `measure_time_varying_signal(signals, bars['bar_ends_dt'], bars['bar_closes'])` → record per-bar stdev/mean, distinct values, step changes, IC & t-stat per horizon, flat-bar count.
4. Run net-of-cost walk-forward on the time-varying signal (options-only / orderflow-only / combined / flat) using `_run_walkforward`, `evaluate_integrated_options_orderflow`, `evaluate_real_net_of_cost`, and `src/campaign/integrated.py` as available; record OOS Sharpe/return/drawdown/trades/cost/turnover and toxicity engagement.
5. Seal `research_state/OPTIONS_LEG_TRADABILITY_30_<UTC>.{json,md}` via `build_eval30_report(orderflow_bars=bars, net_of_cost=..., integrated=...)` + `write_eval30_artifact`, or an equivalent strict artifact with the same measured fields and explicit GO/NO-GO.

**Path B — fallback (if Path A measurement is externally blocked):**
1. Document the exact blocker with evidence (error output, missing input), implement the smallest missing piece (adapter/runner), and ship **targeted tests** for `src/analytics/options_time_varying_signal.py` (causality/no-lookahead, oldest-first ordering, flat pre-first-snapshot, `RealDataUnavailable` invariant, parity of signal components vs hand-computed values on a fixture).
2. Seal a measured NO-GO artifact `research_state/OPTIONS_LEG_TRADABILITY_30_<UTC>.{json,md}` (or `AMENDED_FUSION_EVAL_30_<UTC>` if measurement is only partial) recording what was measured, the blocker, and verification output. **Never idle.**

### 3) Required engineering discipline
- **Reuse (do not rewrite):** `src/analytics/options_time_varying_signal.py` (EVAL-30 adapter, committed), `src/data/options_timeseries.py`, `src/campaign/integrated.py`, `src/analytics/{integrated_options_orderflow_evaluation,production_simulation_evaluation,real_tape_ingestion,real_data_falsification,real_net_of_cost_evaluation,capacity_aware_tca}.py`, `src/data/{public_export_acquisition,loader,schemas,options_exports}.py`, `src/features/*`, `src/backtest/engine.py`.
- **Invariant:** real loaders raise `RealDataUnavailable` and never fall back to synthetic; do not modify `_causal_options_signal_series` in `integrated_options_orderflow_evaluation.py` (sealed EVAL-18/23/27/29 semantics) — use the additive adapter.
- **Verification:** run `python3 -m py_compile` on touched modules + `python3 -m pytest -q tests/<targeted>`; record pass counts and exact commands in the artifact and handoff.
- **Artifacts:** strict JSON/MD in `research_state/` with `report_id`, timestamps, provenance, measured checks, explicit GO/NO-GO. Never emit `{"valid": true}`. Never fabricate provenance or relabel synthetic as real.
- **Seal in place:** update this handoff with measured numbers, artifact paths, verification results, and the next TASK ID/timestamp.

### 4) Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no venue/config/credential mutation, no order placement.
- Network only for **public read-only** market data acquisition with polite rate limiting; no authenticated calls.
- Do not re-open/mutate sealed artifacts (append new timestamped artifacts only). `scripts/run_backtest.py` is not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` out of scope.

### 5) Traps / invariants
- Options signal is broadcast-static in the sealed EVAL-29 path → mean IC 0.0; the fix is the additive adapter, not re-running EVAL-29.
- Do not repeat constant-spot parity test (EVAL-27 parity NO-GO resolved by EVAL-28).
- Orderflow-only net-of-cost is a measured NO-GO on prior real tapes; do not cherry-pick a favorable window.
- Real data is gitignored — "blocked on data" is invalid without running acquisition and measuring; this checkout already has 2 real snapshots + real tape.
- Multi-snapshot consumers must use `discover_all_real_options_exports` (oldest-first).
- The EVAL-30 adapter module exists but has **no artifact and no tests** — building tests alone or an adapter-only change is a failed session without the sealed measurement.

## CAMPAIGN QUEUE

| Eval | Focus | Status |
|---|---|---|
| EVAL-02..EVAL-22 | Sealed prior gates | **SEALED** |
| EVAL-23B / EVAL-24A | Export adapters | **SEALED** |
| EVAL-25 | Real-data acquisition & falsification | **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`) |
| EVAL-26 | Public real-data acquisition | **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T064702Z`) |
| EVAL-23 | Real net-of-cost verdict | **SEALED NO-GO** (`REAL_NET_OF_COST_EVAL_23_20261114T040000Z`) |
| EVAL-24 | Options-leg validity | **SEALED NO-GO** (`OPTIONS_LEG_VALIDITY_24_20261114T041000Z`) |
| EVAL-27 | Options time-series tradability / amended-fusion | **SEALED NO-GO** (`OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z`, `AMENDED_FUSION_EVAL_27_20261114T065033Z`) |
| EVAL-28 | Per-expiry forward-calibrated parity | **SEALED GO** (`OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z`, re-confirmed `..._20261114T093132Z`) |
| EVAL-29 | Options-leg tradability / net-of-cost (calibrated forwards) | **SEALED NO-GO** (`OPTIONS_LEG_TRADABILITY_29_20261114T093151Z`) — root cause: broadcast-static signal |
| **EVAL-30** | **Time-varying causal options signal: measure + seal** | **ACTIVE — adapter built & verified; measurement, tests, and sealed artifact pending** |

## FOCUS CAMPAIGN (non-optional heavy work)
Every session must, in order, and may not skip any step: (0) verify bootstrap (imports; `pip3 install -r requirements.txt` only on failure) and real-data presence (2 snapshots + real tape confirmed 2026-11-14T10:30:05Z); (1) execute the EVAL-30 task block above to a **measured conclusion** — build bars from the real tape, measure the time-varying signal (`measure_time_varying_signal`), run the net-of-cost walk-forward, add targeted tests for `options_time_varying_signal`; (2) produce **>=1 new sealed artifact** `research_state/OPTIONS_LEG_TRADABILITY_30_<UTC>.{json,md}` with measured numbers and explicit GO/NO-GO; (3) record pass counts/artifact paths/commands in this handoff; (4) update the queue and next TASK ID/timestamp. Building the adapter is already done — a session that ends without a sealed measurement artifact (only code, tests, or restated intent) is a **failed session**. If measurement is externally blocked, Path B still requires a sealed measured NO-GO artifact documenting the blocker with evidence. Never idle, never ask follow-up questions.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Do not create competing handoff files. Final responses must not ask follow-up questions.
