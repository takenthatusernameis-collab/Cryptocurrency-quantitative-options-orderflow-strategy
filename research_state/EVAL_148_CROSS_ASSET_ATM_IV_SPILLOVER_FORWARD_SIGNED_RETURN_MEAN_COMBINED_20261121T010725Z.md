# EVAL_148_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN_COMBINED — cross-asset atm_iv spillover -> forward signed return mean (Spearman rank IC)

- Generated: `2026-11-21T01:07:25Z`
- Task: `EVAL148-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-SIGNED-RETURN-MEAN`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM IV atm_iv spillover (other asset's level) and forward own-asset signed log-return mean on real captures
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
| ETH->BTC | 6 | 0.3428 | ETH->BTC::atm_iv::bar300.0::h72 | 1 | True |
| BTC->ETH | 6 | 0.1875 | BTC->ETH::atm_iv::bar300.0::h24 | 1 | True |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::atm_iv::bar300.0::h72', 'ETH<-BTC::atm_iv::bar300.0::h24', 'BTC<-ETH::atm_iv::bar300.0::h24', 'ETH<-BTC::atm_iv::bar60.0::h72', 'ETH<-BTC::atm_iv::bar300.0::h72', 'BTC<-ETH::atm_iv::bar60.0::h72', 'BTC<-ETH::atm_iv::bar60.0::h24', 'BTC<-ETH::atm_iv::bar60.0::h6']
- All targets pass: True
- Campaign state: EVAL_148_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN
