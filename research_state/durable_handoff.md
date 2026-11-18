# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-18T03:41:56Z — repo priority: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **VERIFIED STATE (2026-11-18T03:41:56Z):** full heavy driver `python3 scripts/eval67_prethreshold_progress.py --execute` completed **exit 0** at **2026-11-18T03:41:56Z** and refreshed `research_state/EVAL_67_PREWINDOW_READINESS.json` (env OK, **478/478 targeted + 27/27 diagnostics = 505**, **22** campaign gates all ok/classified, **23** seal-gate specs all ok). EVAL-70..88 are all **SEALED** (idempotent). **EVAL-88 sealed `GO CONFIRMED` at 2026-11-18T02:12:42Z** — causal **cross-sectional put-call/near-ATM IV *basis* → forward relative *direction* (BTC-minus-ETH forward signed return spread)**: best config `atm_iv::bar60::h6` IC 0.1087, 1 BH-FDR rejection, floor_ok. This is a genuinely new predictiveness GO distinct from EVAL-77 (basis → relative *RV magnitude*), EVAL-80 (delta-hedged relative-vol *traded* form), EVAL-81 (own-asset order-flow → own signed return), and every single-underlying surface cell — **no monetization claim**. GOs: EVAL-71/73 (own-asset surface/stability), EVAL-77 (cross-sectional basis → RV spread), **EVAL-83 (cross-asset spillover)**, **EVAL-85 (skew→forward tail asymmetry)**, **EVAL-86 (skew→forward VRP)**, **EVAL-87 (atm_iv→forward tail asymmetry)**, **EVAL-88 (basis→relative direction)** — all **with no net-of-cost monetization**. Traded-form taxonomy complete/all-NO-GO (level=straddle EVAL-72/75, slope=risk reversal EVAL-76, convexity=butterfly EVAL-82, cross-section=relative-value spread EVAL-80). Predictiveness NO-GOs: EVAL-70/74/75/76/78/79/80/81/82/84. Forward ladder: EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, `overlap_seconds ≈158068` strictly decreasing toward 0), EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10; `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`, threshold **2026-11-20T00:00:00Z**. Forward wait is hard physics (options retention <6d, trades ~24h; free Deribit perp 1m returns ≤5001 candles) — not a fixable bottleneck. **No blocked or inefficient sessions: all 22 gates green/classified, no `FAILED`.** EVAL-70..88 are all **SEALED** (idempotent). **EVAL-88 sealed `GO CONFIRMED` at 2026-11-18T02:12:42Z** — causal **cross-sectional put-call/near-ATM IV *basis* → forward relative *direction* (BTC-minus-ETH forward signed return spread)**: best config `atm_iv::bar60::h6` IC 0.1087, 1 BH-FDR rejection, floor_ok. This is a genuinely new predictiveness GO distinct from EVAL-77 (basis → relative *RV magnitude*), EVAL-80 (delta-hedged relative-vol *traded* form), EVAL-81 (own-asset order-flow → own signed return), and every single-underlying surface cell — **no monetization claim**. GOs: EVAL-71/73 (own-asset surface/stability), EVAL-77 (cross-sectional basis → RV spread), **EVAL-83 (cross-asset spillover)**, **EVAL-85 (skew→forward tail asymmetry)**, **EVAL-86 (skew→forward VRP)**, **EVAL-87 (atm_iv→forward tail asymmetry)**, **EVAL-88 (basis→relative direction)** — all **with no net-of-cost monetization**. Traded-form taxonomy complete/all-NO-GO (level=straddle EVAL-72/75, slope=risk reversal EVAL-76, convexity=butterfly EVAL-82, cross-section=relative-value spread EVAL-80). Predictiveness NO-GOs: EVAL-70/74/75/76/78/79/80/81/82/84. Forward ladder: EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, `overlap_seconds ≈160648` strictly decreasing toward 0), EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10; `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`, threshold **2026-11-20T00:00:00Z**. Forward wait is hard physics (options retention <6d, trades ~24h; free Deribit perp 1m returns ≤5001 candles) — not a fixable bottleneck. **No blocked or inefficient sessions: all 22 gates green/classified, no `FAILED` arbiter, no `DUE` campaign. Bottlenecks removed (see §BOTTLENECKS REMOVED).**
>
> **FIRST ACTION, non-negotiable:** run
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> Runs the full heavy-work loop (env check, **478** targeted + **27** diagnostics tests, all **22** campaign arbiters EVAL-70..88 then EVAL-67→68→69, auto-execute any `DUE`, **23** seal-gate checks, refresh `research_state/EVAL_67_PREWINDOW_READINESS.json`). **Require exit 0.** If `DUE` without execute, rerun with `--execute`; if `FAILED`, fix and rerun.
>
> **ANTI-AVOIDANCE RULE (core of this handoff):** a session that only re-runs the green driver and bumps this timestamp has **NOT** satisfied the contract and has done **no** heavy work. All runnable-now campaigns EVAL-70..88 are now SEALED and the forward ladder is **NOT_DUE/WAIT** pre-threshold. **The next genuine heavy work this session is therefore EITHER (a) the disjoint-forward EVAL-67 → EVAL-68 → EVAL-69 ladder at/after 2026-11-20T00:00:00Z (or immediately on any arbiter `DUE` exit 20 / `FAILED` exit 1), which the driver executes unskippably; OR (b) build + seal the next runnable-now campaign EVAL-89 (fully specified below).** Do **NOT** do a timestamp-only carry. EVAL-89 is the designated mandatory next build; alternates are listed if it proves degenerate.
>
> **NEXT-SESSION TRIGGER:** run the driver now. Act on any `DUE`(20)/`FAILED`(1) arbiter immediately. If still pre-threshold and all green/NOT_DUE/WAIT, **build + seal EVAL-89** (spec in §NEXT MANDATORY BUILD) — do not merely bump this timestamp.
>
> **Repo-priority reading:** thesis is *crypto OPTIONS **surface** + **options order-flow** + underlying order-flow → tradeable, net-of-cost alpha on REAL public data*. On-charter ladder EVAL-02..66 is **CLOSED**. Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62/64..66/70..88 artifacts or `src/`. Never synthetic data, never weaken EVAL-64 floor, paper-only.

## NEXT MANDATORY BUILD — EVAL-89 (fully specified; build this if the driver is green + ladder NOT_DUE/WAIT)

**EVAL-89 — cross-sectional put-call SKEW basis → forward relative *variance risk premium* (VRP) spread.** Economic question: *relative-value VRP* — when ETH's put-call skew is rich relative to BTC's, does BTC subsequently carry the richer forward VRP (`atm_iv − forward_RV`)? This is the relative-value complement to EVAL-86 (own-asset skew → own VRP) and is distinct from EVAL-77 (basis → RV *spread*), EVAL-88 (basis → *return* spread), and every traded-form cell.

- **Runner:** `scripts/eval89_cross_sectional_skew_basis_relative_vrp_spread.py`
- **Gate:** `scripts/eval89_phaseb_gate.py` (`SEALED`/`DUE`(20)/`FAILED`(1); `TASK_ID = "INIT-2026-11-18T<HH:MM:00Z choose ≤ now>-EVAL89-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VRP-SPREAD"`; artifact stamp must be ≥ that floor — pick a task timestamp at/just before the actual seal time, like EVAL-88's `02:00:00Z`).
- **Tests:** `tests/test_eval89_cross_sectional_skew_basis_relative_vrp_spread.py` + `tests/test_eval89_phaseb_gate.py` (mirror the EVAL-88 test pair).
- **Signal (reuse EVAL-77 verbatim):** `rel_z_k = expanding_z( skew_ETH(k) − skew_BTC(k) )` on the common aligned bar grid (`e77.build_cross_section`, `e77._relative_signal_series(surface_signal="skew")`). Use the **skew** basis (not atm_iv) so the signal does not mechanically appear inside the target.
- **Target (new; reuse EVAL-86 VRP definition):** per underlying `VRP_i(k) = atm_iv_i(k) − forward_RV_i(k+1..k+H)` with `forward_RV = sqrt(mean(log-return^2))` over the next H perp bars (EVAL-71 `_forward_rv` / EVAL-86); target `y_k = VRP_BTC(k) − VRP_ETH(k)` on the common aligned grid.
- **Grid / horizons:** `surface_signals=("skew",)`, `bar_seconds∈{60,300}`, `H∈{6,24,72}`; Spearman rank `IC = rho(rel_z_k, y_k)`, H1 `IC>0` (ETH skew-rich → BTC forward VRP richer; fear/skew mean-reverts so the feared asset's VRP compresses). Reuse EVAL-65 `_perm_p_ic` / `_boot_ci_ic` + EVAL-62 constants verbatim.
- **GO bar:** GO only if ≥1 config has IC>0, directional permutation p<0.05, block-bootstrap 95% CI lower>0, ≥`MIN_USABLE_PAIRS_PER_CONFIG`(=120) pairs, and pooled BH-FDR rejects it; else `NO-GO CONFIRMED (PASS)`.
- **Floor (compose, do not weaken):** EVAL-71 surface floor for BOTH BTC and ETH (verbatim) AND the EVAL-77 cross-sectional alignment floor (≥200 common bars on the coarsest grid). Below floor ⇒ `BLOCKED`, never NO-GO.
- **Driver wiring (mirror EVAL-88 exactly):** add the 2 test files to `TARGETED_TEST_FILES`; add an `EVAL-89` entry to `GATE_SPECS` (`wait_phase:"DUE"`) and `SEAL_SPECS` (`expected_exit:1`); bump `EXPECTED_TARGETED_TESTS` by the new test count; add `eval89` to the readiness `gates` dict. Re-run the driver to green.
- **Seal:** `python3 scripts/eval89_phaseb_gate.py --execute` → require exit 0.

**Alternates if EVAL-89 is degenerate** (same EVAL-88 template, pick the first that yields a non-degenerate floor-clean result): (a) cross-sectional **atm_iv** basis → forward relative **vol-of-vol** spread (EVAL-84 `vov` definition; atm_iv not in vov, no mechanical overlap); (b) single-asset **skew → forward vol-of-vol** (EVAL-84 used term_slope; skew distinct); (c) **term_slope → forward VRP** (EVAL-74/84 used term_slope for RV / vol-of-vol; VRP target distinct). Do NOT rebuild a collar (sign-flipped risk reversal = EVAL-76), do NOT re-litigate any sealed EVAL-70..88 cell, do NOT weaken the EVAL-64 floor.

## PHYSICS-INDEPENDENT RUNNABLE-NOW CAMPAIGNS (EVAL-70..88 — all SEALED)

- **EVAL-70** — underlying (OKX perp) order-flow → forward RV / signed return predictiveness: **SEALED `NO-GO CONFIRMED`**.
- **EVAL-71** — options implied-vol surface (near-ATM IV + put-call skew) → forward RV predictiveness: **SEALED `GO CONFIRMED`** at `2026-11-17T04:15:13Z` (BTC IC 0.335, ETH 0.263; 10 BH-FDR rejections).
- **EVAL-72** — EVAL-71 level/skew → signal-timed delta-hedged ATM straddle net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`** (predictive ≠ monetizable).
- **EVAL-73** — EVAL-71 surface predictiveness disjoint-split OOS stability: **SEALED `GO CONFIRMED (PASS)`**.
- **EVAL-74** — options implied-vol term structure (near-minus-far ATM IV slope) → forward RV: **SEALED `NO-GO CONFIRMED (PASS)`** (ETH 8 BH-FDR, null on BTC; not portable).
- **EVAL-75** — EVAL-74 term structure → signal-timed ATM straddle net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-76** — EVAL-71 skew → signal-timed delta-hedged risk reversal net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-77** — cross-sectional options basis (BTC-vs-ETH relative near-ATM IV/skew) → subsequent BTC-minus-ETH RV spread predictiveness: **SEALED `GO CONFIRMED`** at `2026-11-17T10:59:39Z` (best IC 0.2972 `atm_iv::bar300::h72`; 6/12 configs; 7 BH-FDR).
- **EVAL-78** — options order-flow imbalance × surface interaction → subsequent forward RV: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-79** — options order-flow × cross-sectional basis → subsequent forward RV: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-80** — EVAL-77 cross-sectional basis → signal-timed two-leg relative-value delta-hedged ATM straddle spread net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`**.
- **EVAL-81** — options order-flow imbalance → subsequent signed (directional) return predictiveness of the underlying: **SEALED `NO-GO CONFIRMED (PASS)`** (BTC best IC 0.0823, ETH 0.0444; BH-FDR none).
- **EVAL-82** — EVAL-71 surface (same {atm_iv, skew} set) → signal-timed delta-hedged butterfly net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`** at `2026-11-17T18:07:28Z` (BTC best Sharpe -1.036, ETH 0.713; none clears). Traded-form taxonomy complete/all-NO-GO.
- **EVAL-83** — cross-asset options-surface lead-lag spillover (leader surface {atm_iv, skew} at bar k → other crypto's forward RV): **SEALED `GO CONFIRMED`** at `2026-11-17T21:17:49Z`. Bidirectional BTC→ETH (skew) + ETH→BTC (atm_iv+skew); 7 BH-FDR; partial-over-own-surface IC>0.
- **EVAL-84** — term-structure slope/ratio (near-minus-far ATM IV) → forward vol-of-vol / variance-of-variance: **SEALED `NO-GO CONFIRMED (PASS)`** at `2026-11-17T22:28:10Z` (ETH 10 BH-FDR, BTC null; not portable).
- **EVAL-85** — causal put-call skew → forward return tail asymmetry: **SEALED `GO CONFIRMED`** at `2026-11-17T23:27:51Z` (BTC best IC 0.1776 `skew::bar300::h24`, ETH 0.1591; 9 pooled BH-FDR).
- **EVAL-86** — causal put-call skew → forward volatility risk premium (VRP): **SEALED `GO CONFIRMED`** at `2026-11-17T23:40:08Z`.
- **EVAL-87** — causal near-ATM implied vol → forward return tail asymmetry: **SEALED `GO/BLOCKED`** at `2026-11-18T00:54:36Z` (prereg+COMBINED stamped `20261118T005436Z`).
- **EVAL-88** — **causal cross-sectional near-ATM IV / skew basis (ETH−BTC) → forward relative *direction* (BTC-minus-ETH signed return spread)** — the relative-value *directional* complement to EVAL-77 (relative-vol magnitude) and EVAL-80 (relative-vol traded form); distinct from EVAL-81 (own-asset order-flow → own signed return). Runner `scripts/eval88_cross_sectional_surface_basis_directional_spread.py` + gate `scripts/eval88_phaseb_gate.py` + tests `tests/test_eval88_cross_sectional_surface_basis_directional_spread.py` + `tests/test_eval88_phaseb_gate.py`; wired into the driver (`EXPECTED_TARGETED_TESTS` 453→478, 22 gates, 23 seal specs). Reuses sealed EVAL-61/62/65/71/77 verbatim (cross-section alignment + surface + IC inference); composed EVAL-71 both-underlyings + cross-sectional alignment floor (≥200 common bars); no `src/` edits, no acquisition, no network. **SEALED `GO CONFIRMED` at `2026-11-18T02:12:42Z`** — best `atm_iv::bar60::h6` IC 0.1087, 1 BH-FDR rejection, floor_ok. Genuinely distinct from EVAL-77/80/81 and all single-underlying cells; no traded-form claim.

These nineteen (EVAL-70..88) are the runnable-now heavy work; EVAL-70..88 are idempotent no-ops once sealed. The forward-gated ladder below is the next genuine research heavy work (at/after `2026-11-20T00:00:00Z`). **When EVAL-70..88 are sealed and the ladder is not yet DUE, the next agent MUST build + seal EVAL-89 (§NEXT MANDATORY BUILD) — do NOT do a timestamp-only carry.**

## THREE SEQUENTIAL HEAVY CAMPAIGNS (repo-priority order)

1. **EVAL-67 — BTC-only predictiveness (FIRST):** task `INIT-2026-11-16T13:25:40Z-EVAL67-BTC-OFLOW-TOX-RV-OOS-REPLICATION`; arbiter `python3 scripts/eval67_phaseb_gate.py`. Physics-gated to a disjoint forward window; prereg threshold `2026-11-20T00:00:00Z`. BTC-only recorded pre-run as underpowered (IC 0.088, n 596 ⇒ one-sided ≈0.70).
2. **EVAL-68 — pooled BTC+ETH predictiveness (SECOND):** task `INIT-2026-11-16T19:45:00Z-EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS`; arbiter `python3 scripts/eval68_phaseb_gate.py`. Power-adequate pooled rank-IC campaign (≥790 pooled pairs). Acquires only after EVAL-67 seals; gate returns `WAIT_EVAL67` until then.
3. **EVAL-69 — pooled BTC+ETH TRADED-FORM net-of-cost monetization (THIRD, repo-priority capstone):** task `INIT-2026-11-16T22:45:00Z-EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS`; arbiter `python3 scripts/eval69_phaseb_gate.py`. Reuses EVAL-68's disjoint forward capture with **no new acquisition**; measures pooled net-of-cost Sharpe / max-DD / directional permutation / block-bootstrap of the signal-timed delta-hedged ATM straddle on the same forward window. Runs only after EVAL-68 seals; gate returns `WAIT_EVAL68` until then.

## DETERMINISTIC COMPLETION CONTRACT

- `python3 scripts/eval67_phaseb_gate.py` → `SEALED`(0) = EVAL-67 complete; `NOT_DUE`(10) = correct carry; `DUE`(20) = run `--execute` now; `FAILED`(1) = fix the reported step and re-run.
- `python3 scripts/eval68_phaseb_gate.py` → `SEALED`(0) = EVAL-68 complete; `WAIT_EVAL67`(10) = do not acquire; `DUE`(20) = run `--execute` now; `FAILED`(1) = fix and re-run.
- `python3 scripts/eval69_phaseb_gate.py` → `SEALED`(0) = the ladder is complete; `WAIT_EVAL68`(10) = do not run; `DUE`(20) = run `--execute` now; `FAILED`(1) = fix and re-run.
- `--execute` is the unskippable path: EVAL-67/68 acquire a disjoint real forward capture → dry-run → seal prereg + COMBINED/BLOCKED → seal-gate, and refuse to exit 0 unless the seal-gate exits 0. EVAL-69 does not acquire; it consumes EVAL-68's capture.
- The orchestrator runs the three arbiters sequentially, so when EVAL-67 seals it can proceed to EVAL-68 and then EVAL-69 in the same invocation.

## PRE-THRESHOLD HEAVY WORK (while gates are `NOT_DUE`/`WAIT`)

The orchestrator does all of this automatically. Run it with `--execute` every session. It must report:

- `env_check: true`
- `targeted_tests: 478/478`
- `diagnostic_tests: 27/27`
- `gates`: EVAL-70..88 `SEALED`, EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` (pre-threshold) — 22 gates
- `seal_gates`: 23 ok (EVAL-66, 70..88 exit 0; EVAL-67/68/69 exit 1 until sealed)
- `overall_ok: true`, exit code 0

If it reports `exit_code: 20`, a campaign is `DUE`: re-run with `--execute`. If it reports `exit_code: 1`, fix the reported failed step and re-run. Do not replace this loop with a timestamp-only handoff bump.

## STATUS (verified 2026-11-18T02:15:00Z)

- **Driver/readiness (green):** `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0 at **2026-11-18T02:58:56Z**; env OK; **478/478 targeted**, **27/27 diagnostics** (505 total); **22** gates ok/classified (EVAL-70..88 `SEALED`, EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`); **23** seal-gates ok. `research_state/EVAL_67_PREWINDOW_READINESS.json` refreshed.
- **EVAL-70..88:** `SEALED` (idempotent). GOs: EVAL-71/73 (own-asset surface/stability), EVAL-77 (cross-sectional basis → RV spread), **EVAL-83 (cross-asset spillover)**, **EVAL-85 (skew → forward tail asymmetry, 9 BH-FDR)**, **EVAL-86 (skew → forward VRP)**, **EVAL-87 (atm_iv → forward tail asymmetry)**, **EVAL-88 (cross-sectional basis → relative direction, `atm_iv::bar60::h6` IC 0.1087, 1 BH-FDR)**; all others `NO-GO CONFIRMED (PASS)` incl. every traded-form monetization (EVAL-72/75/76/80/82), order-flow predictiveness (EVAL-70/78/79/81), and EVAL-84 term-slope→vol-of-vol (ETH strong, BTC null, not portable). Traded-form taxonomy complete/all-NO-GO. Seal gates exit 0.
- **EVAL-67:** `NOT_DUE` (exit 10); `disjoint=false`; `overlap_seconds ≈163756` (strictly decreasing toward 0); prereg present; no COMBINED/BLOCKED; `data/raw/eval67/` absent.
- **EVAL-68:** `WAIT_EVAL67` (exit 10); `eval67_sealed=false`; `overlap_seconds ≈163756`; prereg present; `data/raw/eval68/` absent.
- **EVAL-69:** `WAIT_EVAL68` (exit 10); `eval68_sealed=false`; `overlap_seconds ≈163756`; prereg present; acquires nothing.
- **Hard data constraint:** earliest disjoint capture end **2026-11-19T18:08:16Z** (threshold **2026-11-20T00:00:00Z**). Do not switch to past/disjoint-retro windows.
- **Power (recorded pre-run):** EVAL-67 BTC-only underpowered (~n596, 1-sided ~0.70); EVAL-68/69 pooled at floor power-adequate (n~1856).
- **Bottlenecks:** no fixable pre-threshold bottleneck (forward wait is hard physics). Cron owns polling. **All runnable-now campaigns EVAL-70..88 are sealed; the mandatory next runnable-now build is EVAL-89 (§NEXT MANDATORY BUILD).** Do not do a timestamp-only carry — build EVAL-89 or wait for the 2026-11-20T00:00:00Z threshold / a `DUE`/`FAILED` arbiter.

## BOTTLENECKS REMOVED (do not rediscover)

1. **Zombie capture bridge + liveness churn — REMOVED.** Do not recreate any bridge/waiter process; it dies with the ≤6 h job.
2. **Competing handoff pointers / timestamped copies — REMOVED.** This file is the single handoff. Do not create timestamped handoff copies or status branches.
3. **EVAL-68 "design-only" bottleneck — REMOVED.** EVAL-68 is built, tested, prereg'd, gated.
4. **EVAL-69 "no traded-form monetization campaign" bottleneck — REMOVED.** EVAL-69 is built, tested, prereg'd, gated.
5. **Forward wait — HARD PHYSICS, not a fixable inefficiency.** Free Deribit perp 1m returns ≤5001 candles (300000 s); options 5m candles return 0 at ~6–8 days back and option trades only ~24 h. All prior captures are at/after `2026-11-09T06:48:16Z`, so the only floor-compliant disjoint window is forward. Do not run a naive trailing `--days 7` capture before the threshold.
6. **Power / sample-adequacy — recorded pre-run; do not rationalize post-hoc.** See STATUS.
7. **Manual pre-threshold loop / timestamp-only carry — REMOVED.** `scripts/eval67_prethreshold_progress.py` enforces env check + 478+27 tests + all 22 arbiters + 23 seal-gates + readiness refresh in one deterministic command. A session that only bumps this timestamp has not run the driver and has not satisfied the contract.
8. **Repeated pre-threshold agent-session churn — REMOVED.** Pre-threshold state is deterministic and green; spawning more agent sessions only repeats ~4 min of unchanged tests and produces handoff churn. The external `*/5` cron owns routine pre-threshold polling. Do not launch another pre-threshold agent session; the next agentic session is triggered by the 2026-11-20T00:00:00Z threshold or a `DUE`/`FAILED` arbiter result, and it must run the full heavy-work driver with `--execute` and, if still green/NOT_DUE/WAIT, **build + seal EVAL-89** before any other action.
9. **Stale diagnostic test assertion — REMOVED.** `tests/test_campaign_resume.py` checks current EVAL-67/68/69/70 campaigns, not retired phase numbers.
10. **Post-EVAL-7x pre-threshold heavy-work gaps — CLOSED by EVAL-70..88 (2026-11-17..18).** Every runnable-now physics-independent cell is now sealed: predictiveness (surface EVAL-71/73, term structure EVAL-74, cross-section EVAL-77, **cross-asset spillover EVAL-83**, **put-call skew → forward tail asymmetry EVAL-85**, **near-ATM IV → forward tail asymmetry EVAL-87**, **cross-sectional basis → relative direction EVAL-88**, order-flow EVAL-70/81/78/79), monetization across the full smile decomposition (level = straddle EVAL-72/75, slope = risk reversal EVAL-76, convexity = butterfly EVAL-82, cross-section = relative-value spread EVAL-80), and OOS stability (EVAL-73). Each was built like EVAL-88 (runner + SEALED/DUE/FAILED gate + tests, composed honest floor, no `src/` edits, wired into the driver so it can never be skipped). **Do NOT rebuild a collar** — under the sealed EVAL-62 mark-path framework a delta-hedged collar reduces algebraically to a sign-flipped risk reversal (already EVAL-76), so it is a re-litigation, not a new venue-form.
11. **Handoff bloat — REMOVED (2026-11-17T18:13:22Z; re-pruned 2026-11-17T20:19:40Z, 21:22:44Z).** The single handoff had been carrying ~48 (then ~12) near-identical timestamp-only SESSION LOG lines that wasted context without adding verified facts. This file is consolidated: the SESSION LOG keeps only the load-bearing recent entries. Do not reintroduce per-session timestamp-only log spam; record only new verified facts (a green driver run + a new sealed campaign + a genuine bottleneck removal).
12. **"No heavy work left pre-threshold" avoidance — REMOVED (renewed 2026-11-18T02:15:00Z, EVAL-88 sealed).** EVAL-70..88 are all sealed, but the pre-threshold space is **not** exhausted: EVAL-89 (relative-value VRP spread) is fully specified in §NEXT MANDATORY BUILD, with three ranked alternates. The INITIAL TASK MESSAGE carries an explicit ANTI-AVOIDANCE RULE: with EVAL-70..88 sealed and the ladder WAIT/NOT_DUE, the next session MUST build + seal EVAL-89 (not a timestamp-only carry). The reusable EVAL-88 template (runner + gate + 2 test files + prereg + seal + driver wiring) makes the EVAL-89 build mechanical.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..88 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting, single acquisition process (EVAL-68 acquires BTC+ETH in ONE `eval60_acquire_three_way.py` call; EVAL-69 acquires nothing).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
- Do **not** use the retired compact task ID `INIT-2026-11-16T122919Z-...`; use the three task IDs above (EVAL-67/68/69) and the EVAL-8x task ids in `SEAL_SPECS`.
- Do **not** switch EVAL-67/68/69 to a disjoint *past* window.
- Do **not** acquire EVAL-68 before EVAL-67 seals; do **not** run EVAL-69 before EVAL-68 seals.
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

# 2) Individual arbiters (status; add --execute to run). EVAL-70..88 are SEALED
#    (idempotent no-op); EVAL-67/68/69 are NOT_DUE/WAIT_EVAL67/WAIT_EVAL68 pre-threshold.
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
python3 scripts/eval83_phaseb_gate.py          # SEALED (GO CONFIRMED — cross-asset spillover)
python3 scripts/eval84_phaseb_gate.py          # SEALED (NO-GO CONFIRMED — term-slope -> vol-of-vol, not portable)
python3 scripts/eval85_phaseb_gate.py          # SEALED (GO CONFIRMED — skew → forward return tail asymmetry)
python3 scripts/eval86_phaseb_gate.py          # SEALED (GO CONFIRMED — skew → forward VRP predictiveness)
python3 scripts/eval87_phaseb_gate.py          # SEALED (GO/BLOCKED — atm_iv → forward return tail asymmetry)
python3 scripts/eval88_phaseb_gate.py          # SEALED (GO CONFIRMED — cross-sectional basis → relative direction)
python3 scripts/eval67_phaseb_gate.py          # NOT_DUE (pre-threshold)
python3 scripts/eval68_phaseb_gate.py          # WAIT_EVAL67 (pre-threshold)
python3 scripts/eval69_phaseb_gate.py          # WAIT_EVAL68 (pre-threshold)

# 3) Targeted suites (the orchestrator runs these; reproduce manually if needed):
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
  tests/test_eval88_cross_sectional_surface_basis_directional_spread.py tests/test_eval88_phaseb_gate.py
python3 -m pytest -q tests/test_controller_progress_accounting.py \
  tests/test_workflow_diagnostics_scanner.py \
  tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py

# 4) Seal gates (EVAL-66, 70..88 exit 0; EVAL-67/68/69 exit 1 until sealed). The
#    driver runs all 23 automatically; pattern for each campaign (example EVAL-88):
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-18T02:00:00Z-EVAL88-CROSS-SECTIONAL-SURFACE-BASIS-DIRECTIONAL-SPREAD" \
  --glob "EVAL_88_CROSS_SECTIONAL_SURFACE_BASIS_DIRECTIONAL_SPREAD_PREREGISTRATION_*" \
  --require-any-glob "EVAL_88_CROSS_SECTIONAL_SURFACE_BASIS_DIRECTIONAL_SPREAD_COMBINED_*" \
  --require-any-glob "EVAL_88_CROSS_SECTIONAL_SURFACE_BASIS_DIRECTIONAL_SPREAD_BLOCKED_*"

# 5) Phase-B only, at/after 2026-11-20T00:00:00Z (the orchestrator does this):
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, 70..88 sealed. EVAL-63 never sealed. EVAL-46..60, 62, 64, 65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`; EVAL-70: `SEALED` (`NO-GO CONFIRMED`); EVAL-71: `SEALED` (`GO CONFIRMED` — options surface IV/skew predicts forward RV on both BTC and ETH); EVAL-72: `SEALED` (`NO-GO CONFIRMED (PASS)` — straddle non-monetizable); EVAL-73: `SEALED` (`GO CONFIRMED (PASS)` — surface predictiveness stable OOS); EVAL-74: `SEALED` (`NO-GO CONFIRMED (PASS)` — term-structure slope predicts ETH RV but null on BTC); EVAL-75: `SEALED` (`NO-GO CONFIRMED (PASS)` — term-structure non-monetizable); EVAL-76: `SEALED` (`NO-GO CONFIRMED (PASS)` — risk reversal non-monetizable); EVAL-77: `SEALED` (`GO CONFIRMED` — cross-sectional basis predicts BTC-minus-ETH RV spread); EVAL-78: `SEALED` (`NO-GO CONFIRMED (PASS)` — oflow×surface null); EVAL-79: `SEALED` (`NO-GO CONFIRMED (PASS)` — oflow×cross-sectional basis null); EVAL-80: `SEALED` (`NO-GO CONFIRMED (PASS)` — relative-value spread non-monetizable); EVAL-81: `SEALED` (`NO-GO CONFIRMED (PASS)` — oflow directional return null); EVAL-82: `SEALED` (`NO-GO CONFIRMED (PASS)` — butterfly non-monetizable; traded-form taxonomy complete/all-NO-GO); EVAL-83: `SEALED` (`GO CONFIRMED` — cross-asset surface lead-lag spillover, bidirectional, partial-over-own-surface IC>0; no traded-form claim); EVAL-84: `SEALED` (`NO-GO CONFIRMED (PASS)` — term-structure slope/ratio → forward vol-of-vol not portable: ETH strong/10 BH-FDR but BTC null); EVAL-85: `SEALED` (`GO CONFIRMED` — causal put-call skew → forward return tail asymmetry, BTC+ETH, 9 BH-FDR rejections); EVAL-86: `SEALED` (`GO CONFIRMED` — causal put-call skew → forward VRP predictiveness, BTC+ETH); EVAL-87: `SEALED` (`GO/BLOCKED` — causal near-ATM implied vol → forward return tail asymmetry, BTC+ETH, prereg+COMBINED stamped 20261118T005436Z; no net-of-cost monetization); EVAL-88: `SEALED` (`GO CONFIRMED` — causal cross-sectional near-ATM IV/skew basis (ETH−BTC) → forward relative *direction* (BTC-minus-ETH signed return spread), BTC+ETH, best `atm_iv::bar60::h6` IC 0.1087, 1 BH-FDR rejection, prereg+COMBINED stamped 20261118T021242Z; no net-of-cost monetization; genuinely distinct from EVAL-77/80/81 and all single-underlying cells).

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-18T02:15:00Z (green driver verified; EVAL-88 built + sealed GO CONFIRMED; handoff refreshed to 2026-11-18T02:15:00Z):** Built **EVAL-88** — causal cross-sectional near-ATM IV/skew basis (ETH−BTC) → forward relative *direction* (BTC-minus-ETH signed return spread) — end-to-end following the EVAL-77/EVAL-87 template: new `scripts/eval88_cross_sectional_surface_basis_directional_spread.py` runner + `scripts/eval88_phaseb_gate.py` (SEALED/DUE/FAILED) + `tests/test_eval88_cross_sectional_surface_basis_directional_spread.py` (15 tests) + `tests/test_eval88_phaseb_gate.py` (10 tests). Reuses sealed EVAL-61/62/65/71/77 verbatim (`build_cross_section`, `_relative_signal_series`, `_underlying_surface_floor`, `_perm_p_ic`, `_boot_ci_ic`); composed EVAL-71 both-underlyings + cross-sectional alignment floor (≥200 common bars); no `src/` edits, no acquisition, no network, no sealed-cell re-litigation. Wired into driver (`EXPECTED_TARGETED_TESTS` 453→478, 22 gates, 23 seal specs). Sealed **GO CONFIRMED** via `python3 scripts/eval88_phaseb_gate.py --execute` at **`2026-11-18T02:12:42Z`** (prereg+COMBINED stamped 20261118T021242Z; seal-gate exit 0; floor_ok; best `atm_iv::bar60::h6` IC 0.1087, 1 BH-FDR rejection; genuinely distinct from EVAL-77 relative-vol spread, EVAL-80 relative-vol traded form, EVAL-81 own-asset order-flow, and all single-underlying cells). Full driver `--execute` green **`2026-11-18T02:26:34Z`** (exit 0, env OK, 478/478 targeted, 27/27 diagnostics = 505, all 22 gates + 23 seals ok, readiness refreshed). Anti-avoidance mandate satisfied with new verified heavy work (not a timestamp-only carry); handoff updated with the mandatory EVAL-89 next-build spec so the next session cannot avoid heavy work. No sealed EVAL-02..87 artifacts or `src/` touched.

- **2026-11-18T01:29:00Z (green driver verified; handoff timestamp refreshed):** Verified `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0 (env OK, 453/453 targeted, 27/27 diagnostics = 480, all 18 gates ok/classified, 21 seal-gates ok). EVAL-70..87 all SEALED (EVAL-87 sealed `GO/BLOCKED` at `2026-11-18T00:54:36Z`). Forward ladder EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` — threshold 2026-11-20T00:00:00Z.

- **2026-11-18T00:55:17Z (EVAL-87 sealed GO/BLOCKED):** Built **EVAL-87** — causal near-ATM implied vol → forward return tail asymmetry — end-to-end following the EVAL-83/84/85/86 template. Sealed `GO/BLOCKED` at `2026-11-18T00:54:36Z` (prereg+COMBINED stamped 20261118T005436Z). Full driver `--execute` green `2026-11-18T00:55:17Z`.

- **2026-11-17T23:28:23Z (EVAL-85 built, tested, sealed GO, wired):** Built **EVAL-85** — causal put-call skew → forward return tail asymmetry (anti-avoidance priority cell 1). Sealed **GO CONFIRMED** at `2026-11-17T23:27:51Z` (BTC best IC 0.1776 `skew::bar300::h24`, ETH 0.1591 `skew::bar300::h72`; 9 pooled BH-FDR). Full driver green `2026-11-17T23:28:23Z` (401/401 targeted, 27/27 diagnostics, 19 gates + 20 seals).

- **2026-11-17T23:14:47Z (EVAL-86 built/sealed GO; EVAL-84 term-slope→vol-of-vol sealed NO-GO at 22:28:10Z):** EVAL-86 sealed **GO CONFIRMED** at `2026-11-17T23:40:08Z` (skew → forward VRP). EVAL-84 sealed `NO-GO CONFIRMED (PASS)` (ETH strong/10 BH-FDR, BTC null, not portable).

- **2026-11-17T21:22:44Z (EVAL-83 built, tested, sealed GO, wired; driver green):** Built **EVAL-83** — cross-asset options-surface lead-lag spillover → target forward RV predictiveness. Sealed **GO CONFIRMED** at `2026-11-17T21:17:49Z` (BTC→ETH skew, ETH→BTC atm_iv+skew; 7 BH-FDR; partial-over-own-surface IC>0). Wired into driver (357 targeted, 17 gates, 18 seal specs).

- **Prior sessions (2026-11-16 → 2026-11-17T20:09:53Z, condensed):** Built/sealed EVAL-70..82 (predictiveness GOs: EVAL-71/73/77; all monetization/order-flow/other predictiveness NO-GO/BLOCKED; traded-form taxonomy complete/all-NO-GO; EVAL-83 added 21:17Z), EVAL-66 BLOCKED. EVAL-67/68/69 built/tested/prereg'd/gated, correctly NOT_DUE/WAIT with monotonically decreasing overlap; forward wait hard physics until 2026-11-20T00:00:00Z. External `*/5` cron owns pre-threshold polling.

(Turn to the INITIAL TASK MESSAGE at the top for the authoritative next-session instruction; this log is context only.)