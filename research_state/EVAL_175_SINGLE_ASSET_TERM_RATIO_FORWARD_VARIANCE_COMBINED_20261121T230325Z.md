# EVAL_175_SINGLE_ASSET_TERM_RATIO_FORWARD_VARIANCE_COMBINED — single-asset term_ratio -> forward realized return variance predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-21T23:03:25Z`
- Task: `EVAL175-SINGLE-ASSET-TERM-RATIO-FORWARD-VARIANCE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (EVAL-71 surface floor)

| underlying | option trades | near-ATM | perp candles | perp span s | ok |
|---|---|---|---|---|---|
| BTC | 2748 | 2331 | 1441 | 86400 | True |
| ETH | 3547 | 1509 | 1441 | 86400 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.1113 | term_ratio::bar300.0::h24 | 0 | False |
| ETH | 6 | 0.3256 | term_ratio::bar300.0::h72 | 4 | True |

## Pooled

- BH-FDR rejected: ['ETH::term_ratio::bar60.0::h6', 'ETH::term_ratio::bar60.0::h24', 'ETH::term_ratio::bar60.0::h72', 'ETH::term_ratio::bar300.0::h72', 'ETH::term_ratio::bar300.0::h6', 'BTC::term_ratio::bar300.0::h24']
- All underlyings pass: False
