# EVAL_104_SINGLE_ASSET_TERM_SLOPE_FORWARD_SIGNED_RETURN_PREREGISTRATION — term_slope -> forward signed return (Spearman rank IC)

- Generated: `2026-11-18T19:01:38Z`
- Task: `EVAL104-SINGLE-ASSET-TERM-SLOPE-FORWARD-SIGNED-RETURN`
- Hypothesis: The causal near-to-far ATM implied-vol term ratio (term_slope) has a positive monotone (Spearman rank) relationship with the subsequent forward signed log-return of the same underlying, independent of any trading wrapper; tested on real on-disk captures at the EVAL-74 term floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-74/100 (same term_slope signal path and sealed EVAL-74 term floor) + EVAL-81 (same forward signed log-return target); distinct cell: single-asset term_slope -> forward signed return mean

## Pre-declared protocol

- Signal: term_slope
- Target: signed_return — forward signed log-return = sum(log(close_i/close_{i-1})) over the SAME underlying's next H perp log returns (strictly after the decision at bar k), transcribed verbatim from sealed EVAL-81
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar near-to-far ATM IV term ratio (e74._term_bars term_slope), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(term_slope_z_k, signed_k); directional permutation H1: IC>0 (higher near/far ATM IV ratio -> more positive forward signed return)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered floor (EVAL-74 term floor, not the EVAL-64 ladder floor)

- Reuses the sealed EVAL-74 term floor verbatim (EVAL-71 surface floor: min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s + term adequacy: >= MIN_DISTINCT_EXPIRIES distinct near-ATM expiries with >= MIN_EXPIRY_TRADES trades each and >= MIN_BARS_WITH_TERM bars with a non-null term signal), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min usable pairs per config: 120
