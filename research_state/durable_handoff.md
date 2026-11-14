# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T12:45:20Z UTC — TASK ID `INIT-2026-11-14T12:45:20Z-EVAL-33-OPTIONS-LEG-FALSIFICATION`:** Execute **EVAL-33** now: produce exactly one new sealed measurement artifact `research_state/OPTIONS_LEG_FALSIFICATION_33_<UTC>.{json,md}` that exhaustively falsifies (or, if contrary evidence appears, partially rehabilitates) the **options leg** of the strategy on the existing real data, with **no new data required**. Pre-declared heavy-work scope: (1) per-expiry and per-component IC for the options signal across all 3 real snapshots (calls, puts, moneyness buckets, ATM |Δ| buckets), reported with t-stats and sign; (2) a **net-of-cost frontier**: for each options-only variant (long/short by sign, threshold sweeps, per-moneyness filters) report the walk-forward OOS Sharpe, trades, and total cost USD, and compare against orderflow-only and flat controls on the held-out slice; (3) an explicit statement of whether the options leg can carry positive alpha net of cost on this data, with a sealed `GO`/`NO-GO` verdict. This is mandatory heavy work, not discovery. Do **not** re-litigate sealed EVALs, do **not** edit sealed artifacts, do **not** fabricate a GO, do **not** relabel synthetic data as real, and do **not** end the execution session with handoff-only, tests-only, or "re-read the logs" edits. **A trustworthy NO-GO (falsification) artifact is a full success. No new sealed measurement artifact = FAILED session.**

**Active task:** `INIT-2026-11-14T12:45:20Z-EVAL-33-OPTIONS-LEG-FALSIFICATION` (mandatory heavy work).

**EVAL-32 SEALED — VALIDATION NO-GO (trustworthy; a full success).** `EVAL_32_OOS_VALIDATION_20261114T124437Z.{json,md}`. Strictly held-out last 30% (bars `1087..1552`, 466 bars, `2026-11-14T08:37:20.690Z`→`2026-11-14T10:33:35.690Z`), 9 walk-forward windows per config, pre-declared 4-way walk-forward + permutation + block-bootstrap CI + DSR + PBO(`k_folds=4`) + BH-FDR. Measured: **combined OOS Sharpe 5.0195 vs best control orderflow-only 4.8115 (trades 108)** — but **only 1 of 4 pre-declared criteria passed** (criterion a: superiority+trades PASS; b: permutation p=0.2498 ≥0.05 FAIL; c: bootstrap 95% CI [-6.82, 13.64] includes 0 FAIL; d: PBO combined=0.5156 > 0.5 with valid_combos=4 FAIL). Combined held-out: return +29.30%, maxDD 17.58%, 108 trades, cost $122.07, notional $1.09M. Options-only 0 trades (all-negative signal → flat); orderflow-only Sharpe 4.8115/129 trades/$157.02; flat 0. **Verdict: NO-GO** — the EVAL-31 marginal GO does NOT survive rigorous OOS validation; the edge is indistinguishable from the orderflow-only pillar. DSR 0.0 at all benchmarks (0.0/0.5/1.0).

**Session verification (2026-11-14T12:45:20Z):** `python3 -m py_compile src/analytics/options_time_varying_signal.py scripts/eval31_amended_fusion.py scripts/eval32_oos_validation.py tests/test_eval32_oos_validation.py` => OK. `python3 -m pytest -q tests/test_eval32_oos_validation.py` => **7 passed in 67.33s** (covering: chronological split / no future in train; full-series Rule A positions sliced == manual held-out recomputation; 9 windows + required keys on held-out; statistical primitives execute on deterministic fixture; PBO `k_folds=8` rejected when `valid_combinations==0` while `k_folds=4` valid; pre-declared criteria correctly evaluated; `run_eval32(write=False)` verdict == all-4-criteria). Repo `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`. This file is the single durable handoff; root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers with **no task IDs**. No competing handoffs, no stale `*.lock`/`*.pid`, one active agent. `.env` absent (paper-only; must stay absent). HEAD `bb356da11`.

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

## ACTIVE BOTTLENECK (the only one left; shipping the EVAL-33 artifact removes it)

EVAL-32 NO-GO means the options leg is unproven. The strategic question is now binary: **can the options leg carry any positive net-of-cost alpha on the available real data, ever?** EVAL-33 answers it exhaustively by falsification (per-expiry/per-component IC + a full options-only net-of-cost frontier on the held-out slice). If the answer is NO-GO, that is a trustworthy, decisive result. Do not stop at EVAL-31's single config — enumerate the frontier.

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

## EXECUTE NOW — `INIT-2026-11-14T12:45:20Z-EVAL-33-OPTIONS-LEG-FALSIFICATION`

### Step 0 — Bootstrap (only if an import below fails)
`pip3 install -r requirements.txt`. Do **not** re-acquire data (snapshots + orderflow present). Real loaders must raise `RealDataUnavailable`, never fall back to synthetic.

### Step 1 — Per-expiry / per-component IC (falsification of the options leg)
Load the 3 real snapshots via `load_snapshot_signals("BTC")` and `_build_bars(load_real_orderflow("BTC"))`. For **each** snapshot, split its chain by expiry and by moneyness bucket (e.g., |log(K/F)| < 0.02 ATM, 0.02–0.05 near, > 0.05 wing) and by component (calls vs puts). For each bucket compute the options-signal IC at horizons `HORIZONS=(1,5,20)` bars (reuse the sealed IC helper in `src/analytics/options_time_varying_signal.py` / `compute_alpha_metrics` in `integrated_options_orderflow_evaluation.py`) with t-stats and sign. Record counts, coverage (fraction of contracts with IV/greeks/OI), and whether **any** bucket shows a stable, correctly-signed IC. State explicitly whether the leg is falsified.

### Step 2 — Options-only net-of-cost frontier (held-out slice)
On the held-out bars `1087..1552` (compute full-series causal positions then slice, as in EVAL-32), sweep a **pre-declared** grid of options-only variants: direction = {long-by-signal, short-by-signal}; threshold ∈ {0.1 (default), 0.2, 0.5}; optional per-moneyness / per-expiry filters derived only from the 3 snapshots. For each variant run `_run_walkforward` (same `CapacityAwareSizer` + `IntegratedConfig(seed=42, ...)`, `max_position_pct=DEFAULT_MAX_POSITION_PCT`, seed 42) and record OOS Sharpe, trades, total cost USD, notional, and toxicity-gate engagement. Compare every variant against **orderflow-only** and **flat** controls on the same slice. The frontier must report `num_windows == 9` per variant.

### Step 3 — Verdict + statistical defensibility
Compute the frontier best options-only Sharpe and its permutation p vs orderflow-only and vs flat (paired, 1000 perms, seed=42), and a block-bootstrap CI (block size 2, 1000 resamples). Pre-declared **falsification verdict**: `NO-GO` (options leg cannot carry alpha) unless **any** variant achieves (a) OOS Sharpe > max(orderflow-only, flat) **and** (b) permutation p < 0.05 vs that control **and** (c) bootstrap 95% CI excludes 0. Record every variant's metrics. Do not cherry-pick a single favorable threshold — report the whole frontier.

### Step 4 — Seal artifact + targeted tests (mandatory)
Write `research_state/OPTIONS_LEG_FALSIFICATION_33_<UTC>.{json,md}` with: `report_id`, timestamps, provenance/caveats (`authenticity_verified=false`; no signed venue attestation; inverse BTC-USD-SWAP tape vs spot option snapshots), the split, per-bucket IC table, the full options-only frontier table (every variant), statistical tests, exact commands, pytest results, and an explicit `GO`/`NO-GO` verdict with rationale referencing the pre-declared criteria.

Add `scripts/eval33_options_leg_falsification.py` and `tests/test_eval33_options_leg_falsification.py` covering at minimum: (a) per-bucket IC computation runs and returns finite t-stats on a deterministic fixture; (b) the frontier enumerates >1 variant and every variant runs the walk-forward with `num_windows==9`; (c) controls (orderflow-only, flat) are computed on the same held-out slice; (d) the falsification verdict logic is correct (NO-GO unless all three sub-criteria met for some variant); (e) real loader raises `RealDataUnavailable` rather than silently using synthetic when a snapshot is missing (fixture-level).

Record and run:
```
python3 -m py_compile src/analytics/options_time_varying_signal.py src/analytics/integrated_options_orderflow_evaluation.py scripts/eval33_options_leg_falsification.py tests/test_eval33_options_leg_falsification.py
python3 -m pytest -q tests/test_eval33_options_leg_falsification.py
python3 scripts/eval33_options_leg_falsification.py
```

### Step 5 — Update this handoff in place (same file only)
Replace stale state with measured numbers, sealed artifact paths, pytest counts, a **new TASK ID/timestamp**, and the next active task: if EVAL-33 seals **NO-GO** (expected), define **EVAL-34: Final Strategy Falsification / Portfolio Decision** — seal a single consolidated falsification artifact proving the options+orderflow strategy is not net-of-cost tradable on the available real data, with the orderflow-only pillar as the only non-degenerate control, and a clear recommendation (deploy orderflow-only with caveats, or terminate). If EVAL-33 seals a (surprising) **GO**, define **EVAL-34: Live Paper Trading Shadow Execution** (deploy the validated variant ≥48h with real-time ingestion, routing sim, continuous net-of-cost monitoring; seal artifact with live P&L/fills/slippage/ops metrics). No competing handoff files.

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
| **EVAL-33** | **Exhaustive options-leg falsification: per-expiry/per-component IC + full options-only net-of-cost frontier on held-out slice; pre-declared GO/NO-GO; seal artifact + tests** | **Must seal a measured artifact; whole frontier, no cherry-pick; no new data** | **ACTIVE — execute now** |
| EVAL-34 | If EVAL-33 NO-GO: final consolidated strategy falsification + portfolio decision (deploy orderflow-only w/ caveats OR terminate). If EVAL-33 GO: live paper shadow execution ≥48h | **Seal artifact; no new data required (falsification) OR live paper deployment** | QUEUED (contingent) |
| EVAL-35+ | Continue queue only after EVAL-34 seals: second independent real window / deployment certification or final termination memo | **Each session seals one new measured artifact; no orchestrator wrappers; no synthetic relabeling** | QUEUED |

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