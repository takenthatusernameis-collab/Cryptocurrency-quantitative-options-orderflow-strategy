# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-21T06:57:54Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** `...options...orderflow...strategy` ⇒ two load-bearing signal halves (options **surface** + options **order-flow**) feeding one deliverable (a **tradeable, net-of-cost strategy**). The **options order-flow half is the highest charter-relevance rung** and is the mandated line. Its **distributional-moment sweep is one cell from complete**: signed-return mean (EVAL-149/150/151/152), skewness (153/154), downside-semivariance share (155/156), kurtosis (157/158) and — sealed THIS session — toxicity → forward realized return **variance** (EVAL-159). The **last remaining order-flow distributional cell is imbalance → forward realized return variance (EVAL-160)**. After EVAL-160 seals, the order-flow signal has a complete distributional characterization (mean, variance, skewness, kurtosis, downside-semivariance share) and the programme **pivots to the charter's actual deliverable**: a traded-form, net-of-cost strategy on the strongest *surviving GO* anchor — the **surface** line (EVAL-104 `term_slope`→signed return IC 0.4058 BTC / 0.2600 ETH; fallbacks EVAL-102 `term_ratio`, EVAL-101 `atm_iv`) — NOT more order-flow predictiveness (the order-flow line is uniformly NO-GO).
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver and require exit 0 (idempotent no-op on every sealed rung):
>   ```bash
>   python3 scripts/eval67_prethreshold_progress.py --execute
>   ```
>   Require: `targeted_tests: 1996/1996`, `diagnostic_tests: 27/27`, all `EVAL-70..159` gates `SEALED`/`ok`, `EVAL-67/68/69` `SEALED` (forward disjoint-window threshold `2026-11-20T00:00:00Z` PASSED), every `GATE_SPEC` classified ok + every `SEAL_SPEC` ok, `failures: []`, `gate_phase: SEALED`, `gate_exit=0`.
>
> **SECOND ACTION (anti-avoidance — a green driver + all-sealed is NOT completion):** build + wire + seal the next order-flow rung **EVAL-160** in THIS session (full recipe below), then leave the post-sweep strategy pivot queued. Do **not** stop at "everything is sealed". EVAL-160 is UNBUILT and un-wired; a green driver at `1996/1996` with all `EVAL-70..159` sealed means only that the *sealed* backlog is clean — it does NOT mean the order-flow distributional sweep is finished (imbalance→variance is missing) and it does NOT mean the charter's strategy deliverable exists.

## EVAL-160 BUILD RECIPE (exact, low-friction — follow precisely)

EVAL-160 = **cross-asset options order-flow IMBALANCE spillover → forward realized return VARIANCE**. It is a *pure clone of EVAL-159 with only the signal swapped* — exactly the EVAL-157→EVAL-158 delta (`tox_signal="tox"`→`"imbalance"`, `SURFACE_SIGNAL "toxicity"`→`"imbalance"`). The variance target helper (`_forward_return_variance`, the symmetric `m2` second central moment) is carried over unchanged.

1. **Clone template:** copy `scripts/eval159_cross_asset_orderflow_toxicity_spillover_forward_return_variance.py` → `scripts/eval160_cross_asset_orderflow_imbalance_spillover_forward_return_variance.py`, `scripts/eval159_phaseb_gate.py` → `scripts/eval160_phaseb_gate.py`, `tests/test_eval159_cross_asset_orderflow_toxicity_spillover_forward_return_variance.py` → `tests/test_eval160_cross_asset_orderflow_imbalance_spillover_forward_return_variance.py`, `tests/test_eval159_phaseb_gate.py` → `tests/test_eval160_phaseb_gate.py`.
2. **Swap the signal (ONLY semantic change — do NOT touch the variance target):**
   - In the runner change **all** `tox_signal="tox"` → `tox_signal="imbalance"` (in `build_cross_section`, `_underlying_oflow_floor`, the module docstring, and the `build_protocol` signal/data-availability strings — `grep -n 'tox_signal' ` to catch every one).
   - `SURFACE_SIGNAL: str = "toxicity"` → `SURFACE_SIGNAL: str = "imbalance"`.
   - Keep `_forward_return_variance`, `TARGET = "realized_return_variance"`, `GRID_BAR_SECONDS`, `FORWARD_HORIZONS_BARS`, the floor, and all EVAL-65 inference **verbatim**.
3. **Rename ids/labels/filenames:** `159`→`160` in filenames, `TASK_ID`, `TASK_LABEL`, `COMMANDS`, docstrings, default paths, and the `EVAL159`/`EVAL_159`/`EVAL-159` forms (grep for BOTH `EVAL_160` and `EVAL160` and `EVAL-160` — see bottleneck #13). `variance` stays `variance`.
4. **Tests:** keep the 19-test structure of EVAL-159 (13 runner + 6 gate). In the runner test flip the signal assertions: `a["signal"] == "toxicity"` → `"imbalance"`, `proto["surface_signal"] == "toxicity"` → `"imbalance"`, `e160.SURFACE_SIGNAL == "toxicity"` → `"imbalance"`. Keep `test_forward_return_variance_matches_manual_second_moment` and the fat-tailed/dispersed fixture unchanged.
5. **Gate:** set `TASK_ID = "INIT-<this-session-start ISO Z>-EVAL160-CROSS-ASSET-ORDERFLOW-IMBALANCE-SPILLOVER-FORWARD-RETURN-VARIANCE"` (use the session start time, never a projected future time — bottleneck #6), `TASK_LABEL` likewise; `PREREG_GLOB`/`COMBINED_GLOB`/`BLOCKED_GLOB` → `EVAL_160_..._VARIANCE_*`. Update `test_task_floor_stamp_parses_iso` to the matching stamp, and bump the `test_detect_seal_hit` fake artifact stamp to `>= ` the new floor.
6. **Wire into driver:** in `scripts/eval67_prethreshold_progress.py` add `TARGETED_TEST_FILES` +2 (the 160 runner + gate test files), `GATE_SPECS` +1 (`wait_phase:"DUE"`), `SEAL_SPECS` +1 (`expected_exit:1`, flipped to 0 after sealing). Verify `pytest --collect-only` count, then set `EXPECTED_TARGETED_TESTS = 1996 + 19 = 2015`.
7. **Seal:** `python3 scripts/eval160_phaseb_gate.py --execute` (the driver flips `expected_exit` 1→0 on seal; also flip 1→0 manually in `SEAL_SPECS` for clarity). Re-run the full driver — require green at `2015/2015`.

## POST-SWEEP FOCUS CAMPAIGN (starts the moment EVAL-160 seals — do not re-derive)

Once EVAL-160 seals, the order-flow distributional-moment sweep is **complete** (mean, variance, skewness, kurtosis, downside-semivariance share — for BOTH the toxicity and imbalance signals). The order-flow line is uniformly **NO-GO** as a standalone predictor across every moment; the surviving directional alpha is entirely on the **surface** line (EVAL-101/102/104 GO CONFIRMED, IC 0.26–0.41). The next focus campaign is therefore the charter's actual **"strategy"** deliverable: a **traded-form, net-of-cost** evaluation of the strongest surviving GO surface anchor (**EVAL-104 `term_slope`→forward signed return**, fallbacks EVAL-102 `term_ratio`, EVAL-101 `atm_iv`), paper-only, converting predictiveness into net-of-cost viability. **Constraint:** do NOT re-litigate the already-sealed traded-form cells (EVAL-72/75/76/80/82/124/135/137/142 — all NO-GO/BLOCKED); design a genuinely distinct, non-overlapping cell. This is the anti-avoidance backstop: after the moment sweep there is still a clearly charter-relevant, unsealed campaign to build.

## VERIFIED STATE (2026-11-21T06:57:54Z, this session — driver re-run exit 0)

Driver source of truth: `EXPECTED_TARGETED_TESTS=1996`, `EXPECTED_DIAGNOSTIC_TESTS=27` (see `scripts/eval67_prethreshold_progress.py`). All `EVAL-70..159` `SEALED`/`ok`; `EVAL-67/68/69` `SEALED` (forward disjoint-window ladder complete; disjoint-window threshold `2026-11-20T00:00:00Z` PASSED). Readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json` (`updated_at: 2026-11-21T06:57:14Z`; `tests_passed=1996`, `diagnostics_passed=27`, `total_tests_passed=2023`, `gate_exit=0`, `gate_phase=SEALED`). `research_state/durable_handoff.md` remains the only authoritative build queue.

- **NEW VERIFIED FACTS (this session):** (a) EVAL-157 (cross-asset toxicity → forward realized return kurtosis) sealed `NO-GO CONFIRMED (PASS)` at `20261121T054648Z` (ETH→BTC best IC 0.1004, 0 pass; BTC→ETH 0.0927, 0 pass); (b) EVAL-158 (cross-asset imbalance → forward realized return kurtosis) sealed `NO-GO CONFIRMED (PASS)` at `20261121T060009Z` (ETH→BTC best IC 0.1774, 1 BH-FDR pass; BTC→ETH 0.0784, 0 pass — fails the both-asset GO bar); (c) **EVAL-159 (cross-asset toxicity → forward realized return VARIANCE) built + wired + sealed this session** `NO-GO CONFIRMED (PASS)` at `20261121T065641Z` (ETH→BTC best IC 0.1412, 0 pass; BTC→ETH best IC 0.1019, 0 pass; BH-FDR rejected `[]`); (d) driver advanced from a stale `1939`-expectation/handoff-pointing-at-157 state to a green `1996/1996` run; (e) `EVAL-157`/`EVAL-158` `expected_exit` flipped 1→0 in `SEAL_SPECS` for clarity (bottleneck #5). **No unsealed pre-threshold campaign rung remains *after* EVAL-160 is built** (EVAL-160 imbalance→variance is the mandated next build; then the post-sweep strategy pivot above).

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | **CLOSED** (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67, EVAL-68, EVAL-69 | **SEALED** (`20261120T005220Z`, `20261120T014819Z`, `20261120T015619Z`); 68/69 `BLOCKED` kind |
| Physics-independent predictiveness EVAL-70..147 | 78 rungs | **SEALED** |
| Traded-form net-of-cost | EVAL-72/75, 76, 80, 82, 124/135, 137, 142 | all `NO-GO`/`BLOCKED` |
| Cross-asset spillover → forward signed return mean | EVAL-148 (atm_iv/skew/term_slope/term_ratio) | **SEALED COMPLETE** (4 cells, `010725Z`..`010827Z`) |
| **Cross-asset options order-flow → forward signed return mean** | EVAL-149 (imbalance), 150 (imbalance×atm_iv), 151 (toxicity×atm_iv), 152 (toxicity alone) | **SEALED COMPLETE** (`010848Z`..`025341Z`) |
| **Cross-asset options order-flow → forward skewness** | EVAL-153 (toxicity), 154 (imbalance) | **SEALED COMPLETE** (`025645Z`, `031533Z`) |
| **Cross-asset options order-flow → forward downside-semivariance share** | EVAL-155 (toxicity), 156 (imbalance) | **SEALED COMPLETE** (`042021Z`, `044145Z`) |
| **Cross-asset options order-flow → forward realized return kurtosis** | EVAL-157 (toxicity), 158 (imbalance) | **SEALED COMPLETE** (`054648Z`, `060009Z`) |
| **Cross-asset options order-flow → forward realized return variance** | EVAL-159 (toxicity) | **EVAL-159 SEALED** (`20261121T065641Z`); **EVAL-160 (imbalance) = NEXT MANDATED BUILD** — completes the order-flow moment sweep |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — EVAL-160 is the next unsealed rung

The order-flow distributional sweep is complete for the mean (149–152), skewness (153/154), downside-semivariance share (155/156), kurtosis (157/158) and toxicity→variance (159). The single remaining standard-moment cell is **imbalance → forward realized return variance** — see the **EVAL-160 BUILD RECIPE** above for the exact clone/swap/wire/seal procedure (this section is the charter rationale; the recipe is the executable procedure):

1. **EVAL-160 (NEXT MANDATED BUILD — build + wire + seal next session):** cross-asset **options order-flow imbalance** spillover → forward **realized return variance** (clone **EVAL-159** and swap the signal `tox_signal="tox"`→`"imbalance"`, `SURFACE_SIGNAL "toxicity"`→`"imbalance"`; carry the `_forward_return_variance` target verbatim). Grid `{60s,300s}` × `H∈{6,24,72}` (6 configs per target, 12 total). GO = **BOTH-asset** else `NO-GO CONFIRMED (PASS)`; below floor ⇒ `BLOCKED`.
   - **Runner/gate/tests:** `scripts/eval160_cross_asset_orderflow_imbalance_spillover_forward_return_variance.py`, `scripts/eval160_phaseb_gate.py`, `tests/test_eval160_cross_asset_orderflow_imbalance_spillover_forward_return_variance.py`, `tests/test_eval160_phaseb_gate.py`.
   - **Wire into driver:** `TARGETED_TEST_FILES` +2, `GATE_SPECS` +1 (`wait_phase:"DUE"`), `SEAL_SPECS` +1 (`expected_exit:1` then flip to 0 after sealing), and bump `EXPECTED_TARGETED_TESTS` by the exact collected count — verify with `pytest --collect-only` (expect `2015`).

Already covered — do **not** rebuild: EVAL-77, 88..159. Do not re-test `atm_iv`→VRP (mechanical overlap), do not re-test `term_ratio`→VRP, do not rebuild the collar (EVAL-76), do not re-run EVAL-144..159 as a substitute for new work, do not re-litigate sealed cells, do not weaken EVAL-64, do not touch `src/`.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) complete. EVAL-70..159 gates: `SEALED`(0) idempotent no-op; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- EVAL-137/142: `SEALED`(0) complete (BLOCKED). EVAL-138/139: `SEALED`(0) complete (GO CONFIRMED). EVAL-140/141/144/145/146/147/150/151/152/153/154/155/156/157/158/159: `SEALED`(0) complete (NO-GO). EVAL-143: `SEALED`(0) complete (verdict per run). EVAL-148 (4 cells): `SEALED`(0) complete. EVAL-149: `SEALED`(0) complete. Idempotent no-ops; do not re-run.
- Green driver = env OK, `1996/1996` targeted, `27/27` diagnostics, all `EVAL-70..159` gates `SEALED`/`ok`, `EVAL-67/68/69` `SEALED`, every `GATE_SPEC` ok + every `SEAL_SPEC` ok, `failures: []`, `gate_phase: SEALED`, `gate_exit=0`.
- Adding a rung: write runner+gate+tests → `pytest -q tests/test_evalNNN_*.py` green → wire the three driver tables + bump `EXPECTED_TARGETED_TESTS` to the actual collected count → `python3 scripts/evalNNN_phaseb_gate.py --execute` (flips `expected_exit` 1→0 via the driver's sealed-override; also flip 1→0 in the same session for clarity) → driver green.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling. No capture bridges/waiters.
2. Competing handoff pointers/copies — removed; this file is the single handoff (do not create copies or edit `AGENTS.md` into a competing queue).
3. Pre-threshold "no heavy work left" avoidance — removed; the queue above always has a next rung (EVAL-159 → EVAL-160, then the post-sweep strategy pivot). An explicit "EVAL-160 BUILD RECIPE" section makes the next build unambiguous.
4. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
5. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity (EVAL-157/158 were flipped this session).
6. **Stale-handoff / timestamp-refresh treadmill (removed this session):** the 05:37 handoff still pointed at "build EVAL-157" while EVAL-157/158 were already sealed (`054648Z`/`060009Z`). Fixed: this handoff reflects the true sealed state (157/158 sealed, 159 sealed this session) and points at the genuinely-next unbuilt rung EVAL-160. Do not refresh the timestamp without new verified facts (green driver + green tests + green gates).
7. Task-floor-stamp ordering bug — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
8. Degenerate skew/kurtosis/variance fixture trap — alternating ±drift yields an all-zero third/fourth/second moment; skewness/kurtosis/variance fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
9. **Half-wired driver:** a new rung's test files added to `TARGETED_TEST_FILES` without adding the rung to `GATE_SPECS`/`SEAL_SPECS` and without bumping `EXPECTED_TARGETED_TESTS`, so the driver fails the count check. Always reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green.
10. Signal/target (and hyphenated `TERM-RATIO`) copy-paste bugs in a cloned runner/gate/tests — always grep the new files for stale ids, hyphenated task labels, signal/target names AND stale `e138`/helper references before sealing (the EVAL-159 clone initially carried a corrupted `eval138_..._variance` import and kurtosis helper body — both caught and fixed).
11. Composite/both-asset GO bar — GO requires BOTH BTC and ETH to have ≥1 BH-FDR-rejected passing config; a single-asset pass is a legitimate `NO-GO CONFIRMED (PASS)`; do not relax the bar.
12. Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via EVAL-71 `build_surface_bars`; `term_slope`/`term_ratio` via EVAL-74 `_term_bars`; order-flow imbalance/toxicity via EVAL-62 `build_states`. Do not cross them.
13. No-hyphen / underscore / hyphenated `EVAL159` / `EVAL_159` / `EVAL-159` task-label traps when cloning — a single bulk replace of one form does NOT catch the others; grep for ALL THREE forms (`EVAL_15x`, `EVAL15x`, `EVAL-15x`) before sealing. The hyphenated uppercase form (`CROSS-ASSET-...-KURTOSIS`) is separate from the underscore id form (`EVAL_15x_..._KURTOSIS`).

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..159 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-68 acquires BTC+ETH in ONE process; EVAL-69/143/145/146/147/149/150/151/152/153/154/155/156/157/158/159 acquire nothing (consume on-disk `data/raw/eval61`).
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

# 1) Full heavy-work loop; run every session (idempotent). EVAL-70..159 SEALED; no-op on re-run:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) Verify a sealed campaign idempotently:
python3 scripts/eval159_phaseb_gate.py

# 3) Build/seal a new rung (pattern for EVAL-160):
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q tests/test_eval160_*.py
python3 scripts/eval160_phaseb_gate.py --execute
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself); a bare `python3 scripts/eval1xx_*.py` fails on `numpy` without it.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..69, 70..159 sealed. EVAL-63 never sealed. Predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`), 88, 90, 91, 93, 97, 99, 100, 101, 102, 104, 109, 111, 112, 113, 114, 116, 120, 122, 125, 138, 139 (`GO CONFIRMED`). NO-GO CONFIRMED (PASS): EVAL-70, 72, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103, 105, 106, 107, 108, 110, 115, 117, 118, 119, 121, 123, 126, 127, 128, 129, 130, 131, 133, 134, 136, 140, 141, 144, 145, 146, 147, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159. BLOCKED: EVAL-124, EVAL-135, EVAL-137, EVAL-142. EVAL-67/68/69 SEALED (forward ladder complete). EVAL-148 (4 cells) SEALED. EVAL-149 SEALED. Strongest surviving GO IC anchors unchanged: EVAL-101 `atm_iv`→signed return (BTC 0.2313 / ETH 0.3442); EVAL-102 `term_ratio`→signed return (BTC 0.3926 / ETH 0.2559); EVAL-104 `term_slope`→signed return (BTC 0.4058 / ETH 0.2600); EVAL-114 `atm_iv` spillover→return skewness (BTC 0.4039 / ETH 0.1173); EVAL-122 `term_slope` spillover→return skewness (BTC 0.3817 / ETH 0.4643); EVAL-125 `term_ratio` basis→return-kurtosis spread (IC 0.4128); EVAL-138 `term_ratio` spillover→return kurtosis (BTC 0.2931 / ETH 0.4679); EVAL-139 `term_ratio` spillover→return skewness (BTC 0.2613 / ETH 0.4878, 7 BH-FDR). Order-flow NO-GO anchors (all fail the both-asset GO bar): EVAL-152 toxicity→signed-return (BTC 0.1878, 1 pass; ETH 0.0969, 0); EVAL-153 toxicity→skewness (BTC 0.2180, 2; ETH 0.0598, 0); EVAL-154 imbalance→skewness (BTC 0.0573, 0; ETH 0.0887, 0); EVAL-157 toxicity→kurtosis (ETH→BTC 0.1004, 0; BTC→ETH 0.0927, 0); EVAL-158 imbalance→kurtosis (ETH→BTC 0.1774, 1; BTC→ETH 0.0784, 0); **EVAL-159 toxicity→variance (ETH→BTC 0.1412, 0; BTC→ETH 0.1019, 0)**.

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
- **2026-11-21T06:57:54Z:** **Bottlenecks removed + heavy work continued.** (a) Verified driver green at `1996/1996` targeted + `27/27` diagnostics (157/158 already sealed by prior work; the 05:37 handoff was stale — fixed). (b) Built + wired + sealed **EVAL-159** (cross-asset **toxicity** → forward **realized return variance**, `NO-GO CONFIRMED (PASS)`, `20261121T065641Z`; ETH→BTC best IC 0.1412, 0 pass; BTC→ETH best IC 0.1019, 0 pass; clone of EVAL-157 signal path + new `_forward_return_variance` target = the EVAL-138 moment-family `m2` term; 19 tests). Wired `TARGETED_TEST_FILES` +2, `GATE_SPECS` +1, `SEAL_SPECS` +1 (`expected_exit` 1→0); flipped EVAL-157/158 `expected_exit` 1→0; corrected `EXPECTED_TARGETED_TESTS` 1977→1996 (verified `--collect-only` = 1996). Full driver **green: 1996/1996 targeted + 27/27 diagnostics, all gates SEALED + all seal gates ok, `failures: []`, exit 0** (`EVAL_67_PREWINDOW_READINESS.json`, `updated_at: 2026-11-21T06:57:14Z`). No sealed artifact or `src/` modified. **Next mandated build: EVAL-160 (cross-asset imbalance → forward realized return variance)** — completes the order-flow distributional-moment sweep (mean, variance, skewness, kurtosis, downside-semivariance share for both signals). Anti-avoidance in force — a green driver + all-sealed is NOT completion; after EVAL-160 the programme pivots to the traded-form net-of-cost strategy on the strongest surviving GO surface anchor (EVAL-104 `term_slope`→signed return). Build + seal EVAL-160 in the next session per the EVAL-160 BUILD RECIPE.