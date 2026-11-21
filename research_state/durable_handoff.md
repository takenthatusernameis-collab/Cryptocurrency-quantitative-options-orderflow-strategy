# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-21T22:38:43Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. The order-flow distributional sweep is complete and uniformly NO-GO CONFIRMED (PASS). The surviving directional alpha is on the **surface** line. The single-asset surface distributional grids are complete for signed-return-mean / skewness / kurtosis / CVaR / downside-semivariance share. The cross-asset order-flow distributional sweep is complete. The cross-asset surface/term → forward-CVaR grid is complete (EVAL-168 atm_iv, 169 term_slope, 170 term_ratio, 171 skew; all sealed).
>
> **CURRENT MANDATED QUEUE:** EVAL-172 (single-asset `atm_iv` → forward realized return variance) is **SEALED** (`20261121T211458Z`, `NO-GO CONFIRMED (PASS)`, floor OK). EVAL-173 (single-asset `skew` → forward realized return variance) is **SEALED** (`20261121T220207Z`, `NO-GO CONFIRMED (PASS)`, floor OK). EVAL-174 (single-asset `term_slope` → forward realized return variance) is **SEALED** (`20261121T221926Z`, floor OK). **EVAL-175 (single-asset `term_ratio` → forward realized return variance) is BUILT + WIRED + DUE (unsealed).** The driver is intentionally RED in status mode: exit 20, `needs_execute: ["EVAL-175"]`. The next session must run the driver with `--execute` to seal EVAL-175, then build the next unsealed heavy rung in the same session.
>
> **DECISIVE BOTTLENECK REMOVED — there is ALWAYS runnable-now heavy work.** EVAL-175 is wired into `scripts/eval67_prethreshold_progress.py` (`TARGETED_TEST_FILES`, `GATE_SPECS`, `SEAL_SPECS`) and its expected targeted count is reconciled to **2286**. A green status-mode driver is not completion; after sealing EVAL-175, identify the next genuine gap from the sealed space and build it as a DUE gate. Natural next cells: cross-asset surface/term → forward realized return variance (e.g. cross-asset `atm_iv`/`skew`/`term_slope`/`term_ratio` → forward variance) or single-asset `term_ratio` variants already covered — do not duplicate a sealed cell.
>
> **FIRST ACTION, NON-NEGOTIABLE, EVERY SESSION:**
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
> This should seal EVAL-175 (EVAL-172/173/174 are already sealed), then be an idempotent no-op after the seal. Require after the seal: `targeted_tests: 2286/2286`, `diagnostic_tests: 27/27`, all `EVAL-70..175` gates classified `ok`/phase `SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. If EVAL-175 is still DUE after `--execute`, the run FAILED — investigate; do not hand-wave.
>
> **THEN build the next runnable-now rung in the SAME session (never stop at "driver green"):** identify the next genuine gap from the sealed space (never duplicate a sealed cell) and build it as a DUE gate (runner + gate + 2 test files + driver `TARGETED_TEST_FILES`/`GATE_SPECS`/`SEAL_SPECS` + bump `EXPECTED_TARGETED_TESTS` by the verified `pytest --collect-only` delta), run the driver `--execute` to seal, require exit 0. Do not re-run, re-litigate, or re-seal sealed EVAL-02..62, EVAL-64..66, EVAL-70..174 artifacts or `src/`.
>
> **TRACK A (NON-BLOCKING background, NOT a per-session gate):** a fresh ~3.7-day three-way capture (`python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap`, under `background_process`/`start` if available, else operator-deferred) → EVAL-64 floor probe → **if and only if the floor is met**, build the next unsealed traded-form rung (single-asset `atm_iv`/`term_slope` → directional delta-hedged traded-form net-of-cost; reuse EVAL-64 floor + EVAL-62 mark-path verbatim), else seal `BLOCKED` (never NO-GO). Never block the session on TRACK A (~3.7 days, never in-session).

## VERIFIED STATE (2026-11-21T22:38:43Z)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2286`, `EXPECTED_DIAGNOSTIC_TESTS=27`. EVAL-66..174 are sealed (EVAL-63 never sealed). **EVAL-175 is `DUE` (unsealed) — status-mode driver exits 20 with `needs_execute: ["EVAL-175"]`.** EVAL-67/68/69 are SEALED (forward disjoint-window ladder complete; threshold `2026-11-20T00:00:00Z` PASSED).

- EVAL-172 sealed successfully: `research_state/EVAL_172_SINGLE_ASSET_ATM_IV_FORWARD_VARIANCE_COMBINED_20261121T211458Z.json/.md` and preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH. Pooled all-underlyings pass: `false`.
- EVAL-173 sealed successfully: `research_state/EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_COMBINED_*.json/.md` and preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH. Pooled all-underlyings pass: `false`.
- EVAL-174 sealed successfully: `research_state/EVAL_174_SINGLE_ASSET_TERM_SLOPE_FORWARD_VARIANCE_COMBINED_20261121T221926Z.json/.md` and preregistration; floor OK for BTC and ETH. Single-asset term-structure `term_slope` → forward realized return variance cell complete.
- EVAL-175 built + wired + DUE: `scripts/eval175_single_asset_term_ratio_forward_variance.py` + `scripts/eval175_phaseb_gate.py` + `tests/test_eval175_single_asset_term_ratio_forward_variance.py` + `tests/test_eval175_phaseb_gate.py` (17 tests). Driver tables updated: `TARGETED_TEST_FILES`, `GATE_SPECS` DUE, `SEAL_SPECS` (`expected_exit: 0`), `EXPECTED_TARGETED_TESTS=2286` reconciled via `pytest --collect-only` (2286 collected).
- No sealed EVAL artifact or `src/` modified. Untracked EVAL-172/173/174 artifacts are from the already-completed heavy driver runs. Duplicate EVAL-126 test-artifact churn remains untracked; do not commit it. `tests/test_eval126_phaseb_gate.py` was fixed to monkeypatch `execute_phaseb` so the unit test no longer invokes the real runner with fake captures.

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
| Single-asset surface → forward variance | EVAL-172 (atm_iv), EVAL-173 (skew) | **BOTH SEALED** |
| Single-asset term-structure → forward variance | EVAL-174 (term_slope), EVAL-175 (term_ratio) | **EVAL-174 SEALED; EVAL-175 BUILT + WIRED + DUE (unsealed)** |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — next: `driver --execute` seals EVAL-175 → build next DUE gap → TRACK A background

The order-flow sweep is complete and uniformly NO-GO; the surface-line directional GOs are the only surviving alpha. The single-asset surface distributional grids are complete. The cross-asset → forward-CVaR grid is COMPLETE (atm_iv 168 + term_slope 169 + term_ratio 170 + skew 171, all sealed). **EVAL-172/173 are SEALED; EVAL-174 is SEALED; EVAL-175 is BUILT + WIRED + DUE.** The terminal deliverable (traded-form net-of-cost) remains data-blocked on the EVAL-64 floor — NOT the per-session heavy work.

