# EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_PREREGISTRATION — options order-flow toxicity -> realized vol straddle net-of-cost falsification

- Generated: `2026-11-16T03:29:23Z`
- Task: `EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE`
- Hypothesis: Real options order-flow toxicity predicts subsequent realized volatility, and a signal-timed delta-hedged ATM straddle is net-of-cost tradable for the BTC/ETH perpetual on real, synchronized data.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`

## Pre-declared protocol

- Tox signals: ['tox', 'imbalance']
- Position: q_k = clip(expanding_z(tox_k), -1, 1); causal decision at bar k
- Realized-vol target: rv_{k+1} = |log(S_{k+1}) - log(S_k)| from Deribit 1m perp candles
- Straddle: ATM straddle from real surface snapshot (newest 5m snapshot whose candle closed by bar_end = bar_ms + 300s); IV backed out of the real mark via implied_volatility(mark*spot, spot, K, 0, T, type); greeks from black_scholes_greeks at that IV
- P&L per bar: q_k * [vega*(IV_{k+1}-IV_k) + 0.5*gamma*(dS)^2 - theta*dt] - cost_bps*|q_k*delta_k - q_{k-1}*delta_{k-1}|/1e4 - cost_bps*|q_k - q_{k-1}|/1e4
- Bar grid (s): [60.0, 300.0]
- z-window: 20; cost: net-of-cost: pre-registered 5 bps on delta-hedge rebalance and straddle-position turnover (5.0 bps)
- Stats: perm 1000 paired / bootstrap 1000 block 2 / PBO k=4 / BH-FDR alpha 0.1 / seed 42
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one grid config, net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, bootstrap 95% CI lower > 0, and pooled PBO < 0.5; else NO-GO.

## Heavy-work floor (must be met to seal a verdict)

- min surface snapshots/underlying: 100
- min bars/underlying: 240
- min instruments/underlying: 50
- min Deribit options-venue trades/underlying: 2000
- min span seconds/underlying: 79200.0
- min common 5m bars/underlying: 240
- min underlyings: 2
