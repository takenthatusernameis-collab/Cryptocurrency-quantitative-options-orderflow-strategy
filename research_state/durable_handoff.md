# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

**INITIAL TASK MESSAGE (inferred timestamped 2026-11-15T12:13:10Z UTC, authoritative for next session) — TASK ID `INIT-2026-11-15T11:58:19Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL`**
**SCOPE (repo-charter priority: `Cryptocurrency-quantitative-options-orderflow-strategy` = combined options+orderflow):** EVAL-50 — Real L2 order-book OFI campaign. All four combined options+orderflow venue/asset cells are sealed **NO-GO CONFIRMED (PASS)**: EVAL-46 BTC/OKX (`EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z`), EVAL-47 ETH/OKX (`EVAL_47_ETH_COMBINED_20261115T071330Z`), EVAL-48 BTC Deribit-cross-venue (`EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z`), EVAL-49 ETH Deribit-cross-venue (`EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z`, gate exit 0). The fused thesis is **not net-of-cost tradable on real BTC or real ETH, OKX or Deribit options venues**. **EVAL-50 is the active mandatory rung.** Tooling built/compiled/tested (`scripts/eval50_acquire_l2_depth.py`, `scripts/eval50_l2_ofi_net_of_cost.py`, `tests/test_eval50_l2_ofi_net_of_cost.py` 14/14). **Capture status (re-verified 2026-11-15T12:13:10Z): background capture pid 9687 is NOT running; NO heavy capture is in progress.** Only a **short pre-capture** is on disk: `data/raw/eval50/l2_depth_BTC-USD-SWAP_20261115T112137Z.json` and `data/raw/eval50/l2_depth_ETH-USD-SWAP_20261115T112138Z.json` (266 snapshots each, ~598.75s / ~598.35s span). This is **BELOW the heavy-work floor (≥400 snaps AND ≥900s per instrument)**; the measurement script refuses to seal a verdict on it and would only emit `EVAL_50_BLOCKED_*`. **No `EVAL_50_*` artifacts exist in `research_state/`.** The heavy live capture for BTC+ETH concurrent **MUST be run to completion** (`--duration 900 --cadence 2 --levels 25`, ~450 snaps/instrument, meets floor). **THIS IS THE ONLY TASK. NO NO-OP. NO HANDOFF-ONLY SESSION. NO PRIOR-EVAL RE-RUN. NO SEALING ON THE SHORT PRE-CAPTURE (floor enforced in code). EITHER RUN CAPTURE TO COMPLETION + SEAL `EVAL_50_L2_OFI_COMBINED_*` (or a documented `EVAL_50_BLOCKED_*` only if capture demonstrably cannot meet floor after a full attempt) AND PASS THE SEAL GATE, OR THE SESSION IS A FAILURE.**

**BOTTLENECKS ELIMINATED / MEASURED STATE (2026-11-15T12:13:10Z re-verified; env + tooling READY; prior evals sealed; capture must be executed):**
- **EVAL-46..49 SEALED (DONE):** BTC/OKX, ETH/OKX, BTC Deribit-cross-venue, ETH Deribit-cross-venue combined all **NO-GO CONFIRMED (PASS)** (`EVAL_46_...041621Z`, `EVAL_47_...071330Z`, `EVAL_48_...081951Z`, `EVAL_49_...101149Z`). Never re-run. Do not edit sealed evals or any `src/` module.
- **Deribit acquisition + wrappers BUILT/TESTED/EXECUTED:** `scripts/eval48_acquire_deribit_options.py` (reusable `--underlying ETH|BTC`) + `scripts/eval49_eth_cross_venue_replication.py`. Chronic EVAL-48/49 blockers gone.
- **Env:** `.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED` unset/false. Fresh checkout: `./scripts/verify_env.sh` then `./scripts/verify_env.sh --check`.
- **EVAL-50 tooling READY:** `scripts/eval50_acquire_l2_depth.py`, `scripts/eval50_l2_ofi_net_of_cost.py` present; `tests/test_eval50_l2_ofi_net_of_cost.py` 14/14 (per handoff record). Run measurement with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (depends on numpy via `src/` imports).
- **ACTIVE BOTTLENECK (must clear):** heavy L2 capture not running / not completed to floor. `data/raw/eval50/` contains only the short pre-capture (266 snaps, ~598s per instrument, below ≥400 snaps & ≥900s). No `research_state/EVAL_50_*` exists.

**NEXT AGENT — EXECUTE IMMEDIATELY (DO NOT EXPLORE, DO NOT RE-LITIGATE, DO NOT RUN FULL TEST SUITE, NO PRIOR-EVAL RE-RUN):**
1. **Env/readiness:** `.env` absent; `LIVE_TRADING_ENABLED` unset/false. `.venv-deps/` present. `./scripts/verify_env.sh --check` must PASS. Then `export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`.
2. **RUN HEAVY CAPTURE TO COMPLETION (mandatory; public read-only, polite cadence):**
   `python3 scripts/eval50_acquire_l2_depth.py --inst BTC-USD-SWAP --inst ETH-USD-SWAP --duration 900 --cadence 2 --levels 25 --out-dir data/raw/eval50 --seal`
   This runs ~15 min and should yield ~450 snaps/instrument meeting the floor (≥400 snaps AND ≥900s per instrument). Wait for completion. **Do NOT seal/measure on the existing short pre-capture (`l2_depth_{BTC,ETH}-USD-SWAP_20261115T1121*.json`, 266 snaps/~598s) — it is below floor.** If capture cannot meet floor after a full honest attempt, document the measured constraint and let the measurement emit the documented `EVAL_50_BLOCKED_*` (do not fabricate a verdict).
3. **RUN EVAL-50 MEASUREMENT (mandatory deliverable):** after capture meets floor, run `python3 scripts/eval50_l2_ofi_net_of_cost.py` (pre-registers `EVAL_50_PREREGISTRATION_<UTC>.{json,md}` before measurement, seals `EVAL_50_L2_OFI_COMBINED_<UTC>.{json,md}` or `EVAL_50_BLOCKED_<UTC>` per floor). It is a thin consumer of `src/` analytics/backtest — no `phaseNN_*` wrapper.
4. **Seal gate:** `python3 scripts/check_session_sealed.py --task-id "INIT-2026-11-15T11:58:19Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL" --glob "EVAL_50_*"` must PASS (exit 0; artifact stamp ≥ 20261115T115819Z).
5. **Update this handoff in place** with verified measured outcome (paths, counts/spans, verdict, seal-gate result) and the next mandatory rung if any.

**A SESSION THAT DOES NOT COMPLETE ALL STEPS AND SEAL THE REQUIRED `EVAL_50_*` ARTIFACTS IS A FAILED SESSION — NO EXCEPTIONS, NO ESCAPE HATCH.**

**DE-RISK / GOTCHAS (re-verified 2026-11-15T12:13:10Z):**
- **Short pre-capture on disk is NOT usable for a verdict:** BTC+ETH `20261115T1121*`, 266 snaps, ~598s — below floor (≥400 snaps, ≥900s). Measurement will not seal a NO-GO/GO on it.
- **Acquisition is live, public read-only:** OKX has no historical L2 book endpoint; capture is polling `GET /api/v5/market/books` (polite cadence+jitter, browser UA). Network: public read-only only.
- **Loader/runtime gotchas (carried forward):** run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`; `load_snapshot_signals(symbol, data_raw)` first arg is symbol (`"BTC"`/`"ETH"`); `_causal_signal_series`/`_toxicities_per_bar` take `bar_ends_dt` (datetime); `load_real_orderflow` returns Pydantic `OrderflowSnapshot` (slice via `.model_copy`); sealed `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 (use perm/bootstrap/PBO/BH-FDR as primary); run the **full** tape.
- **EVAL-46..49 sealed immutable.** Do not re-run, do not edit sealed artifacts or `src/`.

**WHY THIS TASK EXISTS (repo-name/charter priority — NON-NEGOTIABLE):** the repo is `Cryptocurrency-quantitative-options-orderflow-strategy` — the deliverable is a **combined options + orderflow strategy**. Combined thesis sealed **NO-GO** on all four venue/asset cells (BTC/OKX EVAL-46, ETH/OKX EVAL-47, BTC Deribit-cross-venue EVAL-48, ETH Deribit-cross-venue EVAL-49). **EVAL-50 (Real L2 order-book OFI campaign) is the active mandatory rung** — acquire real L2 depth data to floor, test book-imbalance/OFI alpha net-of-cost, seal `EVAL_50_*`.

**HEAVY-WORK FLOOR (non-negotiable; below this floor a session is incomplete):** complete heavy real L2 depth capture meeting floor (≥900s AND ≥400 snaps per instrument, BTC+ETH) → `python3 scripts/eval50_l2_ofi_net_of_cost.py` (full-tape net-of-cost OFI alpha + flat control + 1000 permutations + 1000 bootstrap resamples + CSCV PBO k=4 + BH-FDR + DSR) → pre-register `EVAL_50_PREREGISTRATION_*` BEFORE measurement → seal `EVAL_50_*` → pass seal gate. No prior-EVAL re-runs, no `research_state/` enumeration, no full test suite, no handoff-only session.

**CAMPAIGN LADDER (each rung heavy + pre-registered; start the next only after the previous seals):**
- **EVAL-46 (DONE, sealed):** integrated options+orderflow net-of-cost on full dense real BTC → **NO-GO CONFIRMED (PASS)** `EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z`.
- **EVAL-47 (DONE, sealed):** ETH combined cross-asset replication → **NO-GO CONFIRMED (PASS)** `EVAL_47_ETH_COMBINED_20261115T071330Z`.
- **EVAL-48 (DONE, sealed):** BTC cross-venue (Deribit options + OKX BTC orderflow) → **NO-GO CONFIRMED (PASS)** `EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z`.
- **EVAL-49 (DONE, sealed):** ETH cross-venue (Deribit ETH options + OKX ETH orderflow) → **NO-GO CONFIRMED (PASS)** `EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z`.
- **EVAL-50 (ACTIVE, mandatory):** Real L2 order-book OFI campaign — tooling ready; **heavy capture NOT yet completed to floor** (short pre-capture on disk). Run capture to completion → measure → pre-register → seal `EVAL_50_*` → pass seal gate.
- Campaign re-closes only when every rung seals; until then there is always a next heavy rung.

**BOTTLENECKS (verified 2026-11-15T12:13:10Z):**
1. **CLEARED** — EVAL-46/47/48/49 sealed NO-GO (all four venue/asset cells). Never re-run.
2. **CLEARED** — Deribit acquisition + wrapper tooling built/tested/executed.
3. **CLEARED** — Env/safety: `.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED` unset/false.
4. **CLEARED** — Prior sealed-eval inputs on disk (BTC, ETH, Deribit BTC/ETH).
5. **CLEARED (misleading state fixed)** — handoff previously claimed heavy capture in progress (pid 9687); re-verified pid NOT running. State corrected.
6. **ACTIVE — EVAL-50 heavy live capture to floor:** must run `scripts/eval50_acquire_l2_depth.py --inst BTC-USD-SWAP --inst ETH-USD-SWAP --duration 900 --cadence 2 --levels 25 --out-dir data/raw/eval50 --seal` to completion (~15 min, ~450 snaps/instrument). Then run `scripts/eval50_l2_ofi_net_of_cost.py` and pass seal gate. **This is the only blocker; no other blockers.**

## CAMPAIGN STATUS — ACTIVE (EVAL-50 real L2 OFI campaign, capture required)
EVAL-46/47/48/49 sealed all four combined venue/asset cells NO-GO. **EVAL-50 (real L2 order-book OFI) is the active mandatory rung.** Heavy capture is NOT running and not completed to floor (only short pre-capture on disk). Next agent must run capture to completion, measure, pre-register, seal `EVAL_50_*`, and pass seal gate.

## CAMPAIGN LADDER (status)
- **EVAL-43 (DONE, sealed):** orderflow full-roster net-of-cost meta-analysis (BTC) → `NO-GO CONFIRMED (PASS)` `EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z`.
- **EVAL-44 (DONE, sealed, BTC-scoped):** campaign closure certification → `CAMPAIGN_CLOSED` `EVAL_44_CAMPAIGN_CLOSURE_20261114T232641Z`.
- **EVAL-45 (DONE, sealed):** ETH orderflow + options cross-asset net-of-cost falsification → orderflow `NO-GO CONFIRMED (PASS)`; options `BLOCKED`.
- **EVAL-46 (DONE, sealed):** integrated options+orderflow net-of-cost on full dense BTC → **NO-GO CONFIRMED (PASS)** `EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z`.
- **EVAL-47 (DONE, sealed):** ETH combined cross-asset replication → **NO-GO CONFIRMED (PASS)** `EVAL_47_ETH_COMBINED_20261115T071330Z`.
- **EVAL-48 (DONE, sealed):** BTC cross-venue (Deribit options + OKX BTC orderflow) → **NO-GO CONFIRMED (PASS)** `EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z`.
- **EVAL-49 (DONE, sealed):** ETH cross-venue (Deribit ETH options + OKX ETH orderflow) → **NO-GO CONFIRMED (PASS)** `EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z`.
- **EVAL-50 (ACTIVE, mandatory):** real L2 order-book OFI campaign — **capture to floor required, then seal `EVAL_50_*`**.

## SEALED STATUS (do not re-run; append only)
### EVAL-46 — Integrated options+orderflow net-of-cost on full dense BTC (SEALED NO-GO CONFIRMED (PASS))
`research_state/EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z.{json,md}` (prereg `EVAL_46_PREREGISTRATION_20261115T041621Z`). 101 BTC snapshots × 2 real OKX BTC tapes × 3 pre-registered fusion rules, all NO-GO; pooled PBO 0.833; BH-FDR rejected nothing. Never re-run.

### EVAL-47 — ETH combined options+orderflow net-of-cost (SEALED NO-GO CONFIRMED (PASS))
`research_state/EVAL_47_ETH_COMBINED_20261115T071330Z.{json,md}` (prereg `EVAL_47_PREREGISTRATION_20261115T071330Z`; gate exit 0). 5 ETH tapes × 3 rules, all NO-GO. Never re-run.

### EVAL-48 — BTC cross-venue Deribit options + OKX BTC orderflow (SEALED NO-GO CONFIRMED (PASS))
`research_state/EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z.{json,md}` (prereg `EVAL_48_PREREGISTRATION_20261115T081951Z`; acquisition `EVAL_48_DERIBIT_ACQUISITION_20261115T081709Z`; gate exit 0). 133 Deribit BTC snapshots × 2 OKX BTC tapes × 3 rules, all NO-GO; pooled PBO 0.667. Never re-run.

### EVAL-49 — ETH cross-venue Deribit ETH options + OKX ETH orderflow (SEALED NO-GO CONFIRMED (PASS))
`research_state/EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z.{json,md}` (prereg `EVAL_49_PREREGISTRATION_20261115T101149Z`; acquisition `EVAL_49_DERIBIT_ACQUISITION_20261115T101115Z`; gate exit 0). 109 Deribit ETH snapshots × 5 ETH tapes × 3 rules, all NO-GO; GO rule: None. Never re-run.

### EVAL-45 — ETH cross-asset net-of-cost falsification (SEALED)
- Acquisition: `research_state/EVAL_45_ETH_TAPE_ACQUISITION_20261115T012656Z.{json,md}` (5 disjoint real ETH/OKX windows, 172,100 trades).
- Leg A orderflow: `research_state/EVAL_45_ETH_ORDERFLOW_META_20261115T012707Z.{json,md}` — **NO-GO CONFIRMED (PASS)**.
- Leg B options: `research_state/EVAL_45_OPTIONS_ETH_BLOCKED_20261115T012906Z.{json,md}` — **BLOCKED** (no real ETH option series at time of seal).

### Track A / B / EVAL-42 / EVAL-43 / EVAL-44 (SEALED, immutable context)
- Track A `ORDERFLOW_ROBUSTNESS_41_20261114T193836Z` (NO-GO/REPLICATION), Track B `EVAL_41_TIMESERIES_NET_OF_COST_20261114T203006Z` (REPLICATION/NO-GO), EVAL-42 `EVAL_42_OPTIONS_TIMESERIES_INDEPENDENT_AUDIT_20261114T221418Z` (NO-GO CONFIRMED), EVAL-43 `EVAL_43_ORDERFLOW_FULL_ROSTER_META_20261114T224516Z` (NO-GO CONFIRMED (PASS)), EVAL-44 `EVAL_44_CAMPAIGN_CLOSURE_20261114T232641Z` (CAMPAIGN_CLOSED, BTC-scoped). Prior EVAL-18/31 superseded by EVAL-46.

## PER-SESSION CONTRACT
A session is complete only when a sealed `EVAL_50_*` artifact (or a documented `EVAL_50_BLOCKED_*`) exists and the seal gate passes for task `INIT-2026-11-15T11:58:19Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL`. NO-GO keeps EVAL-46/47/48/49 closures in force; a GO requires sealed verifying evidence plus a pre-registered out-of-sample replication campaign. No NO-OP sessions, no prior-eval re-runs, no handoff-only progress claims.

## CURRENT MEASURED STATE (ground truth, re-verified 2026-11-15T12:13:10Z)
- **EVAL-02..49 sealed** (immutable). EVAL-36 `TERMINATE_NO_GO`; EVAL-37 `PASS 9/9`; EVAL-44 `CAMPAIGN_CLOSED` (BTC-scoped).
- **EVAL-45:** ETH orderflow **NO-GO CONFIRMED (PASS)**; ETH options **BLOCKED**.
- **EVAL-46/47/48/49:** combined (fused) options+orderflow **NO-GO CONFIRMED (PASS)** on BTC/OKX, ETH/OKX, BTC Deribit-cross-venue, ETH Deribit-cross-venue — all four venue/asset cells sealed NO-GO.
- **EVAL-50:** tooling ready (`scripts/eval50_acquire_l2_depth.py`, `scripts/eval50_l2_ofi_net_of_cost.py`, `tests/test_eval50_l2_ofi_net_of_cost.py` 14/14). **No `research_state/EVAL_50_*` artifacts.** `data/raw/eval50/` has short pre-capture only: `l2_depth_BTC-USD-SWAP_20261115T112137Z.json` and `l2_depth_ETH-USD-SWAP_20261115T112138Z.json` (266 snaps each, ~598.75s / ~598.35s, BELOW floor ≥400 snaps & ≥900s). Heavy capture pid 9687 NOT running. **Heavy capture to floor must be executed.**
- **Env:** `.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED` unset/false. `./scripts/verify_env.sh --check` expected PASS.
- **Data on disk (sealed inputs):** BTC options `data/raw/options_candles/` (101); BTC orderflow `data/raw/eval41/`; Deribit BTC `data/raw/eval48/`; ETH tapes/options `data/raw/eval45/`; Deribit ETH `data/raw/eval49/`.

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
- **2026-11-15T12:08:31Z (this session, handoff refresh):** Re-verified state. `pid 9687` NOT running; no heavy capture in progress. `data/raw/eval50/` contains only short pre-capture `l2_depth_BTC-USD-SWAP_20261115T112137Z.json` (266 snaps, 598.75s) and `l2_depth_ETH-USD-SWAP_20261115T112138Z.json` (266 snaps, 598.35s) — BELOW floor (≥400 snaps AND ≥900s). No `research_state/EVAL_50_*` artifacts. Corrected handoff to remove misleading "capture in progress" claim and to require running heavy capture to completion (`--duration 900 --cadence 2 --levels 25 --inst BTC-USD-SWAP --inst ETH-USD-SWAP --out-dir data/raw/eval50 --seal`) then `python3 scripts/eval50_l2_ofi_net_of_cost.py` and seal gate `check_session_sealed.py --task-id "INIT-2026-11-15T11:58:19Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL" --glob "EVAL_50_*"`. No EVAL-50 verdict sealed this session.
- **2026-11-15T12:13:10Z (this session, handoff refresh):** Re-verified on-disk state unchanged: no `research_state/EVAL_50_*` artifacts; `data/raw/eval50/` holds only short pre-capture `l2_depth_BTC-USD-SWAP_20261115T112137Z.json` (266 snaps, 598.75s) and `l2_depth_ETH-USD-SWAP_20261115T112138Z.json` (266 snaps, 598.35s) — BELOW floor (≥400 snaps AND ≥900s); no capture process running (pid 9687 not active). EVAL-50 remains the sole active mandatory rung — run heavy capture to completion (`--duration 900 --cadence 2 --levels 25 --inst BTC-USD-SWAP --inst ETH-USD-SWAP --out-dir data/raw/eval50 --seal`), then `python3 scripts/eval50_l2_ofi_net_of_cost.py`, pre-register, seal `EVAL_50_*`, and pass seal gate `check_session_sealed.py --task-id "INIT-2026-11-15T11:58:19Z-EVAL-50-L2-OFI-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL" --glob "EVAL_50_*"`. No EVAL-50 verdict sealed this session.