1. **EVAL-175 (DUE — mandated next heavy work; `driver --execute` seals it automatically):** run `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2286/2286 targeted, 27/27 diagnostics, `failures: []`, `gate_exit=0`).
2. **Next gap (same session after seal, never stop at green):** identify the next genuine unsealed cell from the sealed space (do not duplicate a sealed cell), build it as a DUE gate, run `driver --execute`, require exit 0. Natural next cells: cross-asset surface/term → forward realized return variance (cross-asset `atm_iv`/`skew`/`term_slope`/`term_ratio` → forward variance).
3. **TRACK A (non-blocking background; NOT a per-session gate):** fresh 3.7-day capture → EVAL-64 floor probe → traded-form rung only if floor met, else `BLOCKED` (never NO-GO). Never block the session on TRACK A.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0). EVAL-70..174 gates: `SEALED`(0) idempotent no-op. **EVAL-175: `DUE`(20) until `driver --execute` seals it; after that `SEALED`(0) idempotent no-op.** `FAILED`(1) fix and rerun.
- Green driver = env OK, `2286/2286` targeted, `27/27` diagnostics, all `EVAL-70..175` gates classified `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Before EVAL-175 is sealed the status-mode driver exits 20 with `needs_execute:["EVAL-175"]` — that is the expected DUE state, not a failure.
- EVAL-175 built+wired (DUE, unsealed): test files in `TARGETED_TEST_FILES`, gate in `GATE_SPECS`, seal in `SEAL_SPECS` (`expected_exit:0`), `EXPECTED_TARGETED_TESTS=2286` (reconciled: 2269 + 17 via `pytest --collect-only`). Do not re-run EVAL-161..174 as a substitute for new work; do not hand-run a runner — let the driver seal it.

## BOTTLENECKS REMOVED / DO NOT REDISCOVER

1. Zombie capture bridge / liveness churn — removed; cron owns polling.
2. Competing handoff pointers/copies — removed; this file is the single handoff (do not create copies or edit `AGENTS.md` into a competing queue).
3. "No heavy work left" avoidance — removed; EVAL-175 is wired as DUE, forcing the driver red until executed. When sealed, build the next gap as DUE.
4. Manual pre-threshold loop / timestamp-only carry — removed by `scripts/eval67_prethreshold_progress.py`.
5. Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
6. Stale-handoff / timestamp-refresh treadmill — fixed: this handoff reflects TRUE state (EVAL-172/173/174 sealed; EVAL-175 DUE) and points at genuinely-next runnable work. Do not refresh the timestamp without new verified facts.
7. Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
8. Degenerate moment fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
9. Half-wired driver — reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green (EVAL-175: 2269→2286).
10. Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
11. Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
12. Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`; order-flow via `e62.build_states`. Do not cross them.
13. No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
14. Traded-form "data-blocked" misread as "unbuilt" — the per-session heavy work is ALWAYS a runnable predictiveness rung, never the data-blocked traded-form.
15. Duplicate-artifact churn on sealed EVAL-126 — do not re-run EVAL-126, do not commit churn files, never enumerate `research_state/`. The EVAL-126 gate unit test now monkeypatches `execute_phaseb`; do not reintroduce a real `main --execute` call with fake captures.
16. Dict-vs-list iteration in a cloned runner — iterate `.values()` over `{underlying: capture}` dicts; ensure `_campaign_floor` is actually CALLED.
17. Multi-day acquisition not a per-session gate — TRACK A (~3.7 days) cannot finish in one session; non-blocking background only.
18. **"No runnable-now predictiveness rung" avoidance** — the driver is left RED (EVAL-175 DUE) so the next session is forced to execute heavy work.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..174 artifacts or `src/`. Append-only for new authorized work (EVAL-175 DUE — seal via driver).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-168..175 acquire nothing (consume on-disk `data/raw/eval61`).
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

# 1) Full heavy-work loop; run every session. Seals EVAL-175 (DUE), then no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2286/2286, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..175 gates SEALED/ok, all seal_gates ok. EXPECTED_TARGETED_TESTS=2286.
#    (Status-mode without --execute exits 20 with needs_execute:["EVAL-175"].)

# 2) Verify a sealed campaign idempotently:
python3 scripts/eval172_phaseb_gate.py   # EVAL-172 SEALED, exit 0
python3 scripts/eval173_phaseb_gate.py   # EVAL-173 SEALED, exit 0
python3 scripts/eval174_phaseb_gate.py   # EVAL-174 SEALED, exit 0
python3 scripts/eval175_phaseb_gate.py   # EVAL-175 DUE until --execute seals it (exit 20)

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

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..174 sealed. **EVAL-175 is BUILT + WIRED + DUE (intentionally UNSEALED — the next `driver --execute` seals it).** EVAL-63 never sealed.
