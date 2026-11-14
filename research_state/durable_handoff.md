# SINGLE DURABLE HANDOFF — READ FIRST

**Initial task message (timestamped, for the next agentic work session): 2026-11-14T05:35:49Z (UTC).** Handoff refreshed/verified at HEAD working tree 2026-11-14T05:35:49Z. EVAL-23/EVAL-24 are now **SEALED with measured real-data NO-GO artifacts** (trustworthy NO-GO = success). Prior sealed artifacts remain: `src/data/public_export_acquisition.py`, `tests/test_public_export_acquisition.py`, `src/campaign/integrated.py` (`load_real_orderflow`/`load_real_options_chain`), `tests/test_real_data_inputs.py`, `src/data/options_exports.py`, `src/data/exchange_exports.py`, `src/analytics/real_tape_ingestion.py`, `src/analytics/real_data_falsification.py`, `research_state/REAL_DATA_FALSIFICATION_20261114T025046Z.{json,md}`, `research_state/REAL_TAPE_INGESTION_20261114T025322Z.{json,md}`.

`research_state/durable_handoff.md` is the **only** actionable handoff. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are retired pointers (no task IDs) — do not action, do not create new handoff files.

**Repo priority:** `Cryptocurrency-quantitative-options-orderflow-strategy` — cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** (real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, net-of-cost evaluation).
**Mission:** Deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not a favorable-looking number from a broken harness. A **trustworthy NO-GO** is a full success; a fabricated GO is a failure.

## VERIFIED STATE (measured 2026-11-14T04:46:21Z)

- **Sealed gates:** EVAL-02..EVAL-22 **SEALED**. EVAL-23B/EVAL-24A adapters **SEALED**. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z.{json,md}`, 2 candidates, 1 adequate orderflow + 1 adequate options, fingerprint `fc5b24c2f4e79333faaad5b4f98de90a99ef2046d82f9dd07f4ef2a31bd521ca`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_*`, latest `20261114T035050Z`). **EVAL-23 SEALED (NO-GO, trustworthy). EVAL-24 SEALED (NO-GO, trustworthy).**
- **Environment:** Python 3.12.3, numpy 2.5.4, pandas 3.1.1, scipy 1.18.1, pytest 9.2.0, pydantic 2.14.3, requests 2.31.0. `.env` **ABSENT** (paper-only). Do not create it.
- **Real inputs present (gitignored; regenerate if missing via EVAL-26):**
  - `data/raw/orderflow_okx_BTC-USD-SWAP.json` — SHA-256 `331dc04ee702431d96ec0c30a29c454b613edcd56c1b9a6a0cacbf7e1f7d3624`, venue okx, inverse BTC-USD-SWAP. EVAL-23 evidence: **71,700 trades / 1,552 bars** (15s), span 2026-11-13T21:22:50.143Z→2026-11-14T03:50:49.071Z.
  - `data/raw/options_okx_BTC_20261114T035050Z.json` — SHA-256 `375aa0cfe73ae4daa45cb2fb9fa766865a8616e44633f4e363fe7378d564824a`, 463,134 bytes, venue okx spot options snapshot. EVAL-23/24 evidence: **728 quotes/contracts, 339 calls / 389 puts, 12 expiries, 88 strikes**, spot used 66825.3.
  - Synthetic fixtures remain (`orderflow_btcusdt_synthetic.json`, `options_btc_synthetic.json`) — **never relabel as real, never use via real loaders**.
- **EVAL-23 sealed artifact:** `research_state/REAL_NET_OF_COST_EVAL_23_20261114T040000Z.{json,md}` — `report_id=REAL_NET_OF_COST_EVAL_23`, `trading_mode=paper`, `live_trading_enabled=false`, `data_provenance=real`, `authenticity_verified=false`, `never_valid_true=true`, `verdict=NO-GO`, **8/11 checks passed**. Failed: `options_signal_exists`, `combined_net_of_cost_superior`, `options_signal_tradable`. Measured: combined IC mean -0.016776 (|t|=4.1008, permutation p=0.0020, significant but adverse sign/structure), orderflow IC mean -0.001425, options IC mean 0.0; combined OOS Sharpe 4.702 / return 1.355 / 219 trades / cost 364.40 USD; options-only Sharpe 8.760 / return 13.501 / 591 trades / cost 635.09 USD; orderflow-only Sharpe -2.338 / return -0.645 / 502 trades / cost 588.15 USD; flat 0. Toxicity gate measured (mean 0.8695, engages 83.12%). Fusion adjudication: `options_leg_degenerate=true`, `combined_flat_because_options_degenerate=false`, rule not amended, 725 agree / 657 disagree bars, interpretation “Both pillars produced time variation; the fusion rule is not the binding constraint.” **Measured finding: orderflow-only net-of-cost negative; options-only backtest strong but options leg not tradable as time-varying signal on a single cross-section (EVAL-23 `options_signal_tradable` FAIL).**
- **EVAL-24 sealed artifact:** `research_state/OPTIONS_LEG_VALIDITY_24_20261114T041000Z.{json,md}` — `verdict=NO-GO`, **3/8 checks passed**, `options_leg_degenerate=true`. Passed: `chain_richness`, `surface_calibration_residual`, `term_structure_non_degenerate` (12 ATM tenors). Failed: `surface_reconstructed` (IV range [0,0.473]), `surface_arbitrage_free` (1 calendar violation), `greeks_analytic_vs_finite_difference` (0.9245 < 0.99), `put_call_parity` (338 pairs, max abs residual 133172.85), `options_leg_tradable`. Venue IV/greeks/OI coverage 0% (solved from mid). `authenticity_verified=false`.
- **Targeted regression (measured 2026-11-14T04:46Z):** `PYTHONPATH=. python3 -m pytest -q tests/test_integrated_options_orderflow_evaluation.py tests/test_real_data_inputs.py tests/test_public_export_acquisition.py` → **41 passed in 3.49s**. (Prior broader baseline recorded 2026-11-14T03:00:10Z: 162 passed across 10 files.)

## BOTTLENECK LEDGER

- **Removed:** EVAL-23/EVAL-24 sealing (real net-of-cost + options-leg validity artifacts now exist with measured verdicts). Data acquisition/loader/sizing/causal-gap blockers resolved in prior sessions.
- **Active bottlenecks (must be attacked, not restated):**
  1. **Options leg not tradable from single-snapshot real chain:** time variation/greeks/parity/arbitrage quality insufficient for a trustworthy tradable options signal (EVAL-24 failures; EVAL-23 `options_signal_tradable` FAIL; venue provides no IV/greeks/OI). Single cross-section cannot support a genuinely dynamic options alpha without additional real time-series data or a defensible construction.
  2. **Orderflow-only is net-of-cost negative on current real tape** (Sharpe -2.338, 502 trades) — cannot be declared edge.
  3. **Combined/fusion does not beat best pillar net-of-cost** (`combined_net_of_cost_superior` FAIL) despite measured trades; options-only backtest outperforms but rests on a non-tradable degenerate options leg per sealed checks — **this tension must be resolved by measurement, not narrative**.
  4. **Provenance limits:** `authenticity_verified=false`; inverse BTC-USD-SWAP tape + spot option snapshot; no signed venue attestation.
  5. **`research_state/` noise bottleneck:** directory contains thousands of non-actionable artifacts (`INTEGRATED_STEP_data_ingestion_*.json`, `BACKTEST_*.json`, `CONTINUOUS_VALIDATION_*.json`, `HEALTH_SLO_*.json`, `ALERT_AUDIT_*.json`). **Do not enumerate `research_state/`**. Read/write only by exact path. Enumeration is a time sink and is explicitly prohibited.
- **Do not** rerun discovery, recreate sealed EVAL-23/24, enumerate `research_state/`, run full suite (5,297 tests), modify `.github/workflows/main.yml`, create `phaseNN_*_post_attribution_seal_orchestrator` wrappers, or leave a clean tree without a new sealed artifact when work is feasible.

---

## INITIAL TASK MESSAGE — 2026-11-14T05:35:49Z (copy-paste for next agentic work session)

**TASK ID:** `INIT-2026-11-14T05:35:49Z-EVAL-27-OPTIONS-TIMESERIES-OR-AMENDED-FUSION`
**STATUS:** **ACTIVE — EVAL-23/24 sealed NO-GO; next campaign must resolve the options-leg tradability and fusion/edge tension with new measured evidence.**
> **Hard floor:** a session ending without at least one **new sealed artifact** (`research_state/<EVAL-ID>_<UTC>.{json,md}`) containing measured numbers, code paths, tests/verification output, and an explicit GO/NO-GO verdict is **FAILED**. Handoff-only work is FAILED. A trustworthy NO-GO is success; a fabricated GO is failure.

### Mission for this session (pick the highest-leverage unblocked path and execute fully)

**Path A (preferred, data work): Acquire/build a real options time-series input and re-evaluate options tradability.**
1. Extend `src/data/public_export_acquisition.py` (or add a focused sibling module) to fetch **multiple sequential real option-chain snapshots over time** from public OKX read-only endpoints (same safety: no auth, no `.env`, no orders). Persist as loader-compatible exports under `data/raw/` with provenance (venue, instrument/underlying, timestamps, request params, hashes). Handle gitignore/absence by making acquisition reproducible.
2. Add/extend ingestion so options signals can be computed **per snapshot/bar over time** (causal, no lookahead) rather than broadcasting one cross-section. Reuse sealed primitives: `src/features/iv_surface.py`, `src/features/options_pricing.py`/greeks, `src/features/gamma_exposure.py`, `src/features/volatility.py`, `src/data/loader.py`, `src/data/schemas.py`, validators.
3. Seal **`OPTIONS_TIMESERIES_INGESTION_27_<UTC>.{json,md}`** and/or **`OPTIONS_LEG_VALIDITY_27_<UTC>.{json,md}`** with: n_snapshots, time span, coverage (expiries/strikes/quotes per snapshot), IV/greeks/parity/arbitrage diagnostics over time, whether `options_leg_tradable` becomes true with evidence, and explicit provenance (`authenticity_verified=false` if unattested).

