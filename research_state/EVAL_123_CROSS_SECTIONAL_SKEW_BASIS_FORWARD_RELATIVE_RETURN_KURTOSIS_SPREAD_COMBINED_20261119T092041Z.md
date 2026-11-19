# EVAL_123_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_COMBINED — cross-sectional skew basis (ETH - BTC) -> forward relative realized return kurtosis spread (Spearman rank IC)

- Generated: `2026-11-19T09:20:41Z`
- Task: `EVAL123-CROSS-SECTIONAL-SKEW-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional put-call skew basis (ETH - BTC near-ATM surface) and the subsequent forward relative realized return kurtosis spread (kurtosis[ETH] - kurtosis[BTC]) on the real on-disk captures
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
| skew | 60.0 | 6 | 1370 | 1364 | 0.1022 | 0.000999 | 0.1029 | 0.0320 | 0.1727 | True |
| skew | 60.0 | 24 | 1370 | 1346 | 0.1425 | 0.000999 | 0.1454 | 0.0723 | 0.2153 | True |
| skew | 60.0 | 72 | 1370 | 1298 | 0.1153 | 0.000999 | 0.1188 | 0.0436 | 0.1871 | True |
| skew | 300.0 | 6 | 274 | 268 | -0.0304 | 0.7023 | -0.0333 | -0.1756 | 0.1095 | False |
| skew | 300.0 | 24 | 274 | 250 | 0.1237 | 0.02797 | 0.1202 | -0.0446 | 0.2706 | False |
| skew | 300.0 | 72 | 274 | 202 | -0.2130 | 0.997 | -0.2180 | -0.3778 | -0.0434 | False |

## Summary

- n_configs: 6
- n_pass: 3
- pass_configs: ['skew::bar60.0::h6', 'skew::bar60.0::h24', 'skew::bar60.0::h72']
- best_ic: 0.1425
- best_config: skew::bar60.0::h24

## Pooled

- BH-FDR rejected: ['skew::bar60.0::h6', 'skew::bar60.0::h24', 'skew::bar60.0::h72', 'skew::bar300.0::h24']
- Any config pass: True
- Campaign state: EVAL_123_CROSS_SECTIONAL_SKEW_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD
