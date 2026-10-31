# DURABLE HANDOFF - 2026-10-31T14:00:41Z
Repo: Cryptocurrency-quantitative-options-orderflow-strategy
Goal: Build a robust, production-grade crypto options/orderflow strategy with out-of-sample validation and portfolio capabilities.

## STATUS (verified 2026-10-31T14:00:41Z)
- **Tests**: 364 passed, 0 failed (`python -m pytest tests/ -q`). Codebase is GREEN.
- **Phase 1 (Data)**: DONE - loaders, schemas, validators, synthetic fixtures present.
- **Phase 2 (Features)**: DONE - orderflow, gamma exposure, IV surface, liquidity, volatility, pricing features materialized.
- **Phase 3 (Time-series backtest)**: DONE - `scripts/run_backtest_timeseries.py` produces real metrics.
  - Latest: `research_state/BACKTEST_TIMESERIES_20261031T095347Z.json` (20 trades, win_rate 71.4%, sharpe 2.93, max_dd 0.35%, flow corr -0.458)
  - `research_state/RESULTS_SUMMARY.md` updated with non-trivial metrics.
- **Phase 4 (Walk-forward/OOS, Portfolio, Options Hedging)**: DONE - walk-forward with purge/embargo, portfolio walk-forward (BTC/ETH/SOL), options hedging integrated into backtest path.
  - `research_state/WALKFORWARD_purge_embargo_20261031T130538Z.json` (rolling windows with purge/embargo)
  - `research_state/PORTFOLIO_WALKFORWARD_20261031T130553Z.json` (correlation-aware multi-symbol)
  - `research_state/OPTIONS_HEDGING_INTEGRATED_20261031T130606Z.json`
  - Artifacts in `research_state/`, tests all green.

## BOTTLENECKS REMOVED
- Single-snapshot backtest triviality fixed via windowed time-series execution (50-trade windows).
- Flow-correlation added between orderflow imbalance and forward returns.
- Walk-forward leakage addressed with purge/embargo guards; regime tracking added.
- Portfolio walk-forward extended with correlation-aware constraints.
- Options hedging integrated into backtest path with invariant coverage.

## NEXT FOCUS CAMPAIGN (execute in strict order - heavy implementation required)
### Phase 5: Production hardening, validation rigor, and campaign automation
1. **Strengthen walk-forward robustness** - Review `src/backtest/engine.py` WalkForward/PortfolioWalkForward implementations against current artifacts. Check for proper temporal separation, leakage in regime info, and ensure embargo/purge are applied correctly in all code paths. Add explicit assertions/guards if gaps found.
2. **Expand OOS validation** - Run walk-forward on multiple synthetic regimes (trending/ranging/volatile) to stress-test stability. Generate new artifacts in `research_state/` (e.g., `WALKFORWARD_regime_*_*.json`) and update `RESULTS_SUMMARY.md` with regime-specific OOS metrics.
3. **Portfolio scaling** - Extend portfolio walk-forward to support dynamic correlation estimation, turnover constraints, and capital allocation rules (risk parity / volatility targeting). Add tests if needed and validate with correlation-aware sizing.
4. **Hedging strategy refinement** - Review options hedging integration - ensure delta/gamma hedging hooks are exercised with realistic rebalance costs/slippage. Add/adapt tests for hedging PnL decomposition and invariants under stress.
5. **Campaign orchestration & resume** - Harden `tests/test_campaign_resume.py` coverage; ensure checkpoints are atomic and resumable across long campaigns. Consider adding a script/CLI path for campaign runs with state tracking.
6. **Telemetry/serialization robustness** - Leverage existing telemetry/serialization non-finite guards. Add edge case tests if gaps remain and ensure all artifacts are JSON-serializable safely.

## IMMEDIATE FIRST ACTIONS (do NOT defer)
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q

# 2) Inspect walk-forward implementation
grep -rn "class .*WalkForward\|run_walk_forward\|PortfolioWalkForward" src/backtest/engine.py | head -40

# 3) Review purge/embargo and regime logic
grep -rn "purge\|embargo\|regime_info" src/backtest/engine.py | head -30

# 4) Exercise walk-forward/portfolio on current synthetic data
python -c "
# Try to call walk-forward APIs
from src.backtest import engine
# see available functions
" 2>&1 | tail -40

# 5) Run OOS/walkforward/portfolio/hedging related tests
python -m pytest tests/test_oos_walkforward.py tests/test_walkforward_robustness_adversarial.py tests/test_portfolio_walkforward_correlation_adversarial.py tests/test_campaign_resume.py tests/test_options_hedging.py -v 2>&1 | tail -25
```

## HARD CONSTRAINTS
- **No checkpoint spam**: Only commit when adding executable code, tests, data artifacts, or passing validation.
- **Heavy work required**: Implement, don't just analyze. Fix issues found, don't paper over them.
- **Deterministic & reproducible**: All runs headless, artifacts to `research_state/`, configs explicit.
- **Fail-forward**: If APIs are awkward, extend them. If tests reveal bugs, fix them.
- **Ship every session**: New code/tests/artifacts or concrete fixes with passing tests.
- **Don't redo completed phases**: Phases 1-4 are DONE. Build on them.

## SUCCESS CRITERIA (before next handoff)
- [ ] At least one new regime-based OOS artifact in `research_state/` (e.g., `WALKFORWARD_regime_trending_*.json`) with train/test split and IS/OOS metrics reported separately
- [ ] Portfolio walk-forward extended with at least one new constraint (dynamic correlation OR turnover/capital allocation) with validation
- [ ] Options hedging path exercised with rebalance costs/slippage or hedging decomposition; related tests pass
- [ ] Concrete robustness improvement (code change + test/artifact) showing leak prevention or stability gain
- [ ] All tests green: `python -m pytest tests/ -q` still passes
- [ ] `research_state/RESULTS_SUMMARY.md` updated with Phase 5 findings/metrics
