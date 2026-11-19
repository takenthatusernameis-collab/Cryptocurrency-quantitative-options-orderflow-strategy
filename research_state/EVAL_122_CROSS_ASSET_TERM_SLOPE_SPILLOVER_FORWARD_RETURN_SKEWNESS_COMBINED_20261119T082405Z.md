# EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED — cross-asset term_slope spillover -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-19T08:24:05Z`
- Task: `EVAL122-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-SKEWNESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset term-slope spillover (other asset's slope) and forward own-asset realized return skewness on real captures
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
| ETH->BTC | 6 | 0.3817 | ETH->BTC::term_slope::bar300.0::h72 | 3 | True |
| BTC->ETH | 6 | 0.4643 | BTC->ETH::term_slope::bar300.0::h24 | 2 | True |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::term_slope::bar60.0::h72', 'BTC<-ETH::term_slope::bar300.0::h24', 'BTC<-ETH::term_slope::bar300.0::h72', 'ETH<-BTC::term_slope::bar60.0::h72', 'ETH<-BTC::term_slope::bar300.0::h24', 'ETH<-BTC::term_slope::bar60.0::h24']
- All targets pass: True
- Campaign state: EVAL_122_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_SKEWNESS
