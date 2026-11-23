# SINGLE DURABLE HANDOFF — READ FIRST (the only actionable handoff)

> **INITIAL TASK MESSAGE FOR THE NEXT AGENTIC SESSION — 2026-11-23T07:41:42Z**
> **Repository: `Cryptocurrency-quantitative-options-orderflow-strategy`.**
> **Charter (from the repository name, highest priority):** crypto **OPTIONS surface** + **OPTIONS order-flow** → a **tradeable, net-of-cost alpha strategy** on **REAL public data**. Paper-only. Never synthetic or relabeled. Never weaken the EVAL-64 feasible floor. Sealed rungs are append-only.
>
> **WHERE THE PROGRAM STANDS:** both predictive signal families are sealed, but neither monetizes net-of-cost on the sealed traded-form tests.
> - Predictiveness EVAL-02..183 is sealed (EVAL-63 was never sealed). EVAL-67/68 are predictive `GO CONFIRMED`; EVAL-69 order-flow traded-form is `NO-GO CONFIRMED (PASS)`.
> - Surface traded-form EVAL-184 is `NO-GO CONFIRMED (PASS)` (`20261122T081750Z`), and the EVAL-185 cost×horizon robustness grid is `NO-GO CONFIRMED (PASS)` (`20261122T092235Z`, 0/45 configs pass).
> - The **only remaining on-charter campaign** is **EVAL-186 TRACK A fresh-window replication**. It is sealed `BLOCKED` (`20261122T111006Z`, seal-gate 0), not `NO-GO`: the real forward capture is present and disjoint but under the EVAL-64 floor. The earliest possible strictly-forward capture end is **2026-11-25T23:34:43Z**.
>
> **THIS SESSION'S FRESH VERIFICATION (refreshed 2026-11-23T07:41:42Z):**
> - `eval67_prethreshold_progress.py --execute` at `2026-11-23T07:41:31Z` → **exit 0, `ok:true`, `failures:[]`, `2484/2484` targeted passed, `27/27` diagnostics passed, readiness `gate_phase=SEALED`/`gate_exit=0`**, regenerated `research_state/EVAL_67_PREWINDOW_READINESS.json`.
> - `eval184_phaseb_gate.py`, `eval185_phaseb_gate.py`, `eval186_phaseb_gate.py` all print `SEALED` and exit 0 as idempotent no-ops (COMBINED `20261122T081750Z`, COMBINED `20261122T092235Z`, BLOCKED `20261122T111006Z` respectively).
> - `python3 scripts/eval186_forward_data_preflight.py` at `2026-11-23T07:41:42Z` → **`WAIT_FORWARD_DATA` (exit 10)**: `floor_ok:false`, `disjointness_ok:true`, `missing_underlyings:[]`, `seconds_until_earliest_forward_end=229980.289` (~2.66 days). BTC/ETH are present with disjoint windows (capture spans 319,680 s each), but perp spans are 13,800/14,100 seconds versus the 300,000-second floor (BTC/ETH option trades: 864/615).
> - `data/raw/eval185cap` exists and is git-tracked/committed, but it is the **under-floor** capture. `data/raw/eval84cap` is **MISSING**. Do not claim either is a floor-compliant EVAL-186 capture.
> - The heavy driver passes **2484/2484** targeted and **27/27** diagnostics (exit 0, readiness `gate_phase=SEALED`/`gate_exit=0`).
>
> **BOTTLENECK REVIEW (2026-11-23T07:41:42Z):** no writable campaign bottleneck remains. The five-minute controller can dispatch repeated waiting sessions, but `.github/workflows/main.yml` is controller-managed and the checkpoint code explicitly restores it; do not edit the controller or skip the heavy driver to shorten the queue. Run the complete verification sequence once per session and stop while the preflight is `WAIT_FORWARD_DATA`. The fresh-checkout partial-environment crash in `scripts/eval186_forward_data_preflight.py` was already fixed (validates `numpy`, `scipy`, `pydantic`, `yaml` and bootstraps `requirements.txt` into `.venv-deps`). All acquisition/compute/gate/preflight scripts are present and functional. The only remaining campaign block is the measured wall-clock dependency (`now < 2026-11-25T23:34:43Z`). Do not remove or weaken the 2,484-test heavy driver, the preflight, or the EVAL-64 floor.
>
> **START HERE — RUN THESE IN ORDER, EVERY SESSION:**
> 1. `python3 scripts/eval67_prethreshold_progress.py --execute` — require exit 0, `ok:true`, `failures:[]`, `2484/2484` targeted, `27/27` diagnostics, all reported gates/seal-gates green, and readiness `gate_phase=SEALED`.
> 2. `python3 scripts/eval184_phaseb_gate.py`; `python3 scripts/eval185_phaseb_gate.py`; `python3 scripts/eval186_phaseb_gate.py` — each must print `SEALED` and exit 0 while the corresponding rung is sealed.
> 3. **`python3 scripts/eval186_forward_data_preflight.py` — MANDATORY anti-avoidance gate. Run it BEFORE any wait / "nothing to do" claim, and show its verdict verbatim.**
>    - `WAIT_FORWARD_DATA` (exit 10) — expected now. This is a measured wall-clock fact, not a missing-data excuse. After the driver/gates, report the verdict and stop; do not invent a substitute rung or fabricate a measurement.
>    - `READY_TO_ACQUIRE` (exit 0) — run the printed `acquire_command`, then the printed `followup_commands` (dry-run, then `eval186_phaseb_gate.py --execute`) to reach a new append-only EVAL-186 verdict.
>    - `BLOCKED_*` (exit 1) — resolve missing/non-disjoint/under-floor capture issues before acquisition. Under-floor or non-disjoint data is `BLOCKED`, **never** `NO-GO`.
>
> **RESUME MECHANISM:** this file is the durable resume mechanism. The scheduled `.github/workflows/main.yml` workflow re-enters fresh sessions; `schedule_wakeup`/`cron_create` are session-scoped and are not the campaign resume. The campaign self-resumes when the scheduled preflight reaches `READY_TO_ACQUIRE` at or after **2026-11-25T23:34:43Z**. Do not stall waiting for a wakeup.

## NEXT FOCUS CAMPAIGN (anti-avoidance)

**EVAL-186 TRACK A fresh-window replication** of the dual traded-form NO-GO (EVAL-69 order-flow + EVAL-184 surface) on a **strictly-forward, disjoint, floor-compliant** real BTC+ETH capture. It is sealed `BLOCKED` solely because the current real capture covers only about five hours of the required 3.7-day window.

There is no legitimate substitute campaign:
- synthetic/relabeled data is prohibited;
- weakening the EVAL-64 floor is prohibited;
- re-running/re-sealing EVAL-02..185 or editing `src/` is prohibited;
- the family runners do not compute a traded-form result without `floor_ok and forward_ok`, so under-floor data has no valid early-analysis shortcut;
- any newly invented parallel campaign would necessarily violate one of those invariants. The required heavy work now is the driver plus the preflight; the heavy compute/seal is due when the preflight says `READY_TO_ACQUIRE`.

When ready, the acquisition must produce a window of at least 3.7 days starting at/after `2026-11-22T06:46:43Z`, ending at/after `2026-11-25T23:34:43Z`, disjoint from the sealed EVAL-64/65 and EVAL-84/185 windows. Verify the floor, rerun the preflight, run `eval186_track_a_fresh_window_replication.py --no-write`, then seal with `eval186_phaseb_gate.py --execute`. Only then may EVAL-186 produce a new append-only `COMBINED` artifact (`NO-GO CONFIRMED (PASS)`, `GO CONFIRMED`, or `INCONCLUSIVE (UNDERPOWERED)` per the pre-registered go-bar).

## MANDATED SESSION PROTOCOL

While the preflight returns `WAIT_FORWARD_DATA`:
1. Run the heavy driver and the three sealed gates; all must be green/no-op.
2. Run the preflight and show its `WAIT_FORWARD_DATA` verdict, `floor_ok`, `disjointness_ok`, `missing_underlyings`, and `seconds_until_earliest_forward_end`.
3. Let the driver regenerate `research_state/EVAL_67_PREWINDOW_READINESS.json`; that regeneration is the legitimate verifiable checkpoint. Do not manufacture extra edits on top of it.
4. Stop. Do not invent substitute rungs, rerun/reseal EVAL-02..185, weaken the floor, or fabricate a new measurement to justify a timestamp bump. A green driver plus the preflight verdict is a complete compliant waiting session.

## CAMPAIGN LEDGER (sealed; append-only)

