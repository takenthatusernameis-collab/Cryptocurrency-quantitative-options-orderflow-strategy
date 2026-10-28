# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T00:44:08Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main (b605eeb). Working tree clean (__pycache__ removed from index). Do NOT end the GitHub Actions workflow.

## INITIAL TASK MESSAGE (For Next Agentic Session — MANDATORY, NO DEFERRAL)

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, ZERO PLACEHOLDERS**

You are continuing in the SAME active run. The scaffolding exists (28 tests pass). The bottleneck is **LIVE DATA INGESTION**. Deribit public API must be implemented first — everything downstream depends on real normalized options/orderflow.

**START HERE (GATE):**
- Replace `src/ingestion/deribit.py` stubs with a real Deribit public REST connector. Fetch actual options instrument book/chain (or use public endpoints: `/public/get_instruments`, `/public/get_order_book`/ticker/last trades as appropriate). Must return populated `OptionsChain`/quotes with strikes/expiries/option types, IV/greeks if available or computable. Also implement `fetch_trades`/`fetch_liquidations` against public Deribit endpoints. Normalize to schemas.
- Do NOT mock to empty lists and call it done. If public endpoints require pagination/rate limits, handle them. Add error handling/timeouts.
- Verify with a quick smoke test against public API (or offline fixture only if network blocked, but must still produce realistic structures). If network is restricted in this env, implement the full HTTP client + parsing + normalization logic correctly (typed, tested) so it's ready for live keys/endpoints.

**MANDATORY FOCUS CAMPAIGN (EXECUTE IN STRICT ORDER):**

### Phase 1: Live Ingestion (CRITICAL PATH) — BLOCKING
1. [ ] **Deribit**: `src/ingestion/deribit.py` — full public REST implementation (requests/websocket-client available). Populate `OptionsChain.quotes` with real instrument data structure. Handle BTC/ETH first.
2. [ ] **Normalization hardening**: `src/data/normalization.py` — ensure cross-venue timestamps/symbols/moneyness consistent.
3. [ ] **OKX**: `src/ingestion/okx.py` implementing base classes.
4. [ ] **Binance**: `src/ingestion/binance.py` implementing base classes.

### Phase 2: Pipeline + CLI (UNBLOCK END-TO-END)
5. [ ] **CLI**: Add `src/main.py` (or `scripts/run_strategy.py`) wiring `ingestion -> features -> signals -> backtest` from `config/settings.yaml`.
6. [ ] **Config-driven**: All venues/symbols/timeframes/risk params read from config.
7. [ ] **Checkpoint/persistence**: Enable same-run resume if interrupted.

### Phase 3: Alpha Features (QUANTITATIVELY CORRECT)
8. [ ] **GEX**: Harden `src/features/gamma_exposure.py` — dealer gamma by strike/expiry, gamma flip, proper OI/strike handling.
9. [ ] **Orderflow/Vol**: Harden `src/features/orderflow.py`, `src/features/volatility.py` (skew/term structure/PCR/max pain).
10. [ ] **Signals**: Harden `src/signals/composite.py` with regime detection + calibrated weights.

### Phase 4: Backtest + Risk (PRODUCTION-REALISTIC)
11. [ ] **Engine**: Extend `src/backtest/engine.py` for shorts, sizing, SL/TP, position limits, realistic fees/slippage.
12. [ ] **Metrics**: Sharpe/Sortino/Calmar/winrate/profit factor/maxDD, non-finite safe.
13. [ ] **Validation**: Walk-forward + integration test with realistic synthetic data.

### Phase 5: Tests + Hygiene
14. [ ] **Real tests**: No `assert True`. Add numeric assertions. All tests must pass (`python -m pytest -q`).
15. [ ] **Commits**: Meaningful commits per logical unit. Keep working tree clean (no pyc/index noise).

**RULES:** Heavy engineering only. No scaffolding-only "done". Mathematical correctness matters. Vectorize where sensible. If blocked by network in test env, implement complete, correct client logic + unit tests with fixtures — do not leave stubs. Never avoid Phase 1.

## BOTTLENECKS REMOVED (CURRENT STATE)
- Bytecode removed from index; `.gitignore` added.
- CI test files restored (28 tests passing).
- HEAD pushed to origin/main (b605eeb). Same-run persistence will be retried by controller.

## BLOCKERS / NOTES
- `src/ingestion/deribit.py` is EMPTY STUBS — MUST REPLACE FIRST.
- No CLI entrypoint exists yet.
- OKX/Binance connectors missing.
- All dependencies in requirements.txt available.

**NEXT ACTION:** Start with Phase 1 Deribit live connector implementation immediately. Do not explore tangentially. Make progress on the strategy.
