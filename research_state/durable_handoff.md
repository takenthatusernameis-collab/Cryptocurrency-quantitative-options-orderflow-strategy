# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-22T10:24:49Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **START HERE — DO NOT STOP AT A GREEN DRIVER OR ANOTHER HANDOFF EDIT.** EVAL-185 is **SEALED** (`EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_COMBINED_20261122T092235Z.{json,md}`, stamp `20261122T092235Z`, gate exit 0, seal-gate exit 0): the surface NO-GO is **robust to monetization** (0 grid configs pass the both-asset GO bar across the 45-config cost×horizon grid). Both traded-form lines are now `NO-GO CONFIRMED (PASS)` (EVAL-69 order-flow, EVAL-185 surface). The remaining on-charter work is **TRACK A — fresh-window replication (EVAL-186)**, now a first-class campaign with a runner, a pre-capture gate, and 23 passing tests.
>
> **STARTING COMMAND FOR THIS SESSION (run immediately):** `python3 scripts/eval186_phaseb_gate.py`. It currently reports `WAIT_CAPTURE` (exit 10) because `data/raw/eval185cap` does not yet exist. That is the only missing input. Do not substitute `data/raw/eval84cap` (that is the sealed EVAL-84/185 window). The gate encodes the exact required acquisition; the recommended forward window is:
>
> ```bash
> python3 scripts/eval60_acquire_three_way.py \
>   --underlying BTC --underlying ETH --days 3.7 \
>   --end 2026-11-26T00:00:00Z --max-per-expiry 30 \
>   --out-dir data/raw/eval185cap --seal
> ```
>
> **CRITICAL SCHEDULING FIX (load-bearing — do not reintroduce the old bug):** a 3.7-day acquisition ending `2026-11-25T08:00:00Z` would start `2026-11-21T15:12:00Z`, which **overlaps** the EVAL-84/185 capture window `2026-11-18T13:58:43Z..2026-11-22T06:46:43Z`. The earliest strictly-forward 3.7-day end is `2026-11-25T23:34:43Z`; use `2026-11-26T00:00:00Z` for margin. The gate and runner enforce `start >= PREVIOUS_WINDOW_END` plus span ≥ 300000 s plus disjointness from both the sealed EVAL-64/65 window and the EVAL-84/185 window.
>
> **VERIFIED THIS SESSION (2026-11-22T10:22:30Z):** full driver green — env OK, targeted `2430/2430`, diagnostics `27/27`, `failures: []`, exit 0; all EVAL-67/68/69 + EVAL-70..183 gates sealed; EVAL-184 gate `SEALED`(0) seal-gate 0; EVAL-185 gate `SEALED`(0) seal-gate 0. EVAL-186 runner + gate added (append-only; touches no sealed artifact/src): `scripts/eval186_track_a_fresh_window_replication.py`, `scripts/eval186_phaseb_gate.py`, `tests/test_eval186_track_a_fresh_window_replication.py` (23/23 pass). `data/raw/eval185cap` is absent; `data/raw/eval84cap` is present, floor-compliant, disjoint, and is the previous window to be disjoint from.
>
> **BOTTLENECKS REMOVED (load-bearing — do not reintroduce):**
> 1. The old handoff’s “after ~2026-11-25T08:00:00Z” acquisition was an overlap bug; replaced with the strictly-forward `2026-11-26T00:00:00Z` recommendation and an enforced `starts_after_previous` check.
> 2. The old handoff said “no in-session heavy build remains” while the runner was unbuilt; EVAL-186’s runner + gate + tests now exist, so the only remaining work is capture acquisition + compute, not a build task.
> 3. Subprocess env trap stays fixed: any gate/runner subprocess that imports `numpy`/`pandas`/`scipy` MUST set `PYTHONPATH=.venv-deps` (see `_child_env()` in `eval184_phaseb_gate.py`, `eval185_phaseb_gate.py`, and the new `eval186_phaseb_gate.py`). Without it, `--execute` fails at dry-run with `ModuleNotFoundError`.
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. Predictiveness EVAL-02..183 is sealed. Order-flow is resolved (EVAL-67/68 predictive GO; EVAL-69 net-of-cost NO-GO). Surface predictiveness has GOs (EVAL-177 skew→variance; EVAL-168/169 atm_iv/term_slope→CVaR), but EVAL-184 monetizes them to `NO-GO CONFIRMED (PASS)` and EVAL-185 proves that NO-GO robust across the cost×horizon grid. The next on-charter heavy work is **temporal robustness on a strictly forward fresh window (EVAL-186)**.

## VERIFIED STATE (2026-11-22T10:22:30Z)

- **EVAL-184 SEALED `NO-GO CONFIRMED (PASS)`** — `EVAL_184_SURFACE_TRADED_NETFCOST_OOS_COMBINED_20261122T081750Z.{json,md}` + prereg `..._20261122T065050Z`. Floor OK both; disjointness OK; 12 configs; 2000 pooled returns; power adequate; 0 BH-FDR rejections. Gate `eval184_phaseb_gate.py` → `SEALED`(0), seal-gate 0.
- **EVAL-185 SEALED `NO-GO CONFIRMED (PASS)`** — `EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_COMBINED_20261122T092235Z.{json,md}` (stamp `20261122T092235Z`) + prereg same stamp. 45-config cost×horizon grid; 0 BH-FDR rejections; max pooled returns 2000; power adequate; floor/disjoint OK both. Gate `eval185_phaseb_gate.py` → `SEALED`(0), seal-gate 0.
- **EVAL-186 BUILT THIS SESSION (append-only; no sealed artifact/src touched):**
  - `scripts/eval186_track_a_fresh_window_replication.py` — TRACK A replication runner. Runs EVAL-69 (`write=False`) and EVAL-184 (`write=False`) on a strictly forward capture; composes family verdicts; emits `GO CONFIRMED` if either family GOs, `NO-GO CONFIRMED (PASS)` only if both NO-GO and both power-adequate, `INCONCLUSIVE (UNDERPOWERED)` if neither GO and either underpowered, `BLOCKED` if floor/disjointness fails or a family cannot be evaluated. Enforces `start >= 2026-11-22T06:46:43Z`, span ≥ 300000 s, disjoint from both sealed `2026-11-09T06:48:16Z..2026-11-16T06:48:16Z` and previous `2026-11-18T13:58:43Z..2026-11-22T06:46:43Z` windows. EVAL-64 floor reused verbatim.
  - `scripts/eval186_phaseb_gate.py` — deterministic arbiter. Outcomes: `SEALED`(0) idempotent no-op with seal-gate 0; `WAIT_CAPTURE`(10) when `data/raw/eval185cap` lacks BTC or ETH; `WAIT_RUNNER`(20) when capture present but runner dry-run fails; `DUE`(30) when capture present + runner green + unsealed (re-run with `--execute`); `FAILED`(1) on seal/seal-gate failure. Task floor stamp `20261122T095117Z` (session start). `_child_env()` bakes the PYTHONPATH fix.
  - `tests/test_eval186_track_a_fresh_window_replication.py` — 23 tests: ids/globs, verbatim reuse, forward schedule math, disjointness accept/reject cases, composition verdict precedence, seal artifact selection (BLOCKED vs COMBINED), gate phase precedence, seal detection, capture inventory, idempotent SEALED no-op.
