# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-22T00:11:32Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. The order-flow distributional sweep is complete and uniformly NO-GO CONFIRMED (PASS). The surviving directional alpha is on the **surface** line. The single-asset surface distributional grids are complete (signed-return-mean / skewness / kurtosis / CVaR / downside-semivariance share / **variance**). The cross-asset order-flow sweep is complete. The cross-asset surface/term → forward-CVaR grid is complete (EVAL-168 atm_iv, 169 term_slope, 170 term_ratio, 171 skew; all sealed). **The cross-asset surface/term → forward variance grid is now COMPLETE: EVAL-176 (atm_iv, NO-GO) sealed; EVAL-177 (skew, GO CONFIRMED) sealed; EVAL-178 (term_slope) sealed; EVAL-179 (term_ratio) sealed — all four cells sealed via `driver --execute`.**
>
> **CURRENT MANDATED QUEUE:** EVAL-172 (single-asset `atm_iv` → forward variance), EVAL-173 (`skew`), EVAL-174 (`term_slope`), EVAL-175 (`term_ratio`) are **SEALED** (single-asset surface → forward variance grid COMPLETE). EVAL-176 (cross-asset `atm_iv` → forward variance) is **SEALED** (`20261121T231545Z`, `NO-GO CONFIRMED (PASS)`, floor OK). EVAL-177 (cross-asset `skew` → forward variance) is **SEALED** (`GO CONFIRMED`, both targets pass, 5 BH-FDR-rejected configs). **EVAL-178 (cross-asset `term_slope` → forward realized return variance) is SEALED; EVAL-179 (cross-asset `term_ratio` → forward realized return variance) is SEALED.** The driver is GREEN in status mode: exit 0, `2358/2358` targeted, `27/27` diagnostics, `failures: []`, `gate_exit=0`, all `EVAL-70..179` gates classified `ok`/`SEALED`. A green driver is **not** completion — the next session must identify the next genuine gap from the sealed space and build it as a DUE gate, or advance TRACK A.
>
> **DECISIVE BOTTLENECK REMOVED — there is ALWAYS runnable-now heavy work.** EVAL-177/178/179 are wired into `scripts/eval67_prethreshold_progress.py` (`TARGETED_TEST_FILES`, `GATE_SPECS`, `SEAL_SPECS`) and reconciled to **2358** targeted tests. The cross-asset surface/term → forward variance grid is complete; the next surface → forward variance cells do not exist. Natural next directions: (a) extend the grid into a new moment/target dimension (e.g. forward realized return skewness/kurtosis/CVaR for cross-asset term signals), or (b) advance TRACK A to the traded-form rung. Do not duplicate a sealed cell. No blocked sessions; no bottlenecks — driver green idempotent no-op.
>
> **NEXT FOCUS CAMPAIGN (next genuine gap — future agents cannot avoid this heavy work):** TRACK A — fresh ~3.7-day three-way capture (`python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap`, background/operator-deferred, ~3.7 days, never in-session) → EVAL-64 floor probe → **if and only if the floor is met**, build the next unsealed traded-form rung (single-asset `atm_iv`/`term_slope` → directional delta-hedged traded-form net-of-cost; reuse EVAL-64 floor + EVAL-62 mark-path verbatim), else seal `BLOCKED` (never NO-GO). This is the only remaining path to the terminal deliverable; the predictiveness ladder is fully sealed and cannot substitute for new work.
>
>
> **FIRST ACTION, NON-NEGOTIABLE, EVERY SESSION:**
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
> Require: `targeted_tests: 2358/2358`, `diagnostic_tests: 27/27`, all `EVAL-70..179` gates classified `ok`/phase `SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. If the driver is not green, the session failed — investigate; do not hand-wave.
>
> **THEN build the next runnable-now rung in the SAME session (never stop at "driver green"):** identify the next genuine gap from the sealed space (never duplicate a sealed cell) and build it as a DUE gate (runner + gate + 2 test files + driver `TARGETED_TEST_FILES`/`GATE_SPECS`/`SEAL_SPECS` + bump `EXPECTED_TARGETED_TESTS` by the verified `pytest --collect-only` delta), run the driver `--execute` to seal, require exit 0. Do not re-run, re-litigate, or re-seal sealed EVAL-02..62, EVAL-64..66, EVAL-70..179 artifacts or `src/`.
>
> **TRACK A (NON-BLOCKING background, NOT a per-session gate):** a fresh ~3.7-day three-way capture (`python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap`, under `background_process`/`start` if available, else operator-deferred) → EVAL-64 floor probe → **if and only if the floor is met**, build the next unsealed traded-form rung (single-asset `atm_iv`/`term_slope` → directional delta-hedged traded-form net-of-cost; reuse EVAL-64 floor + EVAL-62 mark-path verbatim), else seal `BLOCKED` (never NO-GO). Never block the session on TRACK A (~3.7 days, never in-session).

## VERIFIED STATE (2026-11-22T00:10:36Z)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2358`, `EXPECTED_DIAGNOSTIC_TESTS=27`. EVAL-66..179 are sealed (EVAL-63 never sealed). **All gates `ok`/phase `SEALED`; driver exit 0; idempotent no-op.** EVAL-67/68/69 are SEALED (forward disjoint-window ladder complete; threshold `2026-11-20T00:00:00Z` PASSED).

