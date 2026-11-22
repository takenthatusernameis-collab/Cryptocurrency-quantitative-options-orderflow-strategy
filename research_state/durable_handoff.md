# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

> **INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (2026-11-22T14:16:48Z — repository: `Cryptocurrency-quantitative-options-orderflow-strategy` ⇒ crypto OPTIONS surface + OPTIONS order-flow → tradeable, net-of-cost alpha on REAL public data; paper-only, never synthetic, never weaken the EVAL-64 floor).**
>
> **START HERE — DO NOT STOP AT A GREEN DRIVER OR ANOTHER HANDOFF EDIT.** The mandated heavy-work driver is GREEN at **2484/2484 targeted** (up from 2430 — the EVAL-184/185/186 + forward-data-preflight suites were added to `TARGETED_TEST_FILES`), **27/27 diagnostics**, `failures: []`, `gate_exit=0`, all EVAL-70..183 + EVAL-67/68/69 gates `ok`/`SEALED`, all 120 seal_gates ok. EVAL-184 (`20261122T081750Z`) and EVAL-185 (`20261122T092235Z`, 0/45 grid configs pass) are SEALED `NO-GO CONFIRMED (PASS)`. EVAL-186 TRACK A fresh-window replication is SEALED `BLOCKED` (stamp `20261122T111006Z`, seal-gate 0) — valid completion per the deterministic contract (SEALED(0) with a BLOCKED artifact). Both traded-form lines (EVAL-69 order-flow, EVAL-184/185 surface) monetize to `NO-GO CONFIRMED (PASS)`.
>
> **RESUME MECHANISM — READ THIS (was previously mis-stated, now corrected):** There is **NO session-scoped scheduled wakeup** that will auto-fire. This repo runs under the GitHub Actions **`.github/workflows/main.yml` "Kilo General Agent Loop" schedule `*/5 * * * *`** — a *fresh* agent session is launched every ~5 min and starts at the TOP of this handoff with an empty `cron_list` (verified: `cron_list` ⇒ "No scheduled cron tasks for this session"). **The handoff IS the resume mechanism.** A future session must NOT wait for a wakeup and must NOT assume one is pending; it must self-resume from this file. Do not rely on `schedule_wakeup`/`cron_create` — they are session-scoped and die with the session. If you (a session) wish to schedule your own future self, you may, but the durable guarantee is the `*/5` Actions cron + this handoff.
>
> **STARTING COMMAND FOR THIS SESSION (run immediately, in order):**
> 1. `python3 scripts/eval67_prethreshold_progress.py --execute` — require exit 0: `targeted_tests 2484/2484`, `diagnostic_tests 27/27`, `failures: []`, `gate_exit=0`, all gates `ok`/`SEALED`, all seal_gates ok.
> 2. `python3 scripts/eval184_phaseb_gate.py` → `SEALED`(0); `python3 scripts/eval185_phaseb_gate.py` → `SEALED`(0); `python3 scripts/eval186_phaseb_gate.py` → `SEALED`(0) idempotent no-op (EVAL-186 already sealed BLOCKED).
> 3. **`python3 scripts/eval186_forward_data_preflight.py` (MANDATORY ANTI-AVOIDANCE GATE — run BEFORE claiming any wait or "no heavy work").** It reuses the sealed runner's own constants/helpers, so it can never disagree with the runner about the floor, disjointness, or windows. It prints a deterministic JSON verdict:
>    - `WAIT_FORWARD_DATA` (exit 10) — forward real data still under the EVAL-64 floor. This is the **expected current verdict** (session time 2026-11-22T14:16Z; earliest viable forward window end `2026-11-25T23:34:43Z`, ~3.39 d away, `seconds_until_earliest_forward_end ≈ 292655`). Waiting is a measured wall-clock fact, not an excuse. Re-run the preflight when `now >= 2026-11-25T23:34:43Z`.
>    - `READY_TO_ACQUIRE` (exit 0) — floor + disjointness now satisfied; the script prints the exact `acquire_command` + `followup_commands` to run.
>    - `BLOCKED_*` (exit 1) — non-disjoint or missing-underlying capture on disk; resolve before acquisition (never `NO-GO`).
>    **A session that only re-runs the green driver and bumps this timestamp has NOT satisfied the contract — it MUST show the preflight verdict.**
>
> **NEXT FOCUS CAMPAIGN (anti-avoidance — future agents must not defer or substitute):** The ONLY remaining on-charter heavy work is **EVAL-186 TRACK A fresh-window replication**, sealed `BLOCKED` because the strictly-forward capture at `data/raw/eval185cap` (BTC+ETH, window `2026-11-22T07:12:00Z..2026-11-26T00:00:00Z`, span 319680 s, disjointness OK) is **under the EVAL-64 feasible floor** — real data covers only ~5 h of the 3.7-day window (BTC perp_span ≈ 13800 s, ETH perp_span ≈ 14100 s vs the 300000 s floor; option_trades 864/615 vs 2000; perp_candles 231/236 vs 1000). Root cause: the forward window extends into the future (end `2026-11-26T00:00:00Z`); floor needs ≥300000 s perp span per underlying, physically unavailable until real time reaches ~`2026-11-25T18:06:43Z` (runner's safe earliest end `2026-11-25T23:34:43Z`). **This is a hard wall-clock dependency, not a code problem — no code change can make future data exist early.** The bottleneck-removal is the preflight gate (above) + the `*/5` Actions cron that re-launches a fresh session every 5 min (so the campaign self-resumes without any session wakeup). When the preflight returns `READY_TO_ACQUIRE`, run its printed `acquire_command`, then its `followup_commands`, to reach `NO-GO CONFIRMED (PASS)` rather than `BLOCKED`. Under-floor ⇒ `BLOCKED`, never `NO-GO`. Do not substitute `data/raw/eval84cap` (it is **MISSING** in this checkout — see invariant below).
>
> **BOTTLENECKS REMOVED (load-bearing — do not reintroduce):**
> 1. **Coverage gap closed:** the mandated driver previously covered only EVAL-67..183 (2430 tests) and did NOT run the EVAL-184/185/186 suites, despite the handoff claiming full sealed-surface coverage. `TARGETED_TEST_FILES` now includes `test_eval184_*`, `test_eval185_*`, `test_eval186_track_a_*`, and `test_eval186_forward_data_preflight.py`; `EXPECTED_TARGETED_TESTS` bumped 2430→2484. A future agent cannot skip the EVAL-186 forward-data gate — the driver runs its tests.
> 2. **Anti-avoidance preflight built:** `scripts/eval186_forward_data_preflight.py` deterministically reports forward-data sufficiency + floor + disjointness by reusing the sealed runner's own helpers (`e186.EARLIEST_FORWARD_CAPTURE_END`, `e186._underlying_floor_strict`, `e186.check_forward_disjointness`). It emits the exact acquisition + follow-up commands. "No runnable-now heavy work" is no longer a defensible claim without showing its verdict.
> 3. **eval84cap absence recorded (was falsely "present"):** `data/raw/eval84cap` is **MISSING** in this checkout. The EVAL-184/185 gates are idempotent no-ops (they read sealed artifacts, not the raw capture), so this does NOT break the sealed gates — but a future agent must not claim eval84cap exists or try to re-verify its floor. Do not substitute it for EVAL-186.
> 4. **Subprocess env trap stays fixed:** any gate/runner subprocess that imports `numpy`/`pandas`/`scipy` MUST set `PYTHONPATH=.venv-deps` (see `_child_env()` in the gates). The preflight `scripts/eval186_forward_data_preflight.py` now self-bootstraps `.venv-deps` on `ModuleNotFoundError`, so `python3 scripts/eval186_forward_data_preflight.py` works with no prefix; the runner `eval186_track_a_fresh_window_replication.py` still needs the `PYTHONPATH=.venv-deps` prefix when run directly.
> 5. **Missing-capture bottleneck resolved earlier:** `data/raw/eval185cap` contains BTC + ETH captures (`three_way_BTC_20261122T110037Z.json`, `three_way_ETH_20261122T110037Z.json`, both non-degenerate). The remaining blocker is data density (under-floor), not absence — see floor diagnostics in the preflight output.
> 6. **Resume-mechanism inaccuracy removed (this session):** the handoff previously claimed "a scheduled wakeup at `2026-11-25T23:39:43Z` carries the campaign forward automatically." That was **false for this repo** — `schedule_wakeup`/`cron_create` are session-scoped and die with the session, and a fresh CI session starts with an empty `cron_list` (verified: `cron_list` ⇒ "No scheduled cron tasks"). The durable resume mechanism is the GitHub Actions **`.github/workflows/main.yml` `cron: "*/5 * * * *"`** ("Kilo General Agent Loop") that launches a fresh agent every ~5 min + this handoff. Correcting this prevents a future session from stalling while waiting for a wakeup that will never arrive — the #1 efficiency risk for the EVAL-186 wait window. The campaign self-resumes: every ~5 min a fresh session reads this file, runs the preflight, and (once `now >= 2026-11-25T23:34:43Z`) proceeds to acquire + seal.
>
> **REPO-NAME PRIORITIZATION (load-bearing, do not re-derive):** the two signal halves are options **surface** and options **order-flow**; the deliverable is a **tradeable, net-of-cost strategy**. Predictiveness EVAL-02..183 is sealed. Order-flow is resolved (EVAL-67/68 predictive GO; EVAL-69 net-of-cost NO-GO). Surface predictiveness has GOs (EVAL-177 skew→variance; EVAL-168/169 atm_iv/term_slope→CVaR), but EVAL-184 monetizes them to `NO-GO CONFIRMED (PASS)` and EVAL-185 proves that NO-GO robust across the cost×horizon grid. The next on-charter heavy work is **temporal robustness on a strictly forward fresh window (EVAL-186)**, gated by the preflight.

## VERIFIED STATE (2026-11-22T14:16:48Z)

- **Driver GREEN at 2484/2484** — `python3 scripts/eval67_prethreshold_progress.py --execute` exit 0; `targeted_tests 2484/2484`, `diagnostic_tests 27/27`, `failures: []`, `gate_exit=0`, gate_phase `SEALED`, all 42 EVAL-67..122 gates `classification: ok`/`exit_code: 0`, all 120 seal_gates ok. (EVAL-184/185/186 are not in the driver's `gates` dict; they are verified by their own gates below.)
- **EVAL-184 SEALED `NO-GO CONFIRMED (PASS)`** — `EVAL_184_SURFACE_TRADED_NETFCOST_OOS_COMBINED_20261122T081750Z.{json,md}` + prereg `..._20261122T065050Z`. Gate `eval184_phaseb_gate.py` → `SEALED`(0), seal-gate 0.
- **EVAL-185 SEALED `NO-GO CONFIRMED (PASS)`** — `EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_COMBINED_20261122T092235Z.{json,md}` (stamp `20261122T092235Z`) + prereg same stamp. 45-config cost×horizon grid; 0 BH-FDR rejections; max pooled returns 2000; power adequate; floor/disjoint OK both. Gate `eval185_phaseb_gate.py` → `SEALED`(0), seal-gate 0.
- **EVAL-186 SEALED `BLOCKED` (2026-11-22T11:30:32Z)** — `EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_BLOCKED_20261122T111006Z.{json,md}` + prereg same stamp. Gate `eval186_phaseb_gate.py` → `SEALED`(0), seal-gate 0 (idempotent no-op). Runner `--no-write` dry-run → `BLOCKED`, `floor_ok: false`, `forward_disjointness_ok: true`, `missing_underlyings: []` (expected under-floor state). Verdict `BLOCKED` (measured; not NO-GO) because `floor_ok: false` — the strictly forward capture at `data/raw/eval185cap` is under the EVAL-64 feasible floor.
- **EVAL-186 preflight `WAIT_FORWARD_DATA` (exit 10)** — `scripts/eval186_forward_data_preflight.py` at session time 2026-11-22T14:16Z: `floor_ok: false`, `disjointness_ok: true`, `earliest_forward_capture_end: 2026-11-25T23:34:43Z`, `seconds_until_earliest_forward_end ≈ 292655`, per-underlying BTC perp_span_seconds ≈ 13800 / ETH ≈ 14100 (vs 300000 floor). Emits the exact `acquire_command` + `followup_commands` for when forward data suffices.
- **EVAL-186 tests:** 29/29 pass (23 runner + 6 preflight). Runner dry-run green (BLOCKED due to under-floor capture — expected).
- **Capture state:** `data/raw/eval185cap` present (BTC+ETH, ~20 MB, gitignored, LOCAL, non-degenerate, disjoint, but **under-floor** — BTC option_trades 864 / ETH 615 vs 2000; perp_candles 231/236 vs 1000; perp_span ≈ 13800–14100 s vs 300000 s). `data/raw/eval84cap` is **MISSING** in this checkout (gitignored; the sealed EVAL-184/185 gates do not need it — they read sealed artifacts).
- **Resume mechanism (verified this session):** `.github/workflows/main.yml` runs the "Kilo General Agent Loop" on `cron: "*/5 * * * *"` — a fresh session every ~5 min. `cron_list` in a fresh session ⇒ "No scheduled cron tasks" (session-scoped wakeups do not persist). The handoff file is the durable resume mechanism; no session wakeup is required or guaranteed.

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
| **TRACK A fresh-window replication (EVAL-186)** | **EVAL-69 + EVAL-184 on new forward window** | **SEALED `BLOCKED` (stamp `20261122T111006Z`)** — capture acquired but under the EVAL-64 floor; forward disjointness OK; gate idempotent no-op. Re-attempt requires a floor-compliant strictly forward capture (forward data insufficient until `now >= 2026-11-25T23:34:43Z`). Enforced by `scripts/eval186_forward_data_preflight.py` + `scripts/eval186_phaseb_gate.py`. |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not re-run a sealed rung as a substitute for new work.

## CURRENT MANDATED QUEUE (the only remaining on-charter work — EVAL-186 TRACK A fresh-window replication, SEALED BLOCKED)

1. **Env + driver green check (every session):** `./scripts/verify_env.sh` then `python3 scripts/eval67_prethreshold_progress.py --execute`. Require exit 0 (2484/2484 targeted, 27/27 diagnostics, `failures: []`, `gate_exit=0`).
2. **Verify sealed gates idempotently:** `python3 scripts/eval185_phaseb_gate.py` → `SEALED`(0); `python3 scripts/eval184_phaseb_gate.py` → `SEALED`(0); `python3 scripts/eval186_phaseb_gate.py` → `SEALED`(0) idempotent no-op (EVAL-186 sealed BLOCKED, seal-gate 0).
3. **MANDATORY anti-avoidance preflight (run BEFORE any wait/“no work” claim):** `python3 scripts/eval186_forward_data_preflight.py`. Record its verdict in the session report:
   - `WAIT_FORWARD_DATA` (exit 10) — expected until `now >= 2026-11-25T23:34:43Z`. Do NOT claim completion; the wait is a measured wall-clock fact. The `.github/workflows/main.yml` `*/5 * * * *` Actions cron re-launches a fresh session every ~5 min; each such session re-runs this preflight and self-resumes from this handoff (no session wakeup required).
   - `READY_TO_ACQUIRE` (exit 0) — proceed to step 4 using the script's printed `acquire_command`.
   - `BLOCKED_*` (exit 1) — fix the non-disjoint/missing-underlying capture before acquisition.
4. **Re-acquisition + seal (only when the preflight returns `READY_TO_ACQUIRE`, i.e. `now >= 2026-11-25T23:34:43Z`):** run the preflight's printed `acquire_command`:
   ```bash
   python3 scripts/eval60_acquire_three_way.py \
     --underlying BTC --underlying ETH --days 3.7 \
     --end 2026-11-25T23:34:43Z --max-per-expiry 30 \
     --out-dir data/raw/eval185cap --seal
   ```
   (any `--end` ≥ `2026-11-25T23:34:43Z` that is disjoint from both sealed windows is fine; `--end` must be ≥ `PREVIOUS_WINDOW_END + 3.7d = 2026-11-25T23:34:43Z` so a 3.7-day window starting ≥ `2026-11-22T06:46:43Z` is fully in the past with ≥300000 s perp span per underlying). Then verify the EVAL-64 floor, run the preflight again to confirm `READY_TO_ACQUIRE`, then:
   ```bash
   PYTHONPATH=.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py \
     --capture-dir data/raw/eval185cap --no-write     # expect floor_ok:true, forward_ok:true
   python3 scripts/eval186_phaseb_gate.py --execute   # require SEALED (exit 0) + seal-gate exit 0 => NO-GO CONFIRMED (PASS)
   ```
   Under-floor ⇒ `BLOCKED`, never `NO-GO`. Do not substitute `data/raw/eval84cap` (missing in this checkout).
5. **Do NOT re-run / re-litigate / re-seal EVAL-67..185** — historical append-only seals. EVAL-186 is sealed BLOCKED (append-only artifact); do not edit it. EVAL-186 produces a NEW artifact (append-only) only if re-attempted with a floor-compliant forward capture.

## NEXT FOCUS CAMPAIGN (anti-avoidance — future agents must not defer or substitute)

EVAL-185 is SEALED (`20261122T092235Z`): the surface NO-GO is robust to monetization (0/45 grid configs pass the both-asset GO bar). Both traded-form lines are `NO-GO CONFIRMED (PASS)`. EVAL-186 is SEALED `BLOCKED` (stamp `20261122T111006Z`): the temporal robustness replication could not reach `NO-GO CONFIRMED (PASS)` because the strictly forward capture at `data/raw/eval185cap` is under the EVAL-64 feasible floor (real forward data covers only ~5 h of a 3.7-day window; floor needs ≥300000 s perp span per underlying). The dual NO-GO stands on both lines; temporal robustness is `BLOCKED` pending a floor-compliant forward capture.

**The next heavy work:** when `now >= 2026-11-25T23:34:43Z` (the runner's `EARLIEST_FORWARD_CAPTURE_END` = `PREVIOUS_WINDOW_END + ACQUIRE_DAYS`), the preflight returns `READY_TO_ACQUIRE`; acquire a floor-compliant capture at `data/raw/eval185cap`, verify the EVAL-64 floor, and re-attempt EVAL-186 to reach `NO-GO CONFIRMED (PASS)`. Until then, EVAL-186's sealed BLOCKED stands — do not treat it as incomplete, do not weaken the floor, do not invent substitute rungs. **The `.github/workflows/main.yml` `*/5 * * * *` Actions cron re-launches a fresh session every ~5 min; each fresh session re-runs the preflight and self-resumes from this handoff — no session wakeup is required or guaranteed (`cron_list` in a fresh session is empty by design). If you are up before then and the preflight says `WAIT_FORWARD_DATA`, the only compliant action is to run the preflight, show its verdict, and stop — do not bump this timestamp.**

**ANTI-AVOIDANCE GUARDRAILS (violation = session failure):**
- **Do not claim "no on-charter heavy work" or "nothing to do" without showing the output of `python3 scripts/eval186_forward_data_preflight.py`.** That script is the deterministic anti-avoidance gate; its verdict (`WAIT_FORWARD_DATA` / `READY_TO_ACQUIRE` / `BLOCKED_*`) is the only legitimate basis for a wait.
- Do not claim a session wakeup is pending or will auto-fire — there is none. The durable resume mechanism is `.github/workflows/main.yml` `cron: "*/5 * * * *"` (fresh session every ~5 min) + this handoff; `cron_list` in a fresh session is empty by design. Self-resume from this file; do not stall waiting for a wakeup that will not arrive.
- Do not claim `data/raw/eval185cap` exists without `ls data/raw/eval185cap/three_way_*.json` showing BOTH BTC and ETH files. (It exists: `three_way_BTC_20261122T110037Z.json`, `three_way_ETH_20261122T110037Z.json`, both non-degenerate.)
- **Do not claim `data/raw/eval84cap` exists — it is MISSING in this checkout.** The sealed EVAL-184/185 gates do not need it (they read sealed artifacts). Do not substitute it for EVAL-186.
- Do not substitute `data/raw/eval84cap` for EVAL-186 — the runner enforces `start >= PREVIOUS_WINDOW_END` and will seal `BLOCKED` on overlap.
- Do not weaken the EVAL-64 floor — under-floor is `BLOCKED`, never `NO-GO`.
- Do not treat a green driver + EVAL-184/185 SEALED as session completion — EVAL-186 is the mandated heavy work (sealed BLOCKED pending floor-compliant forward data). Show the preflight verdict every session.
- Do not invent substitute rungs or "parallel" campaigns — the charter is surface + order-flow → net-of-cost alpha; EVAL-186 is the only remaining on-charter rung.
- Do not re-run / re-litigate / re-seal sealed EVAL-02..185 artifacts or `src/`. EVAL-186 is sealed BLOCKED (append-only); the gate returns `SEALED`(0) idempotent no-op.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) COMBINED (EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)`). EVAL-70..183 gates: `SEALED`(0) idempotent. EVAL-184: `SEALED`(0) COMBINED `NO-GO CONFIRMED (PASS)` (`20261122T081750Z`). EVAL-185: `SEALED`(0) COMBINED `NO-GO CONFIRMED (PASS)` (`20261122T092235Z`). `FAILED`(1) fix and rerun.
- Green driver = env OK, `2484/2484` targeted, `27/27` diagnostics, all EVAL-70..183 + EVAL-67/68/69 gates `ok`/`SEALED`, all `seal_gates` ok, `failures: []`, `gate_exit=0`. Green driver + all-sealed through EVAL-185 is completion ONLY for the predictiveness + both traded-form lines; it is **NOT** session completion — the remaining on-charter work is **EVAL-186 TRACK A fresh-window replication**, now **SEALED `BLOCKED`** (stamp `20261122T111006Z`, seal-gate 0) pending a floor-compliant strictly forward capture.
- EVAL-186 completion = `python3 scripts/eval186_phaseb_gate.py` exits `SEALED`(0) with a COMBINED/BLOCKED artifact stamp ≥ `20261122T095117Z` and a passing `check_session_sealed.py` seal-gate. **BLOCKED ACHIEVED (2026-11-22T11:30:32Z):** `SEALED`(0) seal-gate 0, artifact `EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_BLOCKED_20261122T111006Z.{json,md}` (stamp `20261122T111006Z` ≥ `20261122T095117Z`), verdict `BLOCKED` (measured; not NO-GO) due to under-floor capture. The gate will seal `NO-GO CONFIRMED (PASS)` only with: (a) a strictly forward floor-compliant capture at `data/raw/eval185cap`, (b) a green `scripts/eval186_track_a_fresh_window_replication.py --no-write`, (c) a successful `--seal` run. Under-floor/non-disjoint ⇒ `BLOCKED`, never `NO-GO`.
- **Mandatory preflight every session:** `python3 scripts/eval186_forward_data_preflight.py` — exit 10 (`WAIT_FORWARD_DATA`) is the expected state until `2026-11-25T23:34:43Z`; exit 0 (`READY_TO_ACQUIRE`) triggers the acquisition + seal sequence; exit 1 (`BLOCKED_*`) is a real blocker. A session that does not show this verdict has not satisfied the contract.
- The terminal deliverable (tradeable net-of-cost strategy) is currently `NO-GO CONFIRMED (PASS)` on **both** lines (EVAL-69 order-flow, EVAL-184/185 surface). EVAL-186 tests temporal robustness of that dual NO-GO on a fresh forward window; it returned `BLOCKED` (under-floor) because real forward data covering ~5 h of a 3.7-day window is below the EVAL-64 floor (≥300000 s perp span per underlying). Re-attempt once `now >= 2026-11-25T23:34:43Z` (preflight `READY_TO_ACQUIRE`).
- Task-floor-stamp ordering — `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment/tail fixture trap — skewness/kurtosis/variance/CVaR fixtures need dispersed (occasional large jump) increments, never alternating ±drift.
- Signal/target copy-paste bugs in a cloned runner/gate/tests — grep new files for stale ids, signal/target names AND stale helper references before sealing.
- Composite/both-asset GO bar — GO requires BOTH BTC and ETH to pass; single-asset pass is legitimate `NO-GO CONFIRMED (PASS)`; do not relax.
- Surface-bar vs term-bar signal path — `atm_iv`/`skew` via `e71.build_surface_bars`; `term_slope`/`term_ratio` via `e74._term_bars`. Do not cross them.
- No-hyphen/underscore/hyphenated task-label traps — grep for ALL THREE forms before sealing.
- **Subprocess env trap (fixed; do not reintroduce):** any gate/runner/preflight subprocess that imports `numpy`/`pandas`/`scipy` MUST set `PYTHONPATH=.venv-deps` (see `_child_env()` in `eval184_phaseb_gate.py`, `eval185_phaseb_gate.py`, `eval186_phaseb_gate.py`; the preflight and runner need it too when run directly).
- **"Capture is already on disk" is TRUE for `data/raw/eval185cap`** — it is gitignored/LOCAL; `eval185cap` is non-degenerate but under-floor (~20 MB vs the 297 MB floor-compliant `eval84cap`, which is now MISSING). Do not claim eval185cap is missing — it exists (`three_way_BTC_20261122T110037Z.json`, `three_way_ETH_20261122T110037Z.json`). The blocker is data density (under-floor), not absence.
- **"No runnable-now heavy work" avoidance** — EVAL-186 is sealed BLOCKED; re-attempt requires a floor-compliant strictly forward capture (forward data insufficient until `now >= 2026-11-25T23:34:43Z`). Do not invent a substitute rung. The preflight verdict is the only legitimate basis for a wait.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not re-run / re-litigate / re-seal / edit sealed EVAL-02..62, EVAL-64..69, EVAL-70..185 artifacts or `src/`. Append-only for new authorized work. EVAL-184 (`COMBINED_20261122T081750Z`), EVAL-185 (`COMBINED_20261122T092235Z`), EVAL-186 (`BLOCKED_20261122T111006Z`), and EVAL-67/68/69 are historical seals — do not edit them; EVAL-186 produces NEW artifacts (append-only) only if re-attempted with a floor-compliant forward capture.
- Never synthetic / relabeled-as-real; real loaders raise `RealDataUnavailable`; never emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-186 consumes a freshly acquired strictly forward capture (acquire nothing during the compute phase).
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real ⇒ `BLOCKED`, not `NO-GO`.
- Use correct task IDs (`INIT-2026-11-22T09:51:17Z-EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION`); do not use retired compact task IDs.
- Existing `data/raw/eval61|eval67|eval68` captures are git-TRACKED read-only inputs. `data/raw/eval84cap` is **MISSING** in this checkout (was gitignored; do not claim it exists). `data/raw/eval185cap` (~20 MB now; ~300 MB when floor-compliant) is gitignored and must be kept LOCAL and never committed/pushed. No full-suite discovery, no `research_state/` enumeration loops, no timestamped handoff copies.
- No timestamp-only bumps without new verified facts: green driver + green tests + green gates (+ the mandatory preflight verdict). Do not refresh this timestamp without a sealed EVAL-186 re-attempt or a new verified measurement.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (deps are git-ignored, not in checkout):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session. EVAL-184/185/186 + preflight now included (2484 tests):
python3 scripts/eval67_prethreshold_progress.py --execute
#    Require: targeted_tests 2484/2484, diagnostic_tests 27/27, failures: [], gate_exit=0,
#    all EVAL-70..183 + EVAL-67/68/69 gates SEALED/ok, all seal_gates ok.

# 2) Verify sealed gates idempotently:
python3 scripts/eval184_phaseb_gate.py   # EVAL-184 SEALED (COMBINED NO-GO CONFIRMED (PASS)), exit 0
python3 scripts/eval185_phaseb_gate.py   # EVAL-185 SEALED (COMBINED NO-GO CONFIRMED (PASS)), exit 0
python3 scripts/eval186_phaseb_gate.py   # EVAL-186 SEALED (BLOCKED, stamp 20261122T111006Z), exit 0, idempotent no-op

# 3) MANDATORY anti-avoidance preflight (run BEFORE any wait / "no work" claim):
python3 scripts/eval186_forward_data_preflight.py
#    exit 10 WAIT_FORWARD_DATA (expected until now >= 2026-11-25T23:34:43Z) — show this verdict.
#    exit 0  READY_TO_ACQUIRE — run the printed acquire_command + followup_commands.
#    exit 1  BLOCKED_* — fix non-disjoint/missing-underlying capture.

# 4) When preflight says READY_TO_ACQUIRE (now >= 2026-11-25T23:34:43Z):
# python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 3.7 \
#   --end 2026-11-25T23:34:43Z --max-per-expiry 30 --out-dir data/raw/eval185cap --seal
# PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py \
#   --capture-dir data/raw/eval185cap --no-write     # expect floor_ok:true, forward_ok:true
# python3 scripts/eval186_phaseb_gate.py --execute  => require SEALED (exit 0) + seal-gate exit 0.

# 5) Anti-avoidance: green driver + EVAL-184/185 SEALED is completion ONLY for the predictiveness +
#    both traded-form lines. Remaining on-charter work = EVAL-186 TRACK A fresh-window replication
#    (sealed BLOCKED pending floor-compliant forward capture), enforced by the preflight + gate.
#    Do not fake it; do not weaken the EVAL-64 floor.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..185 sealed. **EVAL-63 never sealed.** EVAL-67/68/69 are sealed **COMBINED**: EVAL-67 `GO CONFIRMED` (`20261122T053156Z`), EVAL-68 `GO CONFIRMED` (`20261122T053327Z`), EVAL-69 `NO-GO CONFIRMED (PASS)` (`20261122T053616Z`) — floor OK both underlyings, disjointness OK. The order-flow toxicity→realized-vol slice is **predictive but not tradeable net-of-cost**. The surface-line GOs EVAL-177 (skew→variance) and EVAL-168/169 (atm_iv/term_slope→CVaR) are sealed predictive GOs, but **EVAL-184 monetizes them to `NO-GO CONFIRMED (PASS)`** (`EVAL_184_SURFACE_TRADED_NETFCOST_OOS_COMBINED_20261122T081750Z.{json,md}`; 0 BH-FDR rejections across 12 configs, floor OK BTC+ETH, disjoint OK) on the floor-compliant disjoint capture that was `data/raw/eval84cap` (now MISSING in this checkout; the gate is idempotent and does not need it), and **EVAL-185 proves that NO-GO robust across the 45-config cost×horizon grid** (`EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_COMBINED_20261122T092235Z.{json,md}`; 0 BH-FDR rejections, floor OK BTC+ETH, disjoint OK). **Both signal families now monetize to NO-GO net-of-cost, robustly.** **EVAL-186 TRACK A fresh-window replication is SEALED `BLOCKED` (stamp `20261122T111006Z`, seal-gate 0)** — the runner + gate + tests exist (29/29 pass incl. the new preflight) and the strictly forward capture at `data/raw/eval185cap` is acquired (BTC+ETH, disjoint, non-degenerate) but under the EVAL-64 feasible floor; temporal robustness cannot reach `NO-GO CONFIRMED (PASS)` until `now >= 2026-11-25T23:34:43Z`. Re-attempt only with a floor-compliant forward capture (gated by `scripts/eval186_forward_data_preflight.py`); under-floor ⇒ `BLOCKED`, never `NO-GO`. Enforced by `scripts/eval186_phaseb_gate.py`.