# EVAL_167_SINGLE_ASSET_TERM_SLOPE_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED — single-asset term slope -> forward downside-semivariance share predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-21T16:28:52Z`
- Task: `EVAL167-SINGLE-ASSET-TERM-SLOPE-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
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
| BTC | 6 | 0.0616 | term_slope::bar300.0::h6 | 0 | False |
| ETH | 6 | -0.0440 | term_slope::bar60.0::h6 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All underlyings pass: False
