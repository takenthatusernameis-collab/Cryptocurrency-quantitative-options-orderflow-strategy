# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T13:42:00Z UTC — TASK ID `INIT-2026-11-14T13:42:00Z-EVAL-34-FINAL-STRATEGY-FALSIFICATION`:** Execute **EVAL-34** now: produce exactly one new sealed measurement artifact `research_state/FINAL_STRATEGY_FALSIFICATION_34_<UTC>.{json,md}` that consolidates the entire falsification chain (EVAL-23 through EVAL-33) into a single decisive portfolio decision. **EVAL-34 COMPLETE (2026-11-14T13:54:16Z).** Artifact sealed: `FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.{json,md}`. Verdict: NO-GO — options+orderflow combined is NOT net-of-cost tradable. Portfolio decision: **DEPLOY ORDERFLOW-ONLY WITH CAVEATS** (paper-only, toxicity gate VPIN≥0.70→flat, capacity-aware sizing, continuous monitoring, kill-switches, max notional $1M, max daily loss $50k; options leg terminated as zero-alpha cost center). Orderflow-only held-out: Sharpe 4.8115, 129 trades, $157.02 cost on 466 bars. 8 tests passed. `python3 -m py_compile scripts/eval34_final_strategy_falsification.py tests/test_eval34_final_strategy_falsification.py` => OK. `python3 -m pytest -q tests/test_eval34_final_strategy_falsification.py` => **8 passed in 3.77s**. `python3 scripts/eval34_final_strategy_falsification.py` => sealed artifact written.

**INITIAL TASK MESSAGE — timestamped 2026-11-14T14:30:47Z UTC — TASK ID `INIT-2026-11-14T14:30:47Z-EVAL-35-ORDERFLOW-ONLY-SECOND-WINDOW-VALIDATION`:** Execute **EVAL-35** now: produce exactly one new sealed measurement artifact `research_state/ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_<UTC>.{json,md}` that validates the orderflow-only pillar on a **second independent real data window** (new ~6.5h OKX BTC-USD-SWAP tape, not previously used), reproducing the held-out orderflow-only result (Sharpe ~4.8115, ~129 trades, ~$157.02 cost) under paper-only net-of-cost accounting with toxicity gate VPIN≥0.70→flat and capacity-aware sizing. Seal artifact + script + targeted tests; run `py_compile`, `pytest`, and the script; record exact command outputs. This is the DEPLOY certification gate: orderflow-only must reconfirm tradable on independent real data before any deployment consideration.

**Active task:** `INIT-2026-11-14T14:30:47Z-EVAL-35-ORDERFLOW-ONLY-SECOND-WINDOW-VALIDATION` — **ACTIVE**. Prior task EVAL-34 COMPLETE (sealed `FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.{json,md}`, verdict NO-GO, decision DEPLOY_ORDERFLOW_ONLY_WITH_CAVEATS). Next: EVAL-35 seal; if GO → proceed to deployment certification / paper-only rollout per caveats; if NO-GO → final termination memo (EVAL-36).

**EVAL-33 SEALED — FALSIFICATION NO-GO (trustworthy; a full success).** `OPTIONS_LEG_FALSIFICATION_33_20261114T134105Z.{json,md}`. Per-expiry/per-component IC across 3 real snapshots (14 expiries each, 825–826 contracts/snapshot split ATM/NEAR/WING, calls vs puts): all IC = 0.0 (cross-sectional buckets; time-series IC infeasible with 3 snapshots). Options-only net-of-cost frontier on held-out bars 1087..1552 (466 bars, 9 windows): 6 variants (long/short × thresholds 0.1/0.2/0.5) — **all 6 produced 0 trades, Sharpe 0.0, cost $0.00** (options signal all-negative → flat; toxicity gate 80.5% engaged). Controls on same slice: orderflow-only Sharpe 4.8115 / 129 trades / $157.02 cost / $1.41M notional; flat 0. Combined (Rule A) Sharpe 5.0195 / 108 trades / $122.07 cost — but EVAL-32 already proved this edge indistinguishable from orderflow-only (perm p=0.2498, PBO=0.5156, bootstrap CI includes 0). Falsification verdict: **NO-GO** — no options-only variant passed (a) superiority + (b) perm p<0.05 + (c) bootstrap CI excludes 0. DSR 0.0 at all benchmarks. PBO k_folds=4 valid_combinations>0.

**Session verification (2026-11-14T13:42:00Z):** `python3 -m py_compile src/analytics/options_time_varying_signal.py src/analytics/integrated_options_orderflow_evaluation.py scripts/eval33_options_leg_falsification.py tests/test_eval33_options_leg_falsification.py` => OK. `python3 -m pytest -q tests/test_eval33_options_leg_falsification.py` => **9 passed in 103.28s** (covering: held-out split matches EVAL-32; bucket IC computation; frontier enumerates 6 variants × 9 windows; controls on same slice; falsification verdict logic; real loader raises RealDataUnavailable; statistical primitives on fixture; PBO k_folds=4 valid). `python3 scripts/eval33_options_leg_falsification.py` => sealed artifact written. Repo `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`. This file is the single durable handoff; root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers with **no task IDs**. No competing handoffs, no stale `*.lock`/`*.pid`, one active agent. `.env` absent (paper-only; must stay absent). HEAD `bb356da11`.

**Repo priority (inferred from the repository name `Cryptocurrency-quantitative-options-orderflow-strategy`):** a cryptocurrency **quantitative OPTIONS + ORDERFLOW strategy** — real options pricing/greeks/vol-surface, orderflow alpha & toxicity, gamma/delta hedging, execution/routing, and **net-of-cost evaluation**.
**Mission:** deliver the strategy and a *trustworthy*, net-of-cost measurement of its performance — not orchestrator wrappers, not favorable-looking numbers from broken harnesses. A **trustworthy NO-GO** is a full success.

## BOTTLENECKS ALREADY REMOVED (do not re-litigate, do not re-derive)

1. **EVAL-30 measurement unblocked, reproduced, and SEALED.** `n_bars=1553`, `n_snapshots=3`, span `2026-11-14T04:05:35Z→10:33:35Z`; per-snapshot signals `-0.036191, -0.051843, -0.029513`; `mean_signal=-0.008405`, `distinct_signal_values=3`, `step_changes=2`, `n_flat_bars=1300`, `ic_present=True`. **IC: 1d=-0.003069 (t=-0.121), 5d=-0.006377 (t=-0.251), 20d=+0.000575 (t=+0.023); `ic_mean=-0.002957`.**
2. **Bootstrap/permutation/PBO verified importable.** `block_bootstrap_ci`, `permutation_test` in `src.analytics.strategy_evaluation`; `_cscv_pbo`, `_benjamini_hochberg` in `src.analytics.real_walkforward_certification`; `_deflated_sharpe` in `src.analytics.strategy_falsification`.
3. **Data present.** 3 real option snapshots (`data/raw/options_okx_BTC_20261114T093032Z.json`, `...093120Z.json`, `...103323Z.json`) and `data/raw/orderflow_okx_BTC-USD-SWAP.json` (50,900 trades). Real loaders raise `RealDataUnavailable` — never fall back to synthetic.
4. **EVAL-30 adapter sealed.** `src/analytics/options_time_varying_signal.py`: `snapshot_options_signal`, `load_snapshot_signals`, `align_options_signal_to_bars` (causal step, bar `i` uses newest snapshot `<= bar_end[i]`, pre-first = 0.0), `measure_time_varying_signal`, `build_eval30_report`, `write_eval30_artifact`.
5. **Root cause of prior NO-GO recorded (do NOT re-fix):** `integrated_options_orderflow_evaluation.py::_causal_options_signal_series` broadcasts a single static options value to every bar → zero time-variation → mean IC 0.0. Do **not** modify that sealed function.
6. **EVAL-31 SEALED GO (marginal).** `AMENDED_FUSION_EVAL_31_20261114T114328Z.{json,md}` — Rule A fusion (options sign regime filter + orderflow direction, toxicity gate ≥0.7→flat), causal. Combined OOS Sharpe 0.3016 (full series), perm p=0.768, PBO combined=0.75. Requires OOS validation before deployment.
7. **EVAL-32 SEALED NO-GO (trustworthy).** `EVAL_32_OOS_VALIDATION_20261114T124437Z.{json,md}` — EVAL-31 marginal GO does not survive held-out validation (only 1/4 criteria passed). The combined edge is not distinguishable from the orderflow-only pillar (perm p=0.2498, PBO combined 0.5156, bootstrap CI includes 0). **The options leg added no measurable net-of-cost value over orderflow-only.**
8. **EVAL-33 SEALED NO-GO (falsification).** `OPTIONS_LEG_FALSIFICATION_33_20261114T134105Z.{json,md}` — Exhaustive options-leg falsification: per-expiry/per-component IC (all 0.0 cross-sectional), full options-only net-of-cost frontier (6 variants, all 0 trades/0 Sharpe/$0 cost). Orderflow-only is the only non-degenerate pillar. **The options leg cannot carry positive net-of-cost alpha on the available real data.**

## ACTIVE BOTTLENECK — NONE (all removed)

EVAL-34 sealed and verified complete (8 tests passed, script OK, artifact `FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.{json,md}`). Verdict: NO-GO — options+orderflow combined is NOT net-of-cost tradable. Portfolio decision: **DEPLOY ORDERFLOW-ONLY WITH CAVEATS**; options leg terminated as zero-alpha cost center. No `*.lock`/`*.pid`, `.env` absent (paper-only, must stay absent), real loaders raise `RealDataUnavailable` (never synthetic), data present (3 option snapshots + 50.9k SWAP trades), EVAL-34 script/tests verified. The only active work is **EVAL-35** (second independent real data window validation of orderflow-only; seal artifact). Bottlenecks already removed: EVAL-30 measurement unblocked/reproduced/sealed; bootstrap/permutation/PBO verified importable; data present; EVAL-30 adapter sealed; prior NO-GO root cause recorded (do not re-fix). Do not re-litigate sealed EVALs.

## VERIFIED STATE (ground truth; re-verify only if an import fails)

- **Sealed:** EVAL-02..EVAL-22; EVAL-23B/EVAL-24A adapters. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T103323Z`).
- **EVAL-23 SEALED NO-GO:** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z` — combined IC mean -0.016776 (|t|=4.1008, p=0.0020 adverse); `options_leg_degenerate=true`.
- **EVAL-24 SEALED NO-GO:** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z` — parity-consistent but `options_leg_tradable` FAIL; venue IV/greeks/OI coverage 0%.
- **EVAL-27 SEALED NO-GO:** `OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z`, `AMENDED_FUSION_EVAL_27_20261114T065033Z`.
- **EVAL-28 SEALED GO (additive):** `OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z` / `...093132Z` — per-expiry forward-calibrated put-call parity 1017/1017 pairs (100%), min R²=0.999919.
- **EVAL-29 SEALED NO-GO:** `OPTIONS_LEG_TRADABILITY_29_20261114T093151Z`.
- **EVAL-30 SEALED NO-GO:** `OPTIONS_LEG_TRADABILITY_30_20261114T113051395ZZ.{json,md}`.
- **EVAL-31 SEALED GO (marginal):** `AMENDED_FUSION_EVAL_31_20261114T114328Z.{json,md}`.
- **EVAL-32 SEALED NO-GO (validation):** `EVAL_32_OOS_VALIDATION_20261114T124437Z.{json,md}` — EVAL-31 GO fails held-out validation (1/4 criteria).
- **EVAL-33 SEALED NO-GO (falsification):** `OPTIONS_LEG_FALSIFICATION_33_20261114T134105Z.{json,md}` — options leg carries zero net-of-cost alpha; all 6 variants flat; orderflow-only is the only non-degenerate control.
- **EVAL-34 SEALED NO-GO + DECISION:** `FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.{json,md}` — consolidated evidence table EVAL-23..33 (7 NO-GO, 2 GO additive/marginal invalidated); options+orderflow combined NOT net-of-cost tradable; portfolio decision: **DEPLOY ORDERFLOW-ONLY WITH CAVEATS**. Orderflow-only held-out: Sharpe 4.8115, 129 trades, $157.02 cost on 466 bars. Options leg terminated as zero-alpha cost center. 8 tests passed.

## EXECUTE NOW — `INIT-2026-11-14T14:30:47Z-EVAL-35-ORDERFLOW-ONLY-SECOND-WINDOW-VALIDATION`

### Step 0 — Bootstrap (only if an import below fails)
`pip3 install -r requirements.txt`. Do **not** re-acquire data unless the new 6.5h window is unavailable. Real loaders must raise `RealDataUnavailable`, never fall back to synthetic. `.env` absent (paper-only, must stay absent); `LIVE_TRADING_ENABLED=false`.

### Step 1 — Acquire second independent real data window
Obtain a new ~6.5h OKX BTC-USD-SWAP orderflow tape not previously used in EVAL-23..34 (different time span from `2026-11-14T04:05:35Z→10:33:35Z`). If acquisition is blocked, seal a measured blocker artifact reporting the exact command that failed; do not fabricate or relabel synthetic data as real. Never emit `{"valid": true}`.

### Step 2 — Replicate orderflow-only net-of-cost result
Run the orderflow-only pipeline on the new window with toxicity gate VPIN≥0.70→flat and capacity-aware sizing (spread 2bps, impact 0.01, max participation 12.5%, cost budget 0.5bps). Record measured: Sharpe, trades, cost, notional, max DD, kill-switch triggers. Success criterion: orderflow-only non-degenerate (Sharpe > 1.0, trades > 0, cost > 0) and within the EVAL-34 held-out band (Sharpe ~4.8115, ~129 trades, ~$157 cost).

### Step 3 — Portfolio certification decision
Choose **one** and justify with measured numbers:
- **CERTIFY DEPLOY (paper-only)**: second window confirms orderflow-only tradable; proceed to paper-only rollout per EVAL-34 caveats (toxicity gate, capacity-aware sizing, continuous net-of-cost monitoring, kill-switches DD 20% / toxicity 80% / cost 5bps, max notional $1M, max daily loss $50k).
- **TERMINATE / NO-GO**: second window fails to replicate (Sharpe ≤ 1.0, 0 trades, or adverse IC); options+orderflow remains NOT net-of-cost tradable; issue final termination memo (EVAL-36) with lessons learned and infrastructure disposal; no further queue.

### Step 4 — Seal artifact + targeted tests (mandatory)
Write `research_state/ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_<UTC>.{json,md}` with: `report_id`, timestamps, window span, provenance/caveats (`authenticity_verified=false`; no signed venue attestation), measured metrics (Sharpe, trades, cost, notional, max DD, kill-switch triggers), toxicity-gate engagement, success/fail vs EVAL-34 band, portfolio certification decision with rationale, exact commands, pytest results.

Add `scripts/eval35_orderflow_only_second_window_validation.py` and `tests/test_eval35_orderflow_only_second_window_validation.py` covering at minimum: (a) loads the new real window via real loader (raises `RealDataUnavailable`, never synthetic); (b) computes orderflow-only Sharpe/trades/cost under toxicity gate; (c) asserts non-degenerate (Sharpe > 1.0, trades > 0, cost > 0) or explicitly records NO-GO; (d) artifact is valid JSON/MD with strict serialization; (e) decision is one of the two pre-declared options with measured justification.

Record and run:
```
python3 -m py_compile scripts/eval35_orderflow_only_second_window_validation.py tests/test_eval35_orderflow_only_second_window_validation.py
python3 -m pytest -q tests/test_eval35_orderflow_only_second_window_validation.py
python3 scripts/eval35_orderflow_only_second_window_validation.py
```

### Step 5 — Update this handoff in place (same file only)
Replace stale state with measured numbers, sealed artifact paths, pytest counts, a **new TASK ID/timestamp**, and the next active task (EVAL-36 only after EVAL-35 seals: deployment certification / paper-only rollout if GO; final termination memo if NO-GO). No competing handoff files. No timestamped handoff copies.

## NEXT-FOCUS CAMPAIGN (heavy work — future agents must not avoid it)

The strategic objective is to determine, with real data and net-of-cost accounting, whether a **tradable** cryptocurrency options+orderflow strategy exists. Every execution session must advance the queue by at least one sealed measurement artifact (or explicitly seal a measured blocker with the exact command that failed). Handoff-only, tests-only-without-sealing, discovery-only, and "re-read the logs" sessions are non-progress. A NO-GO artifact that correctly reports why the strategy is not tradable is a full success; a GO without a verifying sealed artifact is a failure.

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
| EVAL-29 | Options-leg tradability (calibrated forwards) | — | **SEALED NO-GO** |
| EVAL-30 | Time-varying options signal + net-of-cost verdict | **Reproduce IC, walk-forward, seal artifact, ship tests** | **SEALED NO-GO** (`OPTIONS_LEG_TRADABILITY_30_20261114T113051395ZZ`) |
| EVAL-31 | Fuse time-varying options + causal orderflow; re-test superiority | **Must seal measured artifact; re-labeling sealed EVALs forbidden** | **SEALED GO (marginal)** (`AMENDED_FUSION_EVAL_31_20261114T114328Z`) |
| EVAL-32 | Rigorous OOS validation of EVAL-31 GO on held-out last 30% | **Must seal measured artifact; pre-declared criteria; PBO valid_combinations>0** | **SEALED NO-GO (validation)** (`EVAL_32_OOS_VALIDATION_20261114T124437Z`) |
| EVAL-33 | Exhaustive options-leg falsification: per-expiry/per-component IC + full options-only net-of-cost frontier on held-out slice; pre-declared GO/NO-GO; seal artifact + tests | **Must seal a measured artifact; whole frontier, no cherry-pick; no new data** | **SEALED NO-GO (falsification)** (`OPTIONS_LEG_FALSIFICATION_33_20261114T134105Z`) |
| **EVAL-34** | **Final consolidated strategy falsification + portfolio decision (deploy orderflow-only w/ caveats OR terminate)** | **Seal artifact; no new data required; consolidate EVAL-23..33** | **SEALED — COMPLETE** (`FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.{json,md}`; verdict NO-GO; decision DEPLOY_ORDERFLOW_ONLY_WITH_CAVEATS; 8 tests passed) |
| **EVAL-35** | **Second independent real data window validation of orderflow-only; seal artifact; DEPLOY certification gate** | **Acquire new ~6.5h window; replicate orderflow-only (Sharpe ~4.8115, ~129 trades, ~$157 cost) under toxicity gate + capacity-aware sizing; seal artifact + script + tests; record exact command outputs** | **ACTIVE** (`INIT-2026-11-14T14:30:47Z-EVAL-35-ORDERFLOW-ONLY-SECOND-WINDOW-VALIDATION`) |
| EVAL-36 | Deployment certification / paper-only rollout (if EVAL-35 GO) OR final termination memo (if EVAL-35 NO-GO) | **Seal measured artifact; paper-only; kill-switches DD 20% / toxicity 80% / cost 5bps; max notional $1M, max daily loss $50k** | QUEUED (contingent on EVAL-35) |

## HARD CONSTRAINTS / INVARIANTS

- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- Network only for public read-only market data acquisition with polite rate limiting if truly required (not expected — data present).
- Do not mutate sealed artifacts; append new timestamped artifacts only. `scripts/run_backtest.py` is not evidence of edge.
- `next9_unblocked=false`; `research_state/NEXT9_APPROVAL_VALIDATION_*.json` out of scope.
- Reuse existing modules: `src/analytics/options_time_varying_signal.py`, `src/analytics/integrated_options_orderflow_evaluation.py`, `src/analytics/real_net_of_cost_evaluation.py`, `src/analytics/capacity_aware_tca.py`, `src/analytics/strategy_evaluation.py`, `src/analytics/real_walkforward_certification.py`, `src/analytics/strategy_falsification.py`, `src/campaign/integrated.py`, `src/data/{public_export_acquisition,loader,schemas,options_exports,options_timeseries}.py`, `src/features/*`, `src/backtest/engine.py`.
- Real loaders must raise `RealDataUnavailable` and never fall back to synthetic. Never relabel synthetic as real. Never emit `{"valid": true}`.
- Prohibited: discovery runs, re-litigating sealed EVALs, enumerating `research_state/` broadly, full test suite runs (~5k), modifying `.github/workflows/main.yml`, creating `phaseNN_*_post_attribution_seal_orchestrator` wrappers, handoff-only execution sessions.

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands. No timestamped handoff copies.
- Record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.