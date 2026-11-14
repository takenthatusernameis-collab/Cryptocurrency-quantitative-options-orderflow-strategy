# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T13:42:00Z UTC — TASK ID `INIT-2026-11-14T13:42:00Z-EVAL-34-FINAL-STRATEGY-FALSIFICATION`:** Execute **EVAL-34** now: produce exactly one new sealed measurement artifact `research_state/FINAL_STRATEGY_FALSIFICATION_34_<UTC>.{json,md}` that consolidates the entire falsification chain (EVAL-23 through EVAL-33) into a single decisive portfolio decision. EVAL-33 sealed **NO-GO** (trustworthy falsification): the options leg carries **zero net-of-cost alpha** on the available real data — all 6 options-only variants produced 0 trades, 0 Sharpe, 0 cost. The orderflow-only pillar is the only non-degenerate control (Sharpe 4.8115, 129 trades, $157.02 cost on held-out 466 bars). Pre-declared scope: (1) consolidated evidence table citing every sealed NO-GO from EVAL-23 through EVAL-33 with measured numbers; (2) explicit statement that the **options+orderflow strategy is not net-of-cost tradable** on this data; (3) portfolio decision: **deploy orderflow-only with caveats** (paper-only, toxicity gate, capacity-aware sizing, continuous monitoring) OR **terminate** (if risk/complexity exceeds value). This is mandatory heavy work, not discovery. A trustworthy consolidated NO-GO + decision artifact is a full success. No new sealed measurement artifact = FAILED session.

**Active task:** `INIT-2026-11-14T13:42:00Z-EVAL-34-FINAL-STRATEGY-FALSIFICATION` (mandatory heavy work).

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

## ACTIVE BOTTLENECK (the only one left; shipping the EVAL-34 artifact removes it)

EVAL-33 NO-GO is decisive: the options leg is falsified. The final strategic question is binary: **what is the portfolio decision?** EVAL-34 consolidates the entire falsification chain (EVAL-23 through EVAL-33) into a single artifact with a clear recommendation: deploy orderflow-only with caveats (paper-only, toxicity gate, capacity-aware sizing, continuous monitoring) OR terminate. This is the final measurement artifact for this data window.

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

## EXECUTE NOW — `INIT-2026-11-14T13:42:00Z-EVAL-34-FINAL-STRATEGY-FALSIFICATION`

### Step 0 — Bootstrap (only if an import below fails)
`pip3 install -r requirements.txt`. Do **not** re-acquire data (snapshots + orderflow present). Real loaders must raise `RealDataUnavailable`, never fall back to synthetic.

### Step 1 — Consolidate falsification evidence
Load all sealed artifacts EVAL-23 through EVAL-33. Build a consolidated evidence table with measured numbers from each: IC, Sharpe, trades, cost, verdict, key reason. No new computation — only aggregation of sealed facts.

### Step 2 — Final strategy falsification statement
Explicitly state: the **options+orderflow combined strategy is not net-of-cost tradable** on the available real data (BTC, OKX, 3 option snapshots spanning ~6.5h, 50.9k SWAP trades, 1553 bars, held-out 466 bars). Evidence: (a) EVAL-23 combined IC adverse; (b) EVAL-24 options leg not tradable; (c) EVAL-27 time-series ingestion NO-GO; (d) EVAL-29 tradability NO-GO; (e) EVAL-30 time-varying signal NO-GO (IC -0.002957); (f) EVAL-31 marginal GO (combined Sharpe 0.3016) but EVAL-32 validation NO-GO (1/4 criteria); (g) EVAL-33 exhaustive falsification NO-GO (options-only frontier all flat, orderflow-only Sharpe 4.8115). The combined edge in EVAL-32 (Sharpe 5.0195) is entirely attributable to the orderflow pillar.

### Step 3 — Portfolio decision
Choose **one** and justify with measured numbers:
- **DEPLOY ORDERFLOW-ONLY WITH CAVEATS**: paper-only; toxicity gate (VPIN ≥0.7 → flat); capacity-aware sizing (spread 2bps, impact 0.01, max participation 12.5%, cost budget 0.5bps); continuous net-of-cost monitoring; kill-switch (DD 20%, toxicity 80%, cost 5bps); max notional $1M; max daily loss $50k. Rationale: orderflow-only Sharpe 4.8115 on held-out, 129 trades, $157 cost, non-degenerate, measurable.
- **TERMINATE**: if risk/complexity of maintaining the options infrastructure exceeds the marginal value of the orderflow-only pillar. Rationale: options leg is a proven cost center with zero alpha; maintaining parity calibration, IV surface, greeks, OI ingestion for zero return is negative EV.

### Step 4 — Seal artifact + targeted tests (mandatory)
Write `research_state/FINAL_STRATEGY_FALSIFICATION_34_<UTC>.{json,md}` with: `report_id`, timestamps, provenance/caveats (`authenticity_verified=false`; no signed venue attestation; inverse BTC-USD-SWAP tape vs spot option snapshots), consolidated evidence table (EVAL-23..33), final falsification statement, portfolio decision with rationale, exact commands, pytest results.

Add `scripts/eval34_final_strategy_falsification.py` and `tests/test_eval34_final_strategy_falsification.py` covering at minimum: (a) consolidated table loads all sealed artifacts and extracts correct numbers; (b) final statement references every sealed NO-GO; (c) portfolio decision is one of the two pre-declared options with measured justification; (d) artifact is valid JSON/MD with strict serialization.

Record and run:
```
python3 -m py_compile src/analytics/options_time_varying_signal.py src/analytics/integrated_options_orderflow_evaluation.py scripts/eval34_final_strategy_falsification.py tests/test_eval34_final_strategy_falsification.py
python3 -m pytest -q tests/test_eval34_final_strategy_falsification.py
python3 scripts/eval34_final_strategy_falsification.py
```

### Step 5 — Update this handoff in place (same file only)
Replace stale state with measured numbers, sealed artifact paths, pytest counts, a **new TASK ID/timestamp**, and the next active task: **EVAL-35+ only after EVAL-34 seals** — if decision is DEPLOY, define EVAL-35: Second independent real data window validation (acquire new 6.5h window, replicate orderflow-only results, seal artifact); if decision is TERMINATE, define EVAL-35: Final termination memo (consolidated lessons learned, infrastructure disposal, no further queue). No competing handoff files.

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
| **EVAL-34** | **Final consolidated strategy falsification + portfolio decision (deploy orderflow-only w/ caveats OR terminate)** | **Seal artifact; no new data required; consolidate EVAL-23..33** | **ACTIVE — execute now** |
| EVAL-35+ | Continue queue only after EVAL-34 seals: second independent real window / deployment certification or final termination memo | **Each session seals one new measured artifact; no orchestrator wrappers; no synthetic relabeling** | QUEUED (contingent) |

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