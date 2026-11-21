# EVAL_161_SINGLE_ASSET_TERM_SLOPE_FORWARD_CVAR_COMBINED — single-asset term slope -> forward CVaR (expected shortfall) predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-21T09:44:13Z`
- Task: `EVAL161-SINGLE-ASSET-TERM-SLOPE-FORWARD-CVAR`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (EVAL-74 term floor = EVAL-71 surface + term adequacy)

| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |
|---|---|---|---|---|
| BTC | True | 8 | 557 | True |
| ETH | True | 8 | 329 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.3073 | term_slope::bar60.0::h72 | 4 | True |
| ETH | 6 | 0.0756 | term_slope::bar300.0::h72 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC::term_slope::bar60.0::h6', 'BTC::term_slope::bar60.0::h24', 'BTC::term_slope::bar60.0::h72', 'BTC::term_slope::bar300.0::h72', 'BTC::term_slope::bar300.0::h24']
- All underlyings pass: False
