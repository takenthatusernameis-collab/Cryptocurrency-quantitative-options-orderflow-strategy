# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T02:40:19Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: SAME-ACTIVE-RUN continuation. HEAD == origin/main. Working tree clean (pycache de-tracked from index). Do NOT end the GitHub Actions workflow.

## INITIAL TASK MESSAGE (For Next Agentic Session — MANDATORY, NO DEFERRAL)

**PRIORITY 1: BUILD A WORKING CRYPTO OPTIONS ORDERFLOW STRATEGY — HEAVY ENGINEERING, ZERO PLACEHOLDERS**

You are continuing in the SAME active run. All three venue connectors (Deribit/OKX/Binance) implemented. CLI wires ingestion → normalization → features → composite signals → backtest end-to-end. 30 tests passing. The scaffolding is complete; the heavy quantitative work remains: make the backtest engine production-correct, harden alpha features to mathematical correctness, and make the pipeline robust with no silent failures.

**IMMEDIATE GATE (MUST EXECUTE IN ORDER):**
1. **Harden Backtest Engine** (`src/backtest/engine.py`): Fix short-position equity math (current `get_equity` subtracts `qty * price` without crediting the short margin/proceeds), enforce stop-loss/take-profit on every price update, guard profit_factor against `inf`, ensure realized PnL flows to cash on close/cover, add max_drawdown_limit enforcement from config.
2. **Wire Pipeline Fully** (`src/main.py`): Eliminate silent `except Exception: pass` blocks; surface errors in results; ensure `normalize_options_chain`/`normalize_orderflow` applied on every ingested object; make `--symbols` override and JSON output reliable.
3. **Harden Alpha Features** (`src/features/*.py`): Verify GEX formula (gamma * OI * multiplier * spot², scaled), put/call ratio, IV skew, max pain, CVD, orderflow imbalance — all quantitatively correct with edge-case guards (zero division, non-finite).

**MANDATORY FOCUS CAMPAIGN (STRICT EXECUTION — NO SKIPPING PHASES):**

### Phase 1: Backtest Engine Correctness (CRITICAL) — UNBLOCKS REAL EVALUATION
- [ ] Short equity: `get_equity` must value a short as cash + qty × (entry_price − current_price), not cash − qty × current_price.
- [ ] SL/TP enforcement: `check_risk_controls` must trigger on every `update_equity_curve` price tick; covered/closed positions must realize PnL into cash.
- [ ] Risk limits: enforce `max_position_pct` and `max_drawdown_limit` from `config.settings.yaml` risk section.
- [ ] Metrics: profit_factor must not collapse `inf` to `0.0`; win_rate/winning/losing trade classification must count closed trades only; calmar uses total_return / max_drawdown.
- [ ] Non-finite safety: every metric output must be JSON-serializable with `allow_nan=False`; guard all divisions.
- [ ] Add unit tests: short open/cover PnL, SL trigger, TP trigger, position sizing vs risk_pct, metrics on known equity curves.

### Phase 2: End-to-End Pipeline Robustness (CRITICAL)
- [ ] `src/main.py`: replace silent exception swallowing with recorded errors; every venue/symbol ingestion wrapped, errors logged in `results["errors"]` without aborting the run.
- [ ] Apply `normalize_options_chain` and `normalize_orderflow` to every ingested object before features/signals.
- [ ] Cross-venue symbol/timestamp consistency via `normalize_symbol` / `normalize_timestamp`.
- [ ] `--symbols` CLI override honored; JSON output (`--json`) always valid and complete.
- [ ] Structured results: per-venue chain counts, trade counts, signal details, backtest metrics, errors.

### Phase 3: Alpha Features Quantitative Hardening (HIGH)
- [ ] `src/features/gamma_exposure.py`: GEX = gamma × OI × contract_size × spot² / 100 (notional $ gamma), put GEX negative, call GEX positive; gamma flip detection by strike.
- [ ] `src/features/volatility.py`: PCR by volume and OI; IV skew (OTM put IV − OTM call IV); max pain strike minimizing total pain; guard call_volume == 0 (return inf or 0, never crash).
- [ ] `src/features/orderflow.py`: CVD, trade imbalance ratio, aggressive flow detection (size > threshold × avg), funding/OI context.
- [ ] `src/signals/composite.py`: regime-aware weighted components, calibration, conflict resolution; confidence in [0,1].

### Phase 4: Validation & Real Tests (HIGH)
- [ ] Numeric tests for backtest shorts/sizing/SLTP/metrics — no `assert True`, no placeholders.
- [ ] Integration test exercising full pipeline with mocked or real public data where safe.
- [ ] All tests pass: `python -m pytest -q`. CI must be green.

### Phase 5: Hygiene & Clean Commits (MED)
- [ ] No `__pycache__`/`*.pyc` tracked in git (enforced via `.gitignore` + `git rm --cached`).
- [ ] Clean, descriptive commit messages matching repo style (`chore(kilo): ...`).
- [ ] Working tree clean before each checkpoint.

**RULES:** Heavy engineering only. No scaffolding-only "done". Mathematical correctness is mandatory. Vectorize where sensible. Every change must be concrete and functional. Future agents must do substantial implementation work.

## BOTTLENECKS REMOVED (this session)
- **Bottleneck:** `__pycache__/*.pyc` files tracked in git index, polluting `git status` and checkpoints → **REMOVED** via `git rm --cached` on 12 bytecode files (`.gitignore` already excludes them going forward).
- **Bottleneck:** Prior CI run failed because `tests/test_controller_progress_accounting.py` was missing → **RESOLVED** (file exists, 30 tests pass).
- **Bottleneck:** Deribit/OKX/Binance connectors not implemented → **DONE** (all three present).
- **Bottleneck:** CLI not wiring all venues → **DONE** (`src/main.py` wires deribit, okx, binance).
- **Bottleneck:** Normalization utilities missing → **DONE** (`src/data/normalization.py` present).

## REMAINING BOTTLENECKS → ASSIGNED TO FOCUS CAMPAIGN
- Backtest engine correctness (short equity, SL/TP, profit_factor inf, max drawdown limit) → Phase 1.
- Silent exception swallowing in pipeline → Phase 2.
- Alpha feature quantitative rigor → Phase 3.
- Missing numeric tests for backtest/features → Phase 4.

## CURRENT STATE
- 30 tests passing (`python -m pytest -q`)
- All three venues (deribit/okx/binance) connectors implemented
- CLI end-to-end wiring present (`src/main.py`)
- Normalization utilities present (`src/data/normalization.py`)
- Config in place (`config/settings.yaml`)
- Features (GEX, orderflow, volatility) and composite signals implemented
- `.gitignore` excludes `__pycache__/`, `*.pyc`, `.pytest_cache/`, data files, logs

**NEXT ACTION:** Start with Phase 1 — harden `src/backtest/engine.py` for short equity correctness, SL/TP enforcement, risk limits, and non-finite-safe metrics. Make heavy concrete changes.
