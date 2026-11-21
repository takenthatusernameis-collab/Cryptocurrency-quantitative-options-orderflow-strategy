# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-21T23:27:19Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. The order-flow distributional sweep is complete and uniformly NO-GO CONFIRMED (PASS). The surviving directional alpha is on the **surface** line. The single-asset surface distributional grids are complete (signed-return-mean / skewness / kurtosis / CVaR / downside-semivariance share / **variance**). The cross-asset order-flow sweep is complete. The cross-asset surface/term → forward-CVaR grid is complete (EVAL-168 atm_iv, 169 term_slope, 170 term_ratio, 171 skew; all sealed).
>
> **CURRENT MANDATED QUEUE:** EVAL-172 (single-asset `atm_iv` → forward variance), EVAL-173 (`skew`), EVAL-174 (`term_slope`), EVAL-175 (`term_ratio`) are **SEALED** (single-asset surface → forward variance grid COMPLETE). EVAL-176 (cross-asset `atm_iv` → forward variance) is **SEALED** (`20261121T231545Z`, `NO-GO CONFIRMED (PASS)`, floor OK). **EVAL-177 (cross-asset `skew` → forward realized return variance) is BUILT + WIRED + DUE (unsealed), and it computes to `GO CONFIRMED` on the real on-disk captures (floor OK; BOTH BTC and ETH targets pass; 5 pooled BH-FDR-rejected configs).** The driver is intentionally RED in status mode: exit 20, `needs_execute: ["EVAL-177"]`. The next session must run the driver with `--execute` to seal EVAL-177 (a GO), then build the next unsealed heavy rung in the same session.
>
> **DECISIVE BOTTLENECK REMOVED — there is ALWAYS runnable-now heavy work.** EVAL-177 is wired into `scripts/eval67_prethreshold_progress.py` (`TARGETED_TEST_FILES`, `GATE_SPECS`, `SEAL_SPECS`) and its expected targeted count is reconciled to **2322**. A green status-mode driver is not completion; after sealing EVAL-177, identify the next genuine gap from the sealed space and build it as a DUE gate. Natural next cells (remaining cross-asset surface/term → forward realized return variance grid): cross-asset `term_slope` → forward variance (EVAL-178) and cross-asset `term_ratio` → forward variance (EVAL-179). Both are **term-bar** cells (`e74._term_bars`, NOT `e71.build_surface_bars`) with cross-asset alignment — study `scripts/eval169_cross_asset_term_slope_spillover_forward_cvar.py` / `eval170_...term_ratio...` for the term-bar cross-asset pattern before cloning. Do not duplicate a sealed cell.
>
> **FIRST ACTION, NON-NEGOTIABLE, EVERY SESSION:**
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
> This should seal EVAL-177 (EVAL-172/173/174/175/176 are already sealed), then be an idempotent no-op after the seal. Require after the seal: `targeted_tests: 2322/2322`, `diagnostic_tests: 27/27`, all `EVAL-70..177` gates classified `ok`/phase `SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. If EVAL-177 is still DUE after `--execute`, the run FAILED — investigate; do not hand-wave.
>
> **THEN build the next runnable-now rung in the SAME session (never stop at "driver green"):** identify the next genuine gap from the sealed space (never duplicate a sealed cell) and build it as a DUE gate (runner + gate + 2 test files + driver `TARGETED_TEST_FILES`/`GATE_SPECS`/`SEAL_SPECS` + bump `EXPECTED_TARGETED_TESTS` by the verified `pytest --collect-only` delta), run the driver `--execute` to seal, require exit 0. Do not re-run, re-litigate, or re-seal sealed EVAL-02..62, EVAL-64..66, EVAL-70..176 artifacts or `src/`.
>
> **TRACK A (NON-BLOCKING background, NOT a per-session gate):** a fresh ~3.7-day three-way capture (`python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap`, under `background_process`/`start` if available, else operator-deferred) → EVAL-64 floor probe → **if and only if the floor is met**, build the next unsealed traded-form rung (single-asset `atm_iv`/`term_slope` → directional delta-hedged traded-form net-of-cost; reuse EVAL-64 floor + EVAL-62 mark-path verbatim), else seal `BLOCKED` (never NO-GO). Never block the session on TRACK A (~3.7 days, never in-session).

## VERIFIED STATE (2026-11-21T23:27:19Z)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2322`, `EXPECTED_DIAGNOSTIC_TESTS=27`. EVAL-66..176 are sealed (EVAL-63 never sealed). **EVAL-177 is `DUE` (unsealed) — status-mode driver exits 20 with `needs_execute: ["EVAL-177"]` and `failures: ["seal_gate:EVAL-177:1!=0"]` (expected DUE state).** EVAL-67/68/69 are SEALED (forward disjoint-window ladder complete; threshold `2026-11-20T00:00:00Z` PASSED).

