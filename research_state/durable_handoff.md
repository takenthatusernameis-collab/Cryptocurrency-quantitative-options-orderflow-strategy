# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-22T03:06:50Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. The order-flow distributional sweep is complete and uniformly NO-GO CONFIRMED (PASS). The single-asset surface distributional grids are complete. The cross-asset surface/term distributional grids are complete through forward variance (EVAL-176 atm_iv, 177 skew, 178 term_slope, 179 term_ratio). **EVAL-180 is SEALED:** cross-asset order-flow imbalance × atm_iv interaction spillover → forward realized return variance, `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH, artifact stamp `20261122T011312Z`. **EVAL-181 is SEALED:** cross-asset order-flow imbalance × atm_iv interaction spillover → forward CVaR, `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 imbalance states and 289 surface bars each; 274 aligned common bars), artifact stamp `20261122T012720Z`. **EVAL-182 is SEALED:** cross-asset order-flow **toxicity** × atm_iv interaction spillover → forward realized return variance, `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH, artifact stamp `20261122T020547Z`. **EVAL-183 is SEALED:** cross-asset order-flow **toxicity** × atm_iv interaction spillover → forward **CVaR**, `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 toxicity states and 289 surface bars each; 274 aligned common bars), artifact stamp `20261122T025328Z`. All order-flow × surface interaction cells (imbalance/toxicity × atm_iv → variance/CVaR) are now complete and uniformly NO-GO. The only surviving directional/tail alpha remains on the **surface** line; the remaining on-charter work is TRACK A (data-blocked on the EVAL-64 floor).
>
> **CURRENT MANDATED QUEUE:** EVAL-172..179 are **SEALED** (single-asset and cross-asset surface/term → forward variance grids COMPLETE). **EVAL-180/181/182/183 are SEALED** (`NO-GO CONFIRMED (PASS)`, both floors OK, 12 configs each, 0 BH-FDR rejections). **EVAL-183 is the final sealed predictiveness rung.** No unsealed predictiveness rung remains. The next and only remaining on-charter work is **TRACK A (data-blocked on EVAL-64 floor)**: a fresh ~3.7-day three-way capture → EVAL-64 floor probe → **if and only if the floor is met**, build the next unsealed traded-form rung (single-asset `atm_iv`/`term_slope` → directional delta-hedged traded-form net-of-cost; reuse EVAL-64 floor + EVAL-62 mark-path verbatim), else seal `BLOCKED` (never NO-GO). Never block the session on TRACK A (~3.7 days, never in-session).
> **NEXT FOCUS CAMPAIGN (anti-avoidance — future agents must not defer or substitute):** green driver every session is the per-session gate; `green driver + all-sealed through EVAL-183 is NOT completion`. The only remaining mandated heavy work is TRACK A (data-blocked background capture ~3.7 days → EVAL-64 floor probe → traded-form rung iff floor met, else `BLOCKED` never NO-GO). Do not invent a substitute predictiveness rung; none remains unsealed.

## VERIFIED STATE (2026-11-22T02:10:00Z)

Driver source of truth: `EXPECTED_TARGETED_TESTS=2430`, `EXPECTED_DIAGNOSTIC_TESTS=27`. EVAL-66..183 are sealed (EVAL-63 never sealed). **All gates `ok`/phase `SEALED`; driver exit 0; idempotent no-op.** EVAL-67/68/69 are SEALED (forward disjoint-window ladder complete; threshold `2026-11-20T00:00:00Z` PASSED).

- EVAL-180 sealed successfully: `research_state/EVAL_180_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_COMBINED_20261122T011312Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 imbalance states and 289 surface bars each; 274 aligned common bars). Best IC: BTC 0.1331 (`ETH->BTC::oflow_atm_iv_interaction::bar60.0::h6`), ETH 0.1326 (`BTC->ETH::oflow_atm_iv_interaction::bar300.0::h24`); 0 pass configs; 12 configs; no BH-FDR rejections. Cross-asset order-flow × surface interaction → forward variance cell complete.
- EVAL-181 sealed successfully: `research_state/EVAL_181_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_CVAR_COMBINED_20261122T012720Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 imbalance states and 289 surface bars each; 274 aligned common bars). Best IC: BTC -0.0163 (`ETH->BTC::oflow_atm_iv_interaction::bar300.0::h6`), ETH 0.0051 (`BTC->ETH::oflow_atm_iv_interaction::bar300.0::h6`); 0 pass configs; 12 configs; no BH-FDR rejections. Cross-asset order-flow imbalance × atm_iv interaction → forward CVaR cell complete.
- EVAL-182 sealed successfully: `research_state/EVAL_182_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_COMBINED_20261122T020547Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH; 12 configs; no BH-FDR rejections. Cross-asset order-flow **toxicity** × atm_iv interaction → forward variance cell complete. Signal path: `e62.build_states(tox_signal="tox")` × `e71.build_surface_bars().atm_iv`.
- EVAL-183 sealed successfully: `research_state/EVAL_183_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_CVAR_COMBINED_20261122T025328Z.json/.md` + preregistration; verdict `NO-GO CONFIRMED (PASS)`, floor OK for BTC and ETH (289 toxicity states and 289 surface bars each; 274 aligned common bars); 12 configs; no BH-FDR rejections. Cross-asset order-flow **toxicity** × atm_iv interaction → forward CVaR cell complete. Signal path: `e62.build_states(tox_signal="tox")` × `e71.build_surface_bars().atm_iv`; target `_forward_cvar` via EVAL-168 (`CVAR_ALPHA` verbatim from EVAL-163/EVAL-168).
- EVAL-180/181/182/183 scripts/tests are new untracked files. Driver tables updated: `TARGETED_TEST_FILES` (+8 files vs EVAL-181 baseline, +72 tests → 2430), `GATE_SPECS` (+EVAL-182, +EVAL-183), `SEAL_SPECS` (+EVAL-182, +EVAL-183), `EXPECTED_TARGETED_TESTS=2430` reconciled via the full driver run. Duplicate EVAL-126 test-artifact churn remains untracked; do not commit it.
- No sealed EVAL artifact or `src/` modified. Only `scripts/eval67_prethreshold_progress.py` is modified (EVAL-182/183 wiring); EVAL-180/181/182/183 scripts/tests/artifacts are new.

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
| Cross-asset order-flow **toxicity** × atm_iv interaction → forward variance | EVAL-182 (tox × atm_iv) | **SEALED** (`NO-GO CONFIRMED (PASS)`, `20261122T020547Z`) |
| Cross-asset order-flow **toxicity** × atm_iv interaction → forward CVaR | EVAL-183 (tox × atm_iv) | **SEALED** (`NO-GO CONFIRMED (PASS)`, `20261122T025328Z`) |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## PRE-REGISTERED BUILD QUEUE — EVAL-183 sealed → TRACK A background

All predictiveness rungs EVAL-02..183 are sealed (EVAL-63 never sealed); the order-flow × surface interaction cells are uniformly NO-GO and the surface-line GOs (EVAL-177 skew → variance; EVAL-168/169 atm_iv/term_slope → CVaR) are the surviving alpha. The terminal deliverable (traded-form net-of-cost) remains data-blocked on the EVAL-64 floor — NOT the per-session heavy work. There is no unsealed predictiveness rung; do not invent a substitute rung.

1. **Driver green check (every session):** run `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2430/2430 targeted, 27/27 diagnostics, `failures: []`, `gate_exit=0`). All EVAL-70..183 gates SEALED.
2. **TRACK A (non-blocking background; NOT a per-session gate):** fresh 3.7-day capture → EVAL-64 floor probe → traded-form rung only if floor met, else `BLOCKED` (never NO-GO). Never block the session on TRACK A (~3.7 days, never in-session).

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0). EVAL-70..183 gates: `SEALED`(0) idempotent no-op. `FAILED`(1) fix and rerun.
- Green driver = env OK, `2430/2430` targeted, `27/27` diagnostics, all `EVAL-70..183` gates classified `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Green driver + all-sealed through EVAL-183 **IS** session completion for the predictiveness ladder; remaining on-charter work is TRACK A (data-blocked on EVAL-64 floor, never in-session).
- EVAL-180/181/182/183 built+wired+sealed: test files in `TARGETED_TEST_FILES`, gate in `GATE_SPECS`, seal in `SEAL_SPECS` (`expected_exit:0`), `EXPECTED_TARGETED_TESTS=2430` (2412 + 18 via the full driver run). Do not re-run EVAL-161..183 as a substitute for new work; do not hand-run a runner — let the driver seal each EVAL.
- Stale `SEAL_SPECS` `expected_exit` after a driver-driven seal — the driver overrides `expected_exit` to 0 whenever the matching gate is `SEALED`; flip 1→0 in the same session for clarity.
- Stale-handoff / timestamp-refresh treadmill — fixed: this handoff reflects TRUE state (EVAL-180/181/182/183 sealed; driver green at 2430/2430) and points at genuinely-next runnable work (TRACK A, data-blocked). Do not refresh the timestamp without new verified facts.
- Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment/tail fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
- Half-wired driver — reconcile all three driver tables AND `EXPECTED_TARGETED_TESTS` with `pytest --collect-only` before trusting green (EVAL-183: 2412→2430).
- Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
- Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
- Surface-bar vs term-bar vs order-flow signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`; order-flow toxicity via `e62.build_states(tox_signal="tox")`; EVAL-183 composes `e62.build_states(tox_signal="tox")` × `e71.build_surface_bars`. Do not cross them.
- No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
- Traded-form "data-blocked" misread as "unbuilt" — the per-session heavy work is ALWAYS a runnable predictiveness/interaction rung, never the data-blocked traded-form. No predictiveness rung remains unsealed; TRACK A is data-blocked.
- Duplicate-artifact churn on sealed EVAL-126 — do not re-run EVAL-126, do not commit churn files, never enumerate `research_state/`. The EVAL-126 gate unit test now monkeypatches `execute_phaseb`; do not reintroduce a real `main --execute` call with fake captures.
- Dict-vs-list iteration in a cloned runner — iterate `.values()` over `{underlying: capture}` dicts; ensure `_campaign_floor`/`campaign_floor` is actually CALLED.
- Multi-day acquisition not a per-session gate — TRACK A (~3.7 days) cannot finish in one session; non-blocking background only.
- **"No runnable-now predictiveness rung" avoidance** — all predictiveness rungs through EVAL-183 are sealed; the next on-charter work is TRACK A (data-blocked on EVAL-64 floor), which cannot run in-session.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..183 artifacts or `src/`. Append-only for new authorized work.
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-168..183 acquire nothing (consume on-disk `data/raw/eval61`).
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

