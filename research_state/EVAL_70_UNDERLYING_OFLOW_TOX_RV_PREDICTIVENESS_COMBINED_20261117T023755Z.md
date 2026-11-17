# EVAL_70_UNDERLYING_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED — underlying order-flow -> realized-vol / signed-return predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-17T02:37:55Z`
- Task: `EVAL70-UNDERLYING-OFLOW-TOX-RV-PREDICTIVENESS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor

| underlying | perp trades | perp candles | perp span s | 5m bars | ok |
|---|---|---|---|---|---|
| BTC | 319777 | 1441 | 86400 | 289 | True |
| ETH | 176925 | 1441 | 86400 | 289 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 18 | 0.2479 | imbalance::rv::bar300.0::h72 | 1 | True |
| ETH | 18 | 0.0436 | tox::rv::bar300.0::h72 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC::imbalance::rv::bar300.0::h72']
- All underlyings pass: False
