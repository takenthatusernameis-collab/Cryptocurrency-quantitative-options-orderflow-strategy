# EVAL_117_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_KURTOSIS_COMBINED — term_slope -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-19T04:30:17Z`
- Task: `EVAL117-SINGLE-ASSET-TERM-SLOPE-FORWARD-RETURN-KURTOSIS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between causal near-to-far ATM IV term slope and forward own-asset realized return kurtosis on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying term floor (EVAL-74, reused verbatim)

| underlying | floor ok | eval71 floor ok | distinct expiries | bars with term |
|---|---|---|---|---|
| BTC | True | True | 8 | 557 |
| ETH | True | True | 8 | 329 |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | -0.0425 | term_slope::bar300.0::h6 | 0 | False |
| ETH | 6 | 0.1699 | term_slope::bar300.0::h6 | 1 | True |

## Pooled

- BH-FDR rejected: ['ETH::term_slope::bar300.0::h6']
- All underlyings pass: False
- Campaign state: EVAL_117_SINGLE_ASSET_TERM_SLOPE_FORWARD_RETURN_KURTOSIS
