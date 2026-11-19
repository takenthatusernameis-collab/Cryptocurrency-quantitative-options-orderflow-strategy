# EVAL_114_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED — cross-asset atm_iv spillover -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-19T02:14:50Z`
- Task: `EVAL114-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-RETURN-SKEWNESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM IV spillover (other asset's level) and forward own-asset realized return skewness on real captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}

## Per-underlying EVAL-71 surface floor

| underlying | surface floor ok | option trades | near-ATM | perp candles | span (s) |
|---|---|---|---|---|---|
| BTC | None | None | None | None | None |
| ETH | None | None | None | None | None |

## Per-target (best config by Spearman IC)

| target <- signal | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| ETH->BTC | 6 | 0.4039 | ETH->BTC::atm_iv::bar300.0::h72 | 2 | True |
| BTC->ETH | 6 | 0.1173 | BTC->ETH::atm_iv::bar300.0::h24 | 1 | True |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::atm_iv::bar300.0::h24', 'BTC<-ETH::atm_iv::bar300.0::h72', 'ETH<-BTC::atm_iv::bar60.0::h72', 'ETH<-BTC::atm_iv::bar60.0::h24', 'ETH<-BTC::atm_iv::bar300.0::h24']
- All targets pass: True
- Campaign state: EVAL_114_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_SKEWNESS
