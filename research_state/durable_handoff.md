# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK (do this next; no other task is valid until it is done)

**TASK `INIT-2026-11-15T15:25:30Z-EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION-ACQUIRE-MEASURE-AND-SEAL`.**

EVAL-51 is **SEALED `NO-GO CONFIRMED (PASS)`**. Every individual charter leg is now sealed `NO-GO`:
option *surface/candles/greeks* (EVAL-46..49), *spot* order flow (EVAL-43/45), *spot* L2-book OFI
(EVAL-50), and *options-venue* order flow (EVAL-51). **EVAL-52 is the next focus campaign** and it is a
**fresh, pre-registered, heavy real-data falsification** of the **one combination never measured on real
data**: the **Deribit options SURFACE** (GEX flip / IV-skew term structure / calibration residual) fused
with the **Deribit OPTIONS-VENUE ORDER FLOW** (signed option-trade imbalance) — the *pure options-side*
combined strategy that is literally the repo name/charter ("options orderflow strategy"). This is a
**new timestamped task ID**, never a re-run or re-litigation of EVAL-02..51. **No other task is valid
until step 6 passes.**

**YOU MUST, in this session, in this order, and may not skip any step:**

1. **Verify env (fast, ~4 s — do NOT run the full test suite):**
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   ./scripts/verify_env.sh --check
   ```
   Verified green at 2026-11-15T15:25:30Z (python 3.12.3, pytest/numpy/pandas/scipy/pydantic/yaml/requests
   ok, EVAL-37 6 passed, EVAL-36 7 passed, exit 0). If it is still green, proceed immediately to step 2.

2. **Build the EVAL-52 tooling (this is the non-escapable engineering work).** The three files do **not
   exist yet** — creating them IS the work, not a reason to defer:
   `scripts/eval52_acquire_synchronized_options.py`,
   `scripts/eval52_options_surface_orderflow_net_of_cost.py`,
   `tests/test_eval52_options_surface_orderflow_net_of_cost.py`.
   Reuse, do not duplicate, the sealed primitives:
   - **Copy, don't reinvent:** `scripts/eval51_acquire_options_orderflow.py` is the closest template for
     the order-flow leg (instrument discovery, paginated trades, perp candles, sealing); add a
     **surface leg** that mirrors `scripts/eval48_acquire_deribit_options.py` (`fetch_candles` via
     `/public/get_tradingview_chart_data` resolution `5`, `build_snapshots` → chain-shaped quotes with
     `bid`/`ask`/`mark`, one snapshot per 5m bar).
   - **Options-surface alpha:** reuse
     `src/analytics/integrated_options_orderflow_evaluation.py::_options_signal_components(chain, spot,
     now, seed=42)` unchanged (GEX flip distance, IV-skew term-structure slope, calibration residual;
     newest snapshot ≤ bar_end). EVAL-48 snapshots are already `OptionsChain`-compatible.
   - **Options-venue order flow:** reuse the signal construction of
     `scripts/eval51_options_orderflow_net_of_cost.py` (per-bar `imbalance`, `notional_imbalance`,
     `call_minus_put` from real Deribit `amount`/`index_price`).
   - **Statistics:** reuse `_sharpe_of_returns`, `permutation_test(..., paired=True, seed=42)`,
     `block_bootstrap_ci(..., statistic=_sharpe_of_returns)`, CSCV PBO (k=4), BH-FDR, DSR from the sealed
     EVAL-46/48/51 modules. **No new `phaseNN_*` orchestrator wrappers.**
   - Compile + test before any capture:
     ```bash
     python3 -m py_compile scripts/eval52_acquire_synchronized_options.py \
         scripts/eval52_options_surface_orderflow_net_of_cost.py \
         tests/test_eval52_options_surface_orderflow_net_of_cost.py
     python3 -m pytest -q tests/test_eval52_options_surface_orderflow_net_of_cost.py   # must pass
     ```
     (Do not run these before the files exist — that is why step 1 is env-only.)

3. **Synchronized heavy real acquisition (live public read-only Deribit, BTC + ETH, same ~24h window,
   both legs):** the surface leg uses real Deribit 5m option candles (historical candles ARE available →
   back-fillable); the order-flow leg uses real Deribit option trades (**Deribit caps signed trade
   history at ~24h**, so the common window must sit inside the last ~24h). Capture both legs over the
   **same** window:
   ```bash
   python3 scripts/eval52_acquire_synchronized_options.py \
       --underlying BTC --underlying ETH --days 1 \
       --out-dir data/raw/eval52 --seal
   ```
   Writes `data/raw/eval52/options_surface_{BTC,ETH}_<UTC>.json` and
   `data/raw/eval52/options_orderflow_{BTC,ETH}_<UTC>.json`, then seals
   `EVAL_52_SYNCHRONIZED_ACQUISITION_<UTC>.{json,md}`. **Do not proceed unless both underlyings clear the
   per-underlying floor** (the script prints the per-underlying summary):
   - surface leg: ≥100 real option-chain snapshots per underlying, ≥50 option instruments with data,
     ≥240 5m bars (EVAL-48 sealed 133 BTC / 109 ETH snapshots);
   - order-flow leg: ≥2000 option trades, ≥50 option instruments with trades, ≥240 bars, ≥79200 s span
     per underlying (EVAL-51 sealed BTC 5347 trades / 98 instruments / 289 bars, ETH 3429 / 102 / 289);
   - the two legs must **overlap on a common bar grid** (synchronized window).
   Below floor ⇒ widen `--max-per-expiry` / `--max-expiry-days`; **never** widen the floor and **never**
   emit `{"valid": true}` for a below-floor capture.

4. **Smoke measurement (seals nothing):**
   ```bash
   python3 scripts/eval52_options_surface_orderflow_net_of_cost.py --no-write
   ```
   Confirm `floor_ok: true` and inspect per-config Sharpes/PBO.

5. **Seal the verdict** (preregisters `EVAL_52_PREREGISTRATION_<UTC>` BEFORE the verdict, then seals
   `EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_<UTC>`):
   ```bash
   python3 scripts/eval52_options_surface_orderflow_net_of_cost.py
   ```

6. **Seal gate — the session FAILS unless BOTH the synchronized acquisition AND a floor-passing COMBINED
   verdict exist with a stamp ≥ the task timestamp** (an `EVAL_52_BLOCKED_*` alone will NOT pass, so a
   short capture cannot satisfy the campaign). `check_session_sealed.py` supports these flags (verified
   2026-11-15T15:25:30Z):
   ```bash
   python3 scripts/check_session_sealed.py \
        --task-id "INIT-2026-11-15T15:25:30Z-EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION-ACQUIRE-MEASURE-AND-SEAL" \
        --glob "EVAL_52_SYNCHRONIZED_ACQUISITION_*" \
        --require-glob "EVAL_52_PREREGISTRATION_*" \
        --require-glob "EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_*"
   ```
   Must print `OK` lines and exit `0`.

7. **Append a session-log line** to this file (measured numbers + artifact paths) and leave this handoff
   as the single durable record.

**Definition of done:** step 6 exits `0` with an
`EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_<UTC>` artifact present (verdict `GO CONFIRMED` or
`NO-GO CONFIRMED (PASS)`), plus the acquisition and prereg artifacts. A handoff-only session, a
`--no-write`-only session, a re-run of EVAL-02..51, a full-test-suite discovery loop, or a
`research_state/` enumeration are **all failures**.

## WHY THIS IS THE RIGHT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE)
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined options + orderflow** strategy.
EVAL-46/47 (BTC/ETH OKX) and EVAL-48/49 (BTC/ETH Deribit-cross-venue) fused the *option candle/surface*
pillar with the *spot* order-flow pillar → **NO-GO**. EVAL-50 sealed *spot* L2-book OFI → **NO-GO**.
EVAL-51 sealed the *options-venue* order flow standalone → **NO-GO**. The **one combination never
measured** is the options market's **own surface fused with its own order flow** — a *pure options*
combined strategy, the most literal reading of "options orderflow strategy" and the only remaining
charter cell that is both untested and heavy. EVAL-52 is a **new timestamped task ID**, never a re-run.

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
Synchronized real Deribit capture for **both BTC and ETH** over the **same** ~24h window meeting the
per-underlying floor (surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options-venue order flow
≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s; legs time-overlapping) →
`scripts/eval52_options_surface_orderflow_net_of_cost.py` (3 pre-registered fusion rules × {15s, 5m}
bars × 3 order-flow signals; causal expanding z-score; position `clip(z/2,-1,1)`; net-of-cost at 5 bps on
turnover; 1000 paired permutations + 1000 block-bootstrap + CSCV PBO k=4 + BH-FDR + DSR; seed 42) →
pre-register `EVAL_52_PREREGISTRATION_*` BEFORE measurement → seal
`EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_*` → pass the seal gate requiring acquisition + prereg +
COMBINED. No prior-EVAL re-runs, no `research_state/` enumeration, no full test suite, no handoff-only
session.

## EVAL-52 PROTOCOL (pre-declared; implement in the two scripts)
- **Options-surface alpha (causal, per bar, newest snapshot ≤ bar_end):** components `gex_flip_signal`
  (long when spot > gamma flip), `skew_slope_signal` (sign of IV skew term-structure slope across
  tenors), `calib_residual_signal` (contrarian fade of surface-calibration residual);
  `options_signal_raw = mean(components)` clipped to [-1, 1] (EVAL-46 `_options_signal_components`
  pattern).
- **Options-venue order flow (per bar, from real option trades in `(bar_end-bar, bar_end]`):**
  `imbalance = (buy_amt - sell_amt)/(buy_amt+sell_amt)`;
  `notional_imbalance = (notional_buy - notional_sell)/(notional_buy+notional_sell)`;
  `call_minus_put = ((call_buy-call_sell)-(put_buy-put_sell))/total_amt` (amounts = Deribit `amount`,
  notional weighted by `index_price`).
- **Fusion rules (pre-registered, fixed, no fitting; identical to EVAL-46's three rules):**
  (a) `sign_agreement` — both options-side legs agree in sign → take that sign, else flat;
  (b) `regime_filter` — surface sign as causal regime gate × order-flow direction;
  (c) `continuous_zscore` — causal expanding z-score of each leg, summed, `clip(z_sum/2,-1,1)`.
- **Grid:** fusion rule ∈ {sign_agreement, regime_filter, continuous_zscore} × bar ∈ {15s, 5m} ×
  order-flow signal ∈ {imbalance, notional_imbalance, call_minus_put}.
- **Z:** causal expanding z-score, window 20.
- **Cost:** 5 bps on turnover (conservative taker + impact), net-of-cost by construction.
- **GO bar (conservative):** GO only if on **both** BTC and ETH and ≥1 config, net-of-cost Sharpe > 0, no
  kill-switch breach (max-DD ≤ 0.20), permutation p < 0.05, bootstrap 95% CI lower > 0, and pooled
  PBO < 0.5. Else `NO-GO CONFIRMED (PASS)`. Below floor → `BLOCKED` (never NO-GO).

## BOTTLENECKS — CLEARED (verified 2026-11-15T15:25:30Z; do not re-verify)
1. **CLEARED (the historical blocker): the handoff-only loop.** Three prior sessions
   (`INIT-2026-11-15T14:17:27Z`, `15:06:06Z`, `15:11:17Z`) defined EVAL-51 but **never sealed a verdict**;
   the 15:18–15:20 session executed EVAL-51 end-to-end and sealed it `NO-GO CONFIRMED (PASS)`. EVAL-51 is
   done and immutable — nothing left to defer. See "ANTI-STALL RULE" below: a session that only edits
   this file has failed.
2. **CLEARED:** env ready — `.venv-deps/` present; `./scripts/verify_env.sh --check` exit 0 (3.4 s);
   `.env` absent; `LIVE_TRADING_ENABLED` unset/false.
3. **CLEARED:** Deribit public endpoints live and reachable from this environment (checked 15:25Z):
   `get_time` returns `testnet:false`; `get_tradingview_chart_data` returns `status:ok` with
   ticks/open/close/volume for option instruments. Public read-only market data only.
4. **CLEARED:** all reuse inputs on disk — EVAL-51 options-order-flow captures
   (`data/raw/eval51/options_orderflow_{BTC,ETH}_20261115T151843Z.json`), EVAL-48 surface acquisition +
   `fetch_candles`/`build_snapshots` (chain-shaped quotes: `bid`/`ask`/`mark`/`strike`/`expiry`/
   `option_type`), EVAL-46 `_options_signal_components` + statistics/fusion modules. EVAL-02..51 sealed
   immutable.
5. **CLEARED:** no stale processes, no `data/raw/eval52/` dir, clean working tree — a fresh capture can
   start with no collision.
6. **CLEARED:** `scripts/check_session_sealed.py` accepts `--glob` + repeatable `--require-glob`
   (AND semantics) and `--require-any-glob` (OR); `--help` verified 15:25:30Z. The gate in step 6 is
   executable as written.
7. **Remaining work is the heavy work itself** (build `eval52_*` tooling + synchronized capture +
   measurement), not an unblock. There is no valid alternative task.

## ANTI-STALL RULE (read before touching this file)
- The **only** acceptable outputs of a session are: (a) sealed
  `EVAL_52_SYNCHRONIZED_ACQUISITION_*` + `EVAL_52_PREREGISTRATION_*` +
  `EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_*` with gate exit 0, or (b) a *narrower* timestamped
  handoff whose floor is **identical or stricter** and whose only change is the corrected task timestamp.
- **Do NOT** re-issue this task at a new timestamp without either sealing it or making it stricter. A
  session whose only diff to this file is the timestamp is a failed session and is the exact failure mode
  this file has already suffered three times.
- **Do NOT** weaken the floor, drop an underlying, drop a fusion rule, drop a bar size, reduce
  permutations/bootstrap/BH-FDR/PBO/DSR, or convert the gate to `--require-any-glob` in order to pass.
- **Do NOT** create `EVAL_52_BLOCKED_*` and stop: below-floor means *widen the capture*, not *stop*.
- If an unavoidable external block appears (network/venue outage), re-run the acquisition with a wider
  `--max-per-expiry`/`--max-expiry-days` first; only then record a blocked artifact **plus** the exact
  failing floor metric and the command to resume.

## PROHIBITED (hard constraints)
- Do **not** re-run, re-litigate, or re-seal EVAL-02..51; do not edit sealed artifacts or `src/`.
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
All campaign rungs EVAL-02..51 are sealed. EVAL-46..51 (the options+orderflow ladder) are all
**NO-GO CONFIRMED (PASS)**:
- **EVAL-46** integrated options+orderflow net-of-cost on full dense BTC → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z.{json,md}` (101 BTC snapshots ×
  2 real OKX BTC tapes × 3 fusion rules; pooled PBO 0.833; BH-FDR rejected nothing).
- **EVAL-47** ETH combined → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_47_ETH_COMBINED_20261115T071330Z.{json,md}` (5 ETH tapes × 3 rules; gate exit 0).
- **EVAL-48** BTC cross-venue (Deribit options + OKX BTC orderflow) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_48_CROSS_VENUE_COMBINED_20261115T081951Z.{json,md}` (prereg
  `EVAL_48_PREREGISTRATION_20261115T081951Z`; acquisition `EVAL_48_DERIBIT_ACQUISITION_20261115T081709Z`;
  133 Deribit BTC snapshots × 2 OKX BTC tapes × 3 rules; pooled PBO 0.667).
- **EVAL-49** ETH cross-venue (Deribit ETH options + OKX ETH orderflow) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_49_ETH_CROSS_VENUE_COMBINED_20261115T101149Z.{json,md}` (109 Deribit ETH
  snapshots × 5 ETH tapes × 3 rules; gate exit 0).
- **EVAL-50** real L2 order-book OFI (BTC+ETH) → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_50_L2_OFI_COMBINED_20261115T134705Z.{json,md}` (prereg
  `EVAL_50_PREREGISTRATION_20261115T134705Z`; acquisition `EVAL_50_L2_DEPTH_ACQUISITION_20261115T134456Z`;
  floor met BTC 443 snaps/999.6 s, ETH 444 snaps/999.6 s; 4 configs/instrument; pooled PBO 0.5000).
- **EVAL-51** real Deribit **options-venue order flow** (signed option-trade flow → underlying perp),
  BTC+ETH → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_51_OPTIONS_ORDERFLOW_COMBINED_20261115T152005Z.{json,md}` (prereg
  `EVAL_51_PREREGISTRATION_20261115T152005Z`; acquisition
  `EVAL_51_OPTIONS_ORDERFLOW_ACQUISITION_20261115T151843Z` — BTC 5347 trades / 98 instruments / 289 5m
  bars / 86010 s, ETH 3429 trades / 102 instruments / 289 bars / 86381 s; 6 configs/underlying; best
  Sharpe BTC −1.864 `imbalance::bar5`, ETH −1.897 `call_minus_put::bar15`, pooled PBO 0.5000, no config
  passes; seal gate exit 0).
- Earlier: EVAL-37 post-termination audit `PASS 9/9`; EVAL-41/42 options pillar closed; EVAL-43
  orderflow full roster `NO-GO CONFIRMED (PASS)`; EVAL-44 `CAMPAIGN_CLOSED` (BTC-scoped); EVAL-45 ETH
  orderflow `NO-GO` + options `BLOCKED`. Prior EVAL-18/31 superseded by EVAL-46.

**The combined options+orderflow thesis is not net-of-cost tradable on BTC/OKX, ETH/OKX, BTC
Deribit-cross-venue, ETH Deribit-cross-venue, real L2 order-book OFI (BTC+ETH), nor options-venue order
flow standalone (BTC+ETH).** EVAL-52 tests the remaining unmeasured combination — options SURFACE ×
options-venue ORDER FLOW — as a fresh heavy falsification.

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (imports `src/` → needs numpy).
- **GRID ALIGNMENT (EVAL-52 specific):** the acquisition writes **two** files per underlying
  (`options_surface_*`, `options_orderflow_*`). The measurement script must load **both**, build the
  5m bar grid from the order-flow/perp side, and attach the **newest surface snapshot with
  `bar_end(snapshot) ≤ bar_end(bar)`** (causal, no lookahead). Intersect the two legs' bar sets; a bar
  present in only one leg is dropped, and the floor check must be computed on the **intersected** grid.
- Deribit options **trades**: `GET /public/get_last_trades_by_instrument_and_time` (params
  `instrument_name`, `start_timestamp`, `end_timestamp`, `count`≤1000, `sorting=asc`); paginate by setting
  `start_timestamp = last_trade_ts + 1` while `has_more`; fields `timestamp`, `direction` (buy/sell
  aggressor), `amount` (underlying units), `price`, `index_price`, `iv`, `trade_id`.
  `GET /public/trades` does NOT exist — use `get_last_trades_by_instrument_and_time`. **Deribit caps
  signed trade history at ~24h per instrument** (older `start_timestamp` returns only the last ~24h);
  use the full option universe to maximize breadth.
- Deribit options **candles** (surface leg): `GET /public/get_tradingview_chart_data` per option
  instrument, resolution `5` (5m) — historical candles ARE available, so the surface leg can be
  reconstructed over the same ~24h window as the trade leg (unlike trades, no ~24h cap). Copy
  `fetch_candles`/`build_snapshots` from `scripts/eval48_acquire_deribit_options.py` (quotes carry
  `bid`/`ask`/`mark`; `mark` = measured 5m chart close; `spread_source: constant_fallback`).
- Underlying perp candles: `GET /public/get_tradingview_chart_data` (instrument `{BTC,ETH}-PERPETUAL`,
  resolution `5`).
- `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 → DSR may report 0.0; use
  perm/bootstrap/PBO/BH-FDR as primary.
- `permutation_test(rets, flat, statistic=_mean, paired=True, seed=42)` tests mean≠0; read `p_value`.
  `block_bootstrap_ci(rets, statistic=_sharpe_of_returns, ...)` → `(point, lo, hi)`.
- Run the **full** synchronized capture; do not use fixed tail slices.

## HARD INVARIANTS
Paper-only; `.env` absent; `LIVE_TRADING_ENABLED=false`. Never fall back to synthetic; real loaders raise
`RealDataUnavailable`; never relabel synthetic as real. Sealed artifacts immutable; append new timestamped
artifacts only. Public read-only network only. Reuse `src/` modules; no `phaseNN_*`.

## HANDOFF DISCIPLINE
This file is the **single durable handoff**. Update in place with verified facts/timestamps/paths/commands
only; no timestamped handoff copies. Record measured numbers, not intentions. No GO without a verifying
sealed artifact. Final responses must not ask follow-up questions.

## SESSION LOG (append-only)
- 2026-11-14T18:21:06Z→2026-11-15T11:03:55Z: EVAL-41..49 executed and sealed (all four venue/asset cells
  NO-GO). EVAL-50 tooling built/tested; prior handoff claimed heavy capture in progress (pid 9687) with
  short pre-capture below floor.
- 2026-11-15T12:08:31Z–13:03:42Z (multiple handoff refreshes): re-verified `pid 9687` not running;
  `data/raw/eval50/` short pre-capture only (266 snaps/~598 s each, below floor); env/tooling ready.
  Repeatedly set the authoritative EVAL-50 capture→measure→seal task. No EVAL-50 verdict sealed.
- **2026-11-15T13:47:05Z (EVAL-50 COMPLETED):** executed full EVAL-50 end-to-end. Capture run #2
  `--duration 1000 --cadence 2 --levels 25` → BTC 443 snaps/999.6 s, ETH 444 snaps/999.6 s (floor met);
  acquisition sealed `EVAL_50_L2_DEPTH_ACQUISITION_20261115T134456Z.{json,md}`. Measurement →
  prereg `EVAL_50_PREREGISTRATION_20261115T134705Z` then `EVAL_50_L2_OFI_COMBINED_20261115T134705Z`
  — **NO-GO CONFIRMED (PASS)**: 4 configs/instrument, best Sharpe BTC −2.68 / ETH −1.01, pooled PBO
  0.5000, BH-FDR rejected 4 configs. Seal gate exit 0. Campaign ladder EVAL-46..50 closed.
- **2026-11-15T15:06:06Z & 15:11:17Z (EVAL-51 task refreshes, no verdict):** re-issued the EVAL-51
  acquire→measure→seal task twice; no acquisition/verdict was sealed (handoff-only sessions).
- **2026-11-15T15:18:43Z–15:20:05Z (EVAL-51 COMPLETED):** executed EVAL-51 end-to-end. Full BTC+ETH
  acquisition `scripts/eval51_acquire_options_orderflow.py --underlying BTC --underlying ETH --days 1
  --out-dir data/raw/eval51 --seal` → BTC 5347 option trades / 98 instruments / 289 5m bars / 86010 s;
  ETH 3429 trades / 102 instruments / 289 bars / 86381 s (floor met); acquisition sealed
  `EVAL_51_OPTIONS_ORDERFLOW_ACQUISITION_20261115T151843Z.{json,md}`. Measurement
  `scripts/eval51_options_orderflow_net_of_cost.py` → prereg `EVAL_51_PREREGISTRATION_20261115T152005Z`
  then `EVAL_51_OPTIONS_ORDERFLOW_COMBINED_20261115T152005Z` — **NO-GO CONFIRMED (PASS)**: 6
  configs/underlying, best Sharpe BTC −1.864 (imbalance::bar5) / ETH −1.897 (call_minus_put::bar15),
  pooled PBO 0.5000, no config passes. Seal gate exit 0. `pytest
  tests/test_eval51_options_orderflow_net_of_cost.py` → 14 passed. EVAL-51 immutable.
- 2026-11-15T15:22:00Z (handoff refresh): re-issued the authoritative initial task as
  `INIT-2026-11-15T15:22:00Z-EVAL-52-...-ACQUIRE-MEASURE-AND-SEAL` (pure options-side combined strategy:
  Deribit options SURFACE × options-venue ORDER FLOW, BTC+ETH, synchronized ~24h window, pre-registered
  net-of-cost falsification). No EVAL-52 artifact sealed in that session.
- **2026-11-15T15:25:30Z (this session, handoff verified + hardened):** re-verified the tree rather than
  re-issuing blindly — `./scripts/verify_env.sh --check` exit 0 (3.4 s); Deribit `get_time` +
  `get_tradingview_chart_data` live and returning `status:ok`; no stale capture processes; `data/raw/eval52/`
  absent; `scripts/eval52*` and `tests/test_eval52*` absent (building them IS the next session's work);
  `check_session_sealed.py --help` confirms `--glob` / repeatable `--require-glob` / `--require-any-glob`.
  Fixed the step-1 ordering bug in the prior handoff (it told the agent to `py_compile`/`pytest` the three
  EVAL-52 files **before** creating them, which would fail immediately — env-only step 1 now). Added the
  EVAL-52 GRID ALIGNMENT gotcha (two capture files must be merged on the causal 5m bar grid; floor
  measured on the intersection) and a hard **ANTI-STALL RULE** (a session whose only diff to this file is
  the task timestamp is a failed session; do not weaken the floor or the gate). New authoritative task:
  **`INIT-2026-11-15T15:25:30Z-EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION-ACQUIRE-MEASURE-AND-SEAL`**.
  Next session must build `eval52_*` tooling, run the synchronized acquisition + `--no-write` smoke +
  sealed verdict, and pass the seal gate requiring BOTH an `EVAL_52_SYNCHRONIZED_ACQUISITION_*` and a
  floor-passing `EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_*` artifact stamped ≥ this task timestamp.