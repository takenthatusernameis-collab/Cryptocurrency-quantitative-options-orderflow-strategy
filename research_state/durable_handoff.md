# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-17T01:12:22Z — RUN THE HEAVY-WORK DRIVER FIRST; EVAL-67 `NOT_DUE` exit 10, EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10; timestamp-only carry is forbidden):**
>
> **FIRST ACTION, non-negotiable:** run
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> That one command performs the full pre-threshold heavy-work loop: environment check, the **134 targeted tests**, the **27 controller/campaign/diagnostics tests**, all three campaign arbiters in ladder order, automatic `--execute` of any campaign that reports `DUE`, seal-gate checks, and an in-place refresh of `research_state/EVAL_67_PREWINDOW_READINESS.json`. **Do not exit the session until it exits 0.**
>
> **Repo-priority reading of `Cryptocurrency-quantitative-options-orderflow-strategy`:** the thesis is *crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data*. The on-charter ladder EVAL-02..66 is **CLOSED** (EVAL-66 sealed `BLOCKED`, seal-gate exit 0). Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/EVAL-64..66 artifacts or `src/`. Never synthetic data, never weaken the EVAL-64 floor, paper-only.

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
- `targeted_tests: 134/134`
- `diagnostic_tests: 27/27`
- `gates`: EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` (pre-threshold)
- `overall_ok: true`, exit code 0

If it reports `exit_code: 20`, a campaign is `DUE`: re-run with `--execute`. If it reports `exit_code: 1`, fix the reported failed step and re-run. Do not replace this loop with a timestamp-only handoff bump.

## STATUS (verified 2026-11-17T01:12:22Z)

- **EVAL-67:** `NOT_DUE` (gate exit 10) at `2026-11-17T01:12:19Z`; `overlap_seconds = 253436.131` (strictly decreasing; baseline 273337.532), `disjoint = false`. Prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}` present; no `COMBINED_*`/`BLOCKED_*` yet; `data/raw/eval67/` absent; EVAL-67 seal gate exit 1 (expected).
- **EVAL-68:** `WAIT_EVAL67` (gate exit 10); `eval67_sealed = false`; `overlap_seconds = 253435.885`. Prereg `EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T194851Z.{json,md}` present; `data/raw/eval68/` absent; seal gate exit 1 (expected). Acquires only after EVAL-67 seals.
- **EVAL-69:** `WAIT_EVAL68` (gate exit 10); `eval68_sealed = false`; `overlap_seconds = 253435.364`. Runner + gate + 37 tests green; prereg `EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_PREREGISTRATION_20261116T225549Z.{json,md}` present; acquires nothing; seal gate exit 1 (expected).
- **Tests:** **134 passed** targeted (124 prior + 10 new orchestrator tests) in 189.26 s; **27 passed** controller/campaign/diagnostics in 0.95 s; `verify_env.sh --check` → `OK`. Both suites were re-run from scratch this session.
- **Data-availability constraint (hard):** earliest disjoint floor-compliant forward capture end = **2026-11-19T18:08:16Z** (prereg threshold **2026-11-20T00:00:00Z**). Past windows are non-viable because options retention is < 6 days and option trades only ~24 h.
- **Power expectation (recorded pre-run):** EVAL-67 is underpowered for the EVAL-65 BTC effect (IC 0.088, n 596): one-sided ≈0.70, conjunction ≈0.53, ~790 pairs for 80%. EVAL-68 pooled at the EVAL-64 floor is power-adequate (n ≈1856 ≫ 790). EVAL-69 inherits the same pooled adequacy.
- **Durable mechanism:** git-committed handoff + git-committed readiness JSON + external `*/5` cron + the three phase-B gates + `scripts/eval67_prethreshold_progress.py`. No bridges.

## BOTTLENECKS REMOVED (do not rediscover)

1. **Zombie capture bridge + liveness churn — REMOVED.** Do not recreate any bridge/waiter process; it dies with the ≤6 h job.
2. **Competing handoff pointers — REMOVED.** This file is the single handoff. Do not create timestamped handoff copies.
3. **EVAL-68 “design-only” bottleneck — REMOVED.** EVAL-68 is built, tested, prereg’d, and gated.
4. **EVAL-69 “no traded-form monetization campaign” bottleneck — REMOVED.** EVAL-69 is built, tested (37 tests), prereg’d, and gated.
5. **Forward wait — HARD PHYSICS, not a fixable inefficiency.** Free Deribit perp 1m returns ≤5001 candles (300000 s); options 5m candles return 0 at ~6–8 days back and option trades only ~24 h. All prior captures are at/after `2026-11-09T06:48:16Z`, so the only floor-compliant disjoint window is forward. Do not run a naive trailing `--days 7` capture before the threshold.
6. **Power / sample-adequacy — recorded pre-run; do not rationalize post-hoc.** See STATUS above.
7. **Manual pre-threshold loop / timestamp-only carry — REMOVED THIS SESSION (2026-11-17T01:12:22Z).** `scripts/eval67_prethreshold_progress.py` now enforces env check + 134+27 tests + all three arbiters + seal-gates + readiness refresh in one deterministic command, with 10 tests. A session that only bumps this timestamp has not run the driver and has not satisfied the contract.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62 or EVAL-64..66 artifacts or `src/`. Append-only for new authorized work.
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

# 2) Individual arbiters (status; add --execute at/after threshold):
python3 scripts/eval67_phaseb_gate.py
python3 scripts/eval68_phaseb_gate.py
python3 scripts/eval69_phaseb_gate.py

# 3) Targeted suites (the orchestrator runs these; reproduce manually if needed):
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q tests/test_eval67_btc_oflow_tox_rv_oos.py \
  tests/test_eval67_phaseb_gate.py \
  tests/test_eval67_prethreshold_progress.py \
  tests/test_eval66_eth_oflow_tox_rv_oos.py \
  tests/test_eval65_orderflow_tox_rv_predictiveness.py \
  tests/test_eval68_pooled_btc_eth_oflow_tox_rv_oos.py \
  tests/test_eval68_phaseb_gate.py \
  tests/test_eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py \
  tests/test_eval69_phaseb_gate.py
python3 -m pytest -q tests/test_controller_progress_accounting.py \
  tests/test_workflow_diagnostics_scanner.py \
  tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py

# 4) Seal gates (EVAL-66 exit 0; EVAL-67/68/69 exit 1 until sealed):
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-16T11:32:21Z-EVAL66-ETH-OFLOW-TOX-RV-OOS-REPLICATION" \
  --glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_COMBINED_*" \
  --require-any-glob "EVAL_66_ETH_OFLOW_TOX_RV_OOS_BLOCKED_*"
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
- 2026-11-16T22:56:20Z: Built EVAL-69 end-to-end: pooled traded-form runner + gate + 37 tests + prereg; removed the “no out-of-sample traded-form monetization campaign” bottleneck.
- **2026-11-17T01:12:22Z (this session — new verified heavy work):** Added `scripts/eval67_prethreshold_progress.py` + `tests/test_eval67_prethreshold_progress.py` (10 tests) to make the pre-threshold loop deterministic and unskippable: env check, **134 targeted tests**, **27 diagnostics**, all three arbiters in order, automatic `--execute` of DUE campaigns, seal-gate checks, and readiness refresh. Ran `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, **134/134 targeted** in 189.26 s, **27/27 diagnostics** in 0.95 s, `verify_env.sh --check` → `OK`. All three arbiters re-ran: EVAL-67 `NOT_DUE` exit 10 (`overlap_seconds 253436.131`, strictly decreasing from 253702.095; baseline 273337.532; disjoint false); EVAL-68 `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, `overlap_seconds 253435.885`); EVAL-69 `WAIT_EVAL68` exit 10 (`eval68_sealed=false`, `overlap_seconds 253435.364`). Seal gates: EVAL-66 exit 0; EVAL-67/68/69 exit 1 (expected). Refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` in place with the new evidence. Removed the manual timestamp-only-carry bottleneck; no sealed artifacts or `src/` touched; no synthetic data; paper-only.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66 sealed. EVAL-63 never sealed. EVAL-46..60, 62, 64, 65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`. Superseded legacy phase campaigns (through Phase 110) are sealed and **non-actionable**. On-charter closed; **EVAL-67** (BTC-only predictiveness) is the immediate authorized heavy falsification, gated by `scripts/eval67_phaseb_gate.py`; **EVAL-68** (pooled BTC+ETH predictiveness, power-adequate) is the second campaign, gated by `scripts/eval68_phaseb_gate.py` and ordered to run only after EVAL-67 seals; **EVAL-69** (pooled BTC+ETH traded-form net-of-cost monetization, the repo-priority capstone) is the third campaign, gated by `scripts/eval69_phaseb_gate.py`, reuses EVAL-68's capture, and runs only after EVAL-68 seals. The pre-threshold driver is `scripts/eval67_prethreshold_progress.py`.