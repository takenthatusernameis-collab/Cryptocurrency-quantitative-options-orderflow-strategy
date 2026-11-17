# EVAL_75_TERM_STRUCTURE_STRADDLE_MONETIZATION_COMBINED — term-structure signal -> signal-timed delta-hedged ATM straddle net-of-cost monetization falsification

- Generated: `2026-11-17T09:56:28Z`
- Task: `EVAL75-TERM-STRUCTURE-STRADDLE-MONETIZATION`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (composed)

| underlying | traded floor ok | term-signal floor ok | ok |
|---|---|---|---|
| BTC | True | True | True |
| ETH | True | True | True |

## Per-underlying (best config by Sharpe)

| underlying | configs | best Sharpe | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 4 | 1.6331 | term_slope::bar60.0 | 0 | False |
| ETH | 4 | -0.1716 | term_ratio::bar300.0 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All underlyings pass: False
