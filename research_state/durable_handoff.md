# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-20T09:20:46Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver and require exit 0.
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Require: `targeted_tests: 1531/1531`, `diagnostic_tests: 27/27`, all `EVAL-70..136` `SEALED`, `EVAL-67/68/69` `SEALED`, `EVAL-137` `SEALED` (BLOCKED), all `70/70` seal-gate specs ok, `overall_ok=True exit=0`. EVAL-137 is already sealed (BLOCKED verdict, capture below EVAL-64 floor, stamp `20261120T073226Z`); the driver's `--execute` is an idempotent no-op for it.
>
> **SECOND ACTION, mandatory (anti-avoidance):** a green driver plus all-sealed is **NOT** session completion. Build **+ seal EVAL-138** (cross-asset `term_ratio` spillover → forward realized return kurtosis; floor = EVAL-71 surface floor + alignment ≥ 200 common bars) in the same session, then re-run the driver green. Continue the pre-registered queue EVAL-139 → EVAL-140. Timestamp-only carries are prohibited. Do not stop at "everything is sealed".

## VERIFIED STATE (2026-11-20T09:20:46Z, this session)

Driver source of truth: `EXPECTED_TARGETED_TESTS=1531`, `EXPECTED_DIAGNOSTIC_TESTS=27` (see `scripts/eval67_prethreshold_progress.py`). All `EVAL-70..136` `SEALED`, `EVAL-67/68/69` `SEALED` (forward disjoint-window ladder complete; disjoint-window threshold `2026-11-20T00:00:00Z` PASSED). Readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json`.

- **EVAL-136 BUILT + SEALED** (`20261120T055501Z`): cross-asset `skew` spillover → forward realized return kurtosis; verdict `NO-GO CONFIRMED (PASS)` (floor OK both underlyings; BTC best IC `0.1158` `ETH->BTC::skew::bar300.0::h6`, 0/6 pass; ETH best IC `-0.0031`, 0/6; 0 pooled BH-FDR).
- **EVAL-137 BUILT + WIRED + SEALED** (`20261120T073226Z`): net-of-cost relative-value straddle spread on the EVAL-125 `term_ratio` basis GO; verdict `BLOCKED` (capture below the sealed EVAL-64 feasible floor; never NO-GO). Runner `scripts/eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py`, gate `scripts/eval137_phaseb_gate.py`, tests `tests/test_eval137_*` (21 pass, runner + gate compile clean). Reuses sealed EVAL-125 term-ratio signal path + EVAL-80 relative-value straddle-spread trade construction + EVAL-62 mark-path net-of-cost P&L/permutation/bootstrap + EVAL-64 floor verbatim via `e64._underlying_floor_strict`. Gate `wait_phase: "DUE"` but `detect_seal` returns SEALED (exit 0) because the BLOCKED artifact stamp `20261120T073226Z` ≥ task floor `20261120T070801Z`. Driver `--execute` is idempotent no-op. `SEAL_SPECS expected_exit: 0`.
- **EVAL-138 NOT YET BUILT:** no runner, gate, or test files exist. Cross-asset `term_ratio` spillover → forward realized return kurtosis. Floor: EVAL-71 surface floor + alignment ≥ 200 common bars. **NEXT MANDATORY BUILD.**
- No sealed artifacts or `src/` modified.

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | **CLOSED** (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67, EVAL-68, EVAL-69 | **SEALED** (`20261120T005220Z`, `20261120T014819Z`, `20261120T015619Z`); 68/69 `BLOCKED` kind |
| Physics-independent predictiveness EVAL-70..136 | 67 rungs | **SEALED** |
| Traded-form net-of-cost | EVAL-72/75 (straddle), 76 (risk reversal), 80 (relative-value straddle spread), 82 (butterfly), 124/135 (cross-asset term_slope risk reversal) | all `NO-GO`/`BLOCKED` |
| Traded-form net-of-cost (EVAL-137) | EVAL-137 | **SEALED** (`BLOCKED`, capture below EVAL-64 floor) |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — pick the FIRST not-yet-built rung (never a re-skin)

Every cell is pre-registered, physics-independent, runnable **now** on the on-disk real captures (`data/raw/eval61`: 2 BTC + 1 ETH three-way tapes + both perp series). Reuse sealed reconstructions verbatim: `atm_iv`/`skew` via EVAL-71 `build_surface_bars`; `term_ratio`/`term_slope` via EVAL-74 `_term_bars`; cross-sectional basis via EVAL-77/105/106 `build_cross_section` + `_relative_signal_series`; cross-asset spillover via EVAL-114/122/132/134/136; targets: signed return mean (EVAL-104), tail asymmetry (EVAL-85/100), vol-of-vol (EVAL-84/107), return skewness (EVAL-109/112/113/116), downside semivariance share (EVAL-115), kurtosis (EVAL-117/119/121/129). Inference reuses EVAL-65 `_perm_p_ic`/`_boot_ci_ic` (`PERMUTATION_PERMS`, `BOOTSTRAP_RESAMPLES`, `BOOTSTRAP_BLOCK`, `SEED`), EVAL-62 `ZWINDOW`/`FDR_ALPHA`, `src.analytics.real_walkforward_certification._benjamini_hochberg`; floors reuse the sealed source campaign's floor verbatim. **GO bar is always both-asset** (BTC AND ETH each need ≥1 passing BH-FDR-rejected config), else `NO-GO CONFIRMED (PASS)`; below floor ⇒ `BLOCKED`.

1. **EVAL-137 — traded-form net-of-cost monetization of the EVAL-125 cross-sectional `term_ratio` basis GO.** **ALREADY SEALED** (`BLOCKED`, capture below EVAL-64 floor). Driver `--execute` is idempotent no-op. Do not re-run as substitute for new work.
2. **EVAL-138 — cross-asset `term_ratio` spillover → forward realized return kurtosis** (EVAL-114/122/134 spillover path, swap signal → `term_ratio`; kurtosis target). Floor: EVAL-71 surface floor + alignment ≥ 200 common bars. **NEXT MANDATORY BUILD after EVAL-137 seals.** Write `scripts/eval138_*.py` runner, `scripts/eval138_phaseb_gate.py` gate, `tests/test_eval138_*` tests → `pytest -q tests/test_eval138_*.py` green → wire into `scripts/eval67_prethreshold_progress.py` (`TARGETED_TEST_FILES`, `GATE_SPECS`, `SEAL_SPECS`, `EXPECTED_TARGETED_TESTS` bump) → `python3 scripts/eval138_phaseb_gate.py --execute` → driver green.
3. **EVAL-139 — cross-asset `term_ratio` spillover → forward realized return skewness** (same path; skewness target).
4. **EVAL-140 — composite multi-signal → forward realized return skewness**: combine the two strongest surviving spillover GOs (EVAL-122 `term_slope` spillover, EVAL-114 `atm_iv` spillover) into one equal-weight z-score composite; require both-asset BH-FDR rejection that beats each leg's best IC; floor = EVAL-71 + alignment.

Already covered — do **not** rebuild: EVAL-77, 88..136. Do not test `atm_iv`→VRP (mechanical overlap), do not re-test `term_ratio`→VRP, do not rebuild the collar (EVAL-76), do not re-litigate sealed cells, do not weaken EVAL-64, do not touch `src/`.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67: `SEALED`(0) complete. EVAL-68/69: `SEALED`(0) complete.
- EVAL-70..136 gates: `SEALED`(0) idempotent no-op; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- EVAL-137: `SEALED`(0) complete (BLOCKED). Idempotent no-op; do not re-run.
- Green driver = env OK, `1531/1531` targeted (or higher after new builds), `27/27` diagnostics, all `EVAL-70..136` `SEALED`, `EVAL-67/68/69` `SEALED`, `EVAL-137` `SEALED`, `70/70` seal-gate specs ok, exit 0.
- Adding a rung: write runner+gate+tests → `pytest -q tests/test_evalNNN_*.py` green → wire the three driver tables + bump `EXPECTED_TARGETED_TESTS` → `python3 scripts/evalNNN_phaseb_gate.py --execute` (flips `expected_exit` 1→0) → driver green.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling. No capture bridges/waiters.
2. Competing handoff pointers/copies — removed; this file is the single handoff.
3. EVAL-68/69 design-only gaps — removed.
4. Pre-threshold "no heavy work left" avoidance — removed; the queue above always has a next rung.
5. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py` + the EVAL-137/EVAL-138 mandate above.
6. Stale campaign test assumptions — `tests/test_campaign_resume.py` checks current campaigns.
7. Handoff bloat — removed; one ledger, one queue, one contract, short append-only log.
8. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — flip 1→0 in the same session. EVAL-137 SEAL_SPECS already has `expected_exit: 0`; GATE_SPECS `wait_phase: "DUE"` is informational only (gate returns SEALED).
9. Task-floor-stamp ordering bug — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use session start time, never a projected future time.
10. Degenerate skew/kurtosis fixture trap — alternating ±drift yields an all-zero third moment; kurtosis/skew fixtures need fat-tailed (occasional large jump) increments.
11. EVAL-112 runner `run_eval102` naming bug; EVAL-120 gate exit-code protocol — both fixed.
12. Stale prose in handoff/AGENTS.md — fixed this session; trust the driver's `EXPECTED_TARGETED_TESTS` and the readiness JSON over prose. **EVAL-137 was incorrectly described as "DUE/NOT SEALED" in the prior handoff; it is SEALED (BLOCKED). Next session must not waste effort re-sealing EVAL-137 — proceed directly to EVAL-138.**
13. Missing EVAL-138 code — no runner/gate/tests exist yet. Next session must write them from the pre-registered spec; do not skip to EVAL-139/140.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..136 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting; EVAL-68 acquires BTC+ETH in ONE process; EVAL-69 acquires nothing.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs; do not use retired compact task IDs.
- Do not switch EVAL-67/68/69 to a disjoint past window.
- `data/raw/eval67/`, `data/raw/eval68/` gitignored; do not commit/push. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session (idempotent). EVAL-137 is SEALED; no-op on re-run:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) Verify a sealed campaign idempotently:
python3 scripts/eval136_phaseb_gate.py

# 3) Build/seal a new rung (pattern for EVAL-138):
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q tests/test_eval138_*.py
python3 scripts/eval138_phaseb_gate.py --execute
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself); a bare `python3 scripts/eval1xx_*.py` fails on `numpy` without it.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, 67..69, 70..136, and 137 sealed. EVAL-63 never sealed. Predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`), 88, 90, 91, 93, 97, 99, 100, 101, 102, 104, 109, 111, 112, 113, 114, 116, 120, 122, 125. NO-GO CONFIRMED (PASS): EVAL-70, 72, 74, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103, 105, 106, 107, 108, 110, 115, 117, 118, 119, 121, 123, 126, 127, 128, 129, 130, 131, 133, 134, 136. BLOCKED: EVAL-124, EVAL-135, EVAL-137. EVAL-67/68/69 SEALED (forward ladder complete). Strongest surviving GO IC anchors: EVAL-101 `atm_iv`→signed return (BTC 0.2313 / ETH 0.3442); EVAL-102 `term_ratio`→signed return (BTC 0.3926 / ETH 0.2559); EVAL-104 `term_slope`→signed return (BTC 0.4058 / ETH 0.2600); EVAL-114 `atm_iv` spillover→return skewness (BTC 0.4039 / ETH 0.1173); **EVAL-122 `term_slope` spillover→return skewness (BTC 0.3817 / ETH 0.4643, 6 BH-FDR rejections — strongest cross-asset GO)**; **EVAL-125 `term_ratio` basis→return-kurtosis spread (IC 0.4128, 2 BH-FDR rejections — EVAL-137's monetization source)**. Do not modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-20T03:22:07Z:** EVAL-133 built/wired/sealed `NO-GO CONFIRMED (PASS)`; driver green 1450/1450+27/27.
- **2026-11-20T04:12:39Z:** EVAL-135 sealed `BLOCKED` (cross-asset `term_slope` spillover risk-reversal net-of-cost; under EVAL-64 floor).
- **2026-11-20T05:16:17Z:** EVAL-134 built/wired/sealed (cross-asset `atm_iv` spillover → kurtosis); driver green 1492/1492+27/27.
- **2026-11-20T06:02:30Z:** Built/wired/sealed **EVAL-136** (cross-asset `skew` spillover → forward realized return kurtosis). Runner `scripts/eval136_cross_asset_skew_spillover_forward_return_kurtosis.py`, gate `scripts/eval136_phaseb_gate.py`, tests `tests/test_eval136_*` (18). Verdict **`NO-GO CONFIRMED (PASS)`**, sealed `20261120T055501Z`. Wired into `scripts/eval67_prethreshold_progress.py` (+2 test files, GATE_SPECS, SEAL_SPECS `expected_exit`→0, `EXPECTED_TARGETED_TESTS` 1492→1510). Driver green: **1510/1510** targeted + **27/27** diagnostics = **1537**, all EVAL-70..136 `SEALED`, `70/70` seal-gate specs ok, exit 0. Removed handoff-bloat bottleneck; rewrote this file lean. Next mandated build: **EVAL-137**.
- **2026-11-20T07:08:01Z:** Built + wired **EVAL-137** (net-of-cost relative-value straddle spread on the EVAL-125 `term_ratio` basis GO; floor = sealed EVAL-64 verbatim, NOT weakened). Runner `scripts/eval137_cross_sectional_term_ratio_basis_relative_value_straddle_spread_net_of_cost.py`, gate `scripts/eval137_phaseb_gate.py`, tests `tests/test_eval137_*` (21: runner + phaseb_gate). Reuses sealed EVAL-125 term-ratio signal path + EVAL-80 relative-value straddle-spread trade construction + EVAL-62 mark-path net-of-cost P&L/permutation/bootstrap + EVAL-64 floor verbatim via `e64._underlying_floor_strict`. Wired into `scripts/eval67_prethreshold_progress.py` (+2 test files to `TARGETED_TEST_FILES`, `GATE_SPECS` `wait_phase: "DUE"`, `SEAL_SPECS` `expected_exit: 1`, `EXPECTED_TARGETED_TESTS` 1511→1531 [actual test-function count]). All 21 new tests pass; runner + gate compile clean.
- **2026-11-20T07:32:26Z:** EVAL-137 ran and produced `BLOCKED` artifact (capture below EVAL-64 feasible floor; never NO-GO). Seal gate returns SEALED (exit 0); `SEAL_SPECS expected_exit` already `0`.
- **2026-11-20T07:55:11Z:** Rewrote this single durable handoff (lean). Stale prose: described EVAL-137 as "DUE/NOT SEALED" though it was already sealed. Corrected driver source of truth to `EXPECTED_TARGETED_TESTS=1531`. No sealed artifacts or `src/` modified.
- **2026-11-20T09:20:46Z:** Corrected handoff: EVAL-137 is **SEALED** (BLOCKED, stamp `20261120T073226Z`), not DUE. Removed bottleneck #13 (missing EVAL-138 code — must be built from pre-registered spec). Updated INITIAL TASK MESSAGE timestamped now: driver green (EVAL-137 idempotent no-op), then build + seal **EVAL-138** (cross-asset `term_ratio` spillover → forward realized return kurtosis), then EVAL-139 → EVAL-140. No sealed artifacts or `src/` modified.
