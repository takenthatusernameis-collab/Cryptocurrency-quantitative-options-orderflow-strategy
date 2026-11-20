# EVAL_143_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED — cross-asset term_ratio spillover -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-20T18:20:53Z`
- Task: `EVAL143-CROSS-ASSET-TERM-RATIO-SPILLOVER-FORWARD-RETURN-SKEWNESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM IV term_ratio spillover (other asset's term_ratio) and forward own-asset realized return skewness on real captures
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
| ETH->BTC | 6 | 0.2613 | ETH->BTC::term_ratio::bar300.0::h72 | 3 | True |
| BTC->ETH | 6 | 0.4878 | BTC->ETH::term_ratio::bar300.0::h24 | 3 | True |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::term_ratio::bar60.0::h72', 'BTC<-ETH::term_ratio::bar300.0::h72', 'ETH<-BTC::term_ratio::bar60.0::h24', 'ETH<-BTC::term_ratio::bar60.0::h72', 'ETH<-BTC::term_ratio::bar300.0::h24', 'BTC<-ETH::term_ratio::bar300.0::h24', 'BTC<-ETH::term_ratio::bar60.0::h6']
- All targets pass: True
- Campaign state: EVAL_143_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS
