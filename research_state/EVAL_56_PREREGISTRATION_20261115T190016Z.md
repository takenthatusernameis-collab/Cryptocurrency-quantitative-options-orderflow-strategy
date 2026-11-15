# EVAL_56_PREREGISTRATION — EVAL-56 options vol-surface/greeks term-structure calendar-spread net-of-cost falsification

- Generated: `2026-11-15T19:00:16Z`
- Task: `EVAL-56-REAL-OPTIONS-TERM-STRUCTURE-CALENDAR-SPREAD-NET-OF-COST-BTC-ETH`
- Hypothesis: A real Deribit options vol-surface/greeks term-structure calendar spread (long near-expiry ATM straddle / short far-expiry ATM straddle at a common strike, delta-hedged in the perpetual) is net-of-cost tradable for the underlying BTC/ETH perpetual on real, synchronized Deribit data.
- Capture dir: `data/raw/eval56`

## Pre-declared protocol

- Surface -> greeks: per real 5m snapshot & near/far expiry pair at a common strike nearest spot: IV backed out of each real mark (implied_volatility(mark*spot, spot, K, 0, T, type)); delta/gamma from black_scholes_greeks at that IV
- Structures: ['long_near_short_far_straddle']
- Expiry pairs (near_idx, far_idx): [[0, 1]]
- Rebalance choices: [1, 2]
- Bar grid (s): [300.0]
- Cost: net-of-cost: hedge turnover HEDGE_FEE_BPS on |Δhedge|*S; each of the 4 calendar legs pays half its real bid/ask at entry and half at exit (hedge 5.0 bps; each of the 4 calendar legs pays half its real bid/ask at entry and half at exit (long and short legs both charged the round-trip spread))
- PnL: dOption_k = (near_price_{k+1} - near_price_k) - (far_price_{k+1} - far_price_k); gross_k = dOption_k + hedge_k*dS_k (hedge = -net_position_delta); ret_k = (gross_k - cost_k)/S_k; decision at bar k -> outcome over [k,k+1] (causal)
- Common strike rule: nearest-to-spot strike quoted call+put in BOTH near & far expiry; fallback nearest common strike across the two; else config invalid
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
