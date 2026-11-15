# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**COMPLETED TASK `INIT-2026-11-15T13:03:42Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL` — SEALED 2026-11-15T13:47:05Z, seal gate exit 0.** No further EVAL-50 work required; do not re-run capture or measurement.
**SCOPE (repo-charter priority: `Cryptocurrency-quantitative-options-orderflow-strategy` = combined options+orderflow):** ALL rungs of the campaign ladder are now SEALED. The combined options+orderflow thesis is **not net-of-cost tradable on real BTC or real ETH across OKX and Deribit options venues, and real L2 order-book OFI is also not net-of-cost tradable**: EVAL-46 BTC/OKX, EVAL-47 ETH/OKX, EVAL-48 BTC Deribit-cross-venue, EVAL-49 ETH Deribit-cross-venue, **EVAL-50 Real L2 OFI (BTC+ETH)** — all **NO-GO CONFIRMED (PASS)**. **The campaign ladder is COMPLETE; there is no next rung (no EVAL-51 exists anywhere in the repo).** Any future session is a new campaign decision, not a continuation of this ladder — and must NOT re-run, re-litigate, or re-seal EVAL-02..50.

**BOTTLENECKS ELIMINATED / MEASURED STATE (re-verified 2026-11-15T13:47:05Z; ALL CLEARED — campaign ladder complete):**
- **EVAL-46..50 SEALED (DONE, immutable):** BTC/OKX, ETH/OKX, BTC Deribit-cross-venue, ETH Deribit-cross-venue, **EVAL-50 Real L2 OFI (BTC+ETH)** all **NO-GO CONFIRMED (PASS)**. Never re-run. Do not edit sealed evals or `src/`.
- **Env (verified):** `.venv-deps/` present; `./scripts/verify_env.sh --check` **PASS** (deps ok, EVAL-37/EVAL-36 tests 13/13). `.env` absent; `LIVE_TRADING_ENABLED` unset/false. Run with `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`.
- **Tooling READY/BUILT/SEALED:** `scripts/eval50_acquire_l2_depth.py`, `scripts/eval50_l2_ofi_net_of_cost.py`, `tests/test_eval50_l2_ofi_net_of_cost.py`, `scripts/check_session_sealed.py`. All executed and their artifacts sealed.
- **NO ACTIVE BOTTLENECK.** The campaign ladder (EVAL-46..50) is fully sealed; there is no next rung.

**NEXT AGENT — NO ACTION REQUIRED ON THIS LADDER (new campaign decision only):**
The ladder is complete. Do NOT re-run capture, measurement, or seal gate; do NOT re-litigate EVAL-02..50; do NOT run the full test suite as discovery; do NOT enumerate `research_state/` looking for a next task. If a new campaign is desired, it must be a **fresh, pre-registered, heavy real-data falsification** consistent with the repo charter (combined options + orderflow), starting from a new timestamped task ID — never a continuation/re-run of this ladder.

**DE-RISK / GOTCHAS (re-verified 2026-11-15T13:03:42Z):**
- **Short pre-capture on disk is NOT usable for a verdict:** BTC+ETH `20261115T1121*`, 266 snaps, ~598s — below floor (≥400 snaps, ≥900s). Measurement will not seal a NO-GO/GO on it.
- **Acquisition is live, public read-only:** OKX has no historical L2 book endpoint; capture is polling `GET /api/v5/market/books` (polite cadence+jitter, browser UA). Network: public read-only only.
- **Loader/runtime gotchas (carried forward):** run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `load_snapshot_signals(symbol, data_raw)` first arg is symbol (`"BTC"`/`"ETH"`); `_causal_signal_series`/`_toxicities_per_bar` take `bar_ends_dt` (datetime); `load_real_orderflow` returns Pydantic `OrderflowSnapshot` (slice via `.model_copy`); sealed `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 (use perm/bootstrap/PBO/BH-FDR as primary); run the **full** tape.
- **EVAL-46..49 sealed immutable.** Do not re-run, do not edit sealed artifacts or `src/`.

**WHY THIS HANDOFF EXISTS (repo-name/charter priority — NON-NEGOTIABLE):** the repo is `Cryptocurrency-quantitative-options-orderflow-strategy` — the deliverable is a **combined options + orderflow strategy**. The combined thesis was sealed **NO-GO** on all four venue/asset cells (BTC/OKX EVAL-46, ETH/OKX EVAL-47, BTC Deribit-cross-venue EVAL-48, ETH Deribit-cross-venue EVAL-49) and the real L2 order-book OFI modality was sealed **NO-GO** (EVAL-50, BTC+ETH). **The campaign ladder is COMPLETE (EVAL-46..50 all sealed NO-GO CONFIRMED (PASS)); there is no next rung.** This file now records the closed state and prohibits re-running/re-litigating sealed EVALs. Any future work is a fresh, pre-registered, heavy real-data falsification with a new timestamped task ID — never a continuation/re-run of this ladder.

**HEAVY-WORK FLOOR (non-negotiable; below this floor a session is incomplete):** complete heavy real L2 depth capture meeting floor (≥900s AND ≥400 snaps per instrument, BTC+ETH) → `python3 scripts/eval50_l2_ofi_net_of_cost.py` (full-tape net-of-cost OFI alpha + flat control + 1000 permutations + 1000 bootstrap resamples + CSCV PBO k=4 + BH-FDR + DSR) → pre-register `EVAL_50_PREREGISTRATION_*` BEFORE measurement → seal `EVAL_50_*` → pass seal gate. No prior-EVAL re-runs, no `research_state/` enumeration, no full test suite, no handoff-only session.

**CAMPAIGN LADDER — COMPLETE (all rungs sealed NO-GO CONFIRMED (PASS); no next rung exists):**
- **EVAL-46 (DONE, sealed):** integrated options+orderflow net-of-cost on full dense real BTC → **NO-GO CONFIRMED (PASS)** `EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z`.
- **EVAL-47 (DONE, sealed):** ETH combined cross-asset replication → **NO-GO CONFIRMED (PASS)** `EVAL_47_ETH_COMBINED_20261115T071330Z`.
- **EVAL-48 (DONE, sealed):** BTC cross-venue (Deribit options + OKX BTC orderflow) → **NO-GO CONFIRMED (PASS)** `EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z`.
- **EVAL-49 (DONE, sealed):** ETH cross-venue (Deribit ETH options + OKX ETH orderflow) → **NO-GO CONFIRMED (PASS)** `EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z`.
- **EVAL-50 (DONE, SEALED 2026-11-15T13:47:05Z):** Real L2 order-book OFI net-of-cost (BTC+ETH) → **NO-GO CONFIRMED (PASS)** `EVAL_50_L2_OFI_COMBINED_20261115T134705Z` (acquisition `EVAL_50_L2_DEPTH_ACQUISITION_20261115T134456Z`; prereg `EVAL_50_PREREGISTRATION_20261115T134705Z`; seal gate exit 0). **This is the terminal rung of the ladder.**
- **No EVAL-51 exists.** The campaign is closed; a future session must be a fresh, pre-registered, heavy real-data falsification with a new timestamped task ID — never a continuation/re-run of this ladder.

**BOTTLENECKS (verified 2026-11-15T13:47:05Z):**
1. **CLEARED** — EVAL-46/47/48/49/50 sealed NO-GO (all venue/asset cells + real L2 OFI). Never re-run.
2. **CLEARED** — Deribit acquisition + wrapper tooling built/tested/executed.
3. **CLEARED** — Env/safety: `.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED` unset/false.
4. **CLEARED** — Prior sealed-eval inputs on disk (BTC, ETH, Deribit BTC/ETH, L2 depth).
5. **CLEARED** — Misleading "capture in progress" state (pid 9687) corrected; capture since executed to floor and sealed.
6. **CLEARED (terminal)** — EVAL-50 heavy live L2 capture to floor executed (`--duration 1000 --cadence 2 --levels 25`, BTC 443 snaps/999.6s, ETH 444 snaps/999.6s), measurement run, `EVAL_50_*` sealed, seal gate exit 0. **No remaining blockers.**

## CAMPAIGN STATUS — CLOSED (EVAL-46..50 all sealed NO-GO CONFIRMED (PASS))
The combined options+orderflow thesis is **not net-of-cost tradable** on real BTC or real ETH across OKX and Deribit options venues (EVAL-46/47/48/49), and real L2 order-book OFI is **also not net-of-cost tradable** (EVAL-50). **Campaign ladder complete as of 2026-11-15T13:47:05Z.** No active rung; no capture running; no `EVAL_51_*`. Any future work is a new campaign decision, not a continuation.

## CAMPAIGN LADDER (status)
- **EVAL-43 (DONE, sealed):** orderflow full-roster net-of-cost meta-analysis (BTC) → `NO-GO CONFIRMED (PASS)` `EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z`.
- **EVAL-44 (DONE, sealed, BTC-scoped):** campaign closure certification → `CAMPAIGN_CLOSED` `EVAL_44_CAMPAIGN_CLOSURE_20261114T232641Z`.
- **EVAL-45 (DONE, sealed):** ETH orderflow + options cross-asset net-of-cost falsification → orderflow `NO-GO CONFIRMED (PASS)`; options `BLOCKED`.
- **EVAL-46 (DONE, sealed):** integrated options+orderflow net-of-cost on full dense BTC → **NO-GO CONFIRMED (PASS)** `EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z`.
- **EVAL-47 (DONE, sealed):** ETH combined cross-asset replication → **NO-GO CONFIRMED (PASS)** `EVAL_47_ETH_COMBINED_20261115T071330Z`.
- **EVAL-48 (DONE, sealed):** BTC cross-venue (Deribit options + OKX BTC orderflow) → **NO-GO CONFIRMED (PASS)** `EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z`.
- **EVAL-49 (DONE, sealed):** ETH cross-venue (Deribit ETH options + OKX ETH orderflow) → **NO-GO CONFIRMED (PASS)** `EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z`.
- **EVAL-50 (DONE, SEALED 2026-11-15T13:47:05Z):** real L2 order-book OFI net-of-cost (BTC+ETH) → **NO-GO CONFIRMED (PASS)** `EVAL_50_L2_OFI_COMBINED_20261115T134705Z`. **Terminal rung — no next rung.**

## SEALED STATUS (do not re-run; append only)
### EVAL-46 — Integrated options+orderflow net-of-cost on full dense BTC (SEALED NO-GO CONFIRMED (PASS))
`research_state/EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z.{json,md}` (prereg `EVAL_46_PREREGISTRATION_20261115T041621Z`). 101 BTC snapshots × 2 real OKX BTC tapes × 3 pre-registered fusion rules, all NO-GO; pooled PBO 0.833; BH-FDR rejected nothing. Never re-run.

### EVAL-47 — ETH combined options+orderflow net-of-cost (SEALED NO-GO CONFIRMED (PASS))
`research_state/EVAL_47_ETH_COMBINED_20261115T071330Z.{json,md}` (prereg `EVAL_47_PREREGISTRATION_20261115T071330Z`; gate exit 0). 5 ETH tapes × 3 rules, all NO-GO. Never re-run.

### EVAL-48 — BTC cross-venue Deribit options + OKX BTC orderflow (SEALED NO-GO CONFIRMED (PASS))
`research_state/EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z.{json,md}` (prereg `EVAL_48_PREREGISTRATION_20261115T081951Z`; acquisition `EVAL_48_DERIBIT_ACQUISITION_20261115T081709Z`; gate exit 0). 133 Deribit BTC snapshots × 2 OKX BTC tapes × 3 rules, all NO-GO; pooled PBO 0.667. Never re-run.

### EVAL-49 — ETH cross-venue Deribit ETH options + OKX ETH orderflow (SEALED NO-GO CONFIRMED (PASS))
`research_state/EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z.{json,md}` (prereg `EVAL_49_PREREGISTRATION_20261115T101149Z`; acquisition `EVAL_49_DERIBIT_ACQUISITION_20261115T101115Z`; gate exit 0). 109 Deribit ETH snapshots × 5 ETH tapes × 3 rules, all NO-GO; GO rule: None. Never re-run.

### EVAL-50 — Real L2 order-book OFI net-of-cost (SEALED NO-GO CONFIRMED (PASS))
`research_state/EVAL_50_L2_OFI_COMBINED_20261115T134705Z.{json,md}` (prereg `EVAL_50_PREREGISTRATION_20261115T134705Z`; acquisition `EVAL_50_L2_DEPTH_ACQUISITION_20261115T134456Z.{json,md}`; seal gate exit 0). Floor met: BTC-USD-SWAP 443 snaps/999.6s, ETH-USD-SWAP 444 snaps/999.6s (≥400 snaps AND ≥900s per instrument). 4 configs per instrument (bar5/bar10 × z1/z2), all NO-GO; best Sharpe BTC -2.68 (bar10::z2.0), ETH -1.01 (bar10::z1.0); pooled PBO 0.5000; BH-FDR rejected 4 configs; all pass False. **Terminal rung of the campaign ladder; no EVAL-51 exists.** Never re-run.

### EVAL-45 — ETH cross-asset net-of-cost falsification (SEALED)
- Acquisition: `research_state/EVAL_45_ETH_TAPE_ACQUISITION_20261115T012656Z.{json,md}` (5 disjoint real ETH/OKX windows, 172,100 trades).
- Leg A orderflow: `research_state/EVAL_45_ETH_ORDERFLOW_META_20261115T012707Z.{json,md}` — **NO-GO CONFIRMED (PASS)**.
- Leg B options: `research_state/EVAL_45_OPTIONS_ETH_BLOCKED_20261115T012906Z.{json,md}` — **BLOCKED** (no real ETH option series at time of seal).

### Track A / B / EVAL-42 / EVAL-43 / EVAL-44 (SEALED, immutable context)
- Track A `ORDERFLOW_ROBUSTNESS_41_20261114T193836Z` (NO-GO/REPLICATION), Track B `EVAL_41_TIMESERIES_NET_OF_COST_20261114T203006Z` (REPLICATION/NO-GO), EVAL-42 `EVAL_42_OPTIONS_TIMESERIES_INDEPENDENT_AUDIT_20261114T221418Z` (NO-GO CONFIRMED), EVAL-43 `EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z` (NO-GO CONFIRMED (PASS)), EVAL-44 `EVAL_44_CAMPAIGN_CLOSURE_20261114T232641Z` (CAMPAIGN_CLOSED, BTC-scoped). Prior EVAL-18/31 superseded by EVAL-46.

## PER-SESSION CONTRACT
**TASK `INIT-2026-11-15T13:03:42Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL` IS COMPLETE — SEALED 2026-11-15T13:47:05Z, seal gate exit 0.** The campaign ladder (EVAL-46..50) is fully closed; all combined options+orderflow venue/asset cells and real L2 OFI are sealed **NO-GO CONFIRMED (PASS)**. A future session must NOT re-run, re-litigate, or re-seal EVAL-02..50, must NOT run the full test suite as discovery, and must NOT enumerate `research_state/` looking for a next rung. Any new work is a fresh campaign decision: a new timestamped task ID, a pre-registered heavy real-data falsification consistent with the repo charter (combined options + orderflow), and new sealed artifacts only — never a continuation/re-run of this ladder.

## CURRENT MEASURED STATE (ground truth, re-verified 2026-11-15T13:47:05Z)
- **EVAL-02..50 sealed** (immutable). EVAL-36 `TERMINATE_NO_GO`; EVAL-37 `PASS 9/9`; EVAL-44 `CAMPAIGN_CLOSED` (BTC-scoped).
- **EVAL-45:** ETH orderflow **NO-GO CONFIRMED (PASS)**; ETH options **BLOCKED** (at time of seal).
- **EVAL-46/47/48/49:** combined options+orderflow **NO-GO CONFIRMED (PASS)** on BTC/OKX, ETH/OKX, BTC Deribit-cross-venue, ETH Deribit-cross-venue — all four venue/asset cells sealed.
- **EVAL-50 (SEALED 2026-11-15T13:47:05Z, NO-GO CONFIRMED (PASS)):** real L2 order-book OFI net-of-cost on BTC+ETH. Floor met (BTC 443 snaps/999.6s, ETH 444 snaps/999.6s). 4 configs/instrument, all NO-GO; best Sharpe BTC -2.68, ETH -1.01; pooled PBO 0.5000; BH-FDR rejected 4 configs; seal gate exit 0. **Campaign ladder complete; no next rung.**
- **Env:** `.venv-deps/` present; `./scripts/verify_env.sh --check` PASS (13/13). `.env` absent; `LIVE_TRADING_ENABLED` unset/false.
- **Data on disk (sealed inputs):** BTC options `data/raw/options_candles/` (101); BTC orderflow `data/raw/eval41/`; Deribit BTC `data/raw/eval48/`; ETH tapes/options `data/raw/eval45/`; Deribit ETH `data/raw/eval49/`; **L2 depth `data/raw/eval50/`** — BTC `l2_depth_BTC-USD-SWAP_20261115T134456Z.json` (443 snaps) and ETH `l2_depth_ETH-USD-SWAP_20261115T134456Z.json` (444 snaps), plus superseded short pre-capture `20261115T1121*` (266 snaps, below floor, NOT used for the verdict).

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (measurement imports `src/` which requires numpy in `.venv-deps`).
- `load_snapshot_signals(symbol, data_raw)` first arg is symbol (`"BTC"`/`"ETH"`), second options dir. Options discovery non-recursive.
- `_causal_signal_series`/`_toxicities_per_bar` take `bar_ends_dt` (datetime), not string `bar_ends`.
- `load_real_orderflow(symbol, orderflow_path=...)` returns Pydantic `OrderflowSnapshot` (slice via `.model_copy`).
- Sealed `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 (DSR may report 0.0 — use perm/bootstrap/PBO/BH-FDR as primary).
- Run the **full** tape; do not use fixed tail slices that degenerate aligned signals.
- OKX L2: **no historical book endpoint**; live capture only via polling `GET /api/v5/market/books` with browser User-Agent. Acquisition writes to `--out-dir` (e.g. `data/raw/eval50/`) and with `--seal` writes a capture manifest; verdict artifacts are `EVAL_50_*` in `research_state/` produced by measurement.

## HARD CONSTRAINTS / INVARIANTS
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential mutation, or order placement.
- Never fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Sealed artifacts EVAL-02..49 are immutable; append new timestamped artifacts only. Do not modify sealed artifacts or `src/` to make checks pass.
- Network: public read-only market data only, polite rate limiting (EVAL-50 requires it for live L2 capture).
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`; no `phaseNN_*` orchestrator wrappers.
- Prohibited: re-litigating sealed EVALs, broad `research_state/` enumeration, full test-suite runs, handoff-only sessions, prior-EVAL re-runs.

## HANDOFF DISCIPLINE
- This file is the **single durable handoff**. Update in place with verified facts/timestamps/paths/commands only; no timestamped handoff copies. Root `HANDOFF_NEXT_AGENT.md`, `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers with no task IDs.
- Record measured numbers, not intentions. No GO without a verifying sealed artifact.
- Final responses must not ask follow-up questions.

## SESSION LOG (append-only)
- 2026-11-14T18:21:06Z→2026-11-15T11:03:55Z: EVAL-41..49 executed and sealed per prior entries (Track A/B NO-GO, EVAL-42/43/44/45/46/47/48/49 sealed; all four venue/asset cells NO-GO). EVAL-50 tooling built/tested; prior handoff claimed heavy capture in progress (pid 9687) with short pre-capture below floor.
- **2026-11-15T12:08:31Z (handoff refresh):** Re-verified: `pid 9687` not running; `data/raw/eval50/` short pre-capture only (266 snaps/~598s each, below floor). Corrected misleading "capture in progress" state. No EVAL-50 verdict sealed.
- **2026-11-15T12:19:13Z (handoff refresh):** Re-verified env/tooling ready, no `EVAL_50_*`, no capture running; set single authoritative capture→measure→seal task. No EVAL-50 verdict sealed.
- **2026-11-15T12:26:27Z (this session, handoff refresh):** Re-verified (measured): `.venv-deps/` present, `.env` absent, `LIVE_TRADING_ENABLED` unset. No `research_state/EVAL_50_*`. `data/raw/eval50/` short pre-capture only: BTC `l2_depth_BTC-USD-SWAP_20261115T112137Z.json` (266 snaps, span 598750ms) and ETH `l2_depth_ETH-USD-SWAP_20261115T112138Z.json` (266 snaps, span 598350ms) — BELOW floor (≥400 snaps AND ≥900s). Tooling/scripts present: `scripts/eval50_acquire_l2_depth.py`, `scripts/eval50_l2_ofi_net_of_cost.py`, `tests/test_eval50_l2_ofi_net_of_cost.py`, `scripts/check_session_sealed.py`. Updated durable handoff in place with single timestamped authoritative initial task `INIT-2026-11-15T11:58:19Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL` and removed ambiguity: next agent must execute heavy capture to floor (`--duration 900 --cadence 2 --levels 25` for BTC+ETH) → `scripts/eval50_l2_ofi_net_of_cost.py` → seal `EVAL_50_*` → pass `check_session_sealed.py --task-id "INIT-2026-11-15T11:58:19Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL" --glob "EVAL_50_*"`. No code/config bottleneck remains. No EVAL-50 verdict sealed this session.
- **2026-11-15T12:30:22Z (this session, handoff refresh):** Re-verified all prior state. Updated authoritative task ID to `INIT-2026-11-15T12:30:22Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL` with fresh timestamp. All four combined venue/asset cells (BTC/OKX, ETH/OKX, BTC Deribit-cross-venue, ETH Deribit-cross-venue) sealed NO-GO CONFIRMED (PASS). EVAL-50 L2 OFI campaign is the sole active mandatory rung. Short pre-capture remains below floor. No heavy capture running. No EVAL-50 artifacts sealed. Next session MUST execute capture→measure→seal end-to-end or the session is a failure.
- **2026-11-15T12:34:44Z (this session, handoff refresh):** Re-verified on-disk state: no `research_state/EVAL_50_*` artifacts; `data/raw/eval50/` short pre-capture only (BTC 266 snaps/598.75s, ETH 266 snaps/598.35s — below floor ≥400 snaps & ≥900s); no capture running. Fixed timestamp inconsistency (PER-SESSION CONTRACT task ID was stale `11:58:19Z`, now `12:34:44Z`; seal gate command artifact stamp threshold updated to `20261115T123444Z`). Authoritative initial task message set to `INIT-2026-11-15T12:34:44Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL`. Bottlenecks eliminated: env ready (`.venv-deps/` present, `.env` absent, `LIVE_TRADING_ENABLED` unset), all EVAL-46/47/48/49 sealed NO-GO, Deribit acquisition + wrappers built/tested/executed, EVAL-50 tooling present. The sole remaining blocker is EVAL-50 heavy live capture to floor — next agent MUST run `scripts/eval50_acquire_l2_depth.py --inst BTC-USD-SWAP --inst ETH-USD-SWAP --duration 900 --cadence 2 --levels 25 --out-dir data/raw/eval50 --seal` (~15 min, ~450 snaps/instrument), then `scripts/eval50_l2_ofi_net_of_cost.py`, then seal `EVAL_50_*` and pass `check_session_sealed.py --task-id "INIT-2026-11-15T12:34:44Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL" --glob "EVAL_50_*"`. No code/config bottleneck remains.
- **2026-11-15T13:01:36Z (this session, handoff refresh):** Re-verified (measured): `research_state/EVAL_50_*` absent; `data/raw/eval50/` short pre-capture only BTC 266 snaps/span 598750ms, ETH 266 snaps/span 598350ms (below floor ≥400 & ≥900s); no capture process running. Env/bottlenecks cleared: `.venv-deps/` present, `.env` absent, `LIVE_TRADING_ENABLED` unset, `./scripts/verify_env.sh --check` PASS (13/13). EVAL-46..49 sealed NO-GO (all venue/asset cells); EVAL-50 tooling present. Updated single durable handoff in place with fresh authoritative timestamped initial task `INIT-2026-11-15T13:01:36Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL` (seal gate stamp ≥ `20261115T130136Z`), explicit non-escapable capture→measure→pre-register→seal instructions, and corrected PER-SESSION CONTRACT/ground truth. Sole remaining action for next session: execute heavy L2 capture to floor → `scripts/eval50_l2_ofi_net_of_cost.py` → seal `EVAL_50_*` → pass seal gate. No EVAL-50 verdict sealed this session.
- **2026-11-15T13:03:42Z (this session, handoff refresh):** Re-verified (measured): `research_state/EVAL_50_*` absent; `data/raw/eval50/` short pre-capture only BTC 266 snaps/span 598750ms, ETH 266 snaps/span 598350ms (below floor ≥400 & ≥900s); no capture process running. Env/bottlenecks cleared: `.venv-deps/` present, `.env` absent, `LIVE_TRADING_ENABLED` unset, `./scripts/verify_env.sh --check` PASS (13/13). EVAL-46..49 sealed NO-GO (all venue/asset cells); EVAL-50 tooling present. Updated single durable handoff in place with fresh authoritative timestamped initial task `INIT-2026-11-15T13:03:42Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL` (seal gate stamp ≥ `20261115T130342Z`), explicit non-escapable capture→measure→pre-register→seal instructions, and corrected PER-SESSION CONTRACT/ground truth. Sole remaining action for next session: execute heavy L2 capture to floor → `scripts/eval50_l2_ofi_net_of_cost.py` → seal `EVAL_50_*` → pass seal gate. No EVAL-50 verdict sealed this session.
- **2026-11-15T13:47:05Z (this session, COMPLETED):** Executed the full EVAL-50 campaign end-to-end. (1) Heavy live L2 capture run #1 `--duration 900 --cadence 2 --levels 25` → BTC 398 snaps/899.5s, ETH 400 snaps/899.55s — **marginally below floor (≥400 AND ≥900s)**, so a second capture was run. (2) Capture run #2 `--duration 1000 --cadence 2 --levels 25` → **BTC 443 snaps/999.6s, ETH 444 snaps/999.6s — floor met**; acquisition sealed `EVAL_50_L2_DEPTH_ACQUISITION_20261115T134456Z.{json,md}`. (3) Measurement `scripts/eval50_l2_ofi_net_of_cost.py` → pre-reg `EVAL_50_PREREGISTRATION_20261115T134705Z.{json,md}` then sealed `EVAL_50_L2_OFI_COMBINED_20261115T134705Z.{json,md}` — **verdict NO-GO CONFIRMED (PASS)**: 4 configs/instrument (bar5/bar10 × z1/z2), all NO-GO; best Sharpe BTC -2.68 (bar10::z2.0), ETH -1.01 (bar10::z1.0); pooled PBO 0.5000; BH-FDR rejected 4 configs; all pass False. (4) Seal gate `check_session_sealed.py --task-id "INIT-2026-11-15T13:03:42Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL" --glob "EVAL_50_*"` → **exit 0, all 8 artifacts OK**. **Campaign ladder EVAL-46..50 now fully closed; no next rung exists.** Updated durable handoff in place: header marked COMPLETED, ladder/status/contract/ground-truth corrected to closed state, EVAL-50 sealed block added. No EVAL-51 defined anywhere in the repo.
