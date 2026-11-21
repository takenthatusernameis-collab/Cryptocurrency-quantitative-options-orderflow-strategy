# EVAL_148_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN_COMBINED — cross-asset term_ratio spillover -> forward signed return mean (Spearman rank IC)

- Generated: `2026-11-21T01:08:27Z`
- Task: `EVAL148-CROSS-ASSET-TERM-RATIO-SPILLOVER-FORWARD-SIGNED-RETURN-MEAN`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset IV term-structure ratio spillover (other asset's term_ratio) and forward own-asset signed log-return mean on real captures
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
| ETH->BTC | 6 | 0.2547 | ETH->BTC::term_ratio::bar60.0::h72 | 2 | True |
| BTC->ETH | 6 | 0.4107 | BTC->ETH::term_ratio::bar300.0::h24 | 4 | True |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::term_ratio::bar60.0::h24', 'BTC<-ETH::term_ratio::bar60.0::h72', 'ETH<-BTC::term_ratio::bar60.0::h72', 'ETH<-BTC::term_ratio::bar300.0::h24', 'ETH<-BTC::term_ratio::bar300.0::h72', 'BTC<-ETH::term_ratio::bar300.0::h72', 'ETH<-BTC::term_ratio::bar300.0::h6', 'BTC<-ETH::term_ratio::bar60.0::h6', 'BTC<-ETH::term_ratio::bar300.0::h6']
- All targets pass: True
- Campaign state: EVAL_148_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN
