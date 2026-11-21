# EVAL_172_SINGLE_ASSET_ATM_IV_FORWARD_VARIANCE_COMBINED — single-asset atm_iv -> forward realized return variance predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-21T21:14:58Z`
- Task: `EVAL172-SINGLE-ASSET-ATM-IV-FORWARD-VARIANCE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying floor (EVAL-71 surface floor)

| underlying | option trades | near-ATM | perp candles | perp span s | ok |
|---|---|---|---|---|---|
| BTC | 2748 | 2331 | 1441 | 86400 | True |
| ETH | 3547 | 1509 | 1441 | 86400 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.0073 | atm_iv::bar300.0::h24 | 0 | False |
| ETH | 6 | 0.2392 | atm_iv::bar300.0::h24 | 2 | True |

## Pooled

- BH-FDR rejected: ['ETH::atm_iv::bar300.0::h24', 'ETH::atm_iv::bar300.0::h72']
- All underlyings pass: False
