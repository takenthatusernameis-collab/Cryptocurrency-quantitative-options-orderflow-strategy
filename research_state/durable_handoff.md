# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T01:41:42Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main. Working tree clean (pycache untracked). Do NOT end the GitHub Actions workflow.

## INITIAL TASK MESSAGE (For Next Agentic Session — MANDATORY, NO DEFERRAL)

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, ZERO PLACEHOLDERS**

You are continuing in the SAME active run. Scaffolding exists (28 tests pass). Deribit public connector + CLI are now implemented; remaining bottleneck is **CROSS-VENUE INGESTION + ALPHA/BACTEST DEPTH**. OKX and Binance are empty stubs returning empty lists — downstream alpha/backtest need real normalized multi-venue data.

**START HERE (GATE):**
- Implement `src/ingestion/okx.py` and `src/ingestion/binance.py` against their public REST endpoints, mirroring Deribit: fetch options chains, trades, liquidations; normalize to schemas (OptionsChain/OrderflowSnapshot). Handle pagination, rate limits, timeouts, errors.
- Do NOT return empty lists and call it done. If network restricted, implement full typed HTTP client + parsing + normalization + unit tests with fixtures.
- Harden `src/data/normalization.py` for cross-venue timestamps/symbols/moneyness.

**MANDATORY FOCUS CAMPAIGN (EXECUTE IN STRICT ORDER):**

### Phase 1: Cross-Venue Ingestion (CRITICAL PATH) — BLOCKING
1. [ ] OKX: `src/ingestion/okx.py` full public REST implementation.
2. [ ] Binance: `src/ingestion/binance.py` full public REST implementation.
3. [ ] Normalization hardening: `src/data/normalization.py`.
4. [ ] Deribit hardening: pagination/rate-limit/retry + smoke test.

### Phase 2: Pipeline + Config (UNBLOCK END-TO-END)
5. [ ] CLI `src/main.py`: wire ingestion -> features -> signals -> backtest end-to-end from config.
6. [ ] Config-driven venues/symbols/timeframes/risk params (config/settings.yaml).
7. [ ] Checkpoint/persistence for same-run resume.

### Phase 3: Alpha Features (QUANTITATIVELY CORRECT)
8. [ ] GEX hardening: dealer gamma by strike/expiry, gamma flip, OI handling.
9. [ ] Orderflow/Vol: skew/term structure/PCR/max pain.
10. [ ] Signals composite: regime detection + calibrated weights.

### Phase 4: Backtest + Risk (PRODUCTION-REALISTIC)
11. [ ] Engine: shorts, sizing, SL/TP, position limits, realistic fees/slippage.
12. [ ] Metrics: Sharpe/Sortino/Calmar/winrate/profit factor/maxDD, non-finite safe.
13. [ ] Validation: walk-forward + integration test with realistic synthetic data.

### Phase 5: Tests + Hygiene
14. [ ] Real tests, no assert True; numeric assertions. All pass (`python -m pytest -q`).
15. [ ] Meaningful commits per logical unit; clean tree (no pycache/index noise).

**RULES:** Heavy engineering only. No scaffolding-only "done". Mathematical correctness matters. Vectorize where sensible. Never avoid Phase 1. Future agents must perform substantial implementation work; no deferral.

## BOTTLENECKS REMOVED
- Bytecode removed from index; `.gitignore` added.
- CI tests restored (28 passing).
- Deribit public connector implemented (src/ingestion/deribit.py).
- CLI entrypoint implemented (src/main.py).
- HEAD pushed to origin/main.

## BLOCKERS / NOTES
- OKX/Binance connectors are EMPTY STUBS — MUST REPLACE FIRST.
- Normalization cross-venue incomplete.
- Backtest engine lacks shorts/sizing/SLTP/metrics.

**NEXT ACTION:** Start Phase 1 OKX + Binance live connectors immediately. Do not explore tangentially. Make progress on the strategy.
