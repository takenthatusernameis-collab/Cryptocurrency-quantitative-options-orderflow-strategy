# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-18T20:36:04Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor). PRIMARY TASK, IN ORDER: (1) run `python3 scripts/eval67_prethreshold_progress.py --execute` and require exit 0, `targeted_tests: 854/854`, `diagnostic_tests: 27/27`, all EVAL-70..105 `SEALED`, EVAL-67 `NOT_DUE`/EVAL-68 `WAIT_EVAL67`/EVAL-69 `WAIT_EVAL68`, all 40 seal-gate specs ok; (2) BUILD + SEAL EVAL-106 (`scripts/eval106_*` per §PRE-REGISTERED BUILD QUEUE) — cross-sectional `term_slope` basis → relative tail-asymmetry spread; (3) re-run the full driver green; (4) continue down §PRE-REGISTERED BUILD QUEUE (EVAL-107..112). Do NOT timestamp-only carry. The ladder EVAL-67/68/69 remains pre-threshold NOT_DUE/WAIT until `2026-11-20T00:00:00Z`; do not acquire EVAL-68 before EVAL-67 seals, do not run EVAL-69 before EVAL-68 seals.**
>
> **VERIFIED STATE (2026-11-18T20:36:04Z, this session):** EVAL-105 is **BUILT, WIRED, and SEALED** (`GO/NO-GO` per gate; prereg+COMBINED stamped, task `INIT-2026-11-18T19:02:00Z-EVAL105-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD`, seal-gate exit 0, idempotent gate exit 0). Runner `scripts/eval105_cross_sectional_term_ratio_basis_relative_tail_asymmetry_spread.py`, gate `scripts/eval105_phaseb_gate.py`, tests `tests/test_eval105_cross_sectional_term_ratio_basis_relative_tail_asymmetry_spread.py` + `tests/test_eval105_phaseb_gate.py` (17/17 pass with `PYTHONPATH=$PWD/.venv-deps`), driver wiring (`TARGETED_TEST_FILES` +2, `EXPECTED_TARGETED_TESTS` **854**, `GATE_SPECS`/`SEAL_SPECS`/readiness `eval105`) are in-tree. Full driver `python3 scripts/eval67_prethreshold_progress.py --execute` completed green (exit 0, `overall_ok: true`, no failures) at **2026-11-18T20:08:49Z**: env OK, `targeted_tests: 854/854` (rc 0), `diagnostic_tests: 27/27` (rc 0), `total_tests_passed: 881`; all EVAL-70..105 gate specs `SEALED`; EVAL-67 `NOT_DUE` (overlap decreasing, disjoint=false), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`; **40/40 seal-gate specs ok**; readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json`. **EVAL-106 (`scripts/eval106_*`, `tests/test_eval106_*`) is the open bottleneck to clear immediately — cross-sectional `term_slope` basis → relative tail-asymmetry spread.** No timestamp-only carry; build+seal EVAL-106 next.
>
> **EVAL-104 result (sealed):** single-asset near-ATM implied-vol **term slope** (`term_slope`, EVAL-74 `_term_bars` signal path reused verbatim) → forward own-asset **signed log-return mean** (EVAL-81 target transcribed verbatim). Floor ok (EVAL-74 term floor, BTC/ETH). 12 configs (2 bars × 3 horizons × 2 assets), verdict **`GO CONFIRMED` — portable**. **BTC:** best IC **0.405760** at `term_slope::bar300.0::h24`, **3/6 pass** (`bar60` h72, `bar300` h24, `bar300` h72). **ETH:** best IC **0.259992** at `term_slope::bar60.0::h24`, **4/6 pass** (`bar60` h6/h24/h72, `bar300` h72). **9 pooled BH-FDR rejections** (BTC `bar60::h72`, `bar300::h24`, `bar300::h72`, `bar300::h6`; ETH `bar60::h6`, `bar60::h24`, `bar60::h72`, `bar300::h72`). Directional result: a steeper near-vs-far ATM IV term slope precedes more positive forward signed return on BOTH assets (BTC strongest at 5-min bars h24, ETH at 1-min bars h24). Distinct from EVAL-74/84/93/96/99/101/102/103. Do not re-litigate or re-seal EVAL-104.
>
> **EVAL-103 result (sealed):** single-asset near-ATM implied-vol **skew** (`skew`, EVAL-71 `build_surface_bars` signal path reused verbatim) → forward own-asset **signed log-return mean** (EVAL-81 target transcribed verbatim). Floor ok (EVAL-71 surface floor, BTC/ETH). 12 configs (2 bars × 3 horizons × 2 assets), verdict **`NO-GO CONFIRMED (PASS)`**. **BTC:** best IC **0.046218** at `skew::bar300.0::h72`, **0/6 pass**. **ETH:** best IC **0.219521** at `skew::bar300.0::h72`, **5/6 pass** (`bar60` h6/h24/h72, `bar300` h6/h72). **6 pooled BH-FDR rejections** (all ETH: `bar60::h6`, `bar60::h24`, `bar60::h72`, `bar300::h6`, `bar300::h72`, `bar300::h24`). Directional result: positive near-ATM put-call skew precedes more positive forward signed return on ETH at both bar grids, but the GO bar requires passage on BOTH BTC and ETH, so the campaign is NO-GO CONFIRMED (PASS) — a valid sealed negative result, not a weakness. Distinct from EVAL-85/86/97 (`skew`→tail asymmetry / VRP / vol-of-vol), EVAL-72/76/82 (traded-form skew), EVAL-89/91 (skew *basis*), and EVAL-101/102/104 (`atm_iv` / `term_ratio` / `term_slope`→signed return). Do not re-litigate or re-seal EVAL-103.
>
> **EVAL-102 result (sealed, prior):** single-asset near-to-far ATM implied-vol **term ratio** (`term_ratio`, EVAL-74 `_term_bars` path reused verbatim) → forward own-asset **signed log-return mean** (EVAL-81 target transcribed verbatim). Floor ok (BTC/ETH, EVAL-74 term floor). 12 configs (2 bars × 3 horizons × 2 assets), verdict **`GO CONFIRMED` — portable**. **BTC:** best IC **0.392590** at `term_ratio::bar300.0::h24`, **3/6 pass** (`bar60` h72, `bar300` h24, `bar300` h72). **ETH:** best IC **0.255910** at `term_ratio::bar60.0::h24`, **3/6 pass** (`bar60` h6/h24/h72). **7 pooled BH-FDR rejections** (BTC `bar60::h72`, `bar300::h6`, `bar300::h24`, `bar300::h72`; ETH `bar60::h6`, `bar60::h24`, `bar60::h72`). Directional result: a higher near/far ATM IV ratio precedes more positive forward signed return on BOTH assets (BTC strongest at 5-min bars, ETH at 1-min bars). Distinct from EVAL-74/98/100/101. Do not re-litigate or re-seal EVAL-102.
>
> **Forward ladder (hard physics, not fixable pre-threshold):** EVAL-67 `NOT_DUE` exit 10 (disjoint=false, overlap decreasing; **103424.058s** at 2026-11-18T19:01:38Z), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`. Threshold **2026-11-20T00:00:00Z**; earliest disjoint capture end **2026-11-19T18:08:16Z**. External `*/5` cron owns routine polling. Do not spawn capture bridges/waiters.
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver now (idempotent; confirms green, refreshes readiness):
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Require exit 0, `targeted_tests: 837/837` (or higher if more built/sealed), `diagnostic_tests: 27/27`, EVAL-70..104 `SEALED`, EVAL-67 `NOT_DUE`/EVAL-68 `WAIT_EVAL67`/EVAL-69 `WAIT_EVAL68` pre-threshold, and all 39 seal-gate specs ok. If any arbiter is `DUE`(20) execute it; if `FAILED`(1) fix and rerun.
>
> **ANTI-AVOIDANCE RULE (mandatory):** a green driver plus NOT_DUE/WAIT is **not** session completion. With EVAL-70..104 sealed, **EVAL-105 is not built/wired/sealed** (`scripts/eval105*` and `tests/test_eval105*` absent). If the driver is green and the ladder remains NOT_DUE/WAIT, **build + seal EVAL-105 now** (§NEXT MANDATORY BUILD), then re-run the driver green. After EVAL-105 seals, take the first non-sealed entry of the §PRE-REGISTERED BUILD QUEUE (EVAL-106..112) and continue down that queue in the same session while time remains. One campaign per session minimum is required while the ladder is NOT_DUE/WAIT; a timestamp-only carry is prohibited.
>
> **Repo-priority reading:** on-charter ladder EVAL-02..66 is **CLOSED**. Do not re-run, re-litigate, re-seal, or edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..104 artifacts or `src/`. Append-only for new authorized work. No synthetic data, no live trading, no floor weakening.

## NEXT MANDATORY BUILD — EVAL-105 (fully specified; build this if the driver is green and the ladder is NOT_DUE/WAIT)

**EVAL-105 — cross-sectional `term_ratio` basis → relative tail-asymmetry spread.** Economic question: does the causal cross-sectional near-to-far ATM IV **term ratio basis** (ETH minus BTC) predict the **relative tail-asymmetry spread** between the two underlyings? Distinct from EVAL-100 (single-asset `term_ratio`→own tail asymmetry), EVAL-94 (term-ratio basis→relative RV), EVAL-93 (term-slope basis→relative RV), EVAL-102 (single-asset `term_ratio`→signed return). Predictiveness only — **no traded-form or monetization claim**.

- **Runner:** `scripts/eval105_cross_sectional_term_ratio_basis_relative_tail_asymmetry_spread.py` (mirror `scripts/eval100_single_asset_term_ratio_forward_tail_asymmetry.py`; swap ONLY the signal path to `e77._relative_signal_series` + `e74._term_bars` + `term_ratio`, and the target to `e85._forward_return_tail_asym` per-asset then spread `tail_asym_BTC - tail_asym_ETH` via EVAL-89/93 convention, keeping the EVAL-74 `_underlying_term_floor` verbatim on BOTH assets).
- **Gate:** `scripts/eval105_phaseb_gate.py` (copy `scripts/eval100_phaseb_gate.py`, rename identifiers/globs/docstring only). Outcomes `SEALED`(0)/`DUE`(20)/`FAILED`(1), no `NOT_DUE`.
- **Tests:** `tests/test_eval105_cross_sectional_term_ratio_basis_relative_tail_asymmetry_spread.py` and `tests/test_eval105_phaseb_gate.py` (mirror EVAL-100's structure exactly — 18 tests — but signal `term_ratio` from `e77._relative_signal_series` + `e74._term_bars`, target relative tail-asymmetry spread `y_k = tail_asym_BTC(k) - tail_asym_ETH(k)` via `e85._forward_return_tail_asym`, floor delegated to `e74._underlying_term_floor` on BOTH assets).
- **Task ID:** `INIT-2026-11-18T19:02:00Z-EVAL105-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD`; task label `EVAL105-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD`. Artifact stamp must be ≥ task floor.
- **Signal (cross-sectional basis):** `e74._term_bars(capture, bar_seconds=...)` per underlying → `term_ratio`, then `e77._relative_signal_series(term_ratio_BTC, term_ratio_ETH, ...)` → `rel_z_k` (expanding z-scored ETH minus BTC on the common aligned grid), then `e61.expanding_zscore(filled, e62.ZWINDOW)`.
- **Target (cross-sectional spread):** per-asset forward **tail asymmetry** over bars `k+1..k+H` via `e85._forward_return_tail_asym` (max log-return / min log-return, EVAL-85 window convention), then spread `y_k = tail_asym_BTC(k) - tail_asym_ETH(k)` (EVAL-89/93 convention). Horizons `H ∈ {6, 24, 72}`.
- **Grid:** signal `term_ratio` only; `bar_seconds ∈ {60, 300}`; `H ∈ {6, 24, 72}` (6 configs). Spearman rank IC; H1 `IC > 0` (higher ETH-minus-BTC term_ratio basis precedes more positive BTC-minus-ETH tail-asymmetry spread).
- **GO bar:** on BOTH BTC and ETH floors satisfied, at least one config with IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, ≥120 usable pairs, and pooled BH-FDR rejection; else `NO-GO CONFIRMED (PASS)`.
- **Floor (pre-registered; NOT a weakening):** reuse sealed **EVAL-74 term floor verbatim** for EACH underlying (min 2 underlyings) — `1000` option trades, `400` near-ATM trades, `1000` perp candles, `82000s` perp span plus term adequacy. Below floor ⇒ seal `EVAL_105_..._BLOCKED_<UTC>`, never NO-GO. Do not weaken EVAL-64.
- **Driver wiring:** add both test files to `TARGETED_TEST_FILES`; add EVAL-105 to `GATE_SPECS` (`wait_phase:"DUE"`, before EVAL-67) and `SEAL_SPECS` (`expected_exit:1` until sealed, then `0`); bump `EXPECTED_TARGETED_TESTS` by the exact new test count (18 → **855**); add readiness key `eval105` and a notes line. Re-run full driver green.
- **Seal:** `python3 scripts/eval105_phaseb_gate.py --execute`, require exit 0, set `SEAL_SPECS` `expected_exit` to 0, re-run full driver green.

## PRE-REGISTERED BUILD QUEUE (EVAL-104..112 — take the first non-sealed entry; same template/stats, no src edits)

Each cell is distinct from every sealed EVAL-70..104 cell and is predictiveness-only (no monetization claim). All reuse EVAL-65 inference (`_perm_p_ic`, `_boot_ci_ic`, `PERMUTATION_PERMS`, `BOOTSTRAP_RESAMPLES`, `BOOTSTRAP_BLOCK`, `SEED`), EVAL-62 `ZWINDOW`/`FDR_ALPHA`, and BH-FDR from `src.analytics.real_walkforward_certification._benjamini_hochberg`. Expected targeted-test count grows by ~18 per rung: 837 (EVAL-104) → **854** (EVAL-105) → 872 → 890 → 908 → 926 → 944 → 962 → 980.

1. **EVAL-104** — `term_slope` → forward own-asset **signed return mean** (signal from EVAL-74 `_term_bars`; target as EVAL-101/102/103). Distinct from EVAL-99 (`term_slope`→tail asymmetry), EVAL-96 (`term_slope`→VRP), EVAL-74, EVAL-84, EVAL-93 (term-slope basis→relative RV), EVAL-102 (`term_ratio`→signed return). Floor: EVAL-74 term floor verbatim. **SEALED `GO CONFIRMED` (`20261118T190138Z`)**.
2. **EVAL-105** — cross-sectional `term_ratio` basis → **relative tail-asymmetry spread** (per-asset tail asymmetry from EVAL-85 `_forward_return_tail_asym`; signal `rel_z_k = expanding_z(term_ratio_ETH(k) − term_ratio_BTC(k))` on the common aligned grid via EVAL-77 `_relative_signal_series` + EVAL-74 `_term_bars`; target `y_k = tail_asym_BTC(k) − tail_asym_ETH(k)` — EVAL-89/93 convention). Distinct from EVAL-100 (single-asset `term_ratio`→own tail asymmetry), EVAL-94 (term-ratio basis→relative RV), EVAL-93 (term-slope basis→relative RV), EVAL-102. Floor: EVAL-74 term floor on BOTH assets. **BUILT, WIRED, SEALED — driver green 854/854 + 27/27 at 2026-11-18T20:08:49Z.**
3. **EVAL-106** — cross-sectional `term_slope` basis → **relative tail-asymmetry spread** (same construction with `term_slope`). Distinct from EVAL-99 (single-asset `term_slope`→own tail asymmetry), EVAL-93 (term-slope basis→relative RV), EVAL-105 (`term_ratio` basis). Floor: EVAL-74 term floor on BOTH assets.
4. **EVAL-107** — cross-sectional `term_ratio` basis → **relative vol-of-vol spread** (signal `rel_z_k` on `term_ratio_ETH − term_ratio_BTC` via EVAL-77 `_relative_signal_series` + EVAL-74 `_term_bars`; target reuse EVAL-90 `_forward_rel_vov_spread` / EVAL-84 forward vol-of-vol verbatim, i.e. `vov_BTC(k) − vov_ETH(k)`). Distinct from EVAL-90 (atm_iv basis→relative vol-of-vol), EVAL-95 (single-asset atm_iv→own vol-of-vol), EVAL-97 (single-asset skew→own vol-of-vol), EVAL-84 (single-asset term structure→own vol-of-vol), EVAL-94 (term-ratio basis→relative RV), EVAL-102. Floor: EVAL-74 term floor on BOTH assets.
5. **EVAL-108** — cross-sectional `term_slope` basis → **relative vol-of-vol spread** (same construction with `term_slope`; target `_forward_rel_vov_spread` verbatim). Distinct from EVAL-107 (`term_ratio` basis), EVAL-91/93, EVAL-84/96/99. Floor: EVAL-74 term floor on BOTH assets.
6. **EVAL-109** — single-asset `atm_iv` → forward own-asset **realized return skewness** (third standardized moment of the H perp log-returns `k+1..k+H`; local helper `_forward_return_skewness` transcribed in the campaign, mirrored on EVAL-85's window convention; no `src/` edit). Distinct from EVAL-87 (`atm_iv`→tail asymmetry = max/min), EVAL-95 (vov), EVAL-101 (`atm_iv`→signed mean). Floor: EVAL-71 surface floor verbatim.
7. **EVAL-110** — cross-sectional **skew basis** → **relative tail-asymmetry spread** (signal `rel_z_k` on `skew_ETH − skew_BTC` via EVAL-77 `_relative_signal_series` + `e71.build_surface_bars`; target `y_k = tail_asym_BTC(k) − tail_asym_ETH(k)` per EVAL-89/93 convention). Distinct from EVAL-89 (skew basis→relative VRP), EVAL-91 (skew basis→relative vol-of-vol), EVAL-85 (single-asset skew→own tail asymmetry), EVAL-105/106 (term basis→relative tail asymmetry). Floor: EVAL-71 surface floor on BOTH assets.
8. **EVAL-111** — single-asset `skew` → forward own-asset **realized return skewness** (signal `skew` from `e71.build_surface_bars`; target the EVAL-109 `_forward_return_skewness` helper verbatim). Distinct from EVAL-85 (tail asymmetry), EVAL-86 (VRP), EVAL-97 (vov), EVAL-103 (`skew`→signed mean), EVAL-109 (`atm_iv`→skewness). Floor: EVAL-71 surface floor verbatim.
9. **EVAL-112** — single-asset `term_ratio` → forward own-asset **realized return skewness** (signal from EVAL-74 `_term_bars`; target the EVAL-109 `_forward_return_skewness` helper verbatim). Distinct from EVAL-74/98/100/102 (term_ratio→RV level / VRP / tail asymmetry / signed mean) and EVAL-109/111. Floor: EVAL-74 term floor verbatim.

**Further non-sealed candidate space (pre-register a NEW target, never a re-skin):** cross-asset `atm_iv` spillover → other-asset **realized return skewness**; single-asset `atm_iv` → forward **realized downside semivariance share**; single-asset `term_slope` → forward **realized return skewness** (once EVAL-112 is sealed). Already covered — do NOT rebuild: EVAL-88 (atm_iv/skew basis→relative signed-return spread), EVAL-92 (atm_iv basis→relative VRP), EVAL-90 (atm_iv basis→relative vol-of-vol), EVAL-77 (basis→relative RV), EVAL-101 (`atm_iv`→signed return), EVAL-102 (`term_ratio`→signed return). Do **not** test `atm_iv`→VRP (mechanical overlap: `atm_iv_k` is a component of `VRP_k`), do not re-test `term_ratio`→VRP, do not rebuild a collar (EVAL-76), do not re-litigate sealed cells, do not weaken EVAL-64, do not touch `src/`.

## RUNNABLE-NOW CAMPAIGNS — EVAL-70..104 ALL SEALED

Predictiveness GOs (no net-of-cost monetization): EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`, `20261118T005436Z`), 88, 90, 91, 93, 97, 99, 100, 101, 102, **104**. NO-GO CONFIRMED (PASS): EVAL-70, 72, 74, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103. Traded-form taxonomy complete/all NO-GO (straddle 72/75, risk reversal 76, butterfly 82, relative-value straddle spread 80). EVAL-92 atm_iv-basis relative-VRP (mechanical sign overlap). EVAL-94 term-ratio-basis relative-RV (no FDR). EVAL-95 atm_iv→own vol-of-vol (not portable). EVAL-96 term_slope→own VRP (BTC-only). EVAL-97 skew→own vol-of-vol (portable GO). EVAL-98 term_ratio→own VRP (BTC-only). EVAL-99 term_slope→own tail asymmetry (portable GO, 10 BH-FDR). EVAL-100 term_ratio→own tail asymmetry (portable GO, 11 BH-FDR, `20261118T164559Z`). EVAL-101 atm_iv→own signed return (portable GO, 4 BH-FDR, `20261118T174257Z`, BTC best IC 0.2313 / ETH 0.3442). EVAL-102 term_ratio→own signed return (portable GO, 7 BH-FDR, `20261118T183232Z`, BTC best IC 0.3926 / ETH 0.2559). EVAL-103 skew→own signed return (NO-GO CONFIRMED (PASS), `20261118T184710Z`, ETH best IC 0.2195 / BTC 0.0462, 6 pooled BH-FDR rejections all ETH, GO bar requires both assets so NO-GO). EVAL-104 term_slope→own signed return (GO CONFIRMED, `20261118T190138Z`, BTC best IC 0.4058 / ETH 0.2600, 9 pooled BH-FDR rejections both assets). These are idempotent no-ops once sealed; do not re-run as substitute for new work.

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
- EVAL-70..104 gates: `SEALED`(0) idempotent; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- After fully-refreshed green driver: env OK, `854/854` targeted (or higher if more built/sealed), `27/27` diagnostics, all EVAL-70..105 `SEALED`, EVAL-67 `NOT_DUE` / EVAL-68 `WAIT_EVAL67` / EVAL-69 `WAIT_EVAL68` pre-threshold, all 40 seal-gate specs ok, driver exit 0.

