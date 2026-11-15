# EVAL_54_PREREGISTRATION — EVAL-54 options vol-surface/greeks delta-hedged net-of-cost falsification

- Generated: `2026-11-15T17:53:51Z`
- Task: `EVAL-54-REAL-OPTIONS-VOL-SURFACE-DELTA-HEDGING-NET-OF-COST-BTC-ETH`
- Hypothesis: A real Deribit options vol-surface/greeks delta-hedged short-vol book is net-of-cost tradable for the underlying BTC/ETH perpetual on real, synchronized Deribit data.
- Capture dir: `data/raw/eval54`

## Pre-declared protocol

- Surface -> greeks: per real 5m snapshot & chosen expiry/strike: IV backed out of real mark (implied_volatility(mark*spot, spot, K, 0, T, type)); delta/gamma from black_scholes_greeks at that IV (intrinsic-delta fallback if IV fails)
- Structures: ['atm_call', 'atm_put', 'atm_straddle']
- Expiry choices: [0, 1]
- Rebalance choices: [1, 2]
- Bar grid (s): [300.0]
- Cost: net-of-cost: hedge turnover HEDGE_FEE_BPS on |Δhedge|*S; option half real bid/ask charged at entry and exit (hedge 5.0 bps; option half real bid/ask charged at entry and exit)
- PnL: gross_k = -(dOptionUSD_k) + hedge_k*dS_k; ret_k = (gross_k - cost_k)/S_k; decision at bar k -> outcome over [k,k+1] (causal)
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
