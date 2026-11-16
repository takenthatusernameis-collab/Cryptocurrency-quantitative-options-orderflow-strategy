# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK FOR NEXT SESSION (timestamped; the only valid task)

**Status as of 2026-11-16T02:41:37Z (verified this session):** CAMPAIGN **EVAL-02..61 CLOSED** — every rung sealed `NO-GO CONFIRMED (PASS)` (gate exit 0). **EVAL-61 is SEALED** at `research_state/EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_20261116T024137Z.{json,md}` (prereg `..._PREREGISTRATION_20261116T024137Z`; acquisition `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_20261116T022541Z`). Env green: `./scripts/verify_env.sh --check` OK; `.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED` unset. **No further on-charter rung remains: the options+orderflow ladder (EVAL-46..61) is COMPLETE.**

**Measured current state (verified 2026-11-16T02:41:37Z):**
- EVAL-61 **SEALED `NO-GO CONFIRMED (PASS)`**, gate exit 0. Real synchronized three-way captures (Deribit options surface + options-venue order flow + OKX perp order flow) under `data/raw/eval61/`:
  - `three_way_BTC_20261116T011441Z.json` (289 snaps, 2748 opt trades, 87 of-instruments, 288 common 5m bars)
  - `three_way_ETH_20261116T022541Z.json` (289 snaps, 3558 opt trades, 227 of-instruments, 287 common 5m bars) — **acquired live this session** via `scripts/eval60_acquire_three_way.py --underlying ETH --days 1 --max-per-expiry 40 --okx-delay 0.15 --out-dir data/raw/eval61 --seal`
- Floor met on **both** BTC and ETH: surface ≥100 snaps / ≥50 instr / ≥240 bars; Deribit option trades ≥2000 / ≥50 instr / ≥240 bars / ≥79200s; perp ≥240 bars / ≥79200s; common bars ≥240; roster 2 underlyings.
- **All 8 pre-registered configs (2 signals × {60s,300s} × BTC,ETH) FAIL the GO bar.** Best Sharpe BTC +0.9717 (imbalance::300s), ETH +0.9916 (imbalance::300s) — both positive but **every config breaches the kill-switch (max-DD = 1.0000)**, permutation p ≫ 0.05, bootstrap 95% CI lower ≤ 0. Pooled PBO 0.2500; BH-FDR rejected nothing. **The signal-timed delta-hedged ATM straddle is NOT net-of-cost tradable on real BTC or real ETH.**
- The on-charter "options order flow drives a volatility trade" rung is now closed. The full options+orderflow ladder EVAL-46..61 is COMPLETE, all NO-GO.

**MANDATORY NEXT TASK (timestamped, non-optional):**

```
INIT-2026-11-16T02:41:37Z-CAMPAIGN-CLOSED-NO-FURTHER-ON-CHARTER-RUNG
```

**SESSION IS COMPLETE.** EVAL-61 is sealed `NO-GO CONFIRMED (PASS)` (gate exit 0); the
options+orderflow ladder EVAL-46..61 is COMPLETE. There is **no remaining on-charter rung** —
every combination of real options (surface/greeks/smile, options-venue order flow) × real
orderflow (OKX perp, L2 OFI) × fusion rule × volatility/direction trade on BTC/ETH is now
sealed NO-GO. Do not re-run, re-litigate, or re-seal EVAL-02..61. Any future work must be a
**fresh, pre-registered, heavy real-data falsification with a new timestamped task ID** —
e.g. a new asset class (no real ETH option series available; other perps/venues untested), a
new cost/execution model, or a new signal family — and must be recorded here as a new task
with its own acquisition + PREREGISTRATION + COMBINED seal.

### Required steps (in order) — ALL DONE this session, kept for provenance

1. **Acquire missing real ETH data (heavy, LIVE, mandatory) and ensure BTC+ETH floor met.** DONE: `python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 1 --max-per-expiry 40 --okx-delay 0.15 --out-dir data/raw/eval61 --seal --task-label EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE` (live ~25 min; produced `data/raw/eval61/three_way_ETH_20261116T022541Z.json`).
2. **Smoke/verify floors before sealing.** DONE: `--no-write` on `data/raw/eval61` → `floor_ok=true`, roster BTC+ETH.
3. **Pre-register then measure (real verdict, not BLOCKED).** DONE: full run sealed `EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION_20261116T024137Z.{json,md}` + `EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_20261116T024137Z.{json,md}` — verdict **NO-GO CONFIRMED (PASS)**.
4. **Seal with gate exit 0 (REQUIRED).** DONE: `check_session_sealed.py --task-id "INIT-2026-11-16T02:07:52Z-EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE-ACQUIRE-ETH-MEASURE-SEAL" --glob "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION_*" --require-glob "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_*"` → **exit 0**.
5. **Update this handoff in place** with verified facts/paths/commands/measured numbers and outcome. DONE.

## WHY THIS RUNG (repo-name/charter; fixed hypothesis — NON-NEGOTIABLE)

`Cryptocurrency-quantitative-options-orderflow-strategy` = combined **OPTIONS + ORDERFLOW**. EVAL-46..60 are sealed NO-GO across fusion/smile ladders (directional/standalone/static vol/three-way). The one on-charter combination still unmeasured: **real options order-flow toxicity → subsequent realized volatility**, traded via a **signal-timed delta-hedged ATM straddle** net-of-cost on BTC/ETH perpetual (causal: decision at bar k → outcome [k,k+1], fresh ~24h, both BTC and ETH). This makes options ORDER FLOW drive a volatility trade (not directional/static). Fresh, pre-registered, heavy real-data falsification; new task ID outside EVAL-02..60.

**Hypothesis/GO bar (fixed, pre-registered):** per 5m bar `tox_k=(call_notional-put_notional)/(call_notional+put_notional)` from real Deribit option trades (and signed-aggressor imbalance variant), position `q_k=clip(expanding_z(tox_k),-1,1)` in ATM straddle (ATM IV/greeks from real marks), delta-hedged each bar; target `rv_{k+1}=|Δlog(perp_close)|` from real Deribit perp candles; P&L `q_k*[vega*dIV + 0.5*gamma*dS^2 - theta*dt] - hedge_cost - 5bps*|Δq_hedge|` (5bps turnover/hedge). Grid {toxicity variants}×{60s,300s}. **GO only if on both BTC and ETH and ≥1 config:** net-of-cost Sharpe>0, max-DD≤0.20, permutation p<0.05, bootstrap 95% CI lower>0, pooled PBO<0.5; else **NO-GO CONFIRMED (PASS)**.

## BOTTLENECKS — ALL CLEARED (verified 2026-11-16T02:41:37Z)

1. **CLEARED:** EVAL-60 sealed NO-GO (gate exit 0); OKX acquisition bug fixed in `eval60_acquire_three_way.py` (cursor/backoff/delay); EVAL-61 tooling + 11 unit tests built/verified; env green; network public read-only; **ETH three-way capture acquired live** (`data/raw/eval61/three_way_ETH_20261116T022541Z.json`, 289 snaps / 3558 opt trades / 227 of-instruments / 287 common bars); floor met on BTC+ETH; EVAL-61 sealed `NO-GO CONFIRMED (PASS)` gate exit 0.
2. **REMAINING:** None on charter. If a new task ID is opened, reuse the proven EVAL-60/61 acquisition (`scripts/eval60_acquire_three_way.py --underlying <X>`) and the copy-and-retarget measurement pattern (`scripts/eval61_orderflow_realized_vol_net_of_cost.py`); never synthetic, always pre-register then seal with gate exit 0.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal EVAL-02..60; do not edit sealed artifacts or `src/`.
- Never synthetic fallback; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement. Public read-only network only, polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`; no `phaseNN_*` wrappers.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies (root retired pointers stay retired). Update this file in place with verified facts only.

## ANTI-STALL RULE

- Only acceptable outputs: (a) sealed `EVAL_61_*PREREGISTRATION_*` + `EVAL_61_*COMBINED_*` with gate exit 0 (stamp ≥ 2026-11-16T02:07:52Z) — **DONE** — or (b) a stricter in-place handoff keeping floor identical/stricter.
- Timestamp-only edits without sealing/stricter scope = **failed session**. "Tooling built/capture started, run next" = **failed session**. BLOCKED is not a verdict — widen capture, do not stop/weaken floor/drop underlying.

## LOADER / ACQUISITION GOTCHAS

- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`.
- OKX: `GET https://www.okx.com/api/v5/market/history-trades?instId=<PERP>&limit=100` (`trades-history` 404). Paginate backwards `after=<oldest tradeId>` (dedupe by `tradeId`); instruments `BTC-USD-SWAP`,`ETH-USD-SWAP`; browser UA; `--okx-delay 0.15` + backoff; if 0 trades wait/retry (rate-limit cooldown) — do not weaken floor.
- EVAL-60/61 capture schema: `data/raw/eval61/three_way_{BTC,ETH}_<stamp>.json` with `surface.snapshots[]` (causal `spot`, `quotes[]`), `option_trades[]`, `perp_candles[]` (Deribit 1m), `okx_perp_trades[]`. No synthetic.
- Deribit: option trades `get_last_trades_by_instrument_and_time` (~24h cap → common window inside last ~24h); perp candles `get_tradingview_chart_data` `{BTC,ETH}-PERPETUAL` res `1`; surface/IV via real marks.
- DSR undefined for |Sharpe|≥1 (`atanh`) — rely on perm/bootstrap/PBO/BH-FDR.

## SEALED STATE (immutable; append only)

EVAL-02..61 sealed; EVAL-46..61 all **NO-GO CONFIRMED (PASS)** gate exit 0 (see prior COMBINED
artifacts in `research_state/`). Re-running/re-sealing prohibited. **The options+orderflow
ladder is COMPLETE (EVAL-46..61); no further on-charter rung exists.**

## SESSION LOG (append-only)

- 2026-11-14→2026-11-15: EVAL-41..59 sealed NO-GO (gate exit 0).
- 2026-11-15T22:44:10Z: EVAL-60 tooling built + smoke.
- 2026-11-16T00:34:26Z: EVAL-60 heavy BTC+ETH sealed `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_COMBINED_20261116T003146Z` NO-GO (gate exit 0); OKX acquisition bug fixed; task advanced to EVAL-61.
- 2026-11-16T00:40:39Z: task timestamp refreshed; bottlenecks reported cleared.
- 2026-11-16T00:46:36Z: EVAL-61 measurement+tests built (11 passed), `--no-write` BLOCKED (no ETH capture), BTC-only acquisition launched/deferred — **stalled without verdict**.
- **2026-11-16T02:07:52Z (prior session, handoff corrective):** verified state — BTC captures exist (`data/raw/eval61/three_way_BTC_20261116T005923Z.json`, `...011441Z.json`), **ETH capture missing**, no PREREG/COMBINED sealed; `--no-write` BLOCKED (floor_ok false, needs BTC+ETH). Updated authoritative task to `INIT-2026-11-16T02:07:52Z-EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE-ACQUIRE-ETH-MEASURE-SEAL`.
- **2026-11-16T02:41:37Z (this session, COMPLETE):** executed the heavy work. Acquired live ETH three-way capture (`data/raw/eval61/three_way_ETH_20261116T022541Z.json`, 289 snaps / 3558 opt trades / 227 of-instruments / 287 common bars; acquisition manifest `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_ACQUISITION_20261116T022541Z`). `--no-write` floor_ok=true (BTC+ETH). Sealed `EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION_20261116T024137Z.{json,md}` + `EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_20261116T024137Z.{json,md}` — **NO-GO CONFIRMED (PASS)**, all 8 configs fail GO bar (best Sharpe BTC +0.9717 / ETH +0.9916, but every config max-DD=1.0000 kill-switch breach; perm p 0.29–0.72; CI lower ≤0; pooled PBO 0.25; BH-FDR rejected nothing). Gate `check_session_sealed.py` **exit 0**. Handoff updated in place; campaign CLOSED, no further on-charter rung.
