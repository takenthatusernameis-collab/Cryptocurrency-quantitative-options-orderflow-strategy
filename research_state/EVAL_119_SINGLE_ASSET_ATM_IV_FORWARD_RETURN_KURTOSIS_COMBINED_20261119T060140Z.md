# EVAL_119_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_KURTOSIS_COMBINED — atm_iv -> forward realized return kurtosis (Spearman rank IC)

- Generated: `2026-11-19T06:01:40Z`
- Task: `EVAL119-SINGLE-ASSET-ATM-IV-FORWARD-RETURN-KURTOSIS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between causal near-ATM IV level and forward own-asset realized return kurtosis on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | floor ok | option trades | near-ATM trades | perp candles | span (s) |
|---|---|---|---|---|---|
| BTC | True | 2748 | 2331 | 1441 | 86400.0 |
| ETH | True | 3547 | 1509 | 1441 | 86400.0 |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.0825 | atm_iv::bar300.0::h6 | 0 | False |
| ETH | 6 | 0.1175 | atm_iv::bar300.0::h72 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All underlyings pass: False
- Campaign state: EVAL_119_SINGLE_ASSET_ATM_IV_FORWARD_RETURN_KURTOSIS
