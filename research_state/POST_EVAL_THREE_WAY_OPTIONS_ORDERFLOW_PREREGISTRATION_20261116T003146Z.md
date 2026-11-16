# POST_EVAL_THREE_WAY_OPTIONS_ORDERFLOW_PREREGISTRATION — three-way options+orderflow net-of-cost falsification

- Generated: `2026-11-16T00:31:46Z`
- Task: `POST-EVAL-THREE-WAY-OPTIONS-ORDERFLOW-FUSION`
- Hypothesis: The fused three-way (Deribit options surface x Deribit options-venue order flow x OKX perpetual order flow) strategy is net-of-cost tradable for the underlying BTC/ETH perpetual on real, synchronized data.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval60`

## Pre-declared protocol

- Surface components: ['gex_flip_signal', 'skew_slope_signal', 'calib_residual_signal']
- Surface signal: mean(components) clipped to [-1,1] (_options_signal_components)
- Options-venue order-flow signals: ['imbalance', 'notional_imbalance', 'call_minus_put']
- OKX perp order-flow signal: okx_imbalance
- Fusion rules: ['three_way_sign_agreement', 'three_way_regime_filter', 'three_way_continuous_zscore']
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
- min Deribit options-venue trades/underlying: 2000
- min span seconds/underlying: 79200.0
- min OKX perp trades/underlying: 2000
- min common 5m bars/underlying: 240
- min underlyings: 2
