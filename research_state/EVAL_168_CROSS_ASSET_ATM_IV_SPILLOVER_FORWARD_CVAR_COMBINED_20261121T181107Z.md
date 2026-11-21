# EVAL_168_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_CVAR_COMBINED — cross-asset atm_iv spillover -> forward CVaR (Spearman rank IC)

- Generated: `2026-11-21T18:11:07Z`
- Task: `EVAL168-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-CVAR`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM IV atm_iv spillover (other asset's level) and forward own-asset expected shortfall / CVaR on real captures
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
| ETH->BTC | 6 | 0.2960 | ETH->BTC::atm_iv::bar300.0::h72 | 3 | True |
| BTC->ETH | 6 | 0.2634 | BTC->ETH::atm_iv::bar60.0::h24 | 3 | True |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::atm_iv::bar60.0::h24', 'BTC<-ETH::atm_iv::bar60.0::h72', 'BTC<-ETH::atm_iv::bar300.0::h72', 'ETH<-BTC::atm_iv::bar60.0::h6', 'ETH<-BTC::atm_iv::bar60.0::h24', 'ETH<-BTC::atm_iv::bar60.0::h72', 'ETH<-BTC::atm_iv::bar300.0::h72', 'BTC<-ETH::atm_iv::bar60.0::h6', 'BTC<-ETH::atm_iv::bar300.0::h6']
- All targets pass: True
- Campaign state: EVAL_168_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_CVAR
