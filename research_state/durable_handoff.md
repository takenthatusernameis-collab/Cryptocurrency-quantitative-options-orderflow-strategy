# SINGLE DURABLE HANDOFF — READ FIRST

**Initial task message (timestamped, for the next agentic work session): 2026-11-14T08:52:41Z (UTC).** Handoff refreshed/verified at working tree 2026-11-14T08:52:41Z.

`research_state/durable_handoff.md` is the **only** actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/INITIAL_TASK_20261114T063750Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

## VERIFIED STATE (refreshed 2026-11-14T08:52:41Z)

- **Sealed gates:** EVAL-02..EVAL-22 **SEALED**. EVAL-23B/EVAL-24A adapters **SEALED**. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z.{json,md}`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T064702Z.{json,md}` latest).
- **EVAL-23 SEALED (NO-GO, trustworthy)** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z.{json,md}` (8/11 checks). Combined IC mean -0.016776 (|t|=4.1008, p=0.0020, adverse); options-only OOS Sharpe 8.760 / 591 trades / cost 635.09; orderflow-only Sharpe -2.338 / 502 trades / cost 588.15; `options_leg_degenerate=true`, `options_signal_tradable` FAIL.
- **EVAL-24 SEALED (NO-GO, trustworthy)** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z.{json,md}` (3/8 checks): `surface_reconstructed`, `surface_arbitrage_free`, `greeks_analytic_vs_finite_difference`, `put_call_parity`, `options_leg_tradable` FAIL; venue IV/greeks/OI coverage 0%.
- **EVAL-27 SEALED (both paths, trustworthy NO-GO):**
  - Path A `OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z.{json,md}` — 3 real snapshots, span 10,659.8s, `options_leg_tradable=false`, reason "1017 put-call parity violation(s)" (constant-spot parity; **confound resolved by EVAL-28**).
  - Path B `AMENDED_FUSION_EVAL_27_20261114T065033Z.{json,md}` — 5/7 checks, `options_signal_exists` FAIL, `combined_net_of_cost_superior` FAIL; combined OOS Sharpe -100.33, options-only -483.88, orderflow-only 0.79; IC combined -0.07696 (|t|=5.06); defensible_edge=false.
- **EVAL-28 SEALED (GO, additive, measured):** `OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z.{json,md}`. Per-expiry forward-calibrated put-call parity holds on **1017/1017 pairs (100.0%)** within bid-ask spread across 3 snapshots / 12 expiries each; **min R² = 0.999919**. **This overturns the EVAL-27 parity NO-GO: it was a stale-constant-spot artifact, not an arbitrage.**
- **Environment:** Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3, requests 2.31.0. `.env` **ABSENT** (paper-only). Do not create it.
- **Real inputs present (gitignored):**
  - `data/raw/orderflow_okx_BTC-USD-SWAP.json` — 15,195,423 bytes, 71,700 trades / 1,552 bars (15s), span 2026-11-13T21:22:50.143Z→2026-11-14T03:50:49.071Z.
  - `data/raw/options_okx_BTC_20261114T034546Z.json` — 731 quotes, 12 expiries, 88 strikes.
  - `data/raw/options_okx_BTC_20261114T035050Z.json` — 728 quotes, 12 expiries, 88 strikes.
  - `data/raw/options_okx_BTC_20261114T064702Z.json` — 730 quotes, 12 expiries, 89 strikes.
  - Synthetic fixtures (`orderflow_btcusdt_synthetic.json`, `options_btc_synthetic.json`) — **never relabel as real, never use via real loaders**.
- **Targeted regression (2026-11-14T08:52Z):** `PYTHONPATH=. python3 -m pytest -q tests/test_integrated_options_orderflow_evaluation.py tests/test_real_data_inputs.py tests/test_public_export_acquisition.py tests/test_options_timeseries_parity_calibration.py` → **44 passed in 4.57s**.

## BOTTLENECKS (active — must be resolved by measured evidence, not narrative)

- **Removed (measured):**
  1. **Stale-constant-spot parity confound:** EVAL-27 used `REFERENCE_SPOT=66825.3` for every strike/expiry; per-expiry forward fitting (`C_mid - P_mid = F/S - K/S`) yields 100% within-spread, R²>0.9999 (EVAL-28). Options chain is internally arbitrage-free.
  2. EVAL-23/24 sealing, data acquisition plumbing, real loaders, sizing/causal-gap blockers, public export acquisition baseline.
- **Active:**
  1. **Options-leg tradability is parity-consistent but not yet net-of-cost evaluated.** EVAL-28 proves the chain is usable; it does **not** prove a time-varying signal or edge. EVAL-29 must compute causal per-snapshot options features/signals with per-expiry forwards and measure IC / time variation / net-of-cost OOS.
  2. **Orderflow-only net-of-cost negative** on current real tape (EVAL-23 Sharpe -2.338; EVAL-27 orderflow-only Sharpe 0.79 but return -0.083).
  3. **Fusion/combined does not beat best pillar net-of-cost** (EVAL-27 combined Sharpe -100.33 vs orderflow-only 0.79).
  4. **Provenance limits:** `authenticity_verified=false`; inverse BTC-USD-SWAP tape + spot option snapshots; no signed venue attestation.
  5. **`research_state/` noise:** thousands of non-actionable artifacts. **Never enumerate `research_state/`**; read/write only by exact path.
- **Current real-loader semantics (measured in code):** `src/campaign/integrated.load_real_options_chain` / discovery pick the **newest** real export by filename recency. Multi-snapshot consumers must use `src/data/options_timeseries.discover_all_real_options_exports` (oldest-first) and keep sealed single-snapshot semantics intact.

**Prohibited (time sinks / regressions):** discovery runs, recreating/mutating sealed EVAL-23/24/27/28 artifacts, enumerating `research_state/`, full test suite (5,297 tests), modifying `.github/workflows/main.yml`, creating `phaseNN_*_post_attribution_seal_orchestrator` wrappers, leaving a clean tree without a new sealed artifact when work is feasible.

---

## INITIAL TASK MESSAGE — 2026-11-14T08:52:41Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-14T08:52:41Z-EVAL-29-OPTIONS-TRADABILITY-NET-OF-COST`
**STATUS:** **ACTIVE — mandatory heavy-work session.** EVAL-27 sealed (parity confound), EVAL-28 sealed GO (per-expiry parity consistent); EVAL-29 must produce a measured options-leg tradability / net-of-cost verdict.

> **Hard success/failure floor:** session ends with **>=1 new sealed artifact** `research_state/<EVAL-ID>_<UTC>.{json,md}` containing measured numbers, code paths, tests/verification output, and explicit GO/NO-GO → PASS (NO-GO is success if trustworthy). No new sealed artifact / handoff-only / narrative-only → **FAILED**. Fabricated GO or synthetic relabeled as real → **FAILED**.

### Execute one path to completion (pick highest-leverage unblocked; if blocked, seal measured NO-GO). Do not stop at analysis.

**Path A — preferred (options-leg tradability on real data, now unblocked by EVAL-28):**
1. **Reuse** `src/data/options_timeseries.py`: `discover_all_real_options_exports` (oldest-first), `load_options_timeseries`, `calibrate_expiry_parity` (per-expiry forward). Extend with a causal **per-snapshot signal** (e.g., per-expiry forward drift, ATM IV from solved surface, PCR, skew, gamma-flip distance, term-structure slope) — no lookahead, snapshot timestamp only.
2. Compute options features/signals **per snapshot over time** (3 snapshots now; attempt to acquire more via public OKX read-only endpoints if feasible, polite rate limits). Reuse `src/features/{iv_surface,options_pricing,gamma_exposure,volatility}.py`, `src/data/{loader,schemas,options_exports,public_export_acquisition}.py`.
3. Run net-of-cost walk-forward with real loaders: `src/analytics/integrated_options_orderflow_evaluation.py`, `src/campaign/integrated.py`, `src/analytics/capacity_aware_tca.py`, `src/analytics/production_simulation_evaluation.py`, `src/analytics/real_net_of_cost_evaluation.py`.
4. Seal `OPTIONS_LEG_TRADABILITY_29_<UTC>.{json,md}`: n_snapshots, span, per-snapshot coverage, signal time-variation (stdev/mean, IC & significance), net-of-cost OOS Sharpe/return/drawdown/trades/cost/turnover, toxicity engagement, explicit GO/NO-GO answering “does the options leg constitute a defensible net-of-cost edge on current real data?” (expect NO-GO unless evidence proves otherwise; a measured NO-GO is success).

