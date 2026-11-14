# PUBLIC_EXPORT_ACQUISITION_26 — PUBLIC REAL-DATA ACQUISITION (EVAL-26)

- generated_at: 2026-11-14T17:17:25.753962Z
- trading_mode: paper (live_trading_enabled=false)
- data_provenance: real_public_exchange_export (authenticity_verified=false)
- source: {'venue': 'okx', 'endpoints': ['/api/v5/market/history-trades', '/api/v5/public/instruments', '/api/v5/market/tickers'], 'authenticated': False, 'public_read_only': True, 'network': 'public_market_data_only'}

## Orderflow tape

- instrument: `BTC-USD-SWAP`
- path: `data/raw/orderflow_okx_BTC-USD-SWAP-40.json`
- n_trades: 84800, n_bars: 1602, span_seconds: 24021.532, pages: 848
- content_sha256: `a105db1c323c9c64db75882c367f84a81f2ac87374ed62ad490d334af484bc4b`

## Option chain

- underlying: `BTC`
- path: `data/raw/options_okx_BTC_20261114T171725Z.json`
- n_quotes: 827, n_contracts: 827, n_expiries: 14
- expiries: ['2026-11-15T00:00:00Z', '2026-11-16T00:00:00Z', '2026-11-17T00:00:00Z', '2026-11-18T00:00:00Z', '2026-11-20T00:00:00Z', '2026-11-27T00:00:00Z', '2026-12-04T00:00:00Z', '2026-12-11T00:00:00Z', '2026-12-25T00:00:00Z', '2027-01-29T00:00:00Z', '2027-02-26T00:00:00Z', '2027-03-26T00:00:00Z', '2027-06-25T00:00:00Z', '2027-09-24T00:00:00Z']
- content_sha256: `159bc3b8f27a605f2ac3d2430a51485a16c0781aee04c7f3ec79e295934f2eca`

## Adequacy preview (sealed floors)

- {'orderflow_min_returns': 1000, 'orderflow_min_windows': 20, 'orderflow_bar_duration_seconds': 15.0, 'orderflow_adequate': True, 'options_min_contracts': 8, 'options_min_quotes': 8, 'options_min_expiries': 2, 'options_adequate': True}

This is an acquisition/readiness artifact only. The sealed EVAL-22, EVAL-24 and EVAL-25 gates remain the only source of a GO/NO-GO verdict; synthetic data is never relabeled and no ``{"valid": true}`` is emitted.
