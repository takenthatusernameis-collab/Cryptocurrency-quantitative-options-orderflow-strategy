# SINGLE DURABLE HANDOFF — READ FIRST (the only actionable handoff)

> **INITIAL TASK MESSAGE FOR THE NEXT AGENTIC SESSION — 2026-11-23T14:51:15Z**
> **Repository: `Cryptocurrency-quantitative-options-orderflow-strategy`.**
> **Charter (from the repository name, highest priority):** crypto **OPTIONS surface** + **OPTIONS order-flow** → a **tradeable, net-of-cost alpha strategy** on **REAL public data**. Paper-only. Never synthetic or relabeled. Never weaken the EVAL-64 feasible floor. Sealed rungs are append-only.
>
> **WHERE THE PROGRAM STANDS:** both predictive signal families are sealed, but neither monetizes net-of-cost on the sealed traded-form tests.
> - Predictiveness EVAL-02..183 is sealed (EVAL-63 was never sealed). EVAL-67/68 are predictive `GO CONFIRMED`; EVAL-69 order-flow traded-form is `NO-GO CONFIRMED (PASS)`.
> - Surface traded-form EVAL-184 is `NO-GO CONFIRMED (PASS)` (`20261122T081750Z`), and the EVAL-185 cost×horizon robustness grid is `NO-GO CONFIRMED (PASS)` (`20261122T092235Z`, 0/45 configs pass).
> - The **only terminal verdict campaign** is **EVAL-186 TRACK A fresh-window replication**. It is sealed `BLOCKED` (`20261122T111006Z`, seal-gate 0), not `NO-GO`: the real forward capture is present and disjoint but under the EVAL-64 floor. The earliest possible strictly-forward capture end is **2026-11-25T23:34:43Z**.
> - **EVAL-187 is the new non-verdict heavy-work campaign that runs now while EVAL-186 waits.** It audits every real three-way capture under `data/raw/**/three_way_*.json` and writes a rolling readiness report. It never emits GO/NO-GO and never replaces EVAL-186.
>
> **THIS SESSION'S FRESH VERIFICATION (refreshed 2026-11-23T14:51:15Z):**
> - `eval67_prethreshold_progress.py --execute` at `2026-11-23T14:50:22Z` → **exit 0, `ok:true`, `failures:[]`, `2484/2484` targeted, `27/27` diagnostics passed** (`total_tests_passed: 2511`), readiness `gate_phase=SEALED`/`gate_exit=0`, regenerated `research_state/EVAL_67_PREWINDOW_READINESS.json`.
> - `eval184_phaseb_gate.py`, `eval185_phaseb_gate.py`, `eval186_phaseb_gate.py` all print `SEALED` and exit 0 as idempotent no-ops (COMBINED `20261122T081750Z`, COMBINED `20261122T092235Z`, BLOCKED `20261122T111006Z` respectively).
> - `python3 scripts/eval186_forward_data_preflight.py` at `2026-11-23T14:51:15Z` → **`WAIT_FORWARD_DATA` (exit 10)**: `floor_ok:false`, `disjointness_ok:true`, `missing_underlyings:[]`, `seconds_until_earliest_forward_end=204207.679` (~2.36 days). BTC/ETH are present with disjoint windows (capture spans 319,680 s each), but perp spans are under the 300,000-second floor (BTC/ETH option trades: 864/615; surface snapshots 47/48; perp candles 231/236).
> - `python3 scripts/eval187_real_data_readiness_audit.py --execute` at `2026-11-23T14:51Z` → **`audit_status:PASS`, `ok:true`**: 10 real git-tracked captures, 623,919,229 bytes, 3,236,815 records, 0 SPARSE/DEGENERATE/ERROR; forward capture `data/raw/eval185cap` 2 files OK. `tests/test_eval187_real_data_readiness_audit.py` 5/5 pass. Rolling report: `research_state/EVAL_187_REAL_DATA_READINESS.{json,md}`.
> - `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py --capture-dir data/raw/eval185cap --no-write` at `2026-11-23T14:51Z` → **`BLOCKED`**, `floor_ok:false`, `forward_disjointness_ok:true`, family verdicts `BLOCKED`/`BLOCKED`; **no NO-GO emitted**. This is the correct under-floor behavior against the durable git-tracked forward capture.
> - `data/raw/eval185cap` exists and is git-tracked/committed, but it is the **under-floor** capture (`three_way_{BTC,ETH}_20261122T110037Z.json`). `data/raw/eval84cap` is **MISSING**. `data/raw/eval187rehearsal` is **gitignored and ABSENT on this checkout** (local-only 24h rehearsal capture, not a verdict input). Do not claim any of these is a floor-compliant EVAL-186 capture.
> - **Read-only readiness probe (`2026-11-23T08:44:04Z`, public `deribit.get_tradingview_chart_data`, `BTC-PERPETUAL`, resolution `1`, a 3.7-day fully-past window `2026-11-19T15:56:04Z`→`2026-11-23T08:44:04Z`, no writes):** `status:ok`, `n_ticks:5001`, `span_seconds:300000.0`, `est_5m_bars:1001`. This proves the re-acquisition's perp leg will clear the binding floor (`perp_span >= 300000` and `perp_bars_5m/surface_bars_5m >= 1000`) once `now >= 2026-11-25T23:34:43Z`; the wall-clock wait is therefore sufficient, not a permanent block.
>
> **BOTTLENECK REVIEW (2026-11-23T14:51:15Z) — two findings:**
> 1. **Physical wall-clock block (NOT code-removable, do not try).** EVAL-186 needs a strictly-forward window disjoint from the sealed `2026-11-22T06:46:43Z` end, at least 300,000 s (3.47 d) long. The acquisition fetches Deribit history over `[end-3.7d, end]`; Deribit only returns data up to "now". Therefore a floor-compliant capture cannot exist until `now >= 2026-11-25T23:34:43Z` (~2.36 d away at the `2026-11-23T14:51:15Z` preflight). This is a real data-availability limit, not a bug. The `--days 3.7` window (319,680 s) is deliberately wider than the 300,000 s perp floor; the floor's binding leg is `perp_span >= 300000 s` (Deribit's measured 1m cap = 5001 candles = exactly 300000 s) plus `n_surface_snapshots >= 1000` (3.7 d × 288 = 1065). EVAL-64 (sealed) already cleared this exact floor on its 7d capture, and the `2026-11-23T08:44:04Z` read-only probe above confirms Deribit returns 5001 candles / 300000.0 s for a 3.7-day past window, so re-acquisition after the wall-clock time will satisfy the floor. **Do not edit the controller (`.github/workflows/main.yml`) or skip the heavy driver to shorten the queue.**
> 2. **REMOVED this session — non-durable rehearsal dir broke the EVAL-187 runbook on fresh checkouts.** The prior EVAL-187 runbook step 3 hard-coded `--capture-dir data/raw/eval187rehearsal`, but that dir is **gitignored (`.gitignore:56`) and absent on any fresh checkout/CI runner** (confirmed absent here). Every future agent that followed the old runbook literally would have dry-run the EVAL-186 runner against a missing dir (empty underlyings → vacuous `BLOCKED`), wasting the rehearsal step and never exercising the real under-floor BTC/ETH path. **Fix applied:** the runbook now targets the durable git-tracked `data/raw/eval185cap` (always present, exercises the identical `floor_ok:false → BLOCKED, never NO-GO` path), with the local rehearsal dir demoted to an optional extra. This is a genuine state change (case (c): a new blocker in the EVAL-187 runbook revealed and resolved), which is why this handoff was edited rather than left untouched.
> 3. **Removable inefficiency (standing rule) — the timestamp-bump loop.** The prior ~10 handoff revisions were identical except for a bumped timestamp and a shrinking `seconds_until_earliest_forward_end` (≈190 such wait-sessions are scheduled before the wall-clock clears). Rewriting this handoff with no verdict change is *itself* the failure mode the campaign exists to prevent. **Rule: while the preflight is `WAIT_FORWARD_DATA`, run the heavy driver, the EVAL-187 audit, and the sealed gates; then STOP; do NOT edit this file.** This file is edited ONLY on a genuine state change: (a) preflight flips to `READY_TO_ACQUIRE`, (b) a new append-only EVAL-186 artifact is sealed, (c) a new EVAL-187 audit or rehearsal reveals a new blocker, or (d) a real new blocker appears. The durable resume checkpoint is the regenerated `research_state/EVAL_67_PREWINDOW_READINESS.json` plus `research_state/EVAL_187_REAL_DATA_READINESS.json` and the preflight JSON, not a hand-edited timestamp. **This refresh is genuine: it fixes the non-durable rehearsal-dir bottleneck (finding 2), corrects the capture count to the durable 10, and re-verifies the full mandated suite at `2026-11-23T14:51Z`.**
>
> **START HERE — RUN THESE IN ORDER, EVERY SESSION (this IS the heavy work):**
> 1. `python3 scripts/eval67_prethreshold_progress.py --execute` — require exit 0, `ok:true`, `failures:[]`, **`2484/2484` targeted, `27/27` diagnostics**, all reported gates/seal-gates green, and readiness `gate_phase=SEALED`/`gate_exit=0`. This 2,484-test + 27-diagnostic driver is the mandatory heavy compute; a session that runs only the preflight has NOT done heavy work and is non-compliant.
> 2. `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval187_real_data_readiness_audit.py --execute` — require exit 0, `ok:true`, and a regenerated `research_state/EVAL_187_REAL_DATA_READINESS.json`/`.md`. Show `audit_status`, `capture_count`, `total_bytes`, `total_records`, `status_counts`, and `forward_capture`. This is the real-data heavy-work audit; a session that skips it has not satisfied the anti-avoidance contract. Also run `PYTHONPATH=$PWD/.venv-deps python3 -m pytest -q tests/test_eval187_real_data_readiness_audit.py`.
> 3. `python3 scripts/eval184_phaseb_gate.py`; `python3 scripts/eval185_phaseb_gate.py`; `python3 scripts/eval186_phaseb_gate.py` — each must print `SEALED` and exit 0 while the corresponding rung is sealed.
> 4. **`python3 scripts/eval186_forward_data_preflight.py` — MANDATORY anti-avoidance gate. Run it BEFORE any wait / "nothing to do" claim, and show its verdict verbatim.**
>    - `WAIT_FORWARD_DATA` (exit 10) — expected now. This is a measured wall-clock fact, not a missing-data excuse. After steps 1–4, report the verdict and **stop**. Do NOT rewrite this handoff. Do NOT invent a substitute rung or fabricate a measurement.
>    - `READY_TO_ACQUIRE` (exit 0) — execute the runbook below. This is the only path to a new EVAL-186 verdict.
>    - `BLOCKED_*` (exit 1) — resolve missing/non-disjoint/under-floor capture issues before acquisition. Under-floor or non-disjoint data is `BLOCKED`, **never** `NO-GO`.
>
> **RESUME MECHANISM:** this file is the durable resume mechanism. The scheduled `.github/workflows/main.yml` workflow re-enters fresh sessions; `schedule_wakeup`/`cron_create` are session-scoped and are not the campaign resume. The campaign self-resumes when the scheduled preflight reaches `READY_TO_ACQUIRE` at or after **2026-11-25T23:34:43Z**. Do not stall waiting for a wakeup.

## NEXT FOCUS CAMPAIGNS (anti-avoidance)

### EVAL-187 — REAL-DATA READINESS & ACQUISITION REHEARSAL (non-verdict; runs now)

**EVAL-187** is the new anti-idle heavy-work campaign. It is **not a substitute for EVAL-186**, does **not** emit a GO/NO-GO verdict, and does **not** modify sealed artifacts or `src/`. It runs every session while EVAL-186 waits for the `2026-11-25T23:34:43Z` wall-clock threshold.

**What it does:** scans every real `three_way_*.json` capture under `data/raw/`, parses each capture, and reports:
- schema, underlying, venue, window start/end, capture span;
- surface snapshots / 5m bars / instruments / quotes / bid-ask / mark / IV coverage;
- option-trade count / price-size / instrument / timestamp coverage and span;
- perp-candle count / OHLC / timestamp coverage and span;
- OKX perp-trade count / price-size / timestamp coverage and span;
- source provenance (`public_read_only`, `authenticated`), synthetic markers, and per-capture status (`OK`, `SPARSE`, `DEGENERATE`, `ERROR`);
- the forward capture in `data/raw/eval185cap` and its status.

**Heavy-work evidence from the `2026-11-23T14:51Z` session:** 10 real git-tracked `three_way_*.json` captures, 623,919,229 bytes, 3,236,815 records, `audit_status:PASS`, 0 `SPARSE`/`DEGENERATE`/`ERROR`; forward capture `data/raw/eval185cap` 2 files OK; rolling report at `research_state/EVAL_187_REAL_DATA_READINESS.{json,md}`.

**Acquisition rehearsal (LOCAL, NOT DURABLE):** a 24h capture was previously acquired into `data/raw/eval187rehearsal` (`2026-11-23T11:02:36Z`). That directory is **gitignored (`.gitignore:56`) and therefore absent on any fresh checkout/CI runner** — this is the removable bottleneck fixed in this revision. Do NOT depend on `data/raw/eval187rehearsal` existing; it is an optional local extra. The **durable** under-floor rehearsal target is the git-tracked `data/raw/eval185cap` (BTC/ETH `three_way_*_20261122T110037Z.json`), which always exists and exercises the real-data `floor_ok:false → BLOCKED, never NO-GO` path identically.

**Runbook:**
1. `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval187_real_data_readiness_audit.py --execute` — require exit 0, `ok:true`, regenerated rolling JSON/MD, and show the summary.
2. `PYTHONPATH=$PWD/.venv-deps python3 -m pytest -q tests/test_eval187_real_data_readiness_audit.py` — require all pass.
3. `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py --capture-dir data/raw/eval185cap --no-write` — require `BLOCKED` (under-floor), never `NO-GO`. (Durable target. If a local `data/raw/eval187rehearsal` happens to exist, you MAY also dry-run against it, but never require it — it is gitignored and non-durable.)
4. `python3 scripts/eval186_forward_data_preflight.py` — show the authoritative verdict.
5. When preflight is `READY_TO_ACQUIRE`, run the EVAL-186 runbook below; then re-run EVAL-187 to include the new floor-compliant capture.

**Invariant:** EVAL-187 is a rolling, non-verdict audit. It may not be used to claim completion, may not replace EVAL-186, and may not weaken the EVAL-64 floor.

### EVAL-186 — TRACK A fresh-window replication (terminal verdict campaign)

**EVAL-186 TRACK A fresh-window replication** of the dual traded-form NO-GO (EVAL-69 order-flow + EVAL-184 surface) on a **strictly-forward, disjoint, floor-compliant** real BTC+ETH capture. It is sealed `BLOCKED` solely because the current real capture covers only ~5 hours of the required 3.7-day window.

There is no legitimate *verdict* substitute campaign:
- synthetic/relabeled data is prohibited;
- weakening the EVAL-64 floor is prohibited;
- re-running/re-sealing EVAL-02..185 or editing `src/` is prohibited;
- the family runners do not compute a traded-form result without `floor_ok and forward_ok`, so under-floor data has no valid early-analysis shortcut;
- EVAL-187 is a non-verdict readiness audit and cannot produce a GO/NO-GO or replace EVAL-186. The terminal heavy compute/seal is due when the preflight says `READY_TO_ACQUIRE`.

### RUNBOOK — execute these steps IN ORDER when the preflight prints `READY_TO_ACQUIRE` (do not improvise or skip steps)

