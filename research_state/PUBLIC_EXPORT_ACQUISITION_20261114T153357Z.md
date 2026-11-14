# PUBLIC_EXPORT_ACQUISITION_26 — PUBLIC REAL-DATA ACQUISITION (EVAL-26)

- generated_at: 2026-11-14T15:33:57.989901Z
- trading_mode: paper (live_trading_enabled=false)
- data_provenance: real_public_exchange_export (authenticity_verified=false)
- source: {'venue': 'okx', 'endpoints': ['/api/v5/market/history-trades', '/api/v5/public/instruments', '/api/v5/market/tickers'], 'authenticated': False, 'public_read_only': True, 'network': 'public_market_data_only'}

## Orderflow tape

- instrument: `BTC-USD-SWAP`
- path: `data/raw/orderflow_okx_BTC-USD-SWAP.json`
- n_trades: 77700, n_bars: 1555, span_seconds: 23314.102, pages: 777
- content_sha256: `fa9e43b8edeeeace7b7c551b23158aa68778dbf3909898f7e629da843baa43b6`

## Option chain

- underlying: `BTC`
- path: `data/raw/options_okx_BTC_20261114T153357Z.json`
- n_quotes: 815, n_contracts: 815, n_expiries: 14
- expiries: ['2026-11-15T00:00:00Z', '2026-11-16T00:00:00Z', '2026-11-17T00:00:00Z', '2026-11-18T00:00:00Z', '2026-11-20T00:00:00Z', '2026-11-27T00:00:00Z', '2026-12-04T00:00:00Z', '2026-12-11T00:00:00Z', '2026-12-25T00:00:00Z', '2027-01-29T00:00:00Z', '2027-02-26T00:00:00Z', '2027-03-26T00:00:00Z', '2027-06-25T00:00:00Z', '2027-09-24T00:00:00Z']
- content_sha256: `96b2e196811a798237d2506f115c26b36dad4569262ebf7f90f662eafe77f1a1`

## Adequacy preview (sealed floors)

- {'orderflow_min_returns': 1000, 'orderflow_min_windows': 20, 'orderflow_bar_duration_seconds': 15.0, 'orderflow_adequate': True, 'options_min_contracts': 8, 'options_min_quotes': 8, 'options_min_expiries': 2, 'options_adequate': True}

This is an acquisition/readiness artifact only. The sealed EVAL-22, EVAL-24 and EVAL-25 gates remain the only source of a GO/NO-GO verdict; synthetic data is never relabeled and no ``{"valid": true}`` is emitted.
