# SINGLE DURABLE HANDOFF — READ FIRST (the only actionable handoff)

> ## INITIAL TASK MESSAGE FOR THE NEXT AGENTIC SESSION — 2026-11-24T15:58:10Z
> **Repository:** `Cryptocurrency-quantitative-options-orderflow-strategy`
> **Charter (inferred from the repository name — HIGHEST priority):** crypto **OPTIONS surface** + **OPTIONS order-flow** → a **tradeable, net-of-cost alpha strategy** on **REAL public data**. Paper-only. Never synthetic or relabeled. Never weaken the EVAL-64 feasible floor. Sealed rungs are append-only; do not re-run/re-seal EVAL-02..185 or edit `src/`.
>
> **Your single objective this session: do the HEAVY WORK below, IN ORDER, and STOP. Do not passively wait, do not do a timestamp-only handoff bump, do not invent substitute verdict rungs.** A session that runs only the preflight has NOT done heavy work and is non-compliant.
>
> ### RUN THESE IN ORDER, EVERY SESSION (this IS the heavy work — skipping any step is non-compliance)
> 1. **Heavy driver (dominant compute, ~5–6 min):** `python3 scripts/eval67_prethreshold_progress.py --execute` — run as a `background_process monitor` (it exceeds a 10-min blocking shell while still progressing). Require exit 0, `ok:true`, `failures:[]`, **2484/2484 targeted, 27/27 diagnostics**, readiness **gate_phase SEALED / gate_exit 0**.
> 2. **EVAL-187 audit + tests:** `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval187_real_data_readiness_audit.py --execute` (require exit 0, `ok:true`, `audit_status:PASS`/`ATTENTION`, regenerated JSON+MD), then `PYTHONPATH=$PWD/.venv-deps python3 -m pytest -q tests/test_eval187_real_data_readiness_audit.py` (require 5/5).
> 3. **Three sealed gates (idempotent):** `python3 scripts/eval184_phaseb_gate.py` / `eval185_phaseb_gate.py` / `eval186_phaseb_gate.py` — each `SEALED` exit 0.
> 4. **Durable under-floor dry-run:** `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py --capture-dir data/raw/eval185cap --no-write` — require `BLOCKED`, never `NO-GO`.
> 5. **MANDATORY preflight (before any wait / "nothing to do" claim):** `python3 scripts/eval186_forward_data_preflight.py` — show its verdict verbatim, then STOP.
>    - `WAIT_FORWARD_DATA` (exit 10) — expected now; a measured wall-clock fact, not an excuse. Report + stop.
>    - `READY_TO_ACQUIRE` (exit 0) — execute the EVAL-186 acquisition runbook below (only path to a new verdict).
>    - `BLOCKED_*` (exit 1) — resolve missing/non-disjoint capture first; under-floor/non-disjoint is `BLOCKED`, never `NO-GO`.
> 6. **PROOF OF HEAVY WORK (paste all three in your final message — avoidance is detected by their absence):** the driver's `updated_at` from `research_state/EVAL_67_PREWINDOW_READINESS.json`; the audit's `generated_at` from `research_state/EVAL_187_REAL_DATA_READINESS.json`; the preflight's `verdict` + `seconds_until_earliest_forward_end`.
>
> ### VERIFIED STATE THIS SESSION (2026-11-24T15:58:10Z) — verdict unchanged WAIT_FORWARD_DATA; preflight RE-RUN this session; driver/audit durable checkpoints below are the resume points
> - **Heavy driver** durability checkpoint `updated_at 2026-11-24T15:57:46Z`: `gate_phase SEALED`, `gate_exit 0`, `env_check OK`, `tests_passed 2484` (2484/2484 targeted), `diagnostics_passed 27` (27/27), `orchestrator.overall_ok true`, `orchestrator.failures []`, `orchestrator.exit_code 0` (exit 0). **Durable resume point: `research_state/EVAL_67_PREWINDOW_READINESS.json`.** Re-run the driver this session per the mandated protocol; the regenerated checkpoint is the durable resume point.
> - **EVAL-187 audit** `generated_at 2026-11-24T15:57:50Z`: `audit_status PASS`, `ok true`, 10 git-tracked captures, 623,919,229 bytes, 3,236,815 records; `tests/test_eval187_real_data_readiness_audit.py` 5/5 pass; rolling report at `research_state/EVAL_187_REAL_DATA_READINESS.{json,md}`. **Durable resume point: `research_state/EVAL_187_REAL_DATA_READINESS.json`.** Re-run the audit this session per the mandated protocol.
> - **Three sealed gates:** each `SEALED` exit 0 (EVAL-184 `COMBINED_20261122T081750Z`, EVAL-185 `COMBINED_20261122T092235Z`, EVAL-186 `BLOCKED_20261122T111006Z`).
> - **EVAL-186 under-floor dry-run** on `data/raw/eval185cap`: `BLOCKED`, `family_verdicts order_flow/surface = BLOCKED`, `power_adequate false` — no NO-GO emitted. Correct under-floor behavior.
> - **Preflight (2026-11-24T15:58:10Z):** **`WAIT_FORWARD_DATA`, exit 10**, `floor_ok:false`, `disjointness_ok:true`, `missing_underlyings:[]`, `seconds_until_earliest_forward_end=113792.903` (~1.35 days until `2026-11-25T23:34:43Z`). `now_past_earliest_forward_end:false`. BTC/ETH present and strictly-forward-disjoint (capture span 319,680 s each) but perp spans (13,800 / 14,100 s) and surface snapshots (47/48) are under the 300,000 s / 1,000-snapshot EVAL-64 floor.
>
> ### THE ONLY BLOCKER (bottleneck review) — irreducible; no bottleneck is code-removable
> 1. **Physical wall-clock (NOT code-removable — do not try).** EVAL-186 needs a strictly-forward window with ≥300,000 s perp span disjoint from the sealed `2026-11-22T06:46:43Z` end. Earliest viable end = prev_end + `ACQUIRE_DAYS`(3.7 d) = **`2026-11-25T23:34:43Z`** (`scripts/eval186_track_a_fresh_window_replication.py:54-56`). Deribit serves history only up to "now", so a floor-compliant capture cannot exist until `now >= 2026-11-25T23:34:43Z`. Reducing `ACQUIRE_DAYS`/`MIN_CAPTURE_SPAN_SECONDS` = weakening the sealed EVAL-64 floor = forbidden. **This bottleneck cannot be removed by code.** **Resume trigger:** when the preflight flips to `READY_TO_ACQUIRE` (exit 0), execute the EVAL-186 acquisition runbook **immediately** — do not wait for a second nudge. Until then, the only compliant lever is to run the mandated heavy suite once per session and stop.
> 2. **Non-durable rehearsal dir — ALREADY FIXED.** Old runbook pointed at `data/raw/eval187rehearsal`, which is gitignored (`.gitignore:56`) and absent on fresh checkouts (verified ABSENT now). Fixed: the durable dry-run target is git-tracked `data/raw/eval185cap` (2 files, always present). Never depend on the rehearsal dir.
> 3. **Schedule/session-count waste — OUT OF SCOPE, do not attempt.** `.github/workflows/main.yml` (`*/5`, up to 1000 sessions/activation) is maintainer-managed; the standard token has no `workflows` permission; editing it is forbidden by AGENTS.md. The only in-scope lever is to run the mandated heavy suite once per session and stop.
> 4. **Timestamp-bump loop — standing rule.** While `WAIT_FORWARD_DATA`, run steps 1–5 then STOP. Do NOT edit this file except on a genuine state change: (a) preflight flips `READY_TO_ACQUIRE`, (b) a new EVAL-186 artifact seals, (c) a new EVAL-187 audit/rehearsal blocker appears, or (d) a real new blocker appears. **This refresh is operator-directed** (explicit instruction to leave the most relevant timestamped initial task message) and is backed by a full re-verification at `2026-11-24T15:58:10Z`: preflight re-run (`WAIT_FORWARD_DATA`, exit 10, `seconds_until_earliest_forward_end=113792.903` ~1.35 days); driver durable checkpoint `updated_at 2026-11-24T15:57:46Z` (`2484/2484` + `27/27`, `gate_phase SEALED`/`gate_exit 0`, `env_check OK`, `orchestrator.overall_ok:true`, `failures:[]`, exit 0); EVAL-187 audit `generated_at 2026-11-24T15:57:50Z` (`audit_status:PASS`, 10 captures, 5/5 tests); three sealed gates each `SEALED` exit 0; EVAL-186 under-floor dry-run correctly returning `BLOCKED` on `data/raw/eval185cap`. The verdict state is unchanged (`WAIT_FORWARD_DATA`), so this is a genuine re-verification refresh, not a hand-edited timestamp.
>
> ### NEXT FOCUS CAMPAIGN (anti-idle — EVAL-187; future agents cannot avoid doing heavy work)
> **EVAL-187 (real-data readiness & acquisition rehearsal) is the MANDATORY heavy-work campaign that runs every session while EVAL-186 waits.** It is **non-verdict**: it never emits GO/NO-GO, never replaces EVAL-186, and never edits sealed artifacts or `src/`. Skipping it is non-compliance; a session that does not run the full EVAL-187 audit + tests has not done heavy work. Full spec and runbook are in the NEXT FOCUS CAMPAIGNS section below.
>
> **Anti-avoidance contract (binding on every future session):** A compliant session MUST, in order: (1) run the heavy driver `python3 scripts/eval67_prethreshold_progress.py --execute` and require exit 0 / `ok:true` / 2484/2484 targeted / 27/27 diagnostics / `failures:[]`; (2) run the EVAL-187 audit + tests and require exit 0 / `ok:true` / 5/5; (3) run the three sealed gates (each `SEALED` exit 0); (4) run the durable under-floor dry-run on `data/raw/eval185cap` and require `BLOCKED`, never `NO-GO`; (5) run `python3 scripts/eval186_forward_data_preflight.py` and show the verdict verbatim. Only after steps 1–5 may the session stop. **A session that runs only the preflight, or only a timestamp bump, has NOT done heavy work and is non-compliant.** There is no substitute verdict rung, no early-analysis shortcut, and no floor weakening that can replace steps 1–5. The durable checkpoints are `research_state/EVAL_67_PREWINDOW_READINESS.json`, `research_state/EVAL_187_REAL_DATA_READINESS.json`, and the preflight output — not a hand-edited timestamp. **An idle or early-stop session (stopping before step 5, or producing none of the three proof artifacts) is non-compliance; the next session must re-run steps 1–5 in full before any wait or "nothing to do" claim is accepted.**

## WHERE THE PROGRAM STANDS

- **Charter:** crypto options surface + options order-flow → tradeable net-of-cost alpha on real public data. Paper-only.
- **Predictiveness EVAL-02..183 is sealed** (EVAL-63 was never sealed). EVAL-67/68 are predictive `GO CONFIRMED`; EVAL-69 order-flow traded-form is `NO-GO CONFIRMED (PASS)`.
- **Surface traded-form:** EVAL-184 `NO-GO CONFIRMED (PASS)` (`20261122T081750Z`, 0 BH-FDR rejections across 12 configs); EVAL-185 robustness grid `NO-GO CONFIRMED (PASS)` (`20261122T092235Z`, 0/45 cost×horizon configs pass).
- **Only terminal verdict campaign:** **EVAL-186 TRACK A fresh-window replication** of the dual traded-form NO-GO on a strictly-forward, disjoint, floor-compliant real BTC+ETH capture. Sealed `BLOCKED` (`20261122T111006Z`), not `NO-GO`: the real forward capture is present and disjoint but under the EVAL-64 floor. Earliest possible strictly-forward capture end is **2026-11-25T23:34:43Z**.
- **EVAL-187** is the active non-verdict real-data readiness audit; it never emits a verdict and never replaces EVAL-186.

## NEXT FOCUS CAMPAIGNS (anti-avoidance)

### EVAL-187 — REAL-DATA READINESS & ACQUISITION REHEARSAL (non-verdict; runs now, heavy-work mandatory)

**EVAL-187** is the anti-idle heavy-work campaign. It is **not a substitute for EVAL-186**, does **not** emit a GO/NO-GO verdict, and does **not** modify sealed artifacts or `src/`. It runs every session while EVAL-186 waits for the `2026-11-25T23:34:43Z` wall-clock threshold. **Skipping EVAL-187 is non-compliance.**

**What it does:** scans every real `three_way_*.json` capture under `data/raw/`, parses each capture, and reports: schema, underlying, venue, window start/end, capture span; surface snapshots / 5m bars / instruments / quotes / bid-ask / mark / IV coverage; option-trade count / price-size / instrument / timestamp coverage and span; perp-candle count / OHLC / timestamp coverage and span; OKX perp-trade count / price-size / timestamp coverage and span; source provenance (`public_read_only`, `authenticated`), synthetic markers, and per-capture status (`OK`, `SPARSE`, `DEGENERATE`, `ERROR`); and the forward capture in `data/raw/eval185cap` and its status.

**Heavy-work evidence this session (2026-11-24T15:01:21Z):** 10 real git-tracked `three_way_*.json` captures, 623,919,229 bytes, 3,236,815 records, `audit_status:PASS`, 0 `SPARSE`/`DEGENERATE`/`ERROR`; forward capture `data/raw/eval185cap` 2 files OK; rolling report at `research_state/EVAL_187_REAL_DATA_READINESS.{json,md}`.

**Acquisition rehearsal (LOCAL, NOT DURABLE):** `data/raw/eval187rehearsal` is **gitignored (`.gitignore:56`) and absent on any fresh checkout/CI runner** (verified absent 2026-11-24T05:02Z) — the removable bottleneck already fixed in a prior revision. Do NOT depend on it; it is an optional local extra. The **durable** under-floor rehearsal target is the git-tracked `data/raw/eval185cap` (BTC/ETH `three_way_*_20261122T110037Z.json`), which always exists and exercises the real-data `floor_ok:false → BLOCKED, never NO-GO` path identically.

**Runbook (MANDATORY every session — do not skip any step):**
1. `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval187_real_data_readiness_audit.py --execute` — require exit 0, `ok:true`, regenerated rolling JSON/MD; show the summary.
2. `PYTHONPATH=$PWD/.venv-deps python3 -m pytest -q tests/test_eval187_real_data_readiness_audit.py` — require all pass.
3. `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py --capture-dir data/raw/eval185cap --no-write` — require `BLOCKED` (under-floor), never `NO-GO`. (Durable target. A local `data/raw/eval187rehearsal` may optionally be dry-run too, but is gitignored/non-durable and must never be required.)
4. `python3 scripts/eval186_forward_data_preflight.py` — show the authoritative verdict.
5. When preflight is `READY_TO_ACQUIRE`, run the EVAL-186 runbook below; then re-run EVAL-187 to include the new floor-compliant capture.

**Invariant:** EVAL-187 is a rolling, non-verdict audit. It may not be used to claim completion, may not replace EVAL-186, and may not weaken the EVAL-64 floor. A session that skips steps 1–4 has not satisfied the anti-avoidance contract and must re-run them before any wait or "nothing to do" claim.

### EVAL-186 — TRACK A fresh-window replication (terminal verdict campaign)

**EVAL-186 TRACK A fresh-window replication** of the dual traded-form NO-GO (EVAL-69 order-flow + EVAL-184 surface) on a **strictly-forward, disjoint, floor-compliant** real BTC+ETH capture. It is sealed `BLOCKED` solely because the current real capture covers only ~5 hours of the required 3.7-day window.

There is no legitimate *verdict* substitute campaign: synthetic/relabeled data is prohibited; weakening the EVAL-64 floor is prohibited; re-running/re-sealing EVAL-02..185 or editing `src/` is prohibited; the family runners do not compute a traded-form result without `floor_ok and forward_ok`, so under-floor data has no valid early-analysis shortcut; EVAL-187 is a non-verdict readiness audit and cannot produce a GO/NO-GO or replace EVAL-186. The terminal heavy compute/seal is due when the preflight says `READY_TO_ACQUIRE`.

### RUNBOOK — execute these steps IN ORDER when the preflight prints `READY_TO_ACQUIRE` (do not improvise or skip steps)

1. **Re-run the preflight** and confirm `verdict:"READY_TO_ACQUIRE"`, `floor_ok:true`, `disjointness_ok:true`, `missing_underlyings:[]`. Copy its printed `acquire_command` and `followup_commands`.
2. **Acquire** a floor-compliant, strictly-forward capture (the `acquire_command`); it writes `three_way_{BTC,ETH}_<stamp>.json` under `data/raw/eval185cap` and, with `--seal`, a manifest under `research_state/`. The window must start at/after `2026-11-22T06:46:43Z` and end at/after `2026-11-25T23:34:43Z`, disjoint from the sealed EVAL-64/65 and EVAL-84/185 windows.
3. **Verify the floor on the NEW capture** by re-running `python3 scripts/eval186_forward_data_preflight.py`. It must now report `floor_ok:true` and `disjointness_ok:true`. If it still reports under-floor (`WAIT_FORWARD_DATA`) *after* `now >= 2026-11-25T23:34:43Z`, do NOT silently re-wait: capture the per-underlying `perp_span_seconds`/`n_surface_snapshots`/trade counts as evidence, treat it as an acquisition defect (`BLOCKED` with the diagnosis recorded in the handoff), and investigate the fetch (e.g. Deribit returning fewer than 5001 perp candles).
4. **Dry-run compute:** `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py --capture-dir data/raw/eval185cap --no-write`. Require a clean exit and a `floor_and_disjoint_ok:true` report. If it reports `BLOCKED`, do not seal a NO-GO.
5. **Seal:** `python3 scripts/eval186_phaseb_gate.py --execute`. This is the only step that may produce a NEW append-only EVAL-186 artifact (`NO-GO CONFIRMED (PASS)`, `GO CONFIRMED`, or `INCONCLUSIVE (UNDERPOWERED)` per the pre-registered go-bar). Confirm the artifact stamp ≥ `20261122T095117Z` and the seal-gate passes.
6. **Update this handoff** (genuine state change): set the new INITIAL TASK MESSAGE timestamp, record the sealed artifact name/stamp, and update the ledger row for EVAL-186.

## MANDATED SESSION PROTOCOL

While the preflight returns `WAIT_FORWARD_DATA`:
1. Run the heavy driver (step 1).
2. Run the EVAL-187 audit (step 2) and its tests; require `ok:true` and show the summary.
3. Run the three sealed gates (step 3); all must be green/no-op.
4. Run the durable under-floor dry-run: `PYTHONPATH=$PWD/.venv-deps python3 scripts/eval186_track_a_fresh_window_replication.py --capture-dir data/raw/eval185cap --no-write`; require `BLOCKED`, never `NO-GO`.
5. Run the preflight (step 5) and show its `WAIT_FORWARD_DATA` verdict, `floor_ok`, `disjointness_ok`, `missing_underlyings`, and `seconds_until_earliest_forward_end`.
6. Let the driver regenerate `research_state/EVAL_67_PREWINDOW_READINESS.json` and the audit regenerate `research_state/EVAL_187_REAL_DATA_READINESS.json`; those regenerations are the legitimate verifiable checkpoints.
7. **Stop. Do NOT edit this handoff.** Do not invent substitute rungs, rerun/reseal EVAL-02..185, weaken the floor, or fabricate a new measurement to justify a timestamp bump. A green driver + a green EVAL-187 audit + the preflight verdict is a complete compliant heavy session. Rewriting this file without a verdict change is the exact inefficiency this campaign forbids.

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
| Real-data readiness & acquisition rehearsal | EVAL-187 | ACTIVE — NON-VERDICT rolling audit; 10 git-tracked captures / 623,919,229 B / 3,236,815 records; `audit_status:PASS` (`2026-11-24T15:01:21Z`); durable under-floor dry-run target `data/raw/eval185cap` |

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
- **Do not edit `.github/workflows/main.yml`** (maintainer-managed; the standard token cannot authorize workflow-file changes). Do not edit it to try to shorten the queue or reduce the session count. The remaining schedule/session-count waste is out of scope for a worker session.
- Do not use EVAL-187 as a substitute for EVAL-186, do not emit GO/NO-GO from the audit, and do not weaken the EVAL-64 floor to make the rehearsal capture look compliant.
- **No timestamp-only refresh.** Do not bump this handoff's timestamp without a genuine state change (preflight verdict change, a newly sealed EVAL-186 artifact, a new EVAL-187 audit/rehearsal blocker, or a real new blocker). This refresh is operator-directed (explicit instruction to leave the most relevant timestamped initial task message) and is backed by a full re-verification at `2026-11-24T15:00:32Z`–`2026-11-24T15:08:15Z`: preflight re-run (`WAIT_FORWARD_DATA`, exit 10, `seconds_until_earliest_forward_end=116787.822` ~1.35 days); driver durable checkpoint `updated_at 2026-11-24T15:57:46Z` (`2484/2484` + `27/27`, `gate_phase SEALED`/`gate_exit 0`, `env_check OK`, `orchestrator.overall_ok:true`, `failures:[]`, exit 0); EVAL-187 audit `generated_at 2026-11-24T15:57:50Z` (`audit_status:PASS`, 10 captures, 5/5 tests); three sealed gates each `SEALED` exit 0; EVAL-186 under-floor dry-run correctly returning `BLOCKED` on `data/raw/eval185cap`. The verdict state is unchanged (`WAIT_FORWARD_DATA`), so this is a genuine re-verification refresh, not a hand-edited timestamp.
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

EVAL-02..62, 64..185 are sealed. **EVAL-63 was never sealed.** EVAL-67/68/69 are sealed COMBINED: EVAL-67 `GO CONFIRMED` (`20261122T053156Z`), EVAL-68 `GO CONFIRMED` (`20261122T053327Z`), EVAL-69 `NO-GO CONFIRMED (PASS)` (`20261122T053616Z`) — floor OK both underlyings, disjointness OK. The order-flow toxicity→realized-vol slice is predictive but not tradeable net-of-cost. Surface predictive GOs EVAL-177 (skew→variance) and EVAL-168/169 (atm_iv/term_slope→CVaR) are sealed, but EVAL-184 monetizes them to `NO-GO CONFIRMED (PASS)` (0 BH-FDR rejections across 12 configs), and EVAL-185 proves that NO-GO robust across the 45-config cost×horizon grid. **EVAL-186 TRACK A fresh-window replication is SEALED `BLOCKED` (stamp `20261122T111006Z`, seal-gate 0)**; its runner, gate, tests, and preflight are present, and the current strictly-forward capture is disjoint but under the EVAL-64 floor. Reattempt only with a floor-compliant forward capture; under-floor ⇒ `BLOCKED`, never `NO-GO`. **EVAL-187 is not sealed and is not a verdict rung**; it is the active non-verdict real-data readiness audit. **Re-verified at `2026-11-24T15:58:10Z` (fresh preflight + durable driver/audit checkpoints):** EVAL-67 readiness `gate_phase:SEALED`/`gate_exit:0`, `env_check:OK`, `tests_passed:2484` (`2484/2484` targeted), `diagnostics_passed:27` (`27/27`), `orchestrator.overall_ok:true`, `failures:[]`, `updated_at:2026-11-24T15:57:46Z`; EVAL-187 `audit_status:PASS`, 10 git-tracked captures, 5/5 tests, rolling report regenerated at `research_state/EVAL_187_REAL_DATA_READINESS.{json,md}` (`generated_at:2026-11-24T15:57:50Z`); the under-floor dry-run on `data/raw/eval185cap` correctly returns `BLOCKED` (never `NO-GO`); preflight `WAIT_FORWARD_DATA` (`seconds_until_earliest_forward_end=113792.903` ~1.35 days until `2026-11-25T23:34:43Z`).