# EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS_COMBINED — options order-flow x cross-sectional IV basis -> realized-vol predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-17T12:32:44Z`
- Task: `EVAL79-OFLOW-X-CROSS-SECTIONAL-BASIS-RV-PREDICTIVENESS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying composed floor

| underlying | surface floor ok | n option trades | n oflow states | oflow ok | ok |
|---|---|---|---|---|---|
| BTC | True | 2748 | 289 | True | True |
| ETH | True | 3547 | 289 | True | True |

## Cross-sectional alignment

- Aligned common bars on coarsest grid (300s): 274 (floor >= 200)
- Aligned ok: True

## Configs (best first by pooled Spearman IC)

| basis signal | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|
| skew | 60 | 72 | 548 | 0.0966 | 0.0110 | [0.1000, 0.0093, 0.1922] | True |
| skew | 60 | 24 | 548 | 0.0926 | 0.0140 | [0.0952, 0.0070, 0.1823] | True |
| atm_iv | 60 | 24 | 548 | 0.0538 | 0.1079 | [0.0577, -0.0266, 0.1442] | False |
| atm_iv | 60 | 6 | 548 | 0.0496 | 0.1119 | [0.0531, -0.0430, 0.1350] | False |
| skew | 60 | 6 | 548 | 0.0462 | 0.1289 | [0.0495, -0.0378, 0.1374] | False |
| atm_iv | 60 | 72 | 548 | 0.0339 | 0.2078 | [0.0362, -0.0555, 0.1256] | False |
| skew | 300 | 72 | 404 | -0.0107 | 0.5834 | [-0.0110, -0.1185, 0.0859] | False |
| atm_iv | 300 | 6 | 536 | -0.0355 | 0.8072 | [-0.0339, -0.1303, 0.0489] | False |
| skew | 300 | 6 | 536 | -0.0473 | 0.8741 | [-0.0426, -0.1329, 0.0398] | False |
| atm_iv | 300 | 24 | 500 | -0.0477 | 0.8212 | [-0.0429, -0.1340, 0.0459] | False |
| skew | 300 | 24 | 500 | -0.0490 | 0.8541 | [-0.0483, -0.1294, 0.0383] | False |
| atm_iv | 300 | 72 | 404 | -0.1033 | 0.9820 | [-0.1020, -0.2007, -0.0025] | False |

## Pooled

- BH-FDR rejected: ['basis[skew]::bar60.0::h24']
- Any config pass (both underlyings): False
- Campaign state: EVAL_79_OFLOW_X_CROSS_SECTIONAL_BASIS_RV_PREDICTIVENESS