# 1) Full heavy-work loop; run every session. All EVAL-182 sealed, idempotent no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2412/2412, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..183 gates SEALED/ok, all seal_gates ok. EXPECTED_TARGETED_TESTS=2430.

# 2) Verify sealed campaigns idempotently:
python3 scripts/eval175_phaseb_gate.py   # EVAL-175 SEALED, exit 0
python3 scripts/eval176_phaseb_gate.py   # EVAL-176 SEALED, exit 0
python3 scripts/eval177_phaseb_gate.py   # EVAL-177 SEALED, exit 0
python3 scripts/eval178_phaseb_gate.py   # EVAL-178 SEALED, exit 0
python3 scripts/eval179_phaseb_gate.py   # EVAL-179 SEALED, exit 0
python3 scripts/eval180_phaseb_gate.py   # EVAL-180 SEALED, exit 0
python3 scripts/eval181_phaseb_gate.py   # EVAL-181 SEALED, exit 0
python3 scripts/eval182_phaseb_gate.py   # EVAL-182 SEALED, exit 0
python3 scripts/eval183_phaseb_gate.py   # EVAL-183 SEALED, exit 0

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

# 5) Anti-avoidance: green driver + all-sealed through EVAL-183 is completion for the predictiveness ladder; remaining on-charter work is TRACK A (data-blocked on EVAL-64 floor).
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..183 sealed. **EVAL-63 never sealed.** EVAL-183 (cross-asset order-flow toxicity × atm_iv interaction → forward CVaR, `NO-GO CONFIRMED (PASS)`, `20261122T025328Z`) is the latest sealed rung; EVAL-177 (skew → forward variance, GO CONFIRMED) and EVAL-168/169 (atm_iv/term_slope → forward CVaR, GO CONFIRMED) remain the surviving surface-line GOs.
