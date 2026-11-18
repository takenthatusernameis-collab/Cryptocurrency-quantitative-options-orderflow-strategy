# EVAL_103_SINGLE_ASSET_SKEW_FORWARD_SIGNED_RETURN_COMBINED — skew -> forward signed return (Spearman rank IC)

- Generated: `2026-11-18T18:47:10Z`
- Task: `EVAL103-SINGLE-ASSET-SKEW-FORWARD-SIGNED-RETURN`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between causal near-ATM implied-vol skew and forward own-asset signed log-return on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | floor ok | option trades | near-ATM trades | perp candles | span (s) |
|---|---|---|---|---|---|
| BTC | True | 2748 | 2331 | 1441 | 86400.0 |
| ETH | True | 3547 | 1509 | 1441 | 86400.0 |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.0462 | skew::bar300.0::h72 | 0 | False |
| ETH | 6 | 0.2195 | skew::bar300.0::h72 | 5 | True |

## Pooled

- BH-FDR rejected: ['ETH::skew::bar60.0::h6', 'ETH::skew::bar60.0::h24', 'ETH::skew::bar300.0::h6', 'ETH::skew::bar300.0::h72', 'ETH::skew::bar60.0::h72', 'ETH::skew::bar300.0::h24']
- All underlyings pass: False
- Campaign state: EVAL_103_SINGLE_ASSET_SKEW_FORWARD_SIGNED_RETURN
