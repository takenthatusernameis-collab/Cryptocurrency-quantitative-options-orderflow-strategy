# EVAL_53_PREREGISTRATION — EVAL-53 cross-window surface x options order-flow replication

- Generated: `2026-11-15T17:17:12Z`
- Task: `INIT-2026-11-15T17:17:12Z-EVAL-53-CROSS-WINDOW-SYNCHRONIZED-SURFACE-X-ORDERFLOW-REPLICATION`
- Hypothesis: The EVAL-52 fused options-surface x options-venue-order-flow NO-GO is temporally stable across an independent synchronized ~24h Deribit capture (window B, BTC+ETH).
- Window A (sealed eval52): `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval52`
- Window B (new capture): `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval53`

## Pre-declared protocol (sealed EVAL-52, reused verbatim)

- Surface components: ['gex_flip_signal', 'skew_slope_signal', 'calib_residual_signal']
- Order-flow signals: ['imbalance', 'notional_imbalance', 'call_minus_put']
- Fusion rules: ['sign_agreement', 'regime_filter', 'continuous_zscore']
- Bar grid (s): [60.0, 300.0]
- z-window: 20; cost: 5.0 bps
- Stats: perm 1000 paired / bootstrap 1000 block 2 / PBO k=4 / BH-FDR alpha 0.1 / seed 42
- Kill-switch max-DD: 0.2

## Pre-declared cross-window GO bar

GO CONFIRMED only if the per-config GO bar (net-of-cost Sharpe > 0, no kill-switch breach max-DD <= 0.20, permutation p < 0.05, bootstrap 95% CI lower > 0) holds on both windows for the same config on both BTC and ETH, and pooled PBO < 0.5 on both windows; else NO-GO CONFIRMED (PASS) when both windows floor-passing; BLOCKED if window B is below the heavy-work floor.

## Heavy-work floor (must be met to seal a verdict)

- min surface snapshots/underlying: 100
- min bars/underlying: 240
- min instruments/underlying: 50
- min option trades/underlying: 2000
- min span seconds/underlying: 79200.0
- min common 5m bars/underlying: 240
- min underlyings: 2
