# DURABLE HANDOFF - 2026-10-31T10:58:43Z
Repo: Cryptocurrency-quantitative-options-orderflow-strategy
Goal: Build a robust, production-grade crypto options/orderflow strategy with out-of-sample validation and portfolio capabilities.

## STATUS (verified 2026-10-31T10:58:43Z)
- **Tests**: 364 passed, 0 failed (`python -m pytest tests/ -q`). Codebase is GREEN.
- **Phase 1 (Data)**: DONE - loaders, schemas, validators, synthetic fixtures present.
- **Phase 2 (Features)**: DONE - orderflow, gamma exposure, IV surface, liquidity, volatility, pricing features materialized.
- **Phase 3 (Time-series backtest)**: DONE - `scripts/run_backtest_timeseries.py` produces real metrics.
  - Latest: `research_state/BACKTEST_TIMESERIES_20261031T095347Z.json` (20 trades, win_rate 71.4%, sharpe 2.93, max_dd 0.35%, flow corr -0.458)
  - `research_state/RESULTS_SUMMARY.md` updated with non-trivial metrics.

## BOTTLENECKS REMOVED
- Single-snapshot backtest triviality fixed via windowed time-series execution (50-trade windows).
- Flow-correlation added between orderflow imbalance and forward returns.
- Tests added for multi-trade execution and determinism.

## NEXT FOCUS CAMPAIGN (execute in strict order - heavy implementation required)
### Phase 4: Walk-forward/OOS robustness & portfolio scaling
1. **Harden walk-forward validation** - The codebase has `WalkForwardBacktest`, `run_walk_forward`, `run_rolling_window_backtest` in `src/backtest/engine.py` and tests like `test_oos_walkforward.py`, `test_walkforward_robustness_adversarial.py`. Run existing walk-forward on the synthetic data, identify leakage/lookahead issues, fix them. Ensure out-of-sample performance is reported separately.
2. **Portfolio-level backtesting** - `PortfolioWalkForwardBacktest` exists. Extend to handle multi-symbol or multi-strategy allocation, correlation-aware sizing, and realistic constraints (margin, liquidity). Add tests for correlation effects.
3. **Options hedging integration** - `src/backtest/options_hedging.py` and `tests/test_options_hedging.py`, `test_phase1_gamma_invariants.py` exist. Wire options hedging into the live backtest path (delta/gamma hedging based on gamma exposure/IV surface). Make it configurable and test invariants.
4. **Adversarial robustness hardening** - Many adversarial tests exist (routing, stress, correlation). Fix any remaining brittleness: numerical guards, serialization of non-finite results, circuit breakers. Ensure all adversarial tests remain green.
5. **Campaign resume & state management** - `tests/test_campaign_resume.py` exists. Verify resumability for long-running backtests/campaigns with checkpoints.

### IMMEDIATE FIRST ACTIONS (do NOT defer)
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q

# 2) Run walk-forward validation on existing data
python -c "
# quick check - use existing APIs
from src.backtest import run_walk_forward
# see how to call it
" 2>&1 | tail -30

# 3) Explore walk-forward implementation
grep -n "class WalkForward" src/backtest/engine.py | head -5
grep -rn "run_walk_forward" src | head -10

# 4) Run OOS/walkforward tests to see current state
python -m pytest tests/test_oos_walkforward.py tests/test_walkforward_robustness_adversarial.py -v 2>&1 | tail -20
```

## HARD CONSTRAINTS
- **No checkpoint spam**: Only commit when adding executable code, tests, data artifacts, or passing validation.
- **Heavy work required**: Implement, don't just analyze. Fix issues found, don't paper over them.
- **Deterministic & reproducible**: All runs headless, artifacts to `research_state/`, configs explicit.
- **Fail-forward**: If APIs are awkward, extend them. If tests reveal bugs, fix them.
- **Ship every session**: New code/tests/artifacts or concrete fixes with passing tests.
- **Don't redo completed phases**: Time-series backtest is DONE. Build on it.

## SUCCESS CRITERIA (before next handoff)
- [ ] Walk-forward/OOS results written to `research_state/WALKFORWARD_*.json` with train/test split, IS/OOS metrics reported separately
- [ ] At least one concrete robustness fix (leakage guard, purged CV, or proper embargo) if issues found
- [ ] Portfolio walk-forward exercised with correlation-aware logic OR meaningful extension to it
- [ ] Options hedging integrated into backtest path with tests passing (or new tests added)
- [ ] All tests green: `python -m pytest tests/ -q` still passes
- [ ] `research_state/RESULTS_SUMMARY.md` updated with Phase 4 findings/metrics
