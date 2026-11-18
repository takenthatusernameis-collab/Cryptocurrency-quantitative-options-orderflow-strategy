# EVAL_109_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_SKEWNESS_COMBINED — atm_iv -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-18T23:10:58Z`
- Task: `EVAL109-SINGLE-ASSET-ATM-IV-FORWARD-RETURN-SKEWNESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between causal near-ATM IV level and forward own-asset realized return skewness on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | floor ok | option trades | near-ATM trades | perp candles | span (s) |
|---|---|---|---|---|---|
| BTC | True | 2748 | 2331 | 1441 | 86400.0 |
| ETH | True | 3547 | 1509 | 1441 | 86400.0 |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.1101 | atm_iv::bar300.0::h6 | 2 | True |
| ETH | 6 | 0.3506 | atm_iv::bar300.0::h72 | 2 | True |

## Pooled

- BH-FDR rejected: ['BTC::atm_iv::bar60.0::h24', 'ETH::atm_iv::bar60.0::h72', 'ETH::atm_iv::bar300.0::h72', 'BTC::atm_iv::bar60.0::h72', 'ETH::atm_iv::bar300.0::h24', 'BTC::atm_iv::bar300.0::h6', 'BTC::atm_iv::bar300.0::h24']
- All underlyings pass: True
- Campaign state: EVAL_109_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_SKEWNESS
