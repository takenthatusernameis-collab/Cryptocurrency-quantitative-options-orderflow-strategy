# EVAL_105_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD_COMBINED — cross-sectional term-ratio basis -> relative tail-asymmetry spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T20:02:46Z`
- Task: `EVAL105-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-TAIL-ASYMMETRY-SPREAD`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options term-ratio basis (ETH - BTC near-to-far ATM IV term ratio) and the subsequent BTC-minus-ETH forward relative tail-asymmetry spread on the real on-disk captures
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
| term_ratio | 60 | 72 | 1298 | -0.0236 | 0.8052 | [-0.0252, -0.1083, 0.0594] | False |
| term_ratio | 60 | 6 | 1364 | -0.0356 | 0.9101 | [-0.0373, -0.1032, 0.0327] | False |
| term_ratio | 300 | 72 | 202 | -0.0431 | 0.7213 | [-0.0443, -0.2481, 0.1650] | False |
| term_ratio | 300 | 6 | 268 | -0.0787 | 0.9121 | [-0.0782, -0.2389, 0.0795] | False |
| term_ratio | 300 | 24 | 250 | -0.0913 | 0.9051 | [-0.0877, -0.2803, 0.1092] | False |
| term_ratio | 60 | 24 | 1346 | -0.1172 | 1.0000 | [-0.1160, -0.1872, -0.0464] | False |

## Pooled

- BH-FDR rejected: []
- Any config pass: False
- Campaign state: EVAL_105_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_TAIL_ASYMMETRY_SPREAD
