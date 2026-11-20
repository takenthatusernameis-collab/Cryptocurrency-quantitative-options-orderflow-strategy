# EVAL_145_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED — cross-asset term_slope spillover -> forward downside-semivariance share (Spearman rank IC)

- Generated: `2026-11-20T20:15:18Z`
- Task: `EVAL145-CROSS-ASSET-TERM-SLOPE-SPILLOVER-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM IV term_slope spillover (other asset's term_slope) and forward own-asset downside-semivariance share on real captures
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
| ETH->BTC | 6 | -0.0242 | ETH->BTC::term_slope::bar60.0::h24 | 0 | False |
| BTC->ETH | 6 | 0.0300 | BTC->ETH::term_slope::bar300.0::h6 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_145_CROSS_ASSET_TERM_SLOPE_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE
