# EVAL_179_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_VARIANCE_PREREGISTRATION — cross-asset term_ratio spillover -> forward variance (Spearman rank IC)

- Generated: `2026-11-21T23:59:53Z`
- Task: `EVAL179-CROSS-ASSET-TERM-RATIO-SPILLOVER-FORWARD-VARIANCE`
- Hypothesis: The causal ATM implied-vol term ratio of the OTHER underlying (cross-asset term_ratio spillover) has a positive monotone (Spearman rank) relationship with the subsequent forward realized return variance of the target underlying, independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-71 + EVAL-74 + alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-74 (_term_bars term_ratio verbatim + EVAL-74 term floor + EVAL-71 surface floor) + EVAL-148 (cross-asset alignment via build_cross_section) + EVAL-172 (forward realized return variance target verbatim) + EVAL-175 (single-asset term_ratio -> variance) + EVAL-65 (permutation / bootstrap inference) + EVAL-62 (FDR / seed); distinct cell: cross-asset term_ratio spillover -> forward variance

## Pre-declared protocol

- Cross-asset spillover: baseline `BTC`, relative `ETH`
- Spillover signal: signal_k = term_ratio[OTHER](k)  (other asset's ATM IV term ratio)
- Signal: term_ratio
- Target: forward_variance — forward realized return variance = mean((r - mean(r))**2) of the TARGET underlying's next H perp log returns (strictly after the decision at bar k, r_i=log(close_i/close_{i-1}) over i in k+1..k+H); transcribed verbatim from sealed EVAL-159 / EVAL-172
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar ATM implied-vol term ratio of the OTHER underlying (e74._term_bars term_ratio — TERM bar, not the surface bar), aligned to the common BTC-vs-ETH bar grid (build_cross_section), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(other_term_ratio_z_k, own_var_k); directional permutation H1: IC>0 (higher other-asset term ratio -> higher forward realized variance on the target)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120 / min aligned common bars 200

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 surface + EVAL-74 term adequacy + alignment)

- Reuses the sealed EVAL-71 surface floor verbatim (min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s), applied to BOTH BTC and ETH, plus the sealed EVAL-74 term-structure adequacy floor (min_distinct_expiries=2, min_expiry_trades=5, min_bars_with_term=40), plus a cross-asset alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal term bar on the coarsest grid). Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120
