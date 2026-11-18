# EVAL_106_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_COMBINED — cross-sectional term-slope basis -> relative tail-asymmetry spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T20:42:31Z`
- Task: `EVAL106-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options term-slope basis (ETH - BTC near-to-far ATM IV term ratio) and the subsequent BTC-minus-ETH forward relative tail-asymmetry spread on the real on-disk captures
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
| term_slope | 60 | 6 | 1364 | -0.0168 | 0.7263 | [-0.0182, -0.0855, 0.0515] | False |
| term_slope | 60 | 72 | 1298 | -0.0424 | 0.9381 | [-0.0429, -0.1357, 0.0456] | False |
| term_slope | 300 | 24 | 250 | -0.0508 | 0.7722 | [-0.0479, -0.2264, 0.1386] | False |
| term_slope | 60 | 24 | 1346 | -0.0904 | 0.9980 | [-0.0895, -0.1595, -0.0158] | False |
| term_slope | 300 | 6 | 268 | -0.0947 | 0.9471 | [-0.0938, -0.2546, 0.0543] | False |
| term_slope | 300 | 72 | 202 | -0.1245 | 0.9540 | [-0.1313, -0.3424, 0.1111] | False |

## Pooled

- BH-FDR rejected: []
- Any config pass: False
- Campaign state: EVAL_106_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD
