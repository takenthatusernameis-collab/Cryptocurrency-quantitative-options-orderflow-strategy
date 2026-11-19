# EVAL_126_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD_COMBINED — cross-sectional term-slope basis -> forward relative realized return kurtosis spread predictiveness (wrapper-free rank IC)

- Generated: `2026-11-19T14:47:15Z`
- Task: `EVAL126-CROSS-SECTIONAL-TERM-SLOPE-BASIS-FORWARD-RELATIVE-RETURN-KURTOSIS-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options term-slope basis (ETH - BTC near-to-far ATM IV term slope) and the subsequent forward relative realized return kurtosis spread (ETH-minus-BTC forward return kurtosis spread) on the real on-disk captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}

## Per-underlying floor (EVAL-71 surface floor + term-structure adequacy)

| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |
|---|---|---|---|---|
| BTC | True | 8 | 557 | True |
| ETH | True | 8 | 329 | True |

## Configs (best first by Spearman IC)

| signal | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|
| term_slope | 300 | 72 | 202 | 0.3333 | 0.0010 | [0.3292, 0.1344, 0.4989] | True |
| term_slope | 300 | 24 | 250 | 0.2889 | 0.0010 | [0.2861, 0.1262, 0.4237] | True |
| term_slope | 300 | 6 | 268 | 0.0885 | 0.0649 | [0.0872, -0.0564, 0.2259] | False |
| term_slope | 60 | 6 | 1364 | 0.0014 | 0.4825 | [0.0030, -0.0671, 0.0707] | False |
| term_slope | 60 | 24 | 1346 | -0.0674 | 0.9950 | [-0.0658, -0.1443, 0.0077] | False |
| term_slope | 60 | 72 | 1298 | -0.1475 | 1.0000 | [-0.1458, -0.2230, -0.0747] | False |

## Pooled

- BH-FDR rejected: ['term_slope::bar300.0::h24', 'term_slope::bar300.0::h72']
- Any config pass: True
- Campaign state: EVAL_126_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_KURTOSIS_SPREAD
