# EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS_COMBINED — skew -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-19T07:18:09Z`
- Task: `EVAL121-SINGLE-ASSET-SKEW-FORWARD-RETURN-KURTOSIS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between causal near-ATM put-call skew and forward own-asset realized return kurtosis on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | floor ok | option trades | near-ATM trades | perp candles | span (s) |
|---|---|---|---|---|---|
| BTC | True | 2748 | 2331 | 1441 | 86400.0 |
| ETH | True | 3547 | 1509 | 1441 | 86400.0 |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.0553 | skew::bar60.0::h24 | 0 | False |
| ETH | 6 | 0.1921 | skew::bar300.0::h6 | 1 | True |

## Pooled

- BH-FDR rejected: ['ETH::skew::bar300.0::h6', 'BTC::skew::bar60.0::h6']
- All underlyings pass: False
- Campaign state: EVAL_121_SINGLE_ASSET_SKEW_FORWARD_RETURN_KURTOSIS
