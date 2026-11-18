# EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD_COMBINED — cross-sectional term-ratio basis -> relative vol-of-vol spread predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-18T21:58:00Z`
- Task: `EVAL107-CROSS-SECTIONAL-TERM-RATIO-BASIS-RELATIVE-VOL-OF-VOL-SPREAD`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between the causal cross-sectional options term-ratio basis (ETH - BTC near-to-far ATM IV term ratio) and the subsequent BTC-minus-ETH forward relative *vol-of-vol* spread on the real on-disk captures
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
| term_ratio | 60 | 72 | 1298 | 0.1066 | 0.0010 | [0.1040, 0.0273, 0.1889] | True |
| term_ratio | 60 | 24 | 1346 | 0.0709 | 0.0040 | [0.0699, -0.0161, 0.1519] | False |
| term_ratio | 60 | 6 | 1364 | 0.0100 | 0.3726 | [0.0058, -0.0672, 0.0855] | False |
| term_ratio | 300 | 72 | 202 | -0.2187 | 1.0000 | [-0.2171, -0.4278, 0.0129] | False |
| term_ratio | 300 | 6 | 268 | -0.3284 | 1.0000 | [-0.3258, -0.4407, -0.1970] | False |
| term_ratio | 300 | 24 | 250 | -0.4600 | 1.0000 | [-0.4578, -0.5812, -0.3189] | False |

## Pooled

- BH-FDR rejected: ['term_ratio::bar60.0::h72', 'term_ratio::bar60.0::h24']
- Any config pass: True
- Campaign state: EVAL_107_CROSS_SECTIONAL_TERM_RATIO_BASIS_RELATIVE_VOL_OF_VOL_SPREAD
