# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T00:45:06Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main. Working tree clean (pycache removed from index). Do NOT end the GitHub Actions workflow.

## Initial Task Message

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, ZERO PLACEHOLDERS**

You are continuing in the SAME active run. The scaffolding exists (28 tests pass). The bottleneck is LIVE DATA INGESTION. Deribit public API must be implemented first — everything downstream depends on real normalized options/orderflow.

**START HERE (GATE):**
- Replace `src/ingestion/deribit.py` stubs with a real Deribit public REST connector. Fetch actual options instrument book/chain. Must return populated `OptionsChain`/quotes with strikes/expiries/option types, IV/greeks if available or computable. Also implement `fetch_trades`/`fetch_liquidations`. Normalize to schemas.
- Do NOT mock to empty lists. Handle pagination/rate limits. Add error handling/timeouts.
- If network restricted, implement full HTTP client + parsing + normalization logic correctly (typed, tested).

## Immediate Objectives

- Implement Deribit live connector (Phase 1 gate).
- Remove ingestion stubs; normalize cross-venue data.
- Add CLI entrypoint wiring ingestion -> features -> signals -> backtest.
- Harden GEX/orderflow/volatility/signals.
- Extend backtest engine with realistic costs and metrics.
- Keep tests passing with numeric assertions.

## Next Focus Campaign

### Phase 1: Live Ingestion (CRITICAL PATH) — BLOCKING
1. [ ] Deribit `src/ingestion/deribit.py` full public REST.
2. [ ] Normalization `src/data/normalization.py`.
3. [ ] OKX `src/ingestion/okx.py`.
4. [ ] Binance `src/ingestion/binance.py`.

### Phase 2: Pipeline + CLI
5. [ ] CLI `src/main.py` or `scripts/run_strategy.py`.
6. [ ] Config-driven params.
7. [ ] Checkpoint/persistence.

### Phase 3: Alpha Features
8. [ ] GEX hardening.
9. [ ] Orderflow/Vol hardening.
10. [ ] Signals composite.

### Phase 4: Backtest + Risk
11. [ ] Engine extensions.
12. [ ] Metrics.
13. [ ] Validation.

### Phase 5: Tests + Hygiene
14. [ ] Real tests, no assert True.
15. [ ] Meaningful commits, clean tree.

## MANDATE

Heavy engineering only. No scaffolding-only "done". Mathematical correctness matters. Never avoid Phase 1. Future agents must perform substantial implementation work; no deferral.

## BOTTLENECKS REMOVED
- Bytecode removed from index; `.gitignore` added.
- CI tests restored (28 passing).
- pycache untracked.

## BLOCKERS / NOTES
- `src/ingestion/deribit.py` empty stubs — MUST REPLACE FIRST.
- No CLI entrypoint.
- OKX/Binance missing.

**NEXT ACTION:** Start Phase 1 Deribit live connector immediately.
