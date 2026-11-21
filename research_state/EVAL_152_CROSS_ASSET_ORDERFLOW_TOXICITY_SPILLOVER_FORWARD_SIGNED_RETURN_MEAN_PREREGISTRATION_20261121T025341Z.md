# EVAL_152_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN_PREREGISTRATION — cross-asset order-flow toxicity spillover -> forward signed return mean (Spearman rank IC)

- Generated: `2026-11-21T02:53:41Z`
- Task: `EVAL152-CROSS-ASSET-ORDERFLOW-TOXICITY-SPILLOVER-FORWARD-SIGNED-RETURN-MEAN`
- Hypothesis: The causal options order-flow toxicity level of the OTHER underlying (cross-asset order-flow toxicity spillover) has a positive monotone (Spearman rank) relationship with the subsequent forward signed log-return mean of the target underlying, independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-152 floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-81 (options order-flow imbalance -> signed return verbatim) + EVAL-77 (cross-asset alignment via build_cross_section on toxicity states) + EVAL-101 (forward signed log-return mean target verbatim) + EVAL-65 (permutation / bootstrap inference) + EVAL-62 (FDR / seed); distinct cell: cross-asset order-flow toxicity spillover -> forward signed return mean

## Pre-declared protocol

- Cross-asset spillover: baseline `BTC`, relative `ETH`
- Spillover signal: signal_k = tox_z[OTHER](k)  (other asset's order-flow toxicity z)
- Signal: toxicity
- Target: forward_signed_return — forward signed log-return mean = sum(log(close_i/close_{i-1})) over the TARGET underlying's next H perp log returns (strictly after the decision at bar k, lr[k:k+h]); transcribed verbatim from sealed EVAL-101
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar options order-flow toxicity z of the OTHER underlying (e62.build_states tox_signal='tox', expanding-z-scored), aligned to the common BTC-vs-ETH bar grid (build_cross_section on toxicity states), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(other_tox_z_k, own_signed_k); directional permutation H1: IC>0 (higher other-asset order-flow toxicity -> more positive forward signed return on the target)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120 / min aligned common bars 1

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (both underlyings + toxicity states + alignment)

- EVAL-152 cross-asset options order-flow toxicity floor: both underlyings (BTC, ETH) present, each with >= min_oflow_states_per_underlying constructible toxicity states on the coarsest grid, and >= min_aligned_common_bars non-disjoint common bar-ends. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 1
- Min usable pairs per config: 120
