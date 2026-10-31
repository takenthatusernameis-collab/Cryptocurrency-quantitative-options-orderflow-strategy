# DATA INVENTORY - 2026-10-31T08:15:30Z
Repo: Cryptocurrency-quantitative-options-orderflow-strategy

## Raw data (data/raw/)
- data/raw/orderflow_btcusdt_synthetic.json (218KB) - dict with keys: trades, liquidations, funding_rates, symbol, venue. Loaded: 1000 trades, 20 liquidations, 8 funding_rates (venue=synthetic, symbol=BTCUSDT)
- data/raw/options_btc_synthetic.json (18KB) - options chain (30 quotes). Loaded via DataLoader as OptionsChain.

## Processed
- data/processed/ exists (empty directory). No processed feature sets materialized yet.

## Source modules (present)
- src/data/loader.py (DataLoader with load_trades/load_orderflow/load_options_chain), normalization, schemas, validators - all exist and functional
- src/features/orderflow.py, liquidity.py, gamma_exposure.py, volatility.py, iv_surface.py, options_pricing.py
- src/backtest/engine.py, options_hedging.py
- src/signals/composite.py (no orderflow_signal.py yet as specified in handoff)
- src/pipelines/* not present; scripts for running exist

## Entry points
- scripts/run_backtest_synthetic.py works (runs with PYTHONPATH)
- scripts/generate_synthetic_orderflow.py exists
- scripts/run_strategy.py exists

## Observations
- Synthetic data exists and loader/validators work.
- Current synthetic backtest logic only trades if cum_delta>0 and of_imb>0.01 or cum_delta<0 and of_imb<-0.01; with synthetic data values may not trigger trades resulting in 0 trades. Need to inspect feature values.
