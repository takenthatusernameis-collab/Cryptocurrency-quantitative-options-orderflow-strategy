# EVAL_72_SURFACE_SKEW_STRADDLE_MONETIZATION_COMBINED — surface skew -> signal-timed delta-hedged ATM straddle net-of-cost monetization falsification

- Generated: `2026-11-17T05:18:22Z`
- Task: `EVAL72-SURFACE-SKEW-STRADDLE-MONETIZATION`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (composed)

| underlying | traded floor ok | signal floor ok | ok |
|---|---|---|---|
| BTC | True | True | True |
| ETH | True | True | True |

## Per-underlying (best config by Sharpe)

| underlying | configs | best Sharpe | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 4 | 0.8424 | atm_iv::bar300.0 | 0 | False |
| ETH | 4 | -1.1967 | skew::bar300.0 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All underlyings pass: False
