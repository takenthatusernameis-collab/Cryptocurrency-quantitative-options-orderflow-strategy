# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): $(date -u +%Y-%m-%dT%H:%M:%SZ)
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 97 TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- No blocked/inefficient sessions detected. Working tree clean.
- 97/97 tests passing (pytest). No TODO/FIXME/HACK/PLACEHOLDER markers in src/ or tests/.
- Phases 1-5 complete: gamma exposure, orderflow microstructure, volatility/skew, regime-aware signals, backtest rigor (fill/slippage, walk-forward/rolling, drawdown controls, stress/tx costs/partial fills/round lots).
- Walk-forward/rolling-window backtest already implemented in src/backtest/engine.py (WalkForwardBacktest, run_walk_forward, run_rolling_window_backtest) with tests — do NOT re-implement.

## IMMEDIATE TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

START IMMEDIATELY AT PHASE 6. Pick ONE highest-impact uncompleted item and implement it FULLY with tests. Do NOT split; complete end-to-end.

HIGHEST-IMPACT ITEM: End-to-end pipeline integration tests (ingestion -> features -> signals -> backtest) + resilience hardening
- Scope (COMPLETE FULLY):
  1. Add end-to-end pipeline tests using mocked connectors (src/ingestion/mock.py or existing mocks). Exercise: load config -> validate -> ingest options+orderflow -> normalize -> compute features (gamma/orderflow/vol/liquidity) -> generate signals (composite) -> run backtest (BacktestEngine). Assert structure, finite values, no exceptions.
  2. Property-based/numeric invariant tests: explicit finite checks (isfinite) across features; safe division/clamping; empty/NaN/inf inputs; guards against propagation.
  3. Vectorization audit: identify and vectorize loops in features/signals/backtest with numpy where semantics unchanged; add tests if behavior changes.
  4. Campaign resume & non-finite serialization guards: ensure JSON uses allow_nan=False sanitization (main.py) and add explicit guards/tests for non-finite results.
  5. Export new public functions via relevant __init__.py. Follow style. No placeholders/TODOs/FIXMEs. All new code tested.

## NEXT FOCUS CAMPAIGN (MANDATORY — NEVER AVOID HEAVY WORK)
### PHASE 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING — COMPLETE
- [x] Net gamma exposure, gamma notional by delta bands, gamma flip, invariants/tests
### PHASE 2: DEEP ORDERFLOW MICROSTRUCTURE — COMPLETE
- [x] Cumulative delta robust, VWAP-adjusted delta, signed volume
- [x] Orderflow imbalance multi-horizon with decay weighting
- [x] Footprint/orderflow divergence, VPIN-style toxicity with guards
- [x] Absorption/aggressive flow, non-finite/division guards
### PHASE 3: VOLATILITY SURFACE & SKEW QUANTIFICATION — COMPLETE
- [x] IV skew term structure, put-call skew, risk reversal, max pain, ATM term structure
### PHASE 4: REGIME-AWARE SIGNAL ENGINEERING — COMPLETE
- [x] Cross-feature interactions, confidence calibration, regime detection, normalization
### PHASE 5: BACKTEST RIGOR & RISK — COMPLETE
- [x] Realistic fill/slippage (engine.py)
- [x] Walk-forward/rolling-window + OOS stability (engine.py + tests)
- [x] Drawdown controls, SL/TP, stress, tx costs, partial fills, round lots
### PHASE 6: INTEGRATION, RESILIENCE & TESTS — IN PROGRESS (START NOW)
- [ ] End-to-end pipeline tests (ingestion->features->signals->backtest)
- [ ] Property-based tests + explicit finite checks across features
- [ ] Vectorization audits
- [ ] Campaign resume + non-finite serialization guards

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent. Never stop at scaffolding.

## EXECUTION RULES
- Working tree clean; do not create untracked junk.
- Run tests after changes (python -m pytest). Maintain passing state (currently 97 passing).
- Fix inefficiencies/blockers immediately before moving on.
- Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics + rigorous backtesting.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_$(date -u +%Y-%m-%dT%H-%M-%SZ).md (AUTHORITATIVE - THIS FILE)
2. research_state/durable_handoff.md (MIRROR - UPDATE TO SAME CONTENT)
3. Prior LATEST files superseded.

EXECUTE NOW. START AT PHASE 6 (END-TO-END PIPELINE + RESILIENCE TESTS). NO DELAY. DO HEAVY WORK.
