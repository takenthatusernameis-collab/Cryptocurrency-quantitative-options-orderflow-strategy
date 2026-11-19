# EVAL_116_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED — cross-sectional skew basis (ETH - BTC) -> forward relative realized return skewness spread (Spearman rank IC)

- Generated: `2026-11-19T03:25:48Z`
- Task: `EVAL116-CROSS-SECTIONAL-SKEW-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional put-call skew basis (ETH - BTC near-ATM surface) and the subsequent forward relative realized return skewness spread on the real on-disk captures
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
| skew | 60.0 | 6 | 1370 | 1364 | -0.0145 | 0.7083 | -0.0151 | -0.0812 | 0.0562 | False |
| skew | 60.0 | 24 | 1370 | 1346 | 0.0392 | 0.08192 | 0.0412 | -0.0307 | 0.1170 | False |
| skew | 60.0 | 72 | 1370 | 1298 | 0.1543 | 0.000999 | 0.1552 | 0.0863 | 0.2174 | True |
| skew | 300.0 | 6 | 274 | 268 | -0.0161 | 0.5994 | -0.0164 | -0.1656 | 0.1278 | False |
| skew | 300.0 | 24 | 274 | 250 | -0.2291 | 1 | -0.2351 | -0.3783 | -0.0718 | False |
| skew | 300.0 | 72 | 274 | 202 | -0.2903 | 1 | -0.2880 | -0.4504 | -0.1125 | False |

## Summary

- n_configs: 6
- n_pass: 1
- pass_configs: ['skew::bar60.0::h72']
- best_ic: 0.1543
- best_config: skew::bar60.0::h72

## Pooled

- BH-FDR rejected: ['skew::bar60.0::h72']
- Any config pass: True
- Campaign state: EVAL_116_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD
