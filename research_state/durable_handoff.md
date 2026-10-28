# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T11-23-39Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 92 TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- Corrected stale handoff state: prior LATEST files listed Phase 3 (IV skew term structure, put-call skew, risk reversal, term structure) and Phase 4 (regime-aware signals) as unchecked/in-progress, but the code already implements and tests all of them (src/features/volatility.py fully implemented + exported; tests in tests/test_features.py incl. test_iv_skew_term_structure_and_atm, test_iv_skew_term_structure_numerical_stability, test_risk_reversal_and_put_call_skew; src/signals/composite.py + tests/test_signals_regime.py with 12 regime/confidence/direction tests). Marking Phase 3 and Phase 4 COMPLETE so the next agent does not re-do finished work.
- Audited session state: no blocked/inefficient sessions detected. Working tree clean. 92 tests passing. No TODO/FIXME/HACK/PLACEHOLDER markers in src/ or tests/. CI edit-tool invalid-argument noise in prior workflow runs is a tooling artifact, not a code blocker.
- Real remaining heavy work is Phase 5 (backtest rigor & risk) and Phase 6 (integration, resilience & tests). Next focus campaign targets these.

## IMMEDIATE TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

START IMMEDIATELY AT PHASE 5 - FIRST ITEM.
Pick the HIGHEST-IMPACT uncompleted item in Phase 5 and implement it FULLY with tests.
HIGHEST-IMPACT ITEM: realistic fill/slippage model + walk-forward backtest (do this first).
Scope for this single item (COMPLETE FULLY):
1. Extend src/backtest/engine.py with realistic fill modeling: partial fill rate, round-lot rounding, max slippage cap, deterministic slippage seed, partial-fill execution path, and transaction-cost-aware position sizing. Integrate with existing BacktestConfig fields (partial_fill_rate, round_lot_size, max_slippage_bps, slippage_seed).
2. Add walk-forward / rolling-window backtest capability: re-fit/regenerate signals over rolling windows, out-of-sample evaluation, stability metrics.
3. Add numerical stability: finite guards (isfinite), safe division, clamping, handle empty price curves, avoid NaN/inf propagation in metrics (sharpe, sortino, max_drawdown, calmar, profit_factor, win_rate). Vectorize with numpy where sensible.
4. Add/extend tests in tests/test_backtest.py or tests/test_backtest_numeric.py covering normal cases, edge cases (empty curves, zero volatility, all-losing trades, missing prices), and numerical stability. All new code must be tested.
5. Export via src/features/__init__.py or src/backtest/__init__.py if new public functions are added. Follow existing code style. No placeholders/TODOs/FIXMEs. NO cosmetic changes.
Complete ONE major item fully; leave heavy work for next agent. Do not jump to Phase 6 until this item is fully implemented with tests and passing.

## NEXT FOCUS CAMPAIGN (MANDATORY — NEVER AVOID HEAVY WORK)
### PHASE 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING — COMPLETE
- [x] Net gamma exposure, gamma notional by delta bands, gamma flip, invariants/tests
### PHASE 2: DEEP ORDERFLOW MICROSTRUCTURE — COMPLETE
- [x] Cumulative delta robust, VWAP-adjusted delta, signed volume
- [x] Orderflow imbalance multi-horizon with decay weighting (extended + hardened)
- [x] Footprint/orderflow divergence metrics (hardened)
- [x] VPIN-style toxicity proxy with finite-sample guards
- [x] Absorption detection, aggressive flow
- [x] Non-finite/division guards, property tests
### PHASE 3: VOLATILITY SURFACE & SKEW QUANTIFICATION — COMPLETE
- [x] IV skew term structure
- [x] Put-call skew
- [x] Risk reversal
- [x] Max pain
- [x] Term structure (ATM IV term structure)
### PHASE 4: REGIME-AWARE SIGNAL ENGINEERING — COMPLETE
- [x] Cross-feature interactions, confidence calibration, regime detection, normalization
### PHASE 5: BACKTEST RIGOR & RISK (HIGH) — NEXT FOCUS / IN PROGRESS
- [ ] Realistic fill/slippage model + walk-forward backtest (FIRST - DO THIS NOW)
- [ ] Drawdown controls, stop-loss/take-profit enforcement
- [ ] Stress tests, transaction costs, partial fills, round lots
- [ ] Walk-forward stability metrics, out-of-sample evaluation
### PHASE 6: INTEGRATION, RESILIENCE & TESTS (HIGH)
- [ ] End-to-end pipeline tests (ingestion -> features -> signals -> backtest)
- [ ] Property-based tests, explicit finite checks across features
- [ ] Vectorization audits, campaign resume, non-finite serialization guards

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent. Never stop at scaffolding.

## EXECUTION RULES
- Worktree clean; do not create untracked junk.
- Run tests after changes (pytest). Maintain passing state.
- If you discover inefficiencies/blockers, fix them immediately before moving on.
- Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T11-23-39Z.md (AUTHORITATIVE - THIS FILE)
2. research_state/durable_handoff.md (MIRROR)
3. Prior LATEST files superseded.

EXECUTE NOW. START AT PHASE 5 FIRST ITEM (REALISTIC FILL/SLIPPAGE + WALK-FORWARD BACKTEST). NO DELAY. DO HEAVY WORK.
