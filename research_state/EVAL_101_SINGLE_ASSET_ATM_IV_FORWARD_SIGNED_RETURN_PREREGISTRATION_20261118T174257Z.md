# EVAL_101_SINGLE_ASSET_ATM_IV_FORWARD_SIGNED_RETURN_PREREGISTRATION — atm_iv -> forward signed return (Spearman rank IC)

- Generated: `2026-11-18T17:42:57Z`
- Task: `EVAL101-SINGLE-ASSET-ATM-IV-FORWARD-SIGNED-RETURN`
- Hypothesis: The causal near-ATM implied-vol level (atm_iv) has a positive monotone (Spearman rank) relationship with the subsequent forward signed log-return of the same underlying, independent of any trading wrapper; tested on real on-disk captures at the EVAL-71 surface floor.
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`
- Extends: EVAL-71/87 (same atm_iv signal path and sealed EVAL-71 surface floor) + EVAL-81 (same forward signed log-return target); distinct cell: single-asset atm_iv level -> forward signed return mean

## Pre-declared protocol

- Signal: atm_iv
- Target: signed_return — forward signed log-return = sum(log(close_i/close_{i-1})) over the SAME underlying's next H perp log returns (strictly after the decision at bar k), transcribed verbatim from sealed EVAL-81
- Bar grid (s): [60.0, 300.0]
- Forward horizons (bars): [6, 24, 72]
- Signal detail: causal per-bar near-ATM implied-vol level (e71.build_surface_bars atm_iv), forward-filled and expanding-zscored end-of-bar k (reused e71._forward_fill / e61.expanding_zscore)
- Statistic: Spearman rank correlation IC = rho(atm_iv_z_k, signed_k); directional permutation H1: IC>0 (higher near-ATM IV -> more positive forward signed return)
- Stats: perm 1000 / bootstrap 1000 block 2 / BH-FDR alpha 0.1 / seed 42 / zwindow 20 / min usable pairs 120

## Pre-declared GO bar

GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Pre-registered floor (EVAL-71 surface floor, not the EVAL-64 ladder floor)

- Reuses the sealed EVAL-71 surface floor verbatim (min_option_trades_per_underlying=1000, min_near_atm_option_trades_per_underlying=400, min_perp_candles_per_underlying=1000, min_perp_span_seconds_per_underlying=82000s), applied to BOTH BTC and ETH. Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor.
- Min underlyings: 2
- Min usable pairs per config: 120
