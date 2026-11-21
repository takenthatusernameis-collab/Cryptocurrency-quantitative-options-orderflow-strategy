# EVAL_159_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_RETURN_VARIANCE_COMBINED — cross-asset order-flow toxicity spillover -> forward realized return variance (Spearman rank IC)

- Generated: `2026-11-21T06:56:41Z`
- Task: `EVAL159-CROSS-ASSET-ORDERFLOW-TOXICITY-SPILLOVER-FORWARD-RETURN-VARIANCE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow toxicity spillover (other asset's level) and forward own-asset realized return variance on real captures
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
| ETH->BTC | 6 | 0.1412 | ETH->BTC::toxicity::bar60.0::h72 | 0 | False |
| BTC->ETH | 6 | 0.1019 | BTC->ETH::toxicity::bar60.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_159_CROSS_ASSET_ORDERFLOW_TOXICITY_SPILLOVER_FORWARD_RETURN_VARIANCE