- **Green driver** `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0 at `2026-11-22T10:22:30Z` (2430/2430 targeted, 27/27 diagnostics, `failures: []`, all EVAL-70..183 + EVAL-67/68/69 gates `SEALED`/`ok`, 121/121 seal_gates ok). EVAL-184 and EVAL-185 are not wired into the driver (optional; the driver stays green through EVAL-183 + EVAL-67/68/69). EVAL-186 is enforced separately by its gate — do not treat driver wiring as optional completion.
- **Capture state:** `data/raw/eval84cap` present (BTC+ETH, ~297 MB, gitignored, LOCAL, floor-compliant, disjoint). `data/raw/eval185cap` absent — the only missing input for EVAL-186.

## CAMPAIGN LEDGER (all sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | CLOSED (EVAL-63 never sealed) |
| Forward disjoint-window ladder (incl. traded-form EVAL-69) | EVAL-67/68/69 | **SEALED COMBINED** — EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)` |
| Physics-independent predictiveness EVAL-70..160 | 91 rungs | SEALED |
| Single-asset surface → forward CVaR | EVAL-161/162/163/164 | SEALED (163 GO; others NO-GO CONFIRMED (PASS)) |
| Single-asset surface → downside-semivariance share | EVAL-115, 165, 166, 167 | SEALED |
| Cross-asset surface/term → forward signed return mean | EVAL-148 (4 cells) | SEALED COMPLETE |
| Cross-asset options order-flow → signed mean/skew/downside/kurt/var | EVAL-149..160 | SEALED COMPLETE |
| Cross-asset surface/term → forward CVaR | EVAL-168 (atm_iv), 169 (term_slope), 170 (term_ratio), 171 (skew) | SEALED |
| Single-asset surface → forward variance | EVAL-172..175 | SEALED (grid COMPLETE) |
| Cross-asset surface → forward variance | EVAL-176..179 | SEALED COMPLETE (177 GO; others NO-GO) |
| Cross-asset order-flow × surface interaction → variance/CVaR | EVAL-180/181/182/183 | SEALED (`NO-GO CONFIRMED (PASS)` each) |
| **Surface-line traded-form net-of-cost OOS (EVAL-184)** | **skew/atm_iv/term_slope** | **SEALED `NO-GO CONFIRMED (PASS)`** (`20261122T081750Z`) |
| **Surface-line traded-form ROBUSTNESS GRID (EVAL-185)** | **cost×horizon grid** | **SEALED `NO-GO CONFIRMED (PASS)`** (`20261122T092235Z`) — 0/45 grid configs pass |
| **TRACK A fresh-window replication (EVAL-186)** | **EVAL-69 + EVAL-184 on new forward window** | **RUNNER + GATE BUILT; `WAIT_CAPTURE` (exit 10); heavy work = acquire + compute + seal** |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## CURRENT MANDATED QUEUE (the only remaining on-charter work — EVAL-186 TRACK A fresh-window replication)

