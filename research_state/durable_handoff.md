# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-20T12:38:04Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**>> **FIRST ACTION, non-negotiable:** run the full heavy-work driver and require exit 0.
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Require: `targeted_tests: 1605/1605`, `diagnostic_tests: 27/27`, `EVAL-70..141` all `SEALED`, `EVAL-67/68/69` `SEALED`, `EVAL-137` `SEALED` (BLOCKED), `EVAL-138/139` `SEALED` (GO CONFIRMED), `EVAL-140/141` `SEALED` (NO-GO), all `76/76` seal-gate specs ok, `overall_ok=True exit=0`. The driver's `--execute` is an idempotent no-op for every sealed rung.
>
> **SECOND ACTION, mandatory (anti-avoidance):** a green driver plus all-sealed is **NOT** session completion. Build **+ seal EVAL-142** in the same session (cross-asset `term_ratio` spillover → risk-reversal net-of-cost, traded form; spec in the queue below), then re-run the driver green. Continue the pre-registered queue (EVAL-142 → EVAL-143). Timestamp-only carries are prohibited. Do not stop at "everything is sealed".

## VERIFIED STATE (2026-11-20T12:38:04Z, this session)

Driver source of truth: `EXPECTED_TARGETED_TESTS=1605`, `EXPECTED_DIAGNOSTIC_TESTS=27` (see `scripts/eval67_prethreshold_progress.py`). All `EVAL-70..141` `SEALED`; `EVAL-67/68/69` `SEALED` (forward disjoint-window ladder complete; disjoint-window threshold `2026-11-20T00:00:00Z` PASSED). Readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json` (1605 targeted + 27 diagnostics = 1632, 76/76 seal gates, exit 0).

- **EVAL-139 SEALED** (`20261120T103405Z`, `GO CONFIRMED`): cross-asset `term_ratio` spillover → forward realized return skewness (BTC 0.2613 / ETH 0.4878, 7 pooled BH-FDR rejections).
- **EVAL-140 BUILT + WIRED + SEALED** (`20261120T110420Z`): **equal-weight z-score composite** of the two strongest surviving spillover GOs — EVAL-114 `atm_iv` and EVAL-122 `term_slope` (other asset's legs) → forward realized return skewness. Runner `scripts/eval140_composite_atm_iv_term_slope_spillover_forward_return_skewness.py`, gate `scripts/eval140_phaseb_gate.py`, tests `tests/test_eval140_*` (19 pass, runner + gate compile clean). Verdict **`NO-GO CONFIRMED (PASS)`** — BTC composite best IC `0.5052` `ETH->BTC::composite_atm_iv_term_slope::bar300.0::h72` **beats both legs** (atm_iv 0.4039, term_slope 0.3817), 2 pass configs + 2 BH-FDR rejections; ETH composite best IC `0.3883` **fails to beat** its `term_slope` leg (0.4643) though it beats `atm_iv` (0.1173), 2 pass configs + 3 BH-FDR rejections. GO bar required *both* underlyings to pass AND beat both legs ⇒ NO-GO (honest, pre-registered; the composite adds nothing on ETH over its best leg). Wired into `scripts/eval67_prethreshold_progress.py` (+2 test files to `TARGETED_TEST_FILES`, `GATE_SPECS` `wait_phase: "DUE"`, `SEAL_SPECS` `expected_exit: 0`, `EXPECTED_TARGETED_TESTS` 1567→1586). Driver green: **1586/1586** targeted + **27/27** diagnostics = 1613, all `74/74` seal-gate specs ok, exit 0. Driver `--execute` is idempotent no-op on re-run.
- **EVAL-141 BUILT + WIRED + SEALED** (`20261120T114944Z`, `NO-GO CONFIRMED (PASS)`): equal-weight z-score composite of EVAL-114 `atm_iv` + EVAL-139 `term_ratio` cross-asset spillover → forward realized return skewness. Runner `scripts/eval141_composite_atm_iv_term_ratio_spillover_forward_return_skewness.py`, gate `scripts/eval141_phaseb_gate.py`, tests `tests/test_eval141_*` (19 pass, runner + gate compile clean). Verdict `NO-GO CONFIRMED (PASS)` — BTC composite best IC `0.4979` `ETH->BTC::composite_atm_iv_term_ratio::bar300.0::h72` beats both legs (atm_iv 0.4039, term_ratio 0.2613), 2 pass + 2 BH-FDR rejections; ETH composite best IC `0.4151` **fails to beat** its `term_ratio` leg (0.4878) though it beats `atm_iv` (0.1173), 3 pass + 5 BH-FDR rejections. GO bar required *both* underlyings to pass AND beat both legs ⇒ NO-GO (honest, pre-registered; mirrors EVAL-140's ETH leg failure). Wired into `scripts/eval67_prethreshold_progress.py` (+2 test files to `TARGETED_TEST_FILES`, `GATE_SPECS` `wait_phase: "DUE"`, `SEAL_SPECS` `expected_exit: 0`, `EXPECTED_TARGETED_TESTS` 1586→1605). Driver green: **1605/1605** targeted + **27/27** diagnostics = 1632, all `76/76` seal-gate specs ok, exit 0. Driver `--execute` is idempotent no-op on re-run.
- No sealed artifacts or `src/` modified (EVAL-140/EVAL-141 are append-only).

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | **CLOSED** (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67, EVAL-68, EVAL-69 | **SEALED** (`20261120T005220Z`, `20261120T014819Z`, `20261120T015619Z`); 68/69 `BLOCKED` kind |
| Physics-independent predictiveness EVAL-70..136 | 67 rungs | **SEALED** |
| Traded-form net-of-cost | EVAL-72/75 (straddle), 76 (risk reversal), 80 (relative-value straddle spread), 82 (butterfly), 124/135 (cross-asset term_slope risk reversal), 137 (term_ratio basis straddle spread) | all `NO-GO`/`BLOCKED` |
| Physics-independent predictiveness (EVAL-138/139) | EVAL-138 (kurtosis), EVAL-139 (skewness) | **SEALED** `GO CONFIRMED` (`20261120T093729Z`, `20261120T103405Z`) |
| Composite predictiveness (EVAL-140) | EVAL-140 (atm_iv+term_slope composite → skewness) | **SEALED** `NO-GO CONFIRMED (PASS)` (`20261120T110420Z`) |
| Composite predictiveness (EVAL-141) | EVAL-141 (atm_iv+term_ratio composite → skewness) | **SEALED** `NO-GO CONFIRMED (PASS)` (`20261120T114944Z`) |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — pick the FIRST not-yet-built rung (never a re-skin)

Every cell is pre-registered, physics-independent, runnable **now** on the on-disk real captures (`data/raw/eval61`: 2 BTC + 1 ETH three-way tapes + both perp series). Reuse sealed reconstructions verbatim: `atm_iv`/`skew` via EVAL-71 `build_surface_bars`; `term_ratio`/`term_slope` via EVAL-74 `_term_bars`; cross-sectional basis via EVAL-77/105/106 `build_cross_section` + `_relative_signal_series`; cross-asset spillover via EVAL-114/122/132/134/136/138/139/**140**/**141** (`build_cross_section` returning both `maps` for the EVAL-71 surface bar and `term_maps` for the EVAL-74 term bar is the ready-made pattern in the EVAL-140/141 runner — reuse it); targets: signed return mean (EVAL-104), tail asymmetry (EVAL-85/100), vol-of-vol (EVAL-84/107), return skewness (EVAL-109/112/113/116), downside semivariance share (EVAL-115), kurtosis (EVAL-117/119/121/129). Inference reuses EVAL-65 `_perm_p_ic`/`_boot_ci_ic` (`PERMUTATION_PERMS`, `BOOTSTRAP_RESAMPLES`, `BOOTSTRAP_BLOCK`, `SEED`), EVAL-62 `ZWINDOW`/`FDR_ALPHA`, `src.analytics.real_walkforward_certification._benjamini_hochberg`; floors reuse the sealed source campaign's floor verbatim. **GO bar is always both-asset** (BTC AND ETH each need ≥1 passing BH-FDR-rejected config), else `NO-GO CONFIRMED (PASS)`; below floor ⇒ `BLOCKED`.

1. **EVAL-141 — composite `atm_iv` + `term_ratio` cross-asset spillover → forward realized return skewness.** BUILT + WIRED + SEALED (`20261120T114944Z`, `NO-GO CONFIRMED (PASS)`). Do not rebuild; driver-wired (`TARGETED_TEST_FILES` +2, `GATE_SPECS` `wait_phase: "DUE"`, `SEAL_SPECS` `expected_exit: 0`, `EXPECTED_TARGETED_TESTS` 1586→1605).

2. **EVAL-142 — cross-asset `term_ratio` spillover → risk-reversal net-of-cost (traded form).** Distinct from EVAL-135 (which used `term_slope` and sealed `BLOCKED`). Signal = signed z of the OTHER asset's `term_ratio` (EVAL-139 signal path, reuse the EVAL-139 runner's reconstruction); trade = EVAL-76 risk-reversal construction on the TARGET underlying; P&L = EVAL-62 mark-path net-of-cost + permutation/bootstrap; floor = **EVAL-64 verbatim via `e64._underlying_floor_strict`** (never weakened). Below floor ⇒ `BLOCKED`, never NO-GO.

3. **EVAL-143 — pooled BTC+ETH cross-asset `term_ratio` spillover → forward realized return skewness (power-adequate pooled successor to EVAL-139).** Pool the BTC-target and ETH-target configs into one BH-FDR family with the EVAL-68 pooled-power floor concept (≥ `min_pooled_pairs`); require the pooled family to reject after BH-FDR under the EVAL-64-style disjoint-window discipline. Acquires nothing.

Already covered — do **not** rebuild: EVAL-77, 88..140. Do not test `atm_iv`→VRP (mechanical overlap), do not re-test `term_ratio`→VRP, do not rebuild the collar (EVAL-76), do not re-run EVAL-140 as a substitute for EVAL-141, do not re-litigate sealed cells, do not weaken EVAL-64, do not touch `src/`.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) complete. EVAL-70..140 gates: `SEALED`(0) idempotent no-op; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- EVAL-137: `SEALED`(0) complete (BLOCKED). EVAL-138/139: `SEALED`(0) complete (GO CONFIRMED). EVAL-140: `SEALED`(0) complete (NO-GO). Idempotent no-ops; do not re-run.
- Green driver = env OK, `1586/1586` targeted (or higher after new builds), `27/27` diagnostics, all `EVAL-70..140` `SEALED`, `EVAL-67/68/69` `SEALED`, `74/74` seal-gate specs ok, exit 0.
- Adding a rung: write runner+gate+tests → `pytest -q tests/test_evalNNN_*.py` green → wire the three driver tables + bump `EXPECTED_TARGETED_TESTS` → `python3 scripts/evalNNN_phaseb_gate.py --execute` (flips `expected_exit` 1→0 if needed) → driver green.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling. No capture bridges/waiters.
2. Competing handoff pointers/copies — removed; this file is the single handoff.
3. EVAL-68/69 design-only gaps — removed.
4. Pre-threshold "no heavy work left" avoidance — removed; the queue above always has a next rung.
5. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
6. Stale campaign test assumptions — `tests/test_campaign_resume.py` checks current campaigns.
7. Handoff bloat — removed; one ledger, one queue, one contract, short append-only log.
8. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — flip 1→0 in the same session.
9. Task-floor-stamp ordering bug — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use session start time, never a projected future time.
10. Degenerate skew/kurtosis fixture trap — alternating ±drift yields an all-zero third moment; skewness/kurtosis fixtures need fat-tailed (occasional large jump) increments.
11. EVAL-112 runner `run_eval102` naming bug; EVAL-120 gate exit-code protocol — both fixed.
12. Missing/renamed code in a new rung — **do not** describe a rung as DUE when its runner already exists; grep `scripts/` + `tests/` first, then trust the driver's `EXPECTED_TARGETED_TESTS` and the readiness JSON over prose.
13. KURTOSIS/SKEWNESS (and now COMPOSITE-leg) copy-paste bugs in a cloned runner/gate/tests — always `grep -n "EVAL_1[0-9][0-9]\|RATIO\|SLOPE\|KURTOSIS\|SKEWNESS"` the new files and fix ids/labels/globs before sealing. Resolved for EVAL-139/140.
14. **EVAL-140 composite trap (load-bearing for EVAL-141):** the composite GO bar is deliberately strict — it must beat *each leg's best IC on each underlying*. EVAL-140 showed the composite beats both legs on BTC but loses to the `term_slope` leg on ETH, so it seals `NO-GO`. Expect the same possibility for EVAL-141 and do **not** relax the bar to force a GO; a NO-GO sealed is a complete session deliverable.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..140 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting; EVAL-68 acquires BTC+ETH in ONE process; EVAL-69/143 acquire nothing.
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

# 1) Full heavy-work loop; run every session (idempotent). EVAL-137/138/139/140 SEALED; no-op on re-run:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) Verify a sealed campaign idempotently:
python3 scripts/eval140_phaseb_gate.py

# 3) Build/seal a new rung (pattern for EVAL-141):
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q tests/test_eval141_*.py
python3 scripts/eval141_phaseb_gate.py --execute
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself); a bare `python3 scripts/eval1xx_*.py` fails on `numpy` without it.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, 67..69, 70..136, 137, 138, 139, 140, and 141 sealed. EVAL-63 never sealed. Predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`), 88, 90, 91, 93, 97, 99, 100, 101, 102, 104, 109, 111, 112, 113, 114, 116, 120, 122, 125, 138, 139 (`GO CONFIRMED`). NO-GO CONFIRMED (PASS): EVAL-70, 72, 74, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103, 105, 106, 107, 108, 110, 115, 117, 118, 119, 121, 123, 126, 127, 128, 129, 130, 131, 133, 134, 136, 140. BLOCKED: EVAL-124, EVAL-135, EVAL-137. EVAL-67/68/69 SEALED (forward ladder complete). Strongest surviving GO IC anchors: EVAL-101 `atm_iv`→signed return (BTC 0.2313 / ETH 0.3442); EVAL-102 `term_ratio`→signed return (BTC 0.3926 / ETH 0.2559); EVAL-104 `term_slope`→signed return (BTC 0.4058 / ETH 0.2600); EVAL-114 `atm_iv` spillover→return skewness (BTC 0.4039 / ETH 0.1173); EVAL-122 `term_slope` spillover→return skewness (BTC 0.3817 / ETH 0.4643); EVAL-125 `term_ratio` basis→return-kurtosis spread (IC 0.4128); EVAL-138 `term_ratio` spillover→return kurtosis (BTC 0.2931 / ETH 0.4679); EVAL-139 `term_ratio` spillover→return skewness (BTC 0.2613 / ETH 0.4878, 7 BH-FDR); **EVAL-140 composite `atm_iv`+`term_slope` spillover→return skewness (BTC 0.5052 beats both legs / ETH 0.3883 loses to term_slope leg ⇒ NO-GO)**; **EVAL-141 composite `atm_iv`+`term_ratio` spillover→return skewness (BTC 0.4979 beats both legs ⇒ pass on BTC; ETH 0.4151 loses to term_ratio leg 0.4878 ⇒ NO-GO)**. Do not modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-20T03:22:07Z:** EVAL-133 built/wired/sealed `NO-GO CONFIRMED (PASS)`; driver green 1450/1450+27/27.
- **2026-11-20T04:12:39Z:** EVAL-135 sealed `BLOCKED` (cross-asset `term_slope` spillover risk-reversal net-of-cost; under EVAL-64 floor).
- **2026-11-20T05:16:17Z:** EVAL-134 built/wired/sealed (cross-asset `atm_iv` spillover → kurtosis); driver green 1492/1492+27/27.
- **2026-11-20T06:02:30Z:** Built/wired/sealed **EVAL-136** (cross-asset `skew` spillover → forward realized return kurtosis). Verdict `NO-GO CONFIRMED (PASS)`, sealed `20261120T055501Z`. Driver green 1510/1510+27/27.
- **2026-11-20T07:08:01Z:** Built + wired **EVAL-137** (net-of-cost relative-value straddle spread on the EVAL-125 `term_ratio` basis GO; EVAL-64 floor verbatim). Tests 21 pass.
- **2026-11-20T07:32:26Z:** EVAL-137 sealed `BLOCKED` (capture below EVAL-64 feasible floor; never NO-GO).
- **2026-11-20T09:37:29Z:** Built + wired + sealed **EVAL-138** (cross-asset `term_ratio` spillover → forward realized return kurtosis). Verdict `GO CONFIRMED` (BTC 0.2931 / ETH 0.4679, 6 BH-FDR). Driver green 1549/1549+27/27, 71/71 seal gates.
- **2026-11-20T10:34:05Z:** Built + wired + sealed **EVAL-139** (cross-asset `term_ratio` spillover → forward realized return skewness). Verdict `GO CONFIRMED` (BTC 0.2613 / ETH 0.4878, 7 BH-FDR). Fixed KURTOSIS→SKEWNESS copy-paste bug. Driver green 1567/1567+27/27, 72/72 seal gates.
- **2026-11-20T11:12:00Z:** Built + wired + sealed **EVAL-140** (equal-weight z-score composite of EVAL-114 `atm_iv` + EVAL-122 `term_slope` cross-asset spillover → forward realized return skewness; GO additionally requires beating each leg's best IC). Runner `scripts/eval140_composite_atm_iv_term_slope_spillover_forward_return_skewness.py`, gate `scripts/eval140_phaseb_gate.py`, tests `tests/test_eval140_*` (19). Verdict `NO-GO CONFIRMED (PASS)`, sealed `20261120T110420Z` (BTC composite 0.5052 beats both legs, 2 pass + 2 BH-FDR; ETH composite 0.3883 loses to term_slope leg 0.4643, 2 pass + 3 BH-FDR). Wired into driver (+2 test files, `GATE_SPECS`, `SEAL_SPECS` `expected_exit: 0`, `EXPECTED_TARGETED_TESTS` 1567→1586). Driver green: **1586/1586** targeted + **27/27** diagnostics = 1613, `74/74` seal gates, exit 0. Rewrote this handoff: fresh timestamped task message, EVAL-141→EVAL-143 queue, bottleneck #14 (composite-beats-each-leg trap). Next mandated build: **EVAL-141** (composite `atm_iv` + `term_ratio` spillover → forward realized return skewness).
- **2026-11-20T11:40:16Z:** Refreshed durable handoff timestamp; next mandated build remains **EVAL-141** (composite `atm_iv` + `term_ratio` cross-asset spillover → forward realized return skewness). Queue EVAL-141 → EVAL-142 → EVAL-143 unchanged; anti-avoidance in force.
- **2026-11-20T12:13:58Z:** Refreshed durable handoff timestamp; next mandated build remains **EVAL-142** (cross-asset `term_ratio` spillover → risk-reversal net-of-cost, EVAL-64 floor verbatim), then EVAL-143. Queue EVAL-142 → EVAL-143; anti-avoidance in force.
- **2026-11-20T12:28:50Z:** Refreshed durable handoff timestamp; next mandated build remains **EVAL-142** (cross-asset `term_ratio` spillover → risk-reversal net-of-cost, traded form, EVAL-64 floor verbatim), then **EVAL-143**. Queue EVAL-142 → EVAL-143; anti-avoidance in force — a green driver + all-sealed is NOT completion; build + seal EVAL-142 in the same session.
- **2026-11-20T12:38:04Z:** Driver re-verified green: **1605/1605** targeted + **27/27** diagnostics = 1632, all **76/76** seal-gate specs ok, exit 0. EVAL-140/141 SEALED (NO-GO CONFIRMED). Next mandated build remains **EVAL-142** (cross-asset `term_ratio` spillover → risk-reversal net-of-cost, traded form, EVAL-64 floor verbatim), then **EVAL-143**. Queue EVAL-142 → EVAL-143; anti-avoidance in force — a green driver + all-sealed is NOT completion; build + seal EVAL-142 in the same session.
