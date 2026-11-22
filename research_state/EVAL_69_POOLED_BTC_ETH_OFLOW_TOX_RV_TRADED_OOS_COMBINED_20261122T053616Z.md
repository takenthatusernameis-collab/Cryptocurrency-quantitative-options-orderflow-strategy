# EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS_COMBINED — pooled BTC+ETH OOS traded-form net-of-cost monetization of suggestive EVAL-65 slice (tox/imbalance::bar60)

- Generated: `2026-11-22T05:36:16Z`
- Task: `EVAL69-POOLED-BTC-ETH-OFLOW-TOX-RV-TRADED-OOS`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)
- Disjointness OK: True
- Missing underlyings: []
- Max pooled returns: 1998 (>= 790 required; power adequate: True)

## Disjointness (sealed window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)

| underlying | disjoint | overlap s | capture window | span s |
|---|---|---|---|---|
| BTC | True | 0.0 | ['2026-11-18T11:35:59Z', '2026-11-22T04:23:59Z'] | 319680.0 |
| ETH | True | 0.0 | ['2026-11-18T11:35:59Z', '2026-11-22T04:23:59Z'] | 319680.0 |

## Per-underlying floor

| underlying | snaps | surf inst | 5m bars | deribit trades | perp bars | perp span s | common 5m | ok |
|---|---|---|---|---|---|---|---|---|
| BTC | 1066 | 248 | 1001 | 8489 | 1000 | 300000 | 288 | True |
| ETH | 1066 | 240 | 1001 | 6055 | 1000 | 300000 | 282 | True |

## Pooled per-config

| signal | bar_s | underlyings | per-underlying n | pooled n | power ok | Sharpe | max-DD | perm_p | CI95 | pass |
|---|---|---|---|---|---|---|---|---|---|---|
| tox | 60.0 | BTC,ETH | {'BTC': 999, 'ETH': 999} | 1998 | True | 0.1947 | 0.1584 | 0.5984 | [-0.6723, 0.8753] | False |
| imbalance | 60.0 | BTC,ETH | {'BTC': 999, 'ETH': 999} | 1998 | True | 0.2039 | 0.1693 | 0.5894 | [-0.5885, 0.9354] | False |

## Pooled

- BH-FDR rejected: []
- Pass configs: []
- Power adequate: True
- Campaign state: EVAL_69_POOLED_BTC_ETH_OFLOW_TOX_RV_TRADED_OOS
