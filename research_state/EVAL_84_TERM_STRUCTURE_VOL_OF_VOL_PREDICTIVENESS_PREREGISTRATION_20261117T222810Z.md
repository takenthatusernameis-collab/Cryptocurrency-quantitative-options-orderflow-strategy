# EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_PREREGISTRATION — term structure -> forward vol-of-vol predictiveness

- Generated: `2026-11-17T22:28:10Z`
- Task: `EVAL84-TERM-STRUCTURE-VOL-OF-VOL-PREDICTIVENESS`
- Extends: EVAL-74 (same term-structure signal and floor; different forward target: vol-of-vol vs RV)
- Capture dir: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval61`

## Protocol
- Term signals: ['term_slope', 'term_ratio']
- Bar grids (s): [60.0, 300.0]
- Horizons (bars): [6, 24, 72]
- Target: forward vol-of-vol = sqrt(mean((v_i - mean(v))^2)) where v_i = r_i^2 are squared log returns over bars k+1..k+H (distinct from forward RV)
- Statistic: Spearman rank correlation IC = rho(signal_z_k, vov_forward_k); directional permutation H1: IC>0 (steeper near-minus-far slope -> higher forward vol-of-vol)
- GO bar: GO only if, on BOTH BTC and ETH and at least one config, Spearman IC > 0, directional permutation p < 0.05, block-bootstrap 95% CI lower > 0, and pooled BH-FDR rejects that config; else NO-GO CONFIRMED (PASS).

## Floor (composed, not weakened)
```json
{
  "min_underlyings": 2,
  "min_option_trades": 2000,
  "min_near_atm_trades": 200,
  "min_distinct_expiries": 2,
  "min_expiry_trades": 5,
  "min_bars_with_term": 40,
  "min_usable_pairs_per_config": 100,
  "note": "Composes the sealed EVAL-71 trade-tape/surface floor for each underlying (reused verbatim, not weakened) with the EVAL-74 term-structure adequacy floor (>= min_distinct_expiries distinct near-ATM expiries with >= min_expiry_trades trades each, and >= min_bars_with_term bars carrying a non-null term signal). Below the composed floor the campaign seals BLOCKED, never NO-GO. This is NOT the EVAL-64 ladder floor."
}
```
