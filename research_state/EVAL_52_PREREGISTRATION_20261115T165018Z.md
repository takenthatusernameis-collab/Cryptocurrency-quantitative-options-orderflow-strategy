# EVAL_52_PREREGISTRATION — EVAL-52 options surface x options order-flow net-of-cost falsification

- Generated: `2026-11-15T16:50:18Z`
- Task: `EVAL-52-SYNCHRONIZED-OPTIONS-SURFACE-X-OPTIONS-ORDERFLOW-FUSION`
- Hypothesis: The fused options-surface x options-venue-order-flow strategy is net-of-cost tradable for the underlying BTC/ETH perpetual on real, synchronized Deribit data.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval52`

## Pre-declared protocol

- Surface components: ['gex_flip_signal', 'skew_slope_signal', 'calib_residual_signal']
- Surface signal: mean(components) clipped to [-1,1] (_options_signal_components)
- Order-flow signals: ['imbalance', 'notional_imbalance', 'call_minus_put']
- Fusion rules: ['sign_agreement', 'regime_filter', 'continuous_zscore']
- Bar grid (s): [60.0, 300.0]
- z-window: 20; z-clamp: 2.0
- Cost: net-of-cost: pre-registered 5 bps on turnover (taker + impact) (5.0 bps)
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
