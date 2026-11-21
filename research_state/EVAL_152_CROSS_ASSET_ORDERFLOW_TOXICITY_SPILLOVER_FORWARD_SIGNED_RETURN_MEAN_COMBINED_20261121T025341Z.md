# EVAL_152_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN_COMBINED — cross-asset order-flow toxicity spillover -> forward signed return mean (Spearman rank IC)

- Generated: `2026-11-21T02:53:41Z`
- Task: `EVAL152-CROSS-ASSET-ORDERFLOW-TOXICITY-SPILLOVER-FORWARD-SIGNED-RETURN-MEAN`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow toxicity spillover (other asset's level) and forward own-asset signed log-return mean on real captures
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
| ETH->BTC | 6 | 0.1878 | ETH->BTC::toxicity::bar60.0::h72 | 1 | True |
| BTC->ETH | 6 | 0.0969 | BTC->ETH::toxicity::bar300.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::toxicity::bar60.0::h72']
- All targets pass: False
- Campaign state: EVAL_152_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN
