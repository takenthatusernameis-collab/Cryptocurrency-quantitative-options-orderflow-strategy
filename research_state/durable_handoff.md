# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK (do this next; no other task is valid until it is done)

**EVAL-52 IS SEALED (do not re-run):** `NO-GO CONFIRMED (PASS)` at
`research_state/EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_20261115T165018Z.{json,md}` (prereg
`EVAL_52_PREREGISTRATION_20261115T165018Z`; acquisition
`EVAL_52_SYNCHRONIZED_ACQUISITION_20261115T164732Z` — BTC 289 surface snapshots / 102 instruments /
289 5m bars, 4688 option trades / 99 instruments / span 86261.649 s / 288 common 5m bars; ETH 289
snapshots / 102 instruments / 289 5m bars, 3122 option trades / 101 instruments / span 86204.278 s /
287 common 5m bars; 18 configs/underlying, best Sharpe BTC −0.7473
`continuous_zscore::call_minus_put::bar300.0`, ETH −1.6028 `sign_agreement::imbalance::bar300.0`, all
NO-GO, pooled PBO 0.6389, BH-FDR rejected 32 configs; seal gate exit 0). Tooling built/tested
`scripts/eval52_acquire_synchronized_options.py`, `scripts/eval52_options_surface_orderflow_net_of_cost.py`,
`tests/test_eval52_options_surface_orderflow_net_of_cost.py` (7 passed). The options SURFACE ×
options-venue ORDER FLOW (pure options-side) combination is **not net-of-cost tradable on synchronized
real BTC/ETH Deribit data**.

**TASK `INIT-2026-11-15T16:52:00Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION-ACQUIRE-MEASURE-AND-SEAL`.**

EVAL-46..52 are all sealed `NO-GO CONFIRMED (PASS)`. **EVAL-53 is the next focus campaign** — a
**fresh, pre-registered, heavy real-data falsification**: an **independent cross-window replication** of
the EVAL-52 fused options SURFACE × options-venue ORDER FLOW signal on a **new synchronized ~24h
Deribit capture** (BTC+ETH), measured with the same sealed EVAL-52 protocol and combined in a
cross-window meta verdict (window A = EVAL-52 capture `data/raw/eval52/` sealed artifacts, window B =
new EVAL-53 capture). This tests whether the NO-GO is temporally stable or window-specific. It is a
**new timestamped task ID**, never a re-run/re-seal of EVAL-02..52. **No other task is valid until
step 6 passes.**

**YOU MUST, in this session, in this order, and may not skip any step:**

1. **Verify env (fast, ~4 s — do NOT run the full test suite):**
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   ./scripts/verify_env.sh --check
   ```
   Verified green at 2026-11-15T16:50Z (python 3.12.3, deps present, EVAL-37/EVAL-36 green, exit 0). If
   still green, proceed to step 2.

2. **Build EVAL-53 tooling (non-escapable engineering work):**
   `scripts/eval53_cross_window_replication.py` and `tests/test_eval53_cross_window_replication.py`.
   Reuse sealed primitives — do NOT duplicate or modify them: call/read
   `scripts/eval52_acquire_synchronized_options.py` for capture and
   `scripts/eval52_options_surface_orderflow_net_of_cost.py::run_eval52` (or its per-capture helpers) for
   measurement; reuse EVAL-52 stats/protocol/fusion rules unchanged. The script must: (a) accept
   `--window-a-dir data/raw/eval52 --capture-dir-b data/raw/eval53` (or acquire window B in-place),
   (b) run the EVAL-52 net-of-cost evaluation on each window independently, (c) emit a cross-window
   comparison + pooled meta verdict, (d) pre-register `EVAL_53_PREREGISTRATION_<UTC>` BEFORE verdict, and
   (e) seal `EVAL_53_CROSS_WINDOW_COMBINED_<UTC>`. **No new `phaseNN_*` orchestrator wrappers.**
   Compile + test before capture:
   ```bash
   python3 -m py_compile scripts/eval53_cross_window_replication.py \
       tests/test_eval53_cross_window_replication.py
   python3 -m pytest -q tests/test_eval53_cross_window_replication.py   # must pass
   ```

3. **Independent heavy real acquisition — window B (live public read-only Deribit, BTC+ETH, new ~24h
   synchronized window, both legs):** Deribit caps signed option trade history at ~24h, so window B is the
   *current* trailing 24h at capture time (independent of window A `data/raw/eval52/`).
   ```bash
   python3 scripts/eval52_acquire_synchronized_options.py \
       --underlying BTC --underlying ETH --days 1 \
       --out-dir data/raw/eval53 --seal
   ```
   **Do not proceed unless both underlyings clear the per-underlying floor on window B:**
   surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; order flow ≥2000 trades / ≥50 instruments /
   ≥240 bars / ≥79200 s span; legs time-overlapping (common 5m bars ≥240). Below floor ⇒ widen
   `--max-per-expiry` / `--max-expiry-days`; **never** widen the floor and **never** emit `{"valid": true}`
   for a below-floor capture.

4. **Smoke measurement (seals nothing):**
   ```bash
   python3 scripts/eval53_cross_window_replication.py \
       --window-a-dir data/raw/eval52 --window-b-dir data/raw/eval53 --no-write
   ```
   Confirm `floor_ok: true` for window B and inspect per-window Sharpes/PBO.

5. **Seal the verdict** (preregisters `EVAL_53_PREREGISTRATION_<UTC>` BEFORE verdict, then seals
   `EVAL_53_CROSS_WINDOW_COMBINED_<UTC>` or `EVAL_53_BLOCKED_<UTC>` if below floor):
   ```bash
   python3 scripts/eval53_cross_window_replication.py \
       --window-a-dir data/raw/eval52 --window-b-dir data/raw/eval53
   ```

6. **Seal gate — session FAILS unless window-B acquisition AND a floor-passing COMBINED cross-window
   verdict exist with stamp ≥ task timestamp** (`EVAL_53_BLOCKED_*` alone will NOT pass):
   ```bash
   python3 scripts/check_session_sealed.py \
       --task-id "INIT-2026-11-15T16:52:00Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION-ACQUIRE-MEASURE-AND-SEAL" \
       --glob "EVAL_52_SYNCHRONIZED_ACQUISITION_*" \
       --require-glob "EVAL_53_PREREGISTRATION_*" \
       --require-glob "EVAL_53_CROSS_WINDOW_COMBINED_*"
   ```
   (Window-A artifacts already sealed under `EVAL_52_SYNCHRONIZED_ACQUISITION_*` in `data/raw/eval52/`
   + `research_state/`; the gate requires a new window-B acquisition manifest stamped ≥ task time — ensure
   window B's `--seal` produces an `EVAL_52_SYNCHRONIZED_ACQUISITION_*` or an EVAL-53-named acquisition
   manifest that the gate glob matches; prefer adding a window-B acquisition glob
   `--require-glob "EVAL_53_*ACQUISITION*"` if the tooling emits it.) Must exit `0`.

7. **Append a session-log line** to this file (measured numbers + artifact paths) and leave this handoff
   as the single durable record.

**Definition of done:** step 6 exits `0` with an
`EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_<UTC>` artifact present (verdict `GO CONFIRMED` or
`NO-GO CONFIRMED (PASS)`), plus the acquisition and prereg artifacts. A handoff-only session, a
`--no-write`-only session, a re-run of EVAL-02..51, a full-test-suite discovery loop, or a
`research_state/` enumeration are **all failures**.

## WHY THIS IS THE RIGHT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE)
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined options + orderflow** strategy.
EVAL-46..52 sealed the full charter ladder `NO-GO CONFIRMED (PASS)` including the pure options-side
fusion (EVAL-52: Deribit options surface × options-venue order flow). EVAL-53 is a **fresh,
pre-registered, heavy cross-window replication** on a new synchronized ~24h real Deribit capture to test
temporal stability of the EVAL-52 NO-GO — a falsification that requires new live heavy data (Deribit
option trades are ~24h-capped, so a second independent window is genuinely new evidence), not a re-run of
sealed artifacts. **New timestamped task ID, never a re-run/re-seal of EVAL-02..52.**

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
New synchronized real Deribit capture (window B) for **both BTC and ETH** over the **same** ~24h window
meeting the per-underlying floor (surface ≥100 snapshots / ≥50 instruments / ≥240 5m bars; options-venue
order flow ≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span; legs time-overlapping/common 5m
bars ≥240) → `scripts/eval53_cross_window_replication.py` runs the sealed EVAL-52 protocol on window A
(`data/raw/eval52/`, immutable) and window B independently (3 fusion rules × {60s, 300s} bars × 3
order-flow signals; causal expanding z-score; net-of-cost 5 bps; 1000 paired permutations + 1000
block-bootstrap + CSCV PBO k=4 + BH-FDR + DSR; seed 42) and emits a cross-window meta verdict →
pre-register `EVAL_53_PREREGISTRATION_*` BEFORE verdict → seal `EVAL_53_CROSS_WINDOW_COMBINED_*` (or
BLOCKED only if floor unmet, never as substitute) → pass seal gate. No prior-EVAL re-runs/re-seals, no
`research_state/` enumeration, no full test suite, no handoff-only session.

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
- **2026-11-15T15:26:16Z (handoff refreshed for next agentic session):** task timestamp advanced to
  `INIT-2026-11-15T15:26:16Z-EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION-ACQUIRE-MEASURE-AND-SEAL`
  in both the authoritative task block and the seal-gate command; all bottlenecks verified cleared (env
  green, Deribit endpoints live, no stale processes, clean working tree, check_session_sealed.py gate
  confirmed executable). The next session MUST execute the 7-step EVAL-52 protocol end-to-end — build
  `eval52_acquire_synchronized_options.py` + `eval52_options_surface_orderflow_net_of_cost.py` +
  `test_eval52_options_surface_orderflow_net_of_cost.py`, run synchronized real Deribit capture for BTC+ETH
  over the same ~24h window meeting the per-underlying floor, smoke test with `--no-write`, seal the
  preregistration and combined verdict, and pass the seal gate. No other task is valid.
- **2026-11-15T16:42:09Z–16:50:18Z (EVAL-52 COMPLETED, TASK `INIT-2026-11-15T15:26:16Z-...-EVAL-52-...`):** env verified green (`./scripts/verify_env.sh --check` exit 0; deps bootstrapped via `./scripts/verify_env.sh`). EVAL-52 tooling already present (`scripts/eval52_acquire_synchronized_options.py`, `scripts/eval52_options_surface_orderflow_net_of_cost.py`) — fixed surface bar-grid alignment to 5m-boundary ticks (`(start_ms // 300000)*300000`) so `build_snapshots` matches Deribit candle ticks (initial capture run produced 0 surface snapshots; fixed and re-captured). Added `tests/test_eval52_options_surface_orderflow_net_of_cost.py` (7 passed). `py_compile` ok. Synchronized real Deribit capture (live public, BTC+ETH, ~24h, both legs) `--out-dir data/raw/eval52 --seal` → acquisition sealed `research_state/EVAL_52_SYNCHRONIZED_ACQUISITION_20261115T164732Z.{json,md}`. Floor met: BTC 289 surface snapshots / 102 instruments / 289 5m bars, 4688 option trades / 99 instruments / span 86261.649 s / 288 common 5m bars (perp 1441 1m candles); ETH 289 snapshots / 102 instruments / 289 5m bars, 3122 option trades / 101 instruments / span 86204.278 s / 287 common 5m bars. Smoke `--no-write` floor_ok true. Sealed prereg `EVAL_52_PREREGISTRATION_20261115T165018Z.{json,md}` and verdict `EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_20261115T165018Z.{json,md}` — **NO-GO CONFIRMED (PASS)** (18 configs/underlying; best Sharpe BTC −0.7473 `continuous_zscore::call_minus_put::bar300.0`, ETH −1.6028 `sign_agreement::imbalance::bar300.0`; all configs NO-GO `any_pass=false`; pooled PBO 0.6389; BH-FDR rejected 32 configs). Seal gate `scripts/check_session_sealed.py --task-id INIT-2026-11-15T15:26:16Z-EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION-ACQUIRE-MEASURE-AND-SEAL --glob "EVAL_52_SYNCHRONIZED_ACQUISITION_*" --require-glob "EVAL_52_PREREGISTRATION_*" --require-glob "EVAL_52_OPTIONS_SURFACE_ORDERFLOW_COMBINED_*"` exit 0. EVAL-52 immutable. **Next focus: `INIT-2026-11-15T16:52:00Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION-ACQUIRE-MEASURE-AND-SEAL`** (independent cross-window replication, new ~24h synchronized capture → cross-window meta verdict).
