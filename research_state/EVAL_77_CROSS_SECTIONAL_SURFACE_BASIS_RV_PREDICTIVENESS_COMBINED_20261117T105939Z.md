# EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS_COMBINED — cross-sectional options implied-vol surface basis -> relative realized-vol predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-17T10:59:39Z`
- Task: `EVAL77-CROSS-SECTIONAL-SURFACE-BASIS-RV`
- Verdict: **GO CONFIRMED**
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
| atm_iv | 300 | 72 | 202 | 0.2972 | 0.0010 | [0.2992, 0.1031, 0.4911] | True |
| skew | 300 | 72 | 202 | 0.1960 | 0.0020 | [0.1992, 0.0285, 0.3727] | True |
| atm_iv | 60 | 24 | 1346 | 0.1063 | 0.0020 | [0.1064, 0.0281, 0.1803] | True |
| skew | 60 | 6 | 1364 | 0.0966 | 0.0010 | [0.0960, 0.0280, 0.1648] | True |
| atm_iv | 60 | 72 | 1298 | 0.0956 | 0.0010 | [0.0980, 0.0169, 0.1717] | True |
| atm_iv | 300 | 6 | 268 | 0.0942 | 0.0509 | [0.0971, -0.0399, 0.2398] | False |
| skew | 60 | 24 | 1346 | 0.0905 | 0.0020 | [0.0893, 0.0149, 0.1651] | True |
| skew | 60 | 72 | 1298 | 0.0421 | 0.0759 | [0.0413, -0.0382, 0.1209] | False |
| atm_iv | 300 | 24 | 250 | 0.0413 | 0.2747 | [0.0386, -0.1095, 0.1830] | False |
| skew | 300 | 6 | 268 | 0.0341 | 0.2827 | [0.0376, -0.1156, 0.1799] | False |
| atm_iv | 60 | 6 | 1364 | 0.0205 | 0.2168 | [0.0217, -0.0468, 0.0852] | False |
| skew | 300 | 24 | 250 | -0.0475 | 0.7732 | [-0.0542, -0.2293, 0.1099] | False |

## Pooled

- BH-FDR rejected: ['atm_iv::bar60.0::h72', 'atm_iv::bar300.0::h72', 'skew::bar60.0::h6', 'atm_iv::bar60.0::h24', 'skew::bar60.0::h24', 'skew::bar300.0::h72', 'atm_iv::bar300.0::h6']
- Any config pass: True
- Campaign state: EVAL_77_CROSS_SECTIONAL_SURFACE_BASIS_RV_PREDICTIVENESS
