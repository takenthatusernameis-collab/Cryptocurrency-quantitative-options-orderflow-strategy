# EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION_COMBINED — surface -> signal-timed delta-hedged butterfly (smile-convexity) net-of-cost monetization falsification

- Generated: `2026-11-17T18:07:28Z`
- Task: `EVAL82-SURFACE-SKEW-BUTTERFLY-MONETIZATION`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (composed)

| underlying | traded floor ok | surface floor ok | butterfly states | butterfly ok | ok |
|---|---|---|---|---|---|
| BTC | True | True | 274 | True | True |
| ETH | True | True | 280 | True | True |

## Per-underlying (best config by Sharpe)

| underlying | configs | best Sharpe | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 4 | -1.0361 | atm_iv::bar60.0 | 0 | False |
| ETH | 4 | 0.7130 | atm_iv::bar300.0 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All underlyings pass: False
- Campaign state: EVAL_82_SURFACE_SKEW_BUTTERFLY_MONETIZATION
