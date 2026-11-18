# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-18T09:24:17Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **VERIFIED STATE (2026-11-18T09:24:17Z):** `python3 scripts/eval67_prethreshold_progress.py --execute` exited **0** at **2026-11-18T09:24:17Z** and refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` (`overall_ok: true`). Env OK; **625/625 targeted + 27/27 diagnostics = 652 tests**; **27** campaign gates all ok/classified (EVAL-70..93 `SEALED`); **28** seal-gate specs ok. **EVAL-70..93 are SEALED** (idempotent). **EVAL-93 sealed `GO CONFIRMED` at 2026-11-18T09:18:58Z** (cross-sectional term-slope basis → forward relative *realized-vol* spread): floor-clean real BTC+ETH captures, 6 configs, 1 pass (`term_slope::bar300.0::h72`), 1 BH-FDR rejection; best IC **0.264843** at `term_slope::bar300.0::h72`, permutation p **0.000999**, 95% CI **[0.0430, 0.4601]**. The cross-sectional term-slope basis (BTC-vs-ETH relative near-minus-far ATM IV term slope) **does** predict the subsequent BTC-minus-ETH forward relative RV spread on real on-disk data. Do not re-litigate or re-seal EVAL-93.
>
> **Forward ladder:** EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, `overlap_seconds=137526.308` at final driver time, strictly decreasing), EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10. Threshold **2026-11-20T00:00:00Z**; earliest disjoint capture end **2026-11-19T18:08:16Z**. This is hard physics, not a fixable pre-threshold bottleneck. Cron owns routine polling.
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver now:
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Require exit 0. If an arbiter is `DUE` (20), the driver executes it; if `FAILED` (1), fix and rerun. Do not replace this loop with a timestamp-only handoff bump.
>
> **ANTI-AVOIDANCE RULE:** a green driver plus NOT_DUE/WAIT is **not** session completion. With EVAL-70..93 sealed, the next genuine heavy work is **either** the forward EVAL-67→68→69 ladder when eligible **or build + seal EVAL-94** (§NEXT MANDATORY BUILD). If the driver is green and the ladder remains NOT_DUE/WAIT, **build + seal EVAL-94 now**. After EVAL-94 seals, use the first non-sealed alternate in §NEXT MANDATORY BUILD; do not create a competing handoff or a no-work carry.
>
> **Repo-priority reading:** on-charter ladder EVAL-02..66 is **CLOSED**. Do not re-run, re-litigate, re-seal, or edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..93 artifacts or `src/`. Append-only for new authorized work. No synthetic data, no live trading, no floor weakening.

## NEXT MANDATORY BUILD — EVAL-94 (fully specified; build this if the driver is green and the ladder is NOT_DUE/WAIT)

**EVAL-94 — cross-sectional term-structure RATIO basis → forward relative realized-vol (RV) spread.** Economic question: when ETH's near-to-far ATM IV term *ratio* is rich relative to BTC's, does BTC subsequently carry the richer forward RV relative to ETH? This is distinct from sealed EVAL-74 (own-asset term slope → own RV), EVAL-77 (atm_iv/skew basis → relative RV), EVAL-84 (own-asset term slope → own vol-of-vol), EVAL-88 (basis → relative direction), EVAL-89/92 (basis → relative VRP), EVAL-90/91 (basis → relative vol-of-vol), and EVAL-93 (cross-sectional term *slope* basis → relative RV). It is predictiveness only — **no traded-form or monetization claim**.

- **Runner:** `scripts/eval94_cross_sectional_term_ratio_basis_relative_rv_spread.py`
- **Gate:** `scripts/eval94_phaseb_gate.py` (`SEALED`/`DUE`(20)/`FAILED`(1), no `NOT_DUE`).
- **Tests:** `tests/test_eval94_cross_sectional_term_ratio_basis_relative_rv_spread.py` and `tests/test_eval94_phaseb_gate.py`, mirroring EVAL-93 test structure.
- **Task ID:** `INIT-2026-11-18T09:25:00Z-EVAL94-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-RV-SPREAD`; task label `EVAL94-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-RV-SPREAD`. The artifact stamp must be ≥ the task floor.
- **Signal:** `rel_z_k = expanding_z(term_ratio_ETH(k) − term_ratio_BTC(k))` on EVAL-77's common aligned bar grid. Reuse sealed `scripts/eval74_surface_term_structure_predictiveness.py` `_term_bars`, `_term_adequacy`, `_underlying_term_floor`, `SIGNAL_WINDOW_SECONDS`, `ATM_BAND`, and expiry constants verbatim. Overlay the resulting `term_ratio` field onto an in-memory `e77.build_cross_section(...)` maps object by `bar_open_ms`; do not mutate sealed code or artifacts. `term_ratio = IV(nearest expiry) / IV(farthest expiry)` (unitless ratio) from causal trailing near-ATM option trades.
- **Target:** reuse EVAL-77 `_closes_on_common` / `_rv_series`: `y_k = RV_BTC(k) − RV_ETH(k)`, where `RV_i(k) = sqrt(mean(log-return²))` over bars `k+1..k+H` strictly after decision bar `k`.
- **Grid:** `term_ratio` only; `bar_seconds ∈ {60, 300}`; `H ∈ {6, 24, 72}` (6 configs). Spearman rank IC; H1 `IC > 0`.
- **GO bar:** at least one config with IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, ≥120 usable pairs, and pooled BH-FDR rejection; otherwise `NO-GO CONFIRMED (PASS)`.
- **Floor:** compose, do not weaken: both BTC and ETH must pass sealed EVAL-71 surface floor **and** EVAL-74 term-adequacy floor (≥2 distinct near-ATM expiries with ≥5 trades each; ≥40 bars with term data); plus EVAL-77 alignment ≥200 common bars on the coarsest grid. Below floor ⇒ `BLOCKED`, never NO-GO.
- **Driver wiring:** add both test files to `TARGETED_TEST_FILES`; add EVAL-94 to `GATE_SPECS` (`wait_phase:"DUE"`) and `SEAL_SPECS` (`expected_exit:1` until sealed, then `0`); bump `EXPECTED_TARGETED_TESTS` by the exact new test count; add `eval94` to readiness gate handling. Re-run the full driver green.
- **Seal:** `python3 scripts/eval94_phaseb_gate.py --execute`, require exit 0, set seal spec to expected exit 0, and re-run the full driver green.

**Alternates after EVAL-94 (use the first non-sealed cell; same template and floors):** (a) **EVAL-95** single-asset `atm_iv` → forward own-asset vol-of-vol (EVAL-84 used term_slope, so this is distinct); (b) single-asset `term_slope` → forward own-asset VRP (EVAL-74 targeted RV and EVAL-84 targeted vol-of-vol). Do not rebuild a collar (EVAL-76), do not re-litigate sealed cells, do not weaken the EVAL-64 floor, and do not touch `src/`.

## RUNNABLE-NOW CAMPAIGNS — EVAL-70..93 ALL SEALED

Predictiveness GOs (no net-of-cost monetization): EVAL-71, 73 (own-asset surface/stability); EVAL-77 (cross-sectional basis → RV spread); EVAL-83 (cross-asset spillover); EVAL-85 (skew → tail asymmetry); EVAL-86 (own skew → own VRP); EVAL-87 (`GO/BLOCKED`, prereg+COMBINED `20261118T005436Z`); EVAL-88 (basis → relative direction); EVAL-90 (atm_iv basis → relative vol-of-vol); EVAL-91 (skew basis → relative vol-of-vol); **EVAL-93 (cross-sectional term-slope basis → relative RV spread)**.

NO-GO CONFIRMED (PASS): EVAL-70, 72, 74, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92. Traded-form taxonomy is complete and all NO-GO: straddle EVAL-72/75, risk reversal EVAL-76, butterfly EVAL-82, relative-value straddle spread EVAL-80. EVAL-92 is the atm_iv-basis relative-VRP cell; its near −1 IC is mechanical sign overlap, not a reverse signal.

These 24 campaigns are idempotent no-ops once sealed. Do not re-run them as a substitute for new work.

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
- EVAL-70..94 gates: `SEALED`(0) is idempotent complete; `DUE`(20) means run `--execute` now; `FAILED`(1) means fix and rerun.
- The full driver must report: `env_check: true`; `targeted_tests: 625/625`; `diagnostic_tests: 27/27`; all EVAL-70..93 gates `SEALED`; EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` pre-threshold; 28 seal-gate specs ok; `overall_ok: true`, exit 0.

## PRE-THRESHOLD HEAVY-WORK RULE

Run the full driver with `--execute` every session. If green and the ladder is still NOT_DUE/WAIT, build and seal EVAL-94 (then the first non-sealed alternate). A timestamp-only carry is prohibited. Do not spawn capture bridges/waiters; external `*/5` cron owns routine pre-threshold polling. The forward wait is hard physics until the disjoint window.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge and liveness churn — removed; do not recreate.
2. Competing handoff pointers/copies — removed; this file is the single handoff.
3. EVAL-68 and EVAL-69 design-only gaps — removed; both are built/tested/prereg'd/gated.
4. Pre-threshold "no heavy work left" avoidance — removed by EVAL-70..93 and renewed by the mandatory EVAL-94 build above.
5. Manual pre-threshold loop/timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
6. Stale campaign test assumptions — `tests/test_campaign_resume.py` checks current campaigns.
7. Handoff bloat — consolidated; do not create timestamped copies or enumerate `research_state/`.
8. Stale/incomplete prior-session driver process — none was running before this session; this session verified two complete green drivers and sealed EVAL-93.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..93 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting; EVAL-68 acquires BTC+ETH in ONE process; EVAL-69 acquires nothing.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Do not use retired compact task IDs; use the EVAL-67/68/69 task IDs and the EVAL-70..93 task IDs in `SEAL_SPECS`.
- Do not switch EVAL-67/68/69 to a disjoint past window. Do not acquire EVAL-68 before EVAL-67 seals; do not run EVAL-69 before EVAL-68 seals.
- `data/raw/eval67/`, `data/raw/eval68/` are gitignored; do not commit/push. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) EVAL-93 is sealed; verify idempotently:
python3 scripts/eval93_phaseb_gate.py

# 3) At/after 2026-11-20T00:00:00Z, or on DUE/FAILED:
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

The driver runs the env check, all targeted/diagnostic suites, all campaign arbiters in order, any required `--execute`, all seal-gate specs, and the readiness refresh. Use its JSON output and `research_state/EVAL_67_PREWINDOW_READINESS.json` as the verified state.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, and 70..93 are sealed. EVAL-63 was never sealed. EVAL-67/68/69 remain the forward-gated disjoint-window ladder (NOT_DUE/WAIT pre-threshold). Notable predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 88, 90, 91, **93**; EVAL-87 is `GO/BLOCKED` (`20261118T005436Z`). Traded-form monetization is complete/all-NO-GO. Do not modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-18T08:38:12Z (EVAL-92 built + sealed NO-GO; driver green; EVAL-93 mandated):** Ran the full driver before and after the build. Final `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0 at **2026-11-18T08:38:12Z**: env OK, **593/593 targeted + 27/27 diagnostics = 620**, **26** gates (EVAL-70..92 `SEALED`; EVAL-67 `NOT_DUE` overlap **140291.259s**, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`), **27** seal-gates ok; readiness refreshed overall_ok true. **EVAL-92** sealed `NO-GO CONFIRMED (PASS)` at **2026-11-18T08:32:12Z** (prereg+COMBINED `20261118T083212Z`), floor_ok true, 6 configs, 0 pass, best IC **-0.938390** `atm_iv::bar60::h6`, p 1.0000, 95% CI **[-0.9490, -0.9242]**, 0 BH-FDR; mechanical sign overlap means no reverse/traded-form interpretation. No sealed prior artifacts or `src/` modified. Next mandatory runnable-now work is **EVAL-93** (§NEXT MANDATORY BUILD), not another timestamp carry.

- **2026-11-18T09:24:17Z (EVAL-93 built + sealed GO; driver green; EVAL-94 mandated):** Ran the full driver before and after the build. Final `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0 at **2026-11-18T09:24:17Z**: env OK, **625/625 targeted + 27/27 diagnostics = 652**, **27** gates (EVAL-70..93 `SEALED`; EVAL-67 `NOT_DUE` overlap **137526.308s**, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`), **28** seal-gates ok; readiness refreshed overall_ok true. **EVAL-93** sealed `GO CONFIRMED` at **2026-11-18T09:18:58Z** (prereg+COMBINED `20261118T091858Z`), floor_ok true, 6 configs, 1 pass (`term_slope::bar300.0::h72`), 1 BH-FDR rejection; best IC **0.264843** at `term_slope::bar300.0::h72`, p **0.000999**, 95% CI **[0.0430, 0.4601]**. Cross-sectional term-slope basis (BTC-vs-ETH relative near-minus-far ATM IV term slope) predicts subsequent BTC-minus-ETH forward relative RV spread on real on-disk data. No sealed prior artifacts or `src/` modified. Next mandatory runnable-now work is **EVAL-94** (§NEXT MANDATORY BUILD), not another timestamp carry.