**Path B (if multi-snapshot acquisition is blocked by API/rate/data limits): Seal an amended-fusion/orderflow-only measured evaluation (new EVAL, do not mutate sealed rules silently).**
1. Implement and seal **`AMENDED_FUSION_EVAL_27_<UTC>.{json,md}`** that evaluates, with the same real tape/chain and net-of-cost/capacity/toxicity machinery: (i) sealed fusion baseline (reproduced), (ii) orderflow-only when options leg explicitly degenerate, (iii) any other defensible variant you can justify from measured diagnostics. Use `src/analytics/integrated_options_orderflow_evaluation.py` primitives / `src/campaign/integrated.py` real loaders / `src/analytics/capacity_aware_tca.py` / walk-forward stats.
2. Report per-variant net-of-cost OOS metrics (Sharpe, return, drawdown, trades, cost, turnover), IC/significance, toxicity engagement, and a GO/NO-GO per variant with numeric thresholds. Explicitly adjudicate: does any variant constitute defensible edge on current real data? (Given current measurements, expect NO-GO unless evidence proves otherwise.)

**In all paths:** if blocked, ship the adapter/diagnostic and a measured NO-GO artifact explaining the exact blocker with evidence — never idle, never synthesize “real” data.

### Required engineering discipline
- **Reuse (do not rewrite):** `src/campaign/integrated.py` (`load_real_orderflow`, `load_real_options_chain`), `src/analytics/integrated_options_orderflow_evaluation.py`, `src/analytics/production_simulation_evaluation.py`, `src/analytics/real_tape_ingestion.py`, `src/analytics/real_data_falsification.py`, `src/data/public_export_acquisition.py`, `src/data/loader.py`, `src/data/schemas.py`, `src/features/*`, `src/backtest/engine.py`.
- **Tests:** add/extend targeted tests for any new module/behavior; run at minimum relevant suites with `python3 -m pytest -q ...` and record pass counts in the artifact/handoff.
- **Verification:** `python3 -m py_compile` touched modules + targeted pytest. No full suite. No `research_state/` enumeration.
- **Artifacts:** strict JSON/MD in `research_state/` with `report_id`, timestamps, provenance, measured checks, and explicit GO/NO-GO. Never emit `{"valid": true}`. Never fabricate provenance.
- **Seal in place:** update this handoff with what you measured, artifact paths/hashes, verification results, and the next concrete task/timestamp/ID. Commit partial work if incomplete — never leave progress only in chat.

### Hard constraints
- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, no venue/config/credential mutation, no order placement.
- Network allowed only for **public read-only** market data acquisition (OKX public endpoints) with polite rate limiting; no authenticated calls.
- Do not re-open or mutate sealed EVAL artifacts (append new timestamped artifacts only). `scripts/run_backtest.py` is not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` out of scope.

### Reuse / traps
- `load_real_orderflow`/`load_real_options_chain` raise `RealDataUnavailable` and never fall back to synthetic — keep that invariant.
- EVAL-23 showed options-only OOS Sharpe 8.76 / 591 trades but `options_signal_tradable` FAIL and `options_leg_degenerate=true` on single snapshot; do not claim GO from that without resolving tradability/time-variation/provenance with evidence.
- Orderflow-only net-of-cost Sharpe -2.338 on current tape is a measured NO-GO signal; do not hide or reframe without new data/evidence.
- Real loaders select newest matching export by filename recency; if adding multi-snapshot series, ensure loader/consumer semantics are explicit and tested.

## CAMPAIGN QUEUE

| Eval | Focus | Status |
|---|---|---|
| **EVAL-02..EVAL-22** | Sealed prior gates | **SEALED** |
| **EVAL-23B / EVAL-24A** | Export adapters | **SEALED** |
| **EVAL-25** | Real-data acquisition & falsification | **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`) |
| **EVAL-26** | Public real-data acquisition | **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T035050Z` latest) |
| **EVAL-23** | Real net-of-cost verdict | **SEALED NO-GO** (`REAL_NET_OF_COST_EVAL_23_20261114T040000Z`, 8/11) |
| **EVAL-24** | Options-leg validity | **SEALED NO-GO** (`OPTIONS_LEG_VALIDITY_24_20261114T041000Z`, 3/8, degenerate) |
| **EVAL-27** | Options time-series tradability **or** amended-fusion measured evaluation | **ACTIVE — must seal new artifact with measured GO/NO-GO** |

## FOCUS CAMPAIGN (heavy work — future agents cannot avoid this)

This campaign is the only open gate. Every session must:
1. Execute Path A (multi-snapshot real options time-series + tradability re-eval) **or** Path B (amended-fusion/orderflow-only measured eval).
2. Produce at least one new sealed artifact with measured numbers and explicit GO/NO-GO.
3. Record pass counts and artifact hashes in this handoff.
4. Update the CAMPAIGN QUEUE and INITIAL TASK MESSAGE with the next timestamp/ID.

A session that only reads, restates bottlenecks, or leaves the tree without a new sealed artifact has failed this campaign.

## HANDOFF DISCIPLINE
- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands/hashes.
- If incomplete, record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.
