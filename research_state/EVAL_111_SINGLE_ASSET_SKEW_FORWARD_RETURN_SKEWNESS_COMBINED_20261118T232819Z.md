# EVAL_111_SINGLE_ASSET_SKEW_FORWARD_RETURN_SKEWNESS_COMBINED — skew -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-18T23:28:19Z`
- Task: `EVAL111-SINGLE-ASSET-SKEW-FORWARD-RETURN-SKEWNESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between causal near-ATM put-call skew and forward own-asset realized return skewness on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | floor ok | option trades | near-ATM trades | perp candles | span (s) |
|---|---|---|---|---|---|
| BTC | True | 2748 | 2331 | 1441 | 86400.0 |
| ETH | True | 3547 | 1509 | 1441 | 86400.0 |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.1717 | skew::bar300.0::h6 | 3 | True |
| ETH | 6 | 0.2726 | skew::bar60.0::h72 | 5 | True |

## Pooled

- BH-FDR rejected: ['BTC::skew::bar60.0::h6', 'ETH::skew::bar60.0::h6', 'ETH::skew::bar60.0::h24', 'ETH::skew::bar60.0::h72', 'BTC::skew::bar300.0::h6', 'ETH::skew::bar300.0::h72', 'BTC::skew::bar60.0::h24', 'ETH::skew::bar300.0::h6', 'BTC::skew::bar300.0::h72']
- All underlyings pass: True
- Campaign state: EVAL_111_SINGLE_ASSET_SKEW_FORWARD_RETURN_SKEWNESS
