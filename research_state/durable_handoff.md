# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-19T01:43:41Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor). PRIMARY TASK, IN ORDER: (1) run `python3 scripts/eval67_prethreshold_progress.py --execute` and require exit 0, `targeted_tests: 994/994`, `diagnostic_tests: 27/27`, all EVAL-70..113 `SEALED`, EVAL-67 `NOT_DUE`/EVAL-68 `WAIT_EVAL67`/EVAL-69 `WAIT_EVAL68`, all 48 seal-gate specs ok; (2) BUILD + SEAL the next pre-threshold campaign EVAL-114 from the candidate space below (§FURTHER CANDIDATE SPACE) — the pre-registered EVAL-104..113 queue is now COMPLETE (all sealed, all GO CONFIRMED) so explicit directions are ABSENT and the anti-avoidance rule forces a new build: mirror the EVAL-112/113 contract (runner `scripts/eval114_*`, gate `scripts/eval114_phaseb_gate.py`, tests `tests/test_eval114_*` = 18, wire into `TARGETED_TEST_FILES`/`GATE_SPECS`/`SEAL_SPECS` with `expected_exit:1`→`0`, bump `EXPECTED_TARGETED_TESTS` 994→1012, seal with `--execute`, re-run driver green). A green driver + NOT_DUE/WAIT ladder is **NOT** session completion; a timestamp-only carry is prohibited; (3) at/after `2026-11-20T00:00:00Z` (or on `DUE`/`FAILED`), run the forward ladder sequentially: `python3 scripts/eval67_phaseb_gate.py --execute`, `python3 scripts/eval68_phaseb_gate.py --execute`, `python3 scripts/eval69_phaseb_gate.py --execute`. Do NOT acquire EVAL-68 before EVAL-67 seals; do not run EVAL-69 before EVAL-68 seals.
>
> **VERIFIED STATE (2026-11-19T00:21:23Z, this session):** the pre-registered EVAL-111/112/113 build queue is COMPLETE — all three built, wired, sealed and re-verified in one session, driver green.
> · **EVAL-111** — single-asset `skew` → forward own-asset realized return skewness. Runner `scripts/eval111_single_asset_skew_forward_return_skewness.py`, gate `scripts/eval111_phaseb_gate.py`, tests `tests/test_eval111_*` (18). Verdict **`GO CONFIRMED`**, sealed `20261118T232819Z`. Task `INIT-2026-11-18T23:00:00Z-EVAL111-SINGLE-ASSET-SKEW-FORWARD-RETURN-SKEWNESS`.
> · **EVAL-112** — single-asset `term_ratio` → forward own-asset realized return skewness. Runner `scripts/eval112_single_asset_term_ratio_forward_return_skewness.py`, gate `scripts/eval112_phaseb_gate.py`, tests `tests/test_eval112_*` (18). Verdict **`GO CONFIRMED`**, sealed `20261119T000552Z`: **BTC** best IC `0.2883` (`term_ratio::bar60::h72`), 4/6 pass; **ETH** best IC `0.2223` (`term_ratio::bar300::h24`), 2/6 pass; **9 pooled BH-FDR rejections** on both assets. Task `INIT-2026-11-18T23:00:00Z-EVAL112-SINGLE-ASSET-TERM-RATIO-FORWARD-RETURN-SKEWNESS`.
> · **EVAL-113** — single-asset `term_slope` → forward own-asset realized return skewness. Runner `scripts/eval113_single_asset_term_slope_forward_return_skewness.py`, gate `scripts/eval113_phaseb_gate.py`, tests `tests/test_eval113_*` (18). Verdict **`GO CONFIRMED`**, sealed `20261119T001521Z`: **BTC** best IC `0.3005` (`term_slope::bar60::h72`), 4/6 pass; **ETH** best IC `0.2116` (`term_slope::bar300::h24`), 2/6 pass; **9 pooled BH-FDR rejections** on both assets. Task `INIT-2026-11-19T00:12:00Z-EVAL113-SINGLE-ASSET-TERM-SLOPE-FORWARD-RETURN-SKEWNESS`.
> · **Full driver** `python3 scripts/eval67_prethreshold_progress.py --execute` green (exit 0, `overall_ok: true`, `failures: []`) at **2026-11-19T00:21:23Z**: env OK, `targeted_tests: 994/994` (rc 0), `diagnostic_tests: 27/27` (rc 0), `total_tests_passed: 1021`; all EVAL-70..113 `SEALED`; **48/48 seal-gate specs ok**; EVAL-67 `NOT_DUE` (overlap **83704.485s**, disjoint=false), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`; readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json`. **The EVAL-104..113 pre-registered queue is COMPLETE; EVAL-114 is the mandatory next build.**
>
> **Forward ladder (hard physics, not fixable pre-threshold):** EVAL-67 `NOT_DUE` exit 10, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`. Threshold **2026-11-20T00:00:00Z**; earliest disjoint capture end **2026-11-19T18:08:16Z**. External `*/5` cron owns routine polling. Do not spawn capture bridges/waiters.
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver now (idempotent; confirms green, refreshes readiness):
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Require exit 0, `targeted_tests: 994/994` (or higher if more built/sealed), `diagnostic_tests: 27/27`, EVAL-70..113 `SEALED`, EVAL-67 `NOT_DUE` / EVAL-68 `WAIT_EVAL67` / EVAL-69 `WAIT_EVAL68` pre-threshold, and all 48 seal-gate specs ok. If any arbiter is `DUE`(20) execute it; if `FAILED`(1) fix and rerun.
>
> **ANTI-AVOIDANCE RULE (mandatory):** a green driver plus NOT_DUE/WAIT is **not** session completion. With EVAL-70..113 sealed and the EVAL-104..113 queue complete, **EVAL-114 is not built/wired/sealed**. If the driver is green and the ladder remains NOT_DUE/WAIT, **build + seal EVAL-114 now** (mirror the EVAL-112/113 contract; candidate space below). One campaign per session minimum is required while the ladder is NOT_DUE/WAIT; a timestamp-only carry is prohibited.
>
> **Repo-priority reading:** on-charter ladder EVAL-02..66 is **CLOSED**. Do not re-run, re-litigate, re-seal, or edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..113 artifacts or `src/`. Append-only for new authorized work. No synthetic data, no live trading, no floor weakening.

## FURTHER CANDIDATE SPACE — pick the first not yet built for EVAL-114 (never a re-skin)

Each cell is predictiveness-only (no monetization claim) and reuses EVAL-65 inference (`_perm_p_ic`, `_boot_ci_ic`, `PERMUTATION_PERMS`, `BOOTSTRAP_RESAMPLES`, `BOOTSTRAP_BLOCK`, `SEED`), EVAL-62 `ZWINDOW`/`FDR_ALPHA`, and BH-FDR from `src.analytics.real_walkforward_certification._benjamini_hochberg`.

1. **cross-asset `atm_iv` spillover → other-asset realized return skewness** — EVAL-77 `build_cross_section` + other-asset `atm_iv` z → forward own-asset return skewness (EVAL-109 target verbatim). Floor: sealed EVAL-71 surface floor per underlying.
2. **single-asset `atm_iv` → forward realized downside semivariance share** — EVAL-87 `atm_iv` signal path → new target = downside semivariance / total variance over forward window. Floor: sealed EVAL-71 surface floor.
3. **cross-sectional `skew` basis → relative realized return skewness spread** — EVAL-77 `build_cross_section` + `_relative_signal_series` (`skew_ETH − skew_BTC`) → forward relative skewness spread. Floor: sealed EVAL-77 surface basis floor.

Already covered — do NOT rebuild: EVAL-77, 88, 89, 90, 91, 92, 93, 94, 101, 102, 103, 104, 105..113. Do **not** test `atm_iv`→VRP (mechanical overlap), do not re-test `term_ratio`→VRP, do not rebuild a collar (EVAL-76), do not re-litigate sealed cells, do not weaken EVAL-64, do not touch `src/`.

## PRE-REGISTERED BUILD QUEUE (status; EVAL-104..113 all COMPLETE)

1. **EVAL-104** — `term_slope` → own signed return mean. **SEALED `GO CONFIRMED`** (`20261118T190138Z`).
2. **EVAL-105** — `term_ratio` basis → relative tail-asymmetry spread. **SEALED `NO-GO CONFIRMED (PASS)`** (`20261118T200246Z`).
3. **EVAL-106** — `term_slope` basis → relative tail-asymmetry spread. **SEALED `NO-GO CONFIRMED (PASS)`** (`20261118T204231Z`).
4. **EVAL-107** — `term_ratio` basis → relative vol-of-vol spread. **SEALED `NO-GO CONFIRMED (PASS)`** (`20261118T215800Z`).
5. **EVAL-108** — `term_slope` basis → relative vol-of-vol spread. **SEALED `NO-GO CONFIRMED (PASS)`** (`20261118T230834Z`).
6. **EVAL-109** — `atm_iv` → own realized return skewness. **SEALED `GO CONFIRMED`** (`20261118T231058Z`).
7. **EVAL-110** — `skew` basis → relative tail-asymmetry spread. **SEALED `NO-GO CONFIRMED (PASS)`** (`20261118T231811Z`/`20261118T231828Z`).
8. **EVAL-111** — `skew` → own realized return skewness. **SEALED `GO CONFIRMED`** (`20261118T232819Z`).
9. **EVAL-112** — `term_ratio` → own realized return skewness. **SEALED `GO CONFIRMED`** (`20261119T000552Z`).
10. **EVAL-113** — `term_slope` → own realized return skewness. **SEALED `GO CONFIRMED`** (`20261119T001521Z`).
11. **EVAL-114** — next campaign from §FURTHER CANDIDATE SPACE. **NOT BUILT — mandatory next.**

## RUNNABLE-NOW CAMPAIGNS — EVAL-70..113 ALL SEALED

Predictiveness GOs (no net-of-cost monetization): EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`, `20261118T005436Z`), 88, 90, 91, 93, 97, 99, 100, 101, 102, 104, **109**, **111**, **112**, **113**. NO-GO CONFIRMED (PASS): EVAL-70, 72, 74, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103, 105, 106, 107, **108**, **110**. Traded-form taxonomy complete/all NO-GO (straddle 72/75, risk reversal 76, butterfly 82, relative-value straddle spread 80). Key IC anchors: EVAL-101 `atm_iv`→signed return (BTC 0.2313 / ETH 0.3442), EVAL-102 `term_ratio`→signed return (BTC 0.3926 / ETH 0.2559), EVAL-103 `skew`→signed return (ETH 0.2195 / BTC 0.0462, NO-GO), EVAL-104 `term_slope`→signed return (BTC 0.4058 / ETH 0.2600), EVAL-109 `atm_iv`→return skewness (BTC 0.1101 / ETH 0.3506), EVAL-112 `term_ratio`→return skewness (BTC 0.2883 / ETH 0.2223), EVAL-113 `term_slope`→return skewness (BTC 0.3005 / ETH 0.2116). These are idempotent no-ops once sealed; do not re-run as substitute for new work.

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
- EVAL-70..113 gates: `SEALED`(0) idempotent; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- After fully-refreshed green driver: env OK, `994/994` targeted (or higher if more built/sealed), `27/27` diagnostics, all EVAL-70..113 `SEALED`, EVAL-67 `NOT_DUE` / EVAL-68 `WAIT_EVAL67` / EVAL-69 `WAIT_EVAL68` pre-threshold, all 48 seal-gate specs ok, driver exit 0.

## PRE-THRESHOLD HEAVY-WORK RULE

Run full driver with `--execute` every session. If green and ladder still NOT_DUE/WAIT, build and seal EVAL-114 (then the next candidate), re-running the driver green after each seal. Timestamp-only carry prohibited. No capture bridges/waiters; cron owns polling. Forward wait is hard physics until the disjoint window.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge/liveness churn — removed.
2. Competing handoff pointers/copies — removed; this file is the single handoff.
3. EVAL-68/69 design-only gaps — removed.
4. Pre-threshold "no heavy work left" avoidance — removed by EVAL-70..113 and renewed by the mandatory EVAL-114 build.
5. Manual pre-threshold loop/timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
6. Stale campaign test assumptions — `tests/test_campaign_resume.py` checks current campaigns.
7. Handoff bloat — consolidated; no timestamped copies, no `research_state/` enumeration.
8. **Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — removed.** When `--execute` seals a rung, flip that rung's `expected_exit` 1→0 in the same session or the next driver reports a seal-gate failure.
9. **Task-floor-stamp ordering bug — removed / do not repeat.** `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp. A task time later than the run makes the seal-gate emit `FAIL: no artifact ... with stamp >= ...` and the arbiter `FAILED`. Use the session start time, never a projected future time.
10. **Degenerate-skew test fixture trap — removed.** An alternating ±drift price path yields an all-zero third moment; fixtures must use asymmetric increments (see EVAL-109/112/113 tests).
11. EVAL-94..113 staging gaps — all removed (built/wired/sealed).
12. **EVAL-112 runner `run_eval102` naming bug — removed.** Renamed to `run_eval112` for consistency with `run_eval109`/`run_eval111`/`run_eval113`.
13. **Stale handoff claiming EVAL-111 "NOT BUILT" — removed.** EVAL-111/112/113 are all sealed `GO CONFIRMED`; EVAL-114 is the open mandatory build.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..113 artifacts or `src/`. Append-only for new authorized work.
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
python3 scripts/eval113_phaseb_gate.py

# 3) Build/seal a new rung (e.g. EVAL-114):
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q tests/test_eval114_*.py
python3 scripts/eval114_phaseb_gate.py --execute

# 4) At/after 2026-11-20T00:00:00Z, or on DUE/FAILED:
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

Driver runs env check, all targeted/diagnostic suites, all campaign arbiters in order, any required `--execute`, all seal-gate specs, and readiness refresh. Use its output and `research_state/EVAL_67_PREWINDOW_READINESS.json` as verified state. Note: targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself); a bare `python3 scripts/eval1xx_*.py` will fail on `numpy` without it.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, and 70..113 sealed. EVAL-63 never sealed. EVAL-67/68/69 forward-gated (NOT_DUE/WAIT pre-threshold). Predictiveness GOs: EVAL-71,73,77,83,85,86,88,90,91,93,97,99,100,101,102,104,109,**111**,**112**,**113**; EVAL-87 `GO/BLOCKED` (`20261118T005436Z`). Traded-form monetization complete/all-NO-GO. EVAL-70,72,74,75,76,78,79,80,81,82,84,89,92,94,95,96,98,103,105,106,107,108,**110** NO-GO CONFIRMED (PASS). Do not modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-18T19:01:38Z:** EVAL-104 built/wired/sealed `GO CONFIRMED`; driver green 837/837+27/27.
- **2026-11-18T20:08:49Z:** EVAL-105 sealed NO-GO; driver green 854/854+27/27.
- **2026-11-18T21:58:00Z:** EVAL-106 sealed NO-GO; driver green 872/872+27/27.
- **2026-11-18T22:03:45Z:** EVAL-107 sealed NO-GO; driver green 888/888+27/27; EVAL-108 mandated.
- **2026-11-18T23:24:19Z (prior session; three rungs sealed).** EVAL-108 sealed `NO-GO CONFIRMED (PASS)` at `20261118T230834Z`. EVAL-109 sealed `GO CONFIRMED` at `20261118T231058Z`. EVAL-110 sealed `NO-GO CONFIRMED (PASS)` at `20261118T231811Z`/`20261118T231828Z`. Full driver green: **940/940** targeted + 27/27 diagnostics = **967**, all EVAL-70..110 SEALED, EVAL-67 NOT_DUE, EVAL-68 WAIT_EVAL67, EVAL-69 WAIT_EVAL68, **45/45** seal-gate specs ok. **EVAL-111 was already sealed `GO CONFIRMED` (`20261118T232819Z`) prior to this session but the handoff had not been updated — stale-state bottleneck removed.**
- **2026-11-19T00:21:23Z (this session).** Built/wired/sealed **EVAL-112** (`term_ratio`→return skewness, `GO CONFIRMED`, `20261119T000552Z`, BTC 0.2883/ETH 0.2223, 9 BH-FDR rejections) and **EVAL-113** (`term_slope`→return skewness, `GO CONFIRMED`, `20261119T001521Z`, BTC 0.3005/ETH 0.2116, 9 BH-FDR rejections). Fixed `eval112` runner `run_eval102`→`run_eval112` naming. Wired EVAL-112/EVAL-113 into `scripts/eval67_prethreshold_progress.py` (tests, GATE_SPECS, SEAL_SPECS, `EXPECTED_TARGETED_TESTS` 958→994). Full driver green: **994/994** targeted + 27/27 diagnostics = **1021**, all EVAL-70..113 SEALED, EVAL-67 NOT_DUE (overlap 83704.485s), EVAL-68 WAIT_EVAL67, EVAL-69 WAIT_EVAL68, **48/48** seal-gate specs ok, readiness written. Pre-registered queue EVAL-104..113 now **COMPLETE**; **EVAL-114 is the mandatory next build.** No sealed prior artifacts or `src/` modified.
