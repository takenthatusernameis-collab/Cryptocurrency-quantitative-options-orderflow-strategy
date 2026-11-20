# EVAL_136_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_KURTOSIS_COMBINED — cross-asset skew spillover -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-20T05:55:01Z`
- Task: `EVAL136-CROSS-ASSET-SKEW-SPILLOVER-FORWARD-RETURN-KURTOSIS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM put-call skew spillover (other asset's skew) and forward own-asset realized return kurtosis on real captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}

## Per-underlying EVAL-71 surface floor

| underlying | surface floor ok | option trades | near-ATM | perp candles | span (s) |
|---|---|---|---|---|---|
| BTC | None | None | None | None | None |
| ETH | None | None | None | None | None |

## Per-target (best config by Spearman IC)

| target <- signal | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| ETH->BTC | 6 | 0.1158 | ETH->BTC::skew::bar300.0::h6 | 0 | False |
| BTC->ETH | 6 | -0.0031 | BTC->ETH::skew::bar60.0::h6 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All targets pass: False
- Campaign state: EVAL_136_CROSS_ASSET_SKEW_SPILLOVER_FORWARD_RETURN_KURTOSIS
