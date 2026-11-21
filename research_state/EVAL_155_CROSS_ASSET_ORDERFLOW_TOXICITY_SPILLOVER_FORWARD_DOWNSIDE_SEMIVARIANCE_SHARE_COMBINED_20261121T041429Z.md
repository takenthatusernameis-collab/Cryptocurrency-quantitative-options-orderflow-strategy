# EVAL_155_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED — cross-asset order-flow toxicity spillover -> forward downside-semivariance share (Spearman rank IC)

- Generated: `2026-11-21T04:14:29Z`
- Task: `EVAL155-CROSS-ASSET-ORDERFLOW-TOXICITY-SPILLOVER-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow toxicity spillover (other asset's level) and forward own-asset downside-semivariance share on real captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars: 274

## Per-underlying order-flow state floor

| underlying | floor ok | n toxicity states |
|---|---|---|
| BTC | True | 289 |
| ETH | True | 289 |

## Per-target (best config by Spearman IC)

| target <- signal | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| ETH->BTC | 6 | 0.0117 | ETH->BTC::toxicity::bar300.0::h6 | 0 | False |
| BTC->ETH | 6 | 0.1841 | BTC->ETH::toxicity::bar60.0::h24 | 1 | True |

## Pooled

- BH-FDR rejected: ['ETH<-BTC::toxicity::bar60.0::h24']
- All targets pass: False
- Campaign state: EVAL_155_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE
