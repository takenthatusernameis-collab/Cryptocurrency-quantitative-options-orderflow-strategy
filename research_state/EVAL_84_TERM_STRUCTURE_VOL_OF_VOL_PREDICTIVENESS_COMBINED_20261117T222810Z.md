# EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS_COMBINED — term structure -> forward vol-of-vol predictiveness

- Generated: `2026-11-17T22:28:10Z`
- Task: `EVAL84-TERM-STRUCTURE-VOL-OF-VOL-PREDICTIVENESS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 12 | 0.0510 | term_slope::bar300.0::h6 | 0 | False |
| ETH | 12 | 0.3652 | term_slope::bar300.0::h72 | 7 | True |

## Pooled

- BH-FDR rejected: ['ETH::term_slope::bar60.0::h6', 'ETH::term_slope::bar300.0::h72', 'ETH::term_ratio::bar60.0::h6', 'ETH::term_ratio::bar60.0::h72', 'ETH::term_ratio::bar300.0::h72', 'ETH::term_slope::bar60.0::h72', 'ETH::term_slope::bar300.0::h6', 'ETH::term_ratio::bar300.0::h6', 'ETH::term_ratio::bar60.0::h24', 'ETH::term_slope::bar60.0::h24']
- All underlyings pass: False
- Campaign state: EVAL_84_TERM_STRUCTURE_VOL_OF_VOL_PREDICTIVENESS