1. **Re-run the preflight** and confirm `verdict:"READY_TO_ACQUIRE"`, `floor_ok:true`, `disjointness_ok:true`, `missing_underlyings:[]`. Copy its printed `acquire_command` and `followup_commands`.
2. **Acquire** a floor-compliant, strictly-forward capture (this is the `acquire_command`); it writes `three_way_{BTC,ETH}_<stamp>.json` under `data/raw/eval185cap` and, with `--seal`, a manifest under `research_state/`. The window must start at/after `2026-11-22T06:46:43Z` and end at/after `2026-11-25T23:34:43Z`, disjoint from the sealed EVAL-64/65 and EVAL-84/185 windows.
3. **Verify the floor on the NEW capture** by re-running `python3 scripts/eval186_forward_data_preflight.py`. It must now report `floor_ok:true` and `disjointness_ok:true`. If it still reports under-floor (`WAIT_FORWARD_DATA`) *after* `now >= 2026-11-25T23:34:43Z`, do NOT silently re-wait: capture the per-underlying `perp_span_seconds`/`n_surface_snapshots`/trade counts as evidence, treat it as an acquisition defect (`BLOCKED` with the diagnosis recorded in the handoff), and investigate the fetch (e.g. Deribit returning fewer than 5001 perp candles).
4. **Dry-run compute:** `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py --capture-dir data/raw/eval185cap --no-write`. Require a clean exit and a `floor_and_disjoint_ok:true` report. If it reports `BLOCKED`, do not seal a NO-GO.
5. **Seal:** `python3 scripts/eval186_phaseb_gate.py --execute`. This is the only step that may produce a NEW append-only EVAL-186 artifact (`NO-GO CONFIRMED (PASS)`, `GO CONFIRMED`, or `INCONCLUSIVE (UNDERPOWERED)` per the pre-registered go-bar). Confirm the artifact stamp ≥ `20261122T095117Z` and the seal-gate passes.
6. **Update this handoff** (this is a genuine state change): set the new INITIAL TASK MESSAGE timestamp, record the sealed artifact name/stamp, and update the ledger row for EVAL-186.

## MANDATED SESSION PROTOCOL

While the preflight returns `WAIT_FORWARD_DATA`:
1. Run the heavy driver (step 1).
2. Run the EVAL-187 audit (step 2) and its tests; require `ok:true` and show the summary.
3. Run the three sealed gates (step 3); all must be green/no-op.
4. Run the preflight (step 4) and show its `WAIT_FORWARD_DATA` verdict, `floor_ok`, `disjointness_ok`, `missing_underlyings`, and `seconds_until_earliest_forward_end`.
5. Let the driver regenerate `research_state/EVAL_67_PREWINDOW_READINESS.json` and the audit regenerate `research_state/EVAL_187_REAL_DATA_READINESS.json`; those regenerations are the legitimate verifiable checkpoints.
6. **Stop. Do NOT edit this handoff.** Do not invent substitute rungs, rerun/reseal EVAL-02..185, weaken the floor, or fabricate a new measurement to justify a timestamp bump. A green driver plus a green EVAL-187 audit plus the preflight verdict is a complete compliant heavy session. Rewriting this file without a verdict change is the exact inefficiency this campaign forbids.

## CAMPAIGN LEDGER (sealed rungs append-only; EVAL-187 is a rolling non-verdict audit)

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
| Real-data readiness & acquisition rehearsal | EVAL-187 | ACTIVE — NON-VERDICT rolling audit; 10 git-tracked captures / 623,919,229 B / 3,236,815 records; `audit_status:PASS` (`20261123T1451Z`); durable under-floor dry-run target `data/raw/eval185cap` |

All verdicts live in `research_state/EVAL_<n>_*.md`. Do not rerun a sealed rung as a substitute for new work.

## DETERMINISTIC COMPLETION CONTRACT

- EVAL-67/68/69: `SEALED`(0) COMBINED (EVAL-67 GO, EVAL-68 GO, EVAL-69 `NO-GO CONFIRMED (PASS)`). EVAL-70..183 gates: `SEALED`(0) idempotent. EVAL-184: `SEALED`(0) COMBINED `NO-GO CONFIRMED (PASS)` (`20261122T081750Z`). EVAL-185: `SEALED`(0) COMBINED `NO-GO CONFIRMED (PASS)` (`20261122T092235Z`). `FAILED`(1) means fix and rerun.
- Green driver means env OK, `2484/2484` targeted, `27/27` diagnostics, `failures:[]`, `ok=true`, `exit_code=0`, all reported gates/seal-gates green, and readiness `gate_phase=SEALED`/`gate_exit=0`. Green driver plus a green EVAL-187 audit plus all-sealed through EVAL-185 completes only the predictiveness, both traded-form lines, and the real-data readiness audit; it is **not** completion of the remaining EVAL-186 campaign.
- EVAL-187: `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval187_real_data_readiness_audit.py --execute` must exit 0 with `ok:true` and a regenerated `research_state/EVAL_187_REAL_DATA_READINESS.{json,md}`. `audit_status:PASS` or `ATTENTION` is acceptable; `ERROR` is not. EVAL-187 is non-verdict and never completes EVAL-186.
- EVAL-186 completion requires `python3 scripts/eval186_phaseb_gate.py` to exit `SEALED`(0) with a COMBINED/BLOCKED artifact stamp ≥ `20261122T095117Z` and a passing `check_session_sealed.py` seal-gate. The current BLOCKED artifact is `EVAL_186_TRACK_A_FRESH_WINDOW_REPLICATION_BLOCKED_20261122T111006Z.{json,md}`. The gate seals `NO-GO CONFIRMED (PASS)` only with (a) a strictly forward floor-compliant capture at `data/raw/eval185cap`, (b) a green runner `--no-write`, and (c) a successful `--seal` run. Under-floor/non-disjoint is `BLOCKED`, never `NO-GO`.
- Mandatory preflight every session: exit 10 (`WAIT_FORWARD_DATA`) is expected until `2026-11-25T23:34:43Z`; exit 0 (`READY_TO_ACQUIRE`) triggers the runbook above; exit 1 (`BLOCKED_*`) is a real blocker. A session that does not show the preflight verdict has not satisfied the contract.
- The terminal deliverable (tradeable net-of-cost strategy) is `NO-GO CONFIRMED (PASS)` on both sealed lines (EVAL-69 order-flow, EVAL-184/185 surface). EVAL-186 tests temporal robustness of that dual NO-GO on a fresh forward window; it is BLOCKED because the real forward data is under the floor, not because the strategy has been rejected on that window.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do not rerun, relitigate, reseal, or edit sealed EVAL-02..62, EVAL-64..69, EVAL-70..185 artifacts or `src/`. EVAL-184 (`COMBINED_20261122T081750Z`), EVAL-185 (`COMBINED_20261122T092235Z`), EVAL-186 (`BLOCKED_20261122T111006Z`), and EVAL-67/68/69 are historical seals. EVAL-186 may produce NEW append-only artifacts only after a floor-compliant forward reattempt.
- Never use synthetic/relabeled data; real loaders must raise `RealDataUnavailable` rather than emit `{"valid": true}`. Public read-only network only; polite rate limiting. EVAL-186 acquires in the acquisition phase and computes on the fresh capture without acquiring during compute.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- No pre-registered floor weakening. Under-floor, missing-underlying, or non-disjoint non-empty real data is `BLOCKED`, not `NO-GO`.
- Use the correct task ID `INIT-2026-11-22T09:51:17Z-EVAL186-TRACK-A-FRESH-WINDOW-REPLICATION`; do not use retired compact task IDs.
- Existing `data/raw/eval61|eval67|eval68` captures are git-tracked read-only inputs. `data/raw/eval84cap` is MISSING (gitignored; never claim it exists). `data/raw/eval185cap` is git-tracked/committed but under-floor; keep any floor-compliant re-acquisition LOCAL and never commit/push it. `data/raw/eval187rehearsal` is a **gitignored, non-durable local** 24h under-floor rehearsal capture (absent on fresh checkouts); never commit/push it, never use it as a verdict input, and never make any runbook step depend on its presence. No full-suite discovery, no `research_state/` enumeration loops, and no timestamped handoff copies.
- Do not use EVAL-187 as a substitute for EVAL-186, do not emit GO/NO-GO from the audit, and do not weaken the EVAL-64 floor to make the rehearsal capture look compliant.
- **No timestamp-only refresh.** Do not bump this handoff's timestamp without a genuine state change (preflight verdict change, a newly sealed EVAL-186 artifact, a new EVAL-187 audit/rehearsal blocker, or a real new blocker). This refresh is backed by the driver run at `2026-11-23T14:50:22Z` (2484/2484 targeted, 27/27 diagnostics, `ok:true`, `failures:[]`, exit 0, readiness `gate_phase=SEALED`/`gate_exit=0`), the three sealed gate runs (all `SEALED` exit 0), the `WAIT_FORWARD_DATA` preflight at `2026-11-23T14:51:15Z`, the EVAL-187 audit at `2026-11-23T14:51Z` (`audit_status:PASS`, 10 captures), the `tests/test_eval187_real_data_readiness_audit.py` 5/5 pass, the EVAL-186 runner correctly returning `BLOCKED` on `data/raw/eval185cap`, and **the genuine state change that the non-durable `data/raw/eval187rehearsal` dir is absent on this checkout (gitignored) — its runbook dependency was removed this revision**.
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

# 2) EVAL-187 real-data readiness audit (mandatory every session):
PYTHONPATH=$PWD/.venv-deps python3 scripts/eval187_real_data_readiness_audit.py --execute
PYTHONPATH=$PWD/.venv-deps python3 -m pytest -q tests/test_eval187_real_data_readiness_audit.py
# Require: ok=true, exit 0, audit_status PASS or ATTENTION, rolling JSON/MD regenerated.

# 3) Verify sealed gates idempotently:
python3 scripts/eval184_phaseb_gate.py
python3 scripts/eval185_phaseb_gate.py
python3 scripts/eval186_phaseb_gate.py

# 4) EVAL-186 under-floor dry-run (durable git-tracked target => BLOCKED, never NO-GO):
PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py \
  --capture-dir data/raw/eval185cap --no-write
# (Optional local extra ONLY if data/raw/eval187rehearsal exists; it is gitignored/non-durable.)

# 5) Mandatory anti-avoidance preflight (before any wait/no-work claim):
python3 scripts/eval186_forward_data_preflight.py
# exit 10 WAIT_FORWARD_DATA (expected until 2026-11-25T23:34:43Z)
# exit 0 READY_TO_ACQUIRE (run printed acquire_command + followup_commands)
# exit 1 BLOCKED_* (resolve capture/disjointness/floor issue)

# 6) When READY_TO_ACQUIRE, the preflight prints the exact acquisition and
# followup commands. In current form they are:
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH \
  --days 3.7 --end <now ≥ 2026-11-25T23:34:43Z> --max-per-expiry 30 \
  --out-dir data/raw/eval185cap --seal
PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py \
  --capture-dir data/raw/eval185cap --no-write
python3 scripts/eval186_phaseb_gate.py --execute
# Under-floor => BLOCKED, never NO-GO. Do not substitute data/raw/eval84cap.
# After the new capture, re-run step 2 so EVAL-187 includes it.
```

Targeted/diagnostic pytest runs need `PYTHONPATH=$PWD/.venv-deps` (the driver sets it itself via `_child_env`).

## SEALED STATE (immutable; append only)

EVAL-02..62, 64..185 are sealed. **EVAL-63 was never sealed.** EVAL-67/68/69 are sealed COMBINED: EVAL-67 `GO CONFIRMED` (`20261122T053156Z`), EVAL-68 `GO CONFIRMED` (`20261122T053327Z`), EVAL-69 `NO-GO CONFIRMED (PASS)` (`20261122T053616Z`) — floor OK both underlyings, disjointness OK. The order-flow toxicity→realized-vol slice is predictive but not tradeable net-of-cost. Surface predictive GOs EVAL-177 (skew→variance) and EVAL-168/169 (atm_iv/term_slope→CVaR) are sealed, but EVAL-184 monetizes them to `NO-GO CONFIRMED (PASS)` (0 BH-FDR rejections across 12 configs), and EVAL-185 proves that NO-GO robust across the 45-config cost×horizon grid. **EVAL-186 TRACK A fresh-window replication is SEALED `BLOCKED` (stamp `20261122T111006Z`, seal-gate 0)**; its runner, gate, tests, and preflight are present, and the current strictly-forward capture is disjoint but under the EVAL-64 floor. Reattempt only with a floor-compliant forward capture; under-floor ⇒ `BLOCKED`, never `NO-GO`. **EVAL-187 is not sealed and is not a verdict rung**; it is the active non-verdict real-data readiness audit described above.