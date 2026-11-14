# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**Initial task message (timestamped, for the next agentic work session): 2026-11-14T09:32:00Z (UTC).**
**Active task:** `INIT-2026-11-14T09:32:00Z-EVAL-30-TIME-VARYING-OPTIONS-SIGNAL` (mandatory heavy work; see "INITIAL TASK MESSAGE" below — execute to a sealed artifact, not analysis-only).
**Handoff state basis:** rewritten after a **measured** session (2026-11-14T09:32:00Z): environment bootstrap verified, real data re-acquired, parity GO re-confirmed on fresh snapshots, integrated net-of-cost eval re-run, and **EVAL-29 sealed** (`OPTIONS_LEG_TRADABILITY_29_20261114T093151Z.{json,md}`, verdict NO-GO).

**Session verification (2026-11-14T10:26:05Z):** repo inspected; this file remains the single durable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md`, and `research_state/INITIAL_TASK_20261114T063750Z.md` are retired pointers (no task IDs). No other competing handoff files found. **Bottleneck removal for next session is explicit below:** bootstrap deps + re-acquire gitignored real data first, then do heavy EVAL-30 work to produce `>=1` new sealed `research_state/<EVAL-ID>_<UTC>.{json,md}` (trustworthy NO-GO counts). Do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

## VERIFIED STATE (measured 2026-11-14T09:32:00Z — this is the ground truth; do not assume the older "unblocked" claim without re-checking)

- **Sealed gates:** EVAL-02..EVAL-22 **SEALED**. EVAL-23B/EVAL-24A adapters **SEALED**. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z.{json,md}`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T064702Z.{json,md}` latest).
- **EVAL-23 SEALED (NO-GO, trustworthy)** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z.{json,md}` (8/11 checks). Combined IC mean -0.016776 (|t|=4.1008, p=0.0020, adverse); options-only OOS Sharpe 8.760 / 591 trades / cost 635.09; orderflow-only Sharpe -2.338 / 502 trades / cost 588.15; `options_leg_degenerate=true`, `options_signal_tradable` FAIL.
- **EVAL-24 SEALED (NO-GO, trustworthy)** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z.{json,md}` (3/8 checks): `surface_reconstructed`, `surface_arbitrage_free`, `greeks_analytic_vs_finite_difference`, `put_call_parity`, `options_leg_tradable` FAIL; venue IV/greeks/OI coverage 0%.
- **EVAL-27 SEALED (both paths, trustworthy NO-GO):**
  - Path A `OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z.{json,md}` — 3 real snapshots, span 10,659.8s, `options_leg_tradable=false`, reason "1017 put-call parity violation(s)" (constant-spot parity; **confound resolved by EVAL-28**).
  - Path B `AMENDED_FUSION_EVAL_27_20261114T065033Z.{json,md}` — 5/7 checks, `options_signal_exists` FAIL, `combined_net_of_cost_superior` FAIL; combined OOS Sharpe -100.33, options-only -483.88, orderflow-only 0.79; IC combined -0.07696 (|t|=5.06); defensible_edge=false.
- **EVAL-28 SEALED (GO, additive, measured):** `OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z.{json,md}`. Per-expiry forward-calibrated put-call parity holds on **1017/1017 pairs (100.0%)** within bid-ask spread across 3 snapshots / 12 expiries each; **min R² = 0.999919**. **This overturns the EVAL-27 parity NO-GO: it was a stale-constant-spot artifact, not an arbitrage.** **Re-confirmed this session on freshly re-acquired snapshots: 777/777 pairs (100.0%), min R²=0.999903** (`OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T093132Z`).
- **EVAL-29 SEALED (NO-GO, trustworthy, measured this session):** `OPTIONS_LEG_TRADABILITY_29_20261114T093151Z.{json,md}` (seal script `scripts/eval29_options_tradability_seal.py`). Verdict NO-GO: options leg parity-consistent (GO) but `options_signal_exists` FAIL (mean IC 0.0) and `combined_net_of_cost_superior` FAIL; integrated eval 5/7 checks. Options-only WF Sharpe -483.876 / 114 trades / cost $55.83; orderflow-only Sharpe 0.785 / 97 trades / cost $58.26; combined Sharpe -100.333 / 51 trades / cost $53.35.
- **CRITICAL ENVIRONMENT FACT (this is the real bottleneck the old handoff hid):** In a fresh checkout, **Python deps are NOT installed** — `import numpy` failed and every EVAL entry point failed to import until `pip3 install -r requirements.txt` was run (numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3, requests 2.31.0). **Do this FIRST every session.** `.env` **ABSENT** (paper-only). Do not create it.
- **Real inputs (gitignored — absent in a fresh checkout; must be re-acquired):** `data/raw/orderflow_okx_BTC-USD-SWAP.json` and `data/raw/options_okx_BTC_<UTC>.json` are `.gitignore`d, so a fresh clone has **only synthetic fixtures** (`orderflow_btcusdt_synthetic.json`, `options_btc_synthetic.json`). Re-acquire real data with `PYTHONPATH=. python3 -m src.data.public_export_acquisition --underlying BTC --orderflow-instrument BTC-USD-SWAP` (network works; public read-only). Synthetic fixtures — **never relabel as real, never use via real loaders**. This session re-acquired: 2 options snapshots (825/824 quotes, 14 expiries, span 47.8s) + 1 small orderflow tape (100 trades). The old handoff's "real files present" claim was false in this checkout.
- **Targeted regression (re-run 2026-11-14T09:29Z):** `PYTHONPATH=. python3 -m pytest -q tests/test_integrated_options_orderflow_evaluation.py tests/test_real_data_inputs.py tests/test_public_export_acquisition.py tests/test_options_timeseries_parity_calibration.py` → **43 passed, 1 skipped in 4.33s**.
- **EVAL-30 entry points verified present & importable 2026-11-14T09:30Z:** `src/data/options_timeseries.py` (`discover_all_real_options_exports`, `load_options_timeseries`, `calibrate_expiry_parity`); `src/analytics/{real_net_of_cost_evaluation,integrated_options_orderflow_evaluation,capacity_aware_tca,production_simulation_evaluation}.py`; `src/campaign/integrated.py`. EVAL-30 is **unblocked once deps + real data are bootstrapped**.

## BOTTLENECKS (active — must be resolved by measured evidence, not narrative)

- **Removed (measured):**
  1. **Stale-constant-spot parity confound:** EVAL-27 used `REFERENCE_SPOT=66825.3` for every strike/expiry; per-expiry forward fitting (`C_mid - P_mid = F/S - K/S`) yields 100% within-spread, R²>0.9999 (EVAL-28). Options chain is internally arbitrage-free.
  2. EVAL-23/24 sealing, data acquisition plumbing, real loaders, sizing/causal-gap blockers, public export acquisition baseline.
  3. **"Where do I start" blocker:** the exact EVAL-29 entry-point functions are named below; the net-of-cost walk-forward machinery exists and imports cleanly. No exploration tax — start at the named functions.
- **Active:**
  1. **Options-leg signal is broadcast-static by design (MEASURED root cause of the EVAL-29 NO-GO).** `src/analytics/integrated_options_orderflow_evaluation.py :: _causal_options_signal_series` broadcasts a single static options snapshot value to every bar → zero time-variation → mean IC 0.0 → `options_signal_exists` FAILs. The options leg **cannot** produce an edge until the signal is computed **per-snapshot over time**. This is the single most important measured finding; EVAL-30 exists to fix it.
  2. **Insufficient real snapshot span for a time-varying signal:** this session acquired only 2 snapshots 47.8s apart. A defensible time-varying options signal needs >=3 real snapshots separated by a meaningful wall-clock window (or a code path that derives within-snapshot cross-sectional variation).
  3. **Orderflow-only net-of-cost negative** on current real tape (EVAL-23 Sharpe -2.338; EVAL-27 orderflow-only Sharpe 0.79 but negative return).
  4. **Fusion/combined does not beat best pillar net-of-cost** (EVAL-29 combined Sharpe -100.33 vs orderflow-only 0.79).
  5. **Provenance limits:** `authenticity_verified=false`; inverse BTC-USD-SWAP tape + spot option snapshots; no signed venue attestation.
  6. **`research_state/` noise:** thousands of non-actionable artifacts. **Never enumerate `research_state/`**; read/write only by exact path.
- **Current real-loader semantics (measured in code):** `src/campaign/integrated.load_real_options_chain` / discovery pick the **newest** real export by filename recency. Multi-snapshot consumers must use `src/data/options_timeseries.discover_all_real_options_exports` (oldest-first) and keep sealed single-snapshot semantics intact.

**Prohibited (time sinks / regressions):** discovery runs, recreating/mutating sealed EVAL-23/24/27/28 artifacts, enumerating `research_state/`, full test suite (5,297 tests), modifying `.github/workflows/main.yml`, creating `phaseNN_*_post_attribution_seal_orchestrator` wrappers, leaving a clean tree without a new sealed artifact when work is feasible.

---

## INITIAL TASK MESSAGE — 2026-11-14T09:32:00Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-14T09:32:00Z-EVAL-30-TIME-VARYING-OPTIONS-SIGNAL`
**STATUS:** **ACTIVE — mandatory heavy-work session.** EVAL-29 sealed NO-GO with a *measured* root cause: the options signal is broadcast-static (`_causal_options_signal_series`), giving IC 0.0. EVAL-30 must produce a **time-varying** causal options signal and re-measure net-of-cost.

