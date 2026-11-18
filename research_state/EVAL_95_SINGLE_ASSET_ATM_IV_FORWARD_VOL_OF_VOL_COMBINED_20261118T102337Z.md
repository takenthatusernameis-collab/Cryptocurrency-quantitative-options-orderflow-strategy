# EVAL_95_SINGLE_ASSET_ATM_IV_FORWARD_VOL_OF_VOL_COMBINED — atm_iv level -> forward vol-of-vol predictiveness

- Generated: `2026-11-18T10:23:37Z`
- Task: `EVAL95-SINGLE-ASSET-ATM-IV-FORWARD-VOL-OF-VOL`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | -0.0172 | atm_iv::bar300.0::h24 | 0 | False |
| ETH | 6 | 0.2118 | atm_iv::bar300.0::h72 | 2 | True |

## Pooled

- BH-FDR rejected: ['ETH::atm_iv::bar300.0::h24', 'ETH::atm_iv::bar300.0::h72']
- All underlyings pass: False
- Campaign state: EVAL_95_SINGLE_ASSET_ATM_IV_FORWARD_VOL_OF_VOL
