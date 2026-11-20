# EVAL_136_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_KURTOSIS_PREREGISTRATION — cross-asset skew spillover -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-20T05:55:01Z`
- Task: `EVAL136-CROSS-ASSET-SKEW-SPILLOVER-FORWARD-RETURN-KURTOSIS`
- Hypothesis: The causal near-ATM put-call implied-vol skew of the OTHER underlying (cross-asset skew spillover) has a positive monotone (Spearman rank) relationship with the subsequent forward realized return kurtosis (fourth standardized moment) of the target underlying, independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-71 + alignment floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-132 (cross-asset skew spillover signal verbatim) + EVAL-117/119/121/129 (forward realized return kurtosis target verbatim) + EVAL-71 (surface floor) + EVAL-77 (cross-asset alignment) + EVAL-65 (permutation / bootstrap inference) + EVAL-62 (FDR / seed); distinct cell: cross-asset skew spillover -> forward realized return kurtosis

## Pre-declared protocol

- Cross-asset spillover: baseline `BTC`, relative `ETH`
- Spillover signal: signal_k = skew[OTHER](k)  (other asset's near-ATM put-call skew)
- Signal: skew
- Target: realized_return_kurtosis — forward realized return kurtosis = m4 / m2**2 over the TARGET underlying's next H perp log returns (strictly after the decision at bar k, lr[k:k+h]); fourth standardized moment, transcribed verbatim from sealed EVAL-117/119/121/129
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar near-ATM put-call implied-vol skew of the OTHER underlying (e71.build_surface_bars skew), aligned to the common BTC-vs-ETH bar grid (build_cross_section), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(other_skew_z_k, own_kurt_k); directional permutation H1: IC>0 (wider other-asset near-ATM put-call skew -> fatter forward return tails on the target)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120 / min aligned common bars 200

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered composed floor (EVAL-71 both underlyings + alignment)

- Reuses the sealed EVAL-71 surface floor verbatim (min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s), applied to BOTH BTC and ETH, plus a cross-asset alignment floor (>= min_aligned_common_bars bar-ends where both underlyings carry a causal near-ATM put-call skew on the coarsest grid). Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min aligned common bars (coarsest grid): 200
- Min usable pairs per config: 120
