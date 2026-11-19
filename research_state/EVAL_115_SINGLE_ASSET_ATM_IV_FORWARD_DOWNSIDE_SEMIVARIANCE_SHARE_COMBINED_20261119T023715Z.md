# EVAL_115_SINGLE_ASSET_ATM_IV_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED — causal near-ATM implied vol -> forward downside-semivariance share (Spearman rank IC)

- Generated: `2026-11-19T02:37:15Z`
- Task: `EVAL115-SINGLE-ASSET-ATM-IV-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between causal near-ATM implied vol and forward downside-semivariance share on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | n option trades | n near-ATM | n perp candles | span (s) | ok |
|---|---|---|---|---|---|

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.1204 | atm_iv::bar300.0::h72 | 0 | False |
| ETH | 6 | 0.0729 | atm_iv::bar60.0::h24 | 1 | True |

## Pooled

- BH-FDR rejected: ['ETH::atm_iv::bar60.0::h24']
- All underlyings pass: False
- Campaign state: EVAL_115_SINGLE_ASSET_ATM_IV_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE
