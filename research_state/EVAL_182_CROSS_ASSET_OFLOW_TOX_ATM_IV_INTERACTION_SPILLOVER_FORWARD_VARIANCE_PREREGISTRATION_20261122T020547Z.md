# EVAL_182_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_PREREGISTRATION — cross-asset oflow tox x atm_iv interaction spillover -> forward realized return variance (Spearman rank IC)

- Generated: `2026-11-22T02:05:47Z`
- Task: `EVAL182-CROSS-ASSET-OFLOW-TOX-ATM-IV-INTERACTION-SPILLOVER-FORWARD-VARIANCE`
- Hypothesis: The causal options order-flow toxicity x near-ATM implied-vol interaction level of the OTHER underlying (cross-asset interaction spillover) has a positive monotone (Spearman rank) relationship with the subsequent forward realized return variance of the target underlying, independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-182 floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-176 (cross-asset atm_iv -> realized return variance) + EVAL-159 (cross-asset order-flow toxicity -> realized return variance) + EVAL-180 (cross-asset order-flow imbalance x atm_iv interaction -> realized return variance) + EVAL-151 (cross-asset order-flow toxicity x atm_iv interaction -> forward signed return mean) + EVAL-71 (surface atm_iv verbatim) + EVAL-62 (toxicity verbatim) + EVAL-77 (cross-asset alignment) + EVAL-172 (forward realized return variance target verbatim) + EVAL-65 (permutation / bootstrap inference); distinct cell: interaction spillover -> forward realized return variance

## Pre-declared protocol

- Cross-asset spillover: baseline `BTC`, relative `ETH`
- Spillover signal: signal_k = tox_z[OTHER](k) * atm_iv_z[OTHER](k)  (interaction of the other asset's order-flow toxicity z and near-ATM IV z)
- Signal: oflow_tox_atm_iv_interaction
- Target: forward_variance — forward realized return variance = mean((r - mean(r))**2) over the TARGET underlying's next H perp log returns (strictly after the decision at bar k, r_i=log(close_i/close_{i-1}) over i in k+1..k+H); transcribed verbatim from sealed EVAL-172
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar interaction of the OTHER underlying's z-scored options order-flow toxicity and near-ATM implied-vol level (e62.build_states tox_signal='tox' x e71.build_surface_bars atm_iv — SURFACE bar, not the term bar), aligned to the common BTC-vs-ETH bar grid, forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(other_interaction_z_k, own_variance_k); directional permutation H1: IC>0 (higher other-asset order-flow toxicity x atm_iv interaction -> higher forward realized return variance on the target)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120 / min aligned common bars 1

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (both underlyings + toxicity states + surface bars + alignment)

- EVAL-182 cross-asset order-flow toxicity x atm_iv interaction spillover floor: both underlyings (BTC, ETH) present, each with >= min_oflow_states_per_underlying constructible toxicity states and >= min_surface_bars_per_underlying constructible surface atm_iv bars on the coarsest grid, and >= min_aligned_common_bars non-disjoint common bar-ends where both signals coexist. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 1
- Min usable pairs per config: 120
