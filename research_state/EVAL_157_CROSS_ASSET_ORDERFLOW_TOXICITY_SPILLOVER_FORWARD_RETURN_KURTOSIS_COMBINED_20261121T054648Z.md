# EVAL_157_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_RETURN_KURTOSIS_COMBINED — cross-asset order-flow toxicity spillover -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-21T05:46:48Z`
- Task: `EVAL157-CROSS-ASSET-ORDERFLOW-TOXICITY-SPILLOVER-FORWARD-RETURN-KURTOSIS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow toxicity spillover (other asset's level) and forward own-asset realized return kurtosis on real captures
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
| ETH->BTC | 6 | 0.1004 | ETH->BTC::toxicity::bar60.0::h72 | 0 | False |
| BTC->ETH | 6 | 0.0927 | BTC->ETH::toxicity::bar60.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_157_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_RETURN_KURTOSIS
