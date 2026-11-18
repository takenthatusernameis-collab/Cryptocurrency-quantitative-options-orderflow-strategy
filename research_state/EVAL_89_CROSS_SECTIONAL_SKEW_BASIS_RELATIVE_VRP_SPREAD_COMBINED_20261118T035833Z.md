# EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD_COMBINED — cross-sectional put-call skew basis -> relative *VRP* spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T03:58:33Z`
- Task: `EVAL89-CROSS-SECTIONAL-SKEW-BASIS-RELATIVE-VRP-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional put-call skew basis (ETH - BTC) and the subsequent BTC-minus-ETH forward relative *VRP* spread (atm_iv - forward_RV) on the real on-disk captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}

## Per-underlying EVAL-71 floor

| underlying | surface floor ok | option trades | near-ATM | perp candles | ok |
|---|---|---|---|---|---|
| BTC | True | 2748 | 2331 | 1441 | True |
| ETH | True | 3547 | 1509 | 1441 | True |

## Configs (best first by Spearman IC)

| signal | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|
| skew | 300 | 6 | 268 | -0.1701 | 0.9980 | [-0.1698, -0.3243, -0.0295] | False |
| skew | 300 | 24 | 250 | -0.2042 | 1.0000 | [-0.1979, -0.3403, -0.0266] | False |
| skew | 60 | 6 | 1364 | -0.2566 | 1.0000 | [-0.2570, -0.3253, -0.1902] | False |
| skew | 60 | 24 | 1346 | -0.2580 | 1.0000 | [-0.2606, -0.3253, -0.1938] | False |
| skew | 60 | 72 | 1298 | -0.2637 | 1.0000 | [-0.2664, -0.3344, -0.1968] | False |
| skew | 300 | 72 | 202 | -0.2753 | 1.0000 | [-0.2784, -0.4424, -0.0999] | False |

## Pooled

- BH-FDR rejected: []
- Any config pass: False
- Campaign state: EVAL_89_CROSS_SECTIONAL_SKEW_BASIS_RELATIVE_VRP_SPREAD
