# EVAL_97_SINGLE_ASSET_SKEW_FORWARD_VOL_OF_VOL_PREREGISTRATION — skew -> forward vol-of-vol predictiveness

- Generated: `2026-11-18T11:38:11Z`
- Task: `EVAL97-SINGLE-ASSET-SKEW-FORWARD-VOL-OF-VOL`
- Extends: EVAL-71 (same skew surface signal and floor; different forward target: vol-of-vol vs RV)
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`

## Protocol
- Signal: causal per-bar near-ATM put-call skew skew (mean put iv - mean call iv over near-ATM option trades over the trailing window) from the real option trade tape, forward-filled and expanding-zscored end-of-bar k (reused e71.build_surface_bars/e71._forward_fill/e61.expanding_zscore)
- Bar grids (s): [60.0, 300.0]
- Horizons (bars): [6, 24, 72]
- Target: forward vol-of-vol = sqrt(mean((v_i - mean(v))^2)) where v_i = r_i^2 are squared log returns over bars k+1..k+H (reused e84._forward_vov; distinct from forward RV)
- Statistic: Spearman rank correlation IC = rho(signal_z_k, vov_forward_k); directional permutation H1: IC>0 (richer/more positive skew -> higher forward vol-of-vol)
- GO bar: GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Floor (reused verbatim from EVAL-71, not weakened)
```json
{
  "min_underlyings": 2,
  "min_option_trades_per_underlying": 1000,
  "min_near_atm_option_trades_per_underlying": 400,
  "min_perp_candles_per_underlying": 1000,
  "min_perp_span_seconds_per_underlying": 82000.0,
  "min_usable_pairs_per_config": 120,
  "note": "Reuses the sealed EVAL-71 trade-tape/surface floor verbatim (option trades / near-ATM trades / perp candles / span per underlying), applied to BOTH BTC and ETH; not weakened. No term-adequacy requirement (skew is a surface level). Below the floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor."
}
```
