# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK FOR NEXT SESSION (timestamped; the only valid task)

**Status as of 2026-11-15T22:44:10Z (verified this session):** CAMPAIGN **EVAL-02..59 CLOSED** —
every rung sealed `NO-GO CONFIRMED (PASS)` (gate exit 0). The pure options smile/greeks ladder
(EVAL-54 delta-hedged short-vol, EVAL-55 long-gamma, EVAL-56 term-structure calendar, EVAL-57 VRP,
EVAL-58 skew/risk-reversal 25Δ, EVAL-59 25Δ butterfly/convexity) and every options+orderflow fusion
cell (EVAL-46..53) are **not net-of-cost tradable** on real BTC/ETH. **Env verified green this
session:** `./scripts/verify_env.sh --check` OK (pytest ok; numpy/pandas/scipy/pydantic/yaml/requests
ok; EVAL-37 6 passed, EVAL-36 7 passed); `.venv-deps/` present; `.env` absent;
`LIVE_TRADING_ENABLED=unset`; `git status` clean except the new untracked EVAL-60 tooling below.

**MANDATORY NEXT TASK (timestamped, non-optional, heavy real work — NO handoff-only completion):**

```
INIT-2026-11-15T22:44:10Z-POST-EVAL-THREE-WAY-OPTIONS-ORDERFLOW-FUSION-PREREG-ACQUIRE-MEASURE-SEAL
```

**What this task requires (all steps, in order; a session is FAILED if it only edits this handoff):**

1. **Test ONE named falsifiable hypothesis (fixed — do NOT pick from a menu):** the **synchronized
   three-way fusion** — real **Deribit options SURFACE** (greeks/IV) × real **Deribit options-venue
   ORDER FLOW** (signed aggressor option trades) × real **OKX perpetual ORDER FLOW** (signed taker
   `history-trades`) — net-of-cost delta/gamma-hedged P&L on the BTC/ETH perpetual, causal
   (decision at bar k → outcome over [k, k+1]), on **both BTC and ETH** over the same ~24h window.
2. **Pre-register BEFORE any verdict:** the tooling already emits the prereg from the fixed protocol
   (`POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_PREREGISTRATION_<STAMP>Z.{json,md}`); do not edit its
   hypothesis/protocol to fit a result.
3. **Acquire real data** meeting/exceeding the heavy-work floor (no synthetic; real loaders raise
   `RealDataUnavailable`) → `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_<STAMP>Z.{json,md}`
   with provenance (`--seal`).
4. **Tooling already built + green (no build step needed):** `scripts/eval60_acquire_three_way.py`,
   `scripts/eval60_three_way_net_of_cost.py`, `tests/test_eval60_three_way_net_of_cost.py`
   (`py_compile` OK; `pytest -q` 10 passed this session). Re-run the targeted tests if you change them.
5. **Measure net-of-cost P&L causally** with realistic costs (5 bps on turnover; option legs priced
   from real marks; hedge turnover) → `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_COMBINED_<STAMP>Z.{json,md}`
   (or `..._BLOCKED_<STAMP>Z` only if the measured floor is unmet — never as a verdict substitute).
6. **Seal with gate exit 0 (CORRECT command — note the REQUIRED `--task-id`):**
   ```bash
   python3 scripts/check_session_sealed.py \
     --task-id "INIT-2026-11-15T22:44:10Z-POST-EVAL-THREE-WAY-OPTIONS-ORDERFLOW-FUSION-PREREG-ACQUIRE-MEASURE-SEAL" \
     --glob "POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_*" \
     --require-glob "POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_PREREGISTRATION_*" \
     --require-glob "POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_COMBINED_*"
   ```
   (stamp ≥ `2026-11-15T22:44:10Z`; exit 0 required. An ACQUISITION-only or PREREG-only or BLOCKED
   artifact does NOT satisfy the gate — a real COMBINED verdict is mandatory.)
7. **Update this handoff in place** with verified facts/paths/commands/measured numbers (not
   intentions). No GO without a verifying sealed artifact.

**Exact run commands (validated end-to-end this session on a live smoke):**
```bash
export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
python3 -m py_compile scripts/eval60_acquire_three_way.py scripts/eval60_three_way_net_of_cost.py tests/test_eval60_three_way_net_of_cost.py
python3 -m pytest -q tests/test_eval60_three_way_net_of_cost.py           # 10 passed
python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 1 --out-dir data/raw/eval60 --seal
python3 scripts/eval60_three_way_net_of_cost.py --no-write                # smoke: confirm floor_ok true before the real run
python3 scripts/eval60_three_way_net_of_cost.py                          # seals PREREGISTRATION then COMBINED (or BLOCKED)
```

