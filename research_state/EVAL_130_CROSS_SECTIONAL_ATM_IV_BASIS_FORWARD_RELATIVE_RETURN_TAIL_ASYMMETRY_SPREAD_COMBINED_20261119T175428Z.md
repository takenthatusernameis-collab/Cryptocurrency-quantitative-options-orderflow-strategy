# EVAL_130_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD_COMBINED — cross-sectional atm_iv basis (ETH - BTC) -> forward relative realized return tail-asymmetry spread (Spearman rank IC)

- Generated: `2026-11-19T17:54:28Z`
- Task: `EVAL130-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-TAIL-ASYMMETRY-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional near-to-far ATM IV atm_iv basis (ETH - BTC) and the subsequent forward relative realized return tail-asymmetry spread (tail_asym_BTC - tail_asym_ETH) on the real on-disk captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | surface_floor_ok | n option trades | n near-ATM | n perp candles | span (s) | ok |
|---|---|---|---|---|---|---|
| BTC | True | 2748 | 2331 | 1441 | 86400.0 | True |
| ETH | True | 3547 | 1509 | 1441 | 86400.0 | True |

## Alignment

- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}
- Aligned common bars binding (coarsest grid): 274
- Aligned OK: True | Underlyings OK: True

## Per-config (best by Spearman IC)

| signal | bar_seconds | horizon_bars | n_common | n_pairs | IC | perm_p | CI lo | CI hi | pass |
|---|---|---|---|---|---|---|---|---|---|
| atm_iv | 60.0 | 6 | 1370 | 1364 | 0.0096 | 0.3626 | 0.0091 | -0.0579 | 0.0759 | False |
| atm_iv | 60.0 | 24 | 1370 | 1346 | -0.0115 | 0.6683 | -0.0109 | -0.0821 | 0.0594 | False |
| atm_iv | 60.0 | 72 | 1370 | 1298 | -0.0390 | 0.9131 | -0.0366 | -0.1116 | 0.0353 | False |
| atm_iv | 300.0 | 6 | 274 | 268 | -0.0255 | 0.6613 | -0.0231 | -0.1625 | 0.1213 | False |
| atm_iv | 300.0 | 24 | 274 | 250 | 0.1281 | 0.02897 | 0.1413 | -0.0319 | 0.2967 | False |
| atm_iv | 300.0 | 72 | 274 | 202 | -0.0220 | 0.6194 | -0.0158 | -0.2091 | 0.1705 | False |

## Summary

- n_configs: 6
- n_pass: 0
- pass_configs: []
- best_ic: 0.1281
- best_config: atm_iv::bar300.0::h24

## Pooled

- BH-FDR rejected: []
- Any config pass: False
- Campaign state: EVAL_130_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_TAIL_ASYMMETRY_SPREAD
