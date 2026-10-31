# DATA INVENTORY - 2026-10-31T07:14:05Z

Repo: Cryptocurrency-quantitative-options-orderflow-strategy
Goal: Phase 1 data foundation before features/backtest

## data/ (top level)
- `data/` contains only `.gitkeep` (empty). No trade/orderbook/options/liquidations/funding files present.

## Observations from codebase
- Schemas exist: `src/data/schemas.py` (Trade, OrderflowSnapshot, OptionQuote/Chain, FundingRate, Liquidation)
- Normalization: `src/data/normalization.py` has timestamp normalization and helpers
- Ingestion: `src/ingestion/*` (binance/deribit/okx/mock/base). Some may expect real data; no raw files present
- Features: orderflow/options/vol/gamma/iv/liquidity implemented
- Backtest: `src/backtest/engine.py`, `src/backtest/options_hedging.py` exist
- Scripts: `scripts/run_strategy.py`, `scripts/controller_progress.py` exist (inspect for usage)

## Conclusion
No usable raw market data files exist in `data/`. Must generate realistic synthetic fixtures to satisfy loader/validators/tests and enable a baseline backtest. Create fixtures under `data/raw/` and a script to generate them.
