# EVAL_187_REAL_DATA_READINESS_AUDIT — real-data readiness audit (non-verdict)

- Generated: `2026-11-28T06:56:25Z`
- Task: `EVAL187-REAL-DATA-READINESS-AUDIT`
- Verdict rung: `False`
- Audit status: **PASS**
- Captures scanned: `8`
- Bytes scanned: `603664515`
- Records scanned: `3136613`
- Surface snapshots: `4645`
- Option trades: `29342`
- Perp candles: `22208`
- OKX perp trades: `3080418`

## Status counts

| status | count |
|---|---:|
| OK | 8 |
| SPARSE | 0 |
| DEGENERATE | 0 |
| ERROR | 0 |

## Issue counts

| issue | count |
|---|---:|
| none | 0 |

## Captures

| relative path | underlying | status | span s | snaps | quotes | opt trades | perp candles | okx trades | issues |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| data/raw/eval60/three_way_BTC_20261115T232807Z.json | BTC | OK | 86400.0 | 289 | 28711 | 3068 | 1441 | 356839 |  |
| data/raw/eval60/three_way_ETH_20261116T001342Z.json | ETH | OK | 86400.0 | 289 | 75179 | 4289 | 1441 | 231050 |  |
| data/raw/eval61/three_way_BTC_20261116T005923Z.json | BTC | OK | 86400.0 | 289 | 74998 | 6872 | 1441 | 337531 |  |
| data/raw/eval61/three_way_BTC_20261116T011441Z.json | BTC | OK | 86400.0 | 289 | 25125 | 2748 | 1441 | 319777 |  |
| data/raw/eval61/three_way_ETH_20261116T022541Z.json | ETH | OK | 86400.0 | 289 | 76735 | 3558 | 1441 | 176925 |  |
| data/raw/eval67/three_way_BTC_20261120T002428Z.json | BTC | OK | 319680.0 | 1066 | 71328 | 3443 | 5001 | 543520 |  |
| data/raw/eval68/three_way_BTC_20261120T005250Z.json | BTC | OK | 319680.0 | 1067 | 69626 | 3469 | 5001 | 543522 |  |
| data/raw/eval68/three_way_ETH_20261120T005250Z.json | ETH | OK | 319680.0 | 1067 | 78156 | 1895 | 5001 | 571254 |  |

## Forward capture

- Directory: `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/data/raw/eval185cap`
- File count: `0`
- All OK: `False`
- Statuses: ``

Run `python3 scripts/eval186_forward_data_preflight.py` for the authoritative EVAL-186 forward-data verdict.
