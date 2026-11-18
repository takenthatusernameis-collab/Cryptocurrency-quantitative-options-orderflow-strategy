# EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD_COMBINED — cross-sectional term-slope basis -> relative *realized-vol* spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T09:18:58Z`
- Task: `EVAL93-CROSS-SECTIONAL-TERM-SLOPE-BASIS-RELATIVE-RV-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options term-slope basis (ETH - BTC near-minus-far ATM IV term slope) and the subsequent BTC-minus-ETH forward relative *realized-vol* spread on the real on-disk captures
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
| term_slope | 300 | 72 | 202 | 0.2648 | 0.0010 | [0.2677, 0.0430, 0.4601] | True |
| term_slope | 60 | 6 | 1364 | 0.0041 | 0.4565 | [0.0018, -0.0718, 0.0743] | False |
| term_slope | 60 | 24 | 1346 | -0.0016 | 0.5335 | [-0.0037, -0.0872, 0.0802] | False |
| term_slope | 300 | 6 | 268 | -0.1410 | 0.9870 | [-0.1408, -0.2922, 0.0021] | False |
| term_slope | 60 | 72 | 1298 | -0.1512 | 1.0000 | [-0.1503, -0.2290, -0.0735] | False |
| term_slope | 300 | 24 | 250 | -0.1667 | 0.9950 | [-0.1611, -0.3328, 0.0144] | False |

## Pooled

- BH-FDR rejected: ['term_slope::bar300.0::h72']
- Any config pass: True
- Campaign state: EVAL_93_CROSS_SECTIONAL_TERM_SLOPE_BASIS_RELATIVE_RV_SPREAD