1. **Env + driver green check (every session):** `./scripts/verify_env.sh` then `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0.
2. **Verify sealed gates idempotently:** `python3 scripts/eval185_phaseb_gate.py` → `SEALED`(0); `python3 scripts/eval184_phaseb_gate.py` → `SEALED`(0).
3. **EVAL-186 gate (the active anti-avoidance arbiter):** `python3 scripts/eval186_phaseb_gate.py`. Currently `WAIT_CAPTURE`(10). Interpret the phase:
   - `WAIT_CAPTURE`(10): acquire the strictly forward capture (step 4), then re-run the gate.
   - `WAIT_RUNNER`(20): the capture exists but the runner dry-run failed; fix the runner and make `--no-write` green.
   - `DUE`(30): capture present + runner green + unsealed; re-run with `--execute`.
   - `SEALED`(0): EVAL-186 complete; idempotent no-op.
   - `FAILED`(1): fix the failed step and re-run with `--execute`.
4. **Acquire the strictly forward capture (only after step 3 says `WAIT_CAPTURE`):**
   ```bash
   python3 scripts/eval60_acquire_three_way.py \
     --underlying BTC --underlying ETH --days 3.7 \
     --end 2026-11-26T00:00:00Z --max-per-expiry 30 \
     --out-dir data/raw/eval185cap --seal
   ```
   Do not use an end earlier than `2026-11-25T23:34:43Z` — earlier ends overlap the EVAL-84/185 window and the runner will correctly seal `BLOCKED`. Verify the EVAL-64 floor after acquisition.
5. **Seal:** `python3 scripts/eval186_phaseb_gate.py --execute` → require `SEALED`(0) plus a passing seal-gate. Under-floor or non-disjoint data ⇒ `BLOCKED`, never `NO-GO`.
6. **Do NOT re-run / re-litigate / re-seal EVAL-67..185** — historical append-only seals. EVAL-186 produces NEW artifacts (append-only).

## NEXT FOCUS CAMPAIGN (anti-avoidance — future agents must not defer or substitute)

EVAL-185 is SEALED (`20261122T092235Z`): the surface NO-GO is robust to monetization (0/45 grid configs pass the both-asset GO bar). Both traded-form lines are `NO-GO CONFIRMED (PASS)`. The remaining on-charter work is **EVAL-186 — TRACK A fresh-window replication** on a strictly forward BTC+ETH capture at `data/raw/eval185cap` (acquisition end ≥ `2026-11-25T23:34:43Z`; recommended `2026-11-26T00:00:00Z`). The runner + gate + tests already exist; the only missing input is the capture. Enforced by `scripts/eval186_phaseb_gate.py` every session. Under-floor ⇒ `BLOCKED`, never `NO-GO`. Do not invent a substitute rung; do not re-open EVAL-185.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) COMBINED (EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)`). EVAL-70..183 gates: `SEALED`(0) idempotent. EVAL-184: `SEALED`(0) COMBINED `NO-GO CONFIRMED (PASS)` (`20261122T081750Z`). EVAL-185: `SEALED`(0) COMBINED `NO-GO CONFIRMED (PASS)` (`20261122T092235Z`). `FAILED`(1) fix and rerun.
- Green driver = env OK, `2430/2430` targeted, `27/27` diagnostics, all EVAL-70..183 + EVAL-67/68/69 gates `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Green driver + all-sealed through EVAL-185 is completion ONLY for the predictiveness + both traded-form lines; it is **NOT** session completion — the remaining on-charter work is **EVAL-186 TRACK A fresh-window replication**, enforced by `scripts/eval186_phaseb_gate.py`.
- EVAL-186 completion = `python3 scripts/eval186_phaseb_gate.py` exits `SEALED`(0) with a COMBINED/BLOCKED artifact stamp ≥ `20261122T095117Z` and a passing `check_session_sealed.py` seal-gate. The gate will not seal without: (a) a strictly forward floor-compliant capture at `data/raw/eval185cap`, (b) a green `scripts/eval186_track_a_fresh_window_replication.py --no-write`, (c) a successful `--seal` run. Under-floor/non-disjoint ⇒ `BLOCKED`, never `NO-GO`.
- The terminal deliverable (tradeable net-of-cost strategy) is currently `NO-GO CONFIRMED (PASS)` on **both** lines (EVAL-69 order-flow, EVAL-184/185 surface). EVAL-186 tests temporal robustness of that dual NO-GO on a fresh forward window.
- Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment/tail fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
- Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
- Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
- Surface-bar vs term-bar signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`. Do not cross them.
- No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
- **Subprocess env trap (fixed; do not reintroduce):** any gate/runner subprocess that imports `numpy`/`pandas`/`scipy` MUST set `PYTHONPATH=.venv-deps` (see `_child_env()` in `eval184_phaseb_gate.py`, `eval185_phaseb_gate.py`, `eval186_phaseb_gate.py`). Without it, `--execute` fails at dry-run with `ModuleNotFoundError`.
- **"Capture is already on disk" is TRUE for `data/raw/eval84cap` but FALSE for `data/raw/eval185cap`** — the latter is gitignored/absent and needs a fresh strictly-forward acquisition. Do not claim it exists without `ls data/raw/eval185cap/three_way_*.json`.
- **"No runnable-now heavy work" avoidance** — the genuinely-next heavy work is EVAL-186 (TRACK A fresh-window replication), enforced by `scripts/eval186_phaseb_gate.py`. This is the mandated heavy work. Do not invent a substitute rung.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..69, EVAL-70..185 artifacts or `src/`. Append-only for new authorized work. EVAL-184 (`COMBINED_20261122T081750Z`), EVAL-185 (`COMBINED_20261122T092235Z`), and EVAL-67/68/69 are historical seals — do not edit them; EVAL-186 produces NEW artifacts (append-only).
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-186 consumes a freshly acquired strictly forward capture (acquire nothing during the compute phase).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
- Use correct task IDs (`INIT-2026-11-22T09:51:17Z-EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION`); do not use retired compact task IDs.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs. `data/raw/eval84cap` (~300 MB) is gitignored and must be kept LOCAL and never committed/pushed. `data/raw/eval185cap` (~300 MB, once acquired) is likewise gitignored and must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ a real new measurement, e.g. a sealed EVAL-186 artifact). Do not refresh this timestamp without a sealed EVAL-186.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session. All EVAL-184 + EVAL-185 + EVAL-70..183 + EVAL-67/68/69 sealed, idempotent no-op:
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2430/2430, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..183 + EVAL-67/68/69 gates SEALED/ok, all 121 seal_gates ok. EXPECTED_TARGETED_TESTS=2430.

# 2) Verify sealed campaigns idempotently:
python3 scripts/eval184_phaseb_gate.py   # EVAL-184 SEALED (COMBINED NO-GO CONFIRMED (PASS)), exit 0
python3 scripts/eval185_phaseb_gate.py   # EVAL-185 SEALED (COMBINED NO-GO CONFIRMED (PASS)), exit 0

# 3) EVAL-186 anti-avoidance gate (the mandated heavy work arbiter):
python3 scripts/eval186_phaseb_gate.py
#    Currently WAIT_CAPTURE (exit 10) because data/raw/eval185cap is absent.
#    The phase output contains the exact next action. Do NOT skip to sealing. Re-run with --execute ONLY when DUE.

# 4) MANDATED HEAVY WORK — EVAL-186 TRACK A fresh-window replication (enforced by the gate):
#    (a) Acquire the strictly forward capture (end >= 2026-11-25T23:34:43Z; recommended 2026-11-26T00:00:00Z):
python3 scripts/eval60_acquire_three_way.py \
  --underlying BTC --underlying ETH --days 3.7 \
  --end 2026-11-26T00:00:00Z --max-per-expiry 30 \
  --out-dir data/raw/eval185cap --seal
#    (b) Verify the EVAL-64 floor, dry-run green:
PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py \
  --capture-dir data/raw/eval185cap --no-write
#    (c) Seal: python3 scripts/eval186_phaseb_gate.py --execute  => require SEALED (exit 0) + seal-gate exit 0.

# 5) Anti-avoidance: green driver + EVAL-184/185 SEALED is completion ONLY for the predictiveness +
#    both traded-form lines. Remaining on-charter work = EVAL-186 TRACK A fresh-window replication
#    (in-session acquisition + compute + seal), enforced by scripts/eval186_phaseb_gate.py.
#    The gate will not seal without a strictly forward real capture + a green runner. Do not fake it.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..185 sealed. **EVAL-63 never sealed.** EVAL-67/68/69 are sealed **COMBINED**: EVAL-67 `GO CONFIRMED` (`20261122T053156Z`), EVAL-68 `GO CONFIRMED` (`20261122T053327Z`), EVAL-69 `NO-GO CONFIRMED (PASS)` (`20261122T053616Z`) — floor OK both underlyings, disjointness OK. The order-flow toxicity→realized-vol slice is **predictive but not tradeable net-of-cost**. The surface-line GOs EVAL-177 (skew→variance) and EVAL-168/169 (atm_iv/term_slope→CVaR) are sealed predictive GOs, but **EVAL-184 monetizes them to `NO-GO CONFIRMED (PASS)`** (`EVAL_184_SURFACE_TRADED_NETFCOST_OOS_COMBINED_20261122T081750Z.{json,md}`; 0 BH-FDR rejections across 12 configs, floor OK BTC+ETH, disjoint OK) on the floor-compliant disjoint capture `data/raw/eval84cap`, and **EVAL-185 proves that NO-GO robust across the 45-config cost×horizon grid** (`EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_COMBINED_20261122T092235Z.{json,md}`; 0 BH-FDR rejections, floor OK BTC+ETH, disjoint OK). **Both signal families now monetize to NO-GO net-of-cost, robustly.** The next on-charter heavy work is **EVAL-186 TRACK A fresh-window replication** (runner + gate built; `WAIT_CAPTURE` pending the strictly forward capture), enforced by `scripts/eval186_phaseb_gate.py`.