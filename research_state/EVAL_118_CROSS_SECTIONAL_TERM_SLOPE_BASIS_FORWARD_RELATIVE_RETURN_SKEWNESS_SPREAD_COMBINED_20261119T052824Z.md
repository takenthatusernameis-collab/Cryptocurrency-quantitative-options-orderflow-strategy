# EVAL_118_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD_COMBINED — cross-sectional term-slope basis -> forward relative realized return skewness spread predictiveness (wrapper-free rank IC)

- Generated: `2026-11-19T05:28:24Z`
- Task: `EVAL118-CROSS-SECTIONAL-TERM-SLOPE-BASIS-FORWARD-RELATIVE-RETURN-SKEWNESS-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options term-slope basis (ETH - BTC near-to-far ATM IV term ratio) and the subsequent forward relative realized return skewness spread (ETH-minus-BTC forward return skewness spread) on the real on-disk captures
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
| term_slope | 60 | 24 | 1346 | 0.0646 | 0.0120 | [0.0659, -0.0072, 0.1344] | False |
| term_slope | 60 | 72 | 1298 | 0.0530 | 0.0290 | [0.0539, -0.0274, 0.1348] | False |
| term_slope | 300 | 6 | 268 | 0.0304 | 0.3157 | [0.0305, -0.1197, 0.1779] | False |
| term_slope | 60 | 6 | 1364 | 0.0090 | 0.3666 | [0.0123, -0.0585, 0.0796] | False |
| term_slope | 300 | 24 | 250 | -0.1447 | 0.9880 | [-0.1460, -0.3178, 0.0195] | False |
| term_slope | 300 | 72 | 202 | -0.3244 | 1.0000 | [-0.3243, -0.5237, -0.1150] | False |

## Pooled

- BH-FDR rejected: ['term_slope::bar60.0::h24', 'term_slope::bar60.0::h72']
- Any config pass: False
- Campaign state: EVAL_118_CROSS_SECTIONAL_TERM_SLOPE_BASIS_FORWARD_RELATIVE_RETURN_SKEWNESS_SPREAD
