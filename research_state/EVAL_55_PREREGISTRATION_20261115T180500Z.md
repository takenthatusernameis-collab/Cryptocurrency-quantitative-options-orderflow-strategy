# EVAL_55_PREREGISTRATION — EVAL-55 options vol-surface/greeks gamma-hedged net-of-cost falsification

- Generated: `2026-11-15T18:05:00Z`
- Task: `EVAL-55-REAL-OPTIONS-GAMMA-HEDGED-NET-OF-COST-BTC-ETH`
- Hypothesis: A real Deribit options vol-surface/greeks gamma-hedged long-gamma (gamma-scalping) book is net-of-cost tradable for the underlying BTC/ETH perpetual on real, synchronized Deribit data.
- Capture dir: `data/raw/eval55`

## Pre-declared protocol

- Surface -> greeks: per real 5m snapshot & chosen expiry/strike: IV backed out of real mark (implied_volatility(mark*spot, spot, K, 0, T, type)); delta/gamma from black_scholes_greeks at that IV (intrinsic-delta fallback if IV fails)
- Structures: ['long_atm_call', 'long_atm_put', 'long_atm_straddle']
- Expiry choices: [0, 1]
- Rebalance choices: [1, 2]
- Bar grid (s): [300.0]
- Cost: net-of-cost: hedge turnover HEDGE_FEE_BPS on |Δhedge|*S; long option pays half real bid/ask at entry (ask) and exit (bid) (hedge 5.0 bps; option half real bid/ask paid at entry and exit (long options pay the ask))
- PnL: gross_k = +(dOptionUSD_k) + hedge_k*dS_k (long option, hedge=-position_delta); ret_k = (gross_k - cost_k)/S_k; decision at bar k -> outcome over [k,k+1] (causal)
- Gamma attribution: diagnostic: realized gamma capture = sum 0.5*Gamma_usd_k*(dS_k)^2 vs total premium paid; gamma_capture_over_premium reported per config (not a pass criterion)
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
