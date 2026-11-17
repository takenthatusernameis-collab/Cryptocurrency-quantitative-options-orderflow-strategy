# EVAL_86_SURFACE_SKEW_FORWARD_VRP_PREDICTIVENESS_COMBINED — causal put-call skew -> forward VRP predictiveness (Spearman rank IC) falsification

- Generated: `2026-11-17T23:40:08Z`
- Task: `EVAL86-SURFACE-SKEW-FORWARD-VRP-PREDICTIVENESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free Spearman rank IC between causal put-call skew and forward volatility risk premium (implied vol - forward realized vol) on real captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | n option trades | n near-ATM | n perp candles | span (s) | ok |
|---|---|---|---|---|---|

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 6 | 0.1448 | skew::bar60.0::h72 | 3 | True |
| ETH | 6 | 0.3019 | skew::bar300.0::h24 | 6 | True |

## Pooled

- BH-FDR rejected: ['BTC::skew::bar60.0::h6', 'BTC::skew::bar60.0::h24', 'BTC::skew::bar60.0::h72', 'ETH::skew::bar60.0::h6', 'ETH::skew::bar60.0::h24', 'ETH::skew::bar60.0::h72', 'ETH::skew::bar300.0::h6', 'ETH::skew::bar300.0::h24', 'ETH::skew::bar300.0::h72', 'BTC::skew::bar300.0::h6', 'BTC::skew::bar300.0::h24', 'BTC::skew::bar300.0::h72']
- All underlyings pass: True
- Campaign state: EVAL_86_SURFACE_SKEW_FORWARD_VRP_PREDICTIVENESS
