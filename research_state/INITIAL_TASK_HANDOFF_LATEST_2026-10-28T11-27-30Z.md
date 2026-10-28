# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T11-27-30Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 92 TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- No blocked or inefficient sessions detected. Working tree clean. 92 tests passing. No TODO/FIXME/HACK/PLACEHOLDER markers in src/ or tests/.
- Phase 5 item 1 (realistic fill/slippage model) already COMPLETE in src/backtest/engine.py + tests/test_backtest.py (partial_fill_rate, round_lot_size, max_slippage_bps, slippage_seed, partial-fill path, transaction-cost-aware sizing, stop-loss/take-profit enforcement, max_drawdown_limit, isfinite guards).
- Phases 1-4 (gamma exposure, orderflow microstructure, volatility surface/skew, regime-aware signals) already implemented + tested. Mark COMPLETE.
- Real remaining heavy work: Phase 5 item 2 (walk-forward / rolling-window backtest — NOT implemented anywhere in src/) then Phase 6 (integration, resilience & tests).

## IMMEDIATE TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

START IMMEDIATELY AT PHASE 5 ITEM 2. Do NOT re-implement the fill/slippage model — it is done.
Pick the HIGHEST-IMPACT uncompleted item and implement it FULLY with tests.
HIGHEST-IMPACT ITEM: walk-forward / rolling-window backtest capability (do this first).

Scope for this single item (COMPLETE FULLY):
1. Add walk-forward / rolling-window backtest to src/backtest/engine.py (or a new src/backtest/walkforward module): re-fit/regenerate signals over rolling windows, out-of-sample evaluation, walk-forward stability metrics. Must reuse existing BacktestEngine and BacktestConfig.
2. Add numerical stability for the walk-forward path: finite guards (isfinite), safe division, clamping, handle empty price curves, avoid NaN/inf propagation. Vectorize with numpy where sensible.
3. Add/extend tests in tests/test_backtest.py or tests/test_backtest_numeric.py covering normal cases, edge cases (empty curves, zero volatility, all-losing trades, missing prices, single window), and numerical stability. All new code must be tested.
4. Export via src/backtest/__init__.py if new public functions are added. Follow existing code style. No placeholders/TODOs/FIXMEs. NO cosmetic changes.
Complete ONE major item fully; leave heavy work for next agent. Do not jump to Phase 6 until walk-forward is fully implemented with tests and passing.

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
### PHASE 5: BACKTEST RIGOR & RISK (HIGH) — IN PROGRESS
- [x] Realistic fill/slippage model (DONE — engine.py + tests/test_backtest.py)
- [ ] Walk-forward / rolling-window backtest + out-of-sample stability metrics (NEXT — DO THIS NOW)
- [ ] Drawdown controls, stop-loss/take-profit enforcement (DONE in engine.py; verify coverage)
- [ ] Stress tests, transaction costs, partial fills, round lots (DONE in engine.py; extend tests if needed)
- [ ] Walk-forward stability metrics, out-of-sample evaluation (part of walk-forward item above)
### PHASE 6: INTEGRATION, RESILIENCE & TESTS (HIGH)
- [ ] End-to-end pipeline tests (ingestion -> features -> signals -> backtest)
- [ ] Property-based tests, explicit finite checks across features
- [ ] Vectorization audits, campaign resume, non-finite serialization guards

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent. Never stop at scaffolding.

## EXECUTION RULES
- Worktree clean; do not create untracked junk.
- Run tests after changes (pytest). Maintain passing state (currently 92 passing).
- If you discover inefficiencies/blockers, fix them immediately before moving on.
- Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T11-27-30Z.md (AUTHORITATIVE - THIS FILE)
2. research_state/durable_handoff.md (MIRROR)
3. Prior LATEST files superseded.

EXECUTE NOW. START AT PHASE 5 ITEM 2 (WALK-FORWARD / ROLLING-WINDOW BACKTEST). NO DELAY. DO HEAVY WORK.