| block | rungs | state |
|---|---|---|
| On-charter predictiveness ladder EVAL-02..66 | — | CLOSED (EVAL-63 never sealed) |
| Forward disjoint-window ladder | EVAL-67/68/69 | SEALED COMBINED — EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)` |
| Physics-independent predictiveness | EVAL-70..160 | SEALED |
| Single-asset surface → forward CVaR | EVAL-161/162/163/164 | SEALED (163 GO; others NO-GO CONFIRMED (PASS)) |
| Single-asset surface → downside-semivariance share | EVAL-115, 165, 166, 167 | SEALED |
| Cross-asset surface/term → forward signed return mean | EVAL-148 (4 cells) | SEALED COMPLETE |
| Cross-asset options order-flow → signed mean/skew/downside/kurt/var | EVAL-149..160 | SEALED COMPLETE |
| Cross-asset surface/term → forward CVaR | EVAL-168 (atm_iv), 169 (term_slope), 170 (term_ratio), 171 (skew) | SEALED |
| Single-asset surface → forward variance | EVAL-172..175 | SEALED (grid COMPLETE) |
| Cross-asset surface → forward variance | EVAL-176..179 | SEALED COMPLETE (177 GO; others NO-GO) |
| Cross-asset order-flow × surface interaction | EVAL-180/181/182/183 | SEALED (`NO-GO CONFIRMED (PASS)` each) |
| Surface-line traded-form net-of-cost OOS | EVAL-184 | SEALED `NO-GO CONFIRMED (PASS)` (`20261122T081750Z`) |
| Surface-line traded-form robustness grid | EVAL-185 | SEALED `NO-GO CONFIRMED (PASS)` (`20261122T092235Z`) — 0/45 configs pass |
| TRACK A fresh-window replication | EVAL-186 | SEALED `BLOCKED` (`20261122T111006Z`) — under-floor forward capture; preflight + gate enforce the wall-clock wait |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not rerun a sealed rung as a substitute for new work.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) COMBINED (EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)`). EVAL-70..183 gates: `SEALED`(0) idempotent. EVAL-184: `SEALED`(0) COMBINED `NO-GO CONFIRMED (PASS)` (`20261122T081750Z`). EVAL-185: `SEALED`(0) COMBINED `NO-GO CONFIRMED (PASS)` (`20261122T092235Z`). `FAILED`(1) means fix and rerun.
- Green driver means env OK, `2484/2484` targeted, `27/27` diagnostics, `failures:[]`, `ok=true`, `exit_code=0`, all reported gates/seal-gates green, and readiness `gate_phase=SEALED`/`gate_exit=0`. Green driver plus all-sealed through EVAL-185 completes only the predictiveness and both traded-form lines; it is **not** completion of the remaining EVAL-186 campaign.
- EVAL-186 completion requires `python3 scripts/eval186_phaseb_gate.py` to exit `SEALED`(0) with a COMBINED/BLOCKED artifact stamp ≥ `20261122T095117Z` and a passing `check_session_sealed.py` seal-gate. The current BLOCKED artifact is `EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_BLOCKED_20261122T111006Z.{json,md}`. The gate seals `NO-GO CONFIRMED (PASS)` only with (a) a strictly forward floor-compliant capture at `data/raw/eval185cap`, (b) a green runner `--no-write`, and (c) a successful `--seal` run. Under-floor/non-disjoint is `BLOCKED`, never `NO-GO`.
- Mandatory preflight every session: exit 10 (`WAIT_FORWARD_DATA`) is expected until `2026-11-25T23:34:43Z`; exit 0 (`READY_TO_ACQUIRE`) triggers acquisition + seal; exit 1 (`BLOCKED_*`) is a real blocker. A session that does not show this verdict has not satisfied the contract.
- The terminal deliverable (tradeable net-of-cost strategy) is `NO-GO CONFIRMED (PASS)` on both sealed lines (EVAL-69 order-flow, EVAL-184/185 surface). EVAL-186 tests temporal robustness of that dual NO-GO on a fresh forward window; it is BLOCKED because the real forward data is under the floor, not because the strategy has been rejected on that window.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not rerun, relitigate, reseal, or edit sealed EVAL-02..62, EVAL-64..69, EVAL-70..185 artifacts or `src/`. EVAL-184 (`COMBINED_20261122T081750Z`), EVAL-185 (`COMBINED_20261122T092235Z`), EVAL-186 (`BLOCKED_20261122T111006Z`), and EVAL-67/68/69 are historical seals. EVAL-186 may produce NEW append-only artifacts only after a floor-compliant forward reattempt.
- Never use synthetic/relabeled data; real loaders must raise `RealDataUnavailable` rather than emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-186 acquires in the acquisition phase and computes on the fresh capture without acquiring during compute.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real data is `BLOCKED`, not `NO-GO`.
- Use the correct task ID `INIT-2026-11-22T09:51:17Z-EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION`; do not use retired compact task IDs.
- Existing `data/raw/eval61|eval67|eval68` captures are git-tracked read-only inputs. `data/raw/eval84cap` is MISSING (gitignored; never claim it exists). `data/raw/eval185cap` is git-tracked/committed but under-floor; keep any floor-compliant re-acquisition LOCAL and never commit/push it. No full-suite discovery, no `research_state/` enumeration loops, and no timestamped handoff copies.
- No timestamp-only refresh without new verified facts: use the green driver, green gates, and mandatory preflight verdict as evidence. This refresh is backed by the driver run at `2026-11-23T07:41:31Z` (2484/2484 targeted, 27/27 diagnostics, `ok:true`, `failures:[]`, exit 0, readiness `gate_phase=SEALED`/`gate_exit=0`), the three sealed gate runs (all `SEALED` exit 0), and the `WAIT_FORWARD_DATA` preflight at `2026-11-23T07:41:42Z`.
- Task-floor-stamp ordering: `SEAL_SPECS`/gate `TASK_ID` ISO stamps must be ≤ the artifact stamp; use the session start time, never a projected future time.
- Degenerate moment/tail fixtures need dispersed increments with occasional large jumps, never alternating ±drift. Check new runners/gates/tests for stale task IDs, signal/target names, helper references, and all hyphen/underscore task-label variants before sealing.
- Composite/both-asset GO requires BOTH BTC and ETH to pass; single-asset pass remains a legitimate `NO-GO CONFIRMED (PASS)` and must not be relaxed. Use `atm_iv`/`skew` via `e71.build_surface_bars` and `term_slope`/`term_ratio` via `e74._term_bars`; do not cross those paths.

