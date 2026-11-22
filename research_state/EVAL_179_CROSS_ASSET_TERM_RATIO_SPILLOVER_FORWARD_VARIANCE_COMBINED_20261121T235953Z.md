# EVAL_179_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_VARIANCE_COMBINED — cross-asset term_ratio spillover -> forward realized return variance (Spearman rank IC)

- Generated: `2026-11-21T23:59:53Z`
- Task: `EVAL179-CROSS-ASSET-TERM-RATIO-SPILLOVER-FORWARD-VARIANCE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset ATM IV term_ratio spillover (other asset's level) and forward own-asset realized return variance on real captures
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}

## Per-underlying EVAL-71 surface + EVAL-74 term floor

| underlying | eval71 surface floor ok | term adequacy ok | option trades | near-ATM | perp candles | span (s) |
|---|---|---|---|---|---|---|
| BTC | True | True | 2748 | 2331 | 1441 | 86400.0 |
| ETH | True | True | 3547 | 1509 | 1441 | 86400.0 |

## Per-target (best config by Spearman IC)

| target <- signal | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| ETH->BTC | 6 | 0.2731 | ETH->BTC::term_ratio::bar60.0::h72 | 5 | True |
| BTC->ETH | 6 | 0.1458 | BTC->ETH::term_ratio::bar300.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::term_ratio::bar60.0::h6', 'BTC<-ETH::term_ratio::bar60.0::h24', 'BTC<-ETH::term_ratio::bar60.0::h72', 'BTC<-ETH::term_ratio::bar300.0::h72', 'BTC<-ETH::term_ratio::bar300.0::h6', 'ETH<-BTC::term_ratio::bar300.0::h24']
- All targets pass: False
- Campaign state: EVAL_179_CROSS_ASSET_TERM_RATIO_SPILLOVER_FORWARD_VARIANCE
