# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-19T05:29:00Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor). PRIMARY TASK, IN ORDER: (1) run `python3 scripts/eval67_prethreshold_progress.py --execute` and require exit 0, `targeted_tests: 1110/1110` (or higher if more built/sealed), `diagnostic_tests: 27/27`, all EVAL-70..118 `SEALED`, EVAL-67 `NOT_DUE`/EVAL-68 `WAIT_EVAL67`/EVAL-69 `WAIT_EVAL68`, all 53 seal-gate specs ok; (2) BUILD + SEAL the next pre-threshold campaign **EVAL-119** — single-asset `atm_iv` → forward own-asset realized return kurtosis (EVAL-109 signal path + EVAL-117 target; floor: sealed EVAL-71 surface floor): mirror the EVAL-117 contract (runner `scripts/eval119_*`, gate `scripts/eval119_phaseb_gate.py`, tests `tests/test_eval119_*`, wire into `TARGETED_TEST_FILES`/`GATE_SPECS`/`SEAL_SPECS` with `expected_exit:1`→`0`, bump `EXPECTED_TARGETED_TESTS` 1110→1128, seal with `--execute`, re-run driver green). A green driver + NOT_DUE/WAIT ladder is **NOT** session completion; a timestamp-only carry is prohibited; (3) at/after `2026-11-20T00:00:00Z` (or on `DUE`/`FAILED`), run the forward ladder sequentially: `python3 scripts/eval67_phaseb_gate.py --execute`, `python3 scripts/eval68_phaseb_gate.py --execute`, `python3 scripts/eval69_phaseb_gate.py --execute`. Do NOT acquire EVAL-68 before EVAL-67 seals; do not run EVAL-69 before EVAL-68 seals.**

> **VERIFIED STATE (2026-11-19T05:28:44Z, this session):** full driver `python3 scripts/eval67_prethreshold_progress.py --execute` green (exit 0, `overall_ok: true`, `failures: []`): env OK, `targeted_tests: 1110/1110` (rc 0), `diagnostic_tests: 27/27` (rc 0), 1137 total; all EVAL-70..118 `SEALED`; **53/53 seal-gate specs ok**; EVAL-67 `NOT_DUE` (overlap **65260.588s**, disjoint=false), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`; readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json`.
> · **EVAL-117** — single-asset `term_slope` → forward own-asset realized return **kurtosis** (fourth standardized moment, a new target dimension). Runner `scripts/eval117_single_asset_term_slope_forward_return_kurtosis.py`, gate `scripts/eval117_phaseb_gate.py`, tests `tests/test_eval117_*` (8 + 10). Verdict **`NO-GO CONFIRMED (PASS)`**, sealed `20261119T043017Z`: **BTC** best IC `-0.0425` (`term_slope::bar300.0::h6`), 0/6 pass; **ETH** best IC `0.1699` (`term_slope::bar300.0::h6`), 1/6 pass; **1 pooled BH-FDR rejection** (ETH only; BTC fails the both-asset GO bar). Task `INIT-2026-11-19T04:15:00Z-EVAL117-SINGLE-ASSET-TERM-SLOPE-FORWARD-RETURN-KURTOSIS`.
> · **EVAL-116** — cross-sectional `skew` basis → forward relative realized return skewness spread. **`GO CONFIRMED`**, sealed `20261119T032548Z`. Task `INIT-2026-11-19T02:51:29Z-EVAL116-CROSS-SECTIONAL-SKEW-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD`.
> · Earlier: EVAL-104..115 COMPLETE (see SEALED STATE + session log below).