- EVAL-175 sealed successfully: `research_state/EVAL_175_SINGLE_ASSET_TERM_RATIO_FORWARD_VARIANCE_COMBINED_20261121T230325Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH. Single-asset term-structure `term_ratio` → forward realized return variance cell complete.
- EVAL-176 sealed successfully: `research_state/EVAL_176_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_VARIANCE_COMBINED_20261121T231545Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (BTC target 1 pass config, ETH target 0). First cell of the cross-asset surface → forward variance grid.
- EVAL-177 built + wired + DUE: `scripts/eval177_cross_asset_skew_spillover_forward_variance.py` + `scripts/eval177_phaseb_gate.py` + `tests/test_eval177_cross_asset_skew_spillover_forward_variance.py` + `tests/test_eval177_phaseb_gate.py` (18 tests). **`--no-write` on real captures computes `GO CONFIRMED`, floor OK, BOTH targets pass, 5 BH-FDR-rejected configs** (BTC<-ETH skew bar300 h24/h72; ETH<-BTC skew bar60 h72, bar300 h24/h72). Driver tables updated: `TARGETED_TEST_FILES`, `GATE_SPECS` DUE, `SEAL_SPECS` (`expected_exit: 0`), `EXPECTED_TARGETED_TESTS=2322` reconciled via `pytest --collect-only` (2322 collected). **EVAL-177 is the single DUE rung; seal it via the driver, do not hand-run the runner.**
- No sealed EVAL artifact or `src/` modified. Only `scripts/eval67_prethreshold_progress.py` is modified (EVAL-176/177 wiring); EVAL-176/177 scripts+tests are new untracked files. Duplicate EVAL-126 test-artifact churn remains untracked; do not commit it.

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | CLOSED (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67/68/69 | SEALED (`20261120T...`) |
| Physics-independent predictiveness EVAL-70..160 | 91 rungs | SEALED |
| Single-asset surface → forward CVaR | EVAL-161/162/163/164 | SEALED (163 GO CONFIRMED; others NO-GO CONFIRMED (PASS)) |
| Single-asset surface → forward downside-semivariance share | EVAL-115 (atm_iv), 165 (skew), 166 (term_ratio), 167 (term_slope) | SEALED |
| Cross-asset surface/term → forward signed return mean | EVAL-148 (4 cells) | SEALED COMPLETE |
| Cross-asset options order-flow → forward signed return mean / skewness / downside / kurtosis / variance | EVAL-149..160 | SEALED COMPLETE |
| Cross-asset surface/term → forward CVaR | EVAL-168 (atm_iv), 169 (term_slope), 170 (term_ratio), 171 (skew) | SEALED |
| Single-asset surface → forward variance | EVAL-172 (atm_iv), 173 (skew), 174 (term_slope), 175 (term_ratio) | **SEALED (grid COMPLETE)** |
| Cross-asset surface → forward variance | EVAL-176 (atm_iv), EVAL-177 (skew) | **EVAL-176 SEALED (NO-GO); EVAL-177 BUILT + WIRED + DUE (unsealed; computes GO CONFIRMED)** |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — next: `driver --execute` seals EVAL-177 → build next DUE gap → TRACK A background

The order-flow sweep is complete and uniformly NO-GO; the surface-line directional GOs are the only surviving alpha. The single-asset surface distributional grids are complete. The cross-asset → forward-CVaR grid is COMPLETE (168..171, all sealed). **The cross-asset surface → forward-variance grid is in progress: EVAL-176 (atm_iv, NO-GO) sealed; EVAL-177 (skew, GO CONFIRMED) is BUILT + WIRED + DUE.** The terminal deliverable (traded-form net-of-cost) remains data-blocked on the EVAL-64 floor — NOT the per-session heavy work.

1. **EVAL-177 (DUE — mandated next heavy work; `driver --execute` seals it automatically):** run `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2322/2322 targeted, 27/27 diagnostics, `failures: []`, `gate_exit=0`). EVAL-177 seals as `GO CONFIRMED` (both targets pass) — record the GO, do not relax the both-targets bar.
2. **Next gap (same session after seal, never stop at green):** build cross-asset `term_slope` → forward realized return variance (EVAL-178) as a DUE gate, run `driver --execute`, require exit 0. **Term-bar cell:** use `e74._term_bars` for the signal and a term-bar cross-asset alignment (mirror `scripts/eval169_cross_asset_term_slope_spillover_forward_cvar.py` / `eval170_...term_ratio...`), pair with the sealed EVAL-172 `_forward_return_variance` target. The subsequent cell is cross-asset `term_ratio` → forward variance (EVAL-179). Never duplicate a sealed cell.
3. **TRACK A (non-blocking background; NOT a per-session gate):** fresh 3.7-day capture → EVAL-64 floor probe → traded-form rung only if floor met, else `BLOCKED` (never NO-GO). Never block the session on TRACK A.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0). EVAL-70..176 gates: `SEALED`(0) idempotent no-op. **EVAL-177: `DUE`(20) until `driver --execute` seals it; after that `SEALED`(0) idempotent no-op.** `FAILED`(1) fix and rerun.
- Green driver = env OK, `2322/2322` targeted, `27/27` diagnostics, all `EVAL-70..177` gates classified `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Before EVAL-177 is sealed the status-mode driver exits 20 with `needs_execute:["EVAL-177"]` — that is the expected DUE state, not a failure.
- EVAL-177 built+wired (DUE, unsealed): test files in `TARGETED_TEST_FILES`, gate in `GATE_SPECS`, seal in `SEAL_SPECS` (`expected_exit:0`), `EXPECTED_TARGETED_TESTS=2322` (reconciled: 2304 + 18 via `pytest --collect-only`). Do not re-run EVAL-161..176 as a substitute for new work; do not hand-run a runner — let the driver seal it.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling.
2. Competing handoff pointers/copies — removed; this file is the single handoff (do not create copies or edit `AGENTS.md` into a competing queue).
3. "No heavy work left" avoidance — removed; EVAL-177 is wired as DUE, forcing the driver red until executed. When sealed, build the next gap as DUE (EVAL-178 term_slope → forward variance).
4. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
5. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
6. Stale-handoff / timestamp-refresh treadmill — fixed: this handoff reflects TRUE state (EVAL-175/176 sealed; EVAL-177 DUE and computes GO) and points at genuinely-next runnable work. Do not refresh the timestamp without new verified facts.
7. Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time (EVAL-176/177 gate `TASK_ID` = `...22:39:32Z`; artifacts sealed later satisfy it).
8. Degenerate moment fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
9. Half-wired driver — reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green (EVAL-175: 2269→2286; EVAL-176: 2286→2304; EVAL-177: 2304→2322).
10. Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing (EVAL-177 grep-verified: only legitimate `atm_iv`/`e172` cross-references remain).
11. Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax (EVAL-176 NO-GO had only BTC pass; EVAL-177 GO has both).
12. Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`; order-flow via `e62.build_states`. Do not cross them. EVAL-178/179 (term cells) MUST use `e74._term_bars` + term-bar cross-asset alignment.
13. No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
14. Traded-form "data-blocked" misread as "unbuilt" — the per-session heavy work is ALWAYS a runnable predictiveness rung, never the data-blocked traded-form.
15. Duplicate-artifact churn on sealed EVAL-126 — do not re-run EVAL-126, do not commit churn files, never enumerate `research_state/`. The EVAL-126 gate unit test now monkeypatches `execute_phaseb`; do not reintroduce a real `main --execute` call with fake captures.
16. Dict-vs-list iteration in a cloned runner — iterate `.values()` over `{underlying: capture}` dicts; ensure `_campaign_floor` is actually CALLED.
17. Multi-day acquisition not a per-session gate — TRACK A (~3.7 days) cannot finish in one session; non-blocking background only.
18. **"No runnable-now predictiveness rung" avoidance** — the driver is left RED (EVAL-177 DUE) so the next session is forced to execute heavy work.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..176 artifacts or `src/`. Append-only for new authorized work (EVAL-177 DUE — seal via driver).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-168..177 acquire nothing (consume on-disk `data/raw/eval61`).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs; do not use retired compact task IDs.
- Do not switch EVAL-67/68/69 to a disjoint past window.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs. A NEW large capture dir (e.g. `data/raw/eval162cap`, ~100MB+) must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ a real new measurement).

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session. Seals EVAL-177 (DUE, computes GO), then no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2322/2322, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..177 gates SEALED/ok, all seal_gates ok. EXPECTED_TARGETED_TESTS=2322.
#    (Status-mode without --execute exits 20 with needs_execute:["EVAL-177"].)

# 2) Verify sealed campaigns idempotently:
python3 scripts/eval175_phaseb_gate.py   # EVAL-175 SEALED, exit 0
python3 scripts/eval176_phaseb_gate.py   # EVAL-176 SEALED, exit 0
python3 scripts/eval177_phaseb_gate.py   # EVAL-177 DUE until --execute seals it (exit 20)

# 3) EVAL-64 feasible-floor probe across all on-disk captures:
PYTHONPATH=$PWD/.venv-deps python3 - <<'PY'
import json, glob, os, sys; sys.path.insert(0, ".")
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
for f in sorted(glob.glob("data/raw/eval*/three_way_*.json")):
    r = e64._underlying_floor_strict(json.load(open(f)))
    failed = [k for k,v in r["checks"].items() if not v]
    print(os.path.basename(f), "ok=", r["ok"], "FAILED=", failed)
PY

# 4) TRACK A (NON-BLOCKING background; ~3.7 days wall-clock; do NOT block the session):
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap
#    if floor met -> build traded-form rung; else seal BLOCKED.

# 5) Anti-avoidance: green driver + all-sealed is NOT completion. Build the next DUE rung.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..176 sealed. **EVAL-177 is BUILT + WIRED + DUE (intentionally UNSEALED — the next `driver --execute` seals it; it computes `GO CONFIRMED`).** EVAL-63 never sealed.