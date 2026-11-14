# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE — timestamped 2026-11-14T16:20:00Z UTC — TASK ID `INIT-2026-11-14T16:20:00Z-EVAL-39-DURABILITY-CROSS-CHECK`** (most recent, authoritative; supersedes the older 15:39:45Z / 15:29 / 15:18 / 15:19 messages previously at the top of this file). Inferred from the repo's own charter — *cryptocurrency quantitative OPTIONS + ORDERFLOW strategy, net-of-cost, real-data only, sealed measurement* — the single remaining obligation is **EVAL-39: close the durability ledger for the combined options+orderflow leg on re-acquired real data.**

**EVAL-39 IS NOW UNBLOCKED AND PROVEN RUNNABLE — do not re-derive the plan, execute it.** The blocker previously recorded ("EVAL-34's tape path may be hardcoded / the combined leg may not be re-runnable") is **removed**: EVAL-34 is an *aggregation-only* script (no computation, `scripts/eval34_final_strategy_falsification.py` docstring lines 8-16), so the correct re-run target is the real-data engine **`src/analytics/real_net_of_cost_evaluation.py`**, which discovers real exports from `data/raw/` (no hardcoded window). Measured pre-flight on the re-acquired tape (2026-11-14T16:18–16:20Z, `data_provenance="real"`, 59 s):

```
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m src.analytics.real_net_of_cost_evaluation --data-dir data/raw --no-write
# -> verdict NO-GO, 8/11 checks, failed: [options_signal_exists,
#    combined_net_of_cost_superior, options_signal_tradable], options_leg_degenerate=true
```
Inputs actually consumed (verified, not assumed): `load_real_orderflow("BTC")` -> `data/raw/orderflow_okx_BTC-USD-SWAP.json` (77,700 trades, 09:05:22.330Z -> 15:33:56.432Z); `load_real_options_chain("BTC")` -> `data/raw/options_okx_BTC_20261114T153357Z.json` (815 quotes, 14 expiries). Bars: 1555 @ 15 s. Same three failed checks as sealed EVAL-23 on the *old* window.

**EVAL-39 DELIVERABLE (heavy work; one sealed measured artifact, no exceptions):** seal `research_state/DURABILITY_LEDGER_39_<UTC>.{json,md}` containing (a) the re-run verdict + every measured number above, with the exact command and input SHAs, and (b) one ledger row per sealed EVAL-23..38 claim: `claim`, `sealed_artifact`, `raw_data_status ∈ {re_acquired_reproduced, sealed_inputs_only, synthetic_fixture}`, `reproducible` bool, verifying command. A **REPLICATION**, a **REFUTATION**, a **measured blocker artifact**, or a **fully-provenanced ledger** are all full successes. Handoff-only, discovery-only, or tests-without-sealing sessions are **non-progress**.

**EVAL-39 CURRENT STATE: IN PROGRESS — active task.** Sealed chain so far: EVAL-38 `REPLICATION` (`research_state/EVIDENCE_DURABILITY_REPLICATION_38_20261114T153945Z.{json,md}`); campaign remains **TERMINATED** (EVAL-36 `TERMINATE_NO_GO`).

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

## EVAL-39 PRE-FLIGHT (measured 2026-11-14T16:18–16:20Z — UN-SEALED; the EVAL-39 artifact supersedes it)

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

## ACTIVE TASK — EVAL-39 "DURABILITY CROSS-CHECK & LEDGER" (heavy work; future agents must not avoid it)

EVAL-38 proved the EVAL-35 orderflow-only NO-GO replicates on a fresh real tape. The remaining scientific obligation is to **close the durability ledger across the full sealed chain** so no conclusion rests on a single un-reproducible window, and to **quantify how much the NO-GO direction is stable across independent real windows**. Every execution session must advance this by at least one **sealed measured artifact**. Discovery-only, re-reading logs, or tests-without-sealing are non-progress.

**EVAL-39 steps (heavy work required):**

1. **Re-run the combined options+orderflow falsification on the re-acquired real data** and record every measured field. Use the real-data engine (verified, 59 s):
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   python3 -m src.analytics.real_net_of_cost_evaluation --data-dir data/raw --out research_state
   ```
   **Never** use `src/campaign/integrated.py::_load_orderflow` / `_load_options_chain` or
   `python3 -m src.analytics.integrated_options_orderflow_evaluation` for this: both prefer
   `data/raw/orderflow_btcusdt_synthetic.json` / `data/raw/options_btc_synthetic.json` (present in
   the checkout) and silently fall back to deterministic synthesis — that would emit a **synthetic**
   artifact and violate a hard invariant. Always load via `load_real_orderflow` / `load_real_options_chain`
   (or `DataLoader().load_orderflow(<path>)`), which raise `RealDataUnavailable` instead.
   Seal whether the combined leg is **REPLICATED** (still NOT net-of-cost tradable) or **REFUTED**
   (combined becomes tradable — major finding, escalate immediately).
2. **Seal the durability LEDGER** (`research_state/DURABILITY_LEDGER_39_<UTC>.{json,md}`): one row per sealed EVAL-23..38 claim with `claim`, `sealed_artifact`, `raw_data_status ∈ {re_acquired_reproduced, sealed_inputs_only, synthetic_fixture}`, `reproducible` bool, and the verifying command. **Provisional skeleton (verify each row before sealing — do not copy blindly):**

   | EVAL | Claim (short) | Sealed artifact | `raw_data_status` | `reproducible` |
   |---|---|---|---|---|
   | 23 | Combined IC -0.016776 adverse; combined not tradable | `REAL_NET_OF_COST_EVAL_23_20261114T040000Z` | `sealed_inputs_only` (original 08:08→14:39 tape absent) — qualitatively reproduced on re-acquired window (NO-GO 8/11, same 3 failures) | `false` (window-level) |
   | 24 | Options leg not tradable (venue IV/greeks/OI 0%) | `OPTIONS_LEG_VALIDITY_24_20261114T041000Z` | `sealed_inputs_only` | `false` |
   | 25 | GO additive (falsification) | `REAL_DATA_FALSIFICATION_20261114T025046Z` | `sealed_inputs_only` | `false` |
   | 26 | Public export acquisition | `PUBLIC_EXPORT_ACQUISITION_20261114T103323Z` | `sealed_inputs_only` | `false` |
   | 27 | Options time-series ingestion NO-GO | `OPTIONS_TIMESERIES_INGESTION_27_...064908Z` | `sealed_inputs_only` (3-snapshot series; only 1 real snapshot exists now) | `false` |
   | 28 | Parity calibration GO (1017/1017, min R² 0.999919) | `OPTIONS_LEG_PARITY_CALIBRATION_28_...085233Z`/`...093132Z` | `sealed_inputs_only` | `false` |
   | 29 | Options leg tradability NO-GO (broadcast-static, mean IC 0.0) | `OPTIONS_LEG_TRADABILITY_29_...093151Z` | `sealed_inputs_only`; **mechanism re-confirmed** (`options_alpha` IC 0.0 on re-acquired data) | `false` |
   | 30 | Time-varying signal NO-GO (ic_mean -0.002957) | `OPTIONS_LEG_TRADABILITY_30_...113051395ZZ` | `sealed_inputs_only` | `false` |
   | 31 | Rule-A fusion GO (Sharpe 0.3016) | `AMENDED_FUSION_EVAL_31_...114328Z` | `sealed_inputs_only` | `false` |
   | 32 | Held-out validation NO-GO (1/4) | `EVAL_32_OOS_VALIDATION_...124437Z` | `sealed_inputs_only` | `false` |
   | 33 | Options leg carries zero net-of-cost alpha | `OPTIONS_LEG_FALSIFICATION_33_...134105Z` | `sealed_inputs_only`; **re-confirmed** (options_alpha IC 0.0, 0-trade options variants) | `false` |
    | 34 | Combined NOT tradable + decision | `FINAL_STRATEGY_FALSIFICATION_34_...135416Z` (**and** duplicate `...143115Z`, see bottleneck 9) | `sealed_inputs_only` (aggregation of sealed rows) | `true` (deterministic aggregation) |
   | 35 | Second window NO-GO (Sharpe -18.1777) | `ORDERFLOW_ONLY_SECOND_WINDOW_VALIDATION_35_...144800Z` | `sealed_inputs_only` (its tape `..._080515Z.json` is **absent**); **replicated by EVAL-38 on new tape** | `false` (window-level) |
   | 36 | TERMINATE_NO_GO (11 rows) | `FINAL_TERMINATION_MEMO_36_...145419Z` | `sealed_inputs_only` | `true` (aggregation) |
   | 37 | Post-termination audit PASS 9/9 | `FINAL_TERMINATION_AUDIT_37_...152849Z` | `sealed_inputs_only` | `true` (verify command reproducible) |
   | 38 | Orderflow NO-GO replicated on fresh tape | `EVIDENCE_DURABILITY_REPLICATION_38_...153945Z` | **`re_acquired_reproduced`** | `true` (re-acquire + re-run) |
3. **If a row cannot be re-verified** (e.g. options time-series needs the absent `options_okx_..._093032Z.json`), seal a **measured blocker artifact** with the exact failing command and reason; do NOT fall back to synthetic data and do NOT emit `{"valid": true}`.
4. Update this handoff in place; append timestamped artifacts only. Do not modify sealed artifacts.

**ANTI-AVOIDANCE GATE (EVAL-39 acceptance):** a session is complete **only** if `research_state/DURABILITY_LEDGER_39_<UTC>.json` exists and contains (i) `verdict` ∈ {REPLICATION, REFUTED, BLOCKED}, (ii) `measured` block with the re-run numbers, (iii) `ledger_rows` covering EVAL-23..38 with non-empty `verifying_command` per row, (iv) `data_provenance="real"`, `never_valid_true=true`, and (v) at least one sealed `*.md` sibling. Editing this file, reading artifacts, or running tests **without** producing that JSON is non-progress.

A measured REPLICATION, a measured REFUTATION, a measured blocker artifact, or a fully-provenanced durability ledger are all full successes. Handoff-only or tests-only-without-sealing sessions are non-progress.

**Do NOT:** reopen deployment, re-run sealed EVAL-23..37 blindly, modify sealed artifacts, create new handoff files or timestamped handoff copies, use the synthetic-preferring campaign loaders, or claim GO without a verifying sealed artifact. A trustworthy NO-GO with sealed, now-replicated measurement is a full success — this campaign already achieved that twice.

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

- Repo: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`. HEAD `96896d978` (the EVAL-39 pre-flight was run at this commit; `33dfa07fe` was the earlier recorded head).
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
| **EVAL-39a** | **Combined-leg cross-check: real re-run of `real_net_of_cost_evaluation` on re-acquired tape; capture full `measured` block (verdict, ICs, per-leg WF, permutation, bars/trades) with input SHAs** | **Run the verified command; record every field; no synthetic; no re-derivation of the plan** | **IN PROGRESS — step 1** |
| **EVAL-39b** | **Durability LEDGER seal: `DURABILITY_LEDGER_39_<UTC>.{json,md}` with 16 rows EVAL-23..38 (`claim`, `sealed_artifact`, `raw_data_status`, `reproducible`, `verifying_command`) + provenance notes from bottlenecks 7-10** | **Seal the JSON+MD with non-empty verifying commands; honest `sealed_inputs_only` labels; no `{"valid": true}`** | **IN PROGRESS — step 2 (depends on 39a)** |
| **EVAL-39c** | **Per-row verification of the reproducible rows (34/36/37/38): re-run their verify commands and record pass/fail + observed values** | **Execute each verifying command; record measured output; disagreement must be reported, not smoothed** | **PENDING — step 3** |
| EVAL-40+ | Only if EVAL-39 seals a REFUTED or a new tradable signal | Pre-registered replication on a third independent window before any GO language | **NOT STARTED** |

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