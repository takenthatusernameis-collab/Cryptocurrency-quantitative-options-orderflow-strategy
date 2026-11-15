# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK (do this next; no other task is valid until it is done)

**EVAL-53 IS SEALED AND COMPLETE (do not re-run):** `NO-GO CONFIRMED (PASS)` at
`research_state/EVAL_53_CROSS_WINDOW_COMBINED_20261115T171712Z.{json,md}` (prereg
`EVAL_53_PREREGISTRATION_20261115T171210Z`; window-B acquisition
`EVAL_53_WINDOW_B_ACQUISITION_20261115T171210Z` — independent new synchronized ~24h
Deribit capture, window A = sealed `data/raw/eval52/` (immutable), window B =
`data/raw/eval53/` (`options_surface_orderflow_{BTC,ETH}_20261115T171210Z.json`);
floor met on **both** windows: window B BTC 289 surface snaps / 102 inst / 289 5m
bars, 4547 option trades / 99 inst / span 86036.016 s / 287 common 5m bars; ETH 289
snaps / 102 inst / 289 bars, 3066 trades / 101 inst / span 85927.871 s / 287 common
bars; 18 configs/underlying per window, all NO-GO; pooled PBO window A **0.6389**
(matches sealed EVAL-52 exactly), window B **0.5556**; best Sharpe window A
BTC −0.7473 `continuous_zscore::call_minus_put::bar300.0` / ETH −1.6028
`sign_agreement::imbalance::bar300.0`; window B BTC −0.7315 **same best config**
`continuous_zscore::call_minus_put::bar300.0` / ETH −1.7099 **same best config**
`sign_agreement::imbalance::bar300.0`; BH-FDR rejected 32 configs per window;
0 replicated passing configs; seal gate exit 0). **The EVAL-52 NO-GO is
temporally stable — it replicates on an independent window B with identical best
configs.** Tooling: `scripts/eval53_cross_window_replication.py`,
`tests/test_eval53_cross_window_replication.py` (9 passed). Immutable. The Deribit
public network blocker is RESOLVED — window B was acquired at
2026-11-15T17:12:10Z.

**EVAL-52 IS SEALED (do not re-run):** `NO-GO CONFIRMED (PASS)` at
`research_state/EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_20261115T165018Z.{json,md}` (prereg
`EVAL_52_PREREGISTRATION_20261115T165018Z`; acquisition
`EVAL_52_SYNCHRONIZED_ACQUISITION_20261115T164732Z` — BTC 289 surface snapshots / 102 instruments /
289 5m bars, 4688 option trades / 99 instruments / span 86261.649 s / 288 common 5m bars; ETH 289
snapshots / 102 instruments / 289 5m bars, 3122 option trades / 101 instruments / span 86204.278 s /
287 common 5m bars; 18 configs/underlying, best Sharpe BTC −0.7473
`continuous_zscore::call_minus_put::bar300.0`, ETH −1.6028 `sign_agreement::imbalance::bar300.0`, all
NO-GO, pooled PBO 0.6389, BH-FDR rejected 32 configs; seal gate exit 0). Tooling:
`scripts/eval52_acquire_synchronized_options.py`, `scripts/eval52_options_surface_orderflow_net_of_cost.py`,
`tests/test_eval52_options_surface_orderflow_net_of_cost.py` (7 passed). Window-A capture:
`data/raw/eval52/` (`options_surface_orderflow_{BTC,ETH}_20261115T164732Z.json`). Immutable.

**EVAL-54 IS THE NEXT FOCUS CAMPAIGN** — a **fresh, pre-registered, heavy real-data falsification**
aligned with the repo charter (`Cryptocurrency-quantitative-options-orderflow-strategy` = quantitative
**OPTIONS** + orderflow strategy; net-of-cost evaluation). Every options+orderflow fusion cell
(EVAL-46..53) is sealed `NO-GO CONFIRMED (PASS)`; re-litigating fused options+orderflow is prohibited.
The unmeasured heavy real-data rung per the charter is **real options pricing/greeks/vol-surface →
delta-hedged P&L net of execution costs** on real Deribit BTC+ETH option surface — a pure options-native
campaign distinct from the sealed orderflow fusions.

**TASK `INIT-2026-11-15T17:24:39Z-EVAL-54-REAL-OPTIONS-VOL-SURFACE-DELTA-HEDGING-NET-OF-COST-BTC-ETH-ACQUIRE-MEASURE-AND-SEAL`.**

EVAL-54 is a fresh, pre-registered, heavy real-data falsification: real Deribit options vol-surface /
greeks → delta-hedged P&L net of bid-ask spread and fees on **BTC and ETH** over a synchronized ~24h
window, measured with a pre-registered net-of-cost protocol, combined in a single verdict. Deribit
option-trade history is ~24h-capped, so the capture is genuinely new real evidence. **New timestamped
task ID; never re-run/re-seal EVAL-02..53. No other task is valid until step 7 exits 0.**

**YOU MUST, in this session, in this order, and may not skip any step:**

1. **Verify env (fast; do NOT run the full test suite):**
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   ./scripts/verify_env.sh --check
   ```
   If green, proceed.

2. **Build EVAL-54 tooling (non-escapable engineering work):**
   Create `scripts/eval54_acquire_options_surface.py` (real Deribit option surface + perp candles +
   option trades for BTC+ETH into `data/raw/eval54/`, sealing an acquisition manifest) and
   `scripts/eval54_options_surface_hedging_net_of_cost.py` (real vol-surface/greeks delta-hedged P&L
   net of bid-ask and fees; causal, no look-ahead; floor-aligned grid) plus
   `tests/test_eval54_options_surface_hedging_net_of_cost.py`.
   Reuse sealed acquisition primitives (Deribit `get_tradingview_chart_data` surface candles,
   `get_last_trades_by_instrument_and_time` trades, perp candles) — do NOT fall back to synthetic;
   real loaders raise `RealDataUnavailable`. No `phaseNN_*` wrappers; no edits to sealed EVAL-02..53
   scripts/tests/artifacts or `src/`.
   Compile + test before capture:
   ```bash
   python3 -m py_compile scripts/eval54_acquire_options_surface.py \
       scripts/eval54_options_surface_hedging_net_of_cost.py \
       tests/test_eval54_options_surface_hedging_net_of_cost.py
   python3 -m pytest -q tests/test_eval54_options_surface_hedging_net_of_cost.py   # must pass
   ```

3. **Independent heavy real acquisition (live public read-only Deribit, BTC+ETH, synchronized ~24h
   window, both legs):**
   ```bash
   python3 scripts/eval54_acquire_options_surface.py --underlying BTC --underlying ETH --out-dir data/raw/eval54 --seal
   ```
   ensuring an `EVAL_54_WINDOW_B_ACQUISITION_<UTC>` manifest is written to `research_state/`.
   **Do not proceed unless both underlyings clear the per-underlying floor:**
   surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options trades ≥2000 trades / ≥50
   instruments / ≥240 bars / ≥79200 s span; legs time-overlapping (common 5m bars ≥240). Below floor
   ⇒ widen capture parameters and retry; **never** weaken the floor and **never** emit `{"valid": true}`
   for a below-floor capture.

4. **Pre-register BEFORE measurement:** write `EVAL_54_PREREGISTRATION_<UTC>` to `research_state/`
   declaring the net-of-cost protocol, grid, floors, and the GO bar before any verdict is computed.

5. **Smoke measurement (seals nothing):** run acquisition/measurement in dry-run mode and confirm
   `floor_ok: true` for both underlyings; inspect per-underlying net-of-cost P&L/Sharpe.

6. **Seal the verdict:** pre-register (if not yet), then seal `EVAL_54_COMBINED_<UTC>` (or
   `EVAL_54_BLOCKED_<UTC>` only if floor unmet — never a substitute for a floor-passing verdict).

7. **Seal gate — session FAILS unless a window acquisition AND a floor-passing combined verdict exist
   with stamp ≥ task timestamp:**
   ```bash
   python3 scripts/check_session_sealed.py \
       --task-id "INIT-2026-11-15T17:24:39Z-EVAL-54-REAL-OPTIONS-VOL-SURFACE-DELTA-HEDGING-NET-OF-COST-BTC-ETH-ACQUIRE-MEASURE-AND-SEAL" \
       --glob "EVAL_54_WINDOW_B_ACQUISITION_*" \
       --require-glob "EVAL_54_PREREGISTRATION_*" \
       --require-glob "EVAL_54_COMBINED_*"
   ```
   Must exit `0`.

8. **Append a session-log line** to this file (measured numbers, floor metrics, per-underlying +
   combined verdict, artifact paths) and leave this handoff as the single durable record.

**Definition of done:** step 7 exits `0` with `EVAL_54_WINDOW_B_ACQUISITION_<UTC>`,
`EVAL_54_PREREGISTRATION_<UTC>` (pre-verdict), and a floor-passing `EVAL_54_COMBINED_<UTC>` (verdict
`GO CONFIRMED` or `NO-GO CONFIRMED (PASS)`) all stamped ≥ `2026-11-15T17:24:39Z`. A handoff-only
session, re-run/re-seal of EVAL-02..53, full-test-suite discovery loop, `research_state/` enumeration,
or `EVAL_54_BLOCKED_*` in place of a floor-passing combined verdict are **all failures**.

## WHY THIS IS THE RIGHT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE)
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined options + orderflow** strategy,
but every options+orderflow fusion cell (EVAL-46..53) is sealed `NO-GO CONFIRMED (PASS)`; re-running
fused options+orderflow is prohibited re-litigation. The charter's unmeasured heavy rung is **real
options pricing/greeks/vol-surface → net-of-cost evaluation**. EVAL-54 measures whether real Deribit
options vol-surface delta-hedging is net-of-cost tradable on BTC and ETH — the pure options-side
rung not yet measured, requiring new live heavy data (Deribit option trades ~24h-capped = genuinely new
evidence), not a re-run of sealed artifacts. **New timestamped task ID, never a re-run/re-seal of
EVAL-02..53.**

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
New synchronized real Deribit options surface capture (BTC+ETH) over the same ~24h window meeting
per-underlying floor (surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options-venue trades
≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span; legs time-overlapping/common 5m bars ≥240)
→ real vol-surface/greeks delta-hedged P&L net of bid-ask and fees (causal, no look-ahead,
floor-aligned grid) → pre-register `EVAL_54_PREREGISTRATION_*` BEFORE verdict → seal
`EVAL_54_WINDOW_B_ACQUISITION_*` and `EVAL_54_COMBINED_*` (or BLOCKED only if floor unmet, never as
substitute) → pass seal gate. No prior-EVAL re-runs/re-seals, no `research_state/` enumeration, no
full test suite, no handoff-only session.

## BOTTLENECKS — CLEARED (verified 2026-11-15T17:24:39Z)
1. **CLEARED:** Deribit public network — EVAL-53 window-B synchronized capture completed at
   2026-11-15T17:12:10Z (`data/raw/eval53/` BTC+ETH, floor met); EVAL-53 sealed. No active network
   blocker. If a future capture dips below floor, widen capture parameters and retry.
2. **CLEARED:** EVAL-53 sealed `NO-GO CONFIRMED (PASS)` with gate exit 0; artifacts immutable;
   window-B capture `data/raw/eval53/` present and reusable (read-only).
3. **CLEARED:** EVAL-52 sealed `NO-GO CONFIRMED (PASS)`; window-A capture `data/raw/eval52/` present
   and reusable (read-only). No handoff-only loop for EVAL-52.
4. **CLEARED:** env ready — `.venv-deps/` present; `./scripts/verify_env.sh --check` exit 0;
   `.env` absent; `LIVE_TRADING_ENABLED` unset/false.
5. **CLEARED:** sealed EVAL-52/EVAL-53 tooling + tests on disk and importable;
   `scripts/check_session_sealed.py` supports `--glob` + repeatable `--require-glob` (AND) and
   `--require-any-glob` (OR) — gate executable as written.
6. **CLEARED:** `scripts/eval53_*` tooling built and tested (9 passed); EVAL-53 acquisition, prereg,
   and combined verdict all sealed.

## ANTI-STALL RULE (read before touching this file)
- **Only** acceptable outputs: (a) sealed `EVAL_54_WINDOW_B_ACQUISITION_*` + `EVAL_54_PREREGISTRATION_*` +
  `EVAL_54_COMBINED_*` with gate exit 0, or (b) a *narrower* timestamped handoff whose floor is
  **identical or stricter** and whose only change is the corrected task timestamp.
- **Do NOT** re-issue at a new timestamp without either sealing or making stricter. A session whose only
  diff to this file is the timestamp is a failed session.
- **Do NOT** weaken the floor, drop an underlying, drop a bar size, or convert the gate to accept
  `EVAL_54_BLOCKED_*` as a verdict.
- **Do NOT** create `EVAL_54_BLOCKED_*` and stop: below-floor means *widen the capture*, not *stop*.
- If external outage blocks capture, re-run with wider capture parameters first; only then record a
  blocked artifact **plus** the exact failing floor metric and the command to resume.

## PROHIBITED (hard constraints)
- Do **not** re-run, re-litigate, or re-seal EVAL-02..53; do not edit sealed artifacts, sealed EVAL-52/
  EVAL-53 scripts/tests, or `src/`.
- Do **not** fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel
  synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential
  mutation, or order placement. Network: public read-only market data only, polite rate limiting.
- Do **not** run the full test suite as discovery; do **not** enumerate `research_state/`; do **not**
  create timestamped handoff copies or new handoff files (root `HANDOFF_NEXT_AGENT.md`,
  `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers).
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`; no
  `phaseNN_*` orchestrator wrappers.

## SEALED STATE (immutable; do not re-run; append only)
EVAL-02..53 sealed. EVAL-46..53 (options+orderflow ladder) all **NO-GO CONFIRMED (PASS)**:
- **EVAL-46** integrated options+orderflow net-of-cost on full dense BTC → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z.{json,md}`.
- **EVAL-47** ETH combined → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_47_ETH_COMBINED_20261115T071330Z.{json,md}`.
- **EVAL-48** BTC cross-venue (Deribit options + OKX BTC orderflow) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z.{json,md}`.
- **EVAL-49** ETH cross-venue (Deribit ETH options + OKX ETH orderflow) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z.{json,md}`.
- **EVAL-50** real L2 order-book OFI (BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_50_L2_OFI_COMBINED_20261115T134705Z.{json,md}`.
- **EVAL-51** real Deribit options-venue order flow standalone (BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_51_OPTIONS_ORDERFLOW_COMBINED_20261115T152005Z.{json,md}`.
- **EVAL-52** synchronized options SURFACE × options-venue ORDER FLOW (pure options-side, BTC+ETH) →
  `NO-GO CONFIRMED (PASS)` `research_state/EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_20261115T165018Z.{json,md}`
  (acq `EVAL_52_SYNCHRONIZED_ACQUISITION_20261115T164732Z`, prereg `EVAL_52_PREREGISTRATION_20261115T165018Z`,
  window-A data `data/raw/eval52/`; pooled PBO 0.6389; best Sharpe BTC −0.7473, ETH −1.6028; all NO-GO).
- **EVAL-53** synchronized options SURFACE × options-venue ORDER FLOW cross-window replication
  (pure options-side, BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_53_CROSS_WINDOW_COMBINED_20261115T171712Z.{json,md}`
  (acq `EVAL_53_WINDOW_B_ACQUISITION_20261115T171210Z`, prereg
  `EVAL_53_PREREGISTRATION_20261115T171210Z`, window-B data `data/raw/eval53/`; pooled PBO window A
  0.6389 / window B 0.5556; all NO-GO; seal gate exit 0).

Earlier: EVAL-37 audit `PASS 9/9`; EVAL-41/42 options pillar closed; EVAL-43 orderflow full roster
`NO-GO CONFIRMED (PASS)`; EVAL-44 `CAMPAIGN_CLOSED` (BTC-scoped); EVAL-45 ETH orderflow `NO-GO` + options
`BLOCKED`. The combined options+orderflow thesis is not net-of-cost tradable on all measured cells
including the pure options-side fusion (EVAL-52) and its cross-window replication (EVAL-53). EVAL-54 is
the next unmeasured heavy rung (real options vol-surface/greeks delta-hedging net of costs).

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (imports `src/` → needs numpy).
- **GRID ALIGNMENT:** EVAL-52 capture stores `surface` snapshots (5m bar grid) and `option_trades` +
  `perp_candles`; measurement builds 5m bar grid from perp/order-flow side and attaches newest surface
  snapshot with `bar_end(snapshot) ≤ bar_end(bar)` (causal). Intersect legs' bar sets; floor on the
  intersected grid. Reuse EVAL-52 `build_bars`/`surface_signal_series`/`align_surface` logic.
- Deribit options **trades**: `GET /public/get_last_trades_by_instrument_and_time` (paginate
  `start_timestamp = last_trade_ts + 1` while `has_more`; ~24h cap per instrument — window B is the
  trailing ~24h at capture time). Deribit options **candles** (surface): `GET /public/get_tradingview_chart_data`
  per option instrument, resolution `5` (historical candles available). Perp: `get_tradingview_chart_data`
  `{BTC,ETH}-PERPETUAL` resolution `1`/`5` as in EVAL-52.
- `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 → DSR may report 0.0; use perm/bootstrap/PBO/BH-FDR.
- `permutation_test(rets, flat, statistic=_mean, paired=True, seed=42)` → `p_value`. `block_bootstrap_ci`
  → `(point, lo, hi)`. Run full capture; no fixed tail slices.

## HARD INVARIANTS
Paper-only; `.env` absent; `LIVE_TRADING_ENABLED=false`. Never fall back to synthetic; real loaders raise
`RealDataUnavailable`; never relabel synthetic as real. Sealed artifacts immutable; append new timestamped
artifacts only. Public read-only network only. Reuse `src/` modules; no `phaseNN_*`.

## HANDOFF DISCIPLINE
This file is the **single durable handoff**. Update in place with verified facts/timestamps/paths/commands
only; no timestamped handoff copies. Record measured numbers, not intentions. No GO without a verifying
sealed artifact. Final responses must not ask follow-up questions.

## SESSION LOG (append-only)
- 2026-11-14T18:21:06Z→2026-11-15T11:03:55Z: EVAL-41..49 executed and sealed (all NO-GO). EVAL-50 tooling
  built/tested; prior handoff claimed heavy capture in progress (pid 9687) with short pre-capture below floor.
- 2026-11-15T12:08:31Z–13:03:42Z: re-verified `pid 9687` not running; `data/raw/eval50/` short pre-capture
  only (266 snaps/~598 s each, below floor). Repeatedly set EVAL-50 task. No EVAL-50 verdict sealed.
- **2026-11-15T13:47:05Z (EVAL-50 COMPLETED):** capture `--duration 1000 --cadence 2 --levels 25` → BTC
  443 snaps/999.6 s, ETH 444 snaps/999.6 s (floor met); `EVAL_50_L2_DEPTH_ACQUISITION_20261115T134456Z`;
  prereg `EVAL_50_PREREGISTRATION_20261115T134705Z`; verdict `EVAL_50_L2_OFI_COMBINED_20261115T134705Z`
  — **NO-GO CONFIRMED (PASS)** (best BTC −2.68 / ETH −1.01, pooled PBO 0.5000). Seal gate exit 0.
- **2026-11-15T15:06:06Z & 15:11:17Z:** EVAL-51 task refreshes, no verdict (handoff-only).
- **2026-11-15T15:18:43Z–15:20:05Z (EVAL-51 COMPLETED):** acquisition `--days 1` BTC+ETH → BTC 5347 trades
  / 98 instruments / 289 5m bars / 86010 s; ETH 3429 trades / 102 instruments / 289 bars / 86381 s;
  `EVAL_51_OPTIONS_ORDERFLOW_ACQUISITION_20261115T151843Z`; prereg `EVAL_51_PREREGISTRATION_20261115T152005Z`;
  verdict `EVAL_51_OPTIONS_ORDERFLOW_COMBINED_20261115T152005Z` — **NO-GO CONFIRMED (PASS)** (best BTC
  −1.864, ETH −1.897, pooled PBO 0.5000). Seal gate exit 0. `pytest ...eval51...` 14 passed.
- 2026-11-15T15:22:00Z–15:26:16Z: EVAL-52 task set/hardened; no verdict until executed.
- **2026-11-15T16:42:09Z–16:50:18Z (EVAL-52 COMPLETED, `INIT-2026-11-15T15:26:16Z-...-EVAL-52-...`):**
  `./scripts/verify_env.sh --check` exit 0. `py_compile` eval52 scripts+tests ok; `pytest -q tests/test_eval52_options_surface_orderflow_net_of_cost.py` → 7 passed. Synchronized real Deribit capture BTC+ETH `--out-dir data/raw/eval52 --seal` → `EVAL_52_SYNCHRONIZED_ACQUISITION_20261115T164732Z`. Floor met: BTC 289 snaps/102 inst/289 5m bars, 4688 trades/99 inst/span 86261.649s/288 common 5m; ETH 289/102/289, 3122/101/span 86204.278s/287 common. Prereg `EVAL_52_PREREGISTRATION_20261115T165018Z`; verdict `EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_20261115T165018Z` — **NO-GO CONFIRMED (PASS)** (18 configs/underlying; best BTC −0.7473 `continuous_zscore::call_minus_put::bar300.0`, ETH −1.6028 `sign_agreement::imbalance::bar300.0`; all NO-GO; pooled PBO 0.6389; BH-FDR rejected 32). Seal gate exit 0. EVAL-52 immutable.
- **2026-11-15T16:54:19Z (handoff refreshed for EVAL-53):** verified EVAL-52 sealed; env green; `data/raw/eval53/`
  absent; set authoritative task for EVAL-53. Stale body below treated EVAL-53 as pending with a network
  blocker; that blocker is now resolved.
- **2026-11-15T17:08:32Z (EVAL-53 tooling built):** `scripts/eval53_cross_window_replication.py` +
  `tests/test_eval53_cross_window_replication.py` (`py_compile` OK; `pytest -q` 9 passed). `--no-write`
  smoke verified offline; window A `floor_ok: true` pooled PBO 0.6389 matching sealed EVAL-52.
- **2026-11-15T17:12:10Z–17:17:12Z (EVAL-53 COMPLETED):** window-B synchronized Deribit capture BTC+ETH →
  `EVAL_53_WINDOW_B_ACQUISITION_20261115T171210Z`; prereg `EVAL_53_PREREGISTRATION_20261115T171210Z`;
  verdict `EVAL_53_CROSS_WINDOW_COMBINED_20261115T171712Z` — **NO-GO CONFIRMED (PASS)** (window B BTC 289
  snaps/102 inst/289 bars, 4547 trades/99 inst/span 86036.016s/287 common 5m; ETH 289/102/289,
  3066/101/span 85927.871s/287 common; pooled PBO window A 0.6389, window B 0.5556; all NO-GO;
  BH-FDR rejected 32 per window). Seal gate exit 0. EVAL-53 immutable. Deribit network blocker RESOLVED.
- **2026-11-15T17:24:39Z (this session):** handoff refreshed for EVAL-54; EVAL-53 sealed/complete, Deribit
  network blocker resolved, env green, `data/raw/eval53/` present, EVAL-53 tooling built/tested (9 passed).
  Set authoritative task
  **`INIT-2026-11-15T17:24:39Z-EVAL-54-REAL-OPTIONS-VOL-SURFACE-DELTA-HEDGING-NET-OF-COST-BTC-ETH-ACQUIRE-MEASURE-AND-SEAL`**
  with step-7 gate
  (`--glob "EVAL_54_WINDOW_B_ACQUISITION_*" --require-glob "EVAL_54_PREREGISTRATION_*" --require-glob "EVAL_54_COMBINED_*"`, stamp ≥ task). Next session must build eval54 tooling, acquire real synchronized
  Deribit options surface (BTC+ETH ~24h) meeting the per-underlying floor, pre-register, measure
  delta-hedged net-of-cost P&L, seal prereg+acquisition+combined verdict, and pass gate; no other task
  valid.
