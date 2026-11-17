# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-17T23:13:43Z — repo priority: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **VERIFIED STATE (2026-11-17T23:13:43Z):** full heavy driver `python3 scripts/eval67_prethreshold_progress.py --execute` completed exit 0 at 2026-11-17T23:13:43Z (env OK, 375/375 targeted + 27/27 diagnostics, all 18 gates SEALED/NOT_DUE/WAIT, 19 seal specs ok; readiness refreshed). EVAL-70..84 all SEALED. EVAL-84 sealed `NO-GO CONFIRMED (PASS)` at `2026-11-17T22:28:10Z` — term-structure slope/ratio (near-minus-far ATM IV, reused EVAL-74 signal/floor) vs forward vol-of-vol / variance-of-variance target: floor_ok=true; ETH 7 configs pass with 10 BH-FDR rejections (best IC 0.3652 `term_slope::bar300::h72`), but BTC null (best IC 0.051, no pass) so not portable across BTC+ETH. This closes the prioritized "term-slope → forward vol-of-vol" cell (distinct from sealed EVAL-74 slope→RV). Earlier sealed GOs remain: own-asset surface (EVAL-71/73), cross-sectional basis (EVAL-77), cross-asset spillover (EVAL-83); all with no net-of-cost monetization. Traded-form taxonomy remains complete/all-NO-GO: level=ATM straddle (EVAL-72/75), slope=risk reversal (EVAL-76), convexity=butterfly (EVAL-82), cross-section=relative-value spread (EVAL-80). Predictiveness NO-GOs: EVAL-70/74/75/76/78/79/80/81/82/84 (portable nulls / non-monetizable). Arbiters now (23:13Z): EVAL-84 `SEALED` exit 0; EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, `overlap_seconds 174157.613`, decreasing toward 0; `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`), EVAL-68 `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, overlap 174157.377), EVAL-69 `WAIT_EVAL68` exit 10 (`eval68_sealed=false`, overlap 174156.894). Forward wait is hard physics (options retention <6d, trades ~24h; free Deribit perp 1m returns ≤5001 candles). and wired into `scripts/eval67_prethreshold_progress.py` (**375 targeted + 27 diagnostics tests, 18 campaign arbiters, 19 seal specs**). **EVAL-84 sealed `NO-GO CONFIRMED (PASS)` at `2026-11-17T22:28:10Z`** — term-structure slope/ratio (near-minus-far ATM IV, reused EVAL-74 signal/floor) vs **forward vol-of-vol / variance-of-variance** target (std of squared log returns over bars k+1..k+H; distinct from EVAL-74's forward RV): floor_ok=true; ETH 7 configs pass with 10 BH-FDR rejections (best IC 0.3652 `term_slope::bar300::h72`), but **BTC null** (best IC 0.051, no pass) so not portable across BTC+ETH. This closes the prioritized "term-slope → forward vol-of-vol" cell (distinct from sealed EVAL-74 slope→RV). Earlier sealed GOs remain: **own-asset surface** (EVAL-71/73), **cross-sectional basis** (EVAL-77), **cross-asset spillover** (EVAL-83); all with **no net-of-cost monetization**. Traded-form taxonomy remains complete/all-NO-GO: **level=ATM straddle** (EVAL-72/75), **slope=risk reversal** (EVAL-76), **convexity=butterfly** (EVAL-82), **cross-section=relative-value spread** (EVAL-80). Predictiveness NO-GOs: EVAL-70/74/75/76/78/79/80/81/82/84 (portable nulls / non-monetizable). Arbiters now (22:55Z): EVAL-84 `SEALED` exit 0; EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, `overlap_seconds 175274.739`, decreasing toward 0; `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`), EVAL-68 `WAIT_EVAL67` exit 10 (`eval67_sealed=false`, overlap 175274.503), EVAL-69 `WAIT_EVAL68` exit 10 (`eval68_sealed=false`, overlap 175274.020). Forward wait is hard physics (options retention <6d, trades ~24h; free Deribit perp 1m returns ≤5001 candles). Last recorded full green driver before this session's EVAL-84 wiring: `2026-11-17T22:06:17Z` (357/357, 27/27, 17 gates, 18 seals). **A full `python3 scripts/eval67_prethreshold_progress.py --execute` run including EVAL-84 (375 targeted, 18 gates, 19 seals) was initiated 2026-11-17T22:29Z and may still be in progress on this runner; run it now to (re)verify a fully green readiness refresh at current state.**`
>
> **FIRST ACTION, non-negotiable:** run
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> That one command runs the full heavy-work loop (env check, **375** targeted + **27** diagnostics tests, all **18** campaign arbiters EVAL-70..84 then EVAL-67→68→69, auto-execute any `DUE`, **19** seal-gate checks, refresh `research_state/EVAL_67_PREWINDOW_READINESS.json`). **Do not exit until it exits 0.** If `DUE` without execute, rerun with `--execute`; if `FAILED`, fix and rerun.
>
> **ANTI-AVOIDANCE RULE (the entire point of this handoff):** a session that only re-runs the green driver and bumps this timestamp has **NOT** satisfied the contract and has done **no** heavy work. Because EVAL-70..84 are all sealed, the next genuine heavy work is **either** (a) the disjoint-forward **EVAL-67 → EVAL-68 → EVAL-69** ladder at/after **2026-11-20T00:00:00Z** (or immediately on any arbiter `DUE` exit 20 / `FAILED` exit 1), which the driver executes unskippably; **or (b) build + test + seal the NEXT physics-independent runnable-now campaign `EVAL-85`** on the repo charter (options surface + order-flow → tradeable net-of-cost alpha on the real on-disk captures), following the **EVAL-83/84 template**: new `scripts/eval85_*.py` runner + `scripts/eval85_phaseb_gate.py` (SEALED/DUE/FAILED) + two test files + prereg + COMBINED/BLOCKED seal + wire into `scripts/eval67_prethreshold_progress.py` (test list, gate spec, seal spec, `EXPECTED_TARGETED_TESTS`) so it can never be skipped; **no `src/` edits**, composed honest floor, no sealed-cell re-litigation. **Priority EVAL-85 cells (pick one genuinely distinct):** (3) **put-call skew → forward return asymmetry / tail** (signed tail/quantile or skewness target, distinct from skew→RV EVAL-71 and skew traded-forms EVAL-72/76); (4) **signal-timed VRP harvest across BTC+ETH** from the EVAL-71/73 GO surface signal as a traded-form (all prior monetization cells are NO-GO — this must be a genuinely different construction, not a re-litigated straddle/RR/butterfly/RV-spread); or another on-charter cell not covered by sealed EVAL-70..84. **Do NOT** re-litigate VPIN/large-trade clustering → forward RV (overlaps sealed EVAL-65 toxicity→RV NO-GO) and **do NOT** rebuild a collar (sign-flipped risk reversal = EVAL-76).
>
> **NEXT-SESSION TRIGGER:** start only at/after **2026-11-20T00:00:00Z**, or immediately when any phase-B arbiter reports `DUE` (exit 20) or `FAILED` (exit 1). External `*/5` cron owns routine pre-threshold polling — do **not** create another pre-threshold agent session merely to rerun unchanged green tests; if you are up, you must either execute a `DUE` arbiter or build `EVAL-84`.
>
> **Repo-priority reading:** thesis is *crypto OPTIONS **surface** + **options order-flow** + underlying order-flow → tradeable, net-of-cost alpha on REAL public data*. On-charter ladder EVAL-02..66 is **CLOSED**. Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62/64..66/70..83 artifacts or `src/`. Never synthetic data, never weaken EVAL-64 floor, paper-only.

## PHYSICS-INDEPENDENT RUNNABLE-NOW CAMPAIGNS (EVAL-70..83 — all SEALED; fill the pre-threshold heavy-work gap)

- **EVAL-70** — underlying (OKX perp) order-flow → forward RV / signed return predictiveness: **SEALED `NO-GO CONFIRMED`** (gate exit 0). Runnable now on on-disk captures; no acquisition.
- **EVAL-71** — options implied-vol surface (near-ATM IV + put-call skew) → forward RV predictiveness: **SEALED `GO CONFIRMED`** at `2026-11-17T04:15:13Z`. Surface predicts forward RV (BTC IC 0.335, ETH 0.263; 10 BH-FDR rejections). First GO in the predictiveness line; order-flow (EVAL-65/70) is null. EVAL-64 floor untouched.
- **EVAL-72** — EVAL-71 level/skew → signal-timed delta-hedged ATM straddle net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`**. Predictive surface does not monetize (BTC best Sharpe 0.8424, ETH -1.1967). Predictive ≠ monetizable.
- **EVAL-73** — EVAL-71 surface predictiveness disjoint-split OOS stability: **SEALED `GO CONFIRMED (PASS)`**. Both BTC and ETH beat 95th-pct null on a fresh disjoint capture; ETH 8 BH-FDR rejections.
- **EVAL-74** — options implied-vol term structure (near-minus-far ATM IV slope) → forward RV: **SEALED `NO-GO CONFIRMED (PASS)`**. Predicts ETH forward RV (8 BH-FDR rejections; best IC 0.362 `term_slope::bar300::h72`) but **null on BTC**; not portable beyond EVAL-71.
- **EVAL-75** — EVAL-74 term-structure → signal-timed ATM straddle net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`**. BTC best Sharpe 1.6331 (`term_slope::bar60`) but permutation p=0.0629 fails; ETH -0.1716; no config passes.
- **EVAL-76** — EVAL-71 skew → signal-timed delta-hedged **risk reversal** (nearest OTM call + OTM put) net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`**. Skew does not monetize via a risk reversal (BTC best Sharpe -0.9356, ETH -0.2033; no config passes).
- **EVAL-77** — cross-sectional options basis (BTC-vs-ETH relative near-ATM IV/skew) → subsequent BTC-minus-ETH RV spread predictiveness: **SEALED `GO CONFIRMED`** at `2026-11-17T10:59:39Z`. Best IC 0.2972 (`atm_iv::bar300::h72`); 6/12 configs pass; BH-FDR rejects 7. First cross-sectional GO.
- **EVAL-78** — options order-flow imbalance × surface interaction → subsequent forward RV: **SEALED `NO-GO CONFIRMED (PASS)`**. Conditional flow is null (BTC best IC 0.1764 but permutation p fails; ETH 0.0247; BH-FDR none).
- **EVAL-79** — options order-flow × cross-sectional basis → subsequent forward RV: **SEALED `NO-GO CONFIRMED (PASS)`**. Cross-sectional-basis-conditioned flow is null (BH-FDR none).
- **EVAL-80** — EVAL-77 cross-sectional basis → signal-timed two-leg relative-value delta-hedged ATM straddle spread net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`**. Best Sharpe -0.2657 (`skew::bar60`); no config passes; BH-FDR none. Predictive (EVAL-77) ≠ monetizable (cross-section).
- **EVAL-81** — options order-flow imbalance → subsequent **signed (directional) return** predictiveness of the underlying: **SEALED `NO-GO CONFIRMED (PASS)`**. The cell that matters most for direct tradeable alpha: BTC best IC 0.0823, ETH 0.0444; no config clears; BH-FDR none. Options-flow directional alpha is not present.
- **EVAL-82** — EVAL-71 surface (same {atm_iv, skew} set as EVAL-72) → signal-timed delta-hedged **butterfly** (smile-**convexity** structure: long OTM call wing + long OTM put wing, short ATM body) net-of-cost monetization: **SEALED `NO-GO CONFIRMED (PASS)`** at `2026-11-17T18:07:28Z`. floor_ok=true; 8 configs; BTC best Sharpe -1.036 (`atm_iv::bar60`), ETH best 0.713 (`atm_iv::bar300`); no config clears permutation + bootstrap + kill-switch on both underlyings; BH-FDR none. Conclusion: the surface does **not** monetize net-of-cost through a butterfly either — completing the all-NO-GO traded-form taxonomy (level = straddle, slope = risk reversal, convexity = butterfly, cross-section = relative-value spread). Composes the EVAL-61/62 traded floor + EVAL-71 surface floor + a butterfly-constructibility floor (≥200 priceable 4-leg butterfly states/underlying), none weakened; reuses EVAL-57/61/62/71/76 runners verbatim; no `src/` edits. Wired into the driver (329 tests, 16 gates, 17 seal specs) so it can never be skipped.
- **EVAL-83** — **cross-asset options-surface lead-lag spillover** (leader surface {atm_iv, skew} at bar k → *other* crypto's forward RV over k+1..k+H): **SEALED `GO CONFIRMED`** at `2026-11-17T21:17:49Z`. First **cross-asset temporal** GO, distinct from own-asset EVAL-71/73 and contemporaneous-basis EVAL-77. Bidirectional: **BTC→ETH** via **skew** (best IC 0.2806 `skew::bar300::h24`, 3 pass configs) and **ETH→BTC** via **atm_iv + skew** (best IC 0.2666 `atm_iv::bar300::h72`, 3 pass configs); every pass has **partial-over-own-surface IC>0** (so not merely the target's own surface re-expressed) and **7 BH-FDR rejections**. floor_ok=true; composed EVAL-71 surface floor (each underlying) + cross-asset common-bar floor (≥150 common bars/pair on the 300 s grid; actual 274), none weakened. Reuses EVAL-61/62/65/71 verbatim; no `src/` edits; makes **no traded-form claim**. Wired into the driver so it can never be skipped.
- **EVAL-84** — **term-structure slope/ratio (near-minus-far ATM IV) → forward vol-of-vol / variance-of-variance** (distinct forward target: `vov = sqrt(mean((v_i-mean(v))^2))`, `v_i=r_i^2`, vs EVAL-74's forward RV level): **SEALED `NO-GO CONFIRMED (PASS)`** at `2026-11-17T22:28:10Z`. floor_ok=true; 24 configs. ETH 7 configs pass with **10 BH-FDR rejections** (best IC 0.3652 `term_slope::bar300::h72`) but **BTC null** (best IC 0.051, 0 pass) ⇒ not portable across BTC+ETH. Same term-structure signal/floor as EVAL-74 (reused `e74._term_bars` / `e74._underlying_term_floor` verbatim, composed with EVAL-71 floor), different target; does not re-litigate EVAL-74 (slope→RV). No `src/` edits, no acquisition. Wired into the driver (375 tests, 18 gates, 19 seal specs).

These fifteen (EVAL-70..84) are the runnable-now heavy work; they are idempotent no-ops once sealed. The forward-gated ladder below is the next genuine research heavy work (at/after `2026-11-20T00:00:00Z`). **When all fifteen are sealed and the ladder is not yet DUE, the next agent MUST build + seal EVAL-85** (see the ANTI-AVOIDANCE RULE in the INITIAL TASK MESSAGE) rather than do a timestamp-only carry.

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
- `targeted_tests: 357/357`
- `diagnostic_tests: 27/27`
- `gates`: EVAL-70..83 `SEALED`, EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` (pre-threshold)
- `overall_ok: true`, exit code 0

If it reports `exit_code: 20`, a campaign is `DUE`: re-run with `--execute`. If it reports `exit_code: 1`, fix the reported failed step and re-run. Do not replace this loop with a timestamp-only handoff bump.

## STATUS (verified 2026-11-17T22:55:00Z; EVAL-84 sealed; last full green driver 2026-11-17T22:06:17Z pre-EVAL-84 wiring)

- **EVAL-70..84:** `SEALED` (idempotent). GO: EVAL-71/73/77 (own-asset surface / surface stability / cross-sectional basis) and **EVAL-83 (cross-asset lead-lag spillover)**; all others `NO-GO CONFIRMED (PASS)` including every traded-form monetization (EVAL-72/75/76/80/82), order-flow predictiveness (EVAL-70/78/79/81), and term-structure→vol-of-vol (EVAL-84, not portable). Traded-form taxonomy complete/all-NO-GO. Seal gates exit 0.
- **EVAL-83:** `SEALED` (`GO CONFIRMED`) at `2026-11-17T21:17:49Z`; gate exit 0; seal-gate exit 0. Bidirectional spillover BTC→ETH (skew) and ETH→BTC (atm_iv+skew), partial-over-own-surface IC>0, 7 BH-FDR rejections. No traded-form claim.
- **EVAL-84:** `SEALED` (`NO-GO CONFIRMED (PASS)`) at `2026-11-17T22:28:10Z`; prereg + COMBINED present; gate exit 0; seal-gate exit 0. Term-structure slope/ratio → forward vol-of-vol: ETH 7 pass configs / 10 BH-FDR rejections (best IC 0.3652 `term_slope::bar300::h72`) but BTC null (best IC 0.051, 0 pass) ⇒ not portable. Reuses EVAL-74 term bars/floor + EVAL-71 floor; no `src/` edits, no acquisition.
- **EVAL-67:** `NOT_DUE` (exit 10, 22:55Z); `disjoint=false`; `overlap_seconds 175274.739` (strictly decreasing toward 0); prereg present; no COMBINED/BLOCKED; `data/raw/eval67/` absent.
- **EVAL-68:** `WAIT_EVAL67` (exit 10, 22:55Z); `eval67_sealed=false`; `overlap_seconds 175274.503`; prereg present; `data/raw/eval68/` absent.
- **EVAL-69:** `WAIT_EVAL68` (exit 10, 22:55Z); `eval68_sealed=false`; `overlap_seconds 175274.020`; prereg present; acquires nothing.
- **Tests / env:** last full green driver `2026-11-17T22:06:17Z` (357/357, 27/27, 17 gates, 18 seals). This session added EVAL-84 (+18 tests/gate/seal): `pytest tests/test_eval84_term_structure_vol_of_vol_predictiveness.py tests/test_eval84_phaseb_gate.py` => **18 passed** (17.67s) with `PYTHONPATH=$PWD/.venv-deps`; `py_compile` OK on new/modified files; EVAL-84 gate `SEALED` exit 0 and seal-gate exit 0. Full `eval67_prethreshold_progress.py --execute` including EVAL-84 (375 targeted, 18 gates, 19 seals) initiated 22:29Z; **next session must run it to completion and require exit 0/readiness refresh** (driver was in progress at handoff time). `.venv-deps` + `verify_env.sh` present.
- **Hard data constraint:** earliest disjoint capture end **2026-11-19T18:08:16Z** (threshold **2026-11-20T00:00:00Z**). Do not switch to past/disjoint-retro windows.
- **Power (recorded pre-run):** EVAL-67 BTC-only underpowered (~n596, 1-sided ~0.70); EVAL-68/69 pooled at floor power-adequate (n~1856).
- **Bottlenecks:** no fixable pre-threshold bottleneck (physics wait only). Cron owns polling; the next agentic session must either run a `DUE` arbiter `--execute` or build+seal EVAL-84 — not bump this timestamp.

## BOTTLENECKS REMOVED (do not rediscover)

1. **Zombie capture bridge + liveness churn — REMOVED.** Do not recreate any bridge/waiter process; it dies with the ≤6 h job.
2. **Competing handoff pointers / timestamped copies — REMOVED.** This file is the single handoff. Do not create timestamped handoff copies or status branches.
3. **EVAL-68 "design-only" bottleneck — REMOVED.** EVAL-68 is built, tested, prereg'd, gated.
4. **EVAL-69 "no traded-form monetization campaign" bottleneck — REMOVED.** EVAL-69 is built, tested, prereg'd, gated.
5. **Forward wait — HARD PHYSICS, not a fixable inefficiency.** Free Deribit perp 1m returns ≤5001 candles (300000 s); options 5m candles return 0 at ~6–8 days back and option trades only ~24 h. All prior captures are at/after `2026-11-09T06:48:16Z`, so the only floor-compliant disjoint window is forward. Do not run a naive trailing `--days 7` capture before the threshold.
6. **Power / sample-adequacy — recorded pre-run; do not rationalize post-hoc.** See STATUS.
7. **Manual pre-threshold loop / timestamp-only carry — REMOVED.** `scripts/eval67_prethreshold_progress.py` enforces env check + 375+27 tests + all 18 arbiters + 19 seal-gates + readiness refresh in one deterministic command. A session that only bumps this timestamp has not run the driver and has not satisfied the contract.
8. **Repeated pre-threshold agent-session churn — REMOVED.** Pre-threshold state is deterministic and green; spawning more agent sessions only repeats ~4 min of unchanged tests and produces handoff churn. The external `*/5` cron owns routine pre-threshold polling. Do not launch another pre-threshold agent session; the next agentic session is triggered by the 2026-11-20T00:00:00Z threshold or a `DUE`/`FAILED` arbiter result, and it must run the full heavy-work driver with `--execute` (then build EVAL-84 if all runnable-now cells are sealed) before any other action.
9. **Stale diagnostic test assertion — REMOVED.** `tests/test_campaign_resume.py` checks current EVAL-67/68/69/70 campaigns, not retired phase numbers.
10. **Post-EVAL-7x pre-threshold heavy-work gaps — CLOSED by EVAL-70..83 (2026-11-17).** Every runnable-now physics-independent cell is now sealed: predictiveness (surface EVAL-71/73, term structure EVAL-74, cross-section EVAL-77, **cross-asset spillover EVAL-83**, order-flow EVAL-70/81/78/79), monetization across the full smile decomposition (level = straddle EVAL-72/75, slope = risk reversal EVAL-76, convexity = butterfly EVAL-82, cross-section = relative-value spread EVAL-80), and OOS stability (EVAL-73). Each was built like EVAL-82/83 (runner + SEALED/DUE/FAILED gate + tests, composed honest floor, no `src/` edits, wired into the driver so it can never be skipped). **Do NOT rebuild a collar** — under the sealed EVAL-62 mark-path framework a delta-hedged collar reduces algebraically to a sign-flipped risk reversal (already EVAL-76), so it is a re-litigation, not a new venue-form.
11. **Handoff bloat — REMOVED (2026-11-17T18:13:22Z; re-pruned 2026-11-17T20:19:40Z, 21:22:44Z).** The single handoff had been carrying ~48 (then ~12) near-identical timestamp-only SESSION LOG lines that wasted context without adding verified facts. This file is consolidated: the SESSION LOG keeps only the load-bearing recent entries. Do not reintroduce per-session timestamp-only log spam; record only new verified facts (a green driver run + a new sealed campaign + a genuine bottleneck removal).
12. **"No heavy work left pre-threshold" avoidance — REMOVED (2026-11-17T21:22:44Z, renewed 2026-11-17T22:55Z).** EVAL-84 (term-slope → forward vol-of-vol) was built+sealed this session, so EVAL-70..84 are sealed. The INITIAL TASK MESSAGE carries an explicit ANTI-AVOIDANCE RULE with prioritized EVAL-85 candidates (skew→forward return asymmetry/tail; genuinely different signal-timed VRP harvest traded-form; other on-charter cells not in EVAL-70..84) and bans re-litigating VPIN/tox→RV (EVAL-65) or collars (EVAL-76). Reusable EVAL-83/84 template (runner + gate + 2 test files + prereg + seal + driver wiring) makes the next build mechanical.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..84 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic/relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only, polite rate limiting, single acquisition process (EVAL-68 acquires BTC+ETH in ONE `eval60_acquire_three_way.py` call; EVAL-69 acquires nothing).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
- Do **not** use the retired compact task ID `INIT-2026-11-16T122919Z-...`; use the three task IDs above (EVAL-67/68/69).
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

# 2) Individual arbiters (status; add --execute to run). EVAL-70..83 are SEALED
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
  tests/test_eval84_term_structure_vol_of_vol_predictiveness.py tests/test_eval84_phaseb_gate.py
python3 -m pytest -q tests/test_controller_progress_accounting.py \
  tests/test_workflow_diagnostics_scanner.py \
  tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py

# 4) Seal gates (EVAL-66, 70..84 exit 0; EVAL-67/68/69 exit 1 until sealed). The
#    driver runs all 18 automatically; pattern for each campaign (example EVAL-83):
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-17T21:07:14Z-EVAL83-CROSS-ASSET-SURFACE-SPILLOVER-RV-PREDICTIVENESS" \
  --glob "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_PREREGISTRATION_*" \
  --require-any-glob "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_COMBINED_*" \
  --require-any-glob "EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_BLOCKED_*"

# EVAL-84 seal-gate example:
# python3 scripts/check_session_sealed.py \
#   --task-id "INIT-2026-11-17T22:20:00Z-EVAL84-TERM-STRUCTURE-VOL-OF-VOL-PREDICTIVENESS" \
#   --glob "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_PREREGISTRATION_*" \
#   --require-any-glob "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_COMBINED_*" \
#   --require-any-glob "EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_BLOCKED_*"

# 5) Phase-B only, at/after 2026-11-20T00:00:00Z (the orchestrator does this):
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, 70..84 sealed. EVAL-63 never sealed. EVAL-46..60, 62, 64, 65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`; EVAL-70: `SEALED` (`NO-GO CONFIRMED`); EVAL-71: `SEALED` (`GO CONFIRMED` — options surface IV/skew predicts forward RV on both BTC and ETH); EVAL-72: `SEALED` (`NO-GO CONFIRMED (PASS)` — straddle non-monetizable); EVAL-73: `SEALED` (`GO CONFIRMED (PASS)` — surface predictiveness stable OOS); EVAL-74: `SEALED` (`NO-GO CONFIRMED (PASS)` — term-structure slope predicts ETH RV but null on BTC); EVAL-75: `SEALED` (`NO-GO CONFIRMED (PASS)` — term-structure non-monetizable); EVAL-76: `SEALED` (`NO-GO CONFIRMED (PASS)` — risk reversal non-monetizable); EVAL-77: `SEALED` (`GO CONFIRMED` — cross-sectional basis predicts BTC-minus-ETH RV spread); EVAL-78: `SEALED` (`NO-GO CONFIRMED (PASS)` — oflow×surface null); EVAL-79: `SEALED` (`NO-GO CONFIRMED (PASS)` — oflow×cross-sectional basis null); EVAL-80: `SEALED` (`NO-GO CONFIRMED (PASS)` — relative-value spread non-monetizable); EVAL-81: `SEALED` (`NO-GO CONFIRMED (PASS)` — oflow directional return null); EVAL-82: `SEALED` (`NO-GO CONFIRMED (PASS)` — butterfly non-monetizable; traded-form taxonomy complete/all-NO-GO); EVAL-83: `SEALED` (`GO CONFIRMED` — cross-asset surface lead-lag spillover, bidirectional, partial-over-own-surface IC>0; no traded-form claim); EVAL-84: `SEALED` (`NO-GO CONFIRMED (PASS)` — term-structure slope/ratio → forward vol-of-vol not portable: ETH strong/10 BH-FDR but BTC null).

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-17T22:55:00Z (EVAL-84 built, tested, sealed NO-GO CONFIRMED PASS; driver wiring complete; handoff refreshed):** Verified arbiters before work: EVAL-67 `NOT_DUE` exit 10, EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10 (disjoint=false, overlap ~175.3k s, `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`). Ran/attempted full heavy driver `python3 scripts/eval67_prethreshold_progress.py --execute` (initial attempt timed in tool shell; relaunched in-session); no DUE/FAILED ladder arbiter to execute. Per anti-avoidance, built **EVAL-84** (priority cell: term-structure slope/ratio → forward vol-of-vol/variance, distinct target from sealed EVAL-74 slope→RV): added `scripts/eval84_term_structure_vol_of_vol_predictiveness.py`, `scripts/eval84_phaseb_gate.py`, `tests/test_eval84_term_structure_vol_of_vol_predictiveness.py`, `tests/test_eval84_phaseb_gate.py` (18 tests). Reuses EVAL-74 term-bar/floor construction (`e74._term_bars`, `e74._underlying_term_floor`) and EVAL-71/EVAL-65/EVAL-61/EVAL-62 inference/helpers; composed EVAL-71 + term-structure floor, no `src/` edits, no acquisition, no network. `py_compile` OK; `PYTHONPATH=$PWD/.venv-deps pytest tests/test_eval84_*.py` => **18 passed**. Sealed **NO-GO CONFIRMED (PASS)** at `2026-11-17T22:28:10Z` (prereg+COMBINED present; gate `SEALED` exit 0; seal-gate exit 0): floor_ok=true, 24 configs, ETH 7 pass / **10 BH-FDR rejections** (best IC 0.3652 `term_slope::bar300::h72`) but **BTC null** (best IC 0.051, 0 pass) ⇒ not portable. Patched gate `_run` to inject `.venv-deps` PYTHONPATH. Wired EVAL-84 into driver (375 targeted tests, 18 gates, 19 seals). Initiated full `eval67_prethreshold_progress.py --execute` including EVAL-84 at 22:29Z; **process still in progress at 22:55Z with readiness not yet refreshed** (last refreshed 22:06:17Z, 357-target pre-wiring). Next session: run driver first to completion (require exit 0 + readiness refresh), then execute any DUE/FAILED arbiter or build+seal `EVAL-85` if ladder remains WAIT/NOT_DUE. No sealed artifacts or `src/` modified.

- **2026-11-17T22:06:17Z (green driver run + handoff refresh, EVAL-84 mandate sharpened):** Ran `python3 scripts/eval67_prethreshold_progress.py --execute`: exit 0, `overall_ok=true`, env OK, **357/357 targeted**, **27/27 diagnostics**, all **17** gates + **18** seal specs ok; readiness refreshed at `2026-11-17T22:06:17Z`. EVAL-70..83 remain SEALED (idempotent). EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, `overlap_seconds 178203.623`, decreasing toward 0); EVAL-68 `WAIT_EVAL67` (178203.384); EVAL-69 `WAIT_EVAL68` (178202.879); `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`. No fixable pre-threshold bottleneck (forward wait is hard physics until 2026-11-20T00:00:00Z; all §BOTTLENECKS REMOVED already cleared). INITIAL TASK MESSAGE refreshed to `2026-11-17T22:06:17Z`: ANTI-AVOIDANCE RULE kept, EVAL-84 designated as the next heavy work with **priority cell (2) term-structure slope → forward vol-of-vol / variance** (genuinely distinct from sealed EVAL-74's slope→RV), explicit warning that candidate (1) VPIN→forward RV overlaps sealed EVAL-65 tox→RV NO-GO (do not re-litigate), and that collars are sign-flipped risk reversals (EVAL-76). Next session must run the driver first, then either execute any `DUE`/`FAILED` arbiter or **build+seal EVAL-84** per the EVAL-83 template wired into the driver so it can never be skipped.

- **2026-11-17T21:40:04Z (green driver run, no new campaign; handoff refreshed):** Ran `python3 scripts/eval67_phaseb_gate.py`/`eval68_phaseb_gate.py`/`eval69_phaseb_gate.py` (NOT_DUE/WAIT_EVAL67/WAIT_EVAL68, exit 10, preregs present, no captures) then full heavy driver `python3 scripts/eval67_prethreshold_progress.py --execute`: exit 0, `overall_ok=true`, env OK, **357/357 targeted**, **27/27 diagnostics**, all **17** gates + **18** seal specs ok; `research_state/EVAL_67_PREWINDOW_READINESS.json` refreshed `2026-11-17T21:40:04Z`. EVAL-70..83 remain SEALED (idempotent). EVAL-67/68/69 overlaps decreasing (179776.75 / 179776.511 / 179776.006), `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`. No fixable pre-threshold bottleneck (physics wait); external `*/5` cron owns polling. Next session must either execute any `DUE`/`FAILED` arbiter or **build+seal EVAL-84** per ANTI-AVOIDANCE RULE (no timestamp-only carry).

- **2026-11-17T21:22:44Z (EVAL-83 built, tested, sealed GO, wired; driver green):** Built **EVAL-83** — cross-asset options-surface lead-lag spillover → target forward RV predictiveness — end-to-end following the EVAL-82 template: new `scripts/eval83_cross_asset_surface_spillover_rv_predictiveness.py` runner + `scripts/eval83_phaseb_gate.py` (SEALED/DUE/FAILED) + `tests/test_eval83_cross_asset_surface_spillover_rv_predictiveness.py` (20 tests) + `tests/test_eval83_phaseb_gate.py` (8 tests). Reuses sealed EVAL-61/62/65/71 verbatim (EVAL-65 directional permutation + block bootstrap; EVAL-71 `build_surface_bars`/`_forward_rv`/`_forward_fill`/`_underlying_surface_floor`; EVAL-61 `expanding_zscore`); adds a local partial-Spearman control (residualize on target's own surface) so a GO requires *incremental* cross-asset spillover. Composes the EVAL-71 surface floor (each underlying) + a cross-asset common-bar floor (≥150 common bars/pair on the 300 s grid; actual 274); no `src/` edits, no acquisition, no network, no sealed-cell re-litigation. Sealed **GO CONFIRMED** at `2026-11-17T21:17:49Z` (prereg+COMBINED; seal-gate 0; floor_ok). Bidirectional: BTC→ETH via skew (best IC 0.2806 `skew::bar300::h24`), ETH→BTC via atm_iv+skew (best IC 0.2666 `atm_iv::bar300::h72`); every pass partial-over-own-surface IC>0; 7 BH-FDR rejections. Wired into the driver (357 targeted tests, 17 gates, 18 seal specs; `EXPECTED_TARGETED_TESTS` 329→357). Full driver `--execute` green `2026-11-17T21:22:44Z` (exit 0, env OK, 357/357 targeted, 27/27 diagnostics, all gates + seals ok, readiness refreshed). Added ANTI-AVOIDANCE RULE + EVAL-84 candidate menu so the next session cannot do a timestamp-only carry. No sealed EVAL-02..82 artifacts or `src/` touched.

- **2026-11-17T20:19:40Z (green driver run + handoff refresh, no new campaign):** Re-ran phase-B arbiters individually (20:11:10Z: EVAL-67 `NOT_DUE` exit 10, EVAL-68 `WAIT_EVAL67` exit 10, EVAL-69 `WAIT_EVAL68` exit 10, all `disjoint=false`, preregs present, capture dirs absent) then the full driver `python3 scripts/eval67_prethreshold_progress.py --execute`: exit 0, `overall_ok=true`, env OK, **329/329 targeted**, **27/27 diagnostics**, all 16 gates + 17 seal specs ok, `research_state/EVAL_67_PREWINDOW_READINESS.json` refreshed at `2026-11-17T20:19:40Z`. EVAL-70..82 remain SEALED (idempotent no-ops). EVAL-67 `NOT_DUE` (`disjoint=false`, `overlap_seconds 184601.891`, strictly decreasing toward 0; `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`). No fixable pre-threshold bottlenecks (forward wait is hard physics; single acquisition process; no capture bridge; all §BOTTLENECKS REMOVED cleared). INITIAL TASK MESSAGE + STATUS refreshed to `2026-11-17T20:19:40Z` with verified facts; redundant near-identical green-driver log entries pruned (rule #11). **Next agentic session MUST run `python3 scripts/eval67_prethreshold_progress.py --execute` first** and proceed only at/after `2026-11-20T00:00:00Z` or on any `DUE`/`FAILED` arbiter result.

- **2026-11-17T18:13:22Z (EVAL-82 built, tested, sealed, wired; handoff consolidated):** Built **EVAL-82** butterfly (smile-convexity) monetization end-to-end (runner + SEALED/DUE/FAILED gate + tests; reuses EVAL-57/61/62/71/76; composes EVAL-61/62+EVAL-71+butterfly-constructibility floor; no `src/` edits/acquisition/network). Sealed **NO-GO CONFIRMED (PASS)** at `2026-11-17T18:07:28Z` (prereg+COMBINED; seal gate 0; floor_ok; 8 configs; BTC best Sharpe -1.036 `atm_iv::bar60`, ETH best 0.713 `atm_iv::bar300`; no config passes; BH-FDR none). Wired into driver (`329 targeted`, 16 gates, 17 seal specs). Fixed wing-vs-body degeneracy found by tests. No sealed EVAL-02..81 artifacts or `src/` touched. Traded-form taxonomy complete/all-NO-GO.

- **Prior sessions (2026-11-16 → 2026-11-17T20:09:53Z, condensed):** Built/sealed EVAL-70..82 (predictiveness GOs: EVAL-71/73/77; all monetization/order-flow/other predictiveness NO-GO/BLOCKED; traded-form taxonomy complete/all-NO-GO; EVAL-83 added 21:17Z), EVAL-66 BLOCKED. EVAL-67/68/69 built/tested/prereg'd/gated, correctly NOT_DUE/WAIT with monotonically decreasing overlap; forward wait hard physics until 2026-11-20T00:00:00Z. Multiple idempotent green driver runs at 18:22→20:09Z confirmed carry; external `*/5` cron owns pre-threshold polling.

(Turn to the INITIAL TASK MESSAGE at the top for the authoritative next-session instruction; this log is context only.)