# EVAL_96_SINGLE_ASSET_TERM_SLOPE_FORWARD_VRP_COMBINED — term slope -> forward VRP predictiveness (Spearman rank IC)

- Generated: `2026-11-18T11:02:48Z`
- Task: `EVAL96-SINGLE-ASSET-TERM-SLOPE-FORWARD-VRP`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Verdict detail: wrapper-free Spearman rank IC between causal term_slope (near-minus-far ATM IV) and forward VRP (implied vol - forward realized vol) on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying term floor (EVAL-74, reused verbatim)

| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |
|---|---|---|---|---|
| BTC | True | 8 | 557 | True |
| ETH | True | 8 | 329 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.4243 | term_slope::bar60.0::h72 | 6 | True |
| ETH | 6 | 0.0960 | term_slope::bar300.0::h72 | 0 | False |

## Pooled

- BH-FDR rejected: ['BTC::term_slope::bar60.0::h6', 'BTC::term_slope::bar60.0::h24', 'BTC::term_slope::bar60.0::h72', 'BTC::term_slope::bar300.0::h6', 'BTC::term_slope::bar300.0::h24', 'BTC::term_slope::bar300.0::h72']
- All underlyings pass: False
- Campaign state: EVAL_96_SINGLE_ASSET_TERM_SLOPE_FORWARD_VRP
