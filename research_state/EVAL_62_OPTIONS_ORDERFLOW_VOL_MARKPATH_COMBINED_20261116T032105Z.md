# EVAL_62_OPTIONS_ORDERFLOW_VOL_MARKPATH_COMBINED — real options order-flow toxicity -> signal-timed delta-hedged ATM straddle (correct mark-path P&L) net-of-cost falsification

- Generated: `2026-11-16T03:21:05Z`
- Task: `INIT-2026-11-16T03:17:05Z-EVAL62-OPTIONS-ORDERFLOW-VOL-MARKPATH-SEAL`
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
| BTC | 4 | -0.0443 | imbalance::bar300.0 | False |
| ETH | 4 | 0.6163 | imbalance::bar300.0 | False |

## Pooled

- Overall PBO: 0.3750
- BH-FDR rejected: []
- All underlyings pass: False
