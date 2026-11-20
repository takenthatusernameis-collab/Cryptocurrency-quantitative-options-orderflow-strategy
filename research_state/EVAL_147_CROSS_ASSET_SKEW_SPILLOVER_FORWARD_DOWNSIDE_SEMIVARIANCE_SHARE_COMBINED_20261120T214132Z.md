# EVAL_147_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED — cross-asset skew spillover -> forward downside-semivariance share (Spearman rank IC)

- Generated: `2026-11-20T21:41:32Z`
- Task: `EVAL147-CROSS-ASSET-SKEW-SPILLOVER-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options surface skew spillover (other asset's skew) and forward own-asset downside-semivariance share on real captures
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
| ETH->BTC | 6 | -0.0586 | ETH->BTC::skew::bar300.0::h6 | 0 | False |
| BTC->ETH | 6 | 0.1621 | BTC->ETH::skew::bar300.0::h24 | 1 | True |

## Pooled

- BH-FDR rejected: ['ETH<-BTC::skew::bar300.0::h24']
- All targets pass: False
- Campaign state: EVAL_147_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE
