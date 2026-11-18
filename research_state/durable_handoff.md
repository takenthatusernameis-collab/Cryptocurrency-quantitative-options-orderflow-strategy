# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-18T09:49:46Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **VERIFIED STATE (2026-11-18T09:49:46Z):** `python3 scripts/eval67_prethreshold_progress.py --execute` exited **0** at **2026-11-18T09:49:46Z** and refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` (`overall_ok: true`). Env OK; **657/657 targeted + 27/27 diagnostics = 684 tests**; **28** campaign gates (EVAL-70..94 `SEALED`; EVAL-67 `NOT_DUE` exit 10, EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10); **29** seal-gate specs ok. **EVAL-70..94 are SEALED** (idempotent).
>
> **EVAL-94 sealed `NO-GO CONFIRMED (PASS)` at 2026-11-18T09:43:06Z** (prereg+COMBINED `20261118T094306Z`): cross-sectional term-structure **RATIO** basis (BTC-vs-ETH relative near-minus-far ATM IV `term_ratio = IV(near)/IV(far) − 1`) → forward relative *realized-vol* spread. floor_ok **true**; 6 configs; 0 pass; **no BH-FDR rejection**; best IC **0.094242** at `term_ratio::bar300.0::h72`. **Caveat for readers:** EVAL-94's *artifact IDs* are `..._TERM_RATIO_BASIS_...` (correct, ratio signal), but its *internal task label string* was copied from EVAL-93 and reads `...TERM-SLOPE...`; the sealed signal is genuinely the **ratio** (`term_ratio`), distinct from sealed EVAL-93 (term **slope**). Do not re-litigate or re-seal EVAL-94.
>
> **Forward ladder:** EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, `overlap_seconds=135997.346` at final driver time, strictly decreasing), EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10. Threshold **2026-11-20T00:00:00Z**; earliest disjoint capture end **2026-11-19T18:08:16Z**. This is hard physics, not a fixable pre-threshold bottleneck. Cron owns routine polling.
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver now:
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Require exit 0. If an arbiter is `DUE` (20), the driver executes it; if `FAILED` (1), fix and rerun. Do not replace this loop with a timestamp-only handoff bump.
>
> **ANTI-AVOIDANCE RULE:** a green driver plus NOT_DUE/WAIT is **not** session completion. With EVAL-70..94 sealed, the next genuine heavy work is **either** the forward EVAL-67→68→69 ladder when eligible **or build + seal EVAL-95** (§NEXT MANDATORY BUILD). If the driver is green and the ladder remains NOT_DUE/WAIT, **build + seal EVAL-95 now**. After EVAL-95 seals, use the first non-sealed alternate in §NEXT MANDATORY BUILD; do not create a competing handoff or a no-work carry.
>
> **Repo-priority reading:** on-charter ladder EVAL-02..66 is **CLOSED**. Do not re-run, re-litigate, re-seal, or edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..94 artifacts or `src/`. Append-only for new authorized work. No synthetic data, no live trading, no floor weakening.

## NEXT MANDATORY BUILD — EVAL-95 (fully specified; build this if the driver is green and the ladder is NOT_DUE/WAIT)

**EVAL-95 — single-asset `atm_iv` surface LEVEL → forward own-asset vol-of-vol (RV-of-RV).** Economic question: does the near-ATM implied-vol *level* of an underlying predict that underlying's subsequent forward *vol-of-vol* (turbulence/unevenness of realized variance along the path)? This is distinct from sealed EVAL-71 (`atm_iv`/`skew` → own RV level), EVAL-84 (`term_slope`/`term_ratio` → own vol-of-vol), EVAL-86 (`skew` → own VRP), and EVAL-85/87 (`skew`/`atm_iv` → own tail asymmetry). It is predictiveness only — **no traded-form or monetization claim**.

