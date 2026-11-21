# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-21T08:00:00Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** `...options...orderflow...strategy` ⇒ two load-bearing signal halves (options **surface** + options **order-flow**) feeding one deliverable (a **tradeable, net-of-cost strategy**). The **options order-flow half is the highest charter-relevance rung** and is the mandated line. Its **distributional-moment sweep is now COMPLETE**: signed-return mean (EVAL-149/150/151/152), skewness (153/154), downside-semivariance share (155/156), kurtosis (157/158), forward realized return variance (159 toxicity, 160 imbalance). **All order-flow cells are NO-GO CONFIRMED (PASS)** — the order-flow line is uniformly NO-GO as a standalone predictor across every moment. The surviving directional alpha is entirely on the **surface** line (EVAL-101/102/104 GO CONFIRMED, IC 0.26–0.41). **The next focus campaign is the charter's actual "strategy" deliverable: a traded-form, net-of-cost evaluation of the strongest surviving GO surface anchor (EVAL-104 `term_slope`→forward signed return), fallbacks EVAL-102 `term_ratio`, EVAL-101 `atm_iv`), paper-only, converting predictiveness into net-of-cost viability. Constraint: do NOT re-litigate the already-sealed traded-form cells (EVAL-72/75/76/80/82/124/135/137/142 — all NO-GO/BLOCKED); design a genuinely distinct, non-overlapping cell. This is the anti-avoidance backstop: after the moment sweep there is still a clearly charter-relevant, unsealed campaign to build.**
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver and require exit 0 (idempotent no-op on every sealed rung):
>   ```bash
>   python3 scripts/eval67_prethreshold_progress.py --execute
>   ```
>   Require: `targeted_tests: 2015/2015`, `diagnostic_tests: 27/27`, all `EVAL-70..160` gates `SEALED`/`ok`, `EVAL-67/68/69` `SEALED` (forward disjoint-window threshold `2026-11-20T00:00:00Z` PASSED), every `GATE_SPEC` classified ok + every `SEAL_SPEC` ok, `failures: []`, `gate_phase: SEALED`, `gate_exit=0`.

## POST-SWEEP FOCUS CAMPAIGN (starts now — do not re-derive)

The order-flow distributional-moment sweep is **complete** (mean, variance, skewness, kurtosis, downside-semivariance share — for BOTH the toxicity and imbalance signals). The order-flow line is uniformly **NO-GO** as a standalone predictor across every moment; the surviving directional alpha is entirely on the **surface** line (EVAL-101/102/104 GO CONFIRMED, IC 0.26–0.41). The next focus campaign is therefore the charter's actual **"strategy"** deliverable: a **traded-form, net-of-cost** evaluation of the strongest surviving GO surface anchor (**EVAL-104 `term_slope`→forward signed return**, fallbacks EVAL-102 `term_ratio`, EVAL-101 `atm_iv`), paper-only, converting predictiveness into net-of-cost viability. **Constraint:** do NOT re-litigate the already-sealed traded-form cells (EVAL-72/75/76/80/82/124/135/137/142 — all NO-GO/BLOCKED); design a genuinely distinct, non-overlapping cell. This is the anti-avoidance backstop: after the moment sweep there is still a clearly charter-relevant, unsealed campaign to build.

## VERIFIED STATE (2026-11-21T07:59:49Z, this session — driver re-run exit 0)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2015`, `EXPECTED_DIAGNOSTIC_TESTS=27` (see `scripts/eval67_prethreshold_progress.py`). All `EVAL-70..160` `SEALED`/`ok`; `EVAL-67/68/69` `SEALED` (forward disjoint-window ladder complete; disjoint-window threshold `2026-11-20T00:00:00Z` PASSED). Readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json` (`updated_at: 2026-11-21T07:59:49Z`; `tests_passed=2015`, `diagnostics_passed=27`, `total_tests_passed=2042`, `gate_exit=0`, `gate_phase=SEALED`). `research_state/durable_handoff.md` remains the only authoritative build queue.

- **NEW VERIFIED FACTS (this session):** (a) EVAL-157 (cross-asset toxicity → forward realized return kurtosis) sealed `NO-GO CONFIRMED (PASS)` at `20261121T054648Z`; (b) EVAL-158 (cross-asset imbalance → forward realized return kurtosis) sealed `NO-GO CONFIRMED (PASS)` at `20261121T060009Z`; (c) **EVAL-159 (cross-asset toxicity → forward realized return VARIANCE) sealed `NO-GO CONFIRMED (PASS)` at `20261121T065641Z`**; (d) **EVAL-160 (cross-asset imbalance → forward realized return VARIANCE) built + wired + sealed `NO-GO CONFIRMED (PASS)` at `20261121T075913Z`** (ETH→BTC best IC, 0 pass; BTC→ETH best IC, 0 pass; BH-FDR rejected `[]`); (e) driver advanced from `1996`-expectation to a green `2015/2015` run with EVAL-160 wired into `TARGETED_TEST_FILES`, `GATE_SPECS`, `SEAL_SPECS` (+2/+1/+1 respectively) and `EXPECTED_TARGETED_TESTS` bumped 1996→2015; EVAL-159 `expected_exit` flipped 1→0. **No unsealed pre-threshold campaign rung remains.** The order-flow moment sweep is complete; the programme now pivots to the surface-line strategy pivot above.

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | **CLOSED** (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67, EVAL-68, EVAL-69 | **SEALED** (`20261120T005220Z`, `20261120T014819Z`, `20261120T015619Z`); 68/69 `BLOCKED` kind |
| Physics-independent predictiveness EVAL-70..147 | 78 rungs | **SEALED** |
| Traded-form net-of-cost | EVAL-72/75, 76, 80, 82, 124/135, 137, 142 | all `NO-GO`/`BLOCKED` |
| Cross-asset surface/term spillover → forward signed return mean | EVAL-148 (atm_iv/skew/term_slope/term_ratio) | **SEALED COMPLETE** (4 cells, `010725Z`..`010827Z`) |
| Cross-asset options order-flow → forward signed return mean | EVAL-149 (imbalance), 150 (imbalance×atm_iv), 151 (toxicity×atm_iv), 152 (toxicity alone) | **SEALED COMPLETE** (`010848Z`..`025341Z`) |
| Cross-asset options order-flow → forward skewness | EVAL-153 (toxicity), 154 (imbalance) | **SEALED COMPLETE** (`025645Z`, `031533Z`) |
| Cross-asset options order-flow → forward downside-semivariance share | EVAL-155 (toxicity), 156 (imbalance) | **SEALED COMPLETE** (`042021Z`, `044145Z`) |
| Cross-asset options order-flow → forward realized return kurtosis | EVAL-157 (toxicity), 158 (imbalance) | **SEALED COMPLETE** (`054648Z`, `060009Z`) |
| Cross-asset options order-flow → forward realized return variance | EVAL-159 (toxicity), 160 (imbalance) | **SEALED COMPLETE** (`065641Z`, `075913Z`); order-flow moment sweep DONE |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — next: surface-line strategy pivot (EVAL-104 `term_slope` → forward signed return, traded-form net-of-cost)

The order-flow distributional sweep is complete and uniformly NO-GO. The next unsealed campaign is the charter's actual strategy deliverable: **traded-form, net-of-cost evaluation of EVAL-104 `term_slope`→forward signed return** (BTC IC 0.4058 / ETH IC 0.2600), fallbacks EVAL-102 `term_ratio` (BTC 0.3926 / ETH 0.2559) and EVAL-101 `atm_iv` (BTC 0.2313 / ETH 0.3442). Design a genuinely distinct, non-overlapping traded-form cell — do NOT re-litigate EVAL-72/75/76/80/82/124/135/137/142 (all sealed NO-GO/BLOCKED). Paper-only; real data only; never weaken EVAL-64.

Already covered — do **not** rebuild: EVAL-77, 88..160. Do not re-test `atm_iv`→VRP (mechanical overlap), do not re-test `term_ratio`→VRP, do not rebuild the collar (EVAL-76), do not re-run EVAL-144..160 as a substitute for new work, do not re-litigate sealed cells, do not weaken EVAL-64, do not touch `src/`.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) complete. EVAL-70..160 gates: `SEALED`(0) idempotent no-op; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- EVAL-137/142: `SEALED`(0) complete (BLOCKED). EVAL-138/139: `SEALED`(0) complete (GO CONFIRMED). EVAL-140/141/144/145/146/147/148/149/150/151/152/153/154/155/156/157/158/159/160: `SEALED`(0) complete (NO-GO). EVAL-143: `SEALED`(0) complete (verdict per run). Idempotent no-ops; do not re-run.
- Green driver = env OK, `2015/2015` targeted, `27/27` diagnostics, all `EVAL-70..160` gates `SEALED`/`ok`, `EVAL-67/68/69` `SEALED`, every `GATE_SPEC` ok + every `SEAL_SPEC` ok, `failures: []`, `gate_phase: SEALED`, `gate_exit=0`.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling. No capture bridges/waiters.
2. Competing handoff pointers/copies — removed; this file is the single handoff (do not create copies or edit `AGENTS.md` into a competing queue).
3. Pre-threshold "no heavy work left" avoidance — removed; the queue above always has a next rung (order-flow sweep → surface strategy pivot). An explicit "POST-SWEEP FOCUS CAMPAIGN" section makes the next build unambiguous.
4. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
5. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity (EVAL-159 flipped this session).
6. Stale-handoff / timestamp-refresh treadmill — the 06:57 handoff pointed at "build EVAL-160" while EVAL-160 is now sealed (`075913Z`). Fixed: this handoff reflects the true sealed state and points at the genuinely-next unsealed campaign: the surface-line strategy pivot. Do not refresh the timestamp without new verified facts (green driver + green tests + green gates).
7. Task-floor-stamp ordering bug — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
8. Degenerate skew/kurtosis/variance fixture trap — alternating ±drift yields an all-zero third/fourth/second moment; skewness/kurtosis/variance fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
9. Half-wired driver: a new rung's test files added to `TARGETED_TEST_FILES` without adding the rung to `GATE_SPECS`/`SEAL_SPECS` and without bumping `EXPECTED_TARGETED_TESTS`, so the driver fails the count check. Always reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green.
10. Signal/target (and hyphenated `TERM-RATIO`) copy-paste bugs in a cloned runner/gate/tests — always grep the new files for stale ids, hyphenated task labels, signal/target names AND stale helper references before sealing.
11. Composite/both-asset GO bar — GO requires BOTH BTC and ETH to have ≥1 BH-FDR-rejected passing config; a single-asset pass is a legitimate `NO-GO CONFIRMED (PASS)`; do not relax the bar.
12. Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via EVAL-71 `build_surface_bars`; `term_slope`/`term_ratio` via EVAL-74 `_term_bars`; order-flow imbalance/toxicity via EVAL-62 `build_states`. Do not cross them.
13. No-hyphen / underscore / hyphenated `EVAL159` / `EVAL_159` / `EVAL-159` task-label traps when cloning — a single bulk replace of one form does NOT catch the others; grep for ALL THREE forms before sealing.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..160 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-68 acquires BTC+ETH in ONE process; EVAL-69/143/145/146/147/149/150/151/152/153/154/155/156/157/158/159/160 acquire nothing (consume on-disk `data/raw/eval61`).
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

# 1) Full heavy-work loop; run every session (idempotent). EVAL-70..160 SEALED; no-op on re-run:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) Verify a sealed campaign idempotently:
python3 scripts/eval160_phaseb_gate.py

# 3) Next: build the surface-line strategy pivot (traded-form net-of-cost on EVAL-104 term_slope -> forward signed return), paper-only, non-overlapping with sealed traded-form cells.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself); a bare `python3 scripts/eval1xx_*.py` fails on `numpy` without it.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..69, 70..160 sealed. EVAL-63 never sealed. Predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`), 88, 90, 91, 93, 97, 99, 100, 101, 102, 104, 109, 111, 112, 113, 114, 116, 120, 122, 125, 138, 139 (`GO CONFIRMED`). NO-GO CONFIRMED (PASS): EVAL-70, 72, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103, 105, 106, 107, 108, 110, 115, 117, 118, 119, 121, 123, 126, 127, 128, 129, 130, 131, 133, 134, 136, 140, 141, 144, 145, 146, 147, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160. BLOCKED: EVAL-124, EVAL-135, EVAL-137, EVAL-142. EVAL-67/68/69 SEALED (forward ladder complete). EVAL-148 (4 cells) SEALED. EVAL-149 SEALED. Strongest surviving GO IC anchors unchanged: EVAL-101 `atm_iv`→signed return (BTC 0.2313 / ETH 0.3442); EVAL-102 `term_ratio`→signed return (BTC 0.3926 / ETH 0.2559); EVAL-104 `term_slope`→signed return (BTC 0.4058 / ETH 0.2600); EVAL-114 `atm_iv` spillover→return skewness (BTC 0.4039 / ETH 0.1173); EVAL-122 `term_slope` spillover→return skewness (BTC 0.3817 / ETH 0.4643); EVAL-125 `term_ratio` basis→return-kurtosis spread (IC 0.4128); EVAL-138 `term_ratio` spillover→return kurtosis (BTC 0.2931 / ETH 0.4679); EVAL-139 `term_ratio` spillover→return skewness (BTC 0.2613 / ETH 0.4878, 7 BH-FDR). Order-flow NO-GO anchors (all fail the both-asset GO bar): EVAL-152 toxicity→signed-return (BTC 0.1878, 1 pass; ETH 0.0969, 0); EVAL-153 toxicity→skewness (BTC 0.2180, 2; ETH 0.0598, 0); EVAL-154 imbalance→skewness (BTC 0.0573, 0; ETH 0.0887, 0); EVAL-157 toxicity→kurtosis (ETH→BTC 0.1004, 0; BTC→ETH 0.0927, 0); EVAL-158 imbalance→kurtosis (ETH→BTC 0.1774, 1; BTC→ETH 0.0784, 0); EVAL-159 toxicity→variance (ETH→BTC 0.1412, 0; BTC→ETH 0.1019, 0); EVAL-160 imbalance→variance (NO-GO CONFIRMED).

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-21T01:22:25Z:** EVAL-148 (4 cells) + EVAL-149 sealed; driver green 1809/1809+27/27. (Prior session.)
- **2026-11-21T02:18:18Z:** Prior (interrupted) session built EVAL-150/151/152 runners+gates+tests and sealed EVAL-150 (`015450Z`) + EVAL-151 (`020925Z`), wired 150/151 into the driver, but left EVAL-152 unsealed/unwired and set `EXPECTED_TARGETED_TESTS=1845` (actual 1863) — driver left broken; handoff not updated.
- **2026-11-21T03:03:13Z:** Sealed EVAL-152 (`NO-GO`, `025341Z`); wired 152; corrected count 1845→1863; built+wired+sealed EVAL-153 (`NO-GO`, `025645Z`); corrected 1863→1882; driver green 1882/1882+27/27.
- **2026-11-21T03:21:16Z:** Built+wired+sealed EVAL-154 (imbalance→skewness, `NO-GO`, `031533Z`); corrected 1882→1901; driver green 1901/1901+27/27.
- **2026-11-21T04:20:21Z:** Built+wired+sealed EVAL-155 (toxicity→downside-semivariance share, `NO-GO`, `042021Z`); corrected 1901→1920; driver green 1920/1920+27/27.
- **2026-11-21T04:42:15Z:** Built+wired+sealed EVAL-156 (imbalance→downside-semivariance share, `NO-GO`, `044145Z`); corrected 1920→1939; driver green 1939/1939+27/27.
- **2026-11-21T04:55:37Z / 05:37:36Z:** Handoff refreshed (timestamp only); next builds EVAL-157→158.
- **2026-11-21T05:46:48Z:** EVAL-157 (toxicity→forward return kurtosis) sealed `NO-GO CONFIRMED (PASS)` (ETH→BTC 0.1004/0; BTC→ETH 0.0927/0).
- **2026-11-21T06:00:09Z:** EVAL-158 (imbalance→forward return kurtosis) sealed `NO-GO CONFIRMED (PASS)` (ETH→BTC 0.1774, 1 pass; BTC→ETH 0.0784, 0).
- **2026-11-21T06:57:54Z:** Bottlenecks removed + heavy work continued. Built + wired + sealed EVAL-159 (cross-asset toxicity → forward realized return variance, `NO-GO CONFIRMED (PASS)`, `20261121T065641Z`). Driver green 1996/1996+27/27, exit 0. Next mandated build: EVAL-160.
- **2026-11-21T07:59:49Z:** **EVAL-160 built + wired + sealed `NO-GO CONFIRMED (PASS)` (`20261121T075913Z`).** Order-flow moment sweep COMPLETE (mean, variance, skewness, kurtosis, downside-semivariance share — both signals, all NO-GO). Driver green **2015/2015 targeted + 27/27 diagnostics, exit 0**. EVAL-159 `expected_exit` flipped 1→0. EVAL-160 wired into driver (`TARGETED_TEST_FILES` +2, `GATE_SPECS` +1, `SEAL_SPECS` +1), `EXPECTED_TARGETED_TESTS` 1996→2015. No sealed artifact or `src/` modified. **Next focus campaign: surface-line traded-form net-of-cost strategy pivot on EVAL-104 `term_slope`→forward signed return (fallbacks EVAL-102 `term_ratio`, EVAL-101 `atm_iv`), paper-only, non-overlapping with sealed traded-form cells.** Build this campaign in the next session.
