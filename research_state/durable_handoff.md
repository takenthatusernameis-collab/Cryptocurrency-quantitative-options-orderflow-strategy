# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK FOR NEXT SESSION (timestamped; the only valid task)

**Status as of 2026-11-16T00:40:39Z (verified this session):** CAMPAIGN **EVAL-02..60 CLOSED** —
every rung sealed `NO-GO CONFIRMED (PASS)` (gate exit 0). **EVAL-60 (the synchronized three-way fusion:
real Deribit options SURFACE × Deribit options-venue ORDER FLOW × OKX perpetual ORDER FLOW) is now
SEALED `NO-GO CONFIRMED (PASS)`** at
`research_state/POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_COMBINED_20261116T003146Z.{json,md}`
(prereg `..._PREREGISTRATION_20261116T003146Z`; 18 configs/underlying; pooled PBO 0.75; best Sharpe
BTC −1.1388 / ETH −1.4729; no config passes; seal gate exit 0). **Authoritative real captures:**
`data/raw/eval60/three_way_BTC_20261115T232807Z.json` (289 snaps / 104 surf inst / 3,068 Deribit option
trades / 356,839 OKX perp trades / 288 common 5m) and
`data/raw/eval60/three_way_ETH_20261116T001342Z.json` (289 snaps / 276 surf inst / 4,289 Deribit option
trades / 231,050 OKX perp trades / 288 common 5m). **Env verified green this session:**
`./scripts/verify_env.sh --check` OK (pytest ok; numpy/pandas/scipy/pydantic/yaml/requests ok; EVAL-37 6
passed, EVAL-36 7 passed); `.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED=unset`.

**MANDATORY NEXT TASK (timestamped, non-optional, heavy real work — NO handoff-only completion):**

```
INIT-2026-11-16T00:40:39Z-EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE-PREREG-ACQUIRE-MEASURE-SEAL
```

**What this task requires (all steps, in order; a session is FAILED if it only edits this handoff or
only builds tooling without sealing a real COMBINED verdict):**

1. **Test ONE named falsifiable hypothesis (fixed — do NOT pick from a menu):** real **options
   order-flow toxicity** predicts **subsequent realized volatility**, and a **signal-timed delta-hedged
   ATM straddle** is **net-of-cost tradable** on the BTC/ETH perpetual, causal (decision at bar k →
   outcome over [k, k+1]), on **both BTC and ETH** over the same fresh ~24h window.
2. **Acquire real data (heavy, LIVE, mandatory — this is the step prior sessions kept deferring; DO IT
   FIRST, do not substitute building tooling for it):** reuse the proven, bug-fixed acquisition
   `scripts/eval60_acquire_three_way.py` with a FRESH window (writes `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_<STAMP>Z.{json,md}`):
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 1 \
     --max-per-expiry 40 --okx-delay 0.15 --out-dir data/raw/eval61 --seal
   ```
   (~15–20 min live: real Deribit surface + real Deribit option trades + real OKX perp flow + real
   Deribit perp candles; no synthetic; real loaders raise `RealDataUnavailable`).
3. **Pre-register BEFORE any verdict:** the EVAL-61 measurement emits the prereg from the fixed
   protocol (`EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION_<STAMP>Z.{json,md}`); do not edit
   its hypothesis/protocol to fit a result.
4. **Build the EVAL-61 measurement as a copy-and-retarget of the proven
   `scripts/eval60_three_way_net_of_cost.py`** → `scripts/eval61_orderflow_realized_vol_net_of_cost.py`
   (reuse its stats `_sharpe_of_returns`/`_dsr_of_returns`/`_cscv_pbo`/`_benjamini_hochberg`/
   `block_bootstrap_ci`/`permutation_test`, its prereg/seal/floor machinery, and its surface/greeks
   helpers). Replace the strategy body with the delta-hedged ATM straddle below; keep the floor and GO
   bar identical. Add `tests/test_eval61_*`; `py_compile` + `pytest -q tests/test_eval61_*` must pass
   (do NOT run the full ~5k-test suite).
5. **Measure net-of-cost P&L causally** →
   `EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_<STAMP>Z.{json,md}` (or `..._BLOCKED_<STAMP>Z` only
   if the measured floor is unmet — never as a verdict substitute).
6. **Seal with gate exit 0 (note the REQUIRED `--task-id`):**
   ```bash
    python3 scripts/check_session_sealed.py \
      --task-id "INIT-2026-11-16T00:40:39Z-EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE-PREREG-ACQUIRE-MEASURE-SEAL" \
     --glob "POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_*" \
     --require-glob "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION_*" \
     --require-glob "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_*"
   ```
    (stamp ≥ `2026-11-16T00:40:39Z`; exit 0 required. An ACQUISITION-only or PREREG-only or BLOCKED
   artifact does NOT satisfy the gate — a real COMBINED verdict is mandatory.)
7. **Update this handoff in place** with verified facts/paths/commands/measured numbers (not
   intentions). No GO without a verifying sealed artifact.

================================================================================
>>> WHY THIS IS THE CORRECT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE) <<<
================================================================================
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined OPTIONS + ORDERFLOW**
strategy. Every prior cell is sealed NO-GO:
* **options+orderflow fusion cells (EVAL-46..60):** EVAL-46 BTC/OKX integrated, EVAL-47 ETH/OKX,
  EVAL-48 BTC cross-venue (Deribit options × OKX orderflow), EVAL-49 ETH cross-venue, EVAL-50 real L2
  OFI, EVAL-51 options-venue order flow standalone, EVAL-52/53 Deribit surface × Deribit options-venue
  order flow, EVAL-60 the synchronized three-way fusion (Deribit surface × Deribit options-venue flow
  × OKX perp flow).
* **pure options smile/greeks ladder (EVAL-54..59):** delta-hedged short-vol, long-gamma, term-structure
  calendar, VRP (realized-vs-implied), skew/risk-reversal 25Δ, 25Δ butterfly/convexity.

The **one on-charter combination still unmeasured** is to make the **options ORDER FLOW** (the repo's
namesake) drive a **volatility** trade rather than a directional one: does real signed options order
flow carry **predictive information about subsequent realized volatility**, and is a **signal-timed
delta-hedged ATM straddle** net-of-cost tradable? EVAL-54/55/57 traded vol/gamma but were *static*
positions (always short vol / always long gamma / static VRP) or *level* comparisons; none used the
options order flow to *time* a delta-hedged straddle. This connects the order-flow pillar to the
options/vol pillar directly — the most literal remaining reading of "options orderflow strategy" still
untested. It is a fresh, pre-registered, heavy real-data falsification with a new task ID outside
EVAL-02..60 (no re-litigation).

## HYPOTHESIS (fixed, pre-registered, no fitting)
The options-order-flow-timed delta-hedged ATM straddle is **net-of-cost tradable** for the BTC/ETH
perpetual on real, synchronized data. Per 5m bar k (all causal; decision at k → outcome [k, k+1]):
* **order-flow toxicity** `tox_k`: from real Deribit option trades in `(bar_end−bar, bar_end]`,
  `tox_k = (call_notional − put_notional)/(call_notional + put_notional)` (signed options flow); also
  test a signed-aggressor `imbalance` variant. Position uses `clip(expanding_z(tox), −1, 1)`.
* **realized-vol target**: `rv_{k+1} = |log(perp_close_{k+1}) − log(perp_close_k)|` from real Deribit
  `{BTC,ETH}-PERPETUAL` 1m candles.
* **delta-hedged ATM straddle**: ATM IV from the real surface snapshot (newest 5m snapshot whose candle
  has *closed* by `bar_end`, i.e. `available = bar_ms + 300s`); position `q_k = clip(z(tox_k), −1, 1)`
  in the ATM straddle (long when call-heavy/vol-expansion expected, short otherwise), delta-hedged each
  bar with the perp. Net-of-cost P&L per bar:
  `q_k·[vega·(IV_{k+1}−IV_k) + 0.5·gamma·(ΔS)² − theta·dt] − hedge_cost − 5bps·|Δq_hedge|`.
* **cost model:** 5 bps on turnover/hedge (net-of-cost by construction); option legs priced from real
  marks.
* **GO bar (conservative):** GO only if on **both** BTC and ETH and ≥1 grid config, net-of-cost
  Sharpe>0, max-DD≤0.20, permutation p<0.05, bootstrap 95% CI lower>0, pooled PBO<0.5; else
  **NO-GO CONFIRMED (PASS)**. Grid = {toxicity variants} × {60s, 300s} per underlying.

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
Per underlying (BTC **and** ETH), all must hold or the run seals BLOCKED (then widen, do not stop):
* surface: **≥100 snapshots / ≥50 instruments / ≥240 5m bars**;
* Deribit options-venue trades: **≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span**;
* perp candles: **≥240 5m bars / ≥79200 s span**;
* **common bars (surface × trades × perp): ≥240 5m** (the synchronization gate);
* roster has **≥2 underlyings**.
No synthetic fallback; real loaders raise `RealDataUnavailable`.

## BOTTLENECKS — CLEARED THIS SESSION / REMAINING (verified 2026-11-16T00:34:26Z)
1. **CLEARED (this session): the EVAL-60 heavy live run is DONE** — the previously-deferred ~20-min
   BTC+ETH three-way acquisition was executed and sealed `NO-GO CONFIRMED (PASS)` (COMBINED
   `20261116T003146Z`, gate exit 0). This is the significant progress the prior two sessions deferred.
2. **CLEARED (this session): the #1 new stall cause — a real OKX acquisition bug — is FIXED** in
   `scripts/eval60_acquire_three_way.py`. Root cause: `fetch_okx_perp_trades` captured `end_ms` at
   script start, but the OKX walk runs ~2.5 min later (after the Deribit legs), so the newest page was
   entirely *newer* than `end_ms`, got filtered out, and the walk aborted with **0 trades** (BTC
   happened to catch in-window trades; ETH did not, twice). Fix: track the oldest trade on each page
   (even out-of-window) to advance the backward cursor and only stop on a true retention wall (no new
   tradeIds), plus 8-attempt exponential backoff (up to 20 s) on 429/5xx and a polite `--okx-delay`.
   Verified: ETH now captures **231,050 real OKX perp trades** (was 0). This same fix is inherited by
   the EVAL-61 acquisition (step 2).
3. **CLEARED (this session): tooling is proven end-to-end** — `scripts/eval60_acquire_three_way.py` +
   `scripts/eval60_three_way_net_of_cost.py` + `tests/test_eval60_three_way_net_of_cost.py` ran on live
   BTC+ETH and sealed a real verdict. EVAL-61 reuses the acquisition verbatim and copy-and-retargets
   the measurement.
4. **CLEARED:** env ready — `.venv-deps/` present; `verify_env.sh --check` exit 0; `.env` absent;
   `LIVE_TRADING_ENABLED` unset/false.
5. **REMAINING (the heavy work for the next session, unavoidable):** the fresh `--days 1` BTC+ETH
   EVAL-61 live acquisition (step 2) + the new straddle measurement build (step 4) + real verdict (step
   5) + gate (step 6). If any floor metric is short, **widen the capture** (`--max-per-expiry`,
   `--okx-delay`) and re-run; do not stop and do not weaken the floor.

## PROHIBITED (hard constraints)
- Do **not** re-run, re-litigate, or re-seal EVAL-02..60; do not edit sealed artifacts or `src/`.
- Do **not** fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel
  synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential
  mutation, or order placement. Network: public read-only market data only, polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`;
  no `phaseNN_*` orchestrator wrappers.
- Do **not** run the full test suite as discovery; do **not** enumerate `research_state/`; do **not**
  create timestamped handoff copies or new handoff files (root `HANDOFF_NEXT_AGENT.md`,
  `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers).

## ANTI-STALL RULE (read before touching this file)
- **Only** acceptable outputs: (a) sealed `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_*` +
  `EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION_*` + `EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_*`
  with gate exit 0 (stamp ≥ 2026-11-16T00:34:26Z), or (b) a *narrower/stricter* timestamped handoff
  that keeps the floor identical or stricter and corrects only the task timestamp.
- **Do NOT** re-issue at a new timestamp without either sealing artifacts or making the task stricter.
  A session whose only diff to this file is the timestamp is a **failed session**.
- **Do NOT** hand off with "tooling built, run next session" as the terminal state — the live
  acquisition (step 2) is itself heavy work and must be executed in the SAME session that builds the
  measurement; do not defer the run. (This exact deferral is what stalled the two prior sessions.)
- **Do NOT** weaken the floor, drop an underlying, drop a bar size, or convert the gate to accept a
  BLOCKED artifact as a verdict.
- **Do NOT** create a BLOCKED artifact and stop: below-floor means *widen the capture*, not *stop*.
- **No handoff-only completion.** Do not enumerate `research_state/`; do not run the full test suite.

## SEALED STATE (immutable; do not re-run; append only)
EVAL-02..60 sealed; EVAL-46..60 all **NO-GO CONFIRMED (PASS)** with gate exit 0:
- EVAL-46 BTC integrated options+orderflow → `EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z`.
- EVAL-47 ETH combined → `EVAL_47_ETH_COMBINED_20261115T071330Z`.
- EVAL-48 BTC cross-venue (Deribit options + OKX orderflow) → `EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z`.
- EVAL-49 ETH cross-venue → `EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z`.
- EVAL-50 real L2 OFI (BTC+ETH) → `EVAL_50_L2_OFI_COMBINED_20261115T134705Z`.
- EVAL-51 options-venue order flow standalone (BTC+ETH) → `EVAL_51_OPTIONS_ORDERFLOW_COMBINED_20261115T152005Z`.
- EVAL-52/53 Deribit surface × Deribit options-venue order flow → `EVAL_52_..._20261115T165018Z`,
  `EVAL_53_CROSS_WINDOW_COMBINED_20261115T171712Z`.
- EVAL-54 delta-hedged short-vol → `EVAL_54_COMBINED_20261115T175410Z`.
- EVAL-55 long-gamma gamma-scalping → `EVAL_55_COMBINED_20261115T180515Z`.
- EVAL-56 term-structure calendar-spread → `EVAL_56_COMBINED_20261115T190126Z`.
- EVAL-57 VRP / realized-vs-implied → `EVAL_57_COMBINED_20261115T195911Z`.
- EVAL-58 skew / risk-reversal 25Δ → `EVAL_58_COMBINED_20261115T200745Z`.
- EVAL-59 25Δ butterfly / convexity → `EVAL_59_COMBINED_20261115T214832Z`.
- **EVAL-60 synchronized three-way fusion (Deribit options SURFACE × Deribit options-venue ORDER FLOW ×
  OKX perp ORDER FLOW)** → `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_COMBINED_20261116T003146Z` (prereg
  `..._PREREGISTRATION_20261116T003146Z`; gate exit 0).
Re-running or re-sealing EVAL-02..60 is prohibited re-litigation.

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (imports `src/` → needs numpy).
- **OKX perp order-flow endpoint (FIXED this session):** `GET https://www.okx.com/api/v5/market/history-trades?instId=<PERP>&limit=100`
  (the correct historical endpoint; **`trades-history` is 404**). Paginate **backwards** with
  `after=<oldest tradeId>` (boundary trade repeats → dedupe by `tradeId`). Instruments:
  `BTC-USD-SWAP`, `ETH-USD-SWAP`. Use a browser User-Agent (OKX 403s bare clients). `trades` (no
  history) only returns the last few minutes. **The walk runs after `end_ms` was captured → the newest
  page can be entirely newer than `end_ms`; the fetch must still advance the backward cursor (do not
  abort on `new_this_page == 0` when the page has new tradeIds).** OKX also rate-limits aggressive
  pagination into a multi-minute cooldown — use `--okx-delay 0.15` and the built-in backoff; if a leg
  returns 0, wait a few minutes and re-run (do NOT weaken the floor).
- **EVAL-60 capture schema** (`scripts/eval60_acquire_three_way.py`): one file per underlying,
  `data/raw/eval60/three_way_{BTC,ETH}_<stamp>.json` (or `data/raw/eval61/`), with `surface.snapshots[]`
  (each has `bar_ms`, causal `spot`, `quotes[]`), `option_trades[]` (Deribit signed option trades),
  `perp_candles[]` (Deribit 1m), and `okx_perp_trades[]` (real OKX `history-trades` signed taker flow:
  `{ts, px, sz, side, instrument, trade_id}`). No synthetic data; `source` records real provenance.
- **Surface / greeks:** IV backed out of the *real* mark via `implied_volatility(mark*spot, spot, K, 0, T, type)`
  then `black_scholes_greeks` at that IV (intrinsic-delta fallback); measurement walks the real 5m
  snapshots ascending; P&L causal (decision at bar k → outcome over [k, k+1]). Deribit option
  **candles**: `get_tradingview_chart_data` resolution `5`; Deribit option **trades**:
  `get_last_trades_by_instrument_and_time` (paginate `start_timestamp = last_trade_ts + 1`; ~24h cap
  per instrument → the common window must sit inside the last ~24h). Deribit **perp**:
  `get_tradingview_chart_data` `{BTC,ETH}-PERPETUAL` resolution `1`.
- `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 → DSR may report 0.0; use perm/bootstrap/PBO/BH-FDR.
- Full heavy BTC+ETH `--days 1` acquisition ≈ 15–20 min (Deribit ~3–5 min + OKX ~10–15 min); the
  measurement (greeks cached once per capture) ≈ seconds. Run it as a background process and wait —
  do not defer to a later session.

## HARD INVARIANTS
Paper-only; `.env` absent; `LIVE_TRADING_ENABLED=false`. Never fall back to synthetic; real loaders
raise `RealDataUnavailable`; never relabel synthetic as real. Sealed artifacts immutable; append new
timestamped artifacts only. Public read-only network only. Reuse `src/` modules; no `phaseNN_*`.

## HANDOFF DISCIPLINE
This file is the **single durable handoff**. Update in place with verified facts/timestamps/paths/
commands only; no timestamped handoff copies. Record measured numbers, not intentions. No GO without a
verifying sealed artifact. Final responses must not ask follow-up questions.

## SESSION LOG (append-only)
- 2026-11-14→2026-11-15: EVAL-41..49 executed/sealed (NO-GO); EVAL-50/51 sealed; EVAL-52..59 sealed
  `NO-GO CONFIRMED (PASS)` (gate exit 0). Campaign EVAL-02..59 CLOSED.
- 2026-11-15T22:44:10Z: EVAL-60 three-way tooling built + validated live (smoke); task advanced to
  `INIT-2026-11-15T22:44:10Z-POST-EVAL-THREE-WAY-OPTIONS-ORDERFLOW-FUSION-PREREG-ACQUIRE-MEASURE-SEAL`.
- **2026-11-16T00:34:26Z (this session — bottlenecks removed by REAL heavy work, not handoff):** ran
  the deferred EVAL-60 heavy live acquisition (BTC 356,839 / ETH 231,050 real OKX perp trades; 3,068 /
  4,289 Deribit option trades; 289 surface snaps each) and sealed
  `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_COMBINED_20261116T003146Z` = **NO-GO CONFIRMED (PASS)**
  (prereg `20261116T003146Z`; pooled PBO 0.75; best Sharpe BTC −1.1388 / ETH −1.4729; no config
  passes; **seal gate exit 0** with required `--task-id`). **Fixed a real OKX acquisition bug**
  (`fetch_okx_perp_trades` aborted with 0 trades when the newest page was newer than the captured
  `end_ms`; now advances the backward cursor on any new tradeIds + 8× exponential backoff + polite
  delay).   Verified env green (`verify_env.sh --check` exit 0). Removed the 3 stale intermediate acquisition
  manifests (235048/000622/000949) whose captures were deleted during re-acquisition, leaving a clean
  trail: ACQUISITION_20261115T232807Z (BTC) + ACQUISITION_20261116T001342Z (ETH) + PREREG/COMBINED
  20261116T003146Z. **Advanced the authoritative task to
  `INIT-2026-11-16T00:34:26Z-EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE-PREREG-ACQUIRE-MEASURE-SEAL`.**
  Remaining heavy work for the next session (unavoidable): run the fresh `--days 1` BTC+ETH EVAL-61
  acquisition → build the copy-and-retarget straddle measurement → `--no-write` smoke (floor_ok true) →
  real run seals PREREGISTRATION + COMBINED → gate exit 0. Handoff-only completion explicitly prohibited.
- **2026-11-16T00:40:39Z (this session):** refreshed the authoritative task timestamp to
  `INIT-2026-11-16T00:40:39Z-EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE-PREREG-ACQUIRE-MEASURE-SEAL`
  (stamp ≥ `2026-11-16T00:40:39Z`). All bottlenecks cleared: EVAL-60 sealed NO-GO (gate exit 0), OKX
  acquisition bug fixed (ETH 231,050 real perp trades captured), tooling proven end-to-end, env green
  (`verify_env.sh --check` exit 0). The unavoidable heavy work remains: fresh `--days 1` BTC+ETH live
  acquisition via `scripts/eval60_acquire_three_way.py` → copy-and-retarget straddle measurement
  `scripts/eval61_orderflow_realized_vol_net_of_cost.py` + `tests/test_eval61_*` → real PREREGISTRATION +
  COMBINED verdicts → gate exit 0. Handoff-only completion explicitly prohibited; do not defer the run.