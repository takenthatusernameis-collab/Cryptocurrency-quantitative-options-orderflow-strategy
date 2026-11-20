# EVAL_134_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_KURTOSIS_COMBINED — cross-asset atm_iv spillover -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-20T05:15:33Z`
- Task: `EVAL134-CROSS-ASSET-ATM-IV-SPILLOVER-FORWARD-RETURN-KURTOSIS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between the causal cross-asset near-ATM IV spillover (other asset's level) and forward own-asset realized return kurtosis on real captures
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
| ETH->BTC | 6 | 0.2731 | ETH->BTC::atm_iv::bar300.0::h72 | 1 | True |
| BTC->ETH | 6 | 0.1224 | BTC->ETH::atm_iv::bar300.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC<-ETH::atm_iv::bar300.0::h72', 'ETH<-BTC::atm_iv::bar60.0::h72']
- All targets pass: False
- Campaign state: EVAL_134_CROSS_ASSET_ATM_IV_SPILLOVER_FORWARD_RETURN_KURTOSIS