## REPRO / KEY COMMANDS

```bash
# 0) Fresh runner only (dependencies are git-ignored):
./scripts/verify_env.sh

# 1) Full heavy-work loop; run every session:
python3 scripts/eval67_prethreshold_progress.py --execute
# Require: ok=true, exit_code=0, 2484/2484 targeted, 27/27 diagnostics,
# failures: [], all reported gates/seal-gates ok, readiness gate_phase SEALED.

# 2) Verify sealed gates idempotently:
python3 scripts/eval184_phaseb_gate.py
python3 scripts/eval185_phaseb_gate.py
python3 scripts/eval186_phaseb_gate.py

# 3) Mandatory anti-avoidance preflight (before any wait/no-work claim):
python3 scripts/eval186_forward_data_preflight.py
# exit 10 WAIT_FORWARD_DATA (expected until 2026-11-25T23:34:43Z)
# exit 0 READY_TO_ACQUIRE (run printed acquire_command + followup_commands)
# exit 1 BLOCKED_* (resolve capture/disjointness/floor issue)

# 4) When READY_TO_ACQUIRE, the preflight prints the exact acquisition and
# followup commands. In current form they are:
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH \
  --days 3.7 --end 2026-11-25T23:34:43Z --max-per-expiry 30 \
  --out-dir data/raw/eval185cap --seal
PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py \
  --capture-dir data/raw/eval185cap --no-write
python3 scripts/eval186_phaseb_gate.py --execute
# Under-floor => BLOCKED, never NO-GO. Do not substitute data/raw/eval84cap.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..185 are sealed. **EVAL-63 was never sealed.** EVAL-67/68/69 are sealed COMBINED: EVAL-67 `GO CONFIRMED` (`20261122T053156Z`), EVAL-68 `GO CONFIRMED` (`20261122T053327Z`), EVAL-69 `NO-GO CONFIRMED (PASS)` (`20261122T053616Z`) — floor OK both underlyings, disjointness OK. The order-flow toxicity→realized-vol slice is predictive but not tradeable net-of-cost. Surface predictive GOs EVAL-177 (skew→variance) and EVAL-168/169 (atm_iv/term_slope→CVaR) are sealed, but EVAL-184 monetizes them to `NO-GO CONFIRMED (PASS)` (0 BH-FDR rejections across 12 configs), and EVAL-185 proves that NO-GO robust across the 45-config cost×horizon grid. **EVAL-186 TRACK A fresh-window replication is SEALED `BLOCKED` (stamp `20261122T111006Z`, seal-gate 0)**; its runner, gate, tests, and preflight are present, and the current strictly-forward capture is disjoint but under the EVAL-64 floor. Reattempt only with a floor-compliant forward capture; under-floor ⇒ `BLOCKED`, never `NO-GO`.