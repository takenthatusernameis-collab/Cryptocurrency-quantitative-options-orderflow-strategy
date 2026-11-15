# EVAL_50_PREREGISTRATION — EVAL-50 L2 OFI net-of-cost falsification

- Generated: `2026-11-15T13:47:05Z`
- Task: `EVAL-50-L2-OFI-NET-OF-COST`
- Hypothesis: Real L2 order-book OFI carries net-of-cost tradable alpha on OKX BTC/ETH perpetual swaps.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval50`

## Pre-declared protocol

- OFI: Cont/Kukanov/Stoikov (2014) multi-level order-flow imbalance, price-matched
- Bar grid (s): [5.0, 10.0]
- z-clamp grid: [1.0, 2.0]
- OFI z-window: 20
- Cost: net-of-cost: measured bar median quoted spread + fixed impact bps on turnover
- Stats: perm 1000 paired / bootstrap 1000 block 2 / PBO k=4 / BH-FDR alpha 0.1 / seed 42
- Kill-switch max-DD: 0.2

## Pre-declared GO bar

GO only if, on both BTC and ETH and at least one grid config, net-of-cost Sharpe > 0, no kill-switch breach (max-DD <= 0.20), permutation p < 0.05, and bootstrap 95% CI lower > 0; else NO-GO.

## Heavy-work floor (must be met to seal a verdict)

- min snapshots/instrument: 400
- min span seconds/instrument: 900.0
- min instruments: 2
