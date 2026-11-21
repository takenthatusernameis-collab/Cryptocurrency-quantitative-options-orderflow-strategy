# EVAL_171_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_CVAR_COMBINED — cross-asset skew spillover -> forward CVaR (Spearman rank IC)

- Generated: `2026-11-21T20:44:10Z`
- Task: `EVAL171-CROSS-ASSET-SKEW-SPILLOVER-FORWARD-CVAR`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset skew skew spillover (other asset's level) and forward own-asset expected shortfall / CVaR on real captures
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
| ETH->BTC | 6 | 0.2637 | ETH->BTC::skew::bar300.0::h72 | 4 | True |
| BTC->ETH | 6 | 0.0263 | BTC->ETH::skew::bar300.0::h72 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::skew::bar60.0::h6', 'BTC<-ETH::skew::bar60.0::h24', 'BTC<-ETH::skew::bar60.0::h72', 'BTC<-ETH::skew::bar300.0::h72']
- All targets pass: False
- Campaign state: EVAL_171_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_CVAR
