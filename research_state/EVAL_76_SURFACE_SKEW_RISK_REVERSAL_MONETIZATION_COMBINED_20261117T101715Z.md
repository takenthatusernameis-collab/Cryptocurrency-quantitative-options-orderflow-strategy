# EVAL_76_SURFACE_SKEW_RISK_REVERSAL_MONETIZATION_COMBINED — surface skew -> signal-timed delta-hedged risk reversal net-of-cost monetization falsification

- Generated: `2026-11-17T10:17:15Z`
- Task: `EVAL76-SURFACE-SKEW-RISK-REVERSAL-MONETIZATION`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (composed)

| underlying | traded floor ok | surface floor ok | ok |
|---|---|---|---|
| BTC | True | True | True |
| ETH | True | True | True |

## Per-underlying (best config by Sharpe)

| underlying | configs | best Sharpe | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 2 | -0.9356 | skew::bar60.0 | 0 | False |
| ETH | 2 | -0.2033 | skew::bar60.0 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All underlyings pass: False
