# EVAL_149_CROSS_ASSET_ORDERFLOW_IMBALANCE_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN_COMBINED — cross-asset order-flow imbalance spillover -> forward signed return mean (Spearman rank IC)

- Generated: `2026-11-21T01:08:48Z`
- Task: `EVAL149-CROSS-ASSET-ORDERFLOW-IMBALANCE-SPILLOVER-FORWARD-SIGNED-RETURN-MEAN`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow imbalance spillover (other asset's level) and forward own-asset signed log-return mean on real captures
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
| ETH->BTC | 6 | 0.1027 | ETH->BTC::imbalance::bar60.0::h6 | 0 | False |
| BTC->ETH | 6 | 0.0784 | BTC->ETH::imbalance::bar60.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_149_CROSS_ASSET_ORDERFLOW_IMBALANCE_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN
