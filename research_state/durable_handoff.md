# SINGLE DURABLE HANDOFF — READ FIRST (only actionable handoff)

## AUTHORITATIVE INITIAL TASK FOR NEXT SESSION (timestamped; the only valid task)

**Status as of 2026-11-16T03:17:05Z (verified this session):** EVAL-02..60 are sealed
`NO-GO CONFIRMED (PASS)`. EVAL-61 sealed `NO-GO CONFIRMED (PASS)` BUT its verdict is a
**measurement artifact** (see "Why EVAL-61 is not a valid falsification" below): its
P&L accumulates un-normalized **dollar** P&L (`vega*dIV + 0.5*gamma*(dS)^2 - theta*dt`,
with `dS` in dollars) and treats it as a **return**, so every config spuriously breaches
the `max-DD <= 0.20` kill-switch at exactly `1.0000` -> a false NO-GO that never actually
tested the repo's namesake hypothesis. **The genuinely on-charter, untested heavy rung is
now DEFINED and BUILT: EVAL-62** — the repo's namesake hypothesis (real **options ORDER
FLOW** driving a **volatility** trade) measured with the **correct EVAL-57 mark-path
net-of-cost P&L** (`ret_k = (side*exposure*(mark_{k+1}-mark_k)*S_k + hedge_k*dS_k -
cost_k)/S_k`). EVAL-62 tooling + 8 unit tests are built and verified; it reads the
**already-acquired** real `data/raw/eval61/` captures (no re-acquisition bottleneck).

Env green (verified 2026-11-16T03:17:05Z): `./scripts/verify_env.sh --check` OK;
`.venv-deps/` present; `.env` absent; `LIVE_TRADING_ENABLED` unset.

**Measured current state (verified 2026-11-16T03:17:05Z, `--no-write` on real data):**
- EVAL-62 on `data/raw/eval61` → `floor_ok=true` (BTC+ETH), `verdict=NO-GO CONFIRMED (PASS)`,
  pooled PBO 0.3750. **Kill-switch breaches are GONE** (all max-DD 0.03–0.12, not 1.0) —
  confirming EVAL-61's breaches were a P&L artifact. Every config fails on real merits:
  best Sharpe BTC **−0.0443** (imbalance::bar300), ETH **+0.6163** (imbalance::bar300);
  permutation p 0.08–0.97 (≫0.05); bootstrap 95% CI lower negative for all. The options
  order-flow → vol signal does **not** pass the GO bar when measured honestly.

**MANDATORY NEXT TASK (timestamped, non-optional):**

```
INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL
```

**SESSION IS NOT COMPLETE. EVAL-62 is BUILT + VERIFIED but NOT YET SEALED.** The next
session MUST execute the heavy work below (real verdict, gate exit 0). "Tooling built,
run next" = failed session. Timestamp-only edits without sealing = failed session.

### Required steps (in order) — tooling DONE this session; SEAL is the remaining work

1. **Smoke/verify floors (already real data; no acquisition needed).** DONE this session:
   `python3 scripts/eval62_orderflow_realized_vol_markpath.py --capture-dir data/raw/eval61
   --no-write` → `floor_ok=true`, roster BTC+ETH, `NO-GO CONFIRMED (PASS)`.
2. **Seal the real verdict (REQUIRED — the heavy work).** TODO next session:
   ```bash
   export PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"
   python3 scripts/eval62_orderflow_realized_vol_markpath.py \
       --capture-dir data/raw/eval61 --seal \
       --task-label "INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL"
   ```
   This seals `EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION_<UTC>.{json,md}` then
   `EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_<UTC>.{json,md}`. If you want fresher
   data, FIRST re-acquire (heavy, live, ~25 min) with the proven acquisition, then re-run:
   `python3 scripts/eval60_acquire_three_way.py --underlying BTC --underlying ETH --days 1
   --out-dir data/raw/eval62 --seal --task-label EVAL62-ACQUIRE` and point `--capture-dir
   data/raw/eval62`. Never synthetic; never weaken the floor.
3. **Seal with gate exit 0 (REQUIRED).**
   ```bash
   python3 scripts/check_session_sealed.py \
     --task-id "INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL" \
     --glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION_*" \
     --require-glob "EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_*"
   ```
   Exit 0 required. (Use `--require-any-glob ..._BLOCKED_*` instead of `--require-glob`
   only if the floor genuinely fails — but it does not: BTC+ETH floor is met.)
4. **Update this handoff in place** with verified facts/paths/commands/measured numbers
   and the sealed verdict. Then, and only then, is the session complete.

## WHY THIS RUNG (repo-name/charter; fixed hypothesis — NON-NEGOTIABLE)

`Cryptocurrency-quantitative-options-orderflow-strategy` = combined **OPTIONS + ORDERFLOW**.
The repo's **namesake** hypothesis is that real **options order flow** carries predictive
information about **subsequent realized volatility**, and that a **signal-timed
delta-hedged ATM straddle** can harvest it net-of-cost. EVAL-46..60 sealed NO-GO across
fusion/smile/standalone ladders; EVAL-61 attempted this namesake rung but with a **broken
P&L** (see below), so it never actually tested the hypothesis. EVAL-62 is the correct,
heavy, pre-registered falsification.

**Hypothesis/GO bar (fixed, pre-registered):** per 5m bar `tox_k =
(call_notional-put_notional)/(call_notional+put_notional)` from real Deribit option trades
(and signed-aggressor `imbalance` variant); `side_k = sign(tox_z_k)`, `exposure_k =
clip(|tox_z_k|,0,size_cap)`; delta-hedged each bar in the perp; **correct mark-path P&L**
`ret_k = (side_k*exposure_k*(mark_{k+1}-mark_k)*S_k + hedge_k*dS_k - cost_k)/S_k` with
`hedge_k = -side_k*exposure_k*straddle_delta_k` and cost = hedge_fee_bps on |Δhedge|·S +
half real 2-leg spread at entry/exit + full spread on side flip (identical to EVAL-57).
Grid {tox, imbalance} × {60s,300s}. **GO only if on both BTC and ETH and ≥1 config:**
net-of-cost Sharpe>0, max-DD≤0.20, permutation p<0.05, bootstrap 95% CI lower>0, pooled
PBO<0.5; else **NO-GO CONFIRMED (PASS)**.

## Why EVAL-61 is NOT a valid falsification (the bottleneck this session removes)

EVAL-61's `strategy_returns` computes
`net_k = q_k*(vega*dIV + 0.5*gamma*(dS)^2 - theta*dt) - hedge_cost - turnover_cost`
where `dS` is a **dollar** price change and `vega`/`gamma` are per-1.0-vol / per-1.0-spot
greeks, then treats `net_k` itself as a **return** — never dividing by spot `S_k` and
never using the actual straddle mark path. Magnitude is set by the *level* of spot×vega, so
one 5m bar prints `+135` or `-105` "returns" → `max-DD = 1.0000` on all 8 configs → false
`NO-GO`. EVAL-57 already used the **correct** formula
`dOption = side*exposure*(mark_{k+1}-mark_k)*S; gross = dOption + hedge*dS; ret =
(gross-cost)/S` but **ignored options order flow** (sized purely on IV−realized VRP
spread). EVAL-62 fuses the two: order flow drives `side`/`exposure`, EVAL-57 formula
measures it. EVAL-61 is superseded, not re-litigated; do not edit sealed EVAL-61 artifacts.

## BOTTLENECKS — CLEARED this session

1. **CLEARED (no re-acquisition needed):** EVAL-62 reads the already-acquired real
   `data/raw/eval61/three_way_{BTC,ETH}_*.json` (289 snaps / 2748 BTC & 3558 ETH option
   trades / 227 ETH & 87 BTC of-instruments / 288 common 5m bars per underlying; floor met
   on both). No network, no synthetic.
2. **CLEARED (P&L artifact fixed):** EVAL-62 uses the EVAL-57-correct mark-path return;
   the spurious max-DD=1.0 kill-switch breaches are gone (real max-DD 0.03–0.12).
3. **CLEARED (tooling + tests):** `scripts/eval62_orderflow_realized_vol_markpath.py` +
   `tests/test_eval62_orderflow_realized_vol_markpath.py` (8 tests, incl. a regression
   guard pinning the correct return formula) — `py_compile` OK, `pytest` 8 passed;
   EVAL-57/61 regression 35 passed; `./scripts/verify_env.sh --check` OK.
4. **REMAINING (the heavy work):** seal EVAL-62 with gate exit 0 (steps 2–3 above). If a
   new task ID is ever opened, reuse `scripts/eval60_acquire_three_way.py --underlying <X>`
   for acquisition and the EVAL-57 mark-path P&L; never synthetic; pre-register then seal
   with gate exit 0.

## PROHIBITED / INVARIANTS (non-negotiable)

- Do **not** re-run/re-litigate/re-seal EVAL-02..61; do not edit sealed artifacts or `src/`.
- Never synthetic fallback; real loaders raise `RealDataUnavailable`; never relabel
  synthetic as real; never emit `{"valid": true}`.
- Paper-only: `.env` absent; `LIVE_TRADING_ENABLED=false`; no live enablement/venue/config/
  credential mutation/order placement. Public read-only network only, polite rate limiting.
- Reuse `src/analytics/`, `src/data/`, `src/backtest/`, `src/telemetry/`,
  `src/features/options_pricing.py`; no `phaseNN_*` wrappers.
