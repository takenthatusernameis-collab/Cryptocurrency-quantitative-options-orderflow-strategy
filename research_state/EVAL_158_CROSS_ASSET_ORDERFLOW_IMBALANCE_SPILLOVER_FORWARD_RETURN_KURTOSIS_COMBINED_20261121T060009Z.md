# EVAL_158_CROSS_ASSET_ORDERFLOW_IMBALANCE_SPILLOVER_FORWARD_RETURN_KURTOSIS_COMBINED — cross-asset order-flow imbalance spillover -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-21T06:00:09Z`
- Task: `EVAL158-CROSS-ASSET-ORDERFLOW-IMBALANCE-SPILLOVER-FORWARD-RETURN-KURTOSIS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow imbalance spillover (other asset's level) and forward own-asset realized return kurtosis on real captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars: 274

## Per-underlying order-flow state floor

| underlying | floor ok | n imbalance states |
|---|---|---|
| BTC | True | 289 |
| ETH | True | 289 |

## Per-target (best config by Spearman IC)

| target <- signal | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| ETH->BTC | 6 | 0.1774 | ETH->BTC::imbalance::bar300.0::h24 | 1 | True |
| BTC->ETH | 6 | 0.0784 | BTC->ETH::imbalance::bar60.0::h72 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::imbalance::bar300.0::h24']
- All targets pass: False
- Campaign state: EVAL_158_CROSS_ASSET_ORDERFLOW_IMBALANCE_SPILLOVER_FORWARD_RETURN_KURTOSIS
