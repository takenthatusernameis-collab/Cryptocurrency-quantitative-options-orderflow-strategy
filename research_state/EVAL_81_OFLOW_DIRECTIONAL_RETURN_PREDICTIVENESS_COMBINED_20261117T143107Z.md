# EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS_COMBINED — options order-flow imbalance -> subsequent signed (directional) return predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-17T14:31:07Z`
- Task: `EVAL81-OFLOW-DIRECTIONAL-RETURN-PREDICTIVENESS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying composed floor

| underlying | surface floor ok | n option trades | n oflow states | oflow ok | ok |
|---|---|---|---|---|---|
| BTC | True | 2748 | 289 | True | True |
| ETH | True | 3547 | 289 | True | True |

## Configs (best first by Spearman IC)

| underlying | signal | target | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|---|---|
| BTC | imbalance | signed_return | 60 | 24 | 264 | 0.0823 | 0.0959 | [0.0856, -0.0518, 0.2146] | False |
| BTC | imbalance | signed_return | 300 | 72 | 217 | 0.0510 | 0.2338 | [0.0508, -0.0776, 0.1813] | False |
| ETH | imbalance | signed_return | 60 | 6 | 283 | 0.0444 | 0.2368 | [0.0485, -0.0714, 0.1715] | False |
| BTC | imbalance | signed_return | 300 | 24 | 265 | 0.0074 | 0.4725 | [0.0060, -0.1224, 0.1448] | False |
| ETH | imbalance | signed_return | 300 | 6 | 283 | -0.0437 | 0.7862 | [-0.0475, -0.1716, 0.0708] | False |
| BTC | imbalance | signed_return | 300 | 6 | 283 | -0.0495 | 0.8132 | [-0.0517, -0.1702, 0.0650] | False |
| BTC | imbalance | signed_return | 60 | 6 | 282 | -0.0548 | 0.8152 | [-0.0551, -0.1848, 0.0667] | False |
| BTC | imbalance | signed_return | 60 | 72 | 216 | -0.0634 | 0.8112 | [-0.0642, -0.2134, 0.0862] | False |
| ETH | imbalance | signed_return | 60 | 72 | 217 | -0.1076 | 0.9291 | [-0.1063, -0.2460, 0.0258] | False |
| ETH | imbalance | signed_return | 60 | 24 | 265 | -0.1222 | 0.9770 | [-0.1226, -0.2524, 0.0044] | False |
| ETH | imbalance | signed_return | 300 | 72 | 217 | -0.1351 | 0.9740 | [-0.1330, -0.2653, 0.0071] | False |
| ETH | imbalance | signed_return | 300 | 24 | 265 | -0.2341 | 1.0000 | [-0.2318, -0.3574, -0.0983] | False |

## Per-underlying

| underlying | n_configs | best IC | best config | n_pass | any_pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.0823 | imbalance::signed_return::bar60.0::h24 | 0 | False |
| ETH | 6 | 0.0444 | imbalance::signed_return::bar60.0::h6 | 0 | False |

## Pooled

- BH-FDR rejected: []
- Any config pass (all underlyings): False
- Campaign state: EVAL_81_OFLOW_DIRECTIONAL_RETURN_PREDICTIVENESS