- No full test-suite discovery; no `research_state/` enumeration loops; no timestamped
  handoff copies (root retired pointers stay retired). Update this file in place with
  verified facts only.
- EVAL-62 must not reintroduce the EVAL-61 artifact: returns MUST be normalized by spot
  (`ret = net/S`) and use the straddle mark path. The regression guard
  `test_markpath_returns_correct_formula` enforces this; do not weaken it.

## ANTI-STALL RULE

- Only acceptable outputs: (a) sealed `EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_PREREGISTRATION_*`
  + `EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED_*` with gate exit 0 (stamp ≥
  2026-11-16T03:17:05Z) — **the heavy work** — or (b) a stricter in-place handoff keeping
  the floor identical/stricter.
- Timestamp-only edits without sealing = **failed session**. "Tooling built, run next" =
  **failed session**. BLOCKED is not a verdict — widen the capture (reuse the proven
  acquisition), do not stop/weaken the floor/drop an underlying.
- This session already did the buildable work (tooling + tests + real `--no-write`); the
  next session must SEAL. Do not re-derive the hypothesis or rebuild tooling.

## LOADER / ACQUISITION GOTCHAS

- Run with `PYTHONPATH="$PWD/.venv-deps${PYTHONPATH:+:$PYTHONPATH}"`.
- OKX: `GET https://www.okx.com/api/v5/market/history-trades?instId=<PERP>&limit=100`
  (`trades-history` 404). Paginate backwards `after=<oldest tradeId>` (dedupe by
  `tradeId`); instruments `BTC-USD-SWAP`,`ETH-USD-SWAP`; browser UA; `--okx-delay 0.15` +
  backoff; if 0 trades wait/retry (rate-limit cooldown) — do not weaken floor.
- EVAL-60/61/62 capture schema: `data/raw/eval62/three_way_{BTC,ETH}_<stamp>.json` (or
  reuse `data/raw/eval61/`) with `surface.snapshots[]` (causal `spot`, `quotes[]` with
  `mark`/`bid`/`ask`/`strike`/`expiry`/`option_type`), `option_trades[]`,
  `perp_candles[]` (Deribit 1m), `okx_perp_trades[]`. No synthetic.
- Snapshot `bar_ms` is the bar OPEN; EVAL-62 aligns snapshots to the same bar-end grid as
  EVAL-61's `toxicity_per_bar` (`bar_end = ((ts//grid)+1)*grid`) — do not "fix" this back
  to raw `bar_ms` matching or states silently vanish.
- Deribit: option trades `get_last_trades_by_instrument_and_time` (~24h cap → common
  window inside last ~24h); perp candles `get_tradingview_chart_data` `{BTC,ETH}-PERPETUAL`
  res `1`; surface/IV via real marks.
- DSR undefined for |Sharpe|≥1 (`atanh`) — rely on perm/bootstrap/PBO/BH-FDR.

## SEALED STATE (immutable; append only)

EVAL-02..61 sealed; EVAL-46..61 all **NO-GO CONFIRMED (PASS)** gate exit 0 (see prior
COMBINED artifacts in `research_state/`). Re-running/re-sealing prohibited. **EVAL-61's
NO-GO is an artifact (broken P&L); EVAL-62 is its correct replacement and must be sealed
to honestly close the namesake rung.** Do not edit sealed EVAL-61 files.

## SESSION LOG (append-only)

- 2026-11-14→2026-11-15: EVAL-41..59 sealed NO-GO (gate exit 0).
- 2026-11-15T22:44:10Z: EVAL-60 tooling built + smoke.
- 2026-11-16T00:34:26Z: EVAL-60 heavy BTC+ETH sealed NO-GO (gate exit 0); OKX bug fixed.
- 2026-11-16T02:41:37Z: EVAL-61 sealed NO-GO (gate exit 0) — later found to be a P&L artifact.
- **2026-11-16T03:17:05Z (this session):** verified EVAL-61 P&L is a measurement artifact
  (un-normalized dollar P&L as returns → max-DD=1.0 on all configs). Built
  `scripts/eval62_orderflow_realized_vol_markpath.py` (correct EVAL-57 mark-path P&L driven
  by options order-flow side/exposure) + `tests/test_eval62_orderflow_realized_vol_markpath.py`
  (8 tests, incl. regression guard). Verified: `py_compile` OK, `pytest` 8 passed (+35 with
  EVAL-57/61 regression), `verify_env.sh --check` OK. Real `--no-write` on `data/raw/eval61`:
  `floor_ok=true`, `NO-GO CONFIRMED (PASS)`, BTC best Sharpe −0.0443 / ETH +0.6163, pooled
  PBO 0.375, kill-switch breaches GONE (max-DD 0.03–0.12). **EVAL-62 NOT yet sealed** —
  next session must seal with gate exit 0 per the mandatory task above.