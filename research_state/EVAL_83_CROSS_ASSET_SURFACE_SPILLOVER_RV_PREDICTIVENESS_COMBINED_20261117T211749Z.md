# EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS_COMBINED — cross-asset options surface lead-lag spillover -> subsequent forward realized volatility (wrapper-free rank IC) falsification

- Generated: `2026-11-17T21:17:49Z`
- Task: `EVAL83-CROSS-ASSET-SURFACE-SPILLOVER-RV-PREDICTIVENESS`
- Verdict: **GO CONFIRMED**
- Verdict detail: wrapper-free information-content test: Spearman rank IC between one crypto's causal options surface and the OTHER crypto's forward realized volatility on the real on-disk captures
- Floor OK: True (underlyings BTC, ETH)

## Per-underlying surface floor (EVAL-71, reused verbatim)

| underlying | n option trades | n near-ATM | n perp candles | span (s) | ok |
|---|---|---|---|---|---|
| BTC | 2748 | 2331 | 1441 | 86400.0 | True |
| ETH | 3547 | 1509 | 1441 | 86400.0 | True |

## Cross-asset common-bar floor (coarser grid)

| pair | bar s | common bars | min | ok |
|---|---|---|---|---|
| BTC->ETH | 300 | 274 | 150 | True |
| ETH->BTC | 300 | 274 | 150 | True |

## Configs (best first by spillover IC)

| leader->target | signal | bar s | horizon | n pairs | spillover IC | partial IC | own IC | perm p | bootstrap 95% CI | pass |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC->ETH | skew | 300 | 24 | 265 | 0.2806 | 0.2429 | 0.2628 | 0.0010 | [0.2799, 0.1143, 0.4320] | True |
| BTC->ETH | skew | 300 | 72 | 217 | 0.2685 | 0.2387 | 0.1792 | 0.0010 | [0.2773, 0.1125, 0.4283] | True |
| ETH->BTC | atm_iv | 300 | 72 | 202 | 0.2666 | 0.2506 | -0.4461 | 0.0010 | [0.2620, 0.0955, 0.4073] | True |
| ETH->BTC | skew | 300 | 72 | 202 | 0.2252 | 0.1176 | 0.3792 | 0.0010 | [0.2284, 0.0640, 0.3813] | True |
| ETH->BTC | skew | 300 | 24 | 250 | 0.1982 | 0.1579 | 0.3003 | 0.0010 | [0.2040, 0.0647, 0.3437] | True |
| BTC->ETH | skew | 60 | 72 | 1369 | 0.1708 | 0.1793 | -0.0401 | 0.0010 | [0.1704, 0.0884, 0.2453] | True |
| ETH->BTC | atm_iv | 300 | 24 | 250 | 0.1556 | 0.1656 | -0.0940 | 0.0080 | [0.1543, -0.0231, 0.3148] | False |
| BTC->ETH | skew | 300 | 6 | 274 | 0.1108 | 0.0920 | 0.1088 | 0.0360 | [0.1148, -0.0454, 0.2651] | False |
| BTC->ETH | skew | 60 | 24 | 1370 | 0.0474 | 0.0542 | -0.0388 | 0.0549 | [0.0464, -0.0239, 0.1195] | False |
| ETH->BTC | skew | 300 | 6 | 268 | 0.0425 | 0.0194 | 0.1271 | 0.2468 | [0.0413, -0.1006, 0.1792] | False |
| BTC->ETH | skew | 60 | 6 | 1370 | 0.0411 | 0.0429 | -0.0083 | 0.0749 | [0.0418, -0.0305, 0.1140] | False |
| BTC->ETH | atm_iv | 300 | 24 | 265 | 0.0100 | -0.0109 | 0.2276 | 0.4575 | [0.0098, -0.1624, 0.1678] | False |
| ETH->BTC | skew | 60 | 6 | 1364 | 0.0043 | -0.0027 | 0.0457 | 0.4226 | [0.0050, -0.0667, 0.0705] | False |
| ETH->BTC | skew | 60 | 72 | 1298 | -0.0202 | -0.0556 | 0.2415 | 0.7443 | [-0.0200, -0.1008, 0.0527] | False |
| ETH->BTC | skew | 60 | 24 | 1346 | -0.0221 | -0.0361 | 0.0895 | 0.8042 | [-0.0227, -0.0998, 0.0431] | False |
| ETH->BTC | atm_iv | 300 | 6 | 268 | -0.0386 | -0.0248 | -0.1567 | 0.7453 | [-0.0368, -0.1956, 0.1319] | False |
| ETH->BTC | atm_iv | 60 | 6 | 1364 | -0.0642 | -0.0432 | -0.2044 | 0.9900 | [-0.0646, -0.1371, 0.0051] | False |
| BTC->ETH | atm_iv | 60 | 72 | 1369 | -0.0986 | -0.0944 | -0.0434 | 1.0000 | [-0.0989, -0.1744, -0.0158] | False |
| BTC->ETH | atm_iv | 300 | 6 | 274 | -0.0991 | -0.1000 | 0.0047 | 0.9520 | [-0.0939, -0.2394, 0.0627] | False |
| ETH->BTC | atm_iv | 60 | 72 | 1298 | -0.1087 | -0.0879 | -0.1953 | 1.0000 | [-0.1082, -0.1873, -0.0286] | False |
| ETH->BTC | atm_iv | 60 | 24 | 1346 | -0.1543 | -0.1323 | -0.2563 | 1.0000 | [-0.1547, -0.2283, -0.0775] | False |
| BTC->ETH | atm_iv | 60 | 6 | 1370 | -0.1599 | -0.1557 | -0.0479 | 1.0000 | [-0.1585, -0.2331, -0.0872] | False |
| BTC->ETH | atm_iv | 60 | 24 | 1370 | -0.2156 | -0.2064 | -0.1053 | 1.0000 | [-0.2144, -0.2892, -0.1386] | False |
| BTC->ETH | atm_iv | 300 | 72 | 217 | -0.4396 | -0.4355 | 0.1883 | 1.0000 | [-0.4562, -0.5970, -0.2717] | False |

## Per-direction (ordered pair)

| pair | n_configs | best IC | best partial IC | best config | n_pass | any_pass |
|---|---|---|---|---|---|---|
| BTC->ETH | 12 | 0.2806 | 0.2429 | skew::bar300.0::h24 | 3 | True |
| ETH->BTC | 12 | 0.2666 | 0.2506 | atm_iv::bar300.0::h72 | 3 | True |

## Per-target (does each target receive incoming spillover?)

| target | incoming leaders | n incoming configs | any incoming pass | passing leaders |
|---|---|---|---|---|
| BTC | ETH | 12 | True | ETH |
| ETH | BTC | 12 | True | BTC |

## Pooled

- BH-FDR rejected: ['BTC->ETH::skew::bar60.0::h72', 'BTC->ETH::skew::bar300.0::h24', 'BTC->ETH::skew::bar300.0::h72', 'ETH->BTC::atm_iv::bar300.0::h72', 'ETH->BTC::skew::bar300.0::h24', 'ETH->BTC::skew::bar300.0::h72', 'ETH->BTC::atm_iv::bar300.0::h24']
- All targets receive spillover: True
- Any direction passes: True
- Campaign state: EVAL_83_CROSS_ASSET_SURFACE_SPILLOVER_RV_PREDICTIVENESS
