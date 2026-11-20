# EVAL_146_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED — cross-asset atm_iv spillover -> forward downside-semivariance share (Spearman rank IC)

- Generated: `2026-11-20T21:38:12Z`
- Task: `EVAL146-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM IV atm_iv spillover (other asset's level) and forward own-asset downside-semivariance share on real captures
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
| ETH->BTC | 6 | 0.0348 | ETH->BTC::atm_iv::bar60.0::h6 | 0 | False |
| BTC->ETH | 6 | 0.0533 | BTC->ETH::atm_iv::bar60.0::h6 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_146_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE
