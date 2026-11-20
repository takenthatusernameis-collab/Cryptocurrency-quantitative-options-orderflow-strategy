# EVAL_133_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_KURTOSIS_COMBINED — cross-asset term_slope spillover -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-20T03:21:23Z`
- Task: `EVAL133-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-RETURN-KURTOSIS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset term_slope spillover (other asset's term_slope) and forward own-asset realized return kurtosis on real captures
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
| ETH->BTC | 6 | 0.2744 | ETH->BTC::term_slope::bar60.0::h72 | 1 | True |
| BTC->ETH | 6 | 0.5003 | BTC->ETH::term_slope::bar300.0::h72 | 2 | True |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::term_slope::bar60.0::h72', 'ETH<-BTC::term_slope::bar300.0::h24', 'ETH<-BTC::term_slope::bar300.0::h72', 'BTC<-ETH::term_slope::bar60.0::h24', 'BTC<-ETH::term_slope::bar300.0::h6', 'ETH<-BTC::term_slope::bar300.0::h6', 'BTC<-ETH::term_slope::bar60.0::h6']
- All targets pass: True
- Campaign state: EVAL_133_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_RETURN_KURTOSIS
