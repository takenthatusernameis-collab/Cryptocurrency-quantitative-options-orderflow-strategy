# EVAL_173_SINGLE_ASSET_SKEW_FORWARD_VARIANCE_COMBINED — single-asset skew -> forward realized return variance

- Generated: `2026-11-21T22:01:12Z`
- Task: `EVAL173-SINGLE-ASSET-SKEW-FORWARD-VARIANCE`
- Verdict: **GO CONFIRMED**
- Floor OK: True (underlyings BTC, ETH)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.3353 | skew::bar300.0::h72 | 4 | True |
| ETH | 6 | 0.2799 | skew::bar300.0::h24 | 2 | True |

## Pooled

- BH-FDR rejected: ['BTC::skew::bar60.0::h72', 'BTC::skew::bar300.0::h24', 'BTC::skew::bar300.0::h72', 'ETH::skew::bar300.0::h24', 'BTC::skew::bar60.0::h24', 'ETH::skew::bar300.0::h72', 'BTC::skew::bar300.0::h6', 'ETH::skew::bar300.0::h6']
- All underlyings pass: True
