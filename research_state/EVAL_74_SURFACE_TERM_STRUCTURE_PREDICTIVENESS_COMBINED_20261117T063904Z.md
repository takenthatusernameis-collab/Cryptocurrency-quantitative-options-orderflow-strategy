# EVAL_74_SURFACE_TERM_STRUCTURE_PREDICTIVENESS_COMBINED — options implied-vol term structure -> realized-vol predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-17T06:39:04Z`
- Task: `EVAL74-SURFACE-TERM-STRUCTURE-PREDICTIVENESS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (EVAL-71 floor + term-structure adequacy)

| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |
|---|---|---|---|---|
| BTC | True | 8 | 557 | True |
| ETH | True | 8 | 329 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 12 | 0.0981 | term_ratio::bar300.0::h24 | 0 | False |
| ETH | 12 | 0.3621 | term_slope::bar300.0::h72 | 8 | True |

## Pooled

- BH-FDR rejected: ['ETH::term_slope::bar60.0::h6', 'ETH::term_slope::bar60.0::h24', 'ETH::term_slope::bar60.0::h72', 'ETH::term_slope::bar300.0::h72', 'ETH::term_ratio::bar60.0::h6', 'ETH::term_ratio::bar60.0::h24', 'ETH::term_ratio::bar60.0::h72', 'ETH::term_ratio::bar300.0::h72', 'ETH::term_slope::bar300.0::h6', 'ETH::term_ratio::bar300.0::h6']
- All underlyings pass: False
