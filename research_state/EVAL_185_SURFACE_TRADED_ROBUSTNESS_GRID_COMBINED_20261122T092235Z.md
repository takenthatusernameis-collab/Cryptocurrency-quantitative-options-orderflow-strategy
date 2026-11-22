# EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID_COMBINED — surface-line traded-form ROBUSTNESS GRID (is the EVAL-184 surface NO-GO a monetization/horizon artifact?)

- Generated: `2026-11-22T09:22:35Z`
- Task: `EVAL185-SURFACE-TRADED-ROBUSTNESS-GRID`
- Verdict: **NO-GO CONFIRMED (PASS)**
- Floor OK: True (underlyings BTC, ETH)
- Disjointness OK: True
- Missing underlyings: []
- Max pooled returns: 2000 (>= 790 required; power adequate: True)
- Grid: 45 configs (['skew', 'atm_iv', 'term_slope'] x [60.0, 120.0, 240.0, 300.0, 360.0] x [0.5, 1.0, 2.0])

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

## Pooled per-config (signal x horizon x cost haircut)
| signal | bar_s | cost | pooled n | power ok | Sharpe | max-DD | perm_p | CI95 | BH-rej | pass |
|---|---|---|---|---|---|---|---|---|---|---|
| atm_iv | 120 | 0.5 | 1998 | True | -0.0586 | 0.0969 | 0.8841 | [-0.5836, 0.4757] | no | False |
| atm_iv | 120 | 1 | 1998 | True | -0.0699 | 0.1010 | 0.8591 | [-0.5968, 0.4648] | no | False |
| atm_iv | 120 | 2 | 1998 | True | -0.0925 | 0.1126 | 0.8112 | [-0.6221, 0.4430] | no | False |
| atm_iv | 240 | 0.5 | 2000 | True | -0.0594 | 0.0969 | 0.8721 | [-0.5607, 0.5018] | no | False |
| atm_iv | 240 | 1 | 2000 | True | -0.0707 | 0.1016 | 0.8462 | [-0.5722, 0.4917] | no | False |
| atm_iv | 240 | 2 | 2000 | True | -0.0933 | 0.1132 | 0.7902 | [-0.5969, 0.4712] | no | False |
| atm_iv | 300 | 0.5 | 2000 | True | -0.0571 | 0.0971 | 0.8781 | [-0.5599, 0.5128] | no | False |
| atm_iv | 300 | 1 | 2000 | True | -0.0681 | 0.1006 | 0.8591 | [-0.5726, 0.5018] | no | False |
| atm_iv | 300 | 2 | 2000 | True | -0.0901 | 0.1121 | 0.8022 | [-0.5996, 0.4816] | no | False |
| atm_iv | 360 | 0.5 | 1666 | True | -0.0526 | 0.0880 | 0.8891 | [-0.7017, 0.5565] | no | False |
| atm_iv | 360 | 1 | 1666 | True | -0.0655 | 0.0888 | 0.8711 | [-0.7150, 0.5435] | no | False |
| atm_iv | 360 | 2 | 1666 | True | -0.0912 | 0.0905 | 0.8172 | [-0.7430, 0.5155] | no | False |
| atm_iv | 60 | 0.5 | 1998 | True | -0.0571 | 0.0971 | 0.8811 | [-0.5791, 0.4917] | no | False |
| atm_iv | 60 | 1 | 1998 | True | -0.0682 | 0.1006 | 0.8571 | [-0.5914, 0.4815] | no | False |
| atm_iv | 60 | 2 | 1998 | True | -0.0902 | 0.1121 | 0.8102 | [-0.6104, 0.4610] | no | False |
| skew | 120 | 0.5 | 1998 | True | -0.0682 | 0.1324 | 0.8621 | [-0.6113, 0.4914] | no | False |
| skew | 120 | 1 | 1998 | True | -0.1028 | 0.1466 | 0.7802 | [-0.6493, 0.4587] | no | False |
| skew | 120 | 2 | 1998 | True | -0.1719 | 0.1755 | 0.6354 | [-0.7321, 0.3871] | no | False |
| skew | 240 | 0.5 | 2000 | True | -0.1583 | 0.1658 | 0.6713 | [-0.6889, 0.4008] | no | False |
| skew | 240 | 1 | 2000 | True | -0.1931 | 0.1822 | 0.6074 | [-0.7261, 0.3664] | no | False |
| skew | 240 | 2 | 2000 | True | -0.2624 | 0.2140 | 0.4835 | [-0.7993, 0.2967] | no | False |
| skew | 300 | 0.5 | 2000 | True | -0.0875 | 0.1324 | 0.8072 | [-0.5928, 0.4928] | no | False |
| skew | 300 | 1 | 2000 | True | -0.1202 | 0.1444 | 0.7363 | [-0.6321, 0.4610] | no | False |
| skew | 300 | 2 | 2000 | True | -0.1855 | 0.1751 | 0.6124 | [-0.7049, 0.3937] | no | False |
| skew | 360 | 0.5 | 1666 | True | -0.0102 | 0.1148 | 0.9800 | [-0.6396, 0.6485] | no | False |
| skew | 360 | 1 | 1666 | True | -0.0507 | 0.1255 | 0.8941 | [-0.6848, 0.6056] | no | False |
| skew | 360 | 2 | 1666 | True | -0.1316 | 0.1480 | 0.7403 | [-0.7673, 0.5223] | no | False |
| skew | 60 | 0.5 | 1998 | True | -0.0289 | 0.1212 | 0.9351 | [-0.5693, 0.5362] | no | False |
| skew | 60 | 1 | 1998 | True | -0.0616 | 0.1256 | 0.8681 | [-0.6081, 0.4994] | no | False |
| skew | 60 | 2 | 1998 | True | -0.1269 | 0.1536 | 0.7313 | [-0.6895, 0.4317] | no | False |
| term_slope | 120 | 0.5 | 1998 | True | 0.1849 | 0.0851 | 0.6144 | [-0.3347, 0.7078] | no | False |
| term_slope | 120 | 1 | 1998 | True | 0.1514 | 0.0924 | 0.6723 | [-0.3715, 0.6721] | no | False |
| term_slope | 120 | 2 | 1998 | True | 0.0845 | 0.1115 | 0.8232 | [-0.4548, 0.5867] | no | False |
| term_slope | 240 | 0.5 | 2000 | True | 0.1448 | 0.0791 | 0.6963 | [-0.3319, 0.6204] | no | False |
| term_slope | 240 | 1 | 2000 | True | 0.1148 | 0.0791 | 0.7632 | [-0.3726, 0.5906] | no | False |
| term_slope | 240 | 2 | 2000 | True | 0.0548 | 0.0930 | 0.8941 | [-0.4343, 0.5211] | no | False |
| term_slope | 300 | 0.5 | 2000 | True | 0.0617 | 0.1320 | 0.8501 | [-0.5277, 0.5974] | no | False |
| term_slope | 300 | 1 | 2000 | True | 0.0326 | 0.1407 | 0.9221 | [-0.5709, 0.5695] | no | False |
| term_slope | 300 | 2 | 2000 | True | -0.0257 | 0.1578 | 0.9321 | [-0.6386, 0.5190] | no | False |
| term_slope | 360 | 0.5 | 1666 | True | 0.3757 | 0.0417 | 0.3576 | [-0.2336, 0.8426] | no | False |
| term_slope | 360 | 1 | 1666 | True | 0.3376 | 0.0426 | 0.4036 | [-0.2811, 0.8085] | no | False |
| term_slope | 360 | 2 | 1666 | True | 0.2612 | 0.0473 | 0.5215 | [-0.3790, 0.7475] | no | False |
| term_slope | 60 | 0.5 | 1998 | True | 0.1936 | 0.0854 | 0.6004 | [-0.3165, 0.7095] | no | False |
| term_slope | 60 | 1 | 1998 | True | 0.1614 | 0.0857 | 0.6683 | [-0.3524, 0.6677] | no | False |
| term_slope | 60 | 2 | 1998 | True | 0.0968 | 0.0879 | 0.8012 | [-0.4251, 0.5889] | no | False |

## Pooled
- BH-FDR rejected configs: []
- Pass configs: []
- Cost-robust (signal,horizon) pairs: []
- Power adequate: True
- Campaign state: EVAL_185_SURFACE_TRADED_ROBUSTNESS_GRID
