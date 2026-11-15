# EVAL_45_ETH_TAPE_ACQUISITION — real ETH orderflow tape acquisition

- **Generated:** 2026-11-15T01:26:56.157262Z
- **Task ID:** `INIT-2026-11-15T01:26:56.157262Z-EVAL-45-ACQUIRE-ETH-WINDOWS`
- **Artifact kind:** `data_acquisition` (no performance verdict)
- **Venue / instrument:** `okx` / `ETH-USD-SWAP` (symbol `ETH`)
- **Provenance:** okx_public_read_only_history_trades (authenticated=false, authenticity_verified=false)
- **Floors:** min_trades=10000, min_bars=420, bar=15.0s
- **Windows:** 5 (total 172100 trades); all disjoint: True; floors met: True

## Windows

| window | trades | bars | first trade (UTC) | last trade (UTC) | first id | last id | pages | loader | sha256 |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 39000 | 421 | 2026-11-14 15:01:50.483000+00:00 | 2026-11-14 16:46:58.858000+00:00 | 507773331 | 507812330 | - | True | `aed739a69139c6a3…` |
| 2 | 23300 | 421 | 2026-11-14 16:46:58.858000+00:00 | 2026-11-14 18:32:07.710000+00:00 | 507812331 | 507835630 | - | True | `39cf2dbceb7d7a0a…` |
| 3 | 12900 | 422 | 2026-11-14 18:32:07.710000+00:00 | 2026-11-14 20:17:35.680000+00:00 | 507835631 | 507848530 | - | True | `b42fa2d999c197ae…` |
| 4 | 59700 | 421 | 2026-11-14 20:17:35.680000+00:00 | 2026-11-14 22:02:41.927000+00:00 | 507848531 | 507908230 | - | True | `692de81c0f606235…` |
| 5 | 37200 | 422 | 2026-11-14 22:02:41.927000+00:00 | 2026-11-14 23:48:00.499000+00:00 | 507908231 | 507945430 | - | True | `29a90bdd4564da37…` |

## Paths
- `data/raw/orderflow_okx_ETH_w01_507773331.json`
- `data/raw/orderflow_okx_ETH_w02_507812331.json`
- `data/raw/orderflow_okx_ETH_w03_507835631.json`
- `data/raw/orderflow_okx_ETH_w04_507848531.json`
- `data/raw/orderflow_okx_ETH_w05_507908231.json`

## Code paths
- `src/data/public_export_acquisition.py`
- `src/campaign/integrated.py`
- `scripts/eval45_acquire_eth_windows.py`
- `tests/test_eval45_acquire_eth_windows.py`
