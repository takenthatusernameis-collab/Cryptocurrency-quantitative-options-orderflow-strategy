# EXCHANGE_EXPORT_ADAPTERS_23B — EXCHANGE EXPORT ADAPTERS (EVAL-23B)

- generated_at: 2026-11-13T23:52:47Z
- overall_verdict: **NO-GO**
- reason: adapter parsed export but tape is below EVAL-23 adequacy floors (returns 1/1000, windows 0/20)
- adapter_verdict: PASS
- trading_mode: paper
- data_provenance: exchange_export (authenticity_verified=false)
- source_path: `data/examples/exchange_exports/okx_btcusdt_sample.csv`
- venue/symbol: `okx` / `BTCUSDT`
- format: csv
- n_trades: 3
- span_seconds: 30.0
- start/end: 2026-01-01T00:00:00Z → 2026-01-01T00:00:30Z
- canonical_fingerprint: `744a37d319f60205bf6fc03d57be715fa47771120600f7db77f392af84a76676`
- normalized_tape: data/examples/normalized/orderflow_okx_BTCUSDT_20261113T235247Z.json
- floors: {'min_returns': 1000, 'min_windows': 20, 'bar_duration_seconds': 15.0}
- adequacy: 1/1000 returns, 0/20 windows, adequate=false

## Supported export formats

| venue | csv headers | json shape | timestamps | sides |
|---|---|---|---|---|
| okx | `tradeId, instId, px, sz, side, ts` | `list | {data: [...]} | {trades: [...]}` | ISO-8601, epoch-ms | buy, sell |
| binance | `Id, Price, Qty, QuoteQty, Time, IsBuyerMaker` | `list | {trades: [...]} | {data: [...]}` | ISO-8601, epoch-ms | isBuyerMaker=true -> sell, isBuyerMaker=false -> buy |
| deribit | `trade_id, timestamp, instrument_name, price, amount, direction` | `list | {result: [...]} | {trades: [...]}` | epoch-ms, ISO-8601 | buy, sell |

## Readiness

Offline deterministic adapter; no network, no `.env`, no live trading. A parsed export is not proof of real provenance; EVAL-22 must validate the normalized tape before EVAL-23 uses it.
