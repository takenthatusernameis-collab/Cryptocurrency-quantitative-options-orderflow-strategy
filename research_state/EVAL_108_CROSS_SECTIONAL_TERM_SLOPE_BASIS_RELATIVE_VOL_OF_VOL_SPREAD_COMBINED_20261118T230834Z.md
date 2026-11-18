# EVAL_108_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED — cross-sectional term-slope basis -> relative vol-of-vol spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T23:08:34Z`
- Task: `EVAL108-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-VOL-OF-VOL-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options term-slope basis (ETH - BTC near-to-far ATM IV term slope) and the subsequent BTC-minus-ETH forward relative *vol-of-vol* spread on the real on-disk captures
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
| term_slope | 60 | 24 | 1346 | 0.0497 | 0.0380 | [0.0488, -0.0363, 0.1340] | False |
| term_slope | 60 | 72 | 1298 | 0.0253 | 0.1808 | [0.0235, -0.0512, 0.1035] | False |
| term_slope | 60 | 6 | 1364 | -0.0088 | 0.6384 | [-0.0121, -0.0919, 0.0654] | False |
| term_slope | 300 | 72 | 202 | -0.0828 | 0.8821 | [-0.0831, -0.2929, 0.1212] | False |
| term_slope | 300 | 6 | 268 | -0.2816 | 1.0000 | [-0.2803, -0.4077, -0.1467] | False |
| term_slope | 300 | 24 | 250 | -0.3623 | 1.0000 | [-0.3568, -0.4936, -0.2166] | False |

## Pooled

- BH-FDR rejected: []
- Any config pass: False
- Campaign state: EVAL_108_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_VOL_OF_VOL_SPREAD
