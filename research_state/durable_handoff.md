# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-21T03:55:40Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** `...options...orderflow...` ⇒ two load-bearing halves; the **options order-flow half is the highest charter-relevance rung** and is the mandated line. The surface-signal line (EVAL-138..148) is saturated; the **order-flow line EVAL-149 → EVAL-150 → EVAL-151 → EVAL-152 → EVAL-153 → EVAL-154 → EVAL-155 → EVAL-156** is the active heavy-work queue. The order-flow → directional line (signed-return mean) is saturated (149/150/151/152) and the order-flow → skewness line is now complete for both signals (153 toxicity, 154 imbalance). The next mandated heavy work is the **downside-semivariance share (DSS)** distributional target for both order-flow signals:
>   - EVAL-149 cross-asset imbalance → forward signed return mean — SEALED `20261121T010848Z`.
>   - EVAL-150 cross-asset imbalance × atm_iv interaction → forward signed return mean — SEALED `20261121T015450Z` (`NO-GO`, 0 pass both legs).
>   - EVAL-151 cross-asset toxicity × atm_iv interaction → forward signed return mean — SEALED `20261121T020925Z` (`NO-GO`, 0 pass both legs).
>   - EVAL-152 cross-asset toxicity alone → forward signed return mean — SEALED `20261121T025341Z` (`NO-GO CONFIRMED (PASS)`; BTC best IC 0.1878 with 1 BH-FDR-rejected pass, ETH best 0.0969 with 0 pass ⇒ both-asset GO bar unmet).
>   - EVAL-153 cross-asset toxicity alone → forward realized return **skewness** — SEALED `20261121T025645Z` (`NO-GO CONFIRMED (PASS)`; BTC best IC 0.2180 with 2 BH-FDR-rejected passes, ETH best 0.0598 with 0 pass ⇒ both-asset GO bar unmet).
>   - EVAL-154 cross-asset imbalance alone → forward realized return **skewness** — SEALED `20261121T031533Z` (`NO-GO CONFIRMED (PASS)`; BTC best IC 0.0573 with 0 pass, ETH best 0.0887 with 0 pass ⇒ both-asset GO bar unmet).
>
> **FIRST ACTION, non-negotiable:** run the full heavy-work driver and require exit 0 (idempotent no-op on every sealed rung):
>   ```bash
>   python3 scripts/eval67_prethreshold_progress.py --execute
>   ```
>   Require: `targeted_tests: 1901/1901`, `diagnostic_tests: 27/27`, all `EVAL-70..154` gates `SEALED`/`ok`, `EVAL-67/68/69` `SEALED` (forward disjoint-window threshold `2026-11-20T00:00:00Z` PASSED), every `GATE_SPEC` classified ok + every `SEAL_SPEC` ok, `failures: []`, `overall_ok=True exit=0`.
>
> **SECOND ACTION (anti-avoidance — a green driver + all-sealed is NOT completion):** build + wire + seal the next order-flow rung **EVAL-155** in THIS session (full recipe below), then leave EVAL-156 queued. Do **not** stop at "everything is sealed".
>
> **STATUS:** this session removed the prior broken-driver bottleneck (EVAL-152 sealed + wired; `EXPECTED_TARGETED_TESTS` 1845→1863), built + sealed EVAL-153 (toxicity → skewness, 19 tests), then built + sealed EVAL-154 (imbalance → skewness, 19 tests) and wired both into the driver (`TARGETED_TEST_FILES` +4, `GATE_SPECS` +2, `SEAL_SPECS` +2), correcting `EXPECTED_TARGETED_TESTS` to **1901** (verified via `pytest --collect-only` = 1901). The full driver is **green at 1901/1901 + 27/27, exit 0** (`research_state/EVAL_67_PREWINDOW_READINESS.json`, `updated_at: 2026-11-21T03:21:16Z`; 91 unique seal gates; `failures: []`). No sealed artifact or `src/` was modified; all new work is append-only. **Next mandated build: EVAL-155 (cross-asset toxicity → forward downside-semivariance share), then EVAL-156 (imbalance → downside-semivariance share).**
>
> **BOTTLENECKS REMOVED — DO NOT REDISCOVER:** (1) **half-wired driver** — a new rung's test files were added to `TARGETED_TEST_FILES` without adding the rung to `GATE_SPECS`/`SEAL_SPECS` and without bumping `EXPECTED_TARGETED_TESTS`; fixed (152/153/154 all sealed + wired, count → 1901). The driver is the source of truth — always reconcile `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` over `TARGETED_TEST_FILES` before trusting a green run. (2) **order-flow constructibility doubt** — imbalance AND toxicity states are constructible on all three `data/raw/eval61/three_way_*.json` tapes (`e62.build_states(...,tox_signal="imbalance"|"tox",bar_seconds=300)` → 289 states with `signal_z`); never emit data-absence `BLOCKED` for order-flow rungs. (3) **surface-bar vs term-bar vs order-flow signal path** — `atm_iv`/`skew` are EVAL-71 `build_surface_bars` (surface bar); `term_slope`/`term_ratio` are EVAL-74 `_term_bars` (term bar); order-flow imbalance/toxicity are EVAL-62 `build_states`. (4) **composite/both-asset GO bar** — GO requires BOTH BTC and ETH to have ≥1 BH-FDR-rejected passing config; a single-asset pass is a legitimate `NO-GO CONFIRMED (PASS)`, never a reason to relax the bar. (5) **copy-paste id/label/hyphen/task-floor-stamp traps** in cloned runners/gates/tests — grep the new files for stale ids (`EVAL_1[0-9][0-9]`, `EVAL1[0-9][0-9]` no-hyphen), hyphenated task labels, and signal/target names; the gate `TASK_ID` ISO stamp must be ≤ the sealed artifact stamp (use a session-start time); the `test_detect_seal_hit` fixture stamp must be > the floor stamp.

## VERIFIED STATE (2026-11-21T03:55:40Z, this session — driver re-run exit 0)

Driver source of truth: `EXPECTED_TARGETED_TESTS=1901`, `EXPECTED_DIAGNOSTIC_TESTS=27` (see `scripts/eval67_prethreshold_progress.py`). All `EVAL-70..154` `SEALED`/`ok`; `EVAL-67/68/69` `SEALED` (forward disjoint-window ladder complete; disjoint-window threshold `2026-11-20T00:00:00Z` PASSED). Readiness refreshed at `research_state/EVAL_67_PREWINDOW_READINESS.json` (`updated_at: 2026-11-21T03:21:16Z`; 1901 targeted + 27 diagnostics = 1928, all gates SEALED + all seal gates ok, `failures: []`, exit 0, `ok: True`). `research_state/durable_handoff.md` remains the only authoritative build queue.

- **NEW VERIFIED FACTS (this session):** (a) EVAL-152 (cross-asset toxicity → signed return mean) sealed `NO-GO CONFIRMED (PASS)` at `20261121T025341Z`; (b) EVAL-153 (cross-asset toxicity → forward realized return skewness) built + wired + sealed `NO-GO CONFIRMED (PASS)` at `20261121T025645Z`; (c) EVAL-154 (cross-asset imbalance → forward realized return skewness) built + wired + sealed `NO-GO CONFIRMED (PASS)` at `20261121T031533Z`; (d) driver repaired from a broken 1845-expectation/1863-actual state to a green 1901/1901 run. No unsealed pre-threshold campaign rung remains **after** EVAL-155 is built (EVAL-155 is the mandated next build).

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | **CLOSED** (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67, EVAL-68, EVAL-69 | **SEALED** (`20261120T005220Z`, `20261120T014819Z`, `20261120T015619Z`); 68/69 `BLOCKED` kind |
| Physics-independent predictiveness EVAL-70..147 | 78 rungs | **SEALED** |
| Traded-form net-of-cost | EVAL-72/75, 76, 80, 82, 124/135, 137, 142 | all `NO-GO`/`BLOCKED` |
| Cross-asset spillover → forward signed return mean | EVAL-148 (atm_iv/skew/term_slope/term_ratio surface/term bars) | **SEALED COMPLETE** (4 cells, `20261121T010725Z`..`010827Z`) |
| **Cross-asset options order-flow → forward signed return mean** | EVAL-149 (imbalance), EVAL-150 (imbalance×atm_iv), EVAL-151 (toxicity×atm_iv), EVAL-152 (toxicity alone) | **SEALED COMPLETE** (`010848Z`, `015450Z`, `020925Z`, `025341Z`) — serves the *order-flow* half of the charter |
| **Cross-asset options order-flow → forward realized return skewness** | EVAL-153 (toxicity alone), EVAL-154 (imbalance alone) | **SEALED COMPLETE** (`025645Z`, `031533Z`) — both arms of the order-flow → skewness line |
| Cross-asset options order-flow → forward downside-semivariance share | EVAL-155 (toxicity), EVAL-156 (imbalance) | **NEXT MANDATED BUILD** (EVAL-155, unsealed); EVAL-156 queued |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — EVAL-155 is the next unsealed rung

The order-flow → directional line (signed-return mean) is saturated (149/150/151/152) and the order-flow → skewness line is now complete for both signals (153 toxicity, 154 imbalance). The next mandated heavy work is the **downside-semivariance share (DSS)** distributional target for both order-flow signals.

1. **EVAL-155 (NEXT MANDATED BUILD — build + wire + seal this session):** cross-asset **options order-flow toxicity** spillover → forward **downside-semivariance share** (Spearman rank IC).
   - **Signal:** OTHER underlying's causal per-bar options order-flow **toxicity** z — `e62.build_states(capture, tox_signal="tox", bar_seconds=bar_seconds)` → align on the common `bar_ms` grid (`build_cross_section` on toxicity states) → causal forward-fill (`e71._forward_fill`) → expanding z-score end-of-bar `k` (`e61.expanding_zscore`, `e62.ZWINDOW`).
   - **Target:** forward **downside-semivariance share (DSS)** of the TARGET underlying over bars `k+1..k+H` — **transcribed verbatim from sealed EVAL-144** (`_forward_downside_semivariance_share`). Windows with non-positive total variance yield `None`.
   - **Inference:** EVAL-65 `_perm_p_ic` / `_boot_ci_ic` + EVAL-62 `ZWINDOW`/`FDR_ALPHA`; `src.analytics.real_walkforward_certification._benjamini_hochberg`. Grid `{60s,300s}` × `H∈{6,24,72}` (6 configs per target, 12 total). GO = **BOTH-asset** (BTC AND ETH each ≥1 BH-FDR-rejected passing config) else `NO-GO CONFIRMED (PASS)`; below floor ⇒ `BLOCKED`.
   - **Template / clone:** clone **EVAL-153** (`scripts/eval153_cross_asset_orderflow_toxicity_spillover_forward_return_skewness.py` + `eval153_phaseb_gate.py` + `tests/test_eval153_*`) and swap the target to EVAL-144's `_forward_downside_semivariance_share`; keep `tox_signal="tox"` (toxicity). Ids/labels/filenames `153`→`155`; target name `realized_return_skewness`→`downside_semivariance_share`.
   - **Runner/gate/tests:** `scripts/eval155_cross_asset_orderflow_toxicity_spillover_forward_downside_semivariance_share.py`, `scripts/eval155_phaseb_gate.py` (`TASK_ID = INIT-<session-start UTC>-EVAL155-CROSS-ASSET-ORDERFLOW-TOXICITY-SPILLOVER-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`), `tests/test_eval155_cross_asset_orderflow_toxicity_spillover_forward_downside_semivariance_share.py`, `tests/test_eval155_phaseb_gate.py`.
   - **Wire into driver:** `TARGETED_TEST_FILES` +2, `GATE_SPECS` +1 (`wait_phase:"DUE"`), `SEAL_SPECS` +1 (`expected_exit:1` then flip to 0 after sealing), and bump `EXPECTED_TARGETED_TESTS` by the **exact** collected count — verify with `PYTHONPATH=$PWD/.venv-deps python3 -m pytest --collect-only -q tests/test_eval155_*.py` (each standard rung is 18–19 tests; EVAL-153/154 were 19).
   - **Constructibility:** VERIFIED (toxicity states on all three `data/raw/eval61/three_way_*.json` tapes, 289 states with `signal_z`). Never `BLOCKED` for data absence.
2. **EVAL-156 (queued):** cross-asset **imbalance** spillover → forward **downside-semivariance share** (clone EVAL-154 signal + EVAL-144 DSS target).

Already covered — do **not** rebuild: EVAL-77, 88..154. Do not re-test `atm_iv`→VRP (mechanical overlap), do not re-test `term_ratio`→VRP, do not rebuild the collar (EVAL-76), do not re-run EVAL-144..154 as a substitute for new work, do not re-litigate sealed cells, do not weaken EVAL-64, do not touch `src/`.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) complete. EVAL-70..154 gates: `SEALED`(0) idempotent no-op; `DUE`(20) run `--execute` now; `FAILED`(1) fix and rerun.
- EVAL-137/142: `SEALED`(0) complete (BLOCKED). EVAL-138/139: `SEALED`(0) complete (GO CONFIRMED). EVAL-140/141/144/145/146/147/150/151/152/153/154: `SEALED`(0) complete (NO-GO). EVAL-143: `SEALED`(0) complete (verdict per run). EVAL-148 (4 cells): `SEALED`(0) complete. EVAL-149: `SEALED`(0) complete. Idempotent no-ops; do not re-run.
- Green driver = env OK, `1901/1901` targeted, `27/27` diagnostics, all `EVAL-70..154` gates `SEALED`/`ok`, `EVAL-67/68/69` `SEALED`, every `GATE_SPEC` ok + every `SEAL_SPEC` ok, `failures: []`, exit 0.
- Adding a rung: write runner+gate+tests → `pytest -q tests/test_evalNNN_*.py` green → wire the three driver tables + bump `EXPECTED_TARGETED_TESTS` to the actual collected count → `python3 scripts/evalNNN_phaseb_gate.py --execute` (flips `expected_exit` 1→0 via the driver's sealed-override; also flip 1→0 in the same session for clarity) → driver green.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling. No capture bridges/waiters.
2. Competing handoff pointers/copies — removed; this file is the single handoff (do not create copies or edit `AGENTS.md` into a competing queue).
3. Pre-threshold "no heavy work left" avoidance — removed; the queue above always has a next rung (EVAL-155 → EVAL-156).
4. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
5. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
6. Task-floor-stamp ordering bug — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
7. Degenerate skew/kurtosis fixture trap — alternating ±drift yields an all-zero third moment; skewness/kurtosis fixtures need fat-tailed (occasional large jump) increments.
8. **Half-wired driver (removed this session):** a new rung's test files were added to `TARGETED_TEST_FILES` without adding the rung to `GATE_SPECS`/`SEAL_SPECS` and without bumping `EXPECTED_TARGETED_TESTS`, so the driver failed the count check. Always reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green.
9. Signal/target (and hyphenated `TERM-RATIO`) copy-paste bugs in a cloned runner/gate/tests — always grep the new files for stale ids, hyphenated task labels, and signal/target names before sealing.
10. Composite/both-asset GO bar — GO requires BOTH BTC and ETH to have ≥1 BH-FDR-rejected passing config; a single-asset pass is a legitimate `NO-GO CONFIRMED (PASS)`; do not relax the bar.
11. Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via EVAL-71 `build_surface_bars`; `term_slope`/`term_ratio` via EVAL-74 `_term_bars`; order-flow imbalance/toxicity via EVAL-62 `build_states`. Do not cross them.
12. Multi-cell / multi-rung test-count math — each standard rung = 2 test files; EVAL-153/154 each added a 19th test (an extra `matches_eval139` equivalence test), so per-rung counts are 18–19. Verify per-rung count with `pytest --collect-only` and bump `EXPECTED_TARGETED_TESTS` to the exact total.
13. No-hyphen `EVAL153` task-label trap when cloning — bulk-replacing `EVAL-153`→`EVAL-154` does NOT catch `EVAL153-...` (no hyphen) in `TASK_ID`/`TASK_LABEL`/`COMMANDS`/defaults; grep for both `EVAL_15x` and `EVAL15x` before sealing.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..154 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-68 acquires BTC+ETH in ONE process; EVAL-69/143/145/146/147/149/150/151/152/153/154 acquire nothing (consume on-disk `data/raw/eval61`).
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

# 1) Full heavy-work loop; run every session (idempotent). EVAL-70..154 SEALED; no-op on re-run:
python3 scripts/eval67_prethreshold_progress.py --execute

# 2) Verify a sealed campaign idempotently:
python3 scripts/eval154_phaseb_gate.py

# 3) Build/seal a new rung (pattern for EVAL-155):
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m pytest -q tests/test_eval155_*.py
python3 scripts/eval155_phaseb_gate.py --execute
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself); a bare `python3 scripts/eval1xx_*.py` fails on `numpy` without it.

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..66, 67..69, 70..154 sealed. EVAL-63 never sealed. Predictiveness GOs: EVAL-71, 73, 77, 83, 85, 86, 87 (`GO/BLOCKED`), 88, 90, 91, 93, 97, 99, 100, 101, 102, 104, 109, 111, 112, 113, 114, 116, 120, 122, 125, 138, 139 (`GO CONFIRMED`). NO-GO CONFIRMED (PASS): EVAL-70, 72, 75, 76, 78, 79, 80, 81, 82, 84, 89, 92, 94, 95, 96, 98, 103, 105, 106, 107, 108, 110, 115, 117, 118, 119, 121, 123, 126, 127, 128, 129, 130, 131, 133, 134, 136, 140, 141, 144, 145, 146, 147, 150, 151, 152, 153, 154. BLOCKED: EVAL-124, EVAL-135, EVAL-137, EVAL-142. EVAL-67/68/69 SEALED (forward ladder complete). EVAL-148 (4 cells) SEALED. EVAL-149 SEALED. Strongest surviving GO IC anchors unchanged: EVAL-101 `atm_iv`→signed return (BTC 0.2313 / ETH 0.3442); EVAL-102 `term_ratio`→signed return (BTC 0.3926 / ETH 0.2559); EVAL-104 `term_slope`→signed return (BTC 0.4058 / ETH 0.2600); EVAL-114 `atm_iv` spillover→return skewness (BTC 0.4039 / ETH 0.1173); EVAL-122 `term_slope` spillover→return skewness (BTC 0.3817 / ETH 0.4643); EVAL-125 `term_ratio` basis→return-kurtosis spread (IC 0.4128); EVAL-138 `term_ratio` spillover→return kurtosis (BTC 0.2931 / ETH 0.4679); EVAL-139 `term_ratio` spillover→return skewness (BTC 0.2613 / ETH 0.4878, 7 BH-FDR). New NO-GO anchors this session: **EVAL-152 toxicity→signed-return (BTC 0.1878, 1 BH-FDR pass; ETH 0.0969, 0 pass)**; **EVAL-153 toxicity→skewness (BTC 0.2180, 2 BH-FDR passes; ETH 0.0598, 0 pass)**; **EVAL-154 imbalance→skewness (BTC 0.0573, 0 pass; ETH 0.0887, 0 pass)** — all fail the both-asset GO bar.

## SESSION LOG (append-only; only load-bearing entries retained)

- **2026-11-21T01:22:25Z:** EVAL-148 (4 cells) + EVAL-149 sealed; driver green 1809/1809+27/27. (Prior session.)
- **2026-11-21T02:18:18Z:** Prior (interrupted) session built EVAL-150/151/152 runners+gates+tests and sealed EVAL-150 (`015450Z`) + EVAL-151 (`020925Z`), wired 150/151 into the driver, but left **EVAL-152 unsealed and unwired** and set `EXPECTED_TARGETED_TESTS=1845` (actual 1863) — the driver was left **broken** and the handoff was not updated.
- **2026-11-21T03:03:13Z:** **Bottleneck removed + heavy work continued.** (a) Sealed **EVAL-152** (`NO-GO CONFIRMED (PASS)`, `20261121T025341Z`; BTC best IC 0.1878 with 1 BH-FDR-rejected pass, ETH 0.0969 with 0 pass). (b) Wired EVAL-152 into `GATE_SPECS`+`SEAL_SPECS`; corrected `EXPECTED_TARGETED_TESTS` 1845→1863. (c) Built + wired + sealed **EVAL-153** (cross-asset toxicity → forward realized return skewness, `NO-GO CONFIRMED (PASS)`, `20261121T025645Z`; BTC best IC 0.2180 with 2 BH-FDR-rejected passes, ETH 0.0598 with 0 pass; clone of EVAL-152 signal path + EVAL-139 skewness target; 19 tests). (d) Corrected `EXPECTED_TARGETED_TESTS` 1863→1882. (e) Full driver **green: 1882/1882 targeted + 27/27 diagnostics, all gates SEALED + all seal gates ok, `failures: []`, exit 0**.
- **2026-11-21T03:21:16Z:** **Heavy work continued.** Built + wired + sealed **EVAL-154** (cross-asset **imbalance** → forward realized return skewness, `NO-GO CONFIRMED (PASS)`, `20261121T031533Z`; BTC best IC 0.0573 with 0 pass, ETH best IC 0.0887 with 0 pass; clone of EVAL-153 with `tox_signal="imbalance"` + EVAL-139 skewness target; 19 tests). Wired `TARGETED_TEST_FILES` +2, `GATE_SPECS` +1, `SEAL_SPECS` +1; corrected `EXPECTED_TARGETED_TESTS` 1882→1901 (verified `--collect-only` = 1901). Full driver **green: 1901/1901 targeted + 27/27 diagnostics, all gates SEALED + all 91 seal gates ok, `failures: []`, exit 0** (`EVAL_67_PREWINDOW_READINESS.json`, `updated_at: 2026-11-21T03:21:16Z`). No sealed artifact or `src/` modified. **Next mandated build: EVAL-155 (cross-asset toxicity → forward downside-semivariance share), then EVAL-156 (imbalance → downside-semivariance share).** Anti-avoidance in force — a green driver + all-sealed is NOT completion; build + seal EVAL-155 in the same session.