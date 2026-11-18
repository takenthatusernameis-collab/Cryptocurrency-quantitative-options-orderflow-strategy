# EVAL_102_SINGLE_ASSET_TERM_RATIO_FORWARD_SIGNED_RETURN_COMBINED — term_ratio -> forward signed return (Spearman rank IC)

- Generated: `2026-11-18T18:32:32Z`
- Task: `EVAL102-SINGLE-ASSET-TERM-RATIO-FORWARD-SIGNED-RETURN`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between causal near-to-far ATM IV term ratio and forward own-asset signed log-return on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying term floor (EVAL-74, reused verbatim)

| underlying | floor ok | eval71 floor ok | distinct expiries | bars with term |
|---|---|---|---|---|
| BTC | True | True | 8 | 557 |
| ETH | True | True | 8 | 329 |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.3926 | term_ratio::bar300.0::h24 | 3 | True |
| ETH | 6 | 0.2559 | term_ratio::bar60.0::h24 | 3 | True |

## Pooled

- BH-FDR rejected: ['BTC::term_ratio::bar60.0::h72', 'BTC::term_ratio::bar300.0::h24', 'BTC::term_ratio::bar300.0::h72', 'ETH::term_ratio::bar60.0::h6', 'ETH::term_ratio::bar60.0::h24', 'ETH::term_ratio::bar60.0::h72', 'BTC::term_ratio::bar300.0::h6']
- All underlyings pass: True
- Campaign state: EVAL_102_SINGLE_ASSET_TERM_RATIO_FORWARD_SIGNED_RETURN