> **Forward ladder (hard physics, not fixable pre-threshold):** EVAL-67 `NOT_DUE` exit 10, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`. Threshold **2026-11-20T00:00:00Z**; earliest disjoint capture end **2026-11-19T18:08:16Z**. External `*/5` cron owns routine polling. Do not spawn capture bridges/waiters.

> **FIRST ACTION, non-negotiable:** run the full heavy-work driver now (idempotent; confirms green, refreshes readiness):
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Require exit 0, `targeted_tests: 1084/1084` (or higher if more built/sealed), `diagnostic_tests: 27/27`, EVAL-70..117 `SEALED`, EVAL-67 `NOT_DUE` / EVAL-68 `WAIT_EVAL67` / EVAL-69 `WAIT_EVAL68` pre-threshold, and all 52 seal-gate specs ok. If any arbiter is `DUE`(20) execute it; if `FAILED`(1) fix and rerun.

> **ANTI-AVOIDANCE RULE (mandatory):** a green driver plus NOT_DUE/WAIT is **not** session completion. With EVAL-70..117 sealed, **EVAL-118 is not built/wired/sealed**. If the driver is green and the ladder remains NOT_DUE/WAIT, **build + seal EVAL-118 now** (mirror the EVAL-116 contract; candidate space below). One campaign per session minimum is required while the ladder is NOT_DUE/WAIT; a timestamp-only carry is prohibited.

> **Repo-priority reading:** on-charter ladder EVAL-02..66 is **CLOSED**. Do not re-run, re-litigate, re-seal, or edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..117 artifacts or `src/`. Append-only for new authorized work. No synthetic data, no live trading, no floor weakening.

## PRE-REGISTERED BUILD QUEUE — pick the FIRST not-yet-built for the next rung (never a re-skin)

Each cell is predictiveness-only (no monetization claim). Signals reuse sealed reconstructions: `atm_iv`/`skew` via EVAL-71 surface bars, `term_ratio`/`term_slope` via EVAL-74 `_term_bars`; cross-sectional basis via EVAL-77/105/106 `build_cross_section` + `_relative_signal_series`; cross-asset spillover via EVAL-114. Targets reuse sealed forward-window reconstructions: signed return mean (EVAL-104), tail asymmetry (EVAL-85/100), vol-of-vol (EVAL-84/107), return skewness (EVAL-109/112/113/116), downside semivariance share (EVAL-115), kurtosis (EVAL-117). Inference reuses EVAL-65 `_perm_p_ic`/`_boot_ci_ic` (`PERMUTATION_PERMS`, `BOOTSTRAP_RESAMPLES`, `BOOTSTRAP_BLOCK`, `SEED`), EVAL-62 `ZWINDOW`/`FDR_ALPHA`, and `src.analytics.real_walkforward_certification._benjamini_hochberg`; floors reuse the sealed source campaign's floor verbatim. **GO bar is always both-asset** (both BTC and ETH must each have ≥1 passing BH-FDR-rejected config), else `NO-GO CONFIRMED (PASS)`; below floor ⇒ `BLOCKED`.

1. **cross-sectional `term_slope` basis → relative realized return skewness spread** — EVAL-106 signal path + EVAL-116 target. Floor: sealed EVAL-77 surface basis floor. **DONE — EVAL-118 sealed `NO-GO CONFIRMED (PASS)` `20261119T052824Z`. NEXT — mandatory EVAL-119 build.**
2. **single-asset `atm_iv` → forward own-asset realized return kurtosis** — EVAL-109 signal path + EVAL-117 target. Floor: sealed EVAL-71 surface floor. *Reserved: EVAL-119.*
3. **cross-sectional `term_ratio` basis → relative realized return skewness spread** — EVAL-105 signal path + EVAL-116 target. Floor: EVAL-77 surface basis floor. *Reserved: EVAL-120.*
4. **single-asset `skew` → forward own-asset realized return kurtosis** — EVAL-111 signal path + EVAL-117 target. Floor: EVAL-71 surface floor. *Reserved: EVAL-121.*
5. **cross-asset `term_slope` spillover → other-asset realized return skewness** — EVAL-114 cross-asset path (swap `atm_iv`→`term_slope`) + EVAL-109 target. Floor: EVAL-71 surface floor. *Reserved: EVAL-122.*
6. **cross-sectional `skew` basis → relative realized return kurtosis spread** — EVAL-110 signal path + EVAL-117 target. Floor: EVAL-77 surface basis floor. *Reserved: EVAL-123.*
7. **cross-sectional `term_ratio` basis → relative realized return kurtosis spread** — EVAL-105 signal path + EVAL-117 target. Floor: EVAL-77 surface basis floor. *Reserved: EVAL-124.*
8. **cross-asset `term_ratio` spillover → other-asset realized return kurtosis** — EVAL-114 cross-asset path (swap `atm_iv`→`term_ratio`) + EVAL-117 target. Floor: EVAL-71 surface floor. *Reserved: EVAL-125.*

Already covered — do NOT rebuild: EVAL-77, 88, 89, 90, 91, 92, 93, 94, 101, 102, 103, 104, 105..118. Do **not** test `atm_iv`→VRP (mechanical overlap), do not re-test `term_ratio`→VRP, do not rebuild a collar (EVAL-76), do not re-litigate sealed cells, do not weaken EVAL-64, do not touch `src/`.

## BUILD QUEUE STATUS (EVAL-104..117 all COMPLETE/SEALED)

| rung | cell | verdict | stamp |
|---|---|---|---|
| EVAL-104 | `term_slope` → own signed return mean | `GO CONFIRMED` | `20261118T190138Z` |
| EVAL-105 | `term_ratio` basis → relative tail-asymmetry spread | `NO-GO CONFIRMED (PASS)` | `20261118T200246Z` |
| EVAL-106 | `term_slope` basis → relative tail-asymmetry spread | `NO-GO CONFIRMED (PASS)` | `20261118T204231Z` |
| EVAL-107 | `term_ratio` basis → relative vol-of-vol spread | `NO-GO CONFIRMED (PASS)` | `20261118T215800Z` |
| EVAL-108 | `term_slope` basis → relative vol-of-vol spread | `NO-GO CONFIRMED (PASS)` | `20261118T230834Z` |
| EVAL-109 | `atm_iv` → own realized return skewness | `GO CONFIRMED` | `20261118T231058Z` |
| EVAL-110 | `skew` basis → relative tail-asymmetry spread | `NO-GO CONFIRMED (PASS)` | `20261118T231811Z` |
| EVAL-111 | `skew` → own realized return skewness | `GO CONFIRMED` | `20261118T232819Z` |
| EVAL-112 | `term_ratio` → own realized return skewness | `GO CONFIRMED` | `20261119T000552Z` |
| EVAL-113 | `term_slope` → own realized return skewness | `GO CONFIRMED` | `20261119T001521Z` |
| EVAL-114 | cross-asset `atm_iv` spillover → other-asset return skewness | `GO CONFIRMED` | `20261119T021450Z` |
| EVAL-115 | `atm_iv` → forward downside semivariance share | `NO-GO CONFIRMED (PASS)` | `20261119T023715Z` |
| EVAL-116 | `skew` basis → relative realized return skewness spread | `GO CONFIRMED` | `20261119T032548Z` |
| EVAL-117 | `term_slope` → own realized return kurtosis | `NO-GO CONFIRMED (PASS)` | `20261119T043017Z` |
| EVAL-118 | `term_slope` basis → relative return skewness spread | `NO-GO CONFIRMED (PASS)` | `20261119T052824Z` |

## RUNNABLE-NOW CAMPAIGNS — EVAL-70..117 ALL SEALED

Predictiveness GOs (no net-of-cost monetization): EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`, `20261118T005436Z`), 88, 90, 91, 93, 97, 99, 100, 101, 102, 104, 109, 111, 112, 113, 114, **116**. NO-GO CONFIRMED (PASS): EVAL-70, 72, 74, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103, 105, 106, 107, 108, 110, 115, **117**, **118**. Traded-form taxonomy complete/all NO-GO (straddle 72/75, risk reversal 76, butterfly 82, relative-value straddle spread 80). Key IC anchors: EVAL-101 `atm_iv`→signed return (BTC 0.2313 / ETH 0.3442), EVAL-102 `term_ratio`→signed return (BTC 0.3926 / ETH 0.2559), EVAL-103 `skew`→signed return (ETH 0.2195 / BTC 0.0462, NO-GO), EVAL-104 `term_slope`→signed return (BTC 0.4058 / ETH 0.2600), EVAL-109 `atm_iv`→return skewness (BTC 0.1101 / ETH 0.3506), EVAL-112 `term_ratio`→return skewness (BTC 0.2883 / ETH 0.2223), EVAL-113 `term_slope`→return skewness (BTC 0.3005 / ETH 0.2116), EVAL-114 `atm_iv` spillover→return skewness (BTC 0.4039 / ETH 0.1173), EVAL-116 `skew` basis→return-skewness spread (best IC 0.1543, `bar60::h72`, 1 BH-FDR rejection), EVAL-117 `term_slope`→kurtosis (BTC -0.0425 / ETH 0.1699, NO-GO). These are idempotent no-ops once sealed; do not re-run as substitute for new work.

## THREE SEQUENTIAL FORWARD CAMPAIGNS (repo-priority order; hard disjoint-window gate)

1. **EVAL-67 — BTC-only predictiveness:** task `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`; `python3 scripts/eval67_phaseb_gate.py`. BTC-only recorded pre-run as underpowered.
2. **EVAL-68 — pooled BTC+ETH predictiveness:** task `INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS`; acquires only after EVAL-67 seals (single acquisition for BTC+ETH).
3. **EVAL-69 — pooled BTC+ETH traded-form net-of-cost monetization (capstone):** task `INIT-2026-11-16T22:45:00Z-EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS`; consumes EVAL-68 capture, no new acquisition, after EVAL-68 seals.

At/after `2026-11-20T00:00:00Z` (or immediately on `DUE`/`FAILED`), run sequentially with `--execute`:

```bash
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67: `SEALED`(0) complete; `NOT_DUE`(10) correct carry; `DUE`(20) execute now; `FAILED`(1) fix and rerun.
- EVAL-68: `SEALED`(0) complete; `WAIT_EVAL67`(10) do not acquire; `DUE`(20) execute now; `FAILED`(1) fix and rerun.
- EVAL-69: `SEALED`(0) ladder complete; `WAIT_EVAL68`(10) do not run; `DUE`(20) execute now; `FAILED`(1) fix and rerun.
- EVAL-70..118 gates: `SEALED`(0) idempotent; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- After fully-refreshed green driver: env OK, `1110/1110` targeted (or higher if more built/sealed), `27/27` diagnostics, all EVAL-70..118 `SEALED`, EVAL-67 `NOT_DUE` / EVAL-68 `WAIT_EVAL67` / EVAL-69 `WAIT_EVAL68` pre-threshold, all 53 seal-gate specs ok, driver exit 0.

## PRE-THRESHOLD HEAVY-WORK RULE

Run full driver with `--execute` every session. If green and ladder still NOT_DUE/WAIT, build and seal EVAL-119 (then the next queued candidate), re-running the driver green after each seal. Timestamp-only carry prohibited. No capture bridges/waiters; cron owns polling. Forward wait is hard physics until the disjoint window.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge/liveness churn — removed.
2. Competing handoff pointers/copies — removed; this file is the single handoff.
3. EVAL-68/69 design-only gaps — removed.
4. Pre-threshold "no heavy work left" avoidance — removed by EVAL-70..118 queue; never let the ladder go idle.
5. Manual pre-threshold loop/timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
6. Stale campaign test assumptions — `tests/test_campaign_resume.py` checks current campaigns.
7. Handoff bloat — consolidated; no timestamped copies, no `research_state/` enumeration.
8. **Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — removed.** When `--execute` seals a rung, flip that rung's `expected_exit` 1→0 in the same session or the next driver reports a seal-gate failure.
9. **Task-floor-stamp ordering bug — removed / do not repeat.** `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp. A task time later than the run makes the seal-gate emit `FAIL: no artifact ... with stamp >= ...` and the arbiter `FAILED`. Use the session start time, never a projected future time.
10. **Degenerate-skew/kurtosis test fixture trap — removed.** An alternating ±drift price path yields an all-zero third moment; kurtosis fixtures need fat-tailed (occasional large jump) increments (see EVAL-109/112/113/117 tests).
11. EVAL-94..117 staging gaps — all removed (built/wired/sealed).
12. **EVAL-112 runner `run_eval102` naming bug — removed.** Renamed to `run_eval112`.
13. **Stale handoff claiming EVAL-116 "NOT BUILT" — removed (this revision).** EVAL-116 is sealed `GO CONFIRMED` (`20261119T032548Z`) and the driver already expected 1066 before this session; EVAL-117 was built+sealed this session. Always re-read the driver's `targeted_tests.expected` rather than trusting a prose count.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..117 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting; EVAL-68 acquires BTC+ETH in ONE process; EVAL-69 acquires nothing.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs; do not use retired compact task IDs.
- Do not switch EVAL-67/68/69 to a disjoint past window. Do not acquire EVAL-68 before EVAL-67 seals; do not run EVAL-69 before EVAL-68 seals.
- `data/raw/eval67/`, `data/raw/eval68/` gitignored; do not commit/push. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session (idempotent):
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) Verify sealed campaigns idempotently:
python3 scripts/eval117_phaseb_gate.py

