# EVAL_71_SURFACE_IV_RV_PREDICTIVENESS_COMBINED — options implied-vol surface -> realized-vol predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-17T04:15:13Z`
- Task: `EVAL71-SURFACE-IV-RV-PREDICTIVENESS`
- Verdict: **GO CONFIRMED**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor

| underlying | option trades | near-ATM | perp candles | perp span s | ok |
|---|---|---|---|---|---|
| BTC | 2748 | 2331 | 1441 | 86400 | True |
| ETH | 3547 | 1509 | 1441 | 86400 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 12 | 0.3349 | skew::bar300.0::h72 | 4 | True |
| ETH | 12 | 0.2628 | skew::bar300.0::h24 | 4 | True |

## Pooled

- BH-FDR rejected: ['BTC::skew::bar60.0::h72', 'BTC::skew::bar300.0::h24', 'BTC::skew::bar300.0::h72', 'ETH::atm_iv::bar300.0::h24', 'ETH::skew::bar300.0::h24', 'BTC::skew::bar60.0::h24', 'ETH::atm_iv::bar300.0::h72', 'ETH::skew::bar300.0::h72', 'BTC::skew::bar300.0::h6', 'BTC::skew::bar60.0::h6']
- All underlyings pass: True
