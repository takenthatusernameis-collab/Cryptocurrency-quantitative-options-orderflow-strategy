# EVAL_140_COMPOSITE_ATM_IV_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_PREREGISTRATION — composite cross-asset spillover -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-20T11:04:20Z`
- Task: `EVAL140-COMPOSITE-ATM-IV-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-SKEWNESS`
- Hypothesis: An equal-weight z-score composite of the OTHER underlying's causal near-ATM atm_iv level and near-minus-far ATM IV term_slope (cross-asset spillover) has a positive monotone (Spearman rank) relationship with the subsequent forward realized return skewness (third standardized moment) of the target underlying, and that relationship is strictly stronger than either single leg's best IC, tested on real on-disk captures at the composed EVAL-71 + alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-114 (cross-asset atm_iv spillover -> forward return skewness) + EVAL-122 (cross-asset term_slope spillover -> forward return skewness) + EVAL-71 (atm_iv surface bar + surface floor verbatim) + EVAL-74 (term_slope reconstruction _term_bars verbatim) + EVAL-65/62 (inference verbatim); distinct cell: equal-weight z-score composite of the two surviving spillover GOs must beat each leg alone

## Pre-declared protocol

- Cross-asset spillover: baseline `BTC`, relative `ETH`
- Spillover signal: composite_k = 0.5*z(atm_iv[OTHER](k)) + 0.5*z(term_slope[OTHER](k))  (equal-weight z-score composite)
- Composite weights: {'atm_iv': 0.5, 'term_slope': 0.5}
- Target: realized_return_skewness — forward realized return skewness = m3 / m2**1.5 over the TARGET underlying's next H perp log returns (strictly after the decision at bar k, lr[k:k+h]); third standardized moment, transcribed verbatim from sealed EVAL-109/112/113/116
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: equal-weight z-score composite of the OTHER underlying's causal per-bar near-ATM atm_iv level and near-minus-far ATM IV term_slope, aligned to the common BTC-vs-ETH bar grid (build_cross_section), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(composite_z_k, own_skew_k); directional permutation H1: IC>0 (wider other-asset near/far-IV surface -> more right-skewed forward returns on the target)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120 / min aligned common bars 200

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH: (a) at least one composite config has Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0 and is BH-FDR-rejected in the pooled composite family; AND (b) the composite's best IC strictly beats each leg's best IC (atm_iv-only and term_slope-only, computed in the same run as descriptive comparators). Else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 both underlyings + alignment)

- Reuses the sealed EVAL-71 surface floor verbatim (min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s), applied to BOTH BTC and ETH, plus a cross-asset alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal near-ATM surface bar on the coarsest grid). Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120
