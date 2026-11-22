# EVAL_184_SURFACE_TRADED_NETFCOST_OOS_COMBINED — surface-line traded-form net-of-cost OOS monetization of the EVAL-177/168/169 surface GOs

- Generated: `2026-11-22T08:17:50Z`
- Task: `EVAL184-SURFACE-TRADED-NETOFCOST-OOS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)
- Disjointness OK: True
- Missing underlyings: []
- Max pooled returns: 2000 (>= 790 required; power adequate: True)

## Disjointness (sealed window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)

| underlying | disjoint | overlap s | capture window | span s |
|---|---|---|---|---|
| BTC | True | 0.0 | ['2026-11-18T13:58:43Z', '2026-11-22T06:46:43Z'] | 319680.0 |
| ETH | True | 0.0 | ['2026-11-18T13:58:43Z', '2026-11-22T06:46:43Z'] | 319680.0 |

## Per-underlying EVAL-64 floor

| underlying | snaps | surf inst | 5m bars | deribit trades | of inst | of span s | perp bars | perp span s | common 5m | ok |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 1067 | 248 | 1001 | 5446 | 206 | 86377 | 287 | 1000 | 300000 | 288 | True |
| ETH | 1067 | 241 | 1001 | 4017 | 173 | 84471 | 281 | 1000 | 300000 | 281 | True |

## Pooled per-config

| signal | bar_s | underlyings | pooled n | power ok | Sharpe | max-DD | perm_p | CI95 | pass |
|---|---|---|---|---|---|---|---|---|---|
| skew | 60.0 | BTC | 999 | True | 0.0855 | 0.0506 | 0.8601 | [-0.5702, 0.7009] | False |
| skew | 300.0 | BTC | 1000 | True | -0.1322 | 0.0893 | 0.7842 | [-0.7519, 0.4679] | False |
| atm_iv | 60.0 | BTC | 999 | True | -0.0953 | 0.0675 | 0.8511 | [-0.6440, 0.4933] | False |
| atm_iv | 300.0 | BTC | 1000 | True | -0.0953 | 0.0675 | 0.8382 | [-0.6453, 0.4836] | False |
| term_slope | 60.0 | BTC | 999 | True | 0.0762 | 0.0544 | 0.9021 | [-0.4951, 0.6892] | False |
| term_slope | 300.0 | BTC | 1000 | True | -0.3397 | 0.1120 | 0.4945 | [-0.9723, 0.3058] | False |
| skew | 60.0 | ETH | 999 | True | -0.1776 | 0.1256 | 0.7153 | [-1.0421, 0.6260] | False |
| skew | 300.0 | ETH | 1000 | True | -0.1119 | 0.0948 | 0.8531 | [-0.9848, 0.8084] | False |
| atm_iv | 60.0 | ETH | 999 | True | -0.0486 | 0.0995 | 0.9221 | [-1.0147, 0.7735] | False |
| atm_iv | 300.0 | ETH | 1000 | True | -0.0485 | 0.0995 | 0.9261 | [-0.9731, 0.7935] | False |
| term_slope | 60.0 | ETH | 999 | True | 0.2313 | 0.0857 | 0.6853 | [-0.6149, 1.0411] | False |
| term_slope | 300.0 | ETH | 1000 | True | 0.2726 | 0.0793 | 0.5704 | [-0.6310, 1.0586] | False |

## Pooled

- BH-FDR rejected: []
- Pass configs: []
- Power adequate: True
- Campaign state: EVAL_184_SURFACE_TRADED_NETFCOST_OOS
