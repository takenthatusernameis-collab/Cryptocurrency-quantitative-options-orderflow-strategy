# EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS_COMBINED — pooled BTC+ETH OOS replication of suggestive EVAL-65 slice (tox/imbalance::bar60::h72)

- Generated: `2026-11-22T05:33:27Z`
- Task: `EVAL68-POOLED-BTC-ETH-OFLOW-TOX-RV-OOS`
- Verdict: **GO CONFIRMED**
- Floor OK: True (underlyings BTC, ETH)
- Disjointness OK: True
- Missing underlyings: []
- Max pooled pairs: 1856 (>= 790 required; power adequate: True)

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

| signal | bar_s | horizon | underlyings | per-underlying n | pooled n | power ok | IC | perm_p | CI95 | pass |
|---|---|---|---|---|---|---|---|---|---|---|
| tox | 60.0 | 72 | BTC,ETH | {'BTC': 928, 'ETH': 928} | 1856 | True | -0.0060 | 0.6114 | [-0.0740, 0.0499] | False |
| imbalance | 60.0 | 72 | BTC,ETH | {'BTC': 928, 'ETH': 928} | 1856 | True | 0.1396 | 0.0010 | [0.0809, 0.1976] | True |

## Pooled

- BH-FDR rejected: ['imbalance::bar60.0::h72']
- Pass configs: ['imbalance::bar60.0::h72']
- Power adequate: True
- Campaign state: EVAL_68_POOLED_BTC_ETH_OFLOW_TOX_RV_OOS
