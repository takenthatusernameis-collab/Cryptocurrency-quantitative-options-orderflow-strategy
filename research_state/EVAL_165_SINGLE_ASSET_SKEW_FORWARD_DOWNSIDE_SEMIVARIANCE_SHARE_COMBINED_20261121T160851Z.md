# EVAL_165_SINGLE_ASSET_SKEW_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE_COMBINED — causal near-ATM implied-vol skew -> forward downside-semivariance share (Spearman rank IC)

- Generated: `2026-11-21T16:08:51Z`
- Task: `EVAL165-SINGLE-ASSET-SKEW-FORWARD-DOWNSIDE-SEMIVARIANCE-SHARE`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between causal near-ATM implied-vol surface SKEW and forward downside-semivariance share on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | n option trades | n near-ATM | n perp candles | span (s) | ok |
|---|---|---|---|---|---|

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | -0.0114 | skew::bar60.0::h72 | 0 | False |
| ETH | 6 | -0.0980 | skew::bar300.0::h24 | 0 | False |

## Pooled

- BH-FDR rejected: []
- All underlyings pass: False
- Campaign state: EVAL_165_SINGLE_ASSET_SKEW_FORWARD_DOWNSIDE_SEMIVARIANCE_SHARE
