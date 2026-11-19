# EVAL_117_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_KURTOSIS_PREREGISTRATION — term_slope -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-19T04:30:17Z`
- Task: `EVAL117-SINGLE-ASSET-TERM-SLOPE-FORWARD-RETURN-KURTOSIS`
- Hypothesis: The causal near-to-far ATM implied-vol term slope (term_slope) has a positive monotone (Spearman rank) relationship with the subsequent forward realized return kurtosis (fourth standardized moment, tail fatness) of the same underlying, independent of any trading wrapper; tested on real on-disk captures at the EVAL-74 term floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-74/96/104/113 (same term_slope signal path and sealed EVAL-74 term floor) + EVAL-85/109/111/112 (same forward-window convention, fourth moment instead of third); distinct cell: single-asset term_slope -> forward realized return kurtosis

## Pre-declared protocol

- Signal: term_slope
- Target: realized_return_kurtosis — forward realized return kurtosis = m4 / m2**2 over the SAME underlying's next H perp log returns (strictly after the decision at bar k, lr[k:k+h]); fourth standardized moment (tail fatness)
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar near-to-far ATM IV term slope (e74._term_bars term_slope), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(term_slope_z_k, kurt_k); directional permutation H1: IC>0 (higher term slope -> fatter forward return tails)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered floor (EVAL-74 term floor, not the EVAL-64 ladder floor)

- Reuses the sealed EVAL-74 term floor verbatim (EVAL-71 surface floor: min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s + term adequacy: >= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with >= MIN_EXPIRY_TRADES trades each and >= MIN_BARS_WITH_TERM bars with a non-null term signal), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min usable pairs per config: 120
