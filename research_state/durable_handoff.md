# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK FOR NEXT SESSION (timestamped; the only valid task)

**Status as of 2026-11-16T02:07:52Z (verified this session):** CAMPAIGN **EVAL-02..60 CLOSED** — every rung sealed `NO-GO CONFIRMED (PASS)` (gate exit 0). **EVAL-61 is NOT sealed.** Env green: `./scripts/verify_env.sh --check` OK; `.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED` unset.

**Measured current state (verified):**
- EVAL-61 tooling/tests exist and pass: `scripts/eval61_orderflow_realized_vol_net_of_cost.py`, `tests/test_eval61_orderflow_realized_vol_net_of_cost.py` (11 passed earlier), acquisition reuse `scripts/eval60_acquire_three_way.py`.
- Real captures present: `data/raw/eval61/three_way_BTC_20261116T005923Z.json` (289 snaps, 6872 opt trades, 337531 OKX, 1441 perp) and `data/raw/eval61/three_way_BTC_20261116T011441Z.json` (289 snaps, 2748 opt trades, 319777 OKX, 1441 perp). **ETH capture is MISSING** (no `three_way_ETH_*` in `data/raw/eval61/`).
- No EVAL-61 sealed artifacts: no `EVAL_61_*PREREGISTRATION*`, no `EVAL_61_*COMBINED*` in `research_state/`.
- `--no-write` measurement on current captures is `BLOCKED` (`floor_ok=false`) because roster/common-floor requires **both BTC and ETH** with synchronized common bars ≥240; cannot seal a verdict until ETH is acquired and floors met.

**MANDATORY NEXT TASK (timestamped, non-optional, heavy real work — NO handoff-only completion):**

```
INIT-2026-11-16T02:07:52Z-EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE-ACQUIRE-ETH-MEASURE-SEAL
```

A session is **FAILED** if it only edits this handoff, only builds tooling/tests, or seals PREREG/BLOCKED/ACQUISITION without a real `EVAL_61_*COMBINED*` verdict. The live acquisition and measurement are heavy work and must be executed (not deferred).

### Required steps (in order)

1. **Acquire missing real ETH data (heavy, LIVE, mandatory) and ensure BTC+ETH floor met.** Reuse the proven, bug-fixed acquisition (no synthetic; real loaders raise `RealDataUnavailable`):
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   # acquire ETH (and/or re-acquire any short leg) with fresh real window
   python3 scripts/eval60_acquire_three_way.py --underlying ETH --days 1 \
     --max-per-expiry 40 --okx-delay 0.15 --out-dir data/raw/eval61 --seal
   ```
   (~15–20 min live). Use `--okx-delay` and built-in backoff; if OKX returns 0 trades, wait and retry — do **not** weaken floor. Keep/verify BTC captures in `data/raw/eval61/` satisfy floors; re-acquire BTC only if short. Per underlying floor (all must hold or widen capture, do not stop): surface ≥100 snaps / ≥50 instruments / ≥240 5m bars; Deribit option trades ≥2000 / ≥50 instruments / ≥240 bars / ≥79200s; perp candles ≥240 bars / ≥79200s; **common bars (surface×trades×perp) ≥240**; roster has **≥2 underlyings (BTC and ETH)**.
2. **Smoke/verify floors before sealing:** run measurement `--no-write` on `data/raw/eval61` and confirm `floor_ok=true` and roster covers BTC+ETH (or iterate acquisition until it does).
   ```bash
   PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}" \
     python3 scripts/eval61_orderflow_realized_vol_net_of_cost.py --capture-dir data/raw/eval61 --no-write
   ```
3. **Pre-register then measure (real verdict, not BLOCKED):** run without `--no-write` to emit fixed-protocol prereg and real COMBINED verdict from the straddle measurement (do not edit hypothesis/protocol to fit result).
   ```bash
   PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}" \
     python3 scripts/eval61_orderflow_realized_vol_net_of_cost.py --capture-dir data/raw/eval61
   ```
   Produces `EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION_<STAMP>Z.{json,md}` and `EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_<STAMP>Z.{json,md}` in `research_state/` (or `..._BLOCKED_*` only if floor still unmet — BLOCKED is **not** a verdict; widen and re-run).
4. **Seal with gate exit 0 (REQUIRED):**
   ```bash
   PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}" \
     python3 scripts/check_session_sealed.py \
       --task-id "INIT-2026-11-16T02:07:52Z-EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE-ACQUIRE-ETH-MEASURE-SEAL" \
       --require-glob "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION_*" \
       --require-glob "EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED_*"
   ```
   Stamp ≥ `2026-11-16T02:07:52Z`; exit 0 required. ACQUISITION/PREREG/BLOCKED alone does NOT satisfy the gate.
5. **Update this handoff in place** with verified facts/paths/commands/measured numbers and outcome (NO-GO/GO evidence). No GO without a verifying sealed artifact.

## WHY THIS RUNG (repo-name/charter; fixed hypothesis — NON-NEGOTIABLE)

`Cryptocurrency-quantitative-options-orderflow-strategy` = combined **OPTIONS + ORDERFLOW**. EVAL-46..60 are sealed NO-GO across fusion/smile ladders (directional/standalone/static vol/three-way). The one on-charter combination still unmeasured: **real options order-flow toxicity → subsequent realized volatility**, traded via a **signal-timed delta-hedged ATM straddle** net-of-cost on BTC/ETH perpetual (causal: decision at bar k → outcome [k,k+1], fresh ~24h, both BTC and ETH). This makes options ORDER FLOW drive a volatility trade (not directional/static). Fresh, pre-registered, heavy real-data falsification; new task ID outside EVAL-02..60.

**Hypothesis/GO bar (fixed, pre-registered):** per 5m bar `tox_k=(call_notional-put_notional)/(call_notional+put_notional)` from real Deribit option trades (and signed-aggressor imbalance variant), position `q_k=clip(expanding_z(tox_k),-1,1)` in ATM straddle (ATM IV/greeks from real marks), delta-hedged each bar; target `rv_{k+1}=|Δlog(perp_close)|` from real Deribit perp candles; P&L `q_k*[vega*dIV + 0.5*gamma*dS^2 - theta*dt] - hedge_cost - 5bps*|Δq_hedge|` (5bps turnover/hedge). Grid {toxicity variants}×{60s,300s}. **GO only if on both BTC and ETH and ≥1 config:** net-of-cost Sharpe>0, max-DD≤0.20, permutation p<0.05, bootstrap 95% CI lower>0, pooled PBO<0.5; else **NO-GO CONFIRMED (PASS)**.

## BOTTLENECKS — CLEARED / REMAINING (verified 2026-11-16T02:07:52Z)

1. **CLEARED:** EVAL-60 sealed NO-GO (gate exit 0); OKX acquisition bug fixed in `eval60_acquire_three_way.py` (cursor/backoff/delay; ETH captured in prior runs); EVAL-61 tooling + 11 unit tests built/verified; env green; network public read-only.
2. **REMAINING (must remove now, not defer):** **ETH real capture missing** from `data/raw/eval61/` and floors not yet satisfied for a BTC+ETH verdict — run ETH acquisition (and widen/retry on rate-limit/short legs), confirm `--no-write` floor_ok, then seal PREREG+COMBINED with gate exit 0. Do not hand off "run next session".

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal EVAL-02..60; do not edit sealed artifacts or `src/`.
- Never synthetic fallback; real loaders raise `RealDataUnavailable`; never relabel synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/credential mutation/order placement. Public read-only network only, polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`, `src/features/options_pricing.py`; no `phaseNN_*` wrappers.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped handoff copies (root retired pointers stay retired). Update this file in place with verified facts only.

## ANTI-STALL RULE

- Only acceptable outputs: (a) sealed `EVAL_61_*PREREGISTRATION_*` + `EVAL_61_*COMBINED_*` with gate exit 0 (stamp ≥ 2026-11-16T02:07:52Z), or (b) a stricter in-place handoff keeping floor identical/stricter.
- Timestamp-only edits without sealing/stricter scope = **failed session**. "Tooling built/capture started, run next" = **failed session**. BLOCKED is not a verdict — widen capture, do not stop/weaken floor/drop underlying.

## LOADER / ACQUISITION GOTCHAS

- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`.
- OKX: `GET https://www.okx.com/api/v5/market/history-trades?instId=<PERP>&limit=100` (`trades-history` 404). Paginate backwards `after=<oldest tradeId>` (dedupe by `tradeId`); instruments `BTC-USD-SWAP`,`ETH-USD-SWAP`; browser UA; `--okx-delay 0.15` + backoff; if 0 trades wait/retry (rate-limit cooldown) — do not weaken floor.
- EVAL-60/61 capture schema: `data/raw/eval61/three_way_{BTC,ETH}_<stamp>.json` with `surface.snapshots[]` (causal `spot`, `quotes[]`), `option_trades[]`, `perp_candles[]` (Deribit 1m), `okx_perp_trades[]`. No synthetic.
- Deribit: option trades `get_last_trades_by_instrument_and_time` (~24h cap → common window inside last ~24h); perp candles `get_tradingview_chart_data` `{BTC,ETH}-PERPETUAL` res `1`; surface/IV via real marks.
- DSR undefined for |Sharpe|≥1 (`atanh`) — rely on perm/bootstrap/PBO/BH-FDR.

## SEALED STATE (immutable; append only)

EVAL-02..60 sealed; EVAL-46..60 all **NO-GO CONFIRMED (PASS)** gate exit 0 (see prior COMBINED artifacts in `research_state/`). Re-running/re-sealing prohibited.

## SESSION LOG (append-only)

- 2026-11-14→2026-11-15: EVAL-41..59 sealed NO-GO (gate exit 0).
- 2026-11-15T22:44:10Z: EVAL-60 tooling built + smoke.
- 2026-11-16T00:34:26Z: EVAL-60 heavy BTC+ETH sealed `POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_COMBINED_20261116T003146Z` NO-GO (gate exit 0); OKX acquisition bug fixed; task advanced to EVAL-61.
- 2026-11-16T00:40:39Z: task timestamp refreshed; bottlenecks reported cleared.
- 2026-11-16T00:46:36Z: EVAL-61 measurement+tests built (11 passed), `--no-write` BLOCKED (no ETH capture), BTC-only acquisition launched/deferred — **stalled without verdict**.
- **2026-11-16T02:07:52Z (this session, handoff corrective):** verified state — BTC captures exist (`data/raw/eval61/three_way_BTC_20261116T005923Z.json`, `...011441Z.json`), **ETH capture missing**, no PREREG/COMBINED sealed; `--no-write` BLOCKED (floor_ok false, needs BTC+ETH). Updated authoritative task to `INIT-2026-11-16T02:07:52Z-EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE-ACQUIRE-ETH-MEASURE-SEAL` requiring ETH acquisition + floor-verified `--no-write` + real PREREG/COMBINED seal (gate exit 0). No verdict sealed this session (handoff-only corrective); next session must execute heavy acquisition/measurement and seal.
