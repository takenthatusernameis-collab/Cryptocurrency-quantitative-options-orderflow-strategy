# EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION_COMBINED — cross-sectional relative-value delta-hedged ATM straddle spread net-of-cost monetization falsification

- Generated: `2026-11-17T13:44:47Z`
- Task: `EVAL80-CROSS-SECTIONAL-RV-STRADDLE-MONETIZATION`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)
- Aligned common straddle bars by grid: {'60.0': 274, '300.0': 274}

## Per-underlying floor (composed)

| underlying | traded floor ok | surface floor ok | ok |
|---|---|---|---|
| BTC | True | True | True |
| ETH | True | True | True |

## Configs (best first by Sharpe)

| basis signal | bar s | n states | n returns | Sharpe | max-DD | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|---|
| skew | 60 | 274 | 273 | -0.2657 | 0.0395 | 0.7852 | [-0.2657, -2.0415, 1.2018] | False |
| atm_iv | 60 | 274 | 273 | -0.9070 | 0.0459 | 0.3487 | [-0.9070, -2.7561, 0.7614] | False |
| atm_iv | 300 | 274 | 273 | -0.9661 | 0.0659 | 0.3067 | [-0.9661, -2.9015, 0.7755] | False |
| skew | 300 | 274 | 273 | -1.4037 | 0.0618 | 0.1518 | [-1.4037, -3.1778, 0.1888] | False |

## Pooled

- BH-FDR rejected: []
- Any config pass: False
- Campaign state: EVAL_80_CROSS_SECTIONAL_RELATIVE_VALUE_STRADDLE_MONETIZATION
