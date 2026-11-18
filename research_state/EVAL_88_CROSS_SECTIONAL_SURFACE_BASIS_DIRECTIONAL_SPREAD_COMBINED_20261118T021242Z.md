# EVAL_88_CROSS_SECTIONAL_SURFACE_BASIS_DIRECTIONAL_SPREAD_COMBINED — cross-sectional options implied-vol surface basis -> relative *direction* predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T02:12:42Z`
- Task: `EVAL88-CROSS-SECTIONAL-SURFACE-BASIS-DIRECTIONAL-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options implied-vol basis (ETH - BTC near-ATM IV / skew) and the subsequent BTC-minus-ETH forward *signed return spread* (relative direction) on the real on-disk captures
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
| atm_iv | 60 | 6 | 1364 | 0.1087 | 0.0010 | [0.1075, 0.0394, 0.1730] | True |
| atm_iv | 300 | 24 | 250 | 0.0832 | 0.0979 | [0.0866, -0.0732, 0.2266] | False |
| atm_iv | 60 | 24 | 1346 | 0.0380 | 0.0809 | [0.0362, -0.0328, 0.1045] | False |
| atm_iv | 60 | 72 | 1298 | 0.0183 | 0.2507 | [0.0180, -0.0450, 0.0874] | False |
| atm_iv | 300 | 6 | 268 | 0.0111 | 0.3996 | [0.0087, -0.1332, 0.1542] | False |
| skew | 60 | 6 | 1364 | -0.0504 | 0.9640 | [-0.0504, -0.1185, 0.0182] | False |
| skew | 60 | 72 | 1298 | -0.0574 | 0.9850 | [-0.0569, -0.1347, 0.0170] | False |
| atm_iv | 300 | 72 | 202 | -0.0597 | 0.7882 | [-0.0626, -0.2418, 0.1077] | False |
| skew | 300 | 72 | 202 | -0.0684 | 0.8302 | [-0.0775, -0.2720, 0.1012] | False |
| skew | 300 | 6 | 268 | -0.1435 | 0.9890 | [-0.1398, -0.2866, -0.0070] | False |
| skew | 300 | 24 | 250 | -0.1864 | 1.0000 | [-0.1816, -0.3404, -0.0134] | False |
| skew | 60 | 24 | 1346 | -0.1946 | 1.0000 | [-0.1946, -0.2617, -0.1300] | False |

## Pooled

- BH-FDR rejected: ['atm_iv::bar60.0::h6']
- Any config pass: True
- Campaign state: EVAL_88_CROSS_SECTIONAL_SURFACE_BASIS_DIRECTIONAL_SPREAD
