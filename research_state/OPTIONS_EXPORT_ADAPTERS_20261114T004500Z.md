# OPTIONS_EXPORT_ADAPTERS_24A — OPTION EXPORT ADAPTERS (EVAL-24A)

- generated_at: 2026-11-14T00:45:00Z
- overall_verdict: **NO-GO**
- reason: adapter parsed export but chain is below EVAL-24 adequacy floors (contracts 3/8, quotes 3/8, expiries 2/2)
- adapter_verdict: PASS
- trading_mode: paper
- data_provenance: exchange_export (authenticity_verified=false)
- source_path: `data/examples/options_exports/deribit_btc_option_sample.json`
- venue/underlying: `deribit` / `BTC`
- format: json
- n_quotes: 3
- n_contracts: 3
- n_strikes: 3
- n_expiries: 2
- span_seconds: 0.0
- start/end: 2026-01-01T00:00:00Z → 2026-01-01T00:00:00Z
- canonical_fingerprint: `52c27da9c3f13ab119e08d976d4aa86e6fc98bd2bb38bfacdc205039bf627121`
- normalized_chain: data/examples/normalized/options_deribit_BTC_20261114T004349Z.json
- floors: {'min_contracts': 8, 'min_quotes': 8, 'min_expiries': 2}
- adequacy: 3/8 contracts, 3/8 quotes, 2/2 expiries, adequate=false

## Supported export formats

| venue | csv headers | json shape | timestamps | option types |
|---|---|---|---|---|
| okx | `instId, strike, expiry, optionType, bid, ask, mark, markIv, delta, gamma, theta, vega, openInterest, volume, ts` | `list | {data: [...]} | {quotes: [...]}` | ISO-8601, epoch-ms | C, P, call, put |
| binance | `symbol, strike, expiry, optionType, bid, ask, mark, markIv, delta, gamma, theta, vega, openInterest, volume, timestamp` | `list | {quotes: [...]} | {data: [...]}` | ISO-8601, epoch-ms | CALL, PUT |
| deribit | `instrument_name, strike, expiration_timestamp, option_type, bid_price, ask_price, mark_price, mark_iv, delta, gamma, theta, vega, open_interest, volume, timestamp` | `list | {result: [...]} | {quotes: [...]}` | epoch-ms, ISO-8601 | call, put |

## Readiness

Offline deterministic adapter; no network, no `.env`, no live trading. A parsed export is not proof of real provenance; EVAL-24 must validate the normalized chain before any options-leg decision.
