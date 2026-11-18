# EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_COMBINED — cross-sectional skew basis -> relative tail-asymmetry spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T23:18:28Z`
- Task: `EVAL110-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options skew basis (ETH - BTC near-ATM put-call skew) and the subsequent BTC-minus-ETH forward relative tail-asymmetry spread on the real on-disk captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}

## Per-underlying floor (EVAL-71 surface floor)

| underlying | floor ok | option trades | near-ATM trades | perp candles | span (s) |
|---|---|---|---|---|---|
| BTC | True | 2748 | 2331 | 1441 | 86400.0 |
| ETH | True | 3547 | 1509 | 1441 | 86400.0 |

## Configs (best first by Spearman IC)

| signal | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|
| skew | 300 | 72 | 202 | 0.1350 | 0.0290 | [0.1417, -0.0405, 0.3135] | False |
| skew | 60 | 6 | 1364 | 0.0535 | 0.0270 | [0.0515, -0.0170, 0.1154] | False |
| skew | 300 | 6 | 268 | -0.0167 | 0.6234 | [-0.0200, -0.1690, 0.1204] | False |
| skew | 300 | 24 | 250 | -0.0369 | 0.7103 | [-0.0295, -0.2068, 0.1467] | False |
| skew | 60 | 24 | 1346 | -0.0454 | 0.9510 | [-0.0436, -0.1201, 0.0278] | False |
| skew | 60 | 72 | 1298 | -0.0486 | 0.9600 | [-0.0477, -0.1191, 0.0284] | False |

## Pooled

- BH-FDR rejected: ['skew::bar300.0::h72']
- Any config pass: False
- Campaign state: EVAL_110_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD
