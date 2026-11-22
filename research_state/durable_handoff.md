# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-22T01:38:46Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. The order-flow distributional sweep is complete and uniformly NO-GO CONFIRMED (PASS). The single-asset surface distributional grids are complete. The cross-asset surface/term distributional grids are complete through forward variance (EVAL-176 atm_iv, 177 skew, 178 term_slope, 179 term_ratio). **EVAL-180 is SEALED:** cross-asset order-flow imbalance × atm_iv interaction spillover → forward realized return variance, `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH, artifact stamp `20261122T011312Z`. **EVAL-181 is SEALED:** cross-asset order-flow imbalance × atm_iv interaction spillover → forward CVaR, `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 imbalance states and 289 surface bars each; 274 aligned common bars), artifact stamp `20261122T012720Z`. The only surviving directional/tail alpha remains on the **surface** line; the next unsealed work must stay on-charter and runnable on the existing real captures.
>
> **CURRENT MANDATED QUEUE:** EVAL-172..179 are **SEALED** (single-asset and cross-asset surface/term → forward variance grids COMPLETE). **EVAL-180 is SEALED** (`NO-GO CONFIRMED (PASS)`, both floors OK, 12 configs, 0 BH-FDR rejections). **EVAL-181 is SEALED** (`NO-GO CONFIRMED (PASS)`, both floors OK, 12 configs, 0 BH-FDR rejections). **EVAL-182 is the single DUE unsealed campaign and is the next focus campaign: cross-asset order-flow **toxicity** × atm_iv interaction spillover → forward variance.** It is a genuinely distinct cell: EVAL-180 measured the *imbalance* interaction against variance; EVAL-159/160 measured order-flow *toxicity* and *imbalance* alone against variance; no *toxicity* interaction → variance cell exists. Build and seal EVAL-182 in the SAME session; do not re-run, re-litigate, or re-seal EVAL-02..62, EVAL-64..66, or EVAL-70..181 artifacts or `src/`.
>
> **BOTTLENECK REMOVED — there is ALWAYS runnable-now heavy work.** EVAL-181 is wired into `scripts/eval67_prethreshold_progress.py` (`TARGETED_TEST_FILES`, `GATE_SPECS`, `SEAL_SPECS`) and the driver is GREEN at **2394/2394 targeted tests**, **27/27 diagnostics**, `failures: []`, `gate_exit=0`, all `EVAL-70..181` gates `ok`/`SEALED`. A green driver plus all-sealed is **not** completion. The next session must build EVAL-182 as a DUE gate, or it has failed the handoff.
>
> **NEXT FOCUS CAMPAIGN (EVAL-182 — DUE, runnable now, heavy):**
> * **Signal:** the OTHER underlying's causal per-bar order-flow **toxicity** z × near-ATM `atm_iv` z, reconstructed exactly as EVAL-180 (`e62.build_states(tox_signal="toxicity")` × `e71.build_surface_bars().atm_iv`, common BTC-vs-ETH bar grid, causal forward-fill, expanding z-score with `e62.ZWINDOW`).
> * **Target:** forward **variance** of the TARGET underlying's next H perp log returns, transcribed verbatim from sealed EVAL-176 (`_forward_variance` via EVAL-62 `_forward_var`).
> * **Grid:** both target underlyings `{BTC, ETH}` × bar grids `{60s, 300s}` × forward horizons `{6, 24, 72}` bars; directional permutation H1 `IC > 0`, block bootstrap 95% CI lower `> 0`, pooled BH-FDR at `e62.FDR_ALPHA`, `MIN_USABLE_PAIRS_PER_CONFIG` and the EVAL-180 composed floor verbatim.
> * **GO bar:** both BTC and ETH must have at least one config with `IC > 0`, directional permutation `p < 0.05`, block-bootstrap 95% CI lower `> 0`, and a pooled BH-FDR rejection; else `NO-GO CONFIRMED (PASS)`. Below floor ⇒ `BLOCKED`, never NO-GO.
> * **Build contract:** add `scripts/eval182_cross_asset_oflow_tox_atm_iv_interaction_spillover_forward_variance.py` + `scripts/eval182_phaseb_gate.py` + two test files; add them to `TARGETED_TEST_FILES`, `GATE_SPECS`, and `SEAL_SPECS`; bump `EXPECTED_TARGETED_TESTS` by the verified `pytest --collect-only` delta (expect +18: 12 runner + 6 gate, but verify); run `python3 scripts/eval67_prethreshold_progress.py --execute` and require exit 0 with the new gate `SEALED`.
> * **After EVAL-182:** the next unsealed queue is EVAL-183 (cross-asset order-flow **toxicity** × atm_iv interaction → forward CVaR), then TRACK A. Do not skip EVAL-182 and do not substitute a sealed rung.
>
> **FIRST ACTION, NON-NEGOTIABLE, EVERY SESSION:**
> ```bash
> python3 scripts/eval67_prethreshold_progress.py --execute
> ```
> Require: `targeted_tests: 2394/2394`, `diagnostic_tests: 27/27`, all `EVAL-70..181` gates classified `ok`/phase `SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. If the driver is not green, the session failed — investigate; do not hand-wave.
>
> **THEN build the next runnable-now rung in the SAME session (never stop at "driver green"):** build EVAL-182 to the contract above, run the driver `--execute` to seal, require exit 0. Do not re-run, re-litigate, or re-seal sealed EVAL-02..62, EVAL-64..66, EVAL-70..181 artifacts or `src/`.
>
> **TRACK A (NON-BLOCKING background, NOT a per-session gate):** a fresh ~3.7-day three-way capture (`python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --out-dir data/raw/eval162cap`, under `background_process`/`start` if available, else operator-deferred) → EVAL-64 floor probe → **if and only if the floor is met**, build the next unsealed traded-form rung (single-asset `atm_iv`/`term_slope` → directional delta-hedged traded-form net-of-cost; reuse EVAL-64 floor + EVAL-62 mark-path verbatim), else seal `BLOCKED` (never NO-GO). Never block the session on TRACK A (~3.7 days, never in-session).

## VERIFIED STATE (2026-11-22T01:38:46Z)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2394`, `EXPECTED_DIAGNOSTIC_TESTS=27`. EVAL-66..181 are sealed (EVAL-63 never sealed). **All gates `ok`/phase `SEALED`; driver exit 0; idempotent no-op.** EVAL-67/68/69 are SEALED (forward disjoint-window ladder complete; threshold `2026-11-20T00:00:00Z` PASSED).

- EVAL-180 sealed successfully: `research_state/EVAL_180_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_COMBINED_20261122T011312Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 imbalance states and 289 surface bars each; 274 aligned common bars). Best IC: BTC 0.1331 (`ETH->BTC::oflow_atm_iv_interaction::bar60.0::h6`), ETH 0.1326 (`BTC->ETH::oflow_atm_iv_interaction::bar60.0::h24`); 0 pass configs; 12 configs; no BH-FDR rejections. Cross-asset order-flow × surface interaction → forward variance cell complete.
- EVAL-181 sealed successfully: `research_state/EVAL_181_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_CVAR_COMBINED_20261122T012720Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 imbalance states and 289 surface bars each; 274 aligned common bars). Best IC: BTC -0.0163 (`ETH->BTC::oflow_atm_iv_interaction::bar300.0::h6`), ETH 0.0051 (`BTC->ETH::oflow_atm_iv_interaction::bar300.0::h6`); 0 pass configs; 12 configs; no BH-FDR rejections. Cross-asset order-flow imbalance × atm_iv interaction → forward CVaR cell complete.
- EVAL-180/181 scripts/tests are new untracked files (8 files, 36 tests total). Driver tables updated: `TARGETED_TEST_FILES` (+4 files, +36 tests → 2394), `GATE_SPECS` (+EVAL-180, +EVAL-181), `SEAL_SPECS` (+EVAL-180, +EVAL-181), `EXPECTED_TARGETED_TESTS=2394` reconciled via the full driver run.
- No sealed EVAL artifact or `src/` modified. Only `scripts/eval67_prethreshold_progress.py` is modified (EVAL-180/181 wiring); EVAL-180/181 scripts/tests/artifacts are new. Duplicate EVAL-126 test-artifact churn remains untracked; do not commit it.

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
| Single-asset surface → forward variance | EVAL-172 (atm_iv), 173 (skew), 174 (term_slope), 175 (term_ratio) | SEALED (grid COMPLETE) |
| Cross-asset surface → forward variance | EVAL-176 (atm_iv), 177 (skew), 178 (term_slope), 179 (term_ratio) | SEALED COMPLETE (176 NO-GO; 177 GO; 178/179 NO-GO) |
| Cross-asset order-flow × surface interaction → forward variance | EVAL-180 (imbalance × atm_iv) | **SEALED** (`NO-GO CONFIRMED (PASS)`, `20261122T011312Z`) |
| Cross-asset order-flow × surface interaction → forward CVaR | EVAL-181 (imbalance × atm_iv) | **SEALED** (`NO-GO CONFIRMED (PASS)`, `20261122T012720Z`) |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — next: EVAL-182 (DUE) → TRACK A background

The order-flow distributional sweep is complete and uniformly NO-GO; the surface-line directional/tail GOs are the only surviving alpha. EVAL-180 confirms the first order-flow × surface interaction cell (imbalance × atm_iv) is also NO-GO for variance. EVAL-181 confirms the same interaction against forward CVaR is also NO-GO. **EVAL-182 is the next genuine gap:** the *toxicity* × atm_iv interaction against forward variance, reusing EVAL-180's signal path and EVAL-159/160's toxicity signal verbatim. The terminal deliverable (traded-form net-of-cost) remains data-blocked on the EVAL-64 floor — NOT the per-session heavy work.

1. **Driver green check (every session):** run `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2394/2394 targeted, 27/27 diagnostics, `failures: []`, `gate_exit=0`). All EVAL-70..181 gates SEALED.
2. **EVAL-182 (DUE, same session, never stop at green):** build the toxicity × atm_iv interaction → forward variance runner + gate + 2 test files + driver tables; run driver `--execute`; require the new gate SEALED and exit 0. Do not substitute EVAL-183 or a sealed rung.
3. **TRACK A (non-blocking background; NOT a per-session gate):** fresh 3.7-day capture → EVAL-64 floor probe → traded-form rung only if floor met, else `BLOCKED` (never NO-GO). Never block the session on TRACK A.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0). EVAL-70..181 gates: `SEALED`(0) idempotent no-op. `FAILED`(1) fix and rerun.
- Green driver = env OK, `2394/2394` targeted, `27/27` diagnostics, all `EVAL-70..181` gates classified `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Green driver + all-sealed is **NOT** session completion — build EVAL-182.
- EVAL-180/181 built+wired+sealed: test files in `TARGETED_TEST_FILES`, gate in `GATE_SPECS`, seal in `SEAL_SPECS` (`expected_exit:0`), `EXPECTED_TARGETED_TESTS=2394` (2376 + 18 via the full driver run). Do not re-run EVAL-161..181 as a substitute for new work; do not hand-run a runner — let the driver seal EVAL-182.
- Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
- Stale-handoff / timestamp-refresh treadmill — fixed: this handoff reflects TRUE state (EVAL-180/181 sealed; driver green at 2394/2394) and points at genuinely-next runnable work (EVAL-182). Do not refresh the timestamp without new verified facts.
- Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment/tail fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
- Half-wired driver — reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green (EVAL-180: 2358→2376, EVAL-181: 2376→2394).
- Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
- Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
- Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`; order-flow via `e62.build_states`; EVAL-182 composes `e62.build_states(tox_signal="toxicity")` × `e71.build_surface_bars`. Do not cross them.
- No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
- Traded-form "data-blocked" misread as "unbuilt" — the per-session heavy work is ALWAYS a runnable predictiveness/interaction rung, never the data-blocked traded-form.
- Duplicate-artifact churn on sealed EVAL-126 — do not re-run EVAL-126, do not commit churn files, never enumerate `research_state/`. The EVAL-126 gate unit test now monkeypatches `execute_phaseb`; do not reintroduce a real `main --execute` call with fake captures.
- Dict-vs-list iteration in a cloned runner — iterate `.values()` over `{underlying: capture}` dicts; ensure `_campaign_floor`/`campaign_floor` is actually CALLED.
- Multi-day acquisition not a per-session gate — TRACK A (~3.7 days) cannot finish in one session; non-blocking background only.
- **"No runnable-now predictiveness rung" avoidance** — the driver is left GREEN (all sealed through EVAL-181) so the next session must build EVAL-182; this is not optional.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..181 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-168..182 acquire nothing (consume on-disk `data/raw/eval61`).
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

# 1) Full heavy-work loop; run every session. All EVAL-181 sealed, idempotent no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2394/2394, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..181 gates SEALED/ok, all seal_gates ok. EXPECTED_TARGETED_TESTS=2394.

# 2) Verify sealed campaigns idempotently:
python3 scripts/eval175_phaseb_gate.py   # EVAL-175 SEALED, exit 0
python3 scripts/eval176_phaseb_gate.py   # EVAL-176 SEALED, exit 0
python3 scripts/eval177_phaseb_gate.py   # EVAL-177 SEALED, exit 0
python3 scripts/eval178_phaseb_gate.py   # EVAL-178 SEALED, exit 0
python3 scripts/eval179_phaseb_gate.py   # EVAL-179 SEALED, exit 0
python3 scripts/eval180_phaseb_gate.py   # EVAL-180 SEALED, exit 0
python3 scripts/eval181_phaseb_gate.py   # EVAL-181 SEALED, exit 0

# 3) EVAL-64 feasible-floor probe across all on-disk captures (slow: large JSON):
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

# 5) Anti-avoidance: green driver + all-sealed through EVAL-181 is NOT completion.
#    Build EVAL-182 (toxicity x atm_iv interaction -> forward variance) in the same session.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..181 sealed. **EVAL-63 never sealed.** EVAL-181 (cross-asset order-flow imbalance × atm_iv interaction → forward CVaR, `NO-GO CONFIRMED (PASS)`, `20261122T012720Z`) is the latest sealed rung; EVAL-177 (skew → forward variance, GO CONFIRMED) and EVAL-168/169 (atm_iv/term_slope → forward CVaR, GO CONFIRMED) remain the surviving surface-line GOs.