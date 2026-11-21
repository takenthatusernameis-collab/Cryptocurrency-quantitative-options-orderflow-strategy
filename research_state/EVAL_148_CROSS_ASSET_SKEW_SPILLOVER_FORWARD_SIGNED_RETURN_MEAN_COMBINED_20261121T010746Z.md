# EVAL_148_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN_COMBINED — cross-asset skew spillover -> forward signed return mean (Spearman rank IC)

- Generated: `2026-11-21T01:07:46Z`
- Task: `EVAL148-CROSS-ASSET-SKEW-SPILLOVER-FORWARD-SIGNED-RETURN-MEAN`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset put-call skew spillover (other asset's level) and forward own-asset signed log-return mean on real captures
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
| ETH->BTC | 6 | 0.2450 | ETH->BTC::skew::bar300.0::h72 | 6 | True |
| BTC->ETH | 6 | -0.0455 | BTC->ETH::skew::bar300.0::h72 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::skew::bar60.0::h6', 'BTC<-ETH::skew::bar60.0::h24', 'BTC<-ETH::skew::bar60.0::h72', 'BTC<-ETH::skew::bar300.0::h6', 'BTC<-ETH::skew::bar300.0::h72', 'BTC<-ETH::skew::bar300.0::h24']
- All targets pass: False
- Campaign state: EVAL_148_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN
