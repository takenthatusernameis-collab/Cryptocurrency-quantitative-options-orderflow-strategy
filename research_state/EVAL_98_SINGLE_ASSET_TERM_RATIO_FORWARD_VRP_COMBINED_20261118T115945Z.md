# EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP_COMBINED — term ratio -> forward VRP predictiveness (Spearman rank IC)

- Generated: `2026-11-18T11:59:45Z`
- Task: `EVAL98-SINGLE-ASSET-TERM-RATIO-FORWARD-VRP`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between causal term_ratio (near/far ATM IV) and forward VRP (implied vol - forward realized vol) on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying term floor (EVAL-74, reused verbatim)

| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |
|---|---|---|---|---|
| BTC | True | 8 | 557 | True |
| ETH | True | 8 | 329 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.3928 | term_ratio::bar60.0::h24 | 6 | True |
| ETH | 6 | 0.0228 | term_ratio::bar60.0::h6 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC::term_ratio::bar60.0::h6', 'BTC::term_ratio::bar60.0::h24', 'BTC::term_ratio::bar60.0::h72', 'BTC::term_ratio::bar300.0::h6', 'BTC::term_ratio::bar300.0::h24', 'BTC::term_ratio::bar300.0::h72']
- All underlyings pass: False
- Campaign state: EVAL_98_SINGLE_ASSET_TERM_RATIO_FORWARD_VRP
