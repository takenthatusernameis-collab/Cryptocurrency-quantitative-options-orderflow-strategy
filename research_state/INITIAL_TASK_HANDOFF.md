# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T01:41:42Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main. Working tree clean. Do NOT end the GitHub Actions workflow.

## Initial Task Message

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, ZERO PLACEHOLDERS**

You are continuing in the SAME active run. Scaffolding exists (28 tests pass). Deribit connector and CLI are implemented; bottleneck is cross-venue ingestion (OKX/Binance stubs) plus alpha/backtest depth.

**START HERE (GATE):**
- Replace `src/ingestion/okx.py` and `src/ingestion/binance.py` stubs with real public REST connectors. Normalize to schemas. Handle pagination/rate limits/timeouts.
- If network restricted, implement full typed HTTP client + parsing + normalization + fixture tests. No empty-list "done".

## Immediate Objectives
- Implement OKX + Binance live connectors (Phase 1 gate).
- Harden normalization cross-venue.
- Wire CLI end-to-end from config.
- Harden GEX/orderflow/volatility/signals.
- Extend backtest engine with realistic costs and metrics.
- Keep tests passing with numeric assertions.

## Next Focus Campaign
Phase 1: OKX, Binance, normalization, Deribit hardening.
Phase 2: CLI end-to-end, config-driven, checkpoint.
Phase 3: GEX, orderflow/vol, signals.
Phase 4: backtest engine, metrics, validation.
Phase 5: tests + hygiene.

## MANDATE
Heavy engineering only. No scaffolding-only "done". Mathematical correctness matters. Never avoid Phase 1. Future agents must perform substantial implementation work; no deferral.

## BOTTLENECKS REMOVED
- Bytecode removed from index; .gitignore added.
- CI tests restored (28 passing).
- Deribit connector implemented.
- CLI entrypoint implemented.

## BLOCKERS / NOTES
- OKX/Binance empty stubs — MUST REPLACE FIRST.
- Normalization incomplete.
- Backtest lacks shorts/sizing/SLTP/metrics.

**NEXT ACTION:** Start Phase 1 OKX + Binance live connectors immediately.
