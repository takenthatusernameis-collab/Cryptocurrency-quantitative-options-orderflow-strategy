# EVAL_73_SURFACE_IV_RV_STABILITY_SPLIT_COMBINED — EVAL-71 predictive-surface temporal stability (disjoint early/late split) falsification

- Generated: `2026-11-17T05:32:37Z`
- Task: `EVAL73-SURFACE-IV-RV-STABILITY-SPLIT`
- Verdict: **GO CONFIRMED**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (EVAL-71 floor + per-half adequacy)

| underlying | EVAL-71 floor ok | early candles | early near-ATM | late candles | late near-ATM | ok |
|---|---|---|---|---|---|---|
| BTC | True | 720 | 1624 | 721 | 707 | True |
| ETH | True | 720 | 971 | 721 | 538 | True |

## Per-underlying (best config by full-sample IC)

| underlying | configs | best IC full | IC early | IC late | best config | n stable | any stable |
|---|---|---|---|---|---|---|---|
| BTC | 12 | 0.3349 | -0.1846 | 0.2427 | skew::bar300.0::h72 | 2 | True |
| ETH | 12 | 0.2628 | 0.3425 | 0.2668 | skew::bar300.0::h24 | 2 | True |

## Pooled

- BH-FDR rejected: ['BTC::skew::bar60.0::h72', 'BTC::skew::bar300.0::h24', 'BTC::skew::bar300.0::h72', 'ETH::atm_iv::bar300.0::h24', 'ETH::skew::bar300.0::h24', 'BTC::skew::bar60.0::h24', 'ETH::atm_iv::bar300.0::h72', 'ETH::skew::bar300.0::h72', 'BTC::skew::bar300.0::h6', 'BTC::skew::bar60.0::h6']
- All underlyings stable: True
