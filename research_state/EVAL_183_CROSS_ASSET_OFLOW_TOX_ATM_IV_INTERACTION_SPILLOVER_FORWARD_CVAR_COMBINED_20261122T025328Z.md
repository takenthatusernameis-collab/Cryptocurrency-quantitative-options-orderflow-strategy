# EVAL_183_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_CVAR_COMBINED — cross-asset oflow tox x atm_iv interaction spillover -> forward expected shortfall (CVaR) (Spearman rank IC)

- Generated: `2026-11-22T02:53:28Z`
- Task: `EVAL183-CROSS-ASSET-OFLOW-TOX-ATM-IV-INTERACTION-SPILLOVER-FORWARD-CVAR`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset options order-flow toxicity x atm_iv interaction spillover (other asset's level product) and forward own-asset expected shortfall (CVaR) on real captures
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
| ETH->BTC | 6 | 0.1495 | ETH->BTC::oflow_tox_atm_iv_interaction::bar60.0::h72 | 0 | False |
| BTC->ETH | 6 | 0.1046 | BTC->ETH::oflow_tox_atm_iv_interaction::bar300.0::h6 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_183_CROSS_ASSET_OFLOW_TOX_ATM_IV_INTERACTION_SPILLOVER_FORWARD_CVAR
