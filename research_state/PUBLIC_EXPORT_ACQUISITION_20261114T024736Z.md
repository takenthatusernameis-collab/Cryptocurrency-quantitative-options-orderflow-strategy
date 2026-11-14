# PUBLIC_EXPORT_ACQUISITION_26 — PUBLIC REAL-DATA ACQUISITION (EVAL-26)

- generated_at: 2026-11-14T02:47:36Z
- trading_mode: paper (live_trading_enabled=false)
- data_provenance: real_public_exchange_export (authenticity_verified=false)
- source: {'venue': 'okx', 'endpoints': ['/api/v5/market/history-trades', '/api/v5/public/instruments', '/api/v5/market/tickers'], 'authenticated': False, 'public_read_only': True, 'network': 'public_market_data_only'}

## Orderflow tape

- instrument: `BTC-USD-SWAP`
- path: `data/raw/orderflow_okx_BTC-USD-SWAP.json`
- n_trades: 57400, n_bars: 1552, span_seconds: 23265.964, pages: 574
- content_sha256: `865d2e06157331bba01b067eafaefa839f9ce872a73830511289bf922837df83`

## Option chain

- underlying: `BTC`
- path: `data/raw/options_okx_BTC_20261114T024736Z.json`
- n_quotes: 739, n_contracts: 739, n_expiries: 12
- expiries: ['2026-11-15T00:00:00Z', '2026-11-16T00:00:00Z', '2026-11-17T00:00:00Z', '2026-11-20T00:00:00Z', '2026-11-27T00:00:00Z', '2026-12-04T00:00:00Z', '2026-12-25T00:00:00Z', '2027-01-29T00:00:00Z', '2027-02-26T00:00:00Z', '2027-03-26T00:00:00Z', '2027-06-25T00:00:00Z', '2027-09-24T00:00:00Z']
- content_sha256: `268bf34ef8a1099ea79bf353ddfa337388bb071ac4f0968b107fbd1bcb3cc8fa`

## Adequacy preview (sealed floors)

- {'orderflow_min_returns': 1000, 'orderflow_min_windows': 20, 'orderflow_bar_duration_seconds': 15.0, 'orderflow_adequate': True, 'options_min_contracts': 8, 'options_min_quotes': 8, 'options_min_expiries': 2, 'options_adequate': True}

This is an acquisition/readiness artifact only. The sealed EVAL-22, EVAL-24 and EVAL-25 gates remain the only source of a GO/NO-GO verdict; synthetic data is never relabeled and no ``{"valid": true}`` is emitted.
