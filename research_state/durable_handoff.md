# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-17T18:21:39Z — repo priority: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow + underlying order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **VERIFIED STATE (2026-11-17T18:13:22Z):** every physics-independent runnable-now campaign **EVAL-70..82 is SEALED** and wired into `scripts/eval67_prethreshold_progress.py` (329 targeted tests, 27 diagnostics, 16 campaign arbiters, 17 seal specs). Last full heavy driver run green: `overall_ok=true`, exit 0, env OK. Phase-B arbiters re-verified: EVAL-67 `NOT_DUE` exit 10 (`disjoint=false`, `overlap_seconds 192179.448`, strictly decreasing from 192794.167; baseline 273337.532; `earliest_disjoint_capture_end 2026-11-19T18:08:16Z`), EVAL-68 `WAIT_EVAL67` exit 10 (`overlap_seconds 192179.204`), EVAL-69 `WAIT_EVAL68` exit 10 (`overlap_seconds 192178.685`). This session built, sealed and wired **EVAL-82** — the **butterfly** (smile-**convexity**) traded form, the last missing quadrant of the smile decomposition — which sealed `NO-GO CONFIRMED (PASS)`: floor_ok=true, 8 configs (BTC+ETH × {atm_iv,skew} × {60s,300s}), BTC best Sharpe **-1.036** (`atm_iv::bar60`), ETH best **0.713** (`atm_iv::bar300`), no config clears permutation+bootstrap+kill-switch, BH-FDR none. With EVAL-82 the traded-form taxonomy is now complete and all-NO-GO: **level = ATM straddle** (EVAL-72/75), **slope = risk reversal** (EVAL-76), **convexity = butterfly** (EVAL-82), **cross-section = relative-value straddle spread** (EVAL-80). **No runnable-now pre-threshold heavy work remains among physics-independent campaigns EVAL-70..82.**
>
> **FIRST ACTION, non-negotiable:** run
>
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
>
> That one command performs the full heavy-work loop: env check, the **329 targeted tests**, the **27 controller/campaign/diagnostics tests**, all **16 campaign arbiters** in ladder order (EVAL-70..82 physics-independent first, then the EVAL-67 → EVAL-68 → EVAL-69 disjoint-forward ladder), automatic `--execute` of any campaign that reports `DUE`, **17 seal-gate checks**, and an in-place refresh of `research_state/EVAL_67_PREWINDOW_READINESS.json`. **Do not exit the session until it exits 0.** If an early invocation returns `DUE` without `--execute`, rerun the same command immediately; if it returns `FAILED`, fix the reported step and rerun. **A session that only bumps this timestamp has not run the driver and has not satisfied the contract.** The driver is the mandatory heavy work of every session; a pre-threshold session that runs it and finds all-green must not degenerate into timestamp-only churn — the terminal heavy work is the disjoint-forward EVAL-67 → EVAL-68 → EVAL-69 ladder at/after 2026-11-20T00:00:00Z, which the driver executes unskippably when `DUE`.
>
> **NEXT-SESSION TRIGGER:** start only at/after **2026-11-20T00:00:00Z**, or immediately when any phase-B arbiter reports `DUE` (exit 20) or `FAILED` (exit 1). The external `*/5` cron owns routine pre-threshold polling; do **not** create another agent session merely to rerun unchanged tests or bump this timestamp.
>
> **Repo-priority reading of `Cryptocurrency-quantitative-options-orderflow-strategy`:** the thesis is *crypto OPTIONS **surface** + **options order-flow** + underlying order-flow → tradeable, net-of-cost alpha on REAL public data*. The on-charter ladder EVAL-02..66 is **CLOSED** (EVAL-66 sealed `BLOCKED`, seal-gate exit 0). Do **not** re-run, re-litigate, re-seal, or edit sealed EVAL-02..62/64..66/70..82 artifacts or `src/`. Never synthetic data, never weaken the EVAL-64 floor, paper-only.

## PHYSICS-INDEPENDENT RUNNABLE-NOW CAMPAIGNS (EVAL-70..82 — all SEALED; fill the pre-threshold heavy-work gap)

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

These thirteen are the runnable-now heavy work; they are idempotent no-ops once sealed. The forward-gated ladder below is the next genuine research heavy work (at/after `2026-11-20T00:00:00Z`).

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
- `targeted_tests: 329/329`
- `diagnostic_tests: 27/27`
- `gates`: EVAL-70..82 `SEALED`, EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68` (pre-threshold)
- `overall_ok: true`, exit code 0

If it reports `exit_code: 20`, a campaign is `DUE`: re-run with `--execute`. If it reports `exit_code: 1`, fix the reported failed step and re-run. Do not replace this loop with a timestamp-only handoff bump.

## STATUS (gates re-verified 2026-11-17T18:13:22Z; last full driver run 2026-11-17T18:13:22Z)

- **EVAL-70:** `SEALED` (`NO-GO CONFIRMED`). Prereg + COMBINED present; seal gate exit 0. Complete.
- **EVAL-71:** `SEALED` `GO CONFIRMED` (`20261117T041513Z`). Surface IV/skew predicts forward RV on both BTC (IC 0.335) and ETH (IC 0.263); EVAL-64 floor untouched.
- **EVAL-72:** `SEALED` `NO-GO CONFIRMED (PASS)` (`20261117T051822Z`). Predictive surface does not monetize via a signal-timed ATM straddle.
- **EVAL-73:** `SEALED` `GO CONFIRMED (PASS)` (`20261117T053237Z`). EVAL-71's surface predictiveness is stable across a disjoint OOS split.
- **EVAL-74:** `SEALED` `NO-GO CONFIRMED (PASS)` (`20261117T063904Z`). Term-structure slope predicts ETH forward RV (8 BH-FDR) but null on BTC.
- **EVAL-75:** `SEALED` `NO-GO CONFIRMED (PASS)` (`20261117T095628Z`). EVAL-74's term-structure signal does not monetize via an ATM straddle.
- **EVAL-76:** `SEALED` `NO-GO CONFIRMED (PASS)` (`20261117T101715Z`). EVAL-71's skew does not monetize via a risk reversal.
- **EVAL-77:** `SEALED` `GO CONFIRMED` (`20261117T105939Z`). Cross-sectional BTC-vs-ETH basis predicts the BTC-minus-ETH RV spread (best IC 0.2972; 6/12 configs; BH-FDR 7).
- **EVAL-78:** `SEALED` `NO-GO CONFIRMED (PASS)` (`20261117T120846Z`). Options order-flow × surface interaction adds no portable forward-RV predictiveness.
- **EVAL-79:** `SEALED` `NO-GO CONFIRMED (PASS)` (`20261117T123244Z`). Options order-flow × cross-sectional basis adds no portable forward-RV predictiveness.
- **EVAL-80:** `SEALED` `NO-GO CONFIRMED (PASS)` (`20261117T134447Z`). EVAL-77's cross-sectional basis does not monetize via a two-leg relative-value straddle spread.
- **EVAL-81:** `SEALED` `NO-GO CONFIRMED (PASS)` (`20261117T143107Z`). Options order-flow imbalance does not predict the subsequent direction of the underlying.
- **EVAL-82:** `SEALED` `NO-GO CONFIRMED (PASS)` (`20261117T180728Z`). The EVAL-71 surface (same {atm_iv, skew} set as EVAL-72) does not monetize via a four-leg **butterfly** (smile convexity): BTC best Sharpe -1.036, ETH best 0.713; no config clears permutation + bootstrap + kill-switch; BH-FDR none. Completes the all-NO-GO traded-form taxonomy. Seal gate exit 0; floor_ok=true.
- **EVAL-67:** `NOT_DUE` (gate exit 10) at 2026-11-17T18:13:22Z; `disjoint = false`; `overlap_seconds 192179.448` (strictly decreasing from 192794.167; baseline 273337.532). Prereg `EVAL_67_BTC_OFLOW_TOX_RV_OOS_PREREGISTRATION_20261116T132805Z.{json,md}` present; no `COMBINED_*`/`BLOCKED_*`; `data/raw/eval67/` absent.
- **EVAL-68:** `WAIT_EVAL67` (gate exit 10); `eval67_sealed = false`; `overlap_seconds 192179.204`. Prereg present; `data/raw/eval68/` absent. Acquires only after EVAL-67 seals.
- **EVAL-69:** `WAIT_EVAL68` (gate exit 10); `eval68_sealed = false`; `overlap_seconds 192178.685`. Prereg present; acquires nothing.
- **Tests / env:** last full verified heavy driver run **2026-11-17T18:13:22Z** — **329/329 targeted**, **27/27 diagnostics**, `overall_ok=true`, exit 0; all **16** campaign arbiters and **17** seal specs correct. This session built/sealed/wired **EVAL-82** and re-ran the full driver: EVAL-70..82 `SEALED`, EVAL-67 `NOT_DUE`, EVAL-68 `WAIT_EVAL67`, EVAL-69 `WAIT_EVAL68`; seal gates EVAL-66/70/71/72/73/74/75/76/77/78/79/80/81/82 exit 0; EVAL-67/68/69 exit 1 (expected).
- **Data-availability constraint (hard):** earliest disjoint floor-compliant forward capture end = **2026-11-19T18:08:16Z** (prereg threshold **2026-11-20T00:00:00Z**). Past windows are non-viable because options retention is < 6 days and option trades only ~24 h.
- **Power expectation (recorded pre-run):** EVAL-67 is underpowered for the EVAL-65 BTC effect (IC 0.088, n 596): one-sided ≈0.70, conjunction ≈0.53, ~790 pairs for 80%. EVAL-68 pooled at the EVAL-64 floor is power-adequate (n ≈1856 ≫ 790). EVAL-69 inherits the same pooled adequacy.
- **Durable mechanism:** git-committed handoff + git-committed readiness JSON + external `*/5` cron + `scripts/eval67_prethreshold_progress.py` (16 arbiters, 17 seal specs). The next **agentic** session is threshold/alert-triggered; cron alone handles pre-threshold polling. No bridges.

## BOTTLENECKS REMOVED (do not rediscover)

1. **Zombie capture bridge + liveness churn — REMOVED.** Do not recreate any bridge/waiter process; it dies with the ≤6 h job.
2. **Competing handoff pointers / timestamped copies — REMOVED.** This file is the single handoff. Do not create timestamped handoff copies or status branches.
3. **EVAL-68 "design-only" bottleneck — REMOVED.** EVAL-68 is built, tested, prereg'd, gated.
4. **EVAL-69 "no traded-form monetization campaign" bottleneck — REMOVED.** EVAL-69 is built, tested, prereg'd, gated.
5. **Forward wait — HARD PHYSICS, not a fixable inefficiency.** Free Deribit perp 1m returns ≤5001 candles (300000 s); options 5m candles return 0 at ~6–8 days back and option trades only ~24 h. All prior captures are at/after `2026-11-09T06:48:16Z`, so the only floor-compliant disjoint window is forward. Do not run a naive trailing `--days 7` capture before the threshold.
6. **Power / sample-adequacy — recorded pre-run; do not rationalize post-hoc.** See STATUS.
7. **Manual pre-threshold loop / timestamp-only carry — REMOVED.** `scripts/eval67_prethreshold_progress.py` enforces env check + 329+27 tests + all 16 arbiters + 17 seal-gates + readiness refresh in one deterministic command. A session that only bumps this timestamp has not run the driver and has not satisfied the contract.
8. **Repeated pre-threshold agent-session churn — REMOVED.** Pre-threshold state is deterministic and green; spawning more agent sessions only repeats ~190 s of unchanged tests and produces handoff churn. The external `*/5` cron owns routine pre-threshold polling. Do not launch another pre-threshold agent session; the next agentic session is triggered by the 2026-11-20T00:00:00Z threshold or a `DUE`/`FAILED` arbiter result, and it must run the full heavy-work driver with `--execute` before any other action.
9. **Stale diagnostic test assertion — REMOVED.** `tests/test_campaign_resume.py` checks current EVAL-67/68/69/70 campaigns, not retired phase numbers.
10. **Post-EVAL-7x pre-threshold heavy-work gaps — CLOSED by EVAL-70..82 (2026-11-17).** Every runnable-now physics-independent cell is now sealed: predictiveness (surface EVAL-71/73, term structure EVAL-74, cross-section EVAL-77, order-flow EVAL-70/81/78/79), monetization across the full smile decomposition (level = straddle EVAL-72/75, slope = risk reversal EVAL-76, convexity = butterfly EVAL-82, cross-section = relative-value spread EVAL-80), and OOS stability (EVAL-73). Each was built like EVAL-82 (runner + SEALED/DUE/FAILED gate + tests, composed honest floor, no `src/` edits, wired into the driver so it can never be skipped). **Do NOT rebuild a collar** — under the sealed EVAL-62 mark-path framework a delta-hedged collar reduces algebraically to a sign-flipped risk reversal (already EVAL-76), so it is a re-litigation, not a new venue-form.
11. **Handoff bloat — REMOVED (2026-11-17T18:13:22Z).** The single handoff was carrying ~48 near-identical timestamp-only SESSION LOG lines that wasted context without adding verified facts. This file is consolidated: the SESSION LOG now keeps only the load-bearing recent entries plus a one-line prior-session summary. Do not reintroduce per-session timestamp-only log spam; record only new verified facts (a green driver run + a new sealed campaign + a genuine bottleneck removal).

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal/edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..82 artifacts or `src/`. Append-only for new authorized work.
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

# 2) Individual arbiters (status; add --execute to run). EVAL-70..82 are SEALED
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
  tests/test_eval82_surface_skew_butterfly_monetization.py tests/test_eval82_phaseb_gate.py
python3 -m pytest -q tests/test_controller_progress_accounting.py \
  tests/test_workflow_diagnostics_scanner.py \
  tests/test_nonfinite_result_serialization.py tests/test_campaign_resume.py

# 4) Seal gates (EVAL-66, 70..82 exit 0; EVAL-67/68/69 exit 1 until sealed). The
#    driver runs all 17 automatically; pattern for each campaign (example EVAL-82):
python3 scripts/check_session_sealed.py \
  --task-id "INIT-2026-11-17T18:00:00Z-EVAL82-SURFACE-SKEW-BUTTERFLY-MONETIZATION" \
  --glob "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_PREREGISTRATION_*" \
  --require-any-glob "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_COMBINED_*" \
  --require-any-glob "EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_BLOCKED_*"

# 5) Phase-B only, at/after 2026-11-20T00:00:00Z (the orchestrator does this):
python3 scripts/eval67_phaseb_gate.py --execute
python3 scripts/eval68_phaseb_gate.py --execute
python3 scripts/eval69_phaseb_gate.py --execute
```

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, 70..82 sealed. EVAL-63 never sealed. EVAL-46..60, 62, 64, 65: `NO-GO CONFIRMED (PASS)`; EVAL-61: `NO-GO` (artifact); EVAL-66: `BLOCKED`; EVAL-70: `SEALED` (`NO-GO CONFIRMED`); EVAL-71: `SEALED` (`GO CONFIRMED` — options surface IV/skew predicts forward RV on both BTC and ETH; first GO in the predictiveness line); EVAL-72: `SEALED` (`NO-GO CONFIRMED (PASS)` — the surface signal does not monetize net-of-cost via a signal-timed ATM straddle); EVAL-73: `SEALED` (`GO CONFIRMED (PASS)` — EVAL-71's surface predictiveness is stable across a disjoint OOS split); EVAL-74: `SEALED` (`NO-GO CONFIRMED (PASS)` — term-structure slope predicts ETH forward RV but is null on BTC); EVAL-75: `SEALED` (`NO-GO CONFIRMED (PASS)` — EVAL-74's term-structure signal does not monetize via an ATM straddle); EVAL-76: `SEALED` (`NO-GO CONFIRMED (PASS)` — EVAL-71's skew does not monetize via a risk reversal); EVAL-77: `SEALED` (`GO CONFIRMED` — cross-sectional basis predicts the BTC-minus-ETH RV spread; first cross-sectional GO); EVAL-78: `SEALED` (`NO-GO CONFIRMED (PASS)` — options order-flow × surface adds no portable forward-RV predictiveness); EVAL-79: `SEALED` (`NO-GO CONFIRMED (PASS)` — options order-flow × cross-sectional basis adds no portable forward-RV predictiveness); EVAL-80: `SEALED` (`NO-GO CONFIRMED (PASS)` — EVAL-77's cross-sectional basis does not monetize via a two-leg relative-value straddle spread); EVAL-81: `SEALED` (`NO-GO CONFIRMED (PASS)` — options order-flow imbalance does not predict the subsequent direction of the underlying); EVAL-82: `SEALED` (`NO-GO CONFIRMED (PASS)` — the surface does not monetize net-of-cost via a four-leg butterfly / smile convexity; completes the all-NO-GO traded-form taxonomy).

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-17T18:13:22Z (this session — NEW campaign built, tested, sealed, and wired; handoff consolidated):** Built **EVAL-82** end-to-end to close the last missing quadrant of the smile decomposition — the **butterfly** (smile-**convexity**) traded form — using the *same* EVAL-72 surface signal set {atm_iv, skew} and the *same* correct EVAL-62 mark-path net-of-cost P&L, changing only the traded structure (four-leg butterfly: long OTM call wing + long OTM put wing, short ATM body). Files: `scripts/eval82_surface_skew_butterfly_monetization.py` (reuses EVAL-57/61/62/71/76 verbatim; composes the EVAL-61/62 traded floor + EVAL-71 surface floor + a butterfly-constructibility floor ≥200 states/underlying, none weakened; no `src/` edits, no acquisition, no network), `scripts/eval82_phaseb_gate.py` (SEALED/DUE/FAILED arbiter; TASK_ID `INIT-2026-11-17T18:00:00Z-EVAL82-SURFACE-SKEW-BUTTERFLY-MONETIZATION`), and `tests/test_eval82_surface_skew_butterfly_monetization.py` + `tests/test_eval82_phaseb_gate.py` (22 tests, all green). Sealed **NO-GO CONFIRMED (PASS)** at `2026-11-17T18:07:28Z` (prereg + COMBINED `EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_{PREREGISTRATION,COMBINED}_20261117T180728Z.{json,md}`; seal gate exit 0; floor_ok=true; 8 configs; BTC best Sharpe -1.036 `atm_iv::bar60`, ETH best 0.713 `atm_iv::bar300`; no config passes; BH-FDR none). Wired into `scripts/eval67_prethreshold_progress.py` (`EXPECTED_TARGETED_TESTS=329`, gate spec, seal spec, readiness notes/gates; docstring updated to EVAL-70..82). Ran the full driver `python3 scripts/eval67_prethreshold_progress.py --execute` from scratch: **exit 0**, `overall_ok=true`, `env_check=true`, **329/329 targeted**, **27/27 diagnostics**, all **16** gates correct (EVAL-70..82 `SEALED` exit 0; EVAL-67 `NOT_DUE` exit 10 `overlap_seconds 192179.448` strictly decreasing from 192794.167; EVAL-68 `WAIT_EVAL67` exit 10; EVAL-69 `WAIT_EVAL68` exit 10), all **17** seal gates expected (EVAL-66/70..82 exit 0; EVAL-67/68/69 exit 1, all `ok=true`), readiness JSON refreshed in place. Fixed a real butterfly-wing degeneracy found by the tests (wings are now picked relative to the body strike K, not spot, so the OTM put wing can never coincide with the body put). Consolidated this handoff's bloated ~48-line timestamp-only SESSION LOG. No sealed EVAL-02..81 artifacts or `src/` touched; no synthetic data; paper-only; no capture bridges spawned.

- **Prior sessions (2026-11-16 → 2026-11-17T14:31:07Z, condensed):** Built and sealed EVAL-70 (perp order-flow → RV/signed return, NO-GO) through EVAL-81 (options order-flow → direction, NO-GO), each with a SEALED/DUE/FAILED gate + tests + composed honest floor + driver wiring, interleaved with green full-driver runs. EVAL-71/73/77 were the only GOs (options surface level/skew → RV; disjoint OOS stability; cross-sectional BTC-vs-ETH basis → RV spread); every monetization rung (EVAL-72/75/76/80/82) sealed NO-GO, and every order-flow rung (EVAL-65/67/68/69/70/78/79/81) sealed NO-GO/BLOCKED. EVAL-66 sealed BLOCKED. EVAL-67/68/69 are built, tested, prereg'd, gated, and correctly carrying NOT_DUE/WAIT_EVAL67/WAIT_EVAL68 with strictly decreasing overlap; the forward wait is hard physics until 2026-11-20T00:00:00Z. No fixable bottlenecks remained at that point; the external `*/5` cron owns pre-threshold polling.

(Turn to the INITIAL TASK MESSAGE at the top for the authoritative next-session instruction; this log is context only.)