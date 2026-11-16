# EVAL_65_OFLOW_TOX_RV_PREDICTIVENESS_COMBINED — options order-flow toxicity -> realized-vol predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-16T08:49:47Z`
- Task: `EVAL65-OFLOW-TOX-RV-PREDICTIVENESS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor

| underlying | snaps | surf inst | 5m bars | deribit trades | perp bars | perp span s | common 5m | ok |
|---|---|---|---|---|---|---|---|---|
| BTC | 2017 | 223 | 1001 | 3237 | 1000 | 300000 | 288 | True |
| ETH | 2017 | 233 | 1001 | 2270 | 1000 | 300000 | 279 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 12 | 0.0883 | imbalance::bar60.0::h72 | 0 | False |
| ETH | 12 | 0.1176 | imbalance::bar60.0::h72 | 2 | True |

## Pooled

- BH-FDR rejected: ['ETH::imbalance::bar60.0::h72', 'ETH::tox::bar60.0::h72']
- All underlyings pass: False
