# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T01:42:31Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main. Working tree clean. Do NOT end the GitHub Actions workflow.

## Initial Task Message

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, ZERO PLACEHOLDERS**

You are continuing in the SAME active run. Scaffolding exists (28 tests pass). Deribit connector + CLI implemented. **OKX and Binance connectors implemented with full typed HTTP clients, parsing, normalization.** Bottlenecks being removed; remaining heavy work is end-to-end wiring, alpha depth, backtest realism.

**START HERE (GATE):**
- Wire OKX/Binance into CLI `src/main.py` (already loads config venues; add ingestion calls for okx/binance mirroring deribit).
- Harden `src/data/normalization.py` usage across pipeline and ensure cross-venue symbol/timestamp consistency.
- Extend backtest engine with shorts, sizing, SL/TP, realistic metrics (Sharpe/Sortino/Calmar/profit factor), handle non-finite safely.

## Immediate Objectives
- [CRITICAL] Update `src/main.py` to instantiate OKX/Binance ingestion (options + orderflow) for configured venues/symbols.
- [HIGH] Normalize outputs in pipeline (use normalization helpers). Add basic integration path.
- [HIGH] Backtest: add short selling, position sizing/risk limits, stop-loss/take-profit, improved metrics.
- [HIGH] Signals/features: harden GEX/orderflow/skew/PCR/max pain with correct math.
- [MED] Tests: add/extend numeric tests for new connectors where feasible; keep all passing.

## Next Focus Campaign
Phase 1: Cross-Venue Ingestion — **DONE (OKX/Binance implemented)**. Verify and wire.
Phase 2: Pipeline + Config — Wire CLI end-to-end, config-driven flows, checkpointing.
Phase 3: Alpha Features — GEX/orderflow/volatility/signals quantitatively correct.
Phase 4: Backtest + Risk — shorts/sizing/SLTP/metrics, validation.
Phase 5: Tests + Hygiene — real numeric tests, clean commits.

## MANDATE
Heavy engineering only. No scaffolding-only "done". Mathematical correctness matters. Vectorize where sensible. Never deflect from implementation. Future agents must do substantial work.

## BOTTLENECKS REMOVED
- Bytecode removed from index; .gitignore added.
- CI tests restored (28 passing).
- Deribit connector implemented.
- CLI entrypoint implemented.
- **OKX public REST connector implemented** (`src/ingestion/okx.py`).
- **Binance public REST connector implemented** (`src/ingestion/binance.py`).
- **Normalization hardened** (`src/data/normalization.py`).

## BLOCKERS / NOTES
- CLI not yet wiring OKX/Binance (venues configured but ingestion only does deribit). **FIX IMMEDIATELY.**
- Backtest lacks shorts/sizing/SLTP/metrics depth.
- Normalization usage not fully integrated in pipeline.

**NEXT ACTION:** Edit `src/main.py` to add OKX and Binance ingestion paths for options chains and orderflow, normalize results, then proceed to backtest/risk hardening.
