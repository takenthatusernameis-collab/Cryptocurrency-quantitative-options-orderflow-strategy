# PUBLIC_EXPORT_ACQUISITION_26 — PUBLIC REAL-DATA ACQUISITION (EVAL-26)

- generated_at: 2026-11-14T18:46:04Z
- trading_mode: paper (live_trading_enabled=false)
- data_provenance: real_public_exchange_export (authenticity_verified=false)
- source: {'venue': 'okx', 'endpoints': ['/api/v5/market/history-trades', '/api/v5/public/instruments', '/api/v5/market/tickers'], 'authenticated': False, 'public_read_only': True, 'network': 'public_market_data_only'}

## Orderflow tape

- instrument: `BTC-USD-SWAP`
- path: `data/raw/orderflow_okx_41b.json`
- n_trades: 80000, n_bars: 1555, span_seconds: 23310.21, pages: 800
- content_sha256: `f59c21f1945768356907685bcb0b0dda104ac5e709b5ce84a711fe83cb316d6a`

## Option chain

- underlying: `None`
- path: `None`
- n_quotes: None, n_contracts: None, n_expiries: None
- expiries: None
- content_sha256: `None`

## Adequacy preview (sealed floors)

- {'orderflow_min_returns': 1000, 'orderflow_min_windows': 20, 'orderflow_bar_duration_seconds': 15.0, 'orderflow_adequate': True, 'options_min_contracts': 8, 'options_min_quotes': 8, 'options_min_expiries': 2, 'options_adequate': False}

This is an acquisition/readiness artifact only. The sealed EVAL-22, EVAL-24 and EVAL-25 gates remain the only source of a GO/NO-GO verdict; synthetic data is never relabeled and no ``{"valid": true}`` is emitted.
