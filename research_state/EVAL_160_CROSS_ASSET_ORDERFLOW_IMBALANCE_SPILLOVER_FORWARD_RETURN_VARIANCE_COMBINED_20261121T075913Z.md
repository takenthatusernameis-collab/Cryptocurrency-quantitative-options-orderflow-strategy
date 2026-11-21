# EVAL_160_CROSS_ASSET_ORDERFLOW_IMBALANCE_SPILLOVER_FORWARD_RETURN_VARIANCE_COMBINED — cross-asset order-flow imbalance spillover -> forward realized return variance (Spearman rank IC)

- Generated: `2026-11-21T07:59:13Z`
- Task: `EVAL160-CROSS-ASSET-ORDERFLOW-IMBALANCE-SPILLOVER-FORWARD-RETURN-VARIANCE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow imbalance spillover (other asset's level) and forward own-asset realized return variance on real captures
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
| ETH->BTC | 6 | 0.1510 | ETH->BTC::imbalance::bar60.0::h6 | 0 | False |
| BTC->ETH | 6 | 0.1350 | BTC->ETH::imbalance::bar60.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_160_CROSS_ASSET_ORDERFLOW_IMBALANCE_SPILLOVER_FORWARD_RETURN_VARIANCE
