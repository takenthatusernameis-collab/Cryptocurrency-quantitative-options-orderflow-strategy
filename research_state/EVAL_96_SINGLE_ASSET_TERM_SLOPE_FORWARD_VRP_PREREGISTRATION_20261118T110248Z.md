# EVAL_96_SINGLE_ASSET_TERM_SLOPE_FORWARD_VRP_PREREGISTRATION — term slope -> forward VRP predictiveness (Spearman rank IC)

- Generated: `2026-11-18T11:02:48Z`
- Task: `EVAL96-SINGLE-ASSET-TERM-SLOPE-FORWARD-VRP`
- Hypothesis: The causal near-minus-far ATM implied-vol term slope (term_slope) has a positive monotone (Spearman rank) relationship with subsequent forward variance risk premium (implied vol - forward realized vol) of the same underlying, independent of any trading wrapper; tested on real on-disk captures at the composed EVAL-74 term floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-74 (same term_slope signal and sealed term floor) + EVAL-86 (same forward VRP target); distinct cell: term slope -> forward VRP

## Pre-declared protocol

- Signal: term_slope
- Target: forward_vrp — forward VRP = atm_iv_k - forward_RV_{k+1..k+H}, forward_RV = e71._forward_rv = sqrt(mean(r^2)) (reused e86._forward_vrp verbatim)
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar near-minus-far ATM IV term slope (EVAL-74 _term_bars: IV(near expiry)-IV(far expiry) in vol points), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill/e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(signal_z_k, forward_vrp_k); directional permutation H1: IC>0 (steeper near-minus-far slope -> richer forward VRP)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 100

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered floor (EVAL-74 term floor, not the EVAL-64 ladder floor)

- Reuses the sealed EVAL-74 term floor verbatim (EVAL-71 surface floor: min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s + term adequacy: >= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with >= MIN_EXPIRY_TRADES trades each and >= MIN_BARS_WITH_TERM bars with a non-null term signal), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min usable pairs per config: 100
