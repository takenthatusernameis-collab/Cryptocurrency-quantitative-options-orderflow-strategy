# EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_PREREGISTRATION — single-asset skew -> forward realized return variance

- Generated: `2026-11-21T22:01:12Z`
- Task: `EVAL173-SINGLE-ASSET-SKEW-FORWARD-VARIANCE`
- Hypothesis: The causal near-ATM put-call implied-vol skew has a positive monotone relationship with subsequent forward realized return variance of the same underlying's signed return.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Signal: skew
- Target: forward_variance
- Bar grid: [60.0, 300.0]
- Forward horizons: [6, 24, 72]
- GO bar: GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).
