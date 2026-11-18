# EVAL_91_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED — cross-sectional put-call SKEW basis -> relative *vol-of-vol* spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T05:46:42Z`
- Task: `EVAL91-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VOL-OF-VOL-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional put-call SKEW basis (ETH - BTC) and the subsequent BTC-minus-ETH forward relative *vol-of-vol* spread (std of squared log returns) on the real on-disk captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}

## Per-underlying EVAL-71 floor

| underlying | surface floor ok | option trades | near-ATM | perp candles | ok |
|---|---|---|---|---|---|
| BTC | True | 2748 | 2331 | 1441 | True |
| ETH | True | 3547 | 1509 | 1441 | True |

## Configs (best first by Spearman IC)

| signal | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|
| skew | 300 | 72 | 202 | 0.2156 | 0.0010 | [0.2220, 0.0385, 0.3768] | True |
| skew | 300 | 6 | 268 | 0.0827 | 0.0899 | [0.0880, -0.0695, 0.2362] | False |
| skew | 60 | 72 | 1298 | 0.0217 | 0.2318 | [0.0183, -0.0537, 0.1005] | False |
| skew | 60 | 6 | 1364 | 0.0067 | 0.4046 | [0.0050, -0.0650, 0.0742] | False |
| skew | 60 | 24 | 1346 | 0.0057 | 0.4186 | [0.0034, -0.0673, 0.0723] | False |
| skew | 300 | 24 | 250 | -0.1411 | 0.9900 | [-0.1443, -0.3132, 0.0323] | False |

## Pooled

- BH-FDR rejected: ['skew::bar300.0::h72']
- Any config pass: True
- Campaign state: EVAL_91_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VOL_OF_VOL_SPREAD
