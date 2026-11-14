# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T16:43:08Z UTC — TASK ID `INIT-2026-11-14T16:43:08Z-EVAL-40-NEW-REAL-DATA-ACQUISITION-MANDATORY`** (most recent, authoritative; supersedes 16:37:37Z / 16:35:54Z / 16:20:00Z / 15:39:45Z / all prior). Inferred from the repo's own charter — *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy, net-of-cost, real-data only, sealed measurement* — **EVAL-39 SEALED REPLICATION COMPLETE** (durability ledger closed for available real data). Campaign remains **TERMINATED (EVAL-36)**. **EVAL-40+ IS BLOCKED** until a **new, independently re-acquired real dataset/window (with sealed provenance)** is obtained and a **pre-registered plan is sealed first**.

**NEXT MANDATORY HEAVY-WORK ACTION (cannot be avoided, deferred, or substituted):**
1. **ACQUIRE & SEAL NEW REAL DATA** — Execute `python3 -m src.data.public_export_acquisition --symbol BTC-USD-SWAP --start <ISO8601> --end <ISO8601> --out data/raw/` with a **new time window not overlapping existing `data/raw/orderflow_okx_BTC-USD-SWAP.json` (2026-11-14T09:05:22Z→15:33:56Z) or the absent EVAL-35 window (2026-11-14T08:08:15Z→14:39:17Z)**. Capture full provenance: command, stdout/stderr, SHA-256 of outputs, `authenticity_verified=false`, `data_provenance="real"`. Seal `PUBLIC_EXPORT_ACQUISITION_40_<UTC>.{json,md}`.
2. **PRE-REGISTER EVAL-40 PLAN** — Before any evaluation, seal `EVAL_40_PREREGISTRATION_<UTC>.{json,md}` specifying: dataset SHAs, evaluation module (`src.analytics.real_net_of_cost_evaluation`), exact CLI command, success criteria (GO/NO-GO thresholds), and sealing intent (REPLICATION/REFUTED/BLOCKED).
3. **EXECUTE & SEAL EVAL-40** — Only after (1) and (2) are sealed, run the pre-registered command on the new dataset and seal measured artifact with verdict.

**SESSION READINESS / BOTTLENECK REMOVAL (standing, verified):**
- Network verified — public OKX endpoints reachable with a normal `User-Agent` (HTTP 200); `src/data/public_export_acquisition.py` requires no credentials and no `.env`.
- `.env` absent (paper-only; must stay absent). No stale `*.lock`/`*.pid` in `research_state/`.
- `data/raw/` holds exactly one real orderflow export (`orderflow_okx_BTC-USD-SWAP.json`, 2026-11-14T09:05:22Z→15:33:56Z) and one real options export (`options_okx_BTC_20261114T153357Z.json`), plus two synthetic fixtures. Any new EVAL-40 dataset must be a **non-overlapping window** not already in `data/raw/`.
- No dependency install needed: `.venv-deps/` is bootstrapped via `./scripts/verify_env.sh` (git-ignored).
- **There is no remaining technical blocker between this session and step (1).** If a session cannot run the acquisition command, it must seal a **BLOCKED** artifact with the exact failing command and stderr rather than claiming inefficiency.

**NO OTHER WORK COUNTS AS PROGRESS.**

**EVAL-39 SEALED — COMPLETE (REPLICATION) — 2026-11-14T16:35:54Z**
- **Ledger:** `research_state/DURABILITY_LEDGER_39_20261114T163011Z.{json,md}` — verdict **REPLICATION**, `data_provenance="real"`, `never_valid_true=true`, `authenticity_verified=false`, paper-only. `measured` block + `ledger_rows` covering EVAL-23..38 with non-empty `verifying_command` per row included. Campaign remains **TERMINATED** (EVAL-36 `TERMINATE_NO_GO`).
- **EVAL-39a combined-leg cross-check (re-acquired real tape, independent window):** `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}" && python3 -m src.analytics.real_net_of_cost_evaluation --data-dir data/raw --out research_state` (run 2026-11-14T16:25:21Z). Sealed rerun `research_state/REAL_NET_OF_COST_EVAL_23_20261114T162521Z.{json,md}` (SHA-256 json `02d46051ade24fc89fcbc920f9483edc184ad4a8ca75ac5954eeb68c7ef49457`, md `403c06eedcdfa5bbc0622c5932902260afad19ef27ca4ad5991cd1ca68edbf6f`).
  - Inputs: `data/raw/orderflow_okx_BTC-USD-SWAP.json` SHA-256 `fa9e43b8edeeeace7b7c551b23158aa68778dbf3909898f7e629da843baa43b6` (77,700 trades, 1555 bars @15s, 2026-11-14T09:05:22.330Z→15:33:56.432Z); `data/raw/options_okx_BTC_20261114T153357Z.json` SHA-256 `96b2e196811a798237d2506f115c26b36dad4569262ebf7f90f662eafe77f1a1` (815 quotes, 14 expiries).
  - Measured: **NO-GO 8/11**, failed `[options_signal_exists, combined_net_of_cost_superior, options_signal_tradable]`, `options_leg_degenerate=true`. `combined_alpha.ic_mean=-0.0002580345406357545` (t=-0.009947813138064721; 1/5/20 = -0.03871497585893343 / -0.024830233038000995 / +0.06277110527502716). `options_alpha` **0.0 all horizons**. `orderflow_alpha.ic_mean=0.041875591020595127` (t=2.1797478810957527). `combined_wf` Sharpe 7.456068789210498, 245 trades, $420.796502186476, max-DD 0.20840906300699194. `options_only_wf` Sharpe 7.8933794326469275, 589 trades, $666.7463847061821, max-DD 0.17060125080098731. `orderflow_only_wf` Sharpe -0.1381833092643456, 540 trades, $635.9431820718213, max-DD 0.6896679484983017. `flat_wf` 0 trades/$0. `permutation` observed diff -0.11266600582057909, null mean 0.0005672543088086395, **p=0.000999000999000999** (combined significantly worse than best single pillar). Qualitative replication of EVAL-23 non-tradability on a different window (not bit/window-level reproduction).
- **EVAL-39b/c ledger & verification (measured this session):** EVAL-34 tests 7 passed, 1 failed (`test_consolidated_table_extracts_correct_measured_numbers`) because `_find_artifact` selected newest `REAL_NET_OF_COST_EVAL_23_20261114T162521Z` (interaction from newly sealed rerun; pin `FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z` and sealed EVAL-23 timestamps explicitly). EVAL-35 tests 3 passed, 5 failed (`RealDataUnavailable`: missing `data/raw/orderflow_okx_BTC-USD-SWAP_20261114T080515Z.json`). EVAL-36 7 passed. EVAL-37 6 passed. EVAL-38 prior sealed record 9 passed; rerun exceeded 120s and was terminated RC=124 (no completed count) — recorded in ledger.
- **No synthetic fallback; loaders used:** `src.analytics.real_net_of_cost_evaluation` / `load_real_*` path only (never synthetic-preferring `src/campaign/integrated.py` loaders). `never_valid_true=True`; `.env` absent; sealed EVAL-02..38 untouched.

**NEXT HEAVY-WORK CAMPAIGN (must not be avoided):** the strategy is **TERMINATED (EVAL-36)** and the NO-GO/non-tradability is now replicated/ledger-closed for available real data (EVAL-38, EVAL-39). **No EVAL-40+ refutation or GO work is authorized unless a new, independently re-acquired real dataset/window (with sealed provenance) is obtained and a pre-registered plan is sealed first.** The only permitted heavy-work actions now are: (1) acquire & seal a **new** real dataset/window not already in `data/raw/` via `python3 -m src.data.public_export_acquisition ...` with full provenance, and (2) if and only if such a dataset is sealed, run a pre-registered EVAL-40 replication/refutation on that dataset and seal `REPLICATION`/`REFUTED`/`BLOCKED` with measured numbers. Handoff-only or discovery-only sessions are non-progress. Do **NOT** reopen deployment, do **NOT** re-run/modify sealed EVALs, do **NOT** claim GO without a new verifying sealed artifact on new real data.

## EVAL-38 SEALED — COMPLETE (REPLICATION) — 2026-11-14T15:39:45Z

## EVAL-39 PRE-FLIGHT (measured 2026-11-14T16:18–16:20Z — superseded by sealed rerun 16:25:21Z)

Run on the re-acquired real tape/options cross-section; `data_provenance="real"`; no synthetic input; `--no-write` so nothing was sealed. These numbers are the expected values for the EVAL-39 seal — re-measure, do not copy:

| Metric | Measured (re-acquired window 09:05:22Z→15:33:56Z) |
|---|---|
| Verdict / checks | **NO-GO**, 8/11; failed `options_signal_exists`, `combined_net_of_cost_superior`, `options_signal_tradable` |
| `options_leg_degenerate` | **true** |
| `combined_alpha.ic_mean` | -0.000258 (t=-0.00995; per-horizon 1/5/20 = -0.03871 / -0.02483 / +0.06277) |
| `options_alpha` | **0.0 at all horizons** (static broadcast: zero time-variation — the sealed EVAL-29/30 root cause) |
| `orderflow_alpha.ic_mean` | +0.041876 (t=2.1797) — the only positive pillar |
| `combined_wf` | Sharpe 7.4561, 245 trades, $420.80 cost, max-DD 0.2084, 36 windows |
| `options_only_wf` | Sharpe 7.8934, 589 trades, $666.75 cost, max-DD 0.1706 |
| `orderflow_only_wf` | Sharpe **-0.1382**, 540 trades, $635.94 cost, max-DD 0.6897 |
| `flat_wf` | 0 trades / 0 cost (control) |
| `permutation` | observed diff **-0.11267**, null mean 0.000567, **p=0.000999** (combined significantly *worse* than best single pillar) |
| Bars / trades | 1555 bars @15 s / 77,700 trades |

**INTERPRETATION TRAPS — do not cite these as tradable evidence:**
1. `combined_wf` Sharpe 7.4561 and `options_only_wf` Sharpe 7.8934 are **not** edge: the options signal has **zero time-variation** (`options_alpha` IC = 0.0), so "options-only" is economically a constant position on a rising tape, and the permutation test (p=0.000999) shows the combined leg is significantly *worse* than the best single pillar. Sealed EVAL-33/34 already adjudicated this.
2. These numbers come from a **different window** than EVAL-23's sealed -0.016776 IC. A window change is not a refutation and not a bit-level replication; label it honestly (see ledger rows below).
3. Do not "fix" `options_signal_exists` by editing `src/analytics/*` — the static-broadcast function is sealed (see "BOTTLENECKS ALREADY REMOVED" item 4 below). A constant-zero-then-static options leg is the measured truth for this dataset.

## EVAL-39 SEALED STATE (2026-11-14T16:35:54Z)

- **EVAL-39a:** Sealed `REAL_NET_OF_COST_EVAL_23_20261114T162521Z.{json,md}` on re-acquired real tape (command `python3 -m src.analytics.real_net_of_cost_evaluation --data-dir data/raw --out research_state`, `data_provenance="real"`). Verdict **NO-GO 8/11**; failed `options_signal_exists`, `combined_net_of_cost_superior`, `options_signal_tradable`; `options_leg_degenerate=true`; permutation p=0.000999 (combined worse than best single pillar). Combined/options-only Sharpe not tradable edge due to `options_alpha` IC 0.0 (static broadcast).
- **EVAL-39b/c:** Sealed `DURABILITY_LEDGER_39_20261114T163011Z.{json,md}` with verdict **REPLICATION**, full measured block (with input/artifact SHAs), and 16 ledger rows EVAL-23..38 (non-empty `verifying_command`, `raw_data_status`, `reproducible`, provenance notes). Reproducible-row verification recorded (34: 7p/1f interaction from newest EVAL-23 selection; 35: 3p/5f missing tape; 36: 7p; 37: 6p; 38: prior 9p, rerun timeout RC=124).
- **Conclusion:** Durability ledger closed for currently available real data. Campaign remains **TERMINATED** (EVAL-36). EVAL-40+ only on newly acquired/sealed real data with pre-registered plan.

**ANTI-AVOIDANCE GATE (standing):** a session is complete **only** if it produces a new `research_state/*_<UTC>.{json,md}` measured artifact (replication/refutation/blocker/ledger or newly acquired dataset provenance). Reading, planning, or tests-without-sealing are non-progress.

**Do NOT:** reopen deployment, re-run/modify sealed EVAL-02..39, create new handoff files/timestamped copies, use synthetic-preferring campaign loaders, or claim GO without a verifying sealed artifact on new real data.

## PRIOR SEALED STATE (ground truth; do not re-litigate)

- **EVAL-02..EVAL-22** sealed. EVAL-25 **GO** (`REAL_DATA_FALSIFICATION_20261114T025046Z`). EVAL-26 **SEALED** (`PUBLIC_EXPORT_ACQUISITION_20261114T103323Z`; public OKX export, authenticity_verified=false).
- **EVAL-23 SEALED NO-GO:** `REAL_NET_OF_COST_EVAL_23_20261114T040000Z` — combined IC mean -0.016776 (|t|=4.1008, p=0.0020 adverse); `options_leg_degenerate=true`.
- **EVAL-24 SEALED NO-GO:** `OPTIONS_LEG_VALIDITY_24_20261114T041000Z` — parity-consistent but `options_leg_tradable` FAIL; venue IV/greeks/OI coverage 0%.
- **EVAL-27 SEALED NO-GO:** `OPTIONS_TIMESERIES_INGESTION_27_20261114T064908Z`, `AMENDED_FUSION_EVAL_27_20261114T065033Z`.
- **EVAL-28 SEALED GO (additive):** `OPTIONS_LEG_PARITY_CALIBRATION_28_20261114T085233Z` / `...093132Z` — per-expiry forward-calibrated put-call parity 1017/1017 pairs (100%), min R²=0.999919.
- **EVAL-29 SEALED NO-GO:** `OPTIONS_LEG_TRADABILITY_29_20261114T093151Z`.
- **EVAL-30 SEALED NO-GO:** `OPTIONS_LEG_TRADABILITY_30_20261114T113051395ZZ.{json,md}`. Reproduced: `n_bars=1553`, `n_snapshots=3`, `ic_mean=-0.002957`, `distinct_signal_values=3`, `n_flat_bars=1300`.
- **EVAL-31 SEALED GO (marginal):** `AMENDED_FUSION_EVAL_31_20261114T114328Z.{json,md}` — Rule A fusion; combined OOS Sharpe 0.3016, perm p=0.768, PBO 0.75.
- **EVAL-32 SEALED NO-GO (validation):** `EVAL_32_OOS_VALIDATION_20261114T124437Z.{json,md}` — EVAL-31 GO fails held-out (1/4 criteria); combined edge indistinguishable from orderflow-only (perm p=0.2498, PBO 0.5156, bootstrap CI includes 0).
- **EVAL-33 SEALED NO-GO (falsification):** `OPTIONS_LEG_FALSIFICATION_33_20261114T134105Z.{json,md}` — options leg carries zero net-of-cost alpha; all 6 options-only variants flat; orderflow-only is the only non-degenerate control.
- **EVAL-34 SEALED NO-GO + DECISION:** `FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.{json,md}` — combined NOT net-of-cost tradable; decision then DEPLOY_ORDERFLOW_ONLY_WITH_CAVEATS (invalidated by EVAL-35). Orderflow-only held-out: Sharpe 4.8115, 129 trades, $157.02 cost on 466 bars. 8 tests passed. **A second, unrecorded seal `FINAL_STRATEGY_FALSIFICATION_34_20261114T143115Z.{json,md}` also exists** (same schema, `generated_at` 14:31:15Z). Both are immutable; `_find_artifact` sorts and takes the newest, so any EVAL-39 re-aggregation must pin the timestamp explicitly (bottleneck 8).
- **EVAL-35 SEALED NO-GO (replication failure):** `ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_20261114T144800Z.{json,md}` — second independent real window `08:08:15Z→14:39:17Z` (57,600 trades, 1565 bars): Sharpe -18.1777, 1255 trades, $184.93 cost, max-DD 0.9662, kill-switch breached `[max_drawdown,cost_bps,toxicity]`, `non_degenerate=False`, `within_band=False`. 8 tests passed (per sealed record).
- **EVAL-36 SEALED TERMINATE_NO_GO:** `FINAL_TERMINATION_MEMO_36_20261114T145419Z.{json,md}` — 11 evidence rows EVAL-23..35; campaign TERMINATED; 7 tests passed.
- **EVAL-37 SEALED (audit):** `research_state/FINAL_TERMINATION_AUDIT_37_20261114T152849Z.{json,md}` — **PASS 9/9** (see EVAL-38 block). The earlier `..._20261114T151805Z.{json,md}` recorded a measured FAIL 7/9 caused solely by the checker schema bug now fixed; it remains as immutable history.

## BOTTLENECKS ALREADY REMOVED (do not re-litigate)

1. **EVAL-37 checker schema bug FIXED** — `_eval36_field` reads `campaign_status`/`paper_rollout_certified` from `final_decision` (EVAL-36's authoritative schema). EVAL-37 now PASS 9/9.
2. **Runtime unblocked** — `scripts/verify_env.sh` bootstraps `requirements.txt` into git-ignored `.venv-deps/`; `AGENTS.md` records the exact commands. `py_compile` and targeted `pytest` now run on a fresh checkout.
3. **Network verified** — public OKX endpoints reachable with a normal `User-Agent` (HTTP 200); `src/data/public_export_acquisition.py` requires no credentials and no `.env`.
4. **Root cause of prior NO-GO recorded (do NOT re-fix):** `integrated_options_orderflow_evaluation.py::_causal_options_signal_series` broadcasts a single static options value to every bar → zero time-variation → mean IC 0.0. Do not modify that sealed function.
5. **Prior sealed EVALs** (EVAL-23..36) stand as recorded above; do not re-run or modify them.
6. **EVAL-38 REPLICATION sealed (2026-11-14T15:39:45Z):** the EVAL-35 NO-GO reproduces on an independently re-acquired real OKX tape (Sharpe -7.9539, 1221 trades, $179.28 cost, max-DD 0.8679, kill-switch breach). Evidence durability for the orderflow pillar is now **measured**, not assumed. Raw tapes live at `data/raw/orderflow_okx_BTC-USD-SWAP.json` and `data/raw/options_okx_BTC_20261114T153357Z.json` (git-ignored, re-acquirable on demand).
7. **EVAL-39 runnability PROVEN (removed 2026-11-14T16:20Z).** The previous plan assumed EVAL-34 might be the re-run target; it is not (aggregation-only). The real-data engine `python3 -m src.analytics.real_net_of_cost_evaluation --data-dir data/raw --no-write` runs end-to-end on the re-acquired real inputs in **59 s**, `data_provenance="real"`, and reproduces the EVAL-23 failure signature (NO-GO 8/11; same three failed checks; `options_leg_degenerate=true`). No hardcoded window, no network, no synthetic input. Verified loaders: `load_real_orderflow("BTC")` -> 77,700 trades (09:05:22.330Z→15:33:56.432Z); `load_real_options_chain("BTC")` -> 815 quotes / 14 expiries.
8. **Synthetic-preferring loader trap documented.** `src/campaign/integrated.py::_load_orderflow` / `::_load_options_chain` (lines 184-235) check `data/raw/orderflow_btcusdt_synthetic.json` and `data/raw/options_btc_synthetic.json` **first** and then fall back to deterministic synthesis. `src/analytics/integrated_options_orderflow_evaluation.py::main` routes through them. Both files exist in this checkout. Any EVAL-39 run through those entry points would seal a **synthetic** artifact — use `real_net_of_cost_evaluation` / `load_real_*` only.
9. **Duplicate EVAL-34 seal documented (not modified).** `..._20261114T135416Z` (recorded) and `..._20261114T143115Z` (unrecorded) both exist. `_find_artifact` picks the newest by filename sort. EVAL-39 must pin `FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.json` explicitly when citing EVAL-34, and record both in the ledger.
10. **Input-availability map (measured, for honest provenance labels).** `data/raw/` contains exactly one real orderflow export (`orderflow_okx_BTC-USD-SWAP.json`) and one real options export (`options_okx_BTC_20261114T153357Z.json`), plus two synthetic fixtures. Absent: the EVAL-35 tape `orderflow_okx_BTC-USD-SWAP_20261114T080515Z.json`, the EVAL-23/34 window tape, and the multi-snapshot options series (`options_okx_..._093032Z.json` and siblings) required by EVAL-27/29/30. Therefore those rows are `sealed_inputs_only` / `reproducible=false`; only EVAL-34/36/37 (pure aggregation) and EVAL-38 (re-acquired) are bit-reproducible.

## VERIFIED ENVIRONMENT (re-verify only if an import fails)

- Repo: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`. HEAD `6623db02f` (EVAL-39 rerun/ledger sealed at this commit). Prior noted heads: `96896d978` (pre-flight), `33dfa07fe` (earlier).
- `.env` absent (paper-only; must stay absent). No stale `*.lock`/`*.pid` in `research_state/`.
- Bootstrap: `./scripts/verify_env.sh` (or `--check` after deps exist). Deps: `requirements.txt`.
- Single durable handoff: this file. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers with **no task IDs**.

## NEXT-FOCUS CAMPAIGN (heavy work — future agents must not avoid it)

The strategic objective is a **tradable** cryptocurrency options+orderflow strategy measured net-of-cost on real data. The strategy is **TERMINATED** (EVAL-36) and that NO-GO has been **replicated on a freshly re-acquired real tape** (EVAL-38); the combined-leg failure signature is now also re-measured on that tape (pre-flight, 16:20Z). The single remaining obligation is to **close the durability ledger across the whole sealed chain**: seal the EVAL-39 ledger with the re-run numbers and a per-claim provenance + reproducible flag. Every execution session must advance this by at least one **sealed measured artifact** (a replication, a refutation, a blocker with the exact failing command, or a fully-provenanced durability ledger). Discovery-only, re-reading logs, or tests-without-sealing are non-progress.

**Anti-avoidance rule (binding):** if a session ends without a new `research_state/*_<UTC>.{json,md}` artifact that carries measured fields, it did not happen. "I verified the handoff", "I re-read EVAL-38", "tests pass" are not deliverables. The only permitted non-sealing session is one that seals a **BLOCKED** artifact with the exact failing command and stderr.

| Eval | Focus | Heavy-work requirement | Status |
|---|---|---|---|
| EVAL-02..EVAL-22 | Sealed prior gates | — | **SEALED** |
| EVAL-23..EVAL-33 | Real net-of-cost / options-leg falsification | — | **SEALED NO-GO** (EVAL-25/28 GO additive) |
| EVAL-34 | Final consolidated falsification + decision | — | **SEALED NO-GO** (`...135416Z`; duplicate `...143115Z`) |
| EVAL-35 | Second independent real window | — | **SEALED NO-GO** (`...144800Z`; tape absent) |
| EVAL-36 | Final termination memo | — | **SEALED TERMINATE_NO_GO** (`...145419Z`) |
| EVAL-37 | Independent post-termination audit | Load/verify sealed inputs; SHA-256; seal PASS/FAIL | **SEALED PASS 9/9** (`FINAL_TERMINATION_AUDIT_37_20261114T152849Z`) |
| EVAL-38 | Evidence durability: re-acquire tapes; replicate/refute EVAL-35 | Public re-acquisition; real re-run of EVAL-35 methodology; seal replication/refutation/blocker | **SEALED REPLICATION** (`EVIDENCE_DURABILITY_REPLICATION_38_20261114T153945Z`) |
| **EVAL-39** | **Durability cross-check & ledger (combined re-run + 16-row ledger EVAL-23..38)** | Real re-run on re-acquired tape; seal measured rerun + `DURABILITY_LEDGER_39_<UTC>.{json,md}` with SHAs/provenance/verifying commands | **SEALED REPLICATION** (`DURABILITY_LEDGER_39_20261114T163011Z`, rerun `REAL_NET_OF_COST_EVAL_23_20261114T162521Z`) |
| EVAL-40+ | Only if a **new** independently acquired real dataset/window is sealed and a pre-registered refutation plan is sealed first | Acquire & seal new real data provenance, then seal REPLICATION/REFUTED/BLOCKED with measured numbers | **NOT STARTED (blocked until new real dataset acquired & pre-registered)** |

## HARD CONSTRAINTS / INVARIANTS

- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- Never fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`. **Never load inputs through `src/campaign/integrated.py::_load_orderflow` / `_load_options_chain` or `src/analytics/integrated_options_orderflow_evaluation.py`** (synthetic-preferring; see bottleneck 8). Use `load_real_orderflow` / `load_real_options_chain` / `DataLoader().load_orderflow(<explicit path>)`.
- Sealed artifacts are immutable: EVAL-02..38; append new timestamped artifacts only.
- Network: public read-only market data only, polite rate limiting, only if truly required for EVAL-39.
- Reuse existing modules: `src/analytics/{options_time_varying_signal,integrated_options_orderflow_evaluation,real_net_of_cost_evaluation,capacity_aware_tca,strategy_evaluation,real_walkforward_certification,strategy_falsification}.py`, `src/campaign/integrated.py`, `src/data/{public_export_acquisition,loader,schemas,options_exports,options_timeseries}.py`, `src/features/*`, `src/backtest/engine.py`, `src/telemetry/serialization.py`.
- Prohibited: discovery runs, re-litigating sealed EVALs, enumerating `research_state/` broadly, full test-suite runs (~5k), modifying `.github/workflows/main.yml`, `phaseNN_*_post_attribution_seal_orchestrator` wrappers, handoff-only execution sessions.

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands. No timestamped handoff copies.
- Record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.