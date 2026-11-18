# EVAL_94_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RV_SPREAD_COMBINED — cross-sectional term-ratio basis -> relative *realized-vol* spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T09:43:06Z`
- Task: `EVAL94-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-RV-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options term-ratio basis (ETH - BTC near-minus-far ATM IV term slope) and the subsequent BTC-minus-ETH forward relative *realized-vol* spread on the real on-disk captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}

## Per-underlying floor (EVAL-71 surface floor + term-structure adequacy)

| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |
|---|---|---|---|---|
| BTC | True | 8 | 557 | True |
| ETH | True | 8 | 329 | True |

## Configs (best first by Spearman IC)

| signal | bar s | horizon | n pairs | Spearman IC | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|
| term_ratio | 300 | 72 | 202 | 0.0942 | 0.0779 | [0.0930, -0.1352, 0.3149] | False |
| term_ratio | 60 | 24 | 1346 | 0.0532 | 0.0360 | [0.0514, -0.0310, 0.1334] | False |
| term_ratio | 60 | 6 | 1364 | 0.0249 | 0.1938 | [0.0228, -0.0498, 0.0985] | False |
| term_ratio | 60 | 72 | 1298 | -0.0418 | 0.9401 | [-0.0410, -0.1263, 0.0421] | False |
| term_ratio | 300 | 6 | 268 | -0.1818 | 0.9980 | [-0.1827, -0.3153, -0.0417] | False |
| term_ratio | 300 | 24 | 250 | -0.2882 | 1.0000 | [-0.2830, -0.4464, -0.1164] | False |

## Pooled

- BH-FDR rejected: []
- Any config pass: False
- Campaign state: EVAL_94_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_RV_SPREAD
