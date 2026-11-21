# EVAL_164_SINGLE_ASSET_SKEW_FORWARD_CVAR_COMBINED — single-asset skew -> forward CVaR (expected shortfall) predictiveness (wrapper-free rank IC) falsification

- Generated: `2026-11-21T15:05:32Z`
- Task: `EVAL164-SINGLE-ASSET-SKEW-FORWARD-CVAR`
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
| BTC | 6 | -0.0092 | skew::bar300.0::h72 | 0 | False |
| ETH | 6 | 0.1908 | skew::bar300.0::h72 | 4 | True |

## Pooled

- BH-FDR rejected: ['ETH::skew::bar60.0::h6', 'ETH::skew::bar60.0::h24', 'ETH::skew::bar60.0::h72', 'ETH::skew::bar300.0::h72']
- All underlyings pass: False
