# SINGLE DURABLE HANDOFF — READ FIRST

**Initial task message (timestamped, for the next agentic work session): 2026-11-14T06:02:16Z (UTC).** Handoff refreshed/verified at working tree 2026-11-14T06:02:16Z.

`research_state/durable_handoff.md` is the **only** actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

## VERIFIED STATE (refreshed 2026-11-14T06:02:16Z)

- **Sealed gates:** EVAL-02..EVAL-22 **SEALED**. EVAL-23B/EVAL-24A adapters **SEALED**. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z.{json,md}`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T035050Z.{json,md}` latest). **EVAL-23 SEALED (NO-GO, trustworthy)** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z.{json,md}` (8/11 checks). **EVAL-24 SEALED (NO-GO, trustworthy)** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z.{json,md}` (3/8 checks, `options_leg_degenerate=true`).
- **Environment:** Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3, requests 2.31.0. `.env` **ABSENT** (paper-only). Do not create it.
- **Real inputs present (gitignored; regenerate/extend via EVAL-26-style acquisition if needed):**
  - `data/raw/orderflow_okx_BTC-USD-SWAP.json` (15,195,423 bytes) — SHA-256 `331dc04e...`, venue okx, inverse BTC-USD-SWAP, 71,700 trades / 1,552 bars (15s), span 2026-11-13T21:22:50.143Z→2026-11-14T03:50:49.071Z.
  - `data/raw/options_okx_BTC_20261114T034546Z.json` (731 quotes, acquired 2026-11-14T03:49:23.491920Z, 46 distinct quote timestamps).
  - `data/raw/options_okx_BTC_20261114T035050Z.json` (728 quotes, acquired 2026-11-14T03:54:26.712854Z, 29 distinct quote timestamps, SHA-256 `375aa0cf...`, 339 calls / 389 puts, 12 expiries, 88 strikes, spot 66825.3 per prior artifact).
  - **Bottleneck partially removed:** **2 real option snapshots already exist** (~5 min apart). Do not claim “no multi-snapshot options data”; immediate time-series pipeline work is unblocked on existing snapshots (and you must attempt to acquire more if feasible).
  - Synthetic fixtures (`orderflow_btcusdt_synthetic.json`, `options_btc_synthetic.json`) — **never relabel as real, never use via real loaders**.
- **Measured EVAL-23 findings:** `verdict=NO-GO`, `data_provenance=real`, `authenticity_verified=false`. Combined IC mean -0.016776 (|t|=4.1008, p=0.0020, adverse), orderflow IC -0.001425, options IC 0.0; combined OOS Sharpe 4.702/return 1.355/219 trades/cost 364.40; options-only Sharpe 8.760/return 13.501/591 trades/cost 635.09; orderflow-only Sharpe -2.338/return -0.645/502 trades/cost 588.15. Failed: `options_signal_exists`, `combined_net_of_cost_superior`, `options_signal_tradable`. Fusion: `options_leg_degenerate=true`, `combined_flat_because_options_degenerate=false`.
- **Measured EVAL-24 findings:** `verdict=NO-GO`, 3/8 checks. Passed: `chain_richness`, `surface_calibration_residual`, `term_structure_non_degenerate`. Failed: `surface_reconstructed` (IV [0,0.473]), `surface_arbitrage_free` (1 calendar violation), `greeks_analytic_vs_finite_difference` (0.9245 < 0.99), `put_call_parity` (338 pairs, max abs residual 133172.85), `options_leg_tradable`. Venue IV/greeks/OI coverage 0%.
- **Targeted regression (2026-11-14T04:46Z, last recorded):** `PYTHONPATH=. python3 -m pytest -q tests/test_integrated_options_orderflow_evaluation.py tests/test_real_data_inputs.py tests/test_public_export_acquisition.py` → **41 passed in 3.49s**.

## BOTTLENECKS (active — must be resolved by measured evidence, not narrative)

- **Removed:** EVAL-23/24 sealing, data acquisition plumbing, real loaders, sizing/causal-gap blockers, public export acquisition baseline.
- **Active:**
  1. **Options leg not tradable from single-snapshot real chain:** no time-varying options signal; IV/greeks/parity/arbitrage deficiencies on snapshot (EVAL-24) and `options_signal_tradable` FAIL (EVAL-23). **Immediate unblock:** 2 real snapshots exist in `data/raw/`; build a multi-snapshot/time-series options pipeline over them (and acquire additional snapshots if network/rate limits allow) to measure tradability/time-variation.
  2. **Orderflow-only net-of-cost negative** on current real tape (Sharpe -2.338) — no defensible edge as-is.
  3. **Fusion/combined does not beat best pillar net-of-cost** on sealed real eval; options-only backtest looked strong but rested on non-tradable degenerate options leg — tension must be adjudicated by a new sealed measurement.
  4. **Provenance limits:** `authenticity_verified=false`; inverse BTC-USD-SWAP tape + spot option snapshot(s); no signed venue attestation.
  5. **`research_state/` noise:** thousands of non-actionable artifacts. **Never enumerate `research_state/`**; read/write only by exact path.
- **Current real-loader semantics (measured in code):** `src/campaign/integrated.load_real_options_chain` / discovery pick the **newest** real export by filename recency. Any multi-snapshot series work must make loader/consumer semantics explicit and tested (do not silently change behavior for sealed consumers without compatibility).

**Prohibited (time sinks / regressions):** discovery runs, recreating/mutating sealed EVAL-23/24 artifacts, enumerating `research_state/`, full test suite (5,297 tests), modifying `.github/workflows/main.yml`, creating `phaseNN_*_post_attribution_seal_orchestrator` wrappers, leaving a clean tree without a new sealed artifact when work is feasible.

---

## INITIAL TASK MESSAGE — 2026-11-14T06:02:16Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-14T06:02:16Z-EVAL-27-OPTIONS-TIMESERIES-OR-AMENDED-FUSION`
**STATUS:** **ACTIVE — mandatory heavy-work session.** EVAL-23/24 sealed as trustworthy NO-GO; EVAL-27 must produce measured resolution.

> **Hard success/failure floor:** session ends with **>=1 new sealed artifact** `research_state/<EVAL-ID>_<UTC>.{json,md}` containing measured numbers, code paths, tests/verification output, and explicit GO/NO-GO → PASS (NO-GO is success if trustworthy). No new sealed artifact / handoff-only / narrative-only → **FAILED**. Fabricated GO or synthetic relabeled as real → **FAILED**.

### Execute one path to completion (pick highest-leverage unblocked; if blocked, seal measured NO-GO). Do not stop at analysis.

**Path A — preferred (real options time-series): make the options leg genuinely time-varying and tradable on real data.**
1. **Use existing data first:** load/align the **2 existing real option snapshots** in `data/raw/` (`options_okx_BTC_20261114T034546Z.json`, `options_okx_BTC_20261114T035050Z.json`) into a time-ordered series. Then attempt to acquire additional real multi-snapshot options exports via public OKX read-only endpoints (no auth, no `.env`, no orders, polite rate limits) if feasible, persisting loader-compatible, provenance-stamped files under `data/raw/`.
2. Implement explicit multi-snapshot ingestion/consumer support (do not silently break sealed single-snapshot semantics): compute options features/signals **per snapshot over time** (causal, no lookahead), reusing sealed primitives `src/features/iv_surface.py`, `src/features/options_pricing.py`, `src/features/gamma_exposure.py`, `src/features/volatility.py`, `src/data/loader.py`, `src/data/schemas.py`, validators, `src/data/options_exports.py`/`src/data/public_export_acquisition.py` and adapting `src/campaign/integrated.py` / evaluation modules as needed with clear, tested behavior.
3. Seal `OPTIONS_TIMESERIES_INGESTION_27_<UTC>.{json,md}` and/or `OPTIONS_LEG_VALIDITY_27_<UTC>.{json,md}`: n_snapshots, time span, per-snapshot coverage, IV/greeks/parity/arbitrage diagnostics over time, `options_leg_tradable` verdict with evidence, `authenticity_verified` stated honestly. If only 2 snapshots exist, still measure and seal: report measured span/limitations and whether tradability is achieved or remains NO-GO.

