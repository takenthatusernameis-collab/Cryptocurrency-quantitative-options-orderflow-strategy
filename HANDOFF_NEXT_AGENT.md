# DURABLE HANDOFF - 2026-10-31T14:45:47Z
Repo: Cryptocurrency-quantitative-options-orderflow-strategy
Goal: Build a robust, production-grade crypto options/orderflow strategy with out-of-sample validation and portfolio capabilities.

## STATUS (verified 2026-10-31T14:45:47Z)
- **Tests**: 366 passed, 0 failed (`python -m pytest tests/ -q`). Codebase is GREEN.
- **Working tree**: clean, branch `main` up to date with `origin/main`.
- **Phases 1-4**: COMPLETE - data/loaders, features (orderflow/gamma/IV/liquidity/vol/pricing), time-series backtest, walk-forward/OOS with purge/embargo, portfolio walk-forward, options hedging integrated. Artifacts exist in `research_state/`.
- **Phase 5 Priority 1 - Regime-stratified OOS**: COMPLETE (2026-10-31T14:45:13Z). `src/backtest/regime_stress.py` + 4 artifacts (`WALKFORWARD_regime_{trending,ranging,high_vol_chop,liquidity_thin}_*.json`) + `tests/test_regime_stress_oos.py`. `research_state/RESULTS_SUMMARY.md` updated with Phase 5 section.

## BOTTLENECKS REMOVED
- None currently blocking. Single-snapshot triviality fixed (windowed time-series). Flow correlation added; leakage guarded via purge/embargo; regime tracking; correlation-aware portfolio; hedging integrated.
- **Stale initial task retired**: The previous "initial task" (regime-stratified OOS stress suite) is DONE. Do NOT re-run it as the opening task. Start on the new initial task below.
- Next agent starts from a clean green baseline; no open bottlenecks.

## SINGLE CLEAR INITIAL TASK MESSAGE (for next agent)
**START IMMEDIATELY (HEAVY WORK - DO NOT ANALYZE ONLY):**
"Implement and validate **portfolio scaling with constraints** on the crypto options/orderflow walk-forward. Repo priority: crypto options/orderflow strategy needs risk-aware capital allocation, not just per-symbol backtests.
1) Extend `src/backtest/engine.py` `PortfolioWalkForwardBacktest`/`run_portfolio_walk_forward` with: (a) **turnover cap** per window (max portfolio turnover fraction, penalize/reject breaches), (b) **vol-target / risk-parity allocation** across symbols (inverse-vol or equal-risk weights scaled to a target portfolio vol), (c) keep existing rolling correlation constraint + max_correlation. Allocation must be computed on in-sample/train data only and applied out-of-sample (no lookahead).
2) Add tests in `tests/test_portfolio_walkforward_correlation_adversarial.py` (or new `tests/test_portfolio_scaling.py`) covering: turnover cap enforcement (breach → scaled/rejected, finite), vol-target/risk-parity weights sum to 1 and are finite, allocation stability across regimes, no-lookahead (weights derived only from train window), serialization `allow_nan=False`, determinism (run twice identical).
3) Produce `research_state/PORTFOLIO_SCALING_{YYYYMMDDTHHMMSSZ}.json` (>=2 allocation modes, e.g. risk-parity vs vol-target, with turnover cap on/off) containing per-window weights, turnover, OOS metrics, correlation matrices.
4) Update `research_state/RESULTS_SUMMARY.md` with a 'Phase 5: Portfolio Scaling' section.
5) Ensure all tests pass (`python -m pytest tests/ -q` green). Extend APIs if awkward (fail-forward). Do not skip implementation for discussion."

## NEXT FOCUS CAMPAIGN (execute after/while doing the initial task)
### Phase 5: Production hardening, validation rigor, and campaign automation
1. **Regime-stratified OOS** - DONE (artifacts + module + tests).
2. **Portfolio scaling with constraints** (PRIORITY 2, NOW) - turnover caps, vol-target/risk-parity allocation, validation, artifact, tests. = current initial task.
3. **Hedging robustness** - Exercise delta/gamma hedging with realistic rebalance costs/slippage, produce hedging PnL decomposition, add invariants/stress tests. (`src/backtest/options_hedging.py`, `tests/test_options_hedging.py` exist; extend with cost/slippage params + decomposition.)
4. **Campaign resume hardening** - Strengthen `tests/test_campaign_resume.py` (currently minimal), ensure atomic checkpoints/resumability; add minimal `scripts/run_campaign.py` with state tracking if missing orchestration.
5. **Telemetry/serialization** - Harden guards for non-finite/NaN/Inf, ensure JSON-serializable artifacts under all regimes (`tests/test_nonfinite_result_serialization.py` exists; extend guards).

## IMMEDIATE FIRST ACTIONS
```bash
# 1) Confirm green baseline
python -m pytest tests/ -q

# 2) Understand portfolio walk-forward API to extend cleanly
grep -n "class PortfolioWalkForwardBacktest\|def run_portfolio_walk_forward\|max_correlation\|correlation_window" src/backtest/engine.py | head -40

# 3) Run portfolio + options + campaign + telemetry tests
python -m pytest tests/test_portfolio_walkforward_correlation_adversarial.py tests/test_options_hedging.py tests/test_campaign_resume.py tests/test_nonfinite_result_serialization.py -v 2>&1 | tail -30

# 4) Implement turnover cap + vol-target/risk-parity allocation in PortfolioWalkForwardBacktest; add tests; run one scaling config
# (implement per initial task above)
```

## HARD CONSTRAINTS
- **Heavy implementation required**: Code/tests/artifacts, not just analysis/reports.
- **No checkpoint spam**: Commit only when adding executable code/tests/data/artifacts or passing validation.
- **Deterministic & reproducible**: Headless, `research_state/` artifacts, explicit configs.
- **Fail-forward**: Extend APIs if awkward; fix bugs found.
- **Ship every session**: New code/tests/artifacts or concrete fixes with passing tests.
- **Don't redo completed phases**: 1-4 done + regime OOS done - build on them.

## SUCCESS CRITERIA
- [ ] `python -m pytest tests/ -q` still green (>=366 passed)
- [ ] Portfolio scaling: turnover cap + vol-target/risk-parity allocation implemented in `src/backtest/engine.py`
- [ ] Scaling tests added/extended, passing (turnover enforcement, weight sums, no-lookahead, serialization, determinism)
- [ ] `research_state/PORTFOLIO_SCALING_*.json` artifact with >=2 allocation modes
- [ ] `research_state/RESULTS_SUMMARY.md` updated with Phase 5: Portfolio Scaling section
- [ ] Then continue campaign: hedging robustness, campaign resume, telemetry hardening
