# EVAL_64_FEASIBLE_OFLOW_RV_MARKPATH_COMBINED — real options order-flow toxicity -> signal-timed delta-hedged ATM straddle (correct mark-path P&L) net-of-cost falsification

- Generated: `2026-11-16T08:22:10Z`
- Task: `EVAL64-FEASIBLE-FLOOR-OFLOW-RV-MARKPATH`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor

| underlying | snaps | surf inst | 5m bars | deribit trades | of inst | deribit span s | perp bars | perp span s | common 5m | ok |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 2017 | 223 | 1001 | 3237 | 174 | 86446 | 1000 | 300000 | 288 | True |
| ETH | 2017 | 233 | 1001 | 2270 | 164 | 83525 | 1000 | 300000 | 279 | True |

## Per-underlying (best config)

| underlying | configs | best Sharpe | best config | any pass |
|---|---|---|---|---|
| BTC | 4 | -0.5837 | imbalance::bar60.0 | False |
| ETH | 4 | -0.0954 | imbalance::bar300.0 | False |

## Pooled

- Overall PBO: 0.3750
- BH-FDR rejected: ['BTC::imbalance::bar300.0']
- All underlyings pass: False
