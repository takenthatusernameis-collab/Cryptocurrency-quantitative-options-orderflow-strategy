# EVAL_51_PREREGISTRATION — EVAL-51 options order-flow net-of-cost falsification

- Generated: `2026-11-15T15:20:05Z`
- Task: `EVAL-51-OPTIONS-ORDERFLOW-NET-OF-COST`
- Hypothesis: Signed options order flow on real Deribit option trades carries net-of-cost tradable alpha for the underlying BTC/ETH perpetual.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval51`

## Pre-declared protocol

- Signals: ['imbalance', 'notional_imbalance', 'call_minus_put']
- Bar grid (s): [5.0, 15.0]
- z-window: 20; z-clamp: 2.0
- Cost: net-of-cost: pre-registered conservative Deribit perp taker + impact bps on turnover (5.0 bps)
- Stats: perm 1000 paired / bootstrap 1000 block 2 / PBO k=4 / BH-FDR alpha 0.1 / seed 42
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one grid config, net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, and bootstrap 95% CI lower > 0; else NO-GO.

## Heavy-work floor (must be met to seal a verdict)

- min option trades/underlying: 2000
- min bars/underlying: 240
- min instruments/underlying: 50
- min span seconds/underlying: 79200.0
- min underlyings: 2
