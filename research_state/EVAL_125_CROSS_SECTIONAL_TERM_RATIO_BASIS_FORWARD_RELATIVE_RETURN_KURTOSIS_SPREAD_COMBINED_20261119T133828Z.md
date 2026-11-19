# EVAL_125_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_COMBINED — cross-sectional term-ratio basis (ETH - BTC) -> forward relative realized return kurtosis spread (Spearman rank IC)

- Generated: `2026-11-19T13:38:28Z`
- Task: `EVAL125-CROSS-SECTIONAL-TERM-RATIO-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional near-to-far ATM IV term-ratio basis (ETH - BTC) and the subsequent forward relative realized return kurtosis spread (kurtosis[ETH] - kurtosis[BTC]) on the real on-disk captures
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
| term_ratio | 60.0 | 6 | 1370 | 1364 | 0.0129 | 0.3227 | 0.0155 | -0.0564 | 0.0787 | False |
| term_ratio | 60.0 | 24 | 1370 | 1346 | -0.0439 | 0.953 | -0.0413 | -0.1177 | 0.0283 | False |
| term_ratio | 60.0 | 72 | 1370 | 1298 | -0.1990 | 1 | -0.1973 | -0.2778 | -0.1272 | False |
| term_ratio | 300.0 | 6 | 274 | 268 | 0.0729 | 0.1159 | 0.0722 | -0.0640 | 0.2022 | False |
| term_ratio | 300.0 | 24 | 274 | 250 | 0.3650 | 0.000999 | 0.3619 | 0.2127 | 0.4878 | True |
| term_ratio | 300.0 | 72 | 274 | 202 | 0.4128 | 0.000999 | 0.4094 | 0.1881 | 0.5791 | True |

## Summary

- n_configs: 6
- n_pass: 2
- pass_configs: ['term_ratio::bar300.0::h24', 'term_ratio::bar300.0::h72']
- best_ic: 0.4128
- best_config: term_ratio::bar300.0::h72

## Pooled

- BH-FDR rejected: ['term_ratio::bar300.0::h24', 'term_ratio::bar300.0::h72']
- Any config pass: True
- Campaign state: EVAL_125_CROSS_SECTIONAL_TERM_RATIO_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD
