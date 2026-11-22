# EVAL_67_BTC_OFLOW_TOX_RV_OOS_COMBINED — BTC OOS replication of suggestive EVAL-65 slice (tox/imbalance::bar60::h72)

- Generated: `2026-11-22T05:31:56Z`
- Task: `EVAL67-BTC-OFLOW-TOX-RV-OOS`
- Verdict: **GO CONFIRMED**
- Floor OK: True (underlyings BTC)
- Disjointness OK: True

## Disjointness (sealed BTC window 2026-11-09T06:48:16Z..2026-11-16T06:48:16Z)

| underlying | disjoint | overlap s | capture window | span s |
|---|---|---|---|---|
| BTC | True | 0.0 | ['2026-11-18T11:35:59Z', '2026-11-22T04:23:59Z'] | 319680.0 |

## Per-underlying floor

| underlying | snaps | surf inst | 5m bars | deribit trades | perp bars | perp span s | common 5m | ok |
|---|---|---|---|---|---|---|---|---|
| BTC | 1066 | 248 | 1001 | 8489 | 1000 | 300000 | 288 | True |

## Per-underlying (best config by Spearman IC)

| underlying | configs | best IC | best config | n pass | any pass |
|---|---|---|---|---|---|
| BTC | 2 | 0.0962 | imbalance::bar60.0::h72 | 1 | True |

## Per-config

| underlying | signal | bar_s | horizon | n_pairs | IC | perm_p | CI95 | pass |
|---|---|---|---|---|---|---|---|---|
| BTC | tox | 60.0 | 72 | 928 | -0.1418 | 0.9990 | [-0.2221, -0.0577] | False |
| BTC | imbalance | 60.0 | 72 | 928 | 0.0962 | 0.0040 | [0.0099, 0.1797] | True |

## Pooled

- BH-FDR rejected: ['BTC::imbalance::bar60.0::h72']
- All underlyings pass: True
