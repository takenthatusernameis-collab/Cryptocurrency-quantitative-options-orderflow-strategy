# EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_PREREGISTRATION — real options order-flow toxicity -> signal-timed delta-hedged ATM straddle (feasible floor, correct mark-path P&L)

- Generated: `2026-11-16T08:22:10Z`
- Task: `EVAL64-FEASIBLE-FLOOR-OFLOW-RV-MARKPATH`
- Hypothesis: Real options order-flow toxicity predicts subsequent realized volatility, and a signal-timed delta-hedged ATM straddle measured with the correct mark-path net-of-cost P&L is tradable for the BTC/ETH perpetual on the already-acquired real 7d synchronized three-way captures, tested at the HEAVIEST floor the free Deribit/OKX public API can deliver (feasible-floor replication of EVAL-62; supersedes the sealed EVAL-63 BLOCKED whose strict >=7d perp floor is physically unreachable).
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval63`
- Extends: EVAL-62 (identical measurement, feasible pre-registered floor; EVAL-62 stays sealed/immutable)
- Supersedes: EVAL-63 (sealed BLOCKED: the strict >=7d perp floor is physically unreachable; perp 1m candles cap at 300000 s)

## Pre-declared protocol

- Tox signals: ['tox', 'imbalance']
- Position: side_k = sign(tox_z_k); exposure_k = clip(|tox_z_k|, 0, size_cap); causal decision at bar k; delta-hedged in the perp
- Straddle: front-expiry common strike nearest spot, both legs priced from real marks (EVAL-57 _pick_straddle_quotes/_iv_and_greeks, reused)
- P&L per bar: dOption_k = side_k*exposure_k*(mark_{k+1}-mark_k)*S_k; gross_k = dOption_k + hedge_k*dS_k; ret_k = (gross_k - cost_k)/S_k
- Bar grid (s): [60.0, 300.0]
- z-window: 20; cost: net-of-cost: hedge_fee_bps on |dHedge|*S; half real 2-leg spread at entry/exit; full spread on side flip (identical to EVAL-57/62)
- Stats: perm 1000 paired / bootstrap 1000 block 2 / PBO k=4 / BH-FDR alpha 0.1 / seed 42
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one grid config, net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, bootstrap 95% CI lower > 0, and pooled PBO < 0.5; else NO-GO.

## Pre-registered feasible floor (heaviest the free API delivers)

- min surface snapshots/underlying: 1000
- min surface instruments/underlying: 100
- min surface 5m bars/underlying: 1000
- min Deribit option trades/underlying: 2000
- min OF instruments/underlying: 150
- min OF span seconds/underlying: 82000.0
- min OF 5m bars/underlying: 240
- min perp 5m bars/underlying: 1000
- min perp span seconds/underlying: 300000.0
- min common 5m bars/underlying: 240
- min underlyings: 2

## Measured data-availability ceiling

- Option-trade retention (s, ~24h): 86400
- Perp 1m-candle retention (s, measured): 300000
- surface 5m candles DO scale to the full 7d (2017 snaps / 604800 s / 1001 5m bars)