- **Runner:** `scripts/eval95_single_asset_atm_iv_forward_vol_of_vol.py`
- **Gate:** `scripts/eval95_phaseb_gate.py` (`SEALED`/`DUE`(20)/`FAILED`(1), no `NOT_DUE`).
- **Tests:** `tests/test_eval95_single_asset_atm_iv_forward_vol_of_vol.py` and `tests/test_eval95_phaseb_gate.py`, mirroring the EVAL-84 single-asset structure and the EVAL-94 gate tests.
- **Task ID:** `INIT-2026-11-18T09:44:00Z-EVAL95-SINGLE-ASSET-ATM-IV-FORWARD-VOL-OF-VOL`; task label `EVAL95-SINGLE-ASSET-ATM-IV-FORWARD-VOL-OF-VOL`. The artifact stamp must be ≥ the task floor.
- **Signal (per underlying, single-asset):** `e71.build_surface_bars(capture, bar_seconds=...)` → the `atm_iv` field (amount-weighted mean near-ATM option-trade IV over the trailing `e71.SIGNAL_WINDOW_SECONDS` window); forward-fill with `e71._forward_fill`, expanding-zscore with `e61.expanding_zscore(filled, e62.ZWINDOW)`. Reuse EVAL-71's `build_surface_bars` / `_forward_fill` and constants **verbatim** (no fork, no src edits).
- **Target (per underlying):** `e84._forward_vov(bars, H)` reused **verbatim** — `vov_k = sqrt(mean((v_i − mean(v))²))` with `v_i = r_i²` over log returns `r_i` on bars `k+1..k+H` strictly after decision bar `k` (std of squared returns; distinct from EVAL-71/74's forward RV `sqrt(mean(v_i))`).
- **Grid:** signal `atm_iv` only; `bar_seconds ∈ {60, 300}`; `H ∈ {6, 24, 72}` (6 configs). Spearman rank IC; H1 `IC > 0` (rich IV level → subsequent vol-of-vol mean-reverts / is informative).
- **GO bar:** at least one config with IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, ≥120 usable pairs, and pooled BH-FDR rejection; otherwise `NO-GO CONFIRMED (PASS)`.
- **Floor (pre-registered; NOT a weakening of any sealed floor):** EVAL-95 consumes each underlying's trade-tape IV surface + perp candles, so it reuses the sealed **EVAL-71 surface floor verbatim** (min 2 underlyings; ≥ `min_option_trades_per_underlying`=1000 option trades, ≥ `min_near_atm_option_trades_per_underlying`=400 near-ATM trades, ≥ `min_perp_candles_per_underlying`=1000 perp candles, ≥ `min_perp_span_seconds_per_underlying`=82000s perp span, per underlying), applied to BOTH BTC and ETH. No term-adequacy requirement (the `atm_iv` signal is a *level*, not a term structure). Below floor ⇒ seal `EVAL_95_..._BLOCKED_<UTC>`, never NO-GO. Do not weaken the EVAL-64 ladder floor.
- **Driver wiring:** add both test files to `TARGETED_TEST_FILES`; add EVAL-95 to `GATE_SPECS` (`wait_phase:"DUE"`) and `SEAL_SPECS` (`expected_exit:1` until sealed, then `0`); bump `EXPECTED_TARGETED_TESTS` by the exact new test count; add `eval95` to readiness gate handling (and to the readiness notes line). Re-run the full driver green.
- **Seal:** `python3 scripts/eval95_phaseb_gate.py --execute`, require exit 0, set seal spec to expected exit 0, and re-run the full driver green.

**Alternates after EVAL-95 (use the first non-sealed cell; same template and floors):** (a) **EVAL-96** single-asset `term_slope` → forward own-asset VRP (EVAL-74 used term→RV, EVAL-84 used term→vol-of-vol, EVAL-86 used skew→VRP — so term→VRP is distinct); (b) **EVAL-97** single-asset `skew` → forward own-asset vol-of-vol (EVAL-84 used term→vol-of-vol, EVAL-86 used skew→VRP, EVAL-85 used skew→tail asymmetry). Do not rebuild a collar (EVAL-76), do not re-litigate sealed cells, do not weaken the EVAL-64 floor, and do not touch `src/`.

## RUNNABLE-NOW CAMPAIGNS — EVAL-70..94 ALL SEALED

Predictiveness GOs (no net-of-cost monetization): EVAL-71, 73 (own-asset surface/stability); EVAL-77 (cross-sectional basis → RV spread); EVAL-83 (cross-asset spillover); EVAL-85 (skew → tail asymmetry); EVAL-86 (own skew → own VRP); EVAL-87 (`GO/BLOCKED`, prereg+COMBINED `20261118T005436Z`); EVAL-88 (basis → relative direction); EVAL-90 (atm_iv basis → relative vol-of-vol); EVAL-91 (skew basis → relative vol-of-vol); EVAL-93 (cross-sectional term-**slope** basis → relative RV spread).

NO-GO CONFIRMED (PASS): EVAL-70, 72, 74, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, **94**. Traded-form taxonomy is complete and all NO-GO: straddle EVAL-72/75, risk reversal EVAL-76, butterfly EVAL-82, relative-value straddle spread EVAL-80. EVAL-92 is the atm_iv-basis relative-VRP cell; its near −1 IC is mechanical sign overlap, not a reverse signal. EVAL-94 is the term-**ratio**-basis relative-RV cell (distinct from EVAL-93's term-**slope** cell); best IC 0.0942 with no FDR rejection.

These 25 campaigns are idempotent no-ops once sealed. Do not re-run them as a substitute for new work.

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
- EVAL-70..95 gates: `SEALED`(0) is idempotent complete; `DUE`(20) means run `--execute` now; `FAILED`(1) means fix and rerun.
- The full driver must report: `env_check: true`; `targeted_tests: 657/657`; `diagnostic_tests: 27/27`; all EVAL-70..94 gates `SEALED`; EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` pre-threshold; 29 seal-gate specs ok; `overall_ok: true`, exit 0.

## PRE-THRESHOLD HEAVY-WORK RULE

Run the full driver with `--execute` every session. If green and the ladder is still NOT_DUE/WAIT, build and seal EVAL-95 (then the first non-sealed alternate). A timestamp-only carry is prohibited. Do not spawn capture bridges/waiters; external `*/5` cron owns routine pre-threshold polling. The forward wait is hard physics until the disjoint window.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge and liveness churn — removed; do not recreate.
2. Competing handoff pointers/copies — removed; this file is the single handoff.
3. EVAL-68 and EVAL-69 design-only gaps — removed; both are built/tested/prereg'd/gated.
4. Pre-threshold "no heavy work left" avoidance — removed by EVAL-70..94 and renewed by the mandatory EVAL-95 build above.
5. Manual pre-threshold loop/timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
6. Stale campaign test assumptions — `tests/test_campaign_resume.py` checks current campaigns.
7. Handoff bloat — consolidated; do not create timestamped copies or enumerate `research_state/`.
8. **EVAL-94 staging gap — removed this session.** EVAL-94's runner/gate/tests were committed but NOT wired into `GATE_SPECS`/`SEAL_SPECS` and NOT sealed (a future agent could have skipped it). This session wired EVAL-94 into the driver (`GATE_SPECS` `wait_phase:"DUE"` + `SEAL_SPECS`), sealed it, and refreshed readiness. EVAL-94 is now enforced and idempotently `SEALED`.
9. Stale/incomplete prior-session driver process — none was running before this session; this session verified the full green driver and sealed EVAL-94.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..94 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting; EVAL-68 acquires BTC+ETH in ONE process; EVAL-69 acquires nothing.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Do not use retired compact task IDs; use the EVAL-67/68/69 task IDs and the EVAL-70..94 task IDs in `SEAL_SPECS`.
- Do not switch EVAL-67/68/69 to a disjoint past window. Do not acquire EVAL-68 before EVAL-67 seals; do not run EVAL-69 before EVAL-68 seals.
- `data/raw/eval67/`, `data/raw/eval68/` are gitignored; do not commit/push. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) EVAL-94 is sealed; verify idempotently:
python3 scripts/eval94_phaseb_gate.py

# 3) At/after 2026-11-20T00:00:00Z, or on DUE/FAILED:
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

The driver runs the env check, all targeted/diagnostic suites, all campaign arbiters in order, any required `--execute`, all seal-gate specs, and the readiness refresh. Use its JSON output and `research_state/EVAL_67_PREWINDOW_READINESS.json` as the verified state.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, and 70..94 are sealed. EVAL-63 was never sealed. EVAL-67/68/69 remain the forward-gated disjoint-window ladder (NOT_DUE/WAIT pre-threshold). Notable predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 88, 90, 91, 93; EVAL-87 is `GO/BLOCKED` (`20261118T005436Z`). Traded-form monetization is complete/all-NO-GO. Do not modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-18T09:24:17Z (EVAL-93 built + sealed GO; driver green; EVAL-94 mandated):** Ran the full driver before and after the build. Final `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0 at **2026-11-18T09:24:17Z**: env OK, **625/625 targeted + 27/27 diagnostics = 652**, **27** gates (EVAL-70..93 `SEALED`; EVAL-67 `NOT_DUE` overlap **137526.308s**, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`), **28** seal-gates ok; readiness refreshed overall_ok true. **EVAL-93** sealed `GO CONFIRMED` at **2026-11-18T09:18:58Z** (prereg+COMBINED `20261118T091858Z`), floor_ok true, 6 configs, 1 pass (`term_slope::bar300.0::h72`), 1 BH-FDR rejection; best IC **0.264843** at `term_slope::bar300.0::h72`, p **0.000999**, 95% CI **[0.0430, 0.4601]**. Cross-sectional term-slope basis (BTC-vs-ETH relative near-minus-far ATM IV term slope) predicts subsequent BTC-minus-ETH forward relative RV spread on real on-disk data. No sealed prior artifacts or `src/` modified. Next mandatory runnable-now work is **EVAL-94** (§NEXT MANDATORY BUILD), not another timestamp carry.

- **2026-11-18T09:49:46Z (EVAL-94 wired + sealed NO-GO; driver green; EVAL-95 mandated):** Discovered EVAL-94's runner/gate/tests were committed but unwired (`GATE_SPECS`/`SEAL_SPECS`) and unsealed — an avoidable-heavy-work gap. Wired EVAL-94 into the driver (`GATE_SPECS` `wait_phase:"DUE"`; `SEAL_SPECS` with TERM_RATIO_BASIS globs and EVAL-94 task id; `eval94` in the readiness gates/notes) and ran `python3 scripts/eval67_prethreshold_progress.py --execute` to seal it. Final driver exit 0 at **2026-11-18T09:49:46Z**: env OK, **657/657 targeted + 27/27 diagnostics = 684**, **28** gates (EVAL-70..94 `SEALED`; EVAL-67 `NOT_DUE` overlap **135997.346s**, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`), **29** seal-gates ok; readiness refreshed overall_ok true. **EVAL-94** sealed `NO-GO CONFIRMED (PASS)` at **2026-11-18T09:43:06Z** (prereg+COMBINED `20261118T094306Z`), floor_ok true, 6 configs, 0 pass, 0 BH-FDR; best IC **0.094242** at `term_ratio::bar300.0::h72`. Cross-sectional term-**ratio** basis (BTC-vs-ETH relative near-minus-far ATM IV `IV(near)/IV(far) − 1`) does **not** portably predict the subsequent BTC-minus-ETH forward relative RV spread. (Internal task label string reads `...TERM-SLOPE...` from copy-paste; artifact IDs are correctly `...TERM_RATIO_BASIS...` and the sealed signal is the ratio — distinct from EVAL-93.) No sealed prior artifacts or `src/` modified. Next mandatory runnable-now work is **EVAL-95** (§NEXT MANDATORY BUILD), not another timestamp carry.