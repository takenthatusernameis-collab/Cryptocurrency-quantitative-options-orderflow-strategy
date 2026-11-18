# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-18T07:21:45Z — repo priority: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **VERIFIED STATE (2026-11-18T07:21:45Z):** full heavy driver `python3 scripts/eval67_prethreshold_progress.py --execute` completed **exit 0** at **2026-11-18T07:21:45Z** and refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` (env OK, **562/562 targeted + 27/27 diagnostics = 589**, **25** campaign gates all ok/classified, **26** seal-gate specs all ok). EVAL-70..91 are all **SEALED** (idempotent). **EVAL-91 sealed `GO CONFIRMED` at 2026-11-18T05:46:42Z** — causal **cross-sectional put-call SKEW basis → forward relative *vol-of-vol* spread** (`skew_ETH − skew_BTC` → `Vov_BTC − Vov_ETH`, `Vov_i = std_j(r_j^2)` over next H perp bars): 6 configs, **1** pass `skew::bar300::h72` (IC **0.215648**, directional perm p **0.000999**, block-bootstrap 95% CI **[0.0385, 0.3768] > 0**, floor_ok); no monetization claim. Predictiveness GOs: EVAL-71/73 (own-asset surface/stability), EVAL-77 (cross-sectional basis → RV spread), EVAL-83 (cross-asset spillover), EVAL-85 (skew → forward tail asymmetry), EVAL-86 (skew → forward VRP), EVAL-87 (atm_iv → forward tail asymmetry), EVAL-88 (basis → relative direction), EVAL-90 (atm_iv basis → relative vol-of-vol spread), **EVAL-91 (skew basis → relative vol-of-vol spread)** — all **with no net-of-cost monetization**. Traded-form taxonomy complete/all-NO-GO (level=straddle EVAL-72/75, slope=risk reversal EVAL-76, convexity=butterfly EVAL-82, cross-section=relative-value spread EVAL-80). Predictiveness NO-GOs: EVAL-70/74/75/76/78/79/80/81/82/84/89. Forward ladder: EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, `overlap_seconds ≈144878` at driver time, strictly decreasing toward 0), EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10; `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`, threshold **2026-11-20T00:00:00Z**. Forward wait is hard physics (EVAL-64 floor + disjoint window); not a fixable bottleneck.
>
> **FIRST ACTION, non-negotiable:** run
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Runs the full heavy-work loop (env check, **562** targeted + **27** diagnostics tests, all **25** campaign arbiters EVAL-70..91 then EVAL-67→68→69, auto-execute any `DUE`, **26** seal-gate checks, refresh `research_state/EVAL_67_PREWINDOW_READINESS.json`). **Require exit 0.** If `DUE` without execute, rerun with `--execute`; if `FAILED`, fix and rerun.
>
> **ANTI-AVOIDANCE RULE (core of this handoff):** a session that only re-runs the green driver and bumps this timestamp has **NOT** satisfied the contract and has done **no** heavy work. All runnable-now campaigns EVAL-70..91 are now SEALED and the forward ladder is **NOT_DUE/WAIT** pre-threshold. **The next genuine heavy work this session is therefore EITHER (a) the disjoint-forward EVAL-67 → EVAL-68 → EVAL-69 ladder at/after 2026-11-20T00:00:00Z (or immediately on any arbiter `DUE` exit 20 / `FAILED` exit 1), which the driver executes unskippably; OR (b) build + seal the next runnable-now campaign EVAL-92 (fully specified below).** Do **NOT** do a timestamp-only carry. EVAL-92 is the designated mandatory next build; alternates are listed if it proves degenerate.
>
> **NEXT-SESSION TRIGGER:** run the driver now. Act on any `DUE`(20)/`FAILED`(1) arbiter immediately. If still pre-threshold and all green/NOT_DUE/WAIT, **build + seal EVAL-92** (spec in §NEXT MANDATORY BUILD) — do not merely bump this timestamp.
>
> **Repo-priority reading:** thesis is *crypto OPTIONS **surface** + **options order-flow** + underlying order-flow → tradeable, net-of-cost alpha on REAL public data*. On-charter ladder EVAL-02..66 is **CLOSED**. Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62/64..66/70..91 artifacts or `src/`. Never synthetic data, never weaken EVAL-64 floor, paper-only.

## NEXT MANDATORY BUILD — EVAL-92 (fully specified; build this if the driver is green + ladder NOT_DUE/WAIT)

**EVAL-92 — cross-sectional near-ATM IV basis → forward relative *variance risk premium* (VRP) spread.** Economic question: *relative-value VRP via implied-vol level* — when ETH's near-ATM implied vol is rich relative to BTC's, does BTC subsequently carry the richer forward **variance risk premium** (`VRP_i = atm_iv_i(k) − forward_RV_i(k+1..k+H)`) relative to ETH? This complements EVAL-89 (same relative-VRP target but **skew** basis, sealed `NO-GO CONFIRMED`) using the **atm_iv** basis (which carried relative vol-of-vol GO in EVAL-90 and relative direction GO in EVAL-88), and is distinct from EVAL-77 (basis → RV spread), EVAL-86 (own-asset skew → own VRP), EVAL-88 (basis → relative direction), EVAL-90/91 (basis → relative vol-of-vol). It is a predictiveness claim only — **no traded-form / monetization claim**.

- **Runner:** `scripts/eval92_cross_sectional_atm_iv_basis_relative_vrp_spread.py`
- **Gate:** `scripts/eval92_phaseb_gate.py` (`SEALED`/`DUE`(20)/`FAILED`(1)); `TASK_ID = "INIT-2026-11-18T<HH:MM:00Z choose ≤ now>-EVAL92-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VRP-SPREAD"` (pick at/just before seal time); artifact stamp must be ≥ that floor.
- **Tests:** `tests/test_eval92_cross_sectional_atm_iv_basis_relative_vrp_spread.py` + `tests/test_eval92_phaseb_gate.py` (mirror the EVAL-90/91 template: runner behavior + deterministic verdict logic + gate status/seal/idempotence).
- **Signal (reuse EVAL-77 / EVAL-90 verbatim):** `rel_z_k = expanding_z( atm_iv_ETH(k) − atm_iv_BTC(k) )` on the common aligned bar grid (`e77.build_cross_section`, `e77._relative_signal_series(surface_signal="atm_iv")`). Use the **atm_iv** basis (distinct from EVAL-89's skew basis). `atm_iv_i(k)` is the contemporaneous near-ATM IV level at decision bar k (same causal surface input used in EVAL-71/77/88/90).
- **Target (reuse EVAL-89 VRP definition on common grid):** per underlying `VRP_i(k) = atm_iv_i(k) − forward_RV_i(k+1..k+H)` where `forward_RV_i` is the forward realized vol over the next H perp bars (same definition/helpers as `scripts/eval89_cross_sectional_skew_basis_relative_vrp_spread.py`, e.g. `_forward_vrp_on_common` / `_forward_rel_vrp_spread` or equivalent built on EVAL-77 common aligned closes + EVAL-71 atm_iv series). Compute per-underlying on the **common aligned grid** and target `y_k = VRP_BTC(k) − VRP_ETH(k)`.
- **Grid / horizons:** `surface_signals=("atm_iv",)`, `bar_seconds∈{60,300}`, `H∈{6,24,72}` (6 configs); Spearman rank `IC = rho(rel_z_k, y_k)`, H1 `IC>0` (ETH IV-rich → BTC carries richer forward VRP). Reuse EVAL-65 `_perm_p_ic` / `_boot_ci_ic` + EVAL-62 constants verbatim.
- **GO bar:** GO only if ≥1 config has IC>0, directional permutation p<0.05, block-bootstrap 95% CI lower>0, ≥`MIN_USABLE_PAIRS_PER_CONFIG`(=120) pairs, and pooled BH-FDR rejects it; else `NO-GO CONFIRMED (PASS)`.
- **Floor (compose, do not weaken):** EVAL-71 surface floor for BOTH BTC and ETH (verbatim) AND the EVAL-77 cross-sectional alignment floor (≥200 common bars on the coarsest grid). Below floor ⇒ `BLOCKED`, never NO-GO.
- **Primitives to reuse (do not reimplement):** `scripts/eval61_*`, `eval62_*`, `eval65_*`, `eval71_surface_iv_rv_predictiveness.py`, `eval77_cross_sectional_surface_basis_rv_predictiveness.py`, and the VRP-on-common-grid helpers/pattern from `scripts/eval89_cross_sectional_skew_basis_relative_vrp_spread.py` / `eval86_surface_skew_forward_vrp_predictiveness.py`. No new acquisition, no network, no `src/` edits.
- **Driver wiring (mirror EVAL-91 exactly):** add the 2 test files to `TARGETED_TEST_FILES`; add an `EVAL-92` entry to `GATE_SPECS` (`wait_phase:"DUE"`) and `SEAL_SPECS` (`expected_exit:1` until sealed; set to `0` after sealing); bump `EXPECTED_TARGETED_TESTS` by the new test count; add `eval92` to readiness gates/seal-gates handling as applicable. Re-run the driver to green.
- **Seal:** `python3 scripts/eval92_phaseb_gate.py --execute` → require exit 0 (then set seal-gate `expected_exit:0` for EVAL-92 in driver and re-run driver green).

**Alternates if EVAL-92 is degenerate** (same template, pick the first non-degenerate floor-clean result): (a) cross-sectional **term-structure slope** basis (ETH−BTC near-minus-far ATM IV slope) → forward relative **RV spread** (distinct from EVAL-77 which used atm_iv/skew bases, and from EVAL-74/84 own-asset term slope); (b) single-asset **atm_iv → forward vol-of-vol** (EVAL-84 used term_slope, NO-GO not portable); (c) single-asset **term_slope → forward VRP** (EVAL-74→RV, EVAL-84→vol-of-vol; VRP target distinct). Do NOT rebuild a collar (sign-flipped risk reversal = EVAL-76), do NOT re-litigate any sealed EVAL-70..91 cell, do NOT weaken the EVAL-64 floor, do NOT touch `src/`.

## PHYSICS-INDEPENDENT RUNNABLE-NOW CAMPAIGNS (EVAL-70..91 — all SEALED)

- **EVAL-70** — underlying (OKX perp) order-flow → forward RV / signed return: **SEALED `NO-GO CONFIRMED`**.
- **EVAL-71** — options implied-vol surface (near-ATM IV + put-call skew) → forward RV: **SEALED `GO CONFIRMED`** (BTC IC 0.335, ETH 0.263; 10 BH-FDR).
- **EVAL-72** — EVAL-71 level/skew → signal-timed delta-hedged ATM straddle net-of-cost: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-73** — EVAL-71 surface predictiveness disjoint-split OOS stability: **SEALED `GO CONFIRMED (PASS)`**.
- **EVAL-74** — options implied-vol term structure (near-minus-far ATM IV slope) → forward RV: **SEALED `NO-GO CONFIRMED (PASS)`** (not portable).
- **EVAL-75** — EVAL-74 term structure → signal-timed ATM straddle net-of-cost: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-76** — EVAL-71 skew → signal-timed delta-hedged risk reversal net-of-cost: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-77** — cross-sectional options basis (BTC-vs-ETH relative near-ATM IV/skew) → BTC-minus-ETH RV spread: **SEALED `GO CONFIRMED`** (best IC 0.2972 `atm_iv::bar300::h72`; 7 BH-FDR).
- **EVAL-78** — options order-flow imbalance × surface interaction → forward RV: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-79** — options order-flow × cross-sectional basis → forward RV: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-80** — EVAL-77 cross-sectional basis → signal-timed two-leg relative-value delta-hedged ATM straddle spread net-of-cost: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-81** — options order-flow imbalance → subsequent signed (directional) return: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-82** — EVAL-71 surface → signal-timed delta-hedged butterfly net-of-cost: **SEALED `NO-GO CONFIRMED (PASS)`**. Traded-form taxonomy complete/all-NO-GO.
- **EVAL-83** — cross-asset options-surface lead-lag spillover → other crypto's forward RV: **SEALED `GO CONFIRMED`** (bidirectional; 7 BH-FDR).
- **EVAL-84** — term-structure slope/ratio → forward vol-of-vol: **SEALED `NO-GO CONFIRMED (PASS)`** (not portable).
- **EVAL-85** — causal put-call skew → forward return tail asymmetry: **SEALED `GO CONFIRMED`** (BTC+ETH, 9 pooled BH-FDR).
- **EVAL-86** — causal put-call skew → forward VRP: **SEALED `GO CONFIRMED`**.
- **EVAL-87** — causal near-ATM implied vol → forward return tail asymmetry: **SEALED `GO/BLOCKED`** (prereg+COMBINED `20261118T005436Z`).
- **EVAL-88** — causal cross-sectional basis (ETH−BTC) → forward relative *direction* (BTC-minus-ETH signed return spread): **SEALED `GO CONFIRMED`** (best `atm_iv::bar60::h6` IC 0.1087, 1 BH-FDR).
- **EVAL-89** — causal cross-sectional put-call SKEW basis → forward relative *VRP* spread: **SEALED `NO-GO CONFIRMED (PASS)`** (best IC −0.1701, 0 BH-FDR).
- **EVAL-90** — causal cross-sectional near-ATM IV basis → forward relative *vol-of-vol* spread: **SEALED `GO CONFIRMED`** (best IC 0.322168 `atm_iv::bar300::h72`, 3 BH-FDR).
- **EVAL-91** — causal cross-sectional put-call SKEW basis → forward relative *vol-of-vol* spread: **SEALED `GO CONFIRMED`** at **2026-11-18T05:46:42Z** (1 pass `skew::bar300::h72`, IC **0.215648**, perm p **0.000999**, 95% CI **[0.0385, 0.3768] > 0**, floor_ok; no monetization claim).

These twenty-two (EVAL-70..91) are idempotent no-ops once sealed. The forward-gated ladder below is the next genuine disjoint-window heavy work (at/after `2026-11-20T00:00:00Z`). **When EVAL-70..91 are sealed and the ladder is not yet DUE, the next agent MUST build + seal EVAL-92 (§NEXT MANDATORY BUILD) — do NOT do a timestamp-only carry.**

## THREE SEQUENTIAL HEAVY CAMPAIGNS (repo-priority order)

1. **EVAL-67 — BTC-only predictiveness (FIRST):** task `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`; arbiter `python3 scripts/eval67_phaseb_gate.py`. Physics-gated to a disjoint forward window; prereg threshold `2026-11-20T00:00:00Z`. BTC-only recorded pre-run as underpowered.
2. **EVAL-68 — pooled BTC+ETH predictiveness (SECOND):** task `INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS`; arbiter `python3 scripts/eval68_phaseb_gate.py`. Power-adequate pooled rank-IC (≥790 pooled pairs). Acquires only after EVAL-67 seals; gate returns `WAIT_EVAL67` until then.
3. **EVAL-69 — pooled BTC+ETH TRADED-FORM net-of-cost monetization (THIRD, repo-priority capstone):** task `INIT-2026-11-16T22:45:00Z-EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS`; arbiter `python3 scripts/eval69_phaseb_gate.py`. Reuses EVAL-68's disjoint forward capture with **no new acquisition**; pooled net-of-cost Sharpe / max-DD / directional permutation / block-bootstrap of the signal-timed delta-hedged ATM straddle. Runs only after EVAL-68 seals; gate returns `WAIT_EVAL68` until then.

## DETERMINISTIC COMPLETION CONTRACT

- `python3 scripts/eval67_phaseb_gate.py` → `SEALED`(0) complete; `NOT_DUE`(10) correct carry; `DUE`(20) run `--execute` now; `FAILED`(1) fix and re-run.
- `python3 scripts/eval68_phaseb_gate.py` → `SEALED`(0) complete; `WAIT_EVAL67`(10) do not acquire; `DUE`(20) run `--execute`; `FAILED`(1) fix and re-run.
- `python3 scripts/eval69_phaseb_gate.py` → `SEALED`(0) ladder complete; `WAIT_EVAL68`(10) do not run; `DUE`(20) run `--execute`; `FAILED`(1) fix and re-run.
- `--execute` is the unskippable path: EVAL-67/68 acquire a disjoint real forward capture → dry-run → seal prereg + COMBINED/BLOCKED → seal-gate, and refuse to exit 0 unless the seal-gate exits 0. EVAL-69 does not acquire; it consumes EVAL-68's capture.
- The orchestrator runs arbiters sequentially so EVAL-67→68→69 can proceed in one invocation once eligible.

## PRE-THRESHOLD HEAVY WORK (while gates are `NOT_DUE`/`WAIT`)

The orchestrator does all of this automatically. Run it with `--execute` every session. It must report:
- `env_check: true`
- `targeted_tests: 562/562`
- `diagnostic_tests: 27/27`
- `gates`: EVAL-70..91 `SEALED`, EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` (pre-threshold) — 25 gates
- `seal_gates`: 26 ok (EVAL-66, 70..91 exit 0; EVAL-67/68/69 exit 1 until sealed)
- `overall_ok: true`, exit code 0

If it reports `exit_code: 20`, a campaign is `DUE`: re-run with `--execute`. If it reports `exit_code: 1`, fix the reported failed step and re-run. Do not replace this loop with a timestamp-only handoff bump. If green and the ladder is still NOT_DUE/WAIT, **build + seal EVAL-92**.

## STATUS (verified 2026-11-18T07:21:45Z)

- **Driver/readiness (green):** `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0 at **2026-11-18T07:21:45Z**; env OK; **562/562 targeted**, **27/27 diagnostics** (589 total); **25** gates ok/classified (EVAL-70..91 `SEALED`, EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`); **26** seal-gates ok. `research_state/EVAL_67_PREWINDOW_READINESS.json` refreshed (overall_ok true).
- **EVAL-70..91:** `SEALED` (idempotent). GOs: EVAL-71/73, EVAL-77, EVAL-83, EVAL-85, EVAL-86, EVAL-87, EVAL-88, EVAL-90, **EVAL-91** (skew basis → relative vol-of-vol spread, GO CONFIRMED 2026-11-18T05:46:42Z, pass `skew::bar300::h72` IC 0.215648, perm p 0.000999, CI [0.0385,0.3768]). All others `NO-GO CONFIRMED (PASS)` incl. every traded-form monetization (EVAL-72/75/76/80/82), order-flow predictiveness (EVAL-70/78/79/81), EVAL-74 (not portable), EVAL-84 (not portable), and EVAL-89. Traded-form taxonomy complete/all-NO-GO. Seal gates exit 0.
- **EVAL-67:** `NOT_DUE` (exit 10); `disjoint=false`; `overlap_seconds` ≈144878 at driver time (strictly decreasing toward 0); prereg present; no COMBINED/BLOCKED; `data/raw/eval67/` absent.
- **EVAL-68:** `WAIT_EVAL67` (exit 10); `eval67_sealed=false`; prereg present; `data/raw/eval68/` absent.
- **EVAL-69:** `WAIT_EVAL68` (exit 10); `eval68_sealed=false`; prereg present; acquires nothing.
- **Hard data constraint:** earliest disjoint capture end **2026-11-19T18:08:16Z** (threshold **2026-11-20T00:00:00Z**). Do not switch to past/disjoint-retro windows.
- **Bottlenecks:** no fixable pre-threshold bottleneck (forward wait is hard physics). Cron owns polling. **All runnable-now campaigns EVAL-70..91 are sealed; the mandatory next runnable-now build is EVAL-92 (§NEXT MANDATORY BUILD).** Do not do a timestamp-only carry — build EVAL-92 or wait for the threshold / a `DUE`/`FAILED` arbiter.

## BOTTLENECKS REMOVED (do not rediscover)

1. **Zombie capture bridge + liveness churn — REMOVED.** Do not recreate any bridge/waiter process.
2. **Competing handoff pointers / timestamped copies — REMOVED.** This file is the single handoff. Do not create copies.
3. **EVAL-68 "design-only" bottleneck — REMOVED.** Built/tested/prereg'd/gated.
4. **EVAL-69 "no traded-form monetization campaign" bottleneck — REMOVED.** Built/tested/prereg'd/gated.
5. **Forward wait — HARD PHYSICS, not fixable.** Only floor-compliant disjoint window is forward. Do not run a naive trailing capture before threshold.
6. **Power / sample-adequacy — recorded pre-run; do not rationalize post-hoc.** EVAL-67 BTC-only underpowered; EVAL-68/69 pooled at floor power-adequate.
7. **Manual pre-threshold loop / timestamp-only carry — REMOVED.** `scripts/eval67_prethreshold_progress.py` enforces the full loop. A session that only bumps this timestamp has not satisfied the contract.
8. **Repeated pre-threshold agent-session churn — REMOVED.** External `*/5` cron owns routine pre-threshold polling. Next agentic session is triggered by threshold or a `DUE`/`FAILED` arbiter and must run the driver and, if still green/NOT_DUE/WAIT, **build + seal EVAL-92**.
9. **Stale diagnostic test assertion — REMOVED.** `tests/test_campaign_resume.py` checks current campaigns.
10. **Post-EVAL-7x pre-threshold heavy-work gaps — CLOSED by EVAL-70..91.** All sealed runnable-now cells wired into the driver. Do NOT rebuild a collar (sign-flipped risk reversal = EVAL-76).
11. **Handoff bloat — REMOVED.** Single consolidated handoff; session log keeps only load-bearing recent entries.
12. **"No heavy work left pre-threshold" avoidance — REMOVED (renewed 2026-11-18T07:21:45Z, EVAL-91 sealed).** EVAL-92 is fully specified in §NEXT MANDATORY BUILD with alternates. With EVAL-70..91 sealed and the ladder WAIT/NOT_DUE, the next session MUST build + seal EVAL-92 (not a timestamp-only carry). The reusable EVAL-90/91 template makes the build mechanical.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..91 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting, single acquisition process (EVAL-68 acquires BTC+ETH in ONE call; EVAL-69 acquires nothing).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
- Do **not** use retired compact task IDs; use the three EVAL-67/68/69 task IDs and the EVAL-7x/8x/9x task ids in `SEAL_SPECS`.
- Do **not** switch EVAL-67/68/69 to a disjoint *past* window. Do **not** acquire EVAL-68 before EVAL-67 seals; do **not** run EVAL-69 before EVAL-68 seals.
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

# 2) Individual arbiters (status; add --execute to run). EVAL-70..91 SEALED (idempotent).
python3 scripts/eval70_phaseb_gate.py          # SEALED (NO-GO)
python3 scripts/eval71_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval72_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval73_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval74_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval75_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval76_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval77_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval78_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval79_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval80_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval81_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval82_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval83_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval84_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval85_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval86_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval87_phaseb_gate.py          # SEALED (GO/BLOCKED)
python3 scripts/eval88_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval89_phaseb_gate.py          # SEALED (NO-GO CONFIRMED)
python3 scripts/eval90_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval91_phaseb_gate.py          # SEALED (GO CONFIRMED)
python3 scripts/eval67_phaseb_gate.py          # NOT_DUE (pre-threshold)
python3 scripts/eval68_phaseb_gate.py          # WAIT_EVAL67 (pre-threshold)
python3 scripts/eval69_phaseb_gate.py          # WAIT_EVAL68 (pre-threshold)

# 3) Targeted suites (the orchestrator runs these; includes EVAL-91):
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q \
  tests/test_eval70_underlying_oflow_rv_predictiveness.py tests/test_eval70_phaseb_gate.py \
  tests/test_eval67_btc_oflow_tox_rv_oos.py tests/test_eval67_phaseb_gate.py \
  tests/test_eval67_prethreshold_progress.py \
  tests/test_eval66_eth_oflow_tox_rv_oos.py tests/test_eval65_orderflow_tox_rv_predictiveness.py \
  tests/test_eval68_pooled_btc_eth_oflow_tox_rv_oos.py tests/test_eval68_phaseb_gate.py \
  tests/test_eval69_pooled_btc_eth_oflow_tox_rv_traded_oos.py tests/test_eval69_phaseb_gate.py \
  tests/test_eval71_surface_iv_rv_predictiveness.py \
  tests/test_eval72_surface_skew_straddle_monetization.py \
  tests/test_eval73_surface_iv_rv_stability_split.py \
  tests/test_eval74_surface_term_structure_predictiveness.py \
  tests/test_eval75_term_structure_straddle_monetization.py \
  tests/test_eval76_surface_skew_risk_reversal_monetization.py \
  tests/test_eval77_cross_sectional_surface_basis_rv_predictiveness.py \
  tests/test_eval78_oflow_x_surface_rv_predictiveness.py \
  tests/test_eval79_oflow_x_cross_sectional_basis_rv_predictiveness.py tests/test_eval79_phaseb_gate.py \
  tests/test_eval80_cross_sectional_relative_value_straddle_monetization.py tests/test_eval80_phaseb_gate.py \
  tests/test_eval81_oflow_directional_return_predictiveness.py tests/test_eval81_phaseb_gate.py \
  tests/test_eval82_surface_skew_butterfly_monetization.py tests/test_eval82_phaseb_gate.py \
  tests/test_eval83_cross_asset_surface_spillover_rv_predictiveness.py tests/test_eval83_phaseb_gate.py \
  tests/test_eval84_term_structure_vol_of_vol_predictiveness.py tests/test_eval84_phaseb_gate.py \
  tests/test_eval85_surface_skew_forward_return_tail.py tests/test_eval85_phaseb_gate.py \
  tests/test_eval86_surface_skew_forward_vrp_predictiveness.py tests/test_eval86_phaseb_gate.py \
  tests/test_eval87_surface_atm_iv_forward_tail_asymmetry.py tests/test_eval87_phaseb_gate.py \
  tests/test_eval88_cross_sectional_surface_basis_directional_spread.py tests/test_eval88_phaseb_gate.py \
  tests/test_eval89_cross_sectional_skew_basis_relative_vrp_spread.py tests/test_eval89_phaseb_gate.py \
  tests/test_eval90_cross_sectional_atm_iv_basis_relative_vol_of_vol_spread.py tests/test_eval90_phaseb_gate.py \
  tests/test_eval91_cross_sectional_skew_basis_relative_vol_of_vol_spread.py tests/test_eval91_phaseb_gate.py
python3 -m pytest -q tests/test_controller_progress_accounting.py \
  tests/test_workflow_diagnostics_scanner.py \
  tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py

# 4) Seal gates (EVAL-66, 70..91 exit 0; EVAL-67/68/69 exit 1 until sealed). Driver runs all 26.
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-18T05:30:00Z-EVAL91-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VOL-OF-VOL-SPREAD" \
  --glob "EVAL_91_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_PREREGISTRATION_*" \
  --require-any-glob "EVAL_91_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED_*" \
  --require-any-glob "EVAL_91_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_BLOCKED_*"

# 5) Phase-B only, at/after 2026-11-20T00:00:00Z (orchestrator does this):
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, 70..91 sealed. EVAL-63 never sealed. Notable sealed outcomes: EVAL-46..60,62,64,65,70,72,74..76,78..82,84,89 `NO-GO CONFIRMED (PASS)`; EVAL-61 `NO-GO` (artifact); EVAL-66 `BLOCKED`; EVAL-71,73,77,83,85,86,88,90,91 `GO CONFIRMED` (predictiveness only, no net-of-cost monetization); EVAL-87 `GO/BLOCKED` (20261118T005436Z). Traded-form monetization taxonomy (straddle/risk-reversal/butterfly/relative-value spread) complete and all NO-GO. EVAL-67/68/69 remain the forward-gated disjoint-window ladder (NOT_DUE/WAIT). Do not re-seal or modify sealed artifacts.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-18T07:21:45Z (green driver verified; EVAL-91 confirmed sealed GO CONFIRMED; handoff refreshed, EVAL-92 mandated):** Full driver `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0 at **2026-11-18T07:21:45Z** (env OK, **562/562 targeted + 27/27 diagnostics = 589**, **25** gates: EVAL-70..91 `SEALED`, EVAL-67 `NOT_DUE` overlap ~144878, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`; **26** seal-gates ok; readiness refreshed overall_ok true). **EVAL-91** (cross-sectional skew basis → forward relative vol-of-vol spread) is sealed `GO CONFIRMED` at **2026-11-18T05:46:42Z** (6 configs, 1 pass `skew::bar300::h72`, IC 0.215648, perm p 0.000999, 95% CI [0.0385,0.3768], floor_ok; prereg+COMBINED `20261118T054642Z`; no monetization claim). With EVAL-70..91 sealed and ladder WAIT/NOT_DUE, handoff updated with mandatory **EVAL-92** (cross-sectional near-ATM IV basis → forward relative VRP spread) spec + alternates so the next session cannot do a timestamp-only carry. No sealed artifacts or `src/` modified.

- **2026-11-18T05:22:50Z (green driver; EVAL-90 built + sealed GO CONFIRMED):** EVAL-90 (cross-sectional atm_iv basis → relative vol-of-vol spread) sealed GO CONFIRMED at 2026-11-18T04:48:40Z (best IC 0.322168, 3 BH-FDR). Driver green 534/534 targeted, 27/27 diagnostics, 24 gates, 25 seals.

- **2026-11-18T04:04:54Z (EVAL-89 built + sealed NO-GO CONFIRMED):** EVAL-89 (cross-sectional skew basis → relative VRP spread) sealed NO-GO at 2026-11-18T03:58:33Z.

- **2026-11-18T02:15:00Z (EVAL-88 built + sealed GO CONFIRMED):** EVAL-88 (cross-sectional basis → relative direction) sealed GO at 2026-11-18T02:12:42Z.

- **Prior sessions (2026-11-16 → 2026-11-18T01:29:00Z, condensed):** Built/sealed EVAL-70..87; EVAL-66 BLOCKED. EVAL-67/68/69 built/tested/prereg'd/gated, correctly NOT_DUE/WAIT; forward wait hard physics until 2026-11-20T00:00:00Z. External `*/5` cron owns pre-threshold polling.

(Turn to the INITIAL TASK MESSAGE at the top for the authoritative next-session instruction; this log is context only.)

- **2026-11-18T08:15:32Z (session carry; driver re-run in progress, ladder still NOT_DUE/WAIT):** Re-ran `python3 scripts/eval67_phaseb_gate.py` / `eval68_phaseb_gate.py` / `eval69_phaseb_gate.py` — **EVAL-67 `NOT_DUE` (exit 10, overlap_seconds ~142716, disjoint=false), EVAL-68 `WAIT_EVAL67` (exit 10), EVAL-69 `WAIT_EVAL68` (exit 10)** at ~2026-11-18T08:15Z; earliest disjoint capture end remains `2026-11-19T18:08:16Z`, threshold `2026-11-20T00:00:00Z` (hard physics). Started required full heavy driver `python3 scripts/eval67_prethreshold_progress.py --execute` this session; a process is running but completion was not yet verified within this turn. Last green verified driver/readiness remains **2026-11-18T07:21:45Z** (562/562 targeted, 27/27 diagnostics, 25 gates, 26 seals, overall_ok true) per readiness JSON state on disk. EVAL-70..91 remain SEALED; no fixable bottlenecks found. Per anti-avoidance, once a green driver run is verified and ladder is still NOT_DUE/WAIT, next session must build + seal **EVAL-92** (§NEXT MANDATORY BUILD) rather than a timestamp-only carry. No sealed artifacts or `src/` modified.