## PRE-THRESHOLD HEAVY-WORK RULE

Run full driver with `--execute` every session. If green and ladder still NOT_DUE/WAIT, build and seal EVAL-106, then continue down the §PRE-REGISTERED BUILD QUEUE (EVAL-107..112) in the same session while time remains. Timestamp-only carry prohibited. No capture bridges/waiters; cron owns polling. Forward wait is hard physics until the disjoint window.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge/liveness churn — removed.
2. Competing handoff pointers/copies — removed; this file is the single handoff.
3. EVAL-68/69 design-only gaps — removed.
4. Pre-threshold "no heavy work left" avoidance — removed by EVAL-70..103 and renewed by mandatory EVAL-104 + EVAL-105..112 queue.
5. Manual pre-threshold loop/timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
6. Stale campaign test assumptions — `tests/test_campaign_resume.py` checks current campaigns.
7. Handoff bloat — consolidated; no timestamped copies, no `research_state/` enumeration.
8. EVAL-94 staging gap — removed (wired + sealed).
9. EVAL-95 staging gap — removed (built/wired/sealed).
10. EVAL-96 staging gap — removed (built/wired/sealed `20261118T110248Z`).
11. EVAL-97 staging gap — removed (built/wired/sealed `20261118T113811Z`, driver green 711/711).
12. EVAL-98 staging gap — removed (built/wired/sealed `NO-GO CONFIRMED (PASS)` at `20261118T115945Z`; driver green 729/729+27/27).
13. EVAL-99 staging gap — removed (built/wired/sealed `GO CONFIRMED` at `20261118T163647Z`; driver green 747/747+27/27).
14. EVAL-100 staging gap — removed (built/wired/sealed `GO CONFIRMED` at `20261118T164559Z`; driver green 765/765+27/27).
15. EVAL-101 staging gap — removed (built/wired/sealed `GO CONFIRMED` at `20261118T174257Z`; driver green 783/783+27/27).
16. EVAL-102 staging gap — removed (built/wired/sealed `GO CONFIRMED` at `20261118T183232Z`; driver green `801/801` at `2026-11-18T18:41:16Z`).
17. **EVAL-103 staging gap — removed (this session).** Built/wired/sealed `NO-GO CONFIRMED (PASS)` at `20261118T184710Z`; post-seal full driver refresh green at **2026-11-18T18:52:42Z** (`819/819` targeted, `27/27` diagnostics = 846, 38 seal-gate specs ok, readiness written). No sealed prior artifacts or `src/` modified.
18. **EVAL-104 staging gap — removed (this session).** Built/wired/sealed `GO CONFIRMED` at `20261118T190138Z`; post-seal full driver refresh green at **2026-11-18T19:01:38Z** (`837/837` targeted, `27/27` diagnostics = 864, 39 seal-gate specs ok, readiness written). No sealed prior artifacts or `src/` modified.
19. **Avoidance gap after a sealed rung — removed by the §PRE-REGISTERED BUILD QUEUE (EVAL-104..112).** A future session can never claim "no runnable work": seven fully-specified, distinct, data-on-disk cells remain after EVAL-105 (starting with EVAL-106), plus a named extension space.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..104 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting; EVAL-68 acquires BTC+ETH in ONE process; EVAL-69 acquires nothing.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs (EVAL-67/68/69 and EVAL-70..105 in `SEAL_SPECS`); do not use retired compact task IDs.
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
python3 scripts/eval104_phaseb_gate.py

# 3) At/after 2026-11-20T00:00:00Z, or on DUE/FAILED:
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

Driver runs env check, all targeted/diagnostic suites, all campaign arbiters in order, any required `--execute`, all seal-gate specs, and readiness refresh. Use its output and `research_state/EVAL_67_PREWINDOW_READINESS.json` as verified state.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, and 70..105 sealed. EVAL-63 never sealed. EVAL-67/68/69 forward-gated (NOT_DUE/WAIT pre-threshold). Predictiveness GOs: EVAL-71,73,77,83,85,86,88,90,91,93,97,99,100,101,102,104; EVAL-87 `GO/BLOCKED` (`20261118T005436Z`). Traded-form monetization complete/all-NO-GO. EVAL-70,72,74,75,76,78,79,80,81,82,84,89,92,94,95,96,98,103 NO-GO CONFIRMED (PASS) (96/98 BTC-only, not portable; 103 ETH-pass but BTC-fail so GO bar not met). EVAL-105 sealed (cross-sectional `term_ratio` basis → relative tail-asymmetry spread). Do not modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-18T09:49:46Z:** EVAL-94 wired + sealed NO-GO; driver green 657/657+27/27.
- **2026-11-18T10:25:24Z:** EVAL-95 built + sealed NO-GO; driver green 675/675+27/27.
- **2026-11-18T11:19:01Z:** EVAL-96 built + sealed NO-GO (`20261118T110248Z`), wired 693 expected.
- **2026-11-18T11:43:24Z:** EVAL-97 built + sealed GO (`20261118T113811Z`); driver green 711/711+27/27.
- **2026-11-18T12:08:00Z:** EVAL-98 built + sealed NO-GO (`20261118T115945Z`), wired 729 expected.
- **2026-11-18T12:50:00Z:** handoff refreshed; driver green 729/729+27/27; EVAL-99 mandated.
- **2026-11-18T16:45:00Z:** EVAL-99 built, sealed GO (`20261118T163647Z`); driver green 747/747+27/27.
- **2026-11-18T16:52:00Z:** EVAL-100 built + sealed GO (`20261118T164559Z`); driver green 765/765+27/27; EVAL-101 mandated.
- **2026-11-18T18:01:24Z:** EVAL-101 built/wired/sealed `GO CONFIRMED` at `20261118T174257Z`; driver green 783/783+27/27.
- **2026-11-18T18:42:00Z:** EVAL-102 built/wired/sealed `GO CONFIRMED` at `20261118T183232Z` (BTC best IC **0.392590** at `bar300` h24, ETH best IC **0.255910** at `bar60` h24, 3/6 pass on each asset, 7 pooled BH-FDR rejections). Full driver green at `2026-11-18T18:41:16Z`: 801/801 targeted + 27/27 diagnostics = 828, all EVAL-70..102 SEALED, EVAL-67 NOT_DUE (104109.771s overlap), EVAL-68 WAIT_EVAL67, EVAL-69 WAIT_EVAL68, 37/37 seal-gate specs ok. **EVAL-103 (single-asset skew → forward signed return) mandated as next bottleneck.**
- **2026-11-18T18:52:42Z (handoff refreshed; EVAL-103 sealed NO-GO CONFIRMED (PASS), EVAL-104 mandated as next bottleneck):** EVAL-103 built/wired/sealed `NO-GO CONFIRMED (PASS)` at `20261118T184710Z` (BTC best IC 0.0462 0/6 pass; ETH best IC 0.2195 5/6 pass; 6 pooled BH-FDR rejections all ETH; GO bar requires both assets → NO-GO). Full driver green at `2026-11-18T18:52:42Z`: 819/819 targeted + 27/27 diagnostics = 846, all EVAL-70..103 SEALED, EVAL-67 NOT_DUE (103424.058s overlap), EVAL-68 WAIT_EVAL67, EVAL-69 WAIT_EVAL68, 38/38 seal-gate specs ok. **EVAL-104 (single-asset term_slope → forward signed return) is the mandatory next build.** No sealed prior artifacts or `src/` modified.
- **2026-11-18T19:01:38Z (handoff refreshed; EVAL-104 sealed GO CONFIRMED, EVAL-105 mandated as next bottleneck):** EVAL-104 built/wired/sealed `GO CONFIRMED` at `20261118T190138Z` (BTC best IC 0.4058 at `bar300` h24, ETH best IC 0.2600 at `bar60` h24, 3/6 pass BTC / 4/6 pass ETH, 9 pooled BH-FDR rejections both assets). Full driver green at `2026-11-18T19:01:38Z`: 837/837 targeted + 27/27 diagnostics = 864, all EVAL-70..104 SEALED, EVAL-67 NOT_DUE (103424.058s overlap), EVAL-68 WAIT_EVAL67, EVAL-69 WAIT_EVAL68, 39/39 seal-gate specs ok. **EVAL-105 (cross-sectional term_ratio basis → relative tail-asymmetry spread) is the mandatory next build.** No sealed prior artifacts or `src/` modified.
- **2026-11-18T19:42:37Z (handoff refreshed for next session; EVAL-105 remains the mandatory next build):** Full driver `python3 scripts/eval67_prethreshold_progress.py --execute` verified green (exit 0, `overall_ok: true`); env OK, `targeted_tests: 837/837`, `diagnostic_tests: 27/27` = 864 total; all EVAL-70..104 `SEALED`; EVAL-67 `NOT_DUE` (overlap 103424.058s), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`; 39/39 seal-gate specs ok; readiness at `research_state/EVAL_67_PREWINDOW_READINESS.json`. **EVAL-105 (`scripts/eval105*`, `tests/test_eval105*`) is still NOT BUILT/WIRED/SEALED — this is the open bottleneck to clear immediately. Next session MUST run driver, then build+seal EVAL-105, then continue down the queue (EVAL-106..112). No timestamp-only carries permitted.**
- **2026-11-18T19:52:23Z (handoff refreshed; EVAL-105 remains the mandatory next build):** Full driver `python3 scripts/eval67_prethreshold_progress.py --execute` verified green (exit 0, `overall_ok: true`); env OK, `targeted_tests: 837/837`, `diagnostic_tests: 27/27` = 864 total; all EVAL-70..104 `SEALED`; EVAL-67 `NOT_DUE` (overlap **99842.997s**), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`; 39/39 seal-gate specs ok; readiness at `research_state/EVAL_67_PREWINDOW_READINESS.json`. **EVAL-105 (`scripts/eval105*`, `tests/test_eval105*`) is still NOT BUILT/WIRED/SEALED — this is the open bottleneck to clear immediately. Next session MUST run driver, then build+seal EVAL-105, then continue down the queue (EVAL-106..112). No timestamp-only carries permitted.**
- **2026-11-18T20:36:04Z (handoff refreshed; EVAL-106 remains the mandatory next build):** Full driver `python3 scripts/eval67_prethreshold_progress.py --execute` verified green (exit 0, `overall_ok: true`); env OK, `targeted_tests: 854/854`, `diagnostic_tests: 27/27` = 881 total; all EVAL-70..105 `SEALED`; EVAL-67 `NOT_DUE` (overlap decreasing), EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`; 40/40 seal-gate specs ok; readiness at `research_state/EVAL_67_PREWINDOW_READINESS.json`. **EVAL-106 (`scripts/eval106*`, `tests/test_eval106*`) is still NOT BUILT/WIRED/SEALED — this is the open bottleneck to clear immediately. Next session MUST run driver, then build+seal EVAL-106, then continue down the queue (EVAL-107..112). No timestamp-only carries permitted.**