# EVAL_154_CROSS_ASSET_ORDERFLOW_IMBALANCE_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION — cross-asset order-flow imbalance spillover -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-21T03:15:33Z`
- Task: `EVAL154-CROSS-ASSET-ORDERFLOW-IMBALANCE-SPILLOVER-FORWARD-RETURN-SKEWNESS`
- Hypothesis: The causal options order-flow imbalance level of the OTHER underlying (cross-asset order-flow imbalance spillover) has a positive monotone (Spearman rank) relationship with the subsequent forward realized return skewness (third standardized moment) of the target underlying, independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-154 floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-81 (options order-flow imbalance -> signed return verbatim) + EVAL-149 (cross-asset imbalance spillover path verbatim) + EVAL-139 (forward realized return skewness target verbatim) + EVAL-77 (cross-asset alignment) + EVAL-101 (perp close series) + EVAL-65 (permutation / bootstrap inference) + EVAL-62 (FDR / seed); distinct cell: cross-asset order-flow imbalance spillover -> forward realized return skewness

## Pre-declared protocol

- Cross-asset spillover: baseline `BTC`, relative `ETH`
- Spillover signal: signal_k = imb_z[OTHER](k)  (other asset's order-flow imbalance z)
- Signal: imbalance
- Target: realized_return_skewness — forward realized return skewness = m3 / m2**1.5 over the TARGET underlying's next H perp log returns (strictly after the decision at bar k, lr[k:k+h]); third standardized moment, transcribed verbatim from sealed EVAL-139
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar options order-flow imbalance z of the OTHER underlying (e62.build_states tox_signal='imbalance', expanding-z-scored), aligned to the common BTC-vs-ETH bar grid (build_cross_section on imbalance states), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(other_imb_z_k, own_skew_k); directional permutation H1: IC>0 (higher other-asset order-flow imbalance -> more positive forward realized return skewness on the target)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120 / min aligned common bars 1

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (both underlyings + imbalance states + alignment)

- EVAL-154 cross-asset options order-flow imbalance floor: both underlyings (BTC, ETH) present, each with >= min_oflow_states_per_underlying constructible imbalance states on the coarsest grid, and >= min_aligned_common_bars non-disjoint common bar-ends. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 1
- Min usable pairs per config: 120
