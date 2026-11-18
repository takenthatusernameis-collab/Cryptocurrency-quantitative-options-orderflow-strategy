# EVAL_104_SINGLE_ASSET_TERM_SLOPE_FORWARD_SIGNED_RETURN_COMBINED — term_slope -> forward signed return (Spearman rank IC)

- Generated: `2026-11-18T19:01:38Z`
- Task: `EVAL104-SINGLE-ASSET-TERM-SLOPE-FORWARD-SIGNED-RETURN`
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
| BTC | 6 | 0.4058 | term_slope::bar300.0::h24 | 3 | True |
| ETH | 6 | 0.2600 | term_slope::bar60.0::h24 | 4 | True |

## Pooled

- BH-FDR rejected: ['BTC::term_slope::bar60.0::h72', 'BTC::term_slope::bar300.0::h24', 'ETH::term_slope::bar60.0::h6', 'ETH::term_slope::bar60.0::h24', 'ETH::term_slope::bar60.0::h72', 'BTC::term_slope::bar300.0::h72', 'ETH::term_slope::bar300.0::h72', 'BTC::term_slope::bar300.0::h6']
- All underlyings pass: True
- Campaign state: EVAL_104_SINGLE_ASSET_TERM_SLOPE_FORWARD_SIGNED_RETURN
