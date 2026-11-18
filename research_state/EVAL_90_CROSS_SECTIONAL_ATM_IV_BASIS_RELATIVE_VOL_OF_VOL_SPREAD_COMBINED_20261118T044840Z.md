# EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED — cross-sectional near-ATM IV basis -> relative *vol-of-vol* spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T04:48:40Z`
- Task: `EVAL90-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VOL-OF-VOL-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional near-ATM IV basis (ETH - BTC) and the subsequent BTC-minus-ETH forward relative *vol-of-vol* spread (std of squared log returns) on the real on-disk captures
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
| atm_iv | 300 | 72 | 202 | 0.3222 | 0.0010 | [0.3260, 0.1354, 0.4920] | True |
| atm_iv | 300 | 6 | 268 | 0.1178 | 0.0210 | [0.1224, -0.0362, 0.2700] | False |
| atm_iv | 60 | 72 | 1298 | 0.1027 | 0.0010 | [0.1035, 0.0251, 0.1802] | True |
| atm_iv | 60 | 24 | 1346 | 0.0314 | 0.1309 | [0.0319, -0.0449, 0.1029] | False |
| atm_iv | 300 | 24 | 250 | 0.0314 | 0.3147 | [0.0332, -0.1195, 0.1771] | False |
| atm_iv | 60 | 6 | 1364 | -0.0266 | 0.8342 | [-0.0281, -0.0928, 0.0425] | False |

## Pooled

- BH-FDR rejected: ['atm_iv::bar60.0::h72', 'atm_iv::bar300.0::h72', 'atm_iv::bar300.0::h6']
- Any config pass: True
- Campaign state: EVAL_90_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VOL_OF_VOL_SPREAD
