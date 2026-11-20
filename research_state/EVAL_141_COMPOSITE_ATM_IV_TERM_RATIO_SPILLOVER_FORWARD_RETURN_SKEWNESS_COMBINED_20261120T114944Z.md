# EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS_COMBINED — composite cross-asset spillover -> forward realized return skewness (Spearman rank IC)

- Generated: `2026-11-20T11:49:44Z`
- Task: `EVAL141-COMPOSITE-ATM-IV-TERM-RATIO-SPILLOVER-FORWARD-RETURN-SKEWNESS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the equal-weight z-score composite of the cross-asset atm_iv and term_ratio spillovers and forward own-asset realized return skewness on real captures; GO additionally requires the composite to beat each single-leg best IC on both underlyings
- Floor OK: True (underlyings BTC, ETH)
- Aligned common bars by grid: {'60.0': 1370, '300.0': 274}

## Per-underlying EVAL-71 surface floor

| underlying | surface floor ok | option trades | near-ATM | perp candles | span (s) |
|---|---|---|---|---|---|
| BTC | None | None | None | None | None |
| ETH | None | None | None | None | None |

## Per-target (composite best config vs single-leg best IC)

| target <- signal | configs | composite best IC | atm_iv leg best | term_ratio leg best | beats both legs | n pass | any pass | best config |
|---|---|---|---|---|---|---|---|---|
| ETH->BTC | 6 | 0.4979 | 0.4039 | 0.2613 | True | 2 | True | ETH->BTC::composite_atm_iv_term_ratio::bar300.0::h72 |
| BTC->ETH | 6 | 0.4151 | 0.1173 | 0.4878 | False | 3 | True | BTC->ETH::composite_atm_iv_term_ratio::bar300.0::h24 |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::composite_atm_iv_term_ratio::bar300.0::h24', 'BTC<-ETH::composite_atm_iv_term_ratio::bar300.0::h72', 'ETH<-BTC::composite_atm_iv_term_ratio::bar60.0::h24', 'ETH<-BTC::composite_atm_iv_term_ratio::bar60.0::h72', 'ETH<-BTC::composite_atm_iv_term_ratio::bar300.0::h24']
- All targets pass: True
- All targets beat both legs: False
- Campaign state: EVAL_141_COMPOSITE_ATM_IV_TERM_RATIO_SPILLOVER_FORWARD_RETURN_SKEWNESS
