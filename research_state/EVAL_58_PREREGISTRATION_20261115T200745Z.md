# EVAL_58_PREREGISTRATION — EVAL-58 options vol-surface/greeks skew / risk-reversal (25Δ) net-of-cost falsification

- Generated: `2026-11-15T20:07:45Z`
- Task: `EVAL-58-REAL-OPTIONS-SKEW-RISK-REVERSAL-NET-OF-COST-BTC-ETH`
- Hypothesis: A real Deribit options vol-surface/greeks skew / risk-reversal (25Δ) trade (long one 25Δ wing / short the other, sized by the skew mean-reversion deviation, delta-hedged in the perpetual) is net-of-cost tradable for the underlying BTC/ETH perpetual on real, synchronized Deribit data.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval58`

## Pre-declared protocol

- Surface -> IV: per real 5m snapshot & front expiry: IV backed out of each real quote mark (implied_volatility(mark*spot, spot, K, 0, T, type)); ~25Δ call = quoted call with |delta| nearest 0.25, ~25Δ put = quoted put with |delta| nearest 0.25 (both wings need a finite positive IV)
- Structures: ['risk_reversal_25d_delta_hedged']
- Skew lookback bars (trailing skew median): [12, 24, 48]
- Skew target choices: [0.25, 0.5]; size cap choices: [0.5, 1.0]
- Rebalance choices: [1, 2]; 25Δ delta target: 0.25
- Cost: net-of-cost: hedge turnover HEDGE_FEE_BPS on |Δhedge|*S; each of the 2 risk-reversal wings pays half its real bid/ask at entry and half at exit; full spread charged on risk-reversal side flips (hedge 5.0 bps; each of the 2 risk-reversal legs pays half its real bid/ask at entry and half at exit (long and short wings both charged the round-trip spread); full spread charged when the risk-reversal side flips between steps)
- PnL: dRR_k = exposure_k*side_k*((call_mark_{k+1}-call_mark_k)-(put_mark_{k+1}-put_mark_k))*S_k; gross_k = dRR_k + hedge_k*dS_k (hedge = -exposure*side*(call_delta - put_delta)); ret_k = (gross_k - cost_k)/S_k; decision at bar k -> outcome over [k,k+1] (causal)
- Skew rule: skew = IV(~25Δ put) - IV(~25Δ call); deviation = skew - trailing median skew over skew_lookback_bars (causal); side = +1 (long RR: long call/short put) when deviation > 0, -1 (short RR) when deviation < 0, 0 when equal; exposure = clip(|deviation| / skew_target, 0, size_cap)
- Wing selection rule: ~25Δ call = quoted call with |delta| nearest 0.25; ~25Δ put = quoted put with |delta| nearest 0.25; both at the front expiry; else config invalid
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