**Path B — fallback (amended fusion / orderflow-only, only if options signal is non-time-varying):**
1. Run measured evaluation on the same real inputs comparing: (i) sealed fusion baseline reproduced, (ii) orderflow-only when options leg degenerate, (iii) toxicity-filtered / regime-gated variant justified by diagnostics.
2. Seal `AMENDED_FUSION_EVAL_29_<UTC>.{json,md}` with per-variant net-of-cost metrics, IC & significance, toxicity engagement, numeric thresholds, explicit GO/NO-GO.

**If blocked by external limits:** ship adapter/diagnostic code + targeted tests + a measured NO-GO artifact documenting the exact blocker with evidence. Never idle.

### Required engineering discipline
- **Reuse (do not rewrite):** `src/data/options_timeseries.py`, `src/campaign/integrated.py` (`load_real_orderflow`, `load_real_options_chain`, discovery), `src/analytics/integrated_options_orderflow_evaluation.py`, `src/analytics/production_simulation_evaluation.py`, `src/analytics/real_tape_ingestion.py`, `src/analytics/real_data_falsification.py`, `src/data/public_export_acquisition.py`, `src/data/loader.py`, `src/data/schemas.py`, `src/features/*`, `src/backtest/engine.py`.
- **Keep invariant:** real loaders raise `RealDataUnavailable` and never fall back to synthetic.
- **Tests/verification:** add/extend targeted tests for new behavior; run `python3 -m py_compile` on touched modules + relevant `python3 -m pytest -q ...` suites; record pass counts and commands.
- **Artifacts:** strict JSON/MD in `research_state/` with `report_id`, timestamps, provenance, measured checks, explicit GO/NO-GO. Never emit `{"valid": true}`. Never fabricate provenance or relabel synthetic as real.
- **Seal in place:** update this handoff with what you measured, artifact paths (and hashes where useful), verification results, and the next concrete TASK ID/timestamp. Commit partial work if incomplete — never leave progress only in chat.

### Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no venue/config/credential mutation, no order placement.
- Network only for **public read-only** market data acquisition with polite rate limiting; no authenticated calls.
- Do not re-open/mutate sealed artifacts (append new timestamped artifacts only). `scripts/run_backtest.py` is not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` out of scope.

### Traps / invariants
- EVAL-27 parity NO-GO is **resolved** by EVAL-28: the chain is arbitrage-free per-expiry. Do not repeat the constant-spot parity test.
- Orderflow-only net-of-cost Sharpe -2.338 (EVAL-23) / +0.79 with negative return (EVAL-27) is a measured NO-GO signal.
- Real loaders select newest matching export by filename recency; multi-snapshot consumers must use `discover_all_real_options_exports` (oldest-first) and keep sealed semantics.
- Three real option snapshots exist (03:49Z, 03:54Z, 06:47Z); “blocked on data” is not valid without attempting to use/acquire and measuring.

## CAMPAIGN QUEUE

| Eval | Focus | Status |
|---|---|---|
| EVAL-02..EVAL-22 | Sealed prior gates | **SEALED** |
| EVAL-23B / EVAL-24A | Export adapters | **SEALED** |
| EVAL-25 | Real-data acquisition & falsification | **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`) |
| EVAL-26 | Public real-data acquisition | **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T064702Z`) |
| EVAL-23 | Real net-of-cost verdict | **SEALED NO-GO** (`REAL_NET_OF_COST_EVAL_23_20261114T040000Z`) |
| EVAL-24 | Options-leg validity | **SEALED NO-GO** (`OPTIONS_LEG_VALIDITY_24_20261114T041000Z`) |
| EVAL-27 | Options time-series tradability OR amended-fusion | **SEALED NO-GO** (`OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z`, `AMENDED_FUSION_EVAL_27_20261114T065033Z`) |
| EVAL-28 | Per-expiry forward-calibrated parity | **SEALED GO** (`OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z`) |
| **EVAL-29** | **Options-leg tradability / net-of-cost with calibrated forwards** | **ACTIVE — must seal new artifact with measured GO/NO-GO** |

## FOCUS CAMPAIGN (non-optional heavy work)
Every session must: (1) execute Path A or Path B to a measured conclusion, (2) produce >=1 new sealed artifact with measured numbers and explicit GO/NO-GO, (3) record pass counts/artifact paths in this handoff, (4) update queue and next TASK ID/timestamp. Reading/restating without a new sealed artifact is a failed session.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.