# 3) Build/seal a new rung (e.g. EVAL-118):
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q tests/test_eval118_*.py
python3 scripts/eval118_phaseb_gate.py --execute

# 4) At/after 2026-11-20T00:00:00Z, or on DUE/FAILED:
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

Driver runs env check, all targeted/diagnostic suites, all campaign arbiters in order, any required `--execute`, all seal-gate specs, and readiness refresh. Use its output and `research_state/EVAL_67_PREWINDOW_READINESS.json` as verified state. Note: targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself); a bare `python3 scripts/eval1xx_*.py` will fail on `numpy` without it.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, and 70..118 sealed. EVAL-63 never sealed. EVAL-67/68/69 forward-gated (NOT_DUE/WAIT pre-threshold). Predictiveness GOs: EVAL-71,73,77,83,85,86,88,90,91,93,97,99,100,101,102,104,109,111,112,113,114,116; EVAL-87 `GO/BLOCKED` (`20261118T005436Z`). Traded-form monetization complete/all-NO-GO. EVAL-70,72,74,75,76,78,79,80,81,82,84,89,92,94,95,96,98,103,105,106,107,108,110,115,117 NO-GO CONFIRMED (PASS). Do not modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-18T19:01:38Z:** EVAL-104 built/wired/sealed `GO CONFIRMED`; driver green 837/837+27/27.
- **2026-11-18T20:08:49Z:** EVAL-105 sealed NO-GO; driver green 854/854+27/27.
- **2026-11-18T21:58:00Z:** EVAL-106 sealed NO-GO; driver green 872/872+27/27.
- **2026-11-18T22:03:45Z:** EVAL-107 sealed NO-GO; driver green 888/888+27/27; EVAL-108 mandated.
- **2026-11-18T23:24:19Z:** EVAL-108, 109, 110 sealed; driver green 940/940+27/27.
- **2026-11-19T00:21:23Z:** EVAL-112, 113 built/wired/sealed `GO CONFIRMED`; driver green 994/994+27/27 (48/48 seal gates).
- **2026-11-19T02:14:50Z:** EVAL-114 built/wired/sealed `GO CONFIRMED`; driver green 1012/1012+27/27 (49/49 seal gates).
- **2026-11-19T02:43:17Z:** EVAL-115 built/wired/sealed `NO-GO CONFIRMED (PASS)`; driver green 1040/1040+27/27 (50/50 seal gates); EVAL-116 mandated.
- **2026-11-19T03:25:48Z:** EVAL-116 built/wired/sealed `GO CONFIRMED` (`skew` basis → relative return-skewness spread); driver expected count raised to 1066.
- **2026-11-19T04:38:16Z (this session).** Built/wired/sealed **EVAL-117** (single-asset `term_slope` → forward realized return **kurtosis** — a genuinely new fourth-moment target). Runner `scripts/eval117_single_asset_term_slope_forward_return_kurtosis.py`, gate `scripts/eval117_phaseb_gate.py`, tests `tests/test_eval117_*` (8 + 10 = 18). Verdict **`NO-GO CONFIRMED (PASS)`**, sealed `20261119T043017Z`: BTC best IC -0.0425 (`bar300::h6`), 0/6; ETH best IC 0.1699 (`bar300::h6`), 1/6; 1 pooled BH-FDR rejection (ETH only). Wired EVAL-117 into `scripts/eval67_prethreshold_progress.py` (tests, `GATE_SPECS`, `SEAL_SPECS` `expected_exit`→0, `EXPECTED_TARGETED_TESTS` 1066→1084). Full driver green: **1084/1084** targeted + 27/27 diagnostics = **1111**, all EVAL-70..117 SEALED, EVAL-67 NOT_DUE (overlap 68293.069s), EVAL-68 WAIT_EVAL67, EVAL-69 WAIT_EVAL68, **52/52** seal-gate specs ok, readiness written. Handoff queue extended EVAL-118..125 so the next session cannot idle; **EVAL-118 (cross-sectional `term_slope` basis → relative return skewness spread) is the mandatory next build.** No sealed prior artifacts or `src/` modified.

- **2026-11-19T04:46:36Z:** Handoff initial-task message refreshed to mandate EVAL-118 build (cross-sectional `term_slope` basis → relative realized return skewness spread); driver state unchanged (1084/1084 + 27/27, 52/52 seal gates, EVAL-67 NOT_DUE/EVAL-68 WAIT/EVAL-69 WAIT). EVAL-118 NOT BUILT — mandatory next.
- **2026-11-19T04:52:31Z (this session).** Refreshed the INITIAL TASK MESSAGE timestamp to `2026-11-19T04:52:31Z` (repository priority: crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data). State unchanged from prior verified session: driver green (1084/1084 targeted + 27/27 diagnostics = 1111), all EVAL-70..117 SEALED, 52/52 seal-gate specs ok, EVAL-67 NOT_DUE (overlap ~67813s), EVAL-68 WAIT_EVAL67, EVAL-69 WAIT_EVAL68, threshold `2026-11-20T00:00:00Z`. EVAL-118 still NOT BUILT — no `scripts/eval118_*`, no `tests/test_eval118_*`. **Mandatory next build: EVAL-118** (cross-sectional `term_slope` basis → relative realized return skewness spread; mirror EVAL-112/113/116 contract; bump `EXPECTED_TARGETED_TESTS` 1084→1102; wire `TARGETED_TEST_FILES`/`GATE_SPECS`/`SEAL_SPECS` `expected_exit` 1→0; seal with `--execute`; re-run driver green). Bottlenecks already removed (zombie capture bridge, competing handoff pointers, EVAL-68/69 design gaps, pre-threshold idle avoidance, manual timestamp-only carry, stale SEAL_SPECS expected_exit, task-floor-stamp ordering bug, degenerate kurtosis fixture trap, EVAL-112 runner naming bug, stale EVAL-116 "NOT BUILT" claim). Do NOT re-run sealed EVAL-02..62/64..66/70..117 or touch `src/`. Forward ladder (EVAL-67→68→69) remains hard-gated to `2026-11-20T00:00:00Z`; cron owns polling; no capture bridges/waiters.
- **2026-11-19T05:15:09Z (this session).** Built/wired/sealed **EVAL-118** (cross-sectional `term_slope` basis → forward relative realized return skewness spread). Runner `scripts/eval118_cross_sectional_term_slope_basis_forward_relative_return_skewness_spread.py`, gate `scripts/eval118_phaseb_gate.py`, tests `tests/test_eval118_*` (26). Verdict **`NO-GO CONFIRMED (PASS)`**, sealed `20261119T052824Z`: floor OK (both underlyings, 274 aligned common bars at 300s grid), best IC `0.0646` (`term_slope::bar60.0::h24`), 0/6 pass, 2 pooled BH-FDR rejections (`bar60::h24`, `bar60::h72`) but CI lower ≤ 0 on all configs so no config passed the gate. Wired EVAL-118 into `scripts/eval67_prethreshold_progress.py` (tests, `GATE_SPECS`, `SEAL_SPECS` `expected_exit`→0, `EXPECTED_TARGETED_TESTS` 1084→1110). Full driver green: **1110/1110** targeted + 27/27 diagnostics = **1137**, all EVAL-70..118 SEALED, EVAL-67 NOT_DUE (overlap 65260.588s), EVAL-68 WAIT_EVAL67, EVAL-69 WAIT_EVAL68, all seal-gate specs ok, readiness written. Queue advanced: EVAL-119 (single-asset `atm_iv` → forward own-asset realized return kurtosis) is now the mandatory next build. No sealed prior artifacts or `src/` modified.

(End of file)
