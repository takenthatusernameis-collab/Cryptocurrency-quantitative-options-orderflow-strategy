# EVAL_144_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED — cross-asset term_ratio spillover -> forward downside-semivariance share (Spearman rank IC)

- Generated: `2026-11-20T19:02:27Z`
- Task: `EVAL144-CROSS-ASSET-TERM-RATIO-SPILLOVER-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM IV term_ratio spillover (other asset's term_ratio) and forward own-asset downside-semivariance share on real captures
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
| ETH->BTC | 6 | -0.0385 | ETH->BTC::term_ratio::bar60.0::h24 | 0 | False |
| BTC->ETH | 6 | -0.0069 | BTC->ETH::term_ratio::bar60.0::h6 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_144_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE
