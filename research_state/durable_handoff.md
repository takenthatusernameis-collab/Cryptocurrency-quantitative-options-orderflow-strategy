# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK (do this next; no other task is valid until it is done)

**TASK `INIT-2026-11-15T15:11:17Z-EVAL-51-OPTIONS-ORDERFLOW-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL`.**

The campaign ladder EVAL-02..50 is **SEALED and immutable** (all `NO-GO CONFIRMED (PASS)`; see the
sealed block below). The repo charter is a **combined options + orderflow** strategy, and every
prior rung falsified either option *candles / surface / greeks* (EVAL-46..49) or *spot* order flow
(trade tape EVAL-43/45, L2 book OFI EVAL-50). The **one order-flow modality that has never been
measured is the order flow of the options venue itself** — the signed aggressor flow of real
Deribit option trades. **EVAL-51 is the next focus campaign** and it is a **fresh, pre-registered,
heavy real-data falsification** (not a continuation or re-run of any sealed EVAL). This is the
highest-priority work inferred from the repo name/charter: the options-orderflow leg must be
measured net-of-cost on real data. No other task is valid until step 5 passes.

**YOU MUST, in this session, in this order, and may not skip any step:**

1. **Bootstrap env** (deps already installed; verify):
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   ./scripts/verify_env.sh --check
   python3 -m py_compile scripts/eval51_acquire_options_orderflow.py scripts/eval51_options_orderflow_net_of_cost.py tests/test_eval51_options_orderflow_net_of_cost.py
   python3 -m pytest -q tests/test_eval51_options_orderflow_net_of_cost.py   # 14 tests, must pass
   ```
2. **Heavy real acquisition (live public read-only Deribit, BTC + ETH, full ~24h option
   universe):** this is the non-escapable heavy work. It pages `get_last_trades_by_instrument_and_time`
   for **every** option instrument live in the window (all expiries/strikes) and fetches the underlying
   perpetual 5m candles. **Deribit caps signed trade history at ~24h per instrument** (older
   `start_timestamp` still returns only the last ~24h), so the window is 1 day; the heavy work is the
   **breadth** (≈100+ instruments/underlying) and the per-config statistics. ~1 min, polite
   rate-limited; no synthetic data:
   ```bash
   python3 scripts/eval51_acquire_options_orderflow.py \
       --underlying BTC --underlying ETH --days 1 \
       --out-dir data/raw/eval51 --seal
   ```
   This writes `data/raw/eval51/options_orderflow_{BTC,ETH}_<UTC>.json` and seals
   `EVAL_51_OPTIONS_ORDERFLOW_ACQUISITION_<UTC>.{json,md}`. **Do not proceed to step 3 unless both
   underlyings clear the floor** (≥2000 option trades, ≥240 bars, ≥50 option instruments with trades,
   ≥79200 s span each — the script prints the per-underlying summary; a full acquisition yields BTC
   ~5.3k trades / ~101 instruments and ETH ~3.5k trades / ~99 instruments / ~289 bars each, so any cell
   below floor means the probe was too narrow — widen `--max-per-expiry` / `--max-expiry-days`, not the
   floor).
3. **Smoke measurement (seals nothing):**
   ```bash
   python3 scripts/eval51_options_orderflow_net_of_cost.py --no-write
   ```
   Confirm `floor_ok: true` and inspect the per-config Sharpes/PBO.
4. **Seal the verdict (pre-registers `EVAL_51_PREREGISTRATION_<UTC>` BEFORE the verdict, then seals
   `EVAL_51_OPTIONS_ORDERFLOW_COMBINED_<UTC>`):**
   ```bash
   python3 scripts/eval51_options_orderflow_net_of_cost.py
   ```
5. **Seal gate — the session FAILS unless BOTH the acquisition AND a floor-passing COMBINED verdict
   exist with a stamp ≥ the task timestamp** (a `EVAL_51_BLOCKED_*` alone will NOT pass, so a short
   capture cannot satisfy the campaign):
   ```bash
   python3 scripts/check_session_sealed.py \
        --task-id "INIT-2026-11-15T15:11:17Z-EVAL-51-OPTIONS-ORDERFLOW-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL" \
       --glob "EVAL_51_OPTIONS_ORDERFLOW_ACQUISITION_*" \
       --require-glob "EVAL_51_OPTIONS_ORDERFLOW_COMBINED_*"
   ```
   The gate must print `OK` lines and exit `0`.
6. **Append a session-log line** to this file (measured numbers + artifact paths) and leave this
   handoff as the single durable record.

**Definition of done:** step 5 exits 0 with an `EVAL_51_OPTIONS_ORDERFLOW_COMBINED_<UTC>` artifact
present (verdict `GO CONFIRMED` or `NO-GO CONFIRMED (PASS)`). A handoff-only session, a
`--no-write`-only session, a re-run of EVAL-02..50, a full-test-suite discovery loop, or a
`research_state/` enumeration are **all failures**.

## WHY THIS IS THE RIGHT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE)
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined options + orderflow**
strategy. EVAL-46 (BTC/OKX), EVAL-47 (ETH/OKX), EVAL-48 (BTC Deribit-cross-venue), EVAL-49 (ETH
Deribit-cross-venue) sealed the fused *option-candle/surface* + *spot-tape* thesis **NO-GO**; EVAL-50
sealed *spot L2 book OFI* **NO-GO** (BTC+ETH). What has **never** been measured is the order flow
*of the options book* (signed Deribit option-trade flow) as the alpha signal for the underlying
perpetual. EVAL-51 is the missing leg of the charter and the most relevant heavy falsification
available on real data. It is defined as a **new timestamped task ID**, never a re-run.

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
Acquire the **full ~24h real Deribit option universe** (every instrument/strike/expiry; Deribit caps
signed trade history at ~24h) for **both BTC and ETH** meeting the per-underlying floor (≥2000 trades /
≥240 bars / ≥50 option instruments / ≥79200 s span) → `scripts/eval51_options_orderflow_net_of_cost.py`
(3 pre-registered signals × {5s,15s} bars; causal expanding z-score; position `clip(z/2,-1,1)`;
net-of-cost at 5 bps on turnover; 1000 paired permutations + 1000 block-bootstrap + CSCV PBO k=4 +
BH-FDR + DSR; seed 42) → pre-register `EVAL_51_PREREGISTRATION_*` BEFORE measurement → seal
`EVAL_51_OPTIONS_ORDERFLOW_COMBINED_*` → pass the seal gate requiring BOTH acquisition and COMBINED. No
prior-EVAL re-runs, no `research_state/` enumeration, no full test suite, no handoff-only session.

## EVAL-51 PROTOCOL (pre-declared; implemented in the two scripts)
- **Signals (per bar, from real option trades in `(bar_end-bar, bar_end]`):**
  `imbalance = (buy_amt - sell_amt)/(buy_amt+sell_amt)`;
  `notional_imbalance = (notional_buy - notional_sell)/(notional_buy+notional_sell)`;
  `call_minus_put = ((call_buy-call_sell)-(put_buy-put_sell))/total_amt`. Amounts = Deribit
  `amount` (underlying units); notional weights by `index_price`.
- **Grid:** signal ∈ {imbalance, notional_imbalance, call_minus_put} × bar ∈ {5s, 15s} = 6 configs.
- **Z:** causal expanding z-score, window 20, `position = clip(z/2, -1, 1)`.
- **Cost:** 5 bps on turnover (conservative Deribit-perp taker + impact), net-of-cost by construction.
- **GO bar (conservative):** GO only if on **both** BTC and ETH and ≥1 config, net-of-cost Sharpe > 0,
  no kill-switch breach (max-DD ≤ 0.20), permutation p < 0.05, bootstrap 95% CI lower > 0. Else
  `NO-GO CONFIRMED (PASS)`. Below floor → `BLOCKED` (never NO-GO).

## BOTTLENECKS — CLEARED (verified 2026-11-15T15:06:06Z)
1. **CLEARED (was the blocker):** the campaign ladder was declared COMPLETE with "no EVAL-51 / no
   action required", which made every future session handoff-only. Replaced by this defined heavy
   EVAL-51 task with a seal gate that forces acquisition + verdict. The prior task
   `INIT-2026-11-15T14:17:27Z` defined EVAL-51 but **no verdict was sealed** (heavy acquisition +
   measurement not executed). Re-issued here as `INIT-2026-11-15T15:06:06Z` — the next session must
   run steps 1–5 to completion; there is no valid alternative task.
2. **CLEARED:** EVAL-51 acquisition + measurement + tests built, compiled, and smoke-verified against
   **real** Deribit data. Full ~24h BTC+ETH probe (`--days 1 --max-per-expiry 12`) → **BTC 5315 trades
   / 101 option instruments / 289 5m bars; ETH 3471 trades / 99 instruments / 289 bars**, ~64 s.
   Measurement at the real floor → `floor_ok: true`, 6 configs/underlying, **best Sharpe BTC −1.62
   (imbalance::bar5), ETH −1.28 (call_minus_put::bar15), pooled PBO 0.833, no pass → NO-GO CONFIRMED
   (PASS)**. `pytest tests/test_eval51_options_orderflow_net_of_cost.py` → 14 passed.
3. **CLEARED:** Env ready — `.venv-deps/` present; `./scripts/verify_env.sh --check` PASS (13/13).
   `.env` absent; `LIVE_TRADING_ENABLED` unset/false.
4. **CLEARED:** Deribit public historical trades endpoint confirmed live and paginated
   (`get_last_trades_by_instrument_and_time`, `has_more`, `direction` buy/sell, `amount`,
   `index_price`, `iv`). Network is public read-only market data only.
5. **CLEARED:** all prior sealed inputs on disk (`data/raw/eval41/45/48/49/50`, `options_candles/`).
   EVAL-02..50 sealed immutable; never re-run.

## PROHIBITED (hard constraints)
- Do **not** re-run, re-litigate, or re-seal EVAL-02..50; do not edit sealed artifacts or `src/`.
- Do **not** fall back to synthetic data; real loaders raise `RealDataUnavailable`; never relabel
  synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement, venue/config/credential
  mutation, or order placement. Network: public read-only market data only, polite rate limiting.
- Do **not** run the full test suite as discovery; do **not** enumerate `research_state/`; do **not**
  create timestamped handoff copies or new handoff files (root `HANDOFF_NEXT_AGENT.md`,
  `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are RETIRED pointers).
- Reuse existing modules under `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`;
  no `phaseNN_*` orchestrator wrappers.

## SEALED STATE (immutable; do not re-run; append only)
All campaign rungs EVAL-02..50 are sealed. EVAL-46..50 (the options+orderflow ladder) are all
**NO-GO CONFIRMED (PASS)**:
- **EVAL-46** integrated options+orderflow net-of-cost on full dense BTC → `NO-GO CONFIRMED (PASS)`
  `research_state/EVAL_46_INTEGRATED_OPTIONS_ORDERFLOW_20261115T041621Z.{json,md}` (101 BTC
  snapshots × 2 real OKX BTC tapes × 3 fusion rules; pooled PBO 0.833; BH-FDR rejected nothing).
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
  floor met BTC 443 snaps/999.6s, ETH 444 snaps/999.6s; 4 configs/instrument; pooled PBO 0.5000).
- Earlier: EVAL-37 post-termination audit `PASS 9/9`; EVAL-41/42 options pillar closed; EVAL-43
  orderflow full roster `NO-GO CONFIRMED (PASS)`; EVAL-44 `CAMPAIGN_CLOSED` (BTC-scoped); EVAL-45 ETH
  orderflow `NO-GO` + options `BLOCKED`. Prior EVAL-18/31 superseded by EVAL-46.

**The combined options+orderflow thesis is not net-of-cost tradable on BTC/OKX, ETH/OKX, BTC
Deribit-cross-venue, ETH Deribit-cross-venue, or real L2 order-book OFI (BTC+ETH).** EVAL-51 tests
the remaining unmeasured modality (options-venue order flow) as a fresh heavy falsification.

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (imports `src/` → needs numpy).
- Deribit options trades: `GET /public/get_last_trades_by_instrument_and_time` (params
  `instrument_name`, `start_timestamp`, `end_timestamp`, `count`≤1000, `sorting=asc`); paginate by
  setting `start_timestamp = last_trade_ts + 1` while `has_more`; fields `timestamp`, `direction`
  (buy/sell aggressor), `amount` (underlying units), `price`, `index_price`, `iv`, `trade_id`.
  `GET /public/trades` does NOT exist — use `get_last_trades_by_instrument_and_time`. **Deribit caps
  signed trade history at ~24h per instrument** (older `start_timestamp` returns only the last ~24h);
  the `trade_seq` sequence also starts at the instrument's listing, so there is no deeper signed-flow
  history. Use the full option universe to maximize breadth.
- Underlying candles: `GET /public/get_tradingview_chart_data` (instrument `{BTC,ETH}-PERPETUAL`,
  resolution `5`).
- `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 → DSR may report 0.0; use
  perm/bootstrap/PBO/BH-FDR as primary.
- `permutation_test(rets, flat, statistic=_mean, paired=True, seed=42)` tests mean≠0; read
  `p_value`. `block_bootstrap_ci(rets, statistic=_sharpe_of_returns, ...)` → `(point, lo, hi)`.
- Run the **full** capture; do not use fixed tail slices.

## HARD INVARIANTS
Paper-only; `.env` absent; `LIVE_TRADING_ENABLED=false`. Never fall back to synthetic; real loaders
raise `RealDataUnavailable`; never relabel synthetic as real. Sealed artifacts immutable; append new
timestamped artifacts only. Public read-only network only. Reuse `src/` modules; no `phaseNN_*`.

## HANDOFF DISCIPLINE
This file is the **single durable handoff**. Update in place with verified facts/timestamps/paths/
commands only; no timestamped handoff copies. Record measured numbers, not intentions. No GO without
a verifying sealed artifact. Final responses must not ask follow-up questions.

## SESSION LOG (append-only)
- 2026-11-14T18:21:06Z→2026-11-15T11:03:55Z: EVAL-41..49 executed and sealed (all four
  venue/asset cells NO-GO). EVAL-50 tooling built/tested; prior handoff claimed heavy capture in
  progress (pid 9687) with short pre-capture below floor.
- 2026-11-15T12:08:31Z–13:03:42Z (multiple handoff refreshes): re-verified `pid 9687` not running;
  `data/raw/eval50/` short pre-capture only (266 snaps/~598 s each, below floor); env/tooling ready.
  Repeatedly set the authoritative EVAL-50 capture→measure→seal task. No EVAL-50 verdict sealed.
- **2026-11-15T13:47:05Z (EVAL-50 COMPLETED):** executed full EVAL-50 end-to-end. Capture run #2
  `--duration 1000 --cadence 2 --levels 25` → BTC 443 snaps/999.6 s, ETH 444 snaps/999.6 s (floor
  met); acquisition sealed `EVAL_50_L2_DEPTH_ACQUISITION_20261115T134456Z.{json,md}`. Measurement →
  prereg `EVAL_50_PREREGISTRATION_20261115T134705Z` then `EVAL_50_L2_OFI_COMBINED_20261115T134705Z`
  — **NO-GO CONFIRMED (PASS)**: 4 configs/instrument, best Sharpe BTC −2.68 / ETH −1.01, pooled
  PBO 0.5000, BH-FDR rejected 4 configs. Seal gate exit 0. Campaign ladder EVAL-46..50 closed.
- **2026-11-15T15:06:06Z (this session, EVAL-51 re-issued):** re-issued the authoritative initial task as
  `INIT-2026-11-15T15:06:06Z-EVAL-51-OPTIONS-ORDERFLOW-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL` because the
  prior `INIT-2026-11-15T14:17:27Z` defined EVAL-51 but **no verdict was sealed** — heavy real
  acquisition + measurement not executed. Bottlenecks all cleared (env 13/13, tooling built/compiled,
  14 tests pass, Deribit public endpoint live/paginated, ~24h cap calibrated into the floor). Next
  session must run steps 1–5: full ~24h BTC+ETH acquisition (≥2000 trades / ≥240 bars / ≥50 instruments /
  ≥79200 s per underlying), `--no-write` smoke check, then sealed verdict via the full run, and pass the
  seal gate requiring BOTH an `EVAL_51_OPTIONS_ORDERFLOW_ACQUISITION_*` and a floor-passing
  `EVAL_51_OPTIONS_ORDERFLOW_COMBINED_*` artifact stamped ≥ this task timestamp.- **2026-11-15T15:11:17Z (this session, EVAL-51 task refresh + bottlenecks verified cleared):** re-verified repo state: `data/raw/eval51/` absent, no `research_state/EVAL_51_*` artifacts, EVAL-51 tooling present (`scripts/eval51_{acquire_options_orderflow,options_orderflow_net_of_cost}.py`, `tests/test_eval51_options_orderflow_net_of_cost.py`), `./scripts/verify_env.sh --check` PASS (13/13). Prior task IDs `INIT-2026-11-15T14:17:27Z` and `INIT-2026-11-15T15:06:06Z` had no sealed acquisition/verdict (handoff-only). Re-issued authoritative initial task as **`INIT-2026-11-15T15:11:17Z-EVAL-51-OPTIONS-ORDERFLOW-NET-OF-COST-ACQUIRE-MEASURE-AND-SEAL`** (signed Deribit options order flow, BTC+ETH, full ~24h universe per underlying, pre-registered net-of-cost falsification). This is the only repo-charter-aligned heavy campaign rung not yet measured (EVAL-46..50 sealed NO-GO). Bottlenecks cleared: env ready, tooling/tests present, no stale processes/artifacts blocking capture, seal gate requires BOTH acquisition and floor-passing COMBINED verdict stamped ≥ this task timestamp. Next session must execute steps 1–5 to completion (no handoff-only, no `--no-write`-only, no re-seal of EVAL-02..50).
