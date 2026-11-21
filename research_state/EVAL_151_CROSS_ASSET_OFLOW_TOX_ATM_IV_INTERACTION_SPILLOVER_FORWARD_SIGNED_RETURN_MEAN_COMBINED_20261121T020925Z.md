# EVAL_151_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN_COMBINED — cross-asset oflow x atm_iv interaction spillover -> forward signed return mean (Spearman rank IC)

- Generated: `2026-11-21T02:09:25Z`
- Task: `EVAL151-CROSS-ASSET-OFLOW-TOX-ATM-IV-INTERACTION-SPILLOVER-FORWARD-SIGNED-RETURN-MEAN`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow toxicity x atm_iv interaction spillover (other asset's level product) and forward own-asset signed log-return mean on real captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars: 274

## Per-underlying order-flow + surface floor

| underlying | floor ok | n toxicity states | n surface atm_iv bars |
|---|---|---|---|
| BTC | True | 289 | 289 |
| ETH | True | 289 | 289 |

## Per-target (best config by Spearman IC)

| target <- signal | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| ETH->BTC | 6 | 0.1608 | ETH->BTC::oflow_tox_atm_iv_interaction::bar60.0::h72 | 0 | False |
| BTC->ETH | 6 | 0.1230 | BTC->ETH::oflow_tox_atm_iv_interaction::bar300.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_151_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_SIGNED_RETURN_MEAN
