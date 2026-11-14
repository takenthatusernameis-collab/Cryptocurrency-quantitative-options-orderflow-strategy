# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T15:39:45Z UTC — TASK ID `INIT-2026-11-14T15:39:45Z-EVAL-39-DURABILITY-CROSS-CHECK`** (most recent, authoritative; supersedes the older 15:29/15:18/15:19 messages previously at the top of this file): **EVAL-38 EVIDENCE DURABILITY COMPLETE — SEALED REPLICATION.** The raw public OKX tapes were re-acquired live (HTTP 200, code 0; 77,700 trades / 1555 bars / 815 option contracts; tape SHA-256 `fa9e43b8…`) and the **EVAL-35 orderflow-only methodology was re-run verbatim on the freshly acquired tape**. Result: **REPLICATION** of the EVAL-35 NO-GO — Sharpe -7.9539 (EVAL-35 -18.1777), 1221 trades, $179.28 cost, max-DD 0.8679, kill-switch breach `[max_drawdown,cost_bps,toxicity]`, `non_degenerate=False`. The sealed EVAL-23..36 conclusions are now **recomputable from real raw data**, not merely internally consistent. New artifact: `research_state/EVIDENCE_DURABILITY_REPLICATION_38_20261114T153945Z.{json,md}`. 9 tests sealed. Campaign remains **TERMINATED**.

**ACTIVE TASK — EVAL-39 "DURABILITY CROSS-CHECK & LEDGER" (heavy work; future agents must not avoid it)** — the next focus campaign below.

## EVAL-38 SEALED — COMPLETE (REPLICATION) — 2026-11-14T15:39:45Z

- **Re-acquisition (live, public read-only):** `python3 -m src.data.public_export_acquisition --underlying BTC --orderflow-instrument BTC-USD-SWAP --min-bars 1550 --bar-duration-seconds 15` => OKX `history-trades` + `instruments` + `tickers` all HTTP 200 / code 0. Wrote `data/raw/orderflow_okx_BTC-USD-SWAP.json` (77,700 trades, 1555 bars, span 09:05:22Z→15:33:56Z, SHA-256 `fa9e43b8edeeeace7b7c551b23158aa68778dbf3909898f7e629da843baa43b6`) and `data/raw/options_okx_BTC_20261114T153357Z.json` (815 quotes, 14 expiries, SHA-256 `96b2e196…`). Adequacy: orderflow_adequate=true, options_adequate=true. Sealed `research_state/PUBLIC_EXPORT_ACQUISITION_20261114T153357Z.{json,md}`.
- **Replication script:** `scripts/eval38_evidence_durability_replication.py` reuses the EVAL-35 causal orderflow signal (`net_aggression`), VPIN>=0.70 toxicity gate, capacity-aware sizing (spread 2bps, impact 0.01, max participation 12.5%, cost budget 0.5bps), and net-of-cost walk-forward — identical parameters — against the re-acquired tape.
- **Sealed artifact:** `research_state/EVIDENCE_DURABILITY_REPLICATION_38_20261114T153945Z.{json,md}` — verdict **REPLICATION**, durability_status `CONCLUSIONS_REPRODUCIBLE`, task `INIT-2026-11-14T15:39:45Z-EVAL-38-EVIDENCE-DURABILITY-REPLICATION`. Measured: Sharpe -7.953897586502185, 1221 trades, $179.27749184473703 cost, max-DD 0.867913747468125, kill-switch `[max_drawdown,cost_bps,toxicity]`, non_degenerate=False, replicated_eval35=true.
- **Exact commands (run 2026-11-14T15:39Z):**
  - `./scripts/verify_env.sh` => **exit 0** (deps in `.venv-deps/`).
  - `python3 -m src.data.public_export_acquisition ...` => sealed `PUBLIC_EXPORT_ACQUISITION_20261114T153357Z`.
  - `python3 -m py_compile scripts/eval38_evidence_durability_replication.py tests/test_eval38_evidence_durability_replication.py` => OK.
  - `python3 -m pytest -q tests/test_eval38_evidence_durability_replication.py` => **9 passed**.
  - `python3 scripts/eval38_evidence_durability_replication.py` => sealed REPLICATION.
  - `pytest -q tests/test_eval37_final_termination_audit.py` => **6 passed** (sealed audit still green).
- **What this proves:** the -18.1777 NO-GO is not an artifact of a single tape; a second, independently re-acquired real OKX tape (distinct span 09:05→15:33Z vs EVAL-35's 08:08→14:39Z) fails the same way. Evidence durability is now measured, not assumed.
- **No synthetic fallback; `never_valid_true=True`; `authenticity_verified=False`; `.env` absent; sealed EVAL-34/35/36 untouched.**

## ACTIVE TASK — EVAL-39 "DURABILITY CROSS-CHECK & LEDGER" (heavy work; future agents must not avoid it)

EVAL-38 proved the EVAL-35 orderflow-only NO-GO replicates on a fresh real tape. The remaining scientific obligation is to **close the durability ledger across the full sealed chain** so no conclusion rests on a single un-reproducible window, and to **quantify how much the NO-GO direction is stable across independent real windows**. Every execution session must advance this by at least one **sealed measured artifact**. Discovery-only, re-reading logs, or tests-without-sealing are non-progress.

| Eval | Focus | Heavy-work requirement | Status |
|---|---|---|---|
| **EVAL-39** | **Cross-check durability: (a) re-run the EVAL-34 combined options+orderflow falsification on the re-acquired option cross-section + tape to confirm the combined leg also fails; (b) seal a durability LEDGER summarizing every sealed EVAL-23..38 claim with its raw-data provenance (re-acquired / sealed-input-only / synthetic-fixture) and a per-claim reproducible=true/false flag** | **Real re-run of combined falsification on re-acquired real data; seal measured artifact + ledger; no synthetic fallback; honest provenance labeling** | **IN PROGRESS — active task** |

**EVAL-39 steps (heavy work required):**
1. **Re-run the EVAL-34 combined options+orderflow falsification** (`scripts/eval34_final_strategy_falsification.py` methodology) against the re-acquired `data/raw/options_okx_BTC_20261114T153357Z.json` + `data/raw/orderflow_okx_BTC-USD-SWAP.json`. The EVAL-34 script's tape path may be hardcoded to the old window; reuse its methodology on the re-acquired files. Seal whether the combined leg is **REPLICATED** (still NOT net-of-cost tradable) or **REFUTED** (combined becomes tradable — would be a major finding requiring immediate escalation).
2. **Seal a durability LEDGER** (`research_state/DURABILITY_LEDGER_39_<UTC>.{json,md}`): one row per sealed EVAL-23..38 claim with `claim`, `sealed_artifact`, `raw_data_status` ∈ {re_acquired_reproduced, sealed_inputs_only, synthetic_fixture}, `reproducible` bool, and the verifying command. EVAL-38's REPLICATION marks the EVAL-23..35 chain `re_acquired_reproduced` for the orderflow pillar.
3. **If combined falsification cannot be re-run on the re-acquired data** (e.g. option time-series needs the absent `options_okx_…_093032Z.json` snapshot history), seal a **measured blocker artifact** with the exact failing command and reason; do NOT fall back to synthetic data and do NOT emit `{"valid": true}`.
4. Update this handoff in place; append timestamped artifacts only.

A measured REPLICATION, a measured REFUTATION, a measured blocker artifact, or a fully-provenanced durability ledger are all full successes. Handoff-only or tests-only-without-sealing sessions are non-progress.

**Do NOT:** reopen deployment, re-run sealed EVAL-23..37 blindly, modify sealed artifacts, create new handoff files or timestamped handoff copies, or claim GO without a verifying sealed artifact. A trustworthy NO-GO with sealed, now-replicated measurement is a full success — this campaign already achieved that twice.

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
- **EVAL-34 SEALED NO-GO + DECISION:** `FINAL_STRATEGY_FALSIFICATION_34_20261114T135416Z.{json,md}` — combined NOT net-of-cost tradable; decision then DEPLOY_ORDERFLOW_ONLY_WITH_CAVEATS (invalidated by EVAL-35). Orderflow-only held-out: Sharpe 4.8115, 129 trades, $157.02 cost on 466 bars. 8 tests passed.
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

## VERIFIED ENVIRONMENT (re-verify only if an import fails)

- Repo: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`. HEAD `33dfa07fe`.
- `.env` absent (paper-only; must stay absent). No stale `*.lock`/`*.pid` in `research_state/`.
- Bootstrap: `./scripts/verify_env.sh` (or `--check` after deps exist). Deps: `requirements.txt`.
- Single durable handoff: this file. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers with **no task IDs**.

## NEXT-FOCUS CAMPAIGN (heavy work — future agents must not avoid it)

The strategic objective is a **tradable** cryptocurrency options+orderflow strategy measured net-of-cost on real data. The strategy is **TERMINATED** (EVAL-36) and that NO-GO has now been **replicated on a freshly re-acquired real tape** (EVAL-38). The remaining scientific obligation is to **close the durability ledger across the whole sealed chain**: confirm the combined options+orderflow falsification also reproduces on re-acquired real data, and label every sealed claim with its raw-data provenance and a reproducible flag. Every execution session must advance this by at least one **sealed measured artifact** (a replication, a refutation, a blocker with the exact failing command, or a fully-provenanced durability ledger). Discovery-only, re-reading logs, or tests-without-sealing are non-progress.

| Eval | Focus | Heavy-work requirement | Status |
|---|---|---|---|
| EVAL-02..EVAL-22 | Sealed prior gates | — | **SEALED** |
| EVAL-23..EVAL-33 | Real net-of-cost / options-leg falsification | — | **SEALED NO-GO** (EVAL-25/28 GO additive) |
| EVAL-34 | Final consolidated falsification + decision | — | **SEALED NO-GO** (`...135416Z`) |
| EVAL-35 | Second independent real window | — | **SEALED NO-GO** (`...144800Z`) |
| EVAL-36 | Final termination memo | — | **SEALED TERMINATE_NO_GO** (`...145419Z`) |
| EVAL-37 | Independent post-termination audit | Load/verify sealed inputs; SHA-256; seal PASS/FAIL | **SEALED PASS 9/9** (`FINAL_TERMINATION_AUDIT_37_20261114T152849Z`) |
| EVAL-38 | Evidence durability: re-acquire tapes; replicate/refute EVAL-35 | Public re-acquisition; real re-run of EVAL-35 methodology; seal replication/refutation/blocker | **SEALED REPLICATION** (`EVIDENCE_DURABILITY_REPLICATION_38_20261114T153945Z`) |
| **EVAL-39** | **Durability cross-check & ledger: re-run EVAL-34 combined falsification on re-acquired real data; seal durability LEDGER labeling every EVAL-23..38 claim with raw-data provenance + reproducible flag** | **Real re-run of combined falsification; seal measured artifact + ledger; no synthetic fallback; honest provenance labels** | **IN PROGRESS — active task** |

## HARD CONSTRAINTS / INVARIANTS

- Paper-only: `.env` absent and must stay absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- Never fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Sealed artifacts are immutable: EVAL-02..38; append new timestamped artifacts only.
- Network: public read-only market data only, polite rate limiting, only if truly required for EVAL-39.
- Reuse existing modules: `src/analytics/{options_time_varying_signal,integrated_options_orderflow_evaluation,real_net_of_cost_evaluation,capacity_aware_tca,strategy_evaluation,real_walkforward_certification,strategy_falsification}.py`, `src/campaign/integrated.py`, `src/data/{public_export_acquisition,loader,schemas,options_exports,options_timeseries}.py`, `src/features/*`, `src/backtest/engine.py`, `src/telemetry/serialization.py`.
- Prohibited: discovery runs, re-litigating sealed EVALs, enumerating `research_state/` broadly, full test-suite runs (~5k), modifying `.github/workflows/main.yml`, `phaseNN_*_post_attribution_seal_orchestrator` wrappers, handoff-only execution sessions.

## HANDOFF DISCIPLINE

- This file is the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands. No timestamped handoff copies.
- Record measured numbers, not intentions. Never claim persistence or GO without a verifying artifact.
- Final responses must not ask follow-up questions.