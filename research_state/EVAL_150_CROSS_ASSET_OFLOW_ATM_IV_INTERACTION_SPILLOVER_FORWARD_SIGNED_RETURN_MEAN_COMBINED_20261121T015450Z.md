# EVAL_150_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN_COMBINED — cross-asset oflow x atm_iv interaction spillover -> forward signed return mean (Spearman rank IC)

- Generated: `2026-11-21T01:54:50Z`
- Task: `EVAL150-CROSS-ASSET-OFLOW-ATM-IV-INTERACTION-SPILLOVER-FORWARD-SIGNED-RETURN-MEAN`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow imbalance x atm_iv interaction spillover (other asset's level product) and forward own-asset signed log-return mean on real captures
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
| ETH->BTC | 6 | 0.0651 | ETH->BTC::oflow_atm_iv_interaction::bar60.0::h6 | 0 | False |
| BTC->ETH | 6 | 0.0500 | BTC->ETH::oflow_atm_iv_interaction::bar300.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_150_CROSS_ASSET_OFLOW_ATM_IV_INTERACTION_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN
