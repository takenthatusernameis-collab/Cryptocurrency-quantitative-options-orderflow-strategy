# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-18T12:08:00Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **VERIFIED STATE (this session):** EVAL-98 is **BUILT, WIRED, and SEALED** (`NO-GO CONFIRMED (PASS)`, prereg+COMBINED `20261118T115945Z`, task `INIT-2026-11-18T11:44:00Z-EVAL98-SINGLE-ASSET-TERM-RATIO-FORWARD-VRP`, seal-gate exit 0, idempotent gate exit 0). EVAL-97 remains sealed (`GO CONFIRMED`, `20261118T113811Z`). Runner `scripts/eval98_single_asset_term_ratio_forward_vrp.py`, gate `scripts/eval98_phaseb_gate.py`, and tests `tests/test_eval98_single_asset_term_ratio_forward_vrp.py` + `tests/test_eval98_phaseb_gate.py` (18 new tests pass) are in-tree and wired into `scripts/eval67_prethreshold_progress.py` (`TARGETED_TEST_FILES` +2, `EXPECTED_TARGETED_TESTS` 711→729, `GATE_SPECS` DUE, `SEAL_SPECS` TERM_RATIO/FORWARD_VRP expected_exit 0, eval98 in readiness gates/notes). A post-seal full driver refresh (`--execute`) was started to produce `research_state/EVAL_67_PREWINDOW_READINESS.json` reflecting EVAL-98; if readiness still predates EVAL-98, rerun the driver until exit 0 and `overall_ok: true`.
>
> **EVAL-98 result (sealed):** single-asset near-to-far ATM IV **term ratio** (`term_ratio = IV(near)/IV(far)-1`, EVAL-74 `_term_bars`/term floor reused verbatim) → forward own-asset **VRP** (EVAL-86 `_forward_vrp` reused verbatim). Floor ok (BTC/ETH). 12 configs (2 bars × 3 horizons), verdict `NO-GO CONFIRMED (PASS)` — not portable. **BTC:** best IC **0.392757** at `term_ratio::bar60.0::h24`, **6/6 configs pass** with **6 pooled BH-FDR rejections**. **ETH:** best IC **0.022838** at `term_ratio::bar60.0::h6`, **0/6 pass** (null). Distinct from EVAL-74 (`term_ratio`→own RV *level*), EVAL-84 (`term_ratio`/`term_slope`→own vol-of-vol), EVAL-96 (`term_slope`→own VRP), EVAL-97 (`skew`→own vol-of-vol), EVAL-86 (`skew`→own VRP). Do not re-litigate or re-seal EVAL-98.
>
> **Forward ladder:** EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, last fully-verified overlap **129180.513s** at 2026-11-18T11:43:24Z and strictly decreasing), EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10. Threshold **2026-11-20T00:00:00Z**; earliest disjoint capture end **2026-11-19T18:08:16Z**. This is hard physics, not a fixable pre-threshold bottleneck. Cron owns routine polling.
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver now:
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Require exit 0 and refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` with `overall_ok: true`, `targeted_tests: 729/729` (or higher if more built/sealed), EVAL-70..98 gates `SEALED`, and all seal-gate specs ok. If an arbiter is `DUE` (20), the driver executes it; if `FAILED` (1), fix and rerun. Do not replace this loop with a timestamp-only handoff bump.
>
> **ANTI-AVOIDANCE RULE:** a green driver plus NOT_DUE/WAIT is **not** session completion. With EVAL-70..98 sealed, the next genuine heavy work is **either** the forward EVAL-67→68→69 ladder when eligible **or build + seal EVAL-99** (§NEXT MANDATORY BUILD). If the driver is green and the ladder remains NOT_DUE/WAIT, **build + seal EVAL-99 now**. After EVAL-99 seals, use the first non-sealed alternate in §NEXT MANDATORY BUILD; do not create a competing handoff or a no-work carry.
>
> **Repo-priority reading:** on-charter ladder EVAL-02..66 is **CLOSED**. Do not re-run, re-litigate, re-seal, or edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..98 artifacts or `src/`. Append-only for new authorized work. No synthetic data, no live trading, no floor weakening.

## NEXT MANDATORY BUILD — EVAL-99 (fully specified; build this if the driver is green and the ladder is NOT_DUE/WAIT)

**EVAL-99 — single-asset `term_slope` surface → forward own-asset return-tail asymmetry.** Economic question: does the causal near-minus-far ATM IV **term slope** (`term_slope = IV(near) - IV(far)`) predict that same underlying's subsequent forward **return-tail asymmetry**? This is distinct from sealed EVAL-74 (`term_slope`→own RV *level*), EVAL-84 (`term_slope`/`term_ratio`→own vol-of-vol), EVAL-85 (`skew`→own tail asymmetry), EVAL-87 (`atm_iv`→own tail asymmetry, `GO/BLOCKED`), EVAL-96 (`term_slope`→own VRP), and EVAL-98 (`term_ratio`→own VRP). It is predictiveness only — **no traded-form or monetization claim**.

- **Runner:** `scripts/eval99_single_asset_term_slope_forward_tail_asymmetry.py`
- **Gate:** `scripts/eval99_phaseb_gate.py` (`SEALED`/`DUE`(20)/`FAILED`(1), no `NOT_DUE`).
- **Tests:** `tests/test_eval99_single_asset_term_slope_forward_tail_asymmetry.py` and `tests/test_eval99_phaseb_gate.py`, mirroring the EVAL-98 single-asset structure but replacing the target with the EVAL-85/87 tail-asymmetry target reused **verbatim** (identify the exact helper in `scripts/eval85_surface_skew_forward_return_tail.py` / `scripts/eval87_surface_atm_iv_forward_tail_asymmetry.py` and reuse it; do not fork).
- **Task ID:** `INIT-2026-11-18T12:10:00Z-EVAL99-SINGLE-ASSET-TERM-SLOPE-FORWARD-TAIL-ASYMMETRY`; task label `EVAL99-SINGLE-ASSET-TERM-SLOPE-FORWARD-TAIL-ASYMMETRY`. The artifact stamp must be ≥ the task floor.
- **Signal (per underlying, single-asset):** `e74._term_bars(capture, bar_seconds=...)` → the `term_slope` field (EVAL-74 reconstruction verbatim); forward-fill with `e71._forward_fill`, expanding-zscore with `e61.expanding_zscore(filled, e62.ZWINDOW)`. Reuse EVAL-74's `_term_bars` + term floor (`e74._underlying_term_floor`) and constants **verbatim** (no fork, no src edits).
- **Target (per underlying):** forward **return-tail asymmetry** over log returns strictly after decision bar `k`, horizons `H ∈ {6, 24, 72}` bars, reused **verbatim** from the sealed EVAL-85/87 tail-asymmetry helper (same construction/stat definition as EVAL-85/87; do not redefine). Distinct from RV level, vol-of-vol, and VRP.
- **Grid:** signal `term_slope` only; `bar_seconds ∈ {60, 300}`; `H ∈ {6, 24, 72}` (6 configs). Spearman rank IC; H1 `IC > 0` (steeper near-minus-far IV slope → higher/more-positive forward tail asymmetry, consistent with the sealed EVAL-85/87 H1 direction; confirm and state the direction in prereg to match the reused target definition).
- **GO bar:** on BOTH BTC and ETH, at least one config with IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, ≥120 usable pairs, and pooled BH-FDR rejection; otherwise `NO-GO CONFIRMED (PASS)`.
- **Floor (pre-registered; NOT a weakening of any sealed floor):** reuses the sealed **EVAL-74 term floor verbatim** (min 2 underlyings; term-adequacy requirements), applied to BOTH BTC and ETH. Below floor ⇒ seal `EVAL_99_..._BLOCKED_<UTC>`, never NO-GO. Do not weaken the EVAL-64 ladder floor.
- **Driver wiring:** add both test files to `TARGETED_TEST_FILES`; add EVAL-99 to `GATE_SPECS` (`wait_phase:"DUE"`) and `SEAL_SPECS` (`expected_exit:1` until sealed, then `0`); bump `EXPECTED_TARGETED_TESTS` by the exact new test count; add `eval99` to readiness gate handling and the readiness notes line. Re-run the full driver green.
- **Seal:** `python3 scripts/eval99_phaseb_gate.py --execute`, require exit 0, set seal spec to expected exit 0, and re-run the full driver green.

**Alternates after EVAL-99 (use the first non-sealed cell; same template, same stats, no src edits):** (a) **EVAL-100** single-asset `term_ratio` → forward own-asset tail asymmetry (`e74._term_bars` term_ratio + EVAL-85/87 tail-asymmetry target; reuses EVAL-74 term floor verbatim; distinct from EVAL-85 skew and EVAL-87 atm_iv); (b) **EVAL-101** single-asset `atm_iv` → forward own-asset **RV level** regression-IC cross-check is NOT a fresh cell (EVAL-71 covered atm_iv→RV). Do **not** test `atm_iv`→VRP (mechanically overlapping: `atm_iv_k` is a direct component of `VRP_k`). Do not rebuild a collar (EVAL-76), do not re-litigate sealed cells, do not weaken the EVAL-64 floor, and do not touch `src/`.

## RUNNABLE-NOW CAMPAIGNS — EVAL-70..98 ALL SEALED

Predictiveness GOs (no net-of-cost monetization): EVAL-71, 73 (own-asset surface/stability); EVAL-77 (cross-sectional basis → RV spread); EVAL-83 (cross-asset spillover); EVAL-85 (skew → tail asymmetry); EVAL-86 (own skew → own VRP); EVAL-87 (`GO/BLOCKED`, prereg+COMBINED `20261118T005436Z`); EVAL-88 (basis → relative direction); EVAL-90 (atm_iv basis → relative vol-of-vol); EVAL-91 (skew basis → relative vol-of-vol); EVAL-93 (cross-sectional term-**slope** basis → relative RV spread); EVAL-97 (single-asset skew → own forward vol-of-vol).

NO-GO CONFIRMED (PASS): EVAL-70, 72, 74, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, **96**. Traded-form taxonomy is complete and all NO-GO: straddle EVAL-72/75, risk reversal EVAL-76, butterfly EVAL-82, relative-value straddle spread EVAL-80. EVAL-92 is the atm_iv-basis relative-VRP cell (near −1 IC is mechanical sign overlap, not a reverse signal). EVAL-94 is the term-**ratio**-basis relative-RV cell (distinct from EVAL-93's term-**slope** cell); best IC 0.0942 with no FDR rejection. EVAL-95 is the single-asset `atm_iv` level → own vol-of-vol cell (ETH-only signal, BTC null ⇒ not portable). EVAL-96 is the single-asset `term_slope` → own VRP cell (BTC strong, best IC 0.4243 at `term_slope::bar60.0::h72`, 6/6 BH-FDR-rejected passes; ETH null, best IC 0.0960 ⇒ not portable). EVAL-97 is the single-asset `skew` → own vol-of-vol cell (portable GO: BTC best IC 0.2504/4 passes, ETH best IC 0.2929/2 passes, 9 pooled BH-FDR rejections).

These 29 campaigns are idempotent no-ops once sealed. Do not re-run them as a substitute for new work.

## THREE SEQUENTIAL FORWARD CAMPAIGNS (repo-priority order; hard disjoint-window gate)

1. **EVAL-67 — BTC-only predictiveness:** task `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`; `python3 scripts/eval67_phaseb_gate.py`. BTC-only was recorded pre-run as underpowered.
2. **EVAL-68 — pooled BTC+ETH predictiveness:** task `INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS`; power-adequate pooled rank-IC. Acquires only after EVAL-67 seals; single acquisition process for BTC+ETH.
3. **EVAL-69 — pooled BTC+ETH traded-form net-of-cost monetization:** task `INIT-2026-11-16T22:45:00Z-EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS`; consumes EVAL-68's capture, no new acquisition, and is the repo-priority capstone.

At/after `2026-11-20T00:00:00Z` (or immediately on a `DUE`/`FAILED` arbiter), run sequentially with `--execute`:

```bash
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67: `SEALED`(0) complete; `NOT_DUE`(10) correct carry; `DUE`(20) execute now; `FAILED`(1) fix and rerun.
- EVAL-68: `SEALED`(0) complete; `WAIT_EVAL67`(10) do not acquire; `DUE`(20) execute now; `FAILED`(1) fix and rerun.
- EVAL-69: `SEALED`(0) ladder complete; `WAIT_EVAL68`(10) do not run; `DUE`(20) execute now; `FAILED`(1) fix and rerun.
- EVAL-70..99 gates: `SEALED`(0) is idempotent complete; `DUE`(20) means run `--execute` now; `FAILED`(1) means fix and rerun.
- After a fully-refreshed green driver run: `env_check: true`; `targeted_tests: 729/729` (or higher if more built/sealed); `diagnostic_tests: 27/27`; all EVAL-70..98 gates `SEALED` and EVAL-99 `SEALED` once built; EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` pre-threshold; all seal-gate specs ok; `overall_ok: true`, exit 0.

## PRE-THRESHOLD HEAVY-WORK RULE

Run the full driver with `--execute` every session. If green and the ladder is still NOT_DUE/WAIT, build and seal EVAL-99 (then the first non-sealed alternate per §NEXT MANDATORY BUILD). A timestamp-only carry is prohibited. Do not spawn capture bridges/waiters; external `*/5` cron owns routine pre-threshold polling. The forward wait is hard physics until the disjoint window.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge and liveness churn — removed; do not recreate.
2. Competing handoff pointers/copies — removed; this file is the single handoff.
3. EVAL-68 and EVAL-69 design-only gaps — removed; both are built/tested/prereg'd/gated.
4. Pre-threshold "no heavy work left" avoidance — removed by EVAL-70..98 and renewed by the mandatory EVAL-99 build above.
5. Manual pre-threshold loop/timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
6. Stale campaign test assumptions — `tests/test_campaign_resume.py` checks current campaigns.
7. Handoff bloat — consolidated; do not create timestamped copies or enumerate `research_state/`.
8. **EVAL-94 staging gap — removed earlier.** EVAL-94's runner/gate/tests were committed but NOT wired into `GATE_SPECS`/`SEAL_SPECS` and NOT sealed (a future agent could have skipped it); it is now wired and idempotently `SEALED`.
9. **EVAL-95 staging gap — removed (prior session).** EVAL-95 built, wired, sealed, and idempotently `SEALED`.
10. **EVAL-96 staging gap — removed earlier.** Built EVAL-96 runner/gate/tests (18 tests pass, py_compile clean), wired into driver (`TARGETED_TEST_FILES` +2, `EXPECTED_TARGETED_TESTS` 675→693, `GATE_SPECS` DUE, `SEAL_SPECS` TERM_SLOPE/FORWARD_VRP + task `INIT-2026-11-18T10:25:24Z-EVAL96-SINGLE-ASSET-TERM-SLOPE-FORWARD-VRP`, eval96 in readiness gates/notes), and sealed `NO-GO CONFIRMED (PASS)` at `20261118T110248Z` (seal-gate exit 0). Full driver refresh to produce updated green readiness was started (idempotent). No sealed prior artifacts or `src/` modified.
11. **EVAL-97 staging gap — removed (prior session).** Built EVAL-97 runner/gate/tests (18 tests), wired into driver, and sealed `GO CONFIRMED` at `20261118T113811Z` (portable: BTC best IC 0.2504/4 pass, ETH best IC 0.2929/2 pass, 9 pooled BH-FDR rejections). Full driver refresh completed (711/711 + 27/27). No sealed prior artifacts or `src/` modified.
12. **EVAL-98 staging gap — removed this session.** Built EVAL-98 runner/gate/tests (18 tests pass, py_compile clean) — single-asset `term_ratio` (EVAL-74 `_term_bars`/term floor reused verbatim) → forward own-asset VRP (EVAL-86 `_forward_vrp` reused verbatim). Wired into driver (`TARGETED_TEST_FILES` +2, `EXPECTED_TARGETED_TESTS` 711→729, `GATE_SPECS` DUE, `SEAL_SPECS` TERM_RATIO/FORWARD_VRP expected_exit 0 + task `INIT-2026-11-18T11:44:00Z-EVAL98-SINGLE-ASSET-TERM-RATIO-FORWARD-VRP`, eval98 in readiness gates/notes). Sealed `NO-GO CONFIRMED (PASS)` at `20261118T115945Z` (seal-gate exit 0): BTC best IC 0.3928 at `term_ratio::bar60.0::h24` (6/6 pass, 6 BH-FDR rejections) but ETH best IC 0.0228 (0/6 pass) ⇒ not portable. A post-seal full driver refresh (`--execute`) was started; rerun until green if readiness predates EVAL-98. No sealed prior artifacts or `src/` modified.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..98 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting; EVAL-68 acquires BTC+ETH in ONE process; EVAL-69 acquires nothing.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Do not use retired compact task IDs; use the EVAL-67/68/69 task IDs and the EVAL-70..99 task IDs in `SEAL_SPECS` as applicable.
- Do not switch EVAL-67/68/69 to a disjoint past window. Do not acquire EVAL-68 before EVAL-67 seals; do not run EVAL-69 before EVAL-68 seals.
- `data/raw/eval67/`, `data/raw/eval68/` are gitignored; do not commit/push. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) EVAL-98 is sealed; verify idempotently (EVAL-97 also sealed):
python3 scripts/eval98_phaseb_gate.py

# 3) At/after 2026-11-20T00:00:00Z, or on DUE/FAILED:
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

The driver runs the env check, all targeted/diagnostic suites, all campaign arbiters in order, any required `--execute`, all seal-gate specs, and the readiness refresh. Use its JSON output and `research_state/EVAL_67_PREWINDOW_READINESS.json` as the verified state.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, and 70..98 are sealed. EVAL-63 was never sealed. EVAL-67/68/69 remain the forward-gated disjoint-window ladder (NOT_DUE/WAIT pre-threshold). Notable predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 88, 90, 91, 93, 97; EVAL-87 is `GO/BLOCKED` (`20261118T005436Z`). Traded-form monetization is complete/all-NO-GO. EVAL-94, 95, 96, 98 are NO-GO: EVAL-96 `term_slope`→own VRP (BTC-only IC 0.4243/6 BH-FDR passes, ETH null ⇒ not portable); EVAL-98 `term_ratio`→own VRP (BTC-only IC 0.3928/6 BH-FDR passes, ETH null ⇒ not portable). EVAL-97 is the single-asset `skew`→own vol-of-vol GO (portable). Do not modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-18T10:25:24Z (EVAL-95 built + sealed NO-GO; driver green; EVAL-96 mandated):** Built EVAL-95 (`scripts/eval95_single_asset_atm_iv_forward_vol_of_vol.py`, `scripts/eval95_phaseb_gate.py`, `tests/test_eval95_single_asset_atm_iv_forward_vol_of_vol.py`, `tests/test_eval95_phaseb_gate.py`) — single-asset `atm_iv` level → forward own-asset vol-of-vol, reusing EVAL-71 `build_surface_bars`/`_forward_fill`/surface floor and EVAL-84 `_forward_vov` verbatim. Wired EVAL-95 into the driver (`GATE_SPECS` `wait_phase:"DUE"`; `SEAL_SPECS` with ATM_IV/FORWARD_VOL_OF_VOL globs and the EVAL-95 task id; `eval95` in the readiness gates/notes; `EXPECTED_TARGETED_TESTS` 657→675) and ran `python3 scripts/eval67_prethreshold_progress.py --execute`. Final driver exit 0 at **2026-11-18T10:24:11Z**: env OK, **675/675 targeted + 27/27 diagnostics = 702**, **29** gates (EVAL-70..95 `SEALED`; EVAL-67 `NOT_DUE` overlap **133932.625s**, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`), **30** seal-gates ok; readiness refreshed overall_ok true. **EVAL-95** sealed `NO-GO CONFIRMED (PASS)` at **2026-11-18T10:23:37Z** (prereg+COMBINED `20261118T102337Z`), floor_ok true, 6 configs, 0 pass, no pooled GO; best IC **0.211813** (ETH `atm_iv::bar300.0::h72`, 2 ETH BH-FDR rejections) but BTC null (best −0.01722) ⇒ not portable. No sealed prior artifacts or `src/` modified. Next mandatory runnable-now work is **EVAL-96** (§NEXT MANDATORY BUILD), not another timestamp carry.

- **2026-11-18T09:49:46Z (EVAL-94 wired + sealed NO-GO; driver green; EVAL-95 mandated):** Wired EVAL-94 into the driver and sealed it. Final driver exit 0 at **2026-11-18T09:49:46Z**: env OK, **657/657 targeted + 27/27 diagnostics = 684**, **28** gates (EVAL-70..94 `SEALED`; EVAL-67 `NOT_DUE` overlap **135997.346s**), **29** seal-gates ok. **EVAL-94** sealed `NO-GO CONFIRMED (PASS)` at **2026-11-18T09:43:06Z** (`20261118T094306Z`), floor_ok true, 6 configs, 0 pass, 0 BH-FDR; best IC **0.094242** at `term_ratio::bar300.0::h72`. Cross-sectional term-**ratio** basis does not portably predict the subsequent BTC-minus-ETH forward relative RV spread (artifact IDs correctly `...TERM_RATIO_BASIS...`; internal task label string copied `...TERM-SLOPE...`, sealed signal is the ratio — distinct from EVAL-93).
- **2026-11-18T11:19:01Z (EVAL-96 built + sealed NO-GO; driver wired; EVAL-97 mandated):** Built EVAL-96 (`scripts/eval96_single_asset_term_slope_forward_vrp.py`, `scripts/eval96_phaseb_gate.py`, `tests/test_eval96_single_asset_term_slope_forward_vrp.py`, `tests/test_eval96_phaseb_gate.py`) — single-asset `term_slope` (EVAL-74 `_term_bars`/term floor reused verbatim) → forward own-asset VRP (EVAL-86 `_forward_vrp` reused verbatim), 6 configs, EVAL-65 stats. New tests **18/18 pass** (py_compile clean). Wired EVAL-96 into `scripts/eval67_prethreshold_progress.py` (`TARGETED_TEST_FILES` +2, `EXPECTED_TARGETED_TESTS` 675→693, `GATE_SPECS` `wait_phase:"DUE"`, `SEAL_SPECS` TERM_SLOPE/FORWARD_VRP globs + task `INIT-2026-11-18T10:25:24Z-EVAL96-SINGLE-ASSET-TERM-SLOPE-FORWARD-VRP`, `eval96` in readiness gates/notes). Executed `python3 scripts/eval96_phaseb_gate.py --execute` → **SEALED exit 0** at **2026-11-18T11:02:48Z** (prereg+COMBINED `20261118T110248Z`), floor_ok true, 12 configs, verdict `NO-GO CONFIRMED (PASS)`: BTC best IC **0.424321** at `term_slope::bar60.0::h72` (6/6 pass, 6 BH-FDR rejections) but ETH best IC **0.095987** (0/6 pass) ⇒ not portable. No sealed prior artifacts or `src/` modified. Started full driver `--execute` for refreshed readiness (693/27 expected; idempotent). Forward ladder remains `NOT_DUE`/`WAIT_EVAL67`/`WAIT_EVAL68` (last verified overlap 132946.927s at 2026-11-18T10:40:37Z). Next mandatory runnable-now work is **EVAL-97** (§NEXT MANDATORY BUILD), not another timestamp carry.
- **2026-11-18T11:43:24Z (EVAL-97 built + sealed GO; driver green; EVAL-98 mandated):** Built EVAL-97 (`scripts/eval97_single_asset_skew_forward_vol_of_vol.py`, `scripts/eval97_phaseb_gate.py`, `tests/test_eval97_single_asset_skew_forward_vol_of_vol.py`, `tests/test_eval97_phaseb_gate.py`) — single-asset near-ATM put-call `skew` (EVAL-71 `build_surface_bars` reconstruction + surface floor reused verbatim) → forward own-asset vol-of-vol (EVAL-84 `_forward_vov` reused verbatim), 6 configs, EVAL-65 stats. New tests **18/18 pass** (py_compile clean). Wired EVAL-97 into `scripts/eval67_prethreshold_progress.py` (`TARGETED_TEST_FILES` +2, `EXPECTED_TARGETED_TESTS` 693→711, `GATE_SPECS` `wait_phase:"DUE"`, `SEAL_SPECS` SKEW/FORWARD_VOL_OF_VOL globs + task `INIT-2026-11-18T11:19:01Z-EVAL97-SINGLE-ASSET-SKEW-FORWARD-VOL-OF-VOL`, `eval97` in readiness gates/notes). Executed `python3 scripts/eval97_phaseb_gate.py --execute` → **SEALED exit 0** at **2026-11-18T11:38:11Z** (prereg+COMBINED `20261118T113811Z`), floor_ok true, 12 configs, verdict `GO CONFIRMED` (portable): BTC best IC **0.250360** at `skew::bar300.0::h72` (4/6 pass), ETH best IC **0.292907** at `skew::bar300.0::h24` (2/6 pass), **9 pooled BH-FDR rejections**. Set EVAL-97 `SEAL_SPECS` `expected_exit` 1→0 and re-ran full driver `--execute` → exit 0 at **2026-11-18T11:43:24Z**: env OK, **711/711 targeted + 27/27 diagnostics = 738**, **30** gates (EVAL-70..97 `SEALED`; EVAL-67 `NOT_DUE` overlap **129180.513s**, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`), **32** seal-gates ok; readiness refreshed overall_ok true. No sealed prior artifacts or `src/` modified. Next mandatory runnable-now work is **EVAL-98** (§NEXT MANDATORY BUILD), not another timestamp carry.

- **2026-11-18T12:08:00Z (EVAL-98 built + sealed NO-GO; driver wired; EVAL-99 mandated):** Built EVAL-98 (`scripts/eval98_single_asset_term_ratio_forward_vrp.py`, `scripts/eval98_phaseb_gate.py`, `tests/test_eval98_single_asset_term_ratio_forward_vrp.py`, `tests/test_eval98_phaseb_gate.py`) — single-asset `term_ratio` (EVAL-74 `_term_bars`/term floor reused verbatim) → forward own-asset VRP (EVAL-86 `_forward_vrp` reused verbatim), 6 configs, EVAL-65 stats. New tests **18/18 pass** (py_compile clean). Wired EVAL-98 into `scripts/eval67_prethreshold_progress.py` (`TARGETED_TEST_FILES` +2, `EXPECTED_TARGETED_TESTS` 711→729, `GATE_SPECS` `wait_phase:"DUE"`, `SEAL_SPECS` TERM_RATIO/FORWARD_VRP expected_exit 1→0 after seal + task `INIT-2026-11-18T11:44:00Z-EVAL98-SINGLE-ASSET-TERM-RATIO-FORWARD-VRP`, `eval98` in readiness gates/notes). Executed `python3 scripts/eval98_phaseb_gate.py --execute` → **SEALED exit 0** at **2026-11-18T11:59:45Z** (prereg+COMBINED `20261118T115945Z`), floor_ok true, 12 configs, verdict `NO-GO CONFIRMED (PASS)`: BTC best IC **0.392757** at `term_ratio::bar60.0::h24` (6/6 pass, 6 BH-FDR rejections) but ETH best IC **0.022838** (0/6 pass) ⇒ not portable. A post-seal full driver refresh (`--execute`) was started to refresh readiness to 729/729 + eval98 SEALED; rerun until green if readiness predates EVAL-98. Forward ladder remains `NOT_DUE`/`WAIT_EVAL67`/`WAIT_EVAL68` (last fully-verified overlap 129180.513s at 2026-11-18T11:43:24Z). No sealed prior artifacts or `src/` modified. Next mandatory runnable-now work is **EVAL-99** (§NEXT MANDATORY BUILD), not another timestamp carry.
