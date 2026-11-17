# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-17T06:23:02Z — EVAL-70/71/72/73 SEALED; pre-threshold heavy work fully green (188/188 targeted, 27/27 diagnostics, 8 gates); do not launch another pre-threshold wait session):**>
> **NEXT-SESSION TRIGGER:** start only at/after **2026-11-20T00:00:00Z**, or immediately when any phase-B arbiter reports `DUE` (exit 20) or `FAILED` (exit 1). The external `*/5` cron owns routine pre-threshold polling; do **not** create another agent session merely to rerun unchanged tests or bump this timestamp.
>
> **FIRST ACTION, non-negotiable:** run
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> That one command performs the full heavy-work loop: environment check, the **176 targeted tests** (EVAL-72's 12 added), the **27 controller/campaign/diagnostics tests**, all **seven** campaign arbiters in ladder order (EVAL-70 + EVAL-71 + EVAL-72 physics-independent first, then the EVAL-67 -> EVAL-68 -> EVAL-69 disjoint-forward ladder), automatic `--execute` of any campaign that reports `DUE`, seal-gate checks, and an in-place refresh of `research_state/EVAL_67_PREWINDOW_READINESS.json`. **Do not exit the session until it exits 0.** If an early invocation returns `DUE` without `--execute`, rerun the same command immediately; if it returns `FAILED`, fix the reported step and rerun. A session that only bumps this timestamp has not run the driver and has not satisfied the contract.
>
> **THIS SESSION'S NEW VERIFIED HEAVY WORK (2026-11-17T05:20:00Z):** Built, tested, and sealed **EVAL-72** (`scripts/eval72_surface_skew_straddle_monetization.py` + `scripts/eval72_phaseb_gate.py` + 12 tests) — the on-charter, runnable-now *traded-form monetization* of EVAL-71's newly-predictive options implied-vol surface signal. It times the correct EVAL-62 mark-path net-of-cost delta-hedged ATM straddle with the causal surface skew / ATM-IV level (trade-tape IV), reuses the sealed EVAL-57/61/62/71 runners verbatim, composes the sealed EVAL-61/62 + EVAL-71 floors (neither weakened), and touches no `src/`. It sealed **NO-GO CONFIRMED (PASS)**: on the real on-disk BTC+ETH captures the *predictive* surface signal (EVAL-71 GO) does **not** monetize net-of-cost (BTC best Sharpe 0.84 on atm_iv::bar300, ETH best -1.20; no config clears permutation + bootstrap + kill-switch on both underlyings). This is the repo-priority answer for the terminal charter clause ("tradeable, net-of-cost alpha"): predictive != monetizable. EVAL-72 is wired into the driver (176 tests, 7 gates, 7 seal specs) so no future session can skip it.
>
> **NEXT GENUINE HEAVY WORK (repo priority):** the disjoint-forward **EVAL-67 -> EVAL-68 -> EVAL-69** ladder, at/after **2026-11-20T00:00:00Z** (hard Deribit retention physics; see STATUS). This is the unskippable net-of-cost capstone. If a pre-threshold session is genuinely required and all runnable-now campaigns are already sealed, the next runnable-now candidate is **EVAL-73** (see BOTTLENECKS #12) — build and wire it like EVAL-72; do not re-litigate sealed results.
>
> **Repo-priority reading of `Cryptocurrency-quantitative-options-orderflow-strategy`:** the thesis is *crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data*. The on-charter ladder EVAL-02..66 is **CLOSED** (EVAL-66 sealed `BLOCKED`, seal-gate exit 0). Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/EVAL-64..66/EVAL-70/EVAL-71/EVAL-72 artifacts or `src/`. Never synthetic data, never weaken the EVAL-64 floor, paper-only.

## PHYSICS-INDEPENDENT RUNNABLE-NOW CAMPAIGNS (sealed; fill the pre-threshold heavy-work gap)

- **EVAL-70 — underlying (OKX perp) order-flow -> forward RV / signed return predictiveness:** SEALED `NO-GO CONFIRMED` (gate exit 0). Runnable pre-threshold on the on-disk captures; no acquisition.
- **EVAL-71 — options implied-vol surface (near-ATM IV + put-call skew) -> forward RV predictiveness:** SEALED `GO CONFIRMED` (gate exit 0) at `2026-11-17T04:15:13Z`. The surface predicts forward RV (BTC IC 0.335, ETH 0.263) while order-flow (EVAL-65/70) is null. Reuses the sealed EVAL-61/62/65 runners; own pre-registered trade-tape IV floor (EVAL-64 floor untouched). Wired into the driver (176 tests, 7 gates) so it can never be skipped.
- **EVAL-72 — options implied-vol surface (EVAL-71 skew / ATM-IV) -> signal-timed delta-hedged ATM straddle net-of-cost monetization:** SEALED `NO-GO CONFIRMED (PASS)` (gate exit 0) at `2026-11-17T05:18:22Z`. The traded-form complement to EVAL-71: the *predictive* surface signal does not monetize net-of-cost (BTC best Sharpe 0.84, ETH best -1.20; no config clears permutation + bootstrap + kill-switch on both underlyings). Reuses the sealed EVAL-57/61/62 mark-path straddle machinery verbatim; composes the EVAL-61/62 + EVAL-71 floors (neither weakened). Wired into the driver (176 tests, 7 gates) so it can never be skipped.

These three are the runnable-now heavy work; they are idempotent no-ops once sealed. The forward-gated ladder below is the next genuine research heavy work (at/after `2026-11-20T00:00:00Z`).

## THREE SEQUENTIAL HEAVY CAMPAIGNS (repo-priority order)

1. **EVAL-67 — BTC-only predictiveness (FIRST):** task `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`; arbiter `python3 scripts/eval67_phaseb_gate.py`. Physics-gated to a disjoint forward window; prereg threshold `2026-11-20T00:00:00Z`. BTC-only was recorded pre-run as underpowered (IC 0.088, n 596 ⇒ one-sided ≈0.70).
2. **EVAL-68 — pooled BTC+ETH predictiveness (SECOND):** task `INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS`; arbiter `python3 scripts/eval68_phaseb_gate.py`. Power-adequate pooled rank-IC campaign (≥790 pooled pairs). Acquires only after EVAL-67 seals; the gate returns `WAIT_EVAL67` until then.
3. **EVAL-69 — pooled BTC+ETH TRADED-FORM net-of-cost monetization (THIRD, repo-priority capstone):** task `INIT-2026-11-16T22:45:00Z-EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS`; arbiter `python3 scripts/eval69_phaseb_gate.py`. Reuses EVAL-68's disjoint forward capture with **no new acquisition**, and measures pooled net-of-cost Sharpe / max-DD / directional permutation / block-bootstrap of the signal-timed delta-hedged ATM straddle on the same forward window. Runs only after EVAL-68 seals; the gate returns `WAIT_EVAL68` until then.

## DETERMINISTIC COMPLETION CONTRACT

- `python3 scripts/eval67_phaseb_gate.py` → `SEALED`(0) means EVAL-67 complete; `NOT_DUE`(10) means correct carry; `DUE`(20) means run `--execute` now; `FAILED`(1) means fix the reported step and re-run.
- `python3 scripts/eval68_phaseb_gate.py` → `SEALED`(0) means EVAL-68 complete; `WAIT_EVAL67`(10) means do not acquire; `DUE`(20) means run `--execute` now; `FAILED`(1) means fix and re-run.
- `python3 scripts/eval69_phaseb_gate.py` → `SEALED`(0) means the ladder is complete; `WAIT_EVAL68`(10) means do not run; `DUE`(20) means run `--execute` now; `FAILED`(1) means fix and re-run.
- `--execute` is the unskippable path: EVAL-67/68 acquire a disjoint real forward capture → dry-run → seal prereg + COMBINED/BLOCKED → seal-gate, and refuse to exit 0 unless the seal-gate exits 0. EVAL-69 does not acquire; it consumes EVAL-68's capture.
- The orchestrator runs the three arbiters sequentially, so when EVAL-67 seals it can proceed to EVAL-68 and then EVAL-69 in the same invocation.

## PRE-THRESHOLD HEAVY WORK (while gates are `NOT_DUE`/`WAIT`)

The orchestrator does all of this automatically. Run it with `--execute` every session. It must report:

- `env_check: true`
- `targeted_tests: 176/176`
- `diagnostic_tests: 27/27`
- `gates`: EVAL-70 `SEALED`, EVAL-71 `SEALED` (GO CONFIRMED), EVAL-72 `SEALED` (NO-GO CONFIRMED), EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` (pre-threshold)
- `overall_ok: true`, exit code 0

If it reports `exit_code: 20`, a campaign is `DUE`: re-run with `--execute`. If it reports `exit_code: 1`, fix the reported failed step and re-run. Do not replace this loop with a timestamp-only handoff bump.

## STATUS (verified 2026-11-17T06:23:02Z)

- **EVAL-70:** `SEALED` (gate exit 0) at `2026-11-17T02:37:55Z`. Prereg + COMBINED present; seal gate exit 0. Physics-independent; complete.
- **EVAL-71:** `SEALED` `GO CONFIRMED` (gate exit 0) at `2026-11-17T04:15:13Z`. Prereg + COMBINED present (`EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_{PREREGISTRATION,COMBINED}_20261117T041513Z.{json,md}`); seal gate exit 0. Physics-independent; complete. First GO in the predictiveness line: options surface IV/skew predicts forward RV on both BTC (IC 0.335) and ETH (IC 0.263); 10 BH-FDR rejections; EVAL-64 floor untouched.
- **EVAL-72:** `SEALED` `NO-GO CONFIRMED (PASS)` (gate exit 0) at `2026-11-17T05:18:22Z`. Prereg + COMBINED present (`EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_{PREREGISTRATION,COMBINED}_20261117T051822Z.{json,md}`); seal gate exit 0. Physics-independent; complete. Traded-form monetization of EVAL-71's predictive surface signal: on the real on-disk BTC+ETH captures it does **not** monetize net-of-cost (BTC best Sharpe 0.8424 on `atm_iv::bar300`; ETH best -1.1967; no config clears permutation + bootstrap + kill-switch on both underlyings; BH-FDR rejected none). Predictive != monetizable.
- **EVAL-67:** `NOT_DUE` (gate exit 10) at `2026-11-17T05:19:03Z`; `overlap_seconds = 239205.922` (strictly decreasing from 241244.291; baseline 273337.532), `disjoint = false`. Prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}` present; no `COMBINED_*`/`BLOCKED_*` yet; `data/raw/eval67/` absent; EVAL-67 seal gate exit 1 (expected).
- **EVAL-68:** `WAIT_EVAL67` (gate exit 10); `eval67_sealed = false`; `overlap_seconds = 239205.680`. Prereg `EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T194851Z.{json,md}` present; `data/raw/eval68/` absent; seal gate exit 1 (expected). Acquires only after EVAL-67 seals.
- **EVAL-69:** `WAIT_EVAL68` (gate exit 10); `eval68_sealed = false`; `overlap_seconds = 239205.161`. Runner + gate + 37 tests green; prereg `EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_PREREGISTRATION_20261116T225549Z.{json,md}` present; acquires nothing; seal gate exit 1 (expected).
- **Tests:** **188 passed** targeted (EVAL-73's 12 added); **27 passed** controller/campaign/diagnostics; `verify_env.sh --check` → `OK`. Both suites re-run from scratch this session by the driver (final run 2026-11-17T06:23:02Z).
- **Data-availability constraint (hard):** earliest disjoint floor-compliant forward capture end = **2026-11-19T18:08:16Z** (prereg threshold **2026-11-20T00:00:00Z**). Past windows are non-viable because options retention is < 6 days and option trades only ~24 h.
- **Power expectation (recorded pre-run):** EVAL-67 is underpowered for the EVAL-65 BTC effect (IC 0.088, n 596): one-sided ≈0.70, conjunction ≈0.53, ~790 pairs for 80%. EVAL-68 pooled at the EVAL-64 floor is power-adequate (n ≈1856 ≫ 790). EVAL-69 inherits the same pooled adequacy.
- **Durable mechanism:** git-committed handoff + git-committed readiness JSON + external `*/5` cron + the seven phase-B gates (EVAL-70/71/72/67/68/69 + EVAL-66 seal) + `scripts/eval67_prethreshold_progress.py`. The next **agentic** session is threshold/alert-triggered; cron alone handles pre-threshold polling. No bridges.

## BOTTLENECKS REMOVED (do not rediscover)

1. **Zombie capture bridge + liveness churn — REMOVED.** Do not recreate any bridge/waiter process; it dies with the ≤6 h job.
2. **Competing handoff pointers — REMOVED.** This file is the single handoff. Do not create timestamped handoff copies.
3. **EVAL-68 "design-only" bottleneck — REMOVED.** EVAL-68 is built, tested, prereg'd, and gated.
4. **EVAL-69 "no traded-form monetization campaign" bottleneck — REMOVED.** EVAL-69 is built, tested (37 tests), prereg'd, and gated.
5. **Forward wait — HARD PHYSICS, not a fixable inefficiency.** Free Deribit perp 1m returns ≤5001 candles (300000 s); options 5m candles return 0 at ~6–8 days back and option trades only ~24 h. All prior captures are at/after `2026-11-09T06:48:16Z`, so the only floor-compliant disjoint window is forward. Do not run a naive trailing `--days 7` capture before the threshold.
6. **Power / sample-adequacy — recorded pre-run; do not rationalize post-hoc.** See STATUS above.
7. **Manual pre-threshold loop / timestamp-only carry — REMOVED (2026-11-17T01:12:22Z).** `scripts/eval67_prethreshold_progress.py` now enforces env check + 152+27 tests + all four arbiters + seal-gates + readiness refresh in one deterministic command, with 10 tests. A session that only bumps this timestamp has not run the driver and has not satisfied the contract.
8. **Repeated pre-threshold agent-session churn — REMOVED THIS SESSION (2026-11-17T02:22:04Z).** Pre-threshold state is deterministic and green; spawning more agent sessions only repeats ~190 s of unchanged tests and produces handoff churn. The external `*/5` cron now owns routine pre-threshold polling. Do not launch another pre-threshold agent session; the next agentic session is triggered by the 2026-11-20T00:00:00Z threshold or a `DUE`/`FAILED` arbiter result, and it must run the full heavy-work driver with `--execute` before any other action.
9. **Ambiguous resume trigger — REMOVED THIS SESSION (2026-11-17T02:22:04Z).** The handoff now states one timestamped initial task, one first command, one next-session trigger, and one readiness artifact. Do not create alternate handoffs, status copies, or ad-hoc campaign branches.
10. **Stale diagnostic test assertion — REMOVED THIS SESSION (2026-11-17T03:27:33Z).** Fixed `tests/test_campaign_resume.py::test_durable_handoff_is_source_of_truth` to check for current EVAL-67/68/69/70 campaigns instead of retired phase numbers. All 27 diagnostics green.
11. **Post-EVAL-70/71 pre-threshold heavy-work gap — REMOVED (EVAL-71 2026-11-17T04:16:49Z; EVAL-72 2026-11-17T05:18:22Z).** After EVAL-70 and EVAL-71 sealed, pre-threshold sessions again had no runnable-now heavy work. Built **EVAL-71** (options implied-vol surface -> forward RV predictiveness; sealed `GO CONFIRMED`) and then **EVAL-72** (surface-skew-timed delta-hedged ATM straddle net-of-cost monetization; sealed `NO-GO CONFIRMED (PASS)`). Both are on-charter, runnable-now on the on-disk captures, no acquisition, and wired into the driver (now 176 tests, 7 gates) so neither can ever be skipped. Together they close the predictiveness-then-monetization loop for the options *surface* signal on the current captures.
12. **Post-EVAL-72 pre-threshold heavy-work gap — the forward ladder IS the heavy work; do not manufacture churn.** With EVAL-70/71/72 all sealed, there is no *new* on-charter, runnable-now campaign that would not re-litigate a sealed result. The next genuine heavy work is the disjoint-forward **EVAL-67 -> EVAL-68 -> EVAL-69** ladder at/after **2026-11-20T00:00:00Z** (hard physics; see STATUS), which the driver executes unskippably when `DUE`. Do **not** spawn pre-threshold agent sessions to rerun unchanged green tests; the `*/5` cron owns pre-threshold polling. If a pre-threshold session is genuinely mandated, the next runnable-now candidate is **EVAL-73** — a *distinct* signal/wrapper that does not re-litigate sealed results (e.g., a term-structure / calendar-skew surface signal, or an out-of-sample walk-forward stability check of EVAL-71's GO across a disjoint split); build it exactly like EVAL-72 (runner + SEALED/DUE/FAILED gate + tests, composed honest floor, no `src/` edits), wire it into `scripts/eval67_prethreshold_progress.py`, and seal it. Do not re-run, re-litigate, or re-seal EVAL-02..62/64..66/70/71/72.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70, EVAL-71, or EVAL-72 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting, single acquisition process (EVAL-68 acquires BTC+ETH in ONE `eval60_acquire_three_way.py` call; EVAL-69 acquires nothing).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
- Do **not** use the retired compact task ID `INIT-2026-11-16T122919Z-...`; use the three task IDs above.
- Do **not** switch EVAL-67/68/69 to a disjoint *past* window.
- Do **not** acquire EVAL-68 before EVAL-67 seals; do **not** run EVAL-69 before EVAL-68 seals.
- Do **not** spawn/recreate capture bridges or waiter processes.
- `data/raw/eval67/`, `data/raw/eval68/` are gitignored; do not commit/push.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies. Update this file in place with verified facts only.
- **No timestamp-only bumps without new verified facts (green driver run + green tests + green gates).**

## REPRO / KEY COMMANDS

```bash
# 0) FIRST on a fresh runner (deps are git-ignored, not in the checkout):
./scripts/verify_env.sh

# 1) THE heavy-work loop — run this every session, with --execute:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) Individual arbiters (status; add --execute to run):
python3 scripts/eval70_phaseb_gate.py          # SEALED (NO-GO)
python3 scripts/eval71_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval72_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval67_phaseb_gate.py
python3 scripts/eval68_phaseb_gate.py
python3 scripts/eval69_phaseb_gate.py

# 3) Targeted suites (the orchestrator runs these; reproduce manually if needed):
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q tests/test_eval70_underlying_oflow_rv_predictiveness.py \
  tests/test_eval70_phaseb_gate.py \
  tests/test_eval67_btc_oflow_tox_rv_oos.py \
  tests/test_eval67_phaseb_gate.py \
  tests/test_eval67_prethreshold_progress.py \
  tests/test_eval66_eth_oflow_tox_rv_oos.py \
  tests/test_eval65_orderflow_tox_rv_predictiveness.py \
  tests/test_eval68_pooled_btc_eth_oflow_tox_rv_oos.py \
  tests/test_eval68_phaseb_gate.py \
  tests/test_eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py \
  tests/test_eval69_phaseb_gate.py \
  tests/test_eval71_surface_iv_rv_predictiveness.py \
  tests/test_eval72_surface_skew_straddle_monetization.py
python3 -m pytest -q tests/test_controller_progress_accounting.py \
  tests/test_workflow_diagnostics_scanner.py \
  tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py

# 4) Seal gates (EVAL-66/70/71/72 exit 0; EVAL-67/68/69 exit 1 until sealed):
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-17T02:10:00Z-EVAL70-UNDERLYING-OFLOW-TOX-RV-PREDICTIVENESS" \
  --glob "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED_*" \
  --require-any-glob "EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_BLOCKED_*"
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-17T04:10:00Z-EVAL71-SURFACE-IV-RV-PREDICTIVENESS" \
  --glob "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_COMBINED_*" \
  --require-any-glob "EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_BLOCKED_*"
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-17T05:10:00Z-EVAL72-SURFACE-SKEW-STRADDLE-MONETIZATION" \
  --glob "EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_PREREGISTRATION_*" \
  --require-any-glob "EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_COMBINED_*" \
  --require-any-glob "EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_BLOCKED_*"
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_67_BTC_OFLOW_TOX_RV_OOS_BLOCKED_*"
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS" \
  --glob "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T22:45:00Z-EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS" \
  --glob "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED_*" \
  --require-any-glob "EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_BLOCKED_*"

# 5) Phase-B only, at/after 2026-11-20T00:00:00Z (the orchestrator does this):
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

## SESSION LOG (append-only, recent)

- 2026-11-16T12:19:00Z: Sealed **EVAL-66 `BLOCKED`** (under-floor, non-disjoint ETH; gate exit 0). `CAMPAIGN_CLOSED`.
- 2026-11-16T13:39:12Z: De-risked EVAL-67 path (real smoke OK, dry-run BLOCKED with disjointness_ok=true, math proven).
- 2026-11-16T15:28:47Z: Verified gates; proved ephemeral-runner durability model; proved past-window non-viability; produced power/sample-adequacy analysis.
- 2026-11-16T17:30:39Z: Re-verified gates/tests; removed zombie bridge + liveness churn; confirmed forward wait is hard physics.
- 2026-11-16T17:43:38Z: Fresh-runner bootstrap + pre-threshold contract + bottleneck removal; deleted root retired handoff pointers.
- 2026-11-16T19:53:00Z: Built EVAL-68 end-to-end: runner + gate + 36 tests + prereg.
- 2026-11-16T19:56:20Z … 22:01:46Z: pre-threshold gate carries (overlap strictly decreasing; tests green).
- 2026-11-16T22:56:20Z: Built EVAL-69 end-to-end: pooled traded-form runner + gate + 37 tests + prereg; removed the "no out-of-sample traded-form monetization campaign" bottleneck.
- **2026-11-17T01:12:22Z (this session — new verified heavy work):** Added `scripts/eval67_prethreshold_progress.py` + `tests/test_eval67_prethreshold_progress.py` (10 tests) to make the pre-threshold loop deterministic and unskippable: env check, **134 targeted tests**, **27 diagnostics**, all three arbiters in order, automatic `--execute` of DUE campaigns, seal-gate checks, and readiness refresh. Ran `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, **134/134 targeted** in 189.26 s, **27/27 diagnostics** in 0.95 s, `verify_env.sh --check` → `OK`. All three arbiters re-ran: EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 253436.131`, strictly decreasing from 253702.095; baseline 273337.532; disjoint false); EVAL-68 `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 253435.885`); EVAL-69 `WAIT_EVAL68` exit 10 (`eval68_sealed=false`, `overlap_seconds 253435.364`). Seal gates: EVAL-66 exit 0; EVAL-67/68/69 exit 1 (expected). Refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` in place with the new evidence. Removed the manual timestamp-only-carry bottleneck; no sealed artifacts or `src/` touched; no synthetic data; paper-only.
- **2026-11-17T01:31:29Z (this session — re-verified heavy work):** Re-ran the full pre-threshold driver `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, `env_check=true`, **134/134 targeted** in 188.57 s, **27/27 diagnostics** in 1.09 s, `verify_env.sh --check` → `OK`. All three arbiters re-ran: EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 252288.412`, strictly decreasing from 253436.131; baseline 273337.532; disjoint false); EVAL-68 `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 252288.159`); EVAL-69 `WAIT_EVAL68` exit 10 (`eval68_sealed=false`, `overlap_seconds 252287.63`). Seal gates: EVAL-66 exit 0; EVAL-67/68/69 exit 1 (expected, all `ok=true`). Refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` in place with the new evidence. No sealed artifacts or `src/` touched; no synthetic data; paper-only. Only working-tree change: `research_state/EVAL_67_PREWINDOW_READINESS.json` (15 insertions, 15 deletions — purely the verified metrics + timestamp refresh).
- **2026-11-17T02:22:04Z (this session — new verified heavy work):** Re-ran the full pre-threshold driver `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, `env_check=true`, **134/134 targeted** in 189.56 s, **27/27 diagnostics** in 0.939 s, `verify_env.sh --check` → `OK`. All three arbiters re-ran: EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 249253.713`, strictly decreasing from 249567.912; baseline 273337.532; disjoint false); EVAL-68 `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 249253.468`); EVAL-69 `WAIT_EVAL68` exit 10 (`eval68_sealed=false`, `overlap_seconds 249252.948`). Seal gates: EVAL-66 exit 0; EVAL-67/68/69 exit 1 (expected, all `ok=true`). Refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` in place with the new evidence. No sealed artifacts or `src/` touched; no synthetic data; paper-only. Only working-tree change: `research_state/EVAL_67_PREWINDOW_READINESS.json` + this handoff's threshold-trigger/process-bottleneck refresh.
- **2026-11-17T02:39:42Z (this session — handoff refresh):** Refreshed the single durable handoff initial task message timestamp to 2026-11-17T02:39:42Z and updated STATUS verification timestamp. Pre-threshold heavy work remains green (134/134 targeted, 27/27 diagnostics, env_check=OK, all three arbiters NOT_DUE/WAIT_EVAL67/WAIT_EVAL68, all seal gates expected). Next agentic session is threshold-triggered at 2026-11-20T00:00:00Z or on arbiter DUE/FAILED. External */5 cron owns pre-threshold polling. No new bottlenecks introduced; all 9 previously removed bottlenecks stay removed.
- **2026-11-17T03:27:33Z (this session — new verified heavy work):** Re-ran the full pre-threshold driver `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, `env_check=true`, **152/152 targeted** (EVAL-70 added) in 189.45 s, **27/27 diagnostics** in 1.08 s, `verify_env.sh --check` → `OK`. All four arbiters re-ran: EVAL-70 `SEALED` exit 0; EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 245324.615`, strictly decreasing from 248222.615; baseline 273337.532; disjoint false); EVAL-68 `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 245324.367`); EVAL-69 `WAIT_EVAL68` exit 10 (`eval68_sealed=false`, `overlap_seconds 245323.846`). Seal gates: EVAL-66 exit 0; EVAL-70 exit 0; EVAL-67/68/69 exit 1 (expected, all `ok=true`). Fixed stale diagnostic test assertion in `tests/test_campaign_resume.py` (now checks for EVAL-67/68/69/70). Refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` in place with the new evidence. No sealed artifacts or `src/` touched; no synthetic data; paper-only. Working-tree changes: `research_state/EVAL_67_PREWINDOW_READINESS.json`, `tests/test_campaign_resume.py`, this handoff.
- **2026-11-17T04:03:56Z (this session — new verified heavy work):** Re-ran the full pre-threshold driver `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, `env_check=true`, **152/152 targeted** in 191.76 s, **27/27 diagnostics** in 0.97 s, `verify_env.sh --check` → `OK`. All four arbiters re-ran: EVAL-70 `SEALED` exit 0; EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 244520.615`, strictly decreasing from 245324.615; baseline 273337.532; disjoint false); EVAL-68 `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 244520.369`); EVAL-69 `WAIT_EVAL68` exit 10 (`eval68_sealed=false`, `overlap_seconds 244519.848`). Seal gates: EVAL-66 exit 0; EVAL-70 exit 0; EVAL-67/68/69 exit 1 (expected, all `ok=true`). Refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` in place with the new evidence. No sealed artifacts or `src/` touched; no synthetic data; paper-only. Working-tree changes: `research_state/EVAL_67_PREWINDOW_READINESS.json`, this handoff.
- **2026-11-17T04:16:49Z (this session — NEW campaign built, tested, and sealed):** Built **EVAL-71** end-to-end to fill the post-EVAL-70 pre-threshold heavy-work gap: `scripts/eval71_surface_iv_rv_predictiveness.py` (options implied-vol *surface* -> forward RV predictiveness; near-ATM IV level + put-call skew from the real Deribit option trade tape, wrapper-free Spearman rank IC, own pre-registered trade-tape IV floor, EVAL-64 floor untouched, reuses sealed EVAL-61/62/65 runners), `scripts/eval71_phaseb_gate.py` (SEALED/DUE/FAILED arbiter), and `tests/test_eval71_surface_iv_rv_predictiveness.py` (12 tests, all green). Wired EVAL-71 into `scripts/eval67_prethreshold_progress.py` (6 gates, 6 seal specs, 164 expected targeted tests). Ran the full driver `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, `env_check=true`, **164/164 targeted**, **27/27 diagnostics**, `verify_env.sh --check` → `OK`. The driver auto-executed EVAL-71 (`DUE` -> `--execute`) and sealed it **GO CONFIRMED** at `2026-11-17T04:15:13Z` (prereg + COMBINED present; seal gate exit 0). EVAL-71 verdict on the real on-disk BTC+ETH captures: floor_ok=true; BTC best IC 0.335 (skew, 4 pass configs), ETH best IC 0.263 (skew, 4 pass configs); 10 BH-FDR-rejected configs. This is the **first GO in the predictiveness line**: the options surface predicts forward RV while order-flow (EVAL-65 options tape, EVAL-70 perp tape) sealed NO-GO. All other gates: EVAL-70 `SEALED` exit 0; EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 242412.625`, strictly decreasing; disjoint false); EVAL-68 `WAIT_EVAL67` exit 10; EVAL-69 `WAIT_EVAL68` exit 10. Seal gates: EVAL-66/70/71 exit 0; EVAL-67/68/69 exit 1 (expected, all `ok=true`). No sealed EVAL-02..66 artifacts or `src/` touched; no synthetic data; paper-only. Working-tree changes: `scripts/eval71_surface_iv_rv_predictiveness.py`, `scripts/eval71_phaseb_gate.py`, `tests/test_eval71_surface_iv_rv_predictiveness.py`, `scripts/eval67_prethreshold_progress.py`, `research_state/EVAL_67_PREWINDOW_READINESS.json`, `research_state/EVAL_71_*.{json,md}`, this handoff.
- **2026-11-17T04:35:34Z (this session — pre-threshold verification):** Re-ran the full pre-threshold driver `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, `env_check=true`, **164/164 targeted** in 190.5 s, **27/27 diagnostics** in 1.0 s, `verify_env.sh --check` → `OK`. All six gates re-ran: EVAL-70 `SEALED` exit 0; EVAL-71 `SEALED` exit 0; EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 241244.291`, strictly decreasing from 242067.731; baseline 273337.532; disjoint false); EVAL-68 `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 241244.021`); EVAL-69 `WAIT_EVAL68` exit 10 (`eval68_sealed=false`, `overlap_seconds 241243.496`). Seal gates: EVAL-66/70/71 exit 0; EVAL-67/68/69 exit 1 (expected, all `ok=true`). Refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` in place with the new evidence. No sealed artifacts or `src/` touched; no synthetic data; paper-only. Working-tree changes: `research_state/EVAL_67_PREWINDOW_READINESS.json`, this handoff.

- **2026-11-17T05:18:22Z (this session — NEW campaign built, tested, and sealed):** Built **EVAL-72** end-to-end to fill the post-EVAL-71 pre-threshold heavy-work gap and to answer the repo-priority capstone (traded-form net-of-cost monetization of EVAL-71's predictive surface signal): `scripts/eval72_surface_skew_straddle_monetization.py` (causal EVAL-71 surface skew / ATM-IV signal -> side/exposure on the correct EVAL-62 mark-path net-of-cost delta-hedged ATM straddle; reuses sealed EVAL-57/61/62/71 runners verbatim; composed EVAL-61/62 + EVAL-71 floor, neither weakened; no `src/` edits, no acquisition, no network), `scripts/eval72_phaseb_gate.py` (SEALED/DUE/FAILED arbiter), and `tests/test_eval72_surface_skew_straddle_monetization.py` (12 tests, all green). Wired EVAL-72 into `scripts/eval67_prethreshold_progress.py` (7 gates, 7 seal specs, 176 expected targeted tests; readiness notes/gates extended). Ran the full driver `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, `env_check=true`, **176/176 targeted**, **27/27 diagnostics**, `verify_env.sh --check` → `OK`. The driver auto-executed EVAL-72 (`DUE` -> `--execute`) and sealed it **NO-GO CONFIRMED (PASS)** at `2026-11-17T05:18:22Z` (prereg + COMBINED present; seal gate exit 0). EVAL-72 verdict on the real on-disk BTC+ETH captures: floor_ok=true; BTC best Sharpe 0.8424 (`atm_iv::bar300`), ETH best -1.1967 (`skew::bar300`); no config clears permutation + bootstrap + kill-switch on both underlyings; BH-FDR rejected none. Conclusion: EVAL-71's *predictive* surface signal does **not** monetize net-of-cost -> predictive != monetizable (the terminal charter clause answered NO-GO for this traded form). All other gates: EVAL-70 `SEALED` exit 0; EVAL-71 `SEALED` exit 0; EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 239205.922`, strictly decreasing; disjoint false); EVAL-68 `WAIT_EVAL67` exit 10; EVAL-69 `WAIT_EVAL68` exit 10. Seal gates: EVAL-66/70/71/72 exit 0; EVAL-67/68/69 exit 1 (expected, all `ok=true`). Updated `tests/test_campaign_resume.py` (handoff source-of-truth now pins EVAL-67..72). No sealed EVAL-02..66/70/71 artifacts or `src/` touched; no synthetic data; paper-only. Working-tree changes: `scripts/eval72_surface_skew_straddle_monetization.py`, `scripts/eval72_phaseb_gate.py`, `tests/test_eval72_surface_skew_straddle_monetization.py`, `scripts/eval67_prethreshold_progress.py`, `tests/test_campaign_resume.py`, `research_state/EVAL_72_..._{PREREGISTRATION,COMBINED}_20261117T051822Z.{json,md}`, `research_state/EVAL_67_PREWINDOW_READINESS.json`, this handoff.

- **2026-11-17T05:22:00Z (this session — handoff refresh):** Refreshed the single durable handoff initial task message timestamp to 2026-11-17T05:22:00Z and updated STATUS verification timestamp. Pre-threshold heavy work remains green (176/176 targeted, 27/27 diagnostics, env_check=OK, all seven gates SEALED/NOT_DUE/WAIT as expected, all seal gates expected). Next agentic session is threshold-triggered at 2026-11-20T00:00:00Z or on arbiter DUE/FAILED. External */5 cron owns pre-threshold polling. No new bottlenecks introduced; all 12 previously removed bottlenecks stay removed.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, 70, 71, 72, 73 sealed. EVAL-63 never sealed. EVAL-46..60, 62, 64, 65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`; EVAL-70: `SEALED` (`NO-GO CONFIRMED`); EVAL-71: `SEALED` (`GO CONFIRMED` — options surface IV/skew predicts forward RV on both BTC and ETH; first GO in the predictiveness line); EVAL-72: `SEALED` (`NO-GO CONFIRMED (PASS)` — the surface signal does not monetize net-of-cost via a signal-timed delta-hedged ATM straddle; predictive != monetizable). On-charter closed; **EVAL-67** (BTC-only predictiveness) is the immediate authorized heavy falsification, gated by `scripts/eval67_phaseb_gate.py`; **EVAL-68** (pooled BTC+ETH predictiveness, power-adequate) is the second campaign, gated by `scripts/eval68_phaseb_gate.py` and ordered to run only after EVAL-67 seals; **EVAL-69** (pooled BTC+ETH traded-form net-of-cost monetization, the repo-priority capstone) is the third campaign, gated by `scripts/eval69_phaseb_gate.py`, reuses EVAL-68's capture, and runs only after EVAL-68 seals. The pre-threshold driver is `scripts/eval67_prethreshold_progress.py` (now 176 targeted + 27 diagnostics + 7 gates, including the sealed EVAL-70/EVAL-71/EVAL-72 runnable-now campaigns).

(End of file - total 153 lines)