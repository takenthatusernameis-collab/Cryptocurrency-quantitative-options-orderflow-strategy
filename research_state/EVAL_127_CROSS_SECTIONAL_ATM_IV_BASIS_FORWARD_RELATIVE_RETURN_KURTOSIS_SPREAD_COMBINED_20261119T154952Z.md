# EVAL_127_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_COMBINED — cross-sectional atm_iv basis (ETH - BTC) -> forward relative realized return kurtosis spread (Spearman rank IC)

- Generated: `2026-11-19T15:49:52Z`
- Task: `EVAL127-CROSS-SECTIONAL-ATM-IV-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional near-to-far ATM IV atm_iv basis (ETH - BTC) and the subsequent forward relative realized return kurtosis spread (kurtosis[ETH] - kurtosis[BTC]) on the real on-disk captures
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
| atm_iv | 60.0 | 6 | 1370 | 1364 | 0.0267 | 0.1508 | 0.0286 | -0.0387 | 0.0947 | False |
| atm_iv | 60.0 | 24 | 1370 | 1346 | 0.0289 | 0.1588 | 0.0284 | -0.0434 | 0.1033 | False |
| atm_iv | 60.0 | 72 | 1370 | 1298 | 0.0710 | 0.005994 | 0.0708 | 0.0013 | 0.1445 | True |
| atm_iv | 300.0 | 6 | 274 | 268 | 0.0934 | 0.06893 | 0.0903 | -0.0470 | 0.2205 | False |
| atm_iv | 300.0 | 24 | 274 | 250 | 0.0029 | 0.4585 | 0.0000 | -0.1507 | 0.1550 | False |
| atm_iv | 300.0 | 72 | 274 | 202 | -0.2174 | 1 | -0.2209 | -0.3975 | -0.0460 | False |

## Summary

- n_configs: 6
- n_pass: 1
- pass_configs: ['atm_iv::bar60.0::h72']
- best_ic: 0.0934
- best_config: atm_iv::bar300.0::h6

## Pooled

- BH-FDR rejected: ['atm_iv::bar60.0::h72']
- Any config pass: True
- Campaign state: EVAL_127_CROSS_SECTIONAL_ATM_IV_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD
