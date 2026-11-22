# EVAL_177_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_VARIANCE_COMBINED — cross-asset skew spillover -> forward realized return variance (Spearman rank IC)

- Generated: `2026-11-21T23:40:31Z`
- Task: `EVAL177-CROSS-ASSET-SKEW-SPILLOVER-FORWARD-VARIANCE`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM option skew spillover (other asset's level) and forward own-asset realized return variance on real captures
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
| ETH->BTC | 6 | 0.2231 | ETH->BTC::skew::bar300.0::h72 | 2 | True |
| BTC->ETH | 6 | 0.2695 | BTC->ETH::skew::bar300.0::h24 | 3 | True |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::skew::bar300.0::h24', 'BTC<-ETH::skew::bar300.0::h72', 'ETH<-BTC::skew::bar60.0::h72', 'ETH<-BTC::skew::bar300.0::h24', 'ETH<-BTC::skew::bar300.0::h72']
- All targets pass: True
- Campaign state: EVAL_177_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_VARIANCE
