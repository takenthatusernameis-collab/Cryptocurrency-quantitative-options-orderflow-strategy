# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-18T16:45:00Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor). PRIMARY TASK: BUILD + SEAL EVAL-100 (`scripts/eval100*`, `tests/test_eval100*`) per §NEXT MANDATORY BUILD, then re-run full driver green; do not timestamp-only carry.**
>
> **VERIFIED STATE (2026-11-18T16:42:05Z, this session):** EVAL-99 is **BUILT, WIRED, and SEALED** (`GO CONFIRMED`, prereg+COMBINED `20261118T163647Z`, task `INIT-2026-11-18T12:10:00Z-EVAL99-SINGLE-ASSET-TERM-SLOPE-FORWARD-TAIL-ASYMMETRY`, seal-gate exit 0, idempotent gate exit 0). Runner `scripts/eval99_single_asset_term_slope_forward_tail_asymmetry.py`, gate `scripts/eval99_phaseb_gate.py`, tests `tests/test_eval99_single_asset_term_slope_forward_tail_asymmetry.py` + `tests/test_eval99_phaseb_gate.py` (18/18 pass with `PYTHONPATH=$PWD/.venv-deps`), driver wiring (`TARGETED_TEST_FILES` +2, `EXPECTED_TARGETED_TESTS` 747, `GATE_SPECS`/`SEAL_SPECS`/readiness) are in-tree. Full driver `python3 scripts/eval67_prethreshold_progress.py --execute` completed green (exit 0, log ended with `readiness_written: true`) at **2026-11-18T16:42:05Z**: env OK, `targeted_tests: 747/747` (rc 0), `diagnostic_tests: 27/27` (rc 0), `total_tests_passed: 774`; all EVAL-70..99 gates `SEALED`; EVAL-67 `NOT_DUE` (overlap **111260.064s**, disjoint=false), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`; all 34 seal-gate specs ok. Readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json` (`updated_at 2026-11-18T16:42:05Z`). (Readiness records counts/gate/ seal-gate state; treat green = driver exit 0 + counts match + all gate/seal specs ok.)
>
> **EVAL-99 result (sealed):** single-asset near-minus-far ATM IV **term slope** (`term_slope = IV(near)-IV(far)`, EVAL-74 `_term_bars`/term floor reused verbatim) → forward own-asset **return-tail asymmetry** (EVAL-85 `_forward_return_tail_asym` reused verbatim). Floor ok (BTC/ETH). 12 configs (2 bars × 3 horizons), verdict **`GO CONFIRMED` — portable**. **BTC:** best IC **0.259125** at `term_slope::bar60.0::h72`, **3/6 pass** (`bar60` h6/h24/h72). **ETH:** best IC **0.350705** at `term_slope::bar300.0::h72`, **3/6 pass** (`bar60` h24/h72 + `bar300` h72). **10 pooled BH-FDR rejections**. Monotone IC growth with horizon at 60s bars on both assets — the first portable term-structure→tail-asymmetry cell. Distinct from EVAL-74/84/85/87/96/98. Do not re-litigate or re-seal EVAL-99.
>
> **Forward ladder (hard physics, not fixable pre-threshold):** EVAL-67 `NOT_DUE` exit 10 (disjoint=false, overlap decreasing; **111260.064s** at 2026-11-18T16:42:05Z), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`. Threshold **2026-11-20T00:00:00Z**; earliest disjoint capture end **2026-11-19T18:08:16Z**. External `*/5` cron owns routine polling. Do not spawn capture bridges/waiters.
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver now (idempotent; confirms green, refreshes readiness):
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Require exit 0, `targeted_tests: 747/747` (or higher if more built/sealed), `diagnostic_tests: 27/27`, EVAL-70..99 `SEALED`, EVAL-67 `NOT_DUE`/EVAL-68 `WAIT_EVAL67`/EVAL-69 `WAIT_EVAL68` pre-threshold, and all seal-gate specs ok. If any arbiter is `DUE`(20) execute it; if `FAILED`(1) fix and rerun.
>
> **ANTI-AVOIDANCE RULE (mandatory):** a green driver plus NOT_DUE/WAIT is **not** session completion. With EVAL-70..99 sealed, **EVAL-100 is not built/wired/sealed** (`scripts/eval100*` and `tests/test_eval100*` absent). If the driver is green and the ladder remains NOT_DUE/WAIT, **build + seal EVAL-100 now** (§NEXT MANDATORY BUILD), then re-run the driver green. After EVAL-100 seals, take the first non-sealed alternate in §NEXT MANDATORY BUILD. Do not do a timestamp-only carry, do not create competing handoffs, do not enumerate `research_state/`.
>
> **Repo-priority reading:** on-charter ladder EVAL-02..66 is **CLOSED**. Do not re-run, re-litigate, re-seal, or edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..99 artifacts or `src/`. Append-only for new authorized work. No synthetic data, no live trading, no floor weakening.

## NEXT MANDATORY BUILD — EVAL-100 (fully specified; build this if the driver is green and the ladder is NOT_DUE/WAIT)

**EVAL-100 — single-asset `term_ratio` surface → forward own-asset return-tail asymmetry.** Economic question: does the causal near-to-far ATM IV **term ratio** (`term_ratio = IV(near)/IV(far) - 1`) predict that same underlying's subsequent forward **return-tail asymmetry**? Distinct from sealed EVAL-74 (`term_ratio`→own RV *level*), EVAL-84 (`term_ratio`→own vol-of-vol), EVAL-85 (`skew`→own tail asymmetry), EVAL-87 (`atm_iv`→own tail asymmetry), EVAL-98 (`term_ratio`→own VRP), and EVAL-99 (`term_slope`→own tail asymmetry). Predictiveness only — **no traded-form or monetization claim**.

- **Runner:** `scripts/eval100_single_asset_term_ratio_forward_tail_asymmetry.py`
- **Gate:** `scripts/eval100_phaseb_gate.py` (`SEALED`/`DUE`(20)/`FAILED`(1), no `NOT_DUE`).
- **Tests:** `tests/test_eval100_single_asset_term_ratio_forward_tail_asymmetry.py` and `tests/test_eval100_phaseb_gate.py` (mirror EVAL-99's structure exactly — 18 tests — but signal `term_ratio`).
- **Task ID:** `INIT-2026-11-18T16:45:00Z-EVAL100-SINGLE-ASSET-TERM-RATIO-FORWARD-TAIL-ASYMMETRY`; task label `EVAL100-SINGLE-ASSET-TERM-RATIO-FORWARD-TAIL-ASYMMETRY`. Artifact stamp must be ≥ task floor.
- **Signal (per underlying):** `e74._term_bars(capture, bar_seconds=...)` → `term_ratio` (EVAL-74 reconstruction verbatim); forward-fill `e71._forward_fill`, expanding-zscore `e61.expanding_zscore(filled, e62.ZWINDOW)`.
- **Target (per underlying):** forward **return-tail asymmetry** over bars `k+1..k+H`, horizons `H ∈ {6, 24, 72}`, reused **verbatim** as `e85._forward_return_tail_asym` (exactly as EVAL-99; do not redefine).
- **Grid:** signal `term_ratio` only; `bar_seconds ∈ {60, 300}`; `H ∈ {6, 24, 72}` (6 configs × 2 assets). Spearman rank IC; H1 `IC > 0` (higher near/far IV ratio → more positively asymmetric forward tails).
- **GO bar:** on BOTH BTC and ETH, at least one config with IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, ≥120 usable pairs, and pooled BH-FDR rejection; else `NO-GO CONFIRMED (PASS)`.
- **Floor (pre-registered; NOT a weakening):** reuse sealed **EVAL-74 term floor verbatim** (`e74._underlying_term_floor`, min 2 underlyings), applied to BOTH BTC and ETH. Below floor ⇒ seal `EVAL_100_..._BLOCKED_<UTC>`, never NO-GO. Do not weaken EVAL-64.
- **Driver wiring:** add both test files to `TARGETED_TEST_FILES`; add EVAL-100 to `GATE_SPECS` (`wait_phase:"DUE"`) and `SEAL_SPECS` (`expected_exit:1` until sealed, then `0`); bump `EXPECTED_TARGETED_TESTS` by the exact new test count (18 → 765); add `eval100` to readiness gate handling/notes. Re-run full driver green.
- **Seal:** `python3 scripts/eval100_phaseb_gate.py --execute`, require exit 0, set `SEAL_SPECS` `expected_exit` to 0, re-run full driver green.

**Alternates after EVAL-100 (first non-sealed cell; same template/stats, no src edits):** (a) **EVAL-101** single-asset `atm_iv` level → forward own-asset **signed return mean** (EVAL-81 directional target reused verbatim; distinct from EVAL-87 atm_iv→tail asymmetry, EVAL-71 atm_iv→RV level, EVAL-95 atm_iv→vol-of-vol). (b) **EVAL-102** single-asset `term_ratio` → forward own-asset **signed return mean** (term-signal × EVAL-81 target). Do **not** test `atm_iv`→VRP (mechanical overlap: `atm_iv_k` component of `VRP_k`), do not test `term_ratio`→VRP again (EVAL-98 sealed), do not rebuild a collar (EVAL-76), do not re-litigate sealed cells, do not weaken EVAL-64, do not touch `src/`.

## RUNNABLE-NOW CAMPAIGNS — EVAL-70..99 ALL SEALED

Predictiveness GOs (no net-of-cost monetization): EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`, `20261118T005436Z`), 88, 90, 91, 93, 97, **99**. NO-GO CONFIRMED (PASS): EVAL-70, 72, 74, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98. Traded-form taxonomy complete/all NO-GO (straddle 72/75, risk reversal 76, butterfly 82, relative-value straddle spread 80). EVAL-92 atm_iv-basis relative-VRP (mechanical sign overlap). EVAL-94 term-ratio-basis relative-RV (best IC 0.0942, no FDR). EVAL-95 atm_iv→own vol-of-vol (not portable). EVAL-96 term_slope→own VRP (BTC-only). EVAL-97 skew→own vol-of-vol (portable GO). EVAL-98 term_ratio→own VRP (BTC-only). EVAL-99 term_slope→own tail asymmetry (portable GO, 10 BH-FDR). These are idempotent no-ops once sealed; do not re-run as substitute for new work.

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
- EVAL-70..100 gates: `SEALED`(0) idempotent; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- After fully-refreshed green driver: env OK, `747/747` targeted (or higher if more built/sealed), `27/27` diagnostics, all EVAL-70..99 `SEALED` and EVAL-100 `SEALED` once built, EVAL-67 `NOT_DUE` / EVAL-68 `WAIT_EVAL67` / EVAL-69 `WAIT_EVAL68` pre-threshold, all seal-gate specs ok, driver exit 0.

## PRE-THRESHOLD HEAVY-WORK RULE

Run full driver with `--execute` every session. If green and ladder still NOT_DUE/WAIT, build and seal EVAL-100 (then first non-sealed alternate). Timestamp-only carry prohibited. No capture bridges/waiters; cron owns polling. Forward wait is hard physics until disjoint window.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge/liveness churn — removed.
2. Competing handoff pointers/copies — removed; this file is the single handoff.
3. EVAL-68/69 design-only gaps — removed.
4. Pre-threshold "no heavy work left" avoidance — removed by EVAL-70..99 and renewed by mandatory EVAL-100.
5. Manual pre-threshold loop/timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
6. Stale campaign test assumptions — `tests/test_campaign_resume.py` checks current campaigns.
7. Handoff bloat — consolidated; no timestamped copies, no `research_state/` enumeration.
8. EVAL-94 staging gap — removed (wired + sealed).
9. EVAL-95 staging gap — removed (built/wired/sealed).
10. EVAL-96 staging gap — removed (built/wired/sealed `20261118T110248Z`).
11. EVAL-97 staging gap — removed (built/wired/sealed `20261118T113811Z`, driver green 711/711).
12. EVAL-98 staging gap — removed (built/wired/sealed `NO-GO CONFIRMED (PASS)` at `20261118T115945Z`; driver green 729/729+27/27).
13. **EVAL-99 staging gap — removed (this session).** Built/wired/sealed `GO CONFIRMED` at `20261118T163647Z`; post-seal full driver refresh green at **2026-11-18T16:42:05Z** (`747/747` targeted, `27/27` diagnostics, 34 seal-gate specs ok, readiness written). No sealed prior artifacts or `src/` modified.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..99 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting; EVAL-68 acquires BTC+ETH in ONE process; EVAL-69 acquires nothing.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs (EVAL-67/68/69 and EVAL-70..100 in `SEAL_SPECS`); do not use retired compact task IDs.
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
python3 scripts/eval99_phaseb_gate.py

# 3) At/after 2026-11-20T00:00:00Z, or on DUE/FAILED:
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

Driver runs env check, all targeted/diagnostic suites, all campaign arbiters in order, any required `--execute`, all seal-gate specs, and readiness refresh. Use its output and `research_state/EVAL_67_PREWINDOW_READINESS.json` as verified state.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, and 70..99 sealed. EVAL-63 never sealed. EVAL-67/68/69 forward-gated (NOT_DUE/WAIT pre-threshold). Predictiveness GOs: EVAL-71,73,77,83,85,86,88,90,91,93,97,99; EVAL-87 `GO/BLOCKED` (`20261118T005436Z`). Traded-form monetization complete/all-NO-GO. EVAL-94,95,96,98 NO-GO (96/98 BTC-only, not portable). Do not modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-18T09:49:46Z:** EVAL-94 wired + sealed NO-GO; driver green 657/657+27/27.
- **2026-11-18T10:25:24Z:** EVAL-95 built + sealed NO-GO; driver green 675/675+27/27.
- **2026-11-18T11:19:01Z:** EVAL-96 built + sealed NO-GO (`20261118T110248Z`), wired 693 expected.
- **2026-11-18T11:43:24Z:** EVAL-97 built + sealed GO (`20261118T113811Z`); driver green 711/711+27/27.
- **2026-11-18T12:08:00Z:** EVAL-98 built + sealed NO-GO (`20261118T115945Z`), wired 729 expected.
- **2026-11-18T12:50:00Z:** handoff refreshed; driver green 729/729+27/27; EVAL-99 mandated.
- **2026-11-18T16:45:00Z (this session — EVAL-99 built, sealed GO, handoff refreshed, EVAL-100 mandated):** Built runner/gate/tests for EVAL-99 (`term_slope`→forward return-tail asymmetry) and wired the driver (`TARGETED_TEST_FILES` +2, `EXPECTED_TARGETED_TESTS` 747, `GATE_SPECS`/`SEAL_SPECS`/readiness). New tests 18/18 pass. `python3 scripts/eval99_phaseb_gate.py --execute` → **`GO CONFIRMED`**, sealed prereg+COMBINED `20261118T163647Z`, seal-gate exit 0, idempotent gate exit 0. Result: BTC best IC **0.259125** (`bar60` h72, 3/6 pass), ETH best IC **0.350705** (`bar300` h72, 3/6 pass), **10 pooled BH-FDR rejections** — first portable term-structure→tail-asymmetry cell. Full driver `--execute` green at **2026-11-18T16:42:05Z**: env OK, **747/747 targeted + 27/27 diagnostics = 774**, EVAL-70..99 `SEALED`, EVAL-67 `NOT_DUE` overlap **111260.064s** (disjoint=false), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`, **34/34 seal-gate specs ok**, readiness written. Handoff mandates building + sealing EVAL-100 (§NEXT MANDATORY BUILD) if the ladder stays NOT_DUE/WAIT. No sealed prior artifacts or `src/` modified.
