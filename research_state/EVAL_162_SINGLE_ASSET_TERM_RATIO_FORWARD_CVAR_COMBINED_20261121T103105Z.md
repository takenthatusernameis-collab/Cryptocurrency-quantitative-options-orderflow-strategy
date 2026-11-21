# EVAL_162_SINGLE_ASSET_TERM_RATIO_FORWARD_CVAR_COMBINED — single-asset term ratio -> forward CVaR (expected shortfall) predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-21T10:31:05Z`
- Task: `EVAL162-SINGLE-ASSET-TERM-RATIO-FORWARD-CVAR`
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
| BTC | 6 | 0.3605 | term_ratio::bar300.0::h72 | 4 | True |
| ETH | 6 | 0.0424 | term_ratio::bar300.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC::term_ratio::bar60.0::h6', 'BTC::term_ratio::bar60.0::h24', 'BTC::term_ratio::bar60.0::h72', 'BTC::term_ratio::bar300.0::h72', 'BTC::term_ratio::bar300.0::h24']
- All underlyings pass: False