> **Hard success/failure floor:** session ends with **>=1 new sealed artifact** `research_state/<EVAL-ID>_<UTC>.{json,md}` containing measured numbers, code paths, tests/verification output, and explicit GO/NO-GO → PASS (NO-GO is success if trustworthy). No new sealed artifact / handoff-only / narrative-only → **FAILED**. Fabricated GO or synthetic relabeled as real → **FAILED**.

### Bootstrap first (measured this session — non-negotiable)
1. `pip3 install -r requirements.txt` (deps are NOT pre-installed in a fresh checkout; without this every import fails).
2. Re-acquire real data: `PYTHONPATH=. python3 -m src.data.public_export_acquisition --underlying BTC --orderflow-instrument BTC-USD-SWAP --min-bars 1550 --bar-duration-seconds 15` (network works; public read-only). If 1550 bars is too slow, first confirm options-only acquisition works, then bound orderflow pages.
3. Verify `PYTHONPATH=. python3 -c "import src.data.options_timeseries, src.analytics.integrated_options_orderflow_evaluation"` prints no error before proceeding.

### Execute one path to completion. Do not stop at analysis.

**Path A — preferred (make the options signal time-varying, the measured fix):**
1. **Extend** `src/analytics/integrated_options_orderflow_evaluation.py :: _causal_options_signal_series` so it does **not** broadcast one static value. Replace it with a per-snapshot causal signal built from `src/data/options_timeseries.load_options_timeseries` (per-expiry forward drift, ATM IV from solved surface, PCR, skew, gamma-flip distance, term-structure slope). No lookahead; each snapshot uses only its own timestamp. Keep the old function or gate it behind a flag so sealed EVAL-29 semantics are preserved.
2. Acquire **>=3 real options snapshots** separated by a meaningful wall-clock window (public OKX read-only, polite). Use `discover_all_real_options_exports` (oldest-first).
3. Run net-of-cost walk-forward with real loaders (`evaluate_integrated_options_orderflow`, `evaluate_real_net_of_cost`, `evaluate_capacity_aware_tca`, `evaluate_production_simulation`, `src/campaign/integrated.py`).
4. Seal `OPTIONS_LEG_TRADABILITY_30_<UTC>.{json,md}`: n_snapshots, span, per-snapshot coverage, **signal time-variation (stdev/mean) and IC & significance**, net-of-cost OOS Sharpe/return/drawdown/trades/cost/turnover, toxicity engagement, explicit GO/NO-GO. A trustworthy NO-GO is success.

**Path B — fallback (if >=3 real snapshots cannot be acquired in-session):**
1. Make the signal vary **cross-sectionally within a single snapshot** (e.g., term-structure slope, skew slope, per-expiry forward drift across expiries) rather than across time — but only if causally valid and clearly documented.
2. Run measured evaluation and seal `AMENDED_FUSION_EVAL_30_<UTC>.{json,md}` with per-variant metrics, IC & significance, toxicity engagement, thresholds, explicit GO/NO-GO.

**If blocked by external limits:** ship the adapter + targeted tests + a measured NO-GO artifact documenting the exact blocker with evidence. Never idle.

### Required engineering discipline
- **Reuse (do not rewrite):** `src/data/options_timeseries.py`, `src/campaign/integrated.py`, `src/analytics/{integrated_options_orderflow_evaluation,production_simulation_evaluation,real_tape_ingestion,real_data_falsification,real_net_of_cost_evaluation}.py`, `src/data/{public_export_acquisition,loader,schemas,options_exports}.py`, `src/features/*`, `src/backtest/engine.py`.
- **Keep invariant:** real loaders raise `RealDataUnavailable` and never fall back to synthetic.
- **Tests/verification:** add/extend targeted tests; run `python3 -m py_compile` on touched modules + `python3 -m pytest -q ...`; record pass counts and commands.
- **Artifacts:** strict JSON/MD in `research_state/` with `report_id`, timestamps, provenance, measured checks, explicit GO/NO-GO. Never emit `{"valid": true}`. Never fabricate provenance or relabel synthetic as real.
- **Seal in place:** update this handoff with measured numbers, artifact paths, verification results, and the next TASK ID/timestamp.

### Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no venue/config/credential mutation, no order placement.
- Network only for **public read-only** market data acquisition with polite rate limiting; no authenticated calls.
- Do not re-open/mutate sealed artifacts (append new timestamped artifacts only). `scripts/run_backtest.py` is not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` out of scope.

### Traps / invariants
- The options signal is broadcast-static today (`_causal_options_signal_series`) → mean IC 0.0. **This is the bug EVAL-30 fixes.** Do not re-run EVAL-29 expecting a different answer.
- Do not repeat the constant-spot parity test (EVAL-27 parity NO-GO is resolved by EVAL-28; chain is arbitrage-free per-expiry).
- Orderflow-only net-of-cost is a measured NO-GO (EVAL-23 Sharpe -2.338; EVAL-27 Sharpe 0.79 but negative return).
- Real data is gitignored — a fresh checkout has only synthetic fixtures. "Blocked on data" is invalid without running acquisition and measuring.
- Real loaders pick the newest export by filename recency; multi-snapshot consumers must use `discover_all_real_options_exports` (oldest-first).

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
| EVAL-28 | Per-expiry forward-calibrated parity | **SEALED GO** (`OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z`; re-confirmed `..._20261114T093132Z`) |
| EVAL-29 | Options-leg tradability / net-of-cost with calibrated forwards | **SEALED NO-GO** (`OPTIONS_LEG_TRADABILITY_29_20261114T093151Z`) — measured root cause: broadcast-static signal |
| **EVAL-30** | **Time-varying causal options signal (fix broadcast-static bug) + re-measure net-of-cost** | **ACTIVE — must seal new artifact with measured GO/NO-GO** |

## FOCUS CAMPAIGN (non-optional heavy work)
Every session must: (0) bootstrap deps (`pip3 install -r requirements.txt`) and re-acquire real data, (1) execute EVAL-30 Path A or Path B to a measured conclusion, (2) produce >=1 new sealed artifact with measured numbers and explicit GO/NO-GO, (3) record pass counts/artifact paths in this handoff, (4) update queue and next TASK ID/timestamp. Reading/restating without a new sealed artifact is a failed session. The single biggest time sink to avoid: assuming "unblocked" from a stale handoff — verify deps + real data present first.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.