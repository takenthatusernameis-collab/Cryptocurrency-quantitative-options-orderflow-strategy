# EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED — cross-sectional atm_iv basis (ETH - BTC) -> forward relative realized return skewness spread (Spearman rank IC)

- Generated: `2026-11-19T16:25:41Z`
- Task: `EVAL128-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional near-to-far ATM IV atm_iv basis (ETH - BTC) and the subsequent forward relative realized return skewness spread (skewness[ETH] - skewness[BTC]) on the real on-disk captures
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
| atm_iv | 60.0 | 6 | 1370 | 1364 | -0.0183 | 0.7443 | -0.0185 | -0.0840 | 0.0488 | False |
| atm_iv | 60.0 | 24 | 1370 | 1346 | -0.1342 | 1 | -0.1319 | -0.2048 | -0.0645 | False |
| atm_iv | 60.0 | 72 | 1370 | 1298 | -0.0445 | 0.9491 | -0.0431 | -0.1161 | 0.0306 | False |
| atm_iv | 300.0 | 6 | 274 | 268 | 0.0701 | 0.1369 | 0.0702 | -0.0739 | 0.2162 | False |
| atm_iv | 300.0 | 24 | 274 | 250 | -0.2957 | 1 | -0.2962 | -0.4291 | -0.1560 | False |
| atm_iv | 300.0 | 72 | 274 | 202 | -0.3602 | 1 | -0.3568 | -0.5142 | -0.1817 | False |

## Summary

- n_configs: 6
- n_pass: 0
- pass_configs: []
- best_ic: 0.0701
- best_config: atm_iv::bar300.0::h6

## Pooled

- BH-FDR rejected: []
- Any config pass: False
- Campaign state: EVAL_128_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD
