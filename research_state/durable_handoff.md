# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T01:42:31Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main. Working tree clean (pycache untracked). Do NOT end the GitHub Actions workflow.

## INITIAL TASK MESSAGE (For Next Agentic Session — MANDATORY, NO DEFERRAL)

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, ZERO PLACEHOLDERS**

You are continuing in the SAME active run. Scaffolding exists (28 tests pass). Deribit public connector + CLI are implemented. **OKX and Binance public REST connectors are now fully implemented** with typed HTTP clients, parsing/normalization, retries/timeouts. Cross-venue normalization hardened.

**START HERE (GATE):**
1. Wire OKX/Binance into `src/main.py` end-to-end (ingest options+orderflow for configured venues/symbols). Do not leave TODOs.
2. Harden backtest engine: add short selling, position sizing, stop-loss/take-profit, realistic fees/slippage, comprehensive metrics (Sharpe/Sortino/Calmar/profit factor/maxDD), safe non-finite handling.
3. Harden alpha features (GEX, orderflow, volatility/skew/PCR/max pain) and signals composite for quantitative correctness.

**MANDATORY FOCUS CAMPAIGN (EXECUTE IN STRICT ORDER):**

### Phase 1: Cross-Venue Ingestion (CRITICAL PATH) — NEARLY DONE
1. [x] OKX: `src/ingestion/okx.py` full public REST implementation.
2. [x] Binance: `src/ingestion/binance.py` full public REST implementation.
3. [x] Normalization hardening: `src/data/normalization.py`.
4. [ ] Wire into pipeline (CLI) and verify.

### Phase 2: Pipeline + Config (UNBLOCK END-TO-END)
5. [ ] CLI `src/main.py`: wire ingestion -> features -> signals -> backtest end-to-end from config (OKX+Binance).
6. [ ] Config-driven venues/symbols/timeframes/risk params.
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
15. [ ] Meaningful commits per logical unit; clean tree.

**RULES:** Heavy engineering only. No scaffolding-only "done". Mathematical correctness matters. Vectorize where sensible. Never avoid core work. Future agents must perform substantial implementation work.

## BOTTLENECKS REMOVED
- Bytecode removed from index; `.gitignore` added.
- CI tests restored (28 passing).
- Deribit public connector implemented (src/ingestion/deribit.py).
- CLI entrypoint implemented (src/main.py).
- OKX + Binance public REST connectors implemented.
- Normalization hardened.
- HEAD pushed to origin/main.

## BLOCKERS / NOTES
- **CLI wiring missing for OKX/Binance** — must add immediately.
- Backtest engine lacks shorts/sizing/SLTP/metrics.
- Need deeper alpha features and end-to-end integration.

**NEXT ACTION:** Edit `src/main.py` to wire OKX and Binance ingestion for all configured venues/symbols. Make heavy, concrete changes.
