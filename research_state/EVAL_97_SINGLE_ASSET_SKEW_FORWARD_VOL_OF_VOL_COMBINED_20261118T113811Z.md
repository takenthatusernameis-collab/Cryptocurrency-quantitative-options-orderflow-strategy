# EVAL_97_SINGLE_ASSET_SKEW_FORWARD_VOL_OF_VOL_COMBINED — skew -> forward vol-of-vol predictiveness

- Generated: `2026-11-18T11:38:11Z`
- Task: `EVAL97-SINGLE-ASSET-SKEW-FORWARD-VOL-OF-VOL`
- Verdict: **GO CONFIRMED**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.2504 | skew::bar300.0::h72 | 4 | True |
| ETH | 6 | 0.2929 | skew::bar300.0::h24 | 2 | True |

## Pooled

- BH-FDR rejected: ['BTC::skew::bar60.0::h72', 'ETH::skew::bar300.0::h24', 'BTC::skew::bar300.0::h24', 'BTC::skew::bar300.0::h72', 'BTC::skew::bar60.0::h6', 'ETH::skew::bar300.0::h72', 'BTC::skew::bar60.0::h24', 'ETH::skew::bar300.0::h6', 'BTC::skew::bar300.0::h6']
- All underlyings pass: True
- Campaign state: EVAL_97_SINGLE_ASSET_SKEW_FORWARD_VOL_OF_VOL
