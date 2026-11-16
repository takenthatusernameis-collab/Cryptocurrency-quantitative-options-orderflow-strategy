# EVAL_61_OPTIONS_ORDERFLOW_REALIZED_VOL_COMBINED — real options order-flow toxicity -> realized vol straddle net-of-cost falsification

- Generated: `2026-11-16T03:29:23Z`
- Task: `EVAL61-OPTIONS-ORDERFLOW-TO-REALIZED-VOL-STRADDLE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor

| underlying | snaps | surf inst | 5m bars | deribit trades | of inst | deribit span s | perp bars | perp span s | common 5m | ok |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 289 | 92 | 289 | 2748 | 87 | 86351 | 288 | 86400 | 288 | True |
| ETH | 289 | 280 | 289 | 3558 | 227 | 86289 | 288 | 86400 | 287 | True |

## Per-underlying (best config)

| underlying | configs | best Sharpe | best config | any pass |
|---|---|---|---|---|
| BTC | 4 | 0.9717 | imbalance::bar300.0 | False |
| ETH | 4 | 0.9916 | imbalance::bar300.0 | False |

## Pooled

- Overall PBO: 0.2500
- BH-FDR rejected: []
- All underlyings pass: False
