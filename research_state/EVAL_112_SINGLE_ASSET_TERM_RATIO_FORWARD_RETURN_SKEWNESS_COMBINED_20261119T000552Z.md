# EVAL_112_SINGLE_ASSET_TERM_RATIO_FORWARD_RETURN_SKEWNESS_COMBINED — term_ratio -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-19T00:05:52Z`
- Task: `EVAL112-SINGLE-ASSET-TERM-RATIO-FORWARD-RETURN-SKEWNESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between causal near-to-far ATM IV term ratio and forward own-asset realized return skewness on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying term floor (EVAL-74, reused verbatim)

| underlying | floor ok | eval71 floor ok | distinct expiries | bars with term |
|---|---|---|---|---|
| BTC | True | True | 8 | 557 |
| ETH | True | True | 8 | 329 |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.2883 | term_ratio::bar60.0::h72 | 4 | True |
| ETH | 6 | 0.2223 | term_ratio::bar300.0::h24 | 2 | True |

## Pooled

- BH-FDR rejected: ['BTC::term_ratio::bar60.0::h24', 'BTC::term_ratio::bar60.0::h72', 'BTC::term_ratio::bar300.0::h24', 'ETH::term_ratio::bar60.0::h72', 'ETH::term_ratio::bar300.0::h24', 'BTC::term_ratio::bar60.0::h6', 'BTC::term_ratio::bar300.0::h72', 'ETH::term_ratio::bar60.0::h24', 'ETH::term_ratio::bar60.0::h6', 'ETH::term_ratio::bar300.0::h6']
- All underlyings pass: True
- Campaign state: EVAL_112_SINGLE_ASSET_TERM_RATIO_FORWARD_RETURN_SKEWNESS
