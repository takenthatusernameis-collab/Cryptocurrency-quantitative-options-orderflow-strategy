# EVAL_109_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_SKEWNESS_PREREGISTRATION — atm_iv -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-18T23:10:58Z`
- Task: `EVAL109-SINGLE-ASSET-ATM-IV-FORWARD-RETURN-SKEWNESS`
- Hypothesis: The causal near-ATM implied-vol level (atm_iv) has a positive monotone (Spearman rank) relationship with the subsequent forward realized return skewness (third standardized moment) of the same underlying, independent of any trading wrapper; tested on real on-disk captures at the EVAL-71 surface floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71/87/101 (same atm_iv signal path and sealed EVAL-71 surface floor) + EVAL-85 (same forward-window convention, lr[k:k+h]); distinct cell: single-asset atm_iv level -> forward realized return skewness

## Pre-declared protocol

- Signal: atm_iv
- Target: realized_return_skewness — forward realized return skewness = m3 / m2**1.5 over the SAME underlying's next H perp log returns (strictly after the decision at bar k, lr[k:k+h]); third standardized moment, distinct from quantile-spread tail asymmetry and from signed mean
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar near-ATM implied-vol level (e71.build_surface_bars atm_iv), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(atm_iv_z_k, skew_k); directional permutation H1: IC>0 (higher near-ATM IV -> more positively skewed forward returns)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered floor (EVAL-71 surface floor, not the EVAL-64 ladder floor)

- Reuses the sealed EVAL-71 surface floor verbatim (min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min usable pairs per config: 120