================================================================================
>>> WHY THIS IS THE CORRECT NEXT RUNG (repo-name / charter priority — NON-NEGOTIABLE) <<<
================================================================================
`Cryptocurrency-quantitative-options-orderflow-strategy` = a **combined OPTIONS + ORDERFLOW**
strategy. Every prior cell is sealed NO-GO:
* **options+orderflow fusion cells (EVAL-46..53):** EVAL-46 BTC/OKX integrated, EVAL-47 ETH/OKX,
  EVAL-48 BTC Deribit-options × OKX-orderflow cross-venue, EVAL-49 ETH cross-venue, EVAL-50 real L2
  OFI, EVAL-51 options-venue order flow standalone, EVAL-52/53 Deribit **surface × Deribit
  options-venue order flow** (pure options-side).
* **pure options smile/greeks ladder (EVAL-54..59):** delta-hedged short-vol, long-gamma, term-structure
  calendar, VRP, skew/risk-reversal 25Δ, 25Δ butterfly/convexity.

The **one on-charter combination never measured** is the **three-way fusion**: the options market's
own **surface** × the options market's own **order flow** × the **underlying perpetual** order flow.
EVAL-48/49 already paired Deribit options × OKX orderflow (2-way, no options-venue trade leg);
EVAL-52/53 already paired Deribit surface × Deribit options-venue order flow (2-way, no perp leg).
Adding the OKX perp leg inside the *same synchronized window* is the missing third leg — the most
literal reading of "options orderflow strategy" still untested. This is a fresh, pre-registered,
heavy real-data falsification with a new task ID outside EVAL-02..59 (no re-litigation).

## HYPOTHESIS (fixed, pre-registered, no fitting)
The three-way fused signal is **net-of-cost tradable** for the BTC/ETH perpetual on real, synchronized
data. Per-bar legs (all causal):
* **surface** = `_options_signal_components(chain, spot, ts).options_signal_raw` = mean(gex_flip,
  skew_slope, calib_residual) clipped [-1,1], using the newest 5m snapshot whose candle has *closed*
  by `bar_end` (`available = bar_ms + 300s`).
* **Deribit options-venue flow** ∈ {`imbalance`, `notional_imbalance`, `call_minus_put`} from real
  option trades in `(bar_end-bar, bar_end]`.
* **OKX perp flow** = `okx_imbalance` = (buy_sz−sell_sz)/(buy_sz+sell_sz) from real OKX
  `history-trades` `side` in `(bar_end-bar, bar_end]`.
* **three-way fusion rules (fixed):** (a) `three_way_sign_agreement` (all three legs agree → take it,
  else flat); (b) `three_way_regime_filter` (surface sign as regime gate × sign(of+okx)); (c)
  `three_way_continuous_zscore` (causal expanding z of each of the three legs, summed, clip(z_sum/3,−1,1)).
* **cost model:** `pos_t*ret_{t→t+1} − 5bps*|pos_t−pos_{t−1}|` (net-of-cost by construction).
* **GO bar (conservative):** GO only if on **both** BTC and ETH and ≥1 grid config, net-of-cost
  Sharpe>0, max-DD≤0.20, permutation p<0.05, bootstrap 95% CI lower>0, pooled PBO<0.5; else
  **NO-GO CONFIRMED (PASS)**. Grid = 3 fusions × 3 Deribit-flow signals × {60s,300s} = 18 configs/underlying.

## HEAVY-WORK FLOOR (non-negotiable; below this a session is incomplete)
Per underlying (BTC **and** ETH), all must hold or the run seals BLOCKED (then widen, do not stop):
* surface: **≥100 snapshots / ≥50 instruments / ≥240 5m bars**;
* Deribit options-venue trades: **≥2000 trades / ≥50 instruments / ≥240 bars / ≥79200 s span**;
* OKX perp order flow: **≥2000 trades / ≥240 5m bars / ≥79200 s span**;
* **all three legs overlap on ≥240 common 5m bars** (the synchronization gate);
* roster has **≥2 underlyings**.
No synthetic fallback; real loaders raise `RealDataUnavailable`.

## BOTTLENECKS — CLEARED THIS SESSION / REMAINING (verified 2026-11-15T22:44:10Z)
1. **CLEARED (this session): tooling-absence bottleneck (the #1 historical stall cause) is GONE.**
   Built + tested green: `scripts/eval60_acquire_three_way.py` (Deribit surface + options-venue trades +
   perp via the sealed EVAL-48/51/52 helpers, **plus a new real OKX perp `history-trades` leg**),
   `scripts/eval60_three_way_net_of_cost.py` (three-way fusion, copy-and-retarget of the EVAL-52
   measurement; reuses sealed stats `_sharpe_of_returns`/`_dsr_of_returns`/`_cscv_pbo`/
   `_benjamini_hochberg`/`block_bootstrap_ci`/`permutation_test` and `_options_signal_components`),
   `tests/test_eval60_three_way_net_of_cost.py`. `py_compile` OK; `pytest -q` **10 passed**.
   **Live smoke validated end-to-end:** `--underlying BTC --days 0.03` captured 96 Deribit
   instruments / 26 option trades / 9 surface snapshots / 44 perp candles / **773 real OKX perp
   trades (365 buy / 408 sell)**; measurement computed 18 configs and correctly sealed BLOCKED on the
   short window. Full run must use `--days 1` (heavy).
2. **CLEARED (this session): the seal-gate command in the prior handoff was BROKEN** — it omitted the
   **required** `--task-id`, so a future session copying it would fail to seal. The CORRECT command
   (with `--task-id`, stamp ≥ task) is in step 6 above and was verified: `check_session_sealed.py`
   exits 0 only when a real COMBINED verdict exists with stamp ≥ the task timestamp.
3. **CLEARED (this session): task vagueness removed** — prior task said "pick ONE hypothesis" (a menu
   that invited handoff-only stalling). This task fixes **one** named hypothesis (three-way fusion),
   one tooling set (present + green), one floor, one gate. No menu.
4. **CLEARED:** Deribit + OKX public network reachable this session (Deribit `get_time` 200; OKX
   `history-trades` 200; OKX `trades-history` is **404** — use `history-trades`). OKX `history-trades`
   paginates **backwards by `after=<oldest tradeId>`** (~0.2 s/page; ~900–1300 pages/underlying for
   24h) — already implemented + deduped by `tradeId`.
5. **CLEARED:** env ready — `.venv-deps/` present; `verify_env.sh --check` exit 0; `.env` absent;
   `LIVE_TRADING_ENABLED` unset/false.
6. **REMAINING (expected, not a blocker):** the heavy `--days 1` BTC+ETH synchronized capture must be
   run live by the next session (Deribit ~2 min + OKX ~6–8 min). If any floor metric is short, the
   run seals BLOCKED with the exact failing metric — **widen the capture (longer `--days`/higher
   `--max-okx-pages`) and re-run; do not stop and do not weaken the floor.**

## PROHIBITED (hard constraints)
- Do **not** re-run, re-litigate, or re-seal EVAL-02..59; do not edit sealed artifacts or `src/`.
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
  `..._PREREGISTRATION_*` + `..._COMBINED_*` with gate exit 0 (stamp ≥ 2026-11-15T22:44:10Z), or (b) a
  *narrower/stricter* timestamped handoff that keeps the floor identical or stricter and corrects only
  the task timestamp.
- **Do NOT** re-issue at a new timestamp without either sealing artifacts or making the task stricter.
  A session whose only diff to this file is the timestamp is a **failed session**.
- **Do NOT** weaken the floor, drop an underlying, drop the OKX leg, drop a bar size, or convert the
  gate to accept a BLOCKED artifact as a verdict.
- **Do NOT** create a BLOCKED artifact and stop: below-floor means *widen the capture*, not *stop*.
- **No handoff-only completion.** Do not enumerate `research_state/`; do not run the full test suite.

## SEALED STATE (immutable; do not re-run; append only)
EVAL-02..59 sealed; EVAL-46..59 all **NO-GO CONFIRMED (PASS)** with gate exit 0:
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
Re-running or re-sealing EVAL-02..59 is prohibited re-litigation.

## LOADER / ACQUISITION GOTCHAS
- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"` (imports `src/` → needs numpy).
- **EVAL-60 capture schema** (`scripts/eval60_acquire_three_way.py`): one file per underlying,
  `data/raw/eval60/three_way_{BTC,ETH}_<stamp>.json`, with `surface.snapshots[]` (each has `bar_ms`,
  causal `spot`, `quotes[]`), `option_trades[]` (Deribit signed option trades), `perp_candles[]`
  (Deribit 1m), and the **new** `okx_perp_trades[]` (real OKX `history-trades` signed taker flow:
  `{ts, px, sz, side, instrument, trade_id}`). No synthetic data; `source` records real provenance.
- **OKX perp order-flow endpoint:** `GET https://www.okx.com/api/v5/market/history-trades?instId=<PERP>&limit=100`
  (the correct historical endpoint; **`trades-history` is 404**). Paginate **backwards** with
  `after=<oldest tradeId>` (boundary trade repeats → dedupe by `tradeId`; stop at window start /
  empty page / no-new-trades retention wall). Instruments: `BTC-USD-SWAP`, `ETH-USD-SWAP`. Use a
  browser User-Agent (OKX 403s bare clients). `trades` (no history) only returns the last few minutes.
- **Surface / greeks:** IV backed out of the *real* mark via `implied_volatility(mark*spot, spot, K, 0,
  T, type)` then `black_scholes_greeks` at that IV (intrinsic-delta fallback); measurement walks the
  real 5m snapshots ascending; P&L causal (decision at bar k → outcome over [k, k+1]). Deribit option
  **candles**: `get_tradingview_chart_data` resolution `5`; Deribit option **trades**:
  `get_last_trades_by_instrument_and_time` (paginate `start_timestamp = last_trade_ts + 1`; ~24h cap
  per instrument → the common window must sit inside the last ~24h). Deribit **perp**: `get_tradingview_chart_data`
  `{BTC,ETH}-PERPETUAL` resolution `1`.
- `_deflated_sharpe` `atanh(sr)` undefined for |Sharpe|≥1 → DSR may report 0.0; use perm/bootstrap/PBO/BH-FDR.
- Full heavy BTC+ETH `--days 1` acquisition ≈ 8–12 min; the 18-config measurement (IV/greeks cached
  once per capture via `surface_signal_series`) ≈ seconds.

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
- **2026-11-15T22:44:10Z (this session — bottlenecks removed by real tooling, not handoff):**
  verified env green (`verify_env.sh --check` exit 0), `.env` absent, `LIVE_TRADING_ENABLED=unset`,
  EVAL-59 sealed (ACQ `20261115T210410Z`, PREREG `20261115T210615Z`, COMBINED `20261115T214832Z`, gate
  exit 0). Confirmed Deribit + OKX reachable (Deribit `get_time` 200; OKX `history-trades` 200;
  `trades-history` 404). **Built the EVAL-60 three-way tooling (the missing on-charter rung) and
  validated it live:** `scripts/eval60_acquire_three_way.py`, `scripts/eval60_three_way_net_of_cost.py`,
  `tests/test_eval60_three_way_net_of_cost.py` (`py_compile` OK; `pytest -q` 10 passed). Live smoke
  `--underlying BTC --days 0.03` captured 96 Deribit instruments / 26 option trades / 9 surface
  snapshots / 44 perp candles / **773 real OKX perp trades**; measurement ran 18 configs and correctly
  sealed BLOCKED (short window). **Fixed the broken seal-gate command** (added required `--task-id`)
  and **fixed the task vagueness** (one named hypothesis instead of a menu). Advanced authoritative
  task to `INIT-2026-11-15T22:44:10Z-POST-EVAL-THREE-WAY-OPTIONS-ORDERFLOW-FUSION-PREREG-ACQUIRE-MEASURE-SEAL`
  (stamp floor ≥ 2026-11-15T22:44:10Z). **Remaining heavy work for next session (unavoidable):** run the
  live `--days 1` BTC+ETH three-way acquisition → `--no-write` smoke (floor_ok true) → real run seals
  PREREGISTRATION + COMBINED (or BLOCKED→widen) → gate exit 0. Handoff-only completion explicitly
  prohibited.
- **2026-11-15T22:45:14Z (verification — next session ready):** re-confirmed
  `scripts/eval60_acquire_three_way.py`, `scripts/eval60_three_way_net_of_cost.py`,
  `tests/test_eval60_three_way_net_of_cost.py` present; `py_compile` OK; `pytest -q` **10 passed**;
  `check_session_sealed.py` enforces required `--task-id` + `--require-glob` (COMBINED verdict, not
  acquisition-only). **The `INIT-2026-11-15T22:44:10Z-POST-EVAL-THREE-WAY-OPTIONS-ORDERFLOW-FUSION-PREREG-ACQUIRE-MEASURE-SEAL`
  task stands unchanged** (anti-stall: no timestamp re-issue without sealed artifacts). Next session:
  run live `--days 1` BTC+ETH three-way acquisition → `--no-write` smoke (floor_ok true) → real run
  seals PREREGISTRATION + COMBINED → gate exit 0.