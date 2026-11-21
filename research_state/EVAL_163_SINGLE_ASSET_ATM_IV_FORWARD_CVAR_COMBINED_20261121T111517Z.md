# EVAL_163_SINGLE_ASSET_ATM_IV_FORWARD_CVAR_COMBINED — single-asset atm_iv -> forward CVaR (expected shortfall) predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-21T11:15:17Z`
- Task: `EVAL163-SINGLE-ASSET-ATM-IV-FORWARD-CVAR`
- Verdict: **GO CONFIRMED**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (EVAL-71 surface floor)

| underlying | option trades | near-ATM | perp candles | perp span s | ok |
|---|---|---|---|---|---|
| BTC | 2748 | 2331 | 1441 | 86400 | True |
| ETH | 3547 | 1509 | 1441 | 86400 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.2068 | atm_iv::bar60.0::h24 | 2 | True |
| ETH | 6 | 0.2481 | atm_iv::bar300.0::h72 | 3 | True |

## Pooled

- BH-FDR rejected: ['BTC::atm_iv::bar60.0::h24', 'BTC::atm_iv::bar60.0::h72', 'ETH::atm_iv::bar60.0::h72', 'ETH::atm_iv::bar300.0::h72', 'ETH::atm_iv::bar60.0::h24', 'BTC::atm_iv::bar300.0::h6', 'BTC::atm_iv::bar60.0::h6', 'BTC::atm_iv::bar300.0::h72']
- All underlyings pass: True
