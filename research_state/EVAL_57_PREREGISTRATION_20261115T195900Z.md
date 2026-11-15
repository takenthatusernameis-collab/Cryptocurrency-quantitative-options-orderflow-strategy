# EVAL_57_PREREGISTRATION — EVAL-57 options vol-surface/greeks VRP / realized-vs-implied vol net-of-cost falsification

- Generated: `2026-11-15T19:59:00Z`
- Task: `INIT-2026-11-15T19:55:04Z-EVAL-57-REAL-OPTIONS-VOL-RISK-PREMIUM-REALIZED-VS-IMPLIED-NET-OF-COST-BTC-ETH-ACQUIRE-MEASURE-AND-SEAL`
- Hypothesis: A real Deribit options vol-surface/greeks volatility risk premium trade (long/short ATM straddle sized by the IV-realized-vol spread, delta-hedged in the perpetual) is net-of-cost tradable for the underlying BTC/ETH perpetual on real, synchronized Deribit data.
- Capture dir: `data/raw/eval57`

## Pre-declared protocol

- Surface -> IV: per real 5m snapshot & front expiry at a common strike nearest spot: series IV = mean(call IV, put IV), each backed out of each real mark (implied_volatility(mark*spot, spot, K, 0, T, type))
- Structures: ['vrp_straddle_delta_hedged']
- Lookback bars (realized vol): [12, 24, 48]
- Vol target: 0.5; size cap: 1.0
- Rebalance choices: [1, 2]
- Bar grid (s): [300.0]
- Cost: net-of-cost: hedge turnover HEDGE_FEE_BPS on |Δhedge|*S; each of the 2 straddle legs pays half its real bid/ask at entry and half at exit; full spread charged on VRP side flips (hedge 5.0 bps; each of the 2 straddle legs pays half its real bid/ask at entry and half at exit (long and short legs both charged the round-trip spread); full spread charged when the VRP side flips between steps)
- PnL: dOption_k = side_k*exposure_k*(straddle_mark_{k+1}-straddle_mark_k)*S_k; gross_k = dOption_k + hedge_k*dS_k (hedge = -side*exposure*straddle_delta); ret_k = (gross_k - cost_k)/S_k; decision at bar k -> outcome over [k,k+1] (causal)
- VRP rule: side = +1 (long straddle) when IV < realized (buy vol), -1 (short straddle) when IV > realized (sell vol), 0 when equal; exposure = clip(|IV - realized| / vol_target, 0, size_cap)
- Common strike rule: nearest-to-spot strike quoted call+put in the front expiry; else config invalid
- Walk-forward: {'train_frac': '1/3', 'test_frac': '1/5', 'step_frac': '1/5'}
- Stats: perm 1000 paired / bootstrap 1000 block 2 / PBO k=4 / BH-FDR alpha 0.1 / seed 42
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one grid config, net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, bootstrap 95% CI lower > 0, and pooled PBO < 0.5; else NO-GO.

## Heavy-work floor (must be met to seal a verdict)

- min surface snapshots/underlying: 100
- min bars/underlying: 240
- min instruments/underlying: 50
- min option trades/underlying: 2000
- min span seconds/underlying: 79200.0
- min common 5m bars/underlying: 240
- min underlyings: 2
- term-structure min expiries: 2
- term-structure min snapshots/expiry: 100
