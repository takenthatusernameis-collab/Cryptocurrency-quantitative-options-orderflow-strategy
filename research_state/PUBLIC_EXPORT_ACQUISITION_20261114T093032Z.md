# PUBLIC_EXPORT_ACQUISITION_26 — PUBLIC REAL-DATA ACQUISITION (EVAL-26)

- generated_at: 2026-11-14T09:30:32.425254Z
- trading_mode: paper (live_trading_enabled=false)
- data_provenance: real_public_exchange_export (authenticity_verified=false)
- source: {'venue': 'okx', 'endpoints': ['/api/v5/market/history-trades', '/api/v5/public/instruments', '/api/v5/market/tickers'], 'authenticated': False, 'public_read_only': True, 'network': 'public_market_data_only'}

## Orderflow tape

- instrument: `None`
- path: `None`
- n_trades: None, n_bars: None, span_seconds: None, pages: None
- content_sha256: `None`

## Option chain

- underlying: `BTC`
- path: `data/raw/options_okx_BTC_20261114T093032Z.json`
- n_quotes: 825, n_contracts: 825, n_expiries: 14
- expiries: ['2026-11-15T00:00:00Z', '2026-11-16T00:00:00Z', '2026-11-17T00:00:00Z', '2026-11-18T00:00:00Z', '2026-11-20T00:00:00Z', '2026-11-27T00:00:00Z', '2026-12-04T00:00:00Z', '2026-12-11T00:00:00Z', '2026-12-25T00:00:00Z', '2027-01-29T00:00:00Z', '2027-02-26T00:00:00Z', '2027-03-26T00:00:00Z', '2027-06-25T00:00:00Z', '2027-09-24T00:00:00Z']
- content_sha256: `29338351a841a14ca33b5f0eb05d93f51075b58b64aa120d9ea7b890d977ccd1`

## Adequacy preview (sealed floors)

- {'orderflow_min_returns': 1000, 'orderflow_min_windows': 20, 'orderflow_bar_duration_seconds': 15.0, 'orderflow_adequate': False, 'options_min_contracts': 8, 'options_min_quotes': 8, 'options_min_expiries': 2, 'options_adequate': True}

This is an acquisition/readiness artifact only. The sealed EVAL-22, EVAL-24 and EVAL-25 gates remain the only source of a GO/NO-GO verdict; synthetic data is never relabeled and no ``{"valid": true}`` is emitted.
