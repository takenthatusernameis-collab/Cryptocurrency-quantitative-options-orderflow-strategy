# EVAL_113_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_SKEWNESS_COMBINED — term_slope -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-19T00:15:21Z`
- Task: `EVAL113-SINGLE-ASSET-TERM-SLOPE-FORWARD-RETURN-SKEWNESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between causal near-to-far ATM IV term slope and forward own-asset realized return skewness on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying term floor (EVAL-74, reused verbatim)

| underlying | floor ok | eval71 floor ok | distinct expiries | bars with term |
|---|---|---|---|---|
| BTC | True | True | 8 | 557 |
| ETH | True | True | 8 | 329 |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.3005 | term_slope::bar60.0::h72 | 4 | True |
| ETH | 6 | 0.2116 | term_slope::bar300.0::h24 | 2 | True |

## Pooled

- BH-FDR rejected: ['BTC::term_slope::bar60.0::h24', 'BTC::term_slope::bar60.0::h72', 'BTC::term_slope::bar300.0::h24', 'ETH::term_slope::bar60.0::h72', 'ETH::term_slope::bar300.0::h24', 'BTC::term_slope::bar60.0::h6', 'ETH::term_slope::bar60.0::h24', 'ETH::term_slope::bar300.0::h72', 'ETH::term_slope::bar60.0::h6', 'ETH::term_slope::bar300.0::h6']
- All underlyings pass: True
- Campaign state: EVAL_113_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_SKEWNESS
