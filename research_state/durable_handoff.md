# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-22T09:48:42Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **START HERE — DO NOT STOP AT A GREEN DRIVER OR ANOTHER HANDOFF EDIT.** EVAL-185 is **SEALED** (`EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_COMBINED_20261122T092235Z.{json,md}`, stamp `20261122T092235Z`, gate exit 0, seal-gate exit 0): the surface NO-GO is **robust to monetization** (0 grid configs pass the both-asset GO bar across the 45-config cost×horizon grid). Both traded-form lines are now `NO-GO CONFIRMED (PASS)` (EVAL-69 order-flow, EVAL-185 surface). The remaining on-charter work is **TRACK A — fresh-window replication** (non-blocking, background, ~3.7 days for new data): acquire `data/raw/eval185cap` (after ~2026-11-25T08:00:00Z) and re-run EVAL-69 + EVAL-184 runners on the fresh window to confirm the dual NO-GO is temporally robust (not a single-window artifact). Under-floor ⇒ `BLOCKED`, never NO-GO. Do not invent a substitute rung. No in-session heavy build remains; do not re-open EVAL-185.
>
> **VERIFIED THIS SESSION (2026-11-22T08:39:21Z):** the full driver is green — env OK, targeted `2430/2430`, diagnostics `27/27`, `failures: []`, exit 0; all EVAL-67/68/69 + EVAL-70..183 gates are sealed. EVAL-184 is sealed with 12 configs, 2000 pooled returns, 0 BH-FDR rejections, floor/disjointness OK for BTC+ETH. `data/raw/eval84cap` is present locally (`three_way_BTC_20261122T064658Z.json`, `three_way_ETH_20261122T064658Z.json`, ~297 MB total, gitignored): this is the capture EVAL-185 reuses read-only. The EVAL-185 gate independently returned `WAIT_RUNNER` (exit 20, 08:41:21Z) with `grid_config_count: 45`, confirming that the next session is build-blocked only by the missing runner, not by data or an underspecified grid.
>
> **BOTTLENECK REMOVED (load-bearing — do not reintroduce):** `scripts/eval184_phaseb_gate.py`'s `_run` originally did **not** set `PYTHONPATH=.venv-deps`, so `--execute` subprocesses raised `ModuleNotFoundError: No module named 'numpy'`. It now has `_child_env()` (used by `_run` and the runner green check), and `scripts/eval185_phaseb_gate.py` bakes the same fix in. Also, stale `AGENTS.md` language that called the terminal deliverable merely data-blocked has been replaced with the EVAL-185 anti-avoidance queue above, so future agents cannot mistake green-driver + EVAL-184 for completion. `.venv-deps` is gitignored; always bootstrap with `./scripts/verify_env.sh`.
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. The predictiveness ladder EVAL-02..183 is sealed. Order-flow is resolved (EVAL-67/68 predictive GO; EVAL-69 net-of-cost NO-GO). Surface predictiveness has GOs (EVAL-177 skew→variance; EVAL-168/169 atm_iv/term_slope→CVaR), but EVAL-184 monetizes them to `NO-GO CONFIRMED (PASS)`. The next on-charter heavy work is to **bound whether that surface NO-GO is a monetization/horizon artifact (EVAL-185)**, then test temporal robustness on a fresh window.

## VERIFIED STATE (2026-11-22T08:40:00Z)

