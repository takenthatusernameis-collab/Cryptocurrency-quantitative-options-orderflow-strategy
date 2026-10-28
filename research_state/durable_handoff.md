# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T01:48:29Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main. Working tree clean. 28 tests passing. Do NOT end the GitHub Actions workflow.

## INITIAL TASK MESSAGE (For Next Agentic Session — MANDATORY, NO DEFERRAL)

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, ZERO PLACEHOLDERS**

You are continuing in the SAME active run. Cross-venue ingestion scaffolding and connectors exist (Deribit/OKX/Binance implemented). CLI already wires all three venues. The heavy quantitative work is incomplete — make it correct, realistic, and end-to-end functional.

**IMMEDIATE GATE (MUST EXECUTE IN ORDER):**
1. **Harden Backtest Engine** (`src/backtest/engine.py`): Add proper short selling (initiate shorts, cover), position sizing (risk-based via config), stop-loss/take-profit enforcement, realistic fees/slippage, position limits. Compute full metrics: total_return, sharpe/ sortino/calmar, max_drawdown, win_rate, profit_factor with non-finite safety. Make it production-realistic.
2. **Wire Pipeline Fully** (`src/main.py`): Currently wires ingestion/signals/backtest class names only. Actually call feature extraction (GEX/orderflow/vol), run composite signals on real data, execute backtest with signals/positions, persist results. Use normalization throughout. No stubs.
3. **Harden Alpha Features** (`src/features/*.py`): Make GEX calculations quantitatively correct (gamma exposure by strike/expiry, gamma flip), orderflow (CVD, aggressive flow), volatility/skew/PCR/max pain with proper math. Add tests/validation as you harden.

**MANDATORY FOCUS CAMPAIGN (STRICT EXECUTION):**

### Phase 1: Backtest Engine Hardening (CRITICAL) — UNBLOCKS REAL EVALUATION
- [ ] Shorts: allow short initiation (`sell` to open short when no long), short PnL = (entry - exit)*qty, track side properly. Update Position/Trade semantics.
- [ ] Sizing: integrate risk limits from config (`risk.*`), position sizing methods (e.g. % capital, ATR-based). Enforce `max_position_pct`.
- [ ] Risk controls: stop-loss/take-profit checks per position (on price updates), max drawdown monitoring.
- [ ] Metrics: fix win_rate/profit_factor (need winning/losing trade classification), add calmar correctly, guard all divisions/non-finite (inf/nan).
- [ ] Slippage/fees: ensure applied correctly on entry/exit; track realized PnL.

### Phase 2: End-to-End Pipeline Wiring (CRITICAL)
- [ ] `src/main.py`: build full flow - ingest all configured venues/symbols, normalize chains/orderflow, extract features per venue/symbol, generate signals (CompositeSignalGenerator) with context, run backtest with signal-driven trades or realistic simulation, output comprehensive results.
- [ ] Use `normalize_options_chain`/`normalize_orderflow` from `src/data/normalization.py` on ingested objects.
- [ ] Add proper error handling, structured results with metrics.
- [ ] Support `--symbols` override, JSON output with full details.

### Phase 3: Alpha Features Quantitative Hardening
- [ ] `src/features/gamma_exposure.py`: correct GEX formula (gamma * OI * contract multiplier * spot^2 / 100 for notional gamma in $ terms), gamma flip detection, net GEX by strike/expiry.
- [ ] `src/features/orderflow.py`: CVD, trade imbalance, large/sweep detection, funding/oi context.
- [ ] `src/features/volatility.py`: skew, term structure, IV percentile/rank, PCR (put-call ratio), max pain calculation.
- [ ] `src/signals/composite.py`: regime-aware weighted signals, calibration, conflict resolution.

### Phase 4: Validation & Real Tests
- [ ] Add numeric tests for shorts/sizing/SLTP/metrics in backtest.
- [ ] Integration test exercising full pipeline with mocked data or real public endpoints where safe.
- [ ] All tests pass: `python -m pytest -q`. No `assert True`, no placeholders.

**RULES:** Heavy engineering only. No scaffolding-only "done". Mathematical correctness is mandatory. Vectorize where sensible. Every change must be concrete and functional. Future agents must do substantial implementation work.

## BOTTLENECKS IDENTIFIED & REMOVAL PLAN
- **Bottleneck 1:** Backtest engine incomplete (no shorts/sizing/SLTP/metrics depth) → Phase 1 above.
- **Bottleneck 2:** Pipeline wiring superficial (only prints class names) → Phase 2 above, must produce actionable results.
- **Bottleneck 3:** Alpha features may be simplistic → Phase 3 harden to quantitative correctness.
- **Bottleneck 4:** Tests don't cover new critical paths → Phase 4 add real tests.

## CURRENT STATE
- 28 tests passing
- All three venues (deribit/okx/binance) connectors implemented
- CLI exists and wires all venues for ingestion
- Normalization utilities present
- Config in place

**NEXT ACTION:** Start with Phase 1 - harden `src/backtest/engine.py` for shorts, sizing, SL/TP, and full metrics. Make heavy concrete changes.
