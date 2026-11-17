# EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION_COMBINED — options order-flow x implied-vol surface interaction -> realized-vol predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-17T12:08:46Z`
- Task: `EVAL78-OFLOW-X-SURFACE-RV-INTERACTION`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying composed floor

| underlying | surface floor ok | n option trades | n oflow states | oflow ok | ok |
|---|---|---|---|---|---|
| BTC | True | 2748 | 289 | True | True |
| ETH | True | 3547 | 289 | True | True |

## Configs (best first by Spearman IC)

| underlying | interaction | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|---|
| BTC | oflow[imbalance]_x_skew | 300 | 72 | 217 | 0.1764 | 0.0060 | [0.1805, 0.0502, 0.3116] | True |
| BTC | oflow[imbalance]_x_skew | 300 | 6 | 283 | 0.0971 | 0.0629 | [0.1003, -0.0224, 0.2178] | False |
| BTC | oflow[imbalance]_x_skew | 60 | 6 | 282 | 0.0738 | 0.1079 | [0.0736, -0.0339, 0.1863] | False |
| BTC | oflow[imbalance]_x_skew | 300 | 24 | 265 | 0.0468 | 0.2328 | [0.0470, -0.0758, 0.1695] | False |
| ETH | oflow[imbalance]_x_skew | 300 | 72 | 217 | 0.0247 | 0.3866 | [0.0262, -0.1195, 0.1900] | False |
| BTC | oflow[imbalance]_x_skew | 60 | 72 | 216 | 0.0079 | 0.4346 | [0.0132, -0.1431, 0.1539] | False |
| BTC | oflow[imbalance]_x_atm_iv | 60 | 72 | 216 | 0.0043 | 0.4815 | [0.0074, -0.1544, 0.1580] | False |
| ETH | oflow[imbalance]_x_atm_iv | 300 | 6 | 283 | 0.0013 | 0.4795 | [0.0012, -0.1396, 0.1178] | False |
| BTC | oflow[imbalance]_x_skew | 60 | 24 | 264 | -0.0020 | 0.5245 | [-0.0008, -0.1350, 0.1234] | False |
| ETH | oflow[imbalance]_x_atm_iv | 300 | 24 | 265 | -0.0160 | 0.5964 | [-0.0198, -0.1443, 0.1143] | False |
| ETH | oflow[imbalance]_x_skew | 60 | 6 | 283 | -0.0283 | 0.6693 | [-0.0313, -0.1435, 0.0776] | False |
| ETH | oflow[imbalance]_x_skew | 60 | 72 | 217 | -0.0348 | 0.6873 | [-0.0301, -0.1662, 0.1118] | False |
| BTC | oflow[imbalance]_x_atm_iv | 300 | 6 | 283 | -0.0643 | 0.8631 | [-0.0589, -0.1848, 0.0587] | False |
| ETH | oflow[imbalance]_x_atm_iv | 300 | 72 | 217 | -0.0686 | 0.8641 | [-0.0685, -0.2228, 0.0868] | False |
| ETH | oflow[imbalance]_x_skew | 300 | 24 | 265 | -0.0744 | 0.8791 | [-0.0749, -0.2067, 0.0550] | False |
| ETH | oflow[imbalance]_x_atm_iv | 60 | 24 | 265 | -0.0758 | 0.8991 | [-0.0756, -0.2125, 0.0566] | False |
| BTC | oflow[imbalance]_x_atm_iv | 300 | 24 | 265 | -0.0809 | 0.8971 | [-0.0781, -0.2071, 0.0454] | False |
| ETH | oflow[imbalance]_x_atm_iv | 60 | 6 | 283 | -0.0871 | 0.9291 | [-0.0918, -0.2129, 0.0217] | False |
| ETH | oflow[imbalance]_x_skew | 300 | 6 | 283 | -0.0930 | 0.9331 | [-0.0966, -0.2138, 0.0134] | False |
| BTC | oflow[imbalance]_x_atm_iv | 60 | 6 | 282 | -0.1043 | 0.9620 | [-0.1057, -0.2322, 0.0236] | False |
| BTC | oflow[imbalance]_x_atm_iv | 60 | 24 | 264 | -0.1067 | 0.9610 | [-0.1057, -0.2401, 0.0306] | False |
| ETH | oflow[imbalance]_x_skew | 60 | 24 | 265 | -0.1185 | 0.9750 | [-0.1212, -0.2500, 0.0069] | False |
| ETH | oflow[imbalance]_x_atm_iv | 60 | 72 | 217 | -0.1345 | 0.9650 | [-0.1278, -0.2693, 0.0101] | False |
| BTC | oflow[imbalance]_x_atm_iv | 300 | 72 | 217 | -0.1897 | 0.9970 | [-0.1918, -0.3270, -0.0595] | False |

## Pooled

- BH-FDR rejected: []
- Any config pass (all underlyings): False
- Campaign state: EVAL_78_OFLOW_X_SURFACE_RV_INTERACTION