- EVAL-175 sealed successfully: `research_state/EVAL_175_SINGLE_ASSET_TERM_RATIO_FORWARD_VARIANCE_COMBINED_20261121T230325Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH. Single-asset term-structure `term_ratio` → forward realized return variance cell complete.
- EVAL-176 sealed successfully: `research_state/EVAL_176_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_VARIANCE_COMBINED_20261121T231545Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (BTC target 1 pass config, ETH target 0). First cell of the cross-asset surface → forward variance grid.
- EVAL-177 sealed successfully: `research_state/EVAL_177_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_VARIANCE_COMBINED_*.json/.md` + preregistration; verdict `GO CONFIRMED`, floor OK, BOTH targets pass (BTC<-ETH skew bar300 h24/h72; ETH<-BTC skew bar60 h72, bar300 h24/h72), 5 BH-FDR-rejected configs. Cross-asset `skew` → forward variance cell complete.
- EVAL-178 sealed successfully: `scripts/eval178_cross_asset_term_slope_spillover_forward_variance.py` + `scripts/eval178_phaseb_gate.py` + `tests/test_eval178_cross_asset_term_slope_spillover_forward_variance.py` + `tests/test_eval178_phaseb_gate.py` (18 tests). Cross-asset `term_slope` → forward variance cell sealed via `driver --execute`. Term-bar cell (`e74._term_bars`, NOT `e71.build_surface_bars`) with cross-asset alignment.
- EVAL-179 sealed successfully: `scripts/eval179_cross_asset_term_ratio_spillover_forward_variance.py` + `scripts/eval179_phaseb_gate.py` + `tests/test_eval179_cross_asset_term_ratio_spillover_forward_variance.py` + `tests/test_eval179_phaseb_gate.py` (18 tests). Cross-asset `term_ratio` → forward variance cell sealed via `driver --execute`. Term-bar cell (`e74._term_bars`, NOT `e71.build_surface_bars`) with cross-asset alignment.
- Driver tables updated: `TARGETED_TEST_FILES` (+4 files, +36 tests → 2358), `GATE_SPECS` (+EVAL-178, EVAL-179), `SEAL_SPECS` (+EVAL-178, EVAL-179), `EXPECTED_TARGETED_TESTS=2358` reconciled via `pytest --collect-only`.
- No sealed EVAL artifact or `src/` modified. Only `scripts/eval67_prethreshold_progress.py` is modified (EVAL-178/179 wiring); EVAL-178/179 scripts+tests are new untracked files. Duplicate EVAL-126 test-artifact churn remains untracked; do not commit it.

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
| Cross-asset surface → forward variance | EVAL-176 (atm_iv), 177 (skew), 178 (term_slope), 179 (term_ratio) | **SEALED COMPLETE** (176 NO-GO; 177/178/179 sealed via driver) |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — next: identify next gap from sealed space → build as DUE gate → TRACK A background

The order-flow sweep is complete and uniformly NO-GO; the surface-line directional GOs are the only surviving alpha. The single-asset surface distributional grids are complete. The cross-asset surface/term → forward-CVaR grid is COMPLETE (168..171, all sealed). **The cross-asset surface/term → forward-variance grid is now COMPLETE (176..179, all sealed).** The terminal deliverable (traded-form net-of-cost) remains data-blocked on the EVAL-64 floor — NOT the per-session heavy work.

1. **Driver green check (every session):** run `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2358/2358 targeted, 27/27 diagnostics, `failures: []`, `gate_exit=0`). All EVAL-70..179 gates SEALED.
2. **Next gap (same session after green, never stop at green):** all predictiveness cells (EVAL-70..179) are complete — no new predictiveness cell exists without duplicating a sealed cell, so this step yields no new rung. The genuine next gap is TRACK A (step 3): build/run the fresh ~3.7-day three-way capture → EVAL-64 floor probe → traded-form rung only if the floor is met, else seal `BLOCKED` (never NO-GO).
3. **TRACK A (non-blocking background; NOT a per-session gate):** fresh 3.7-day capture → EVAL-64 floor probe → traded-form rung only if floor met, else `BLOCKED` (never NO-GO). Never block the session on TRACK A.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0). EVAL-70..179 gates: `SEALED`(0) idempotent no-op. `FAILED`(1) fix and rerun.
- Green driver = env OK, `2358/2358` targeted, `27/27` diagnostics, all `EVAL-70..179` gates classified `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Green driver + all-sealed is **NOT** session completion — build the next DUE rung.
- EVAL-177/178/179 built+wired+sealed: test files in `TARGETED_TEST_FILES`, gates in `GATE_SPECS`, seals in `SEAL_SPECS` (`expected_exit:0`), `EXPECTED_TARGETED_TESTS=2358` (reconciled: 2322 + 36 via `pytest --collect-only`). Do not re-run EVAL-161..176 as a substitute for new work; do not hand-run a runner — let the driver seal it.
- Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
- Stale-handoff / timestamp-refresh treadmill — fixed: this handoff reflects TRUE state (EVAL-177/178/179 sealed; driver green at 2358/2358) and points at genuinely-next runnable work. Do not refresh the timestamp without new verified facts.
- Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
- Half-wired driver — reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green (EVAL-177: 2304→2322; EVAL-178/179: 2322→2358).
- Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
- Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
- Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`; order-flow via `e62.build_states`. Do not cross them.
- No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
- Traded-form "data-blocked" misread as "unbuilt" — the per-session heavy work is ALWAYS a runnable predictiveness rung, never the data-blocked traded-form.
- Duplicate-artifact churn on sealed EVAL-126 — do not re-run EVAL-126, do not commit churn files, never enumerate `research_state/`. The EVAL-126 gate unit test now monkeypatches `execute_phaseb`; do not reintroduce a real `main --execute` call with fake captures.
- Dict-vs-list iteration in a cloned runner — iterate `.values()` over `{underlying: capture}` dicts; ensure `_campaign_floor` is actually CALLED.
- Multi-day acquisition not a per-session gate — TRACK A (~3.7 days) cannot finish in one session; non-blocking background only.
- **"No runnable-now predictiveness rung" avoidance** — the driver is left GREEN (all sealed) so the next session must either build a new DUE gap or advance TRACK A; neither is optional.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..179 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-168..179 acquire nothing (consume on-disk `data/raw/eval61`).
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

# 1) Full heavy-work loop; run every session. All EVAL-177/178/179 sealed, idempotent no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2358/2358, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..179 gates SEALED/ok, all seal_gates ok. EXPECTED_TARGETED_TESTS=2358.

# 2) Verify sealed campaigns idempotently:
python3 scripts/eval175_phaseb_gate.py   # EVAL-175 SEALED, exit 0
python3 scripts/eval176_phaseb_gate.py   # EVAL-176 SEALED, exit 0
python3 scripts/eval177_phaseb_gate.py   # EVAL-177 SEALED, exit 0
python3 scripts/eval178_phaseb_gate.py   # EVAL-178 SEALED, exit 0
python3 scripts/eval179_phaseb_gate.py   # EVAL-179 SEALED, exit 0

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

EVAL-02..62, 64..179 sealed. **EVAL-63 never sealed.** EVAL-177 (skew → forward variance, GO CONFIRMED), EVAL-178 (term_slope → forward variance), EVAL-179 (term_ratio → forward variance) all sealed via `driver --execute`; cross-asset surface/term → forward variance grid COMPLETE.