**Path B — if multi-snapshot tradability cannot be established: seal amended-fusion / orderflow-only measured evaluation (new artifacts, do not mutate sealed rules silently).**
1. Implement and run measured evaluation using real loaders + net-of-cost/capacity/toxicity/walk-forward machinery (`src/analytics/integrated_options_orderflow_evaluation.py`, `src/campaign/integrated.py`, `src/analytics/capacity_aware_tca.py`, `src/analytics/production_simulation_evaluation.py`, `src/analytics/real_net_of_cost_evaluation.py`). Compare at least: (i) sealed fusion baseline reproduced on same real inputs, (ii) orderflow-only when options leg degenerate, (iii) any defensible variant justified by diagnostics.
2. Seal `AMENDED_FUSION_EVAL_27_<UTC>.{json,md}`: per-variant net-of-cost OOS Sharpe/return/drawdown/trades/cost/turnover, IC & significance, toxicity engagement, numeric thresholds, and explicit GO/NO-GO per variant answering “does any variant constitute defensible edge on current real data?” (expect NO-GO unless evidence proves otherwise).

**If blocked by external limits:** ship adapter/diagnostic code + targeted tests + a measured NO-GO artifact documenting the exact blocker with evidence. Never idle.

### Required engineering discipline
- **Reuse (do not rewrite):** `src/campaign/integrated.py` (`load_real_orderflow`, `load_real_options_chain`, discovery), `src/analytics/integrated_options_orderflow_evaluation.py`, `src/analytics/production_simulation_evaluation.py`, `src/analytics/real_tape_ingestion.py`, `src/analytics/real_data_falsification.py`, `src/data/public_export_acquisition.py`, `src/data/loader.py`, `src/data/schemas.py`, `src/features/*`, `src/backtest/engine.py`.
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
- EVAL-23: options-only OOS Sharpe 8.76 / 591 trades but `options_signal_tradable` FAIL and `options_leg_degenerate=true` on single snapshot — do not claim GO without resolving tradability/time-variation/provenance with evidence.
- Orderflow-only net-of-cost Sharpe -2.338 on current tape is measured NO-GO signal.
- Real loaders select newest matching export by filename recency; if adding multi-snapshot series, make loader/consumer semantics explicit and tested.
- Two real option snapshots already exist; “blocked on data” is not a valid reason without attempting to use/acquire and measuring.

## CAMPAIGN QUEUE

| Eval | Focus | Status |
|---|---|---|
| EVAL-02..EVAL-22 | Sealed prior gates | **SEALED** |
| EVAL-23B / EVAL-24A | Export adapters | **SEALED** |
| EVAL-25 | Real-data acquisition & falsification | **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`) |
| EVAL-26 | Public real-data acquisition | **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T035050Z`, plus earlier 034546Z snapshot present) |
| EVAL-23 | Real net-of-cost verdict | **SEALED NO-GO** (`REAL_NET_OF_COST_EVAL_23_20261114T040000Z`) |
| EVAL-24 | Options-leg validity | **SEALED NO-GO** (`OPTIONS_LEG_VALIDITY_24_20261114T041000Z`) |
| **EVAL-27** | **Options time-series tradability OR amended-fusion measured evaluation** | **ACTIVE — must seal new artifact with measured GO/NO-GO** |

## FOCUS CAMPAIGN (non-optional heavy work)
Every session must: (1) execute Path A or Path B to a measured conclusion, (2) produce >=1 new sealed artifact with measured numbers and explicit GO/NO-GO, (3) record pass counts/artifact paths in this handoff, (4) update queue and next TASK ID/timestamp. Reading/restating without a new sealed artifact is a failed session.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.
