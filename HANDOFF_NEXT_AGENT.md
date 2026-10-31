# DURABLE HANDOFF - 2026-10-31T14:02:52Z
Repo: Cryptocurrency-quantitative-options-orderflow-strategy
Goal: Build a robust, production-grade crypto options/orderflow strategy with out-of-sample validation and portfolio capabilities.

## STATUS (verified 2026-10-31T14:02:52Z)
- **Tests**: 364 passed, 0 failed (`python -m pytest tests/ -q`). Codebase is GREEN.
- **Phases 1-4**: COMPLETE - data/loaders, features (orderflow/gamma/IV/liquidity/vol/pricing), time-series backtest, walk-forward/OOS with purge/embargo, portfolio walk-forward, options hedging integrated. Artifacts exist in `research_state/`.
- **Recent artifacts**: `BACKTEST_TIMESERIES_20261031T095347Z.json`, `WALKFORWARD_purge_embargo_20261031T130538Z.json`, `PORTFOLIO_WALKFORWARD_20261031T130553Z.json`, `OPTIONS_HEDGING_INTEGRATED_20261031T130606Z.json`, `RESULTS_SUMMARY.md`.

## BOTTLENECKS REMOVED
- Single-snapshot triviality fixed (windowed time-series).
- Flow correlation added; leakage guarded via purge/embargo; regime tracking; correlation-aware portfolio; hedging integrated.

## SINGLE CLEAR INITIAL TASK MESSAGE (for next agent)
**START IMMEDIATELY (HEAVY WORK - DO NOT ANALYZE ONLY):**
"Implement and validate a **regime-stratified OOS stress suite** focused on crypto options/orderflow.
1) Add `src/backtest/regime_stress.py` that generates synthetic regimes (trending, ranging, high-vol/chop, liquidity-thin) with crypto-realistic orderflow/gamma/IV microstructure (respect existing schemas/fixtures).
2) Extend walk-forward to run per-regime with strict purge/embargo, log train/test splits, IS/OOS metrics (sharpe/Sortino/CAGR/maxDD/turnover/winrate) separately.
3) Produce `research_state/WALKFORWARD_regime_{regime}_{YYYYMMDDTHHMMSSZ}.json` for >=3 regimes and update `research_state/RESULTS_SUMMARY.md` with a 'Phase 5: Regime OOS' section.
4) Add/extend tests in `tests/test_oos_walkforward.py` (or new `tests/test_regime_stress_oos.py`) covering regime separation and no-lookahead.
5) Ensure all tests pass. If walk-forward APIs need extension, extend them (fail-forward). Do not skip implementation for discussion."

## NEXT FOCUS CAMPAIGN (execute after/while doing the initial task)
### Phase 5: Production hardening, validation rigor, and campaign automation
1. **Regime-stratified OOS (PRIORITY 1)** - As above; make it concrete with artifacts.
2. **Portfolio scaling with constraints** - Extend portfolio walk-forward for dynamic correlation (rolling), turnover caps, vol-target/risk-parity allocation. Validate correlation-aware sizing; add tests.
3. **Hedging robustness** - Exercise delta/gamma hedging with realistic rebalance costs/slippage, produce hedging PnL decomposition, add invariants/stress tests.
4. **Campaign resume hardening** - Strengthen `tests/test_campaign_resume.py`, ensure atomic checkpoints/resumability; if missing orchestration, add minimal `scripts/run_campaign.py` with state tracking.
5. **Telemetry/serialization** - Harden guards for non-finite/NaN/Inf, ensure JSON-serializable artifacts under all regimes.

## IMMEDIATE FIRST ACTIONS
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q

# 2) Understand walk-forward API to extend cleanly
grep -rn "class .*WalkForward\|run_walk_forward\|PortfolioWalkForward" src/backtest/engine.py | head -50
grep -rn "purge\|embargo\|regime_info" src/backtest/engine.py | head -40

# 3) Run OOS/walkforward/portfolio/hedging/campaign tests
python -m pytest tests/test_oos_walkforward.py tests/test_walkforward_robustness_adversarial.py tests/test_portfolio_walkforward_correlation_adversarial.py tests/test_campaign_resume.py tests/test_options_hedging.py -v 2>&1 | tail -30

# 4) Create regime_stress module + tests + run one regime
# (implement per initial task above)
```

## HARD CONSTRAINTS
- **Heavy implementation required**: Code/tests/artifacts, not just analysis/reports.
- **No checkpoint spam**: Commit only when adding executable code/tests/data/artifacts or passing validation.
- **Deterministic & reproducible**: Headless, `research_state/` artifacts, explicit configs.
- **Fail-forward**: Extend APIs if awkward; fix bugs found.
- **Ship every session**: New code/tests/artifacts or concrete fixes with passing tests.
- **Don't redo completed phases**: 1-4 done - build on them.

## SUCCESS CRITERIA
- [ ] >=3 regime artifacts `research_state/WALKFORWARD_regime_*.json` with IS/OOS separated
- [ ] `src/backtest/regime_stress.py` + tests added/extended, passing
- [ ] Portfolio constraints (dynamic correlation/turnover/capital alloc) implemented with validation
- [ ] Hedging with costs/slippage exercised + decomposition tests
- [ ] `research_state/RESULTS_SUMMARY.md` updated with Phase 5 findings
- [ ] `python -m pytest tests/ -q` still green
