# EVAL_99_SINGLE_ASSET_TERM_SLOPE_FORWARD_TAIL_ASYMMETRY_COMBINED — term slope -> forward return-tail asymmetry (Spearman rank IC)

- Generated: `2026-11-18T16:36:47Z`
- Task: `EVAL99-SINGLE-ASSET-TERM-SLOPE-FORWARD-TAIL-ASYMMETRY`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between causal term_slope (near-minus-far ATM IV) and forward return-tail asymmetry on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying term floor (EVAL-74, reused verbatim)

| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |
|---|---|---|---|---|
| BTC | True | 8 | 557 | True |
| ETH | True | 8 | 329 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.2591 | term_slope::bar60.0::h72 | 3 | True |
| ETH | 6 | 0.3507 | term_slope::bar300.0::h72 | 3 | True |

## Pooled

- BH-FDR rejected: ['BTC::term_slope::bar60.0::h24', 'BTC::term_slope::bar60.0::h72', 'ETH::term_slope::bar60.0::h24', 'ETH::term_slope::bar60.0::h72', 'ETH::term_slope::bar300.0::h72', 'BTC::term_slope::bar60.0::h6', 'ETH::term_slope::bar300.0::h24', 'BTC::term_slope::bar300.0::h72', 'ETH::term_slope::bar60.0::h6', 'ETH::term_slope::bar300.0::h6']
- All underlyings pass: True
- Campaign state: EVAL_99_SINGLE_ASSET_TERM_SLOPE_FORWARD_TAIL_ASYMMETRY