- **EVAL-184 SEALED `NO-GO CONFIRMED (PASS)`** — `research_state/EVAL_184_SURFACE_TRADED_NETFCOST_OOS_COMBINED_20261122T081750Z.json/.md` (stamp `20261122T081750Z`) + prereg `EVAL_184_SURFACE_TRADED_NETFCOST_OOS_PREREGISTRATION_20261122T065050Z.{json,md}`. Floor OK both underlyings; disjointness OK; 12 configs; 2000 pooled returns; power adequate; **0 BH-FDR rejections**; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`. Gate `scripts/eval184_phaseb_gate.py` → `SEALED` (exit 0), seal-gate `check_session_sealed.py` exit 0. **Do not re-run/re-seal EVAL-184.**
- **Green driver** `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0 at `2026-11-22T08:39:21Z` (2430/2430 targeted, 27/27 diagnostics, `failures: []`, all EVAL-70..183 + EVAL-67/68/69 gates `SEALED`/`ok`, 120/120 seal_gates). EVAL-184 is **not** wired into the driver (optional; the driver stays green through EVAL-183 + EVAL-67/68/69). EVAL-185 is enforced separately by its gate — do not treat driver wiring as optional completion.
- **`data/raw/eval84cap` is PRESENT on disk** (gitignored, LOCAL, never commit): `three_way_BTC_20261122T064658Z.json` (154 MB, 07:14Z) + `three_way_ETH_20261122T064658Z.json` (156 MB, 07:42Z); floor-compliant (both underlyings), disjoint from the sealed EVAL-64/65 window. **This is the capture EVAL-185 reuses read-only.** (Corrects the older stale "capture absent" note: it is present in this checkout; a fresh checkout has it gitignored/absent and would need a ~1 h re-acquisition.)
- **NEW this session:** `scripts/eval185_phaseb_gate.py` added (append-only; touches no sealed artifact/src) — the deterministic anti-avoidance arbiter of the EVAL-185 completion contract; reports `WAIT_RUNNER` (exit 20) because the EVAL-185 runner is not yet built. Also fixed the `_run` PYTHONPATH bottleneck in `scripts/eval184_phaseb_gate.py` (see top).

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | CLOSED (EVAL-63 never sealed) |
| Forward disjoint-window ladder (incl. traded-form EVAL-69) | EVAL-67/68/69 | **SEALED COMBINED** — EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)` (predictive but not tradeable net-of-cost); floor OK both, disjoint OK |
| Physics-independent predictiveness EVAL-70..160 | 91 rungs | SEALED |
| Single-asset surface → forward CVaR | EVAL-161/162/163/164 | SEALED (163 GO; others NO-GO CONFIRMED (PASS)) |
| Single-asset surface → downside-semivariance share | EVAL-115, 165, 166, 167 | SEALED |
| Cross-asset surface/term → forward signed return mean | EVAL-148 (4 cells) | SEALED COMPLETE |
| Cross-asset options order-flow → signed mean/skew/downside/kurt/var | EVAL-149..160 | SEALED COMPLETE |
| Cross-asset surface/term → forward CVaR | EVAL-168 (atm_iv), 169 (term_slope), 170 (term_ratio), 171 (skew) | SEALED |
| Single-asset surface → forward variance | EVAL-172..175 | SEALED (grid COMPLETE) |
| Cross-asset surface → forward variance | EVAL-176..179 | SEALED COMPLETE (177 GO; others NO-GO) |
| Cross-asset order-flow × surface interaction → variance/CVaR | EVAL-180/181/182/183 | SEALED (`NO-GO CONFIRMED (PASS)` each) |
| **Surface-line traded-form net-of-cost OOS (EVAL-184)** | **skew/atm_iv/term_slope** | **SEALED `NO-GO CONFIRMED (PASS)`** (`20261122T081750Z`) — 0 BH-FDR rejections, floor OK both, disjoint OK |
| **Surface-line traded-form ROBUSTNESS GRID (EVAL-185)** | **cost×horizon grid** | **NEXT — gate built (`eval185_phaseb_gate.py`), `WAIT_RUNNER`; heavy work = build runner + run grid + seal** |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## CURRENT MANDATED QUEUE (the only remaining on-charter work — TRACK A fresh-window replication; non-blocking, background)

1. **Env + driver green check (every session):** `./scripts/verify_env.sh` then `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0.
2. **Verify sealed gates idempotently:** `python3 scripts/eval185_phaseb_gate.py` → `SEALED` (exit 0); `python3 scripts/eval184_phaseb_gate.py` → `SEALED` (exit 0).
3. **TRACK A (background, non-blocking, after ~2026-11-25T08:00:00Z):** acquire `data/raw/eval185cap` via `scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 --end <≥ 2026-11-25T08:00:00Z> --max-per-expiry 30 --out-dir data/raw/eval185cap --seal`, verify the EVAL-64 floor, then re-run the EVAL-69 + EVAL-184 runners on the fresh window to confirm the dual NO-GO is temporally robust. Under-floor ⇒ `BLOCKED`, never NO-GO.
4. **Do NOT re-run / re-litigate / re-seal EVAL-67..185** — historical append-only seals. EVAL-185 is sealed; no in-session heavy build remains.

## NEXT FOCUS CAMPAIGN (anti-avoidance — future agents must not defer or substitute)

EVAL-185 is SEALED (`20261122T092235Z`): the surface NO-GO is robust to monetization (0/45 grid configs pass the both-asset GO bar). Both traded-form lines are `NO-GO CONFIRMED (PASS)`. The remaining on-charter work is **TRACK A — fresh-window replication** (background, ~3.7 days): acquire `data/raw/eval185cap` after ~2026-11-25T08:00:00Z and re-run EVAL-69 + EVAL-184 runners on the fresh window to confirm the dual NO-GO is temporally robust. Under-floor ⇒ `BLOCKED`, never NO-GO. Do not invent a substitute rung; do not re-open EVAL-185.

## PRE-REGISTERED BUILD QUEUE — EVAL-185 surface-line robustness grid (the next heavy work)

All predictiveness rungs EVAL-02..184 are sealed; both traded-form lines (EVAL-69 order-flow, EVAL-184 surface) are `NO-GO CONFIRMED (PASS)`. The next on-charter heavy work is to bound whether the surface NO-GO is a monetization/horizon artifact (EVAL-185), then a fresh-window replication (TRACK A). Enforced by `scripts/eval185_phaseb_gate.py`.

1. **Env + driver green check** (step 1 above).
2. **EVAL-185 gate:** `python3 scripts/eval185_phaseb_gate.py` → `WAIT_RUNNER` (build the runner).
3. **Build `scripts/eval185_surface_traded_robustness_oos.py`** (EVAL-184 runner + the exact 45-config cost×horizon grid; reuse `e71`/`e74`/`e62`/EVAL-64 floor verbatim; scale both hedge fees and spreads by cost haircut; pooled BH-FDR across the FULL grid; both-asset GO bar; single-asset pass = legitimate `NO-GO CONFIRMED (PASS)`) + prereg + tests. Make `--no-write` green.
4. **Seal:** `python3 scripts/eval185_phaseb_gate.py --execute` → require `SEALED` (exit 0) + passing seal-gate.
5. **Background TRACK A replication** (fresh ~3.7-day capture at `data/raw/eval185cap`, after ~2026-11-25; non-blocking, never in-session).

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) COMBINED (EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)`). EVAL-70..183 gates: `SEALED`(0) idempotent. EVAL-184: `SEALED`(0) COMBINED `NO-GO CONFIRMED (PASS)` (`20261122T081750Z`). `FAILED`(1) fix and rerun.
- Green driver = env OK, `2430/2430` targeted, `27/27` diagnostics, all EVAL-70..183 + EVAL-67/68/69 gates `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Green driver + all-sealed through EVAL-184 is completion ONLY for the predictiveness + both traded-form lines; it is **NOT** session completion — the remaining on-charter work is the **surface-line robustness grid (EVAL-185)**, enforced by `scripts/eval185_phaseb_gate.py`.
- EVAL-185 completion = `python3 scripts/eval185_phaseb_gate.py` exits `SEALED`(0) with a COMBINED/BLOCKED artifact stamp ≥ `20261122T084000Z` and a passing `check_session_sealed.py` seal-gate. The gate will not seal without: (a) the floor-compliant disjoint capture at `data/raw/eval84cap`, (b) a green `scripts/eval185_surface_traded_robustness_oos.py --no-write`, (c) a successful `--seal` run. Under-floor/non-disjoint ⇒ `BLOCKED`, never NO-GO.
- The terminal deliverable (tradeable net-of-cost strategy) is currently `NO-GO CONFIRMED (PASS)` on **both** lines (EVAL-69 order-flow, EVAL-184 surface). EVAL-185 bounds whether the surface NO-GO is a monetization/horizon artifact; TRACK A then tests temporal robustness on a fresh window.
- Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment/tail fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
- Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
- Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
- Surface-bar vs term-bar signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`. Do not cross them.
- No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
- **Subprocess env trap (fixed this session; do not reintroduce):** any gate/runner subprocess that imports `numpy`/`pandas`/`scipy` MUST set `PYTHONPATH=.venv-deps` (see `_child_env()` in `scripts/eval184_phaseb_gate.py` and `scripts/eval185_phaseb_gate.py`). Without it, `--execute` fails at dry-run with `ModuleNotFoundError`.
- **"Capture is already on disk" is TRUE in this checkout but FALSE on a fresh checkout** — `data/raw/eval84cap` is gitignored (~300 MB) and present here; on a fresh checkout it is absent and needs a fresh ~1 h acquisition. Do not claim it exists without `ls data/raw/eval84cap/three_way_*.json`.
- **"No runnable-now heavy work" avoidance** — the genuinely-next heavy work is EVAL-185 (surface-line robustness grid), enforced by `scripts/eval185_phaseb_gate.py`. This is the mandated heavy work. Do not invent a substitute rung.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..66, EVAL-70..184 artifacts or `src/`. Append-only for new authorized work. EVAL-184 (`COMBINED_20261122T081750Z`) and EVAL-67/68/69 are historical seals — do not edit them; EVAL-185 produces NEW artifacts (append-only).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-185 consumes the already-acquired disjoint capture (acquire nothing during the compute phase).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not NO-GO.
- Use correct task IDs (`INIT-2026-11-22T08:40:00Z-EVAL185-SURFACE-TRADED-ROBUSTNESS-GRID`); do not use retired compact task IDs.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs. `data/raw/eval84cap` (~300 MB) is gitignored and must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ a real new measurement, e.g. a sealed EVAL-185 artifact). Do not refresh this timestamp without a sealed EVAL-185.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session. All EVAL-184 + EVAL-70..183 + EVAL-67/68/69 sealed, idempotent no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2430/2430, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..183 + EVAL-67/68/69 gates SEALED/ok, all 120 seal_gates ok. EXPECTED_TARGETED_TESTS=2430.

# 1b) EVAL-185 anti-avoidance gate (the next heavy work arbiter):
python3 scripts/eval185_phaseb_gate.py
#    Currently WAIT_RUNNER (exit 20) because scripts/eval185_surface_traded_robustness_oos.py is not built.
#    The phase output contains the exact next action. Do NOT skip to sealing. Re-run with --execute ONLY when DUE.

# 2) Verify sealed campaigns idempotently:
python3 scripts/eval184_phaseb_gate.py   # EVAL-184 SEALED (COMBINED NO-GO CONFIRMED (PASS)), exit 0
python3 scripts/eval175_phaseb_gate.py   # EVAL-175 SEALED, exit 0
python3 scripts/eval176_phaseb_gate.py   # EVAL-176 SEALED, exit 0
python3 scripts/eval177_phaseb_gate.py   # EVAL-177 SEALED, exit 0
python3 scripts/eval178_phaseb_gate.py   # EVAL-178 SEALED, exit 0
python3 scripts/eval179_phaseb_gate.py   # EVAL-179 SEALED, exit 0
python3 scripts/eval180_phaseb_gate.py   # EVAL-180 SEALED, exit 0
python3 scripts/eval181_phaseb_gate.py   # EVAL-181 SEALED, exit 0
python3 scripts/eval182_phaseb_gate.py   # EVAL-182 SEALED, exit 0
python3 scripts/eval183_phaseb_gate.py   # EVAL-183 SEALED, exit 0
python3 scripts/eval67_phaseb_gate.py    # EVAL-67 SEALED (COMBINED GO), exit 0
python3 scripts/eval68_phaseb_gate.py    # EVAL-68 SEALED (COMBINED GO), exit 0
python3 scripts/eval69_phaseb_gate.py    # EVAL-69 SEALED (COMBINED NO-GO CONFIRMED (PASS)), exit 0

# 3) EVAL-64 feasible-floor probe across all on-disk captures (slow: large JSON):
PYTHONPATH=$PWD/.venv-deps python3 - <<'PY'
import json, glob, os, sys; sys.path.insert(0, ".")
import scripts.eval64_orderflow_realized_vol_markpath_feasible as e64
for f in sorted(glob.glob("data/raw/eval*/three_way_*.json")):
    r = e64._underlying_floor_strict(json.load(open(f)))
    failed = [k for k,v in r["checks"].items() if not v]
    print(os.path.basename(f), "ok=", r["ok"], "FAILED=", failed)
PY

# 4) MANDATED HEAVY WORK — EVAL-185 surface-line traded-form robustness grid (enforced by the gate):
#    (a) EVAL-184 capture is PRESENT (data/raw/eval84cap, BTC+ETH, floor-compliant, disjoint). Reuse read-only.
#    (b) Build scripts/eval185_surface_traded_robustness_oos.py (EVAL-184 runner + cost×horizon grid;
#        reuse e71/e74/e62 + EVAL-64 floor verbatim; pooled BH-FDR across the FULL grid; both-asset GO bar)
#        + prereg + tests. Make --no-write green.
#    (c) Seal: python3 scripts/eval185_phaseb_gate.py --execute  => require SEALED (exit 0) + seal-gate exit 0.

# 5) Background TRACK A replication (non-blocking; after ~2026-11-25 for 3.7 days of fresh forward data):
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 \
  --end <≥ 2026-11-25T08:00:00Z> --max-per-expiry 30 --out-dir data/raw/eval185cap --seal
#    Then verify the EVAL-64 floor and re-run EVAL-69 + EVAL-184 runners on the fresh window.

# 6) Anti-avoidance: green driver + EVAL-184 SEALED is completion ONLY for the predictiveness + both
#    traded-form lines. Remaining on-charter work = EVAL-185 surface-line robustness grid (in-session)
#    + TRACK A fresh-window replication (background), enforced by scripts/eval185_phaseb_gate.py.
#    The gate will not seal without a real capture + a green runner. Do not fake it.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..184 sealed. **EVAL-63 never sealed.** EVAL-67/68/69 are sealed **COMBINED**: EVAL-67 `GO CONFIRMED` (`20261122T053156Z`), EVAL-68 `GO CONFIRMED` (`20261122T053327Z`), EVAL-69 `NO-GO CONFIRMED (PASS)` (`20261122T053616Z`) — floor OK both underlyings, disjointness OK. The order-flow toxicity→realized-vol slice is **predictive but not tradeable net-of-cost**. The surface-line GOs EVAL-177 (skew→variance) and EVAL-168/169 (atm_iv/term_slope→CVaR) are sealed predictive GOs, but **EVAL-184 monetizes them to `NO-GO CONFIRMED (PASS)`** (`EVAL_184_SURFACE_TRADED_NETFCOST_OOS_COMBINED_20261122T081750Z.{json,md}`; 0 BH-FDR rejections across 12 configs, floor OK BTC+ETH, disjoint OK) on the floor-compliant disjoint capture `data/raw/eval84cap`. **Both signal families now monetize to NO-GO net-of-cost.** The next on-charter heavy work is the **surface-line traded-form robustness grid (EVAL-185)**, enforced by `scripts/eval185_phaseb_gate.py` (currently `WAIT_RUNNER`), followed by a fresh-window replication (TRACK A).