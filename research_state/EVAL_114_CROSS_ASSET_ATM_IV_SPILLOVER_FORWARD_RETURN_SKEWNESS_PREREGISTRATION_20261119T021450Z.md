# EVAL_114_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION — cross-asset atm_iv spillover -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-19T02:14:50Z`
- Task: `EVAL114-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-RETURN-SKEWNESS`
- Hypothesis: The causal near-ATM implied-vol level of the OTHER underlying (cross-asset atm_iv spillover) has a positive monotone (Spearman rank) relationship with the subsequent forward realized return skewness (third standardized moment) of the target underlying, independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-71 + alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71/87/109 (same atm_iv signal path and sealed EVAL-71 surface floor) + EVAL-77 (cross-asset alignment via build_cross_section) + EVAL-85 (forward-window convention lr[k:k+h]); distinct cell: cross-asset atm_iv spillover -> forward realized return skewness

## Pre-declared protocol

- Cross-asset spillover: baseline `BTC`, relative `ETH`
- Spillover signal: signal_k = atm_iv[OTHER](k)  (other asset's near-ATM IV)
- Signal: atm_iv
- Target: realized_return_skewness — forward realized return skewness = m3 / m2**1.5 over the TARGET underlying's next H perp log returns (strictly after the decision at bar k, lr[k:k+h]); third standardized moment, transcribed verbatim from sealed EVAL-109/111/112/113
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar near-ATM implied-vol level of the OTHER underlying (e71.build_surface_bars atm_iv), aligned to the common BTC-vs-ETH bar grid (build_cross_section), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(other_atm_iv_z_k, own_skew_k); directional permutation H1: IC>0 (higher other-asset near-ATM IV -> more right-skewed forward returns on the target)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120 / min aligned common bars 200

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 both underlyings + alignment)

- Reuses the sealed EVAL-71 surface floor verbatim (min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s), applied to BOTH BTC and ETH, plus a cross-asset alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal near-ATM IV on the coarsest grid). Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120
