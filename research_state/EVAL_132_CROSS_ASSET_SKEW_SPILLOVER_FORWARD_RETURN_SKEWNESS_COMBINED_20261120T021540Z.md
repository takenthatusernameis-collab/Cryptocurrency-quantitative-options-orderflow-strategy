# EVAL_132_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED — cross-asset skew spillover -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-20T02:15:40Z`
- Task: `EVAL132-CROSS-ASSET-SKEW-SPILLOVER-FORWARD-RETURN-SKEWNESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset skew spillover (other asset's skew) and forward own-asset realized return skewness on real captures
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
| ETH->BTC | 6 | 0.3225 | ETH->BTC::skew::bar300.0::h72 | 4 | True |
| BTC->ETH | 6 | 0.1094 | BTC->ETH::skew::bar300.0::h6 | 1 | True |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::skew::bar60.0::h6', 'BTC<-ETH::skew::bar60.0::h24', 'BTC<-ETH::skew::bar300.0::h24', 'BTC<-ETH::skew::bar300.0::h72', 'ETH<-BTC::skew::bar60.0::h6', 'BTC<-ETH::skew::bar60.0::h72', 'ETH<-BTC::skew::bar60.0::h24', 'ETH<-BTC::skew::bar300.0::h6']
- All targets pass: True
- Campaign state: EVAL_132_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_SKEWNESS
