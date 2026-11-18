# EVAL_92_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VRP_SPREAD_COMBINED — cross-sectional near-ATM IV basis -> relative *VRP* spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T08:32:12Z`
- Task: `EVAL92-CROSS-SECTIONAL-ATM-IV-BASIS-RELATIVE-VRP-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional near-ATM IV basis (ETH - BTC) and the subsequent BTC-minus-ETH forward relative *VRP* spread (atm_iv - forward_RV) on the real on-disk captures
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
| atm_iv | 60 | 6 | 1364 | -0.9384 | 1.0000 | [-0.9383, -0.9490, -0.9242] | False |
| atm_iv | 300 | 6 | 268 | -0.9393 | 1.0000 | [-0.9394, -0.9579, -0.9105] | False |
| atm_iv | 60 | 24 | 1346 | -0.9401 | 1.0000 | [-0.9401, -0.9501, -0.9274] | False |
| atm_iv | 60 | 72 | 1298 | -0.9416 | 1.0000 | [-0.9413, -0.9519, -0.9295] | False |
| atm_iv | 300 | 24 | 250 | -0.9446 | 1.0000 | [-0.9443, -0.9616, -0.9162] | False |
| atm_iv | 300 | 72 | 202 | -0.9582 | 1.0000 | [-0.9574, -0.9714, -0.9345] | False |

## Pooled

- BH-FDR rejected: []
- Any config pass: False
- Campaign state: EVAL_92_CROSS_SECTIONAL_ATM_IV_BASIS_RELATIVE_VRP_SPREAD
