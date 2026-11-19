# EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED — cross-sectional term-ratio basis (ETH - BTC) -> forward relative realized return skewness spread (Spearman rank IC)

- Generated: `2026-11-19T06:16:07Z`
- Task: `EVAL120-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-RETURN-SKEWNESS-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options implied-vol term-ratio basis (ETH - BTC near-to-far ATM IV term ratio) and the subsequent forward relative realized return skewness spread on the real on-disk captures
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
| term_ratio | 60.0 | 6 | 1370 | 1364 | 0.0350 | 0.1059 | 0.0377 | -0.0324 | 0.1043 | False |
| term_ratio | 60.0 | 24 | 1370 | 1346 | 0.0834 | 0.001998 | 0.0845 | 0.0056 | 0.1586 | True |
| term_ratio | 60.0 | 72 | 1370 | 1298 | 0.0722 | 0.008991 | 0.0741 | -0.0153 | 0.1593 | False |
| term_ratio | 300.0 | 6 | 274 | 268 | 0.0118 | 0.4366 | 0.0142 | -0.1407 | 0.1554 | False |
| term_ratio | 300.0 | 24 | 274 | 250 | -0.0819 | 0.8961 | -0.0852 | -0.2733 | 0.1040 | False |
| term_ratio | 300.0 | 72 | 274 | 202 | -0.1765 | 0.994 | -0.1695 | -0.4185 | 0.0587 | False |

## Summary

- n_configs: 6
- n_pass: 1
- pass_configs: ['term_ratio::bar60.0::h24']
- best_ic: 0.0834
- best_config: term_ratio::bar60.0::h24

## Pooled

- BH-FDR rejected: ['term_ratio::bar60.0::h24', 'term_ratio::bar60.0::h72']
- Any config pass: True
- Campaign state: EVAL_120_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RETURN_SKEWNESS_SPREAD
