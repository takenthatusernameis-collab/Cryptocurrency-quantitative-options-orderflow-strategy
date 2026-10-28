# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T03:59:18Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main. Working tree clean. 30 tests passing. DO NOT end the GitHub Actions workflow.

## INITIAL TASK MESSAGE (For Next Agentic Session — MANDATORY, HEAVY ENGINEERING, NO DEFERRAL)

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — ZERO PLACEHOLDERS, MATHEMATICAL CORRECTNESS MANDATORY**

Project name is `Cryptocurrency-quantitative-options-orderflow-strategy`. The scaffolding is complete: Deribit/OKX/Binance connectors, normalization, features, signals, CLI wiring, 30 tests green. Remaining work is deep quantitative hardening and production-grade robustness. Every future action must be concrete implementation that moves the strategy closer to a correct, testable engine.

### IMMEDIATE GATE (EXECUTE IN STRICT ORDER)

1. **Backtest Engine Correctness (CRITICAL)** — `src/backtest/engine.py`
   - Short equity: `get_equity` must return `cash + qty × (entry_price − current_price)` for shorts (credit proceeds on open, subtract liability correctly). Realized PnL must flow to cash on close/cover.
   - SL/TP: enforce on every price tick via `check_risk_controls` called from `update_equity_curve`. Close/cover on trigger and realize PnL.
   - Risk limits: enforce `max_position_pct` and `max_drawdown_limit` from risk config (config/settings.yaml). Close all positions on max drawdown breach.
   - Metrics: `profit_factor` must remain `inf` when total_wins>0 and total_losses==0 (never collapse to 0). `win_rate`/counts from closed trades only. `calmar_ratio = total_return / max_drawdown` when dd>0. All metrics non-finite-safe and JSON-serializable with `allow_nan=False`.
   - Add numeric tests for shorts, SL/TP triggers, position sizing vs limits, and metrics edge cases.

2. **Pipeline Robustness (CRITICAL)** — `src/main.py`, `src/data/normalization.py`
   - Eliminate ALL silent `except Exception: pass`. Every exception must be recorded in `results["errors"]` with context (venue/symbol/phase). Never abort entire run on single venue failure.
   - Apply `normalize_options_chain` and `normalize_orderflow` to EVERY ingested object before features/signals.
   - Enforce cross-venue symbol/timestamp consistency via `normalize_symbol`/`normalize_timestamp`.
   - Honor `--symbols` override. JSON output via `--json` must always be valid (`allow_nan=False`), sanitize non-finite to None if needed.
   - Pass full config (including `risk`) to BacktestEngine; load from settings.yaml.
   - Structured results: per-venue counts, trades, signals, backtest metrics, errors.

3. **Alpha Features Quantitative Hardening (HIGH)** — `src/features/*.py`, `src/signals/composite.py`
   - GEX: `GEX = gamma × OI × contract_size × spot² / 100` (puts negative, calls positive). Correct aggregation by strike; gamma flip detection robust.
   - Volatility: PCR by volume and OI (handle call_volume==0 without crash). IV skew = OTM put IV − OTM call IV. Max pain strike minimizing total pain.
   - Orderflow: CVD, orderflow imbalance, aggressive flow with guards (zero division, non-finite). Delta-adjusted flow where applicable.
   - Composite signals: regime-aware weighting, confidence in [0,1], conflict resolution, calibration.

## MANDATORY FOCUS CAMPAIGN (NO SKIPPING, NO PLACEHOLDERS)

### Phase 1: Backtest Engine (CRITICAL) — BLOCKS REAL EVALUATION
- [ ] Fix/verify short equity math end-to-end with numeric test.
- [ ] Enforce SL/TP on every price tick; realized PnL to cash.
- [ ] Enforce `max_position_pct`, `max_drawdown_limit` from config.
- [ ] `profit_factor` never becomes 0 when inf is correct; all divisions guarded.
- [ ] Add tests: short open/cover, SL trigger, TP trigger, sizing limits, metrics.

### Phase 2: Pipeline Hardening (CRITICAL)
- [ ] Remove silent swallows in `src/main.py`; errors surfaced.
- [ ] Normalize every ingested object; symbol/timestamp consistency.
- [ ] `--symbols` + `--json` robust; pass risk config to engine.
- [ ] Structured, valid JSON output under all failure modes.

### Phase 3: Feature Hardening (HIGH)
- [ ] GEX formula correct with edge guards.
- [ ] PCR/skew/max-pain/CVD mathematically correct.
- [ ] Composite signal calibration and robustness.

### Phase 4: Validation (HIGH)
- [ ] Add numeric tests (no `assert True`, no placeholders).
- [ ] `python -m pytest -q` all green.
- [ ] Integration sanity check of full pipeline.

### Phase 5: Hygiene (MED)
- [ ] No `__pycache__`/`*.pyc` tracked; `.gitignore` correct.
- [ ] Clean commits, working tree clean.

## BOTTLENECKS REMOVED
- Bytecode de-tracked (17 files) + `.gitignore` excludes `__pycache__/*.pyc`.
- All 30 tests passing.
- Connectors + CLI + normalization present.

## REMAINING BOTTLENECKS (MUST FIX)
- Ensure backtest enforces config-driven risk limits everywhere (pass risk config through pipeline).
- Eliminate any remaining silent exception paths.
- Harden feature calculations against division by zero/non-finite.
- Add missing numeric regression tests for critical paths.

## CURRENT STATE
- 30 tests passing (`python -m pytest -q`)
- Venues: deribit/okx/binance implemented
- CLI end-to-end wiring present
- Normalization present
- Config has risk section; engine/main must fully honor it
- Features/signals implemented

**NEXT ACTION:** Start with Phase 1 in `src/backtest/engine.py` — verify short equity, SL/TP on ticks, risk limits from config, profit_factor inf preservation, add numeric tests. Do not stop until heavy implementation is complete. Future agents must do substantial work.
