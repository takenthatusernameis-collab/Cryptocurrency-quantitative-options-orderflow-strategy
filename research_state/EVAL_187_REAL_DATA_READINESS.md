# EVAL_187_REAL_DATA_READINESS_AUDIT — real-data readiness audit (non-verdict)

- Generated: `2026-11-25T18:18:49Z`
- Task: `EVAL187-REAL-DATA-READINESS-AUDIT`
- Verdict rung: `False`
- Audit status: **PASS**
- Captures scanned: `10`
- Bytes scanned: `623919229`
- Records scanned: `3236815`
- Surface snapshots: `4740`
- Option trades: `30821`
- Perp candles: `22675`
- OKX perp trades: `3178579`

## Status counts

| status | count |
|---|---:|
| OK | 10 |
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
| data/raw/eval185cap/three_way_BTC_20261122T110037Z.json | BTC | OK | 319680.0 | 47 | 8850 | 864 | 231 | 62230 |  |
| data/raw/eval185cap/three_way_ETH_20261122T110037Z.json | ETH | OK | 319680.0 | 48 | 8828 | 615 | 236 | 35931 |  |
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
- File count: `2`
- All OK: `True`
- Statuses: `OK, OK`

Run `python3 scripts/eval186_forward_data_preflight.py` for the authoritative EVAL-186 forward-data verdict.
