# EVAL_100_SINGLE_ASSET_TERM_RATIO_FORWARD_TAIL_ASYMMETRY_COMBINED — term ratio -> forward return-tail asymmetry (Spearman rank IC)

- Generated: `2026-11-18T16:45:59Z`
- Task: `EVAL100-SINGLE-ASSET-TERM-RATIO-FORWARD-TAIL-ASYMMETRY`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between causal term_ratio (near-to-far ATM IV) and forward return-tail asymmetry on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying term floor (EVAL-74, reused verbatim)

| underlying | EVAL-71 floor ok | distinct expiries | bars with term | ok |
|---|---|---|---|---|
| BTC | True | 8 | 557 | True |
| ETH | True | 8 | 329 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.2171 | term_ratio::bar60.0::h72 | 2 | True |
| ETH | 6 | 0.3387 | term_ratio::bar300.0::h72 | 4 | True |

## Pooled

- BH-FDR rejected: ['BTC::term_ratio::bar60.0::h24', 'BTC::term_ratio::bar60.0::h72', 'ETH::term_ratio::bar60.0::h24', 'ETH::term_ratio::bar60.0::h72', 'ETH::term_ratio::bar300.0::h72', 'BTC::term_ratio::bar300.0::h72', 'ETH::term_ratio::bar300.0::h24', 'ETH::term_ratio::bar60.0::h6', 'BTC::term_ratio::bar60.0::h6', 'BTC::term_ratio::bar300.0::h24', 'ETH::term_ratio::bar300.0::h6']
- All underlyings pass: True
- Campaign state: EVAL_100_SINGLE_ASSET_TERM_RATIO_FORWARD_TAIL_ASYMMETRY
