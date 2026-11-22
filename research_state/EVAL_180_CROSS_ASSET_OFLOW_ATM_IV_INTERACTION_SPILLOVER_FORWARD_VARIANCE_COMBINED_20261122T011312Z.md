# EVAL_180_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE_COMBINED — cross-asset oflow x atm_iv interaction spillover -> forward realized return variance (Spearman rank IC)

- Generated: `2026-11-22T01:13:12Z`
- Task: `EVAL180-CROSS-ASSET-OFLOW-ATM-IV-INTERACTION-SPILLOVER-FORWARD-VARIANCE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow imbalance x atm_iv interaction spillover (other asset's level product) and forward own-asset realized return variance on real captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars: 274

## Per-underlying order-flow + surface floor

| underlying | floor ok | n imbalance states | n surface atm_iv bars |
|---|---|---|---|
| BTC | True | 289 | 289 |
| ETH | True | 289 | 289 |

## Per-target (best config by Spearman IC)

| target <- signal | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| ETH->BTC | 6 | 0.1331 | ETH->BTC::oflow_atm_iv_interaction::bar60.0::h6 | 0 | False |
| BTC->ETH | 6 | 0.1326 | BTC->ETH::oflow_atm_iv_interaction::bar60.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_180_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_VARIANCE
