# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T11-22-40Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 89 TESTS PASSING | NO BLOCKED/INEFFICIENT SESSIONS | WORKING TREE CLEAN
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- Audited session state: no blocked/inefficient sessions detected. All prior checkpoints reviewed; working tree clean. 89 tests passing. No TODO/FIXME/HACK/PLACEHOLDER markers in src/ or tests/. Bottlenecks eliminated.

## IMMEDIATE TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

START IMMEDIATELY AT PHASE 3 - FIRST ITEM.
Pick the HIGHEST-IMPACT uncompleted item in Phase 3 and implement it FULLY with tests.
HIGHEST-IMPACT ITEM: IV skew term structure (do this first).
Scope for this single item (COMPLETE FULLY):
1. Implement robust functions in src/features/volatility.py for IV skew term structure: compute skew by expiry/tenor with put-call skew, risk reversal (e.g. RR = IV_OTM_call - IV_OTM_put at same delta/tenor), term structure of skew/RR, and integrate with existing patterns.
2. Add numerical stability: finite guards (isfinite), safe division, clamping where appropriate, handle missing IVs/deltas, avoid NaN/inf propagation. Vectorize with numpy where sensible.
3. Add/extend tests in tests/test_features.py (or new tests/test_volatility_skew.py if cleaner) covering normal cases, edge cases (missing data, zero OI/volume, extreme strikes), and numerical stability. All new code must be tested.
4. Export via src/features/__init__.py if needed. Follow existing code style. No placeholders/TODOs/FIXMEs. NO cosmetic changes.
Complete ONE major item fully; leave heavy work for next agent. Do not jump to Phase 4 until this item is fully implemented with tests and passing.

## NEXT FOCUS CAMPAIGN (MANDATORY — NEVER AVOID HEAVY WORK)
### PHASE 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING — COMPLETE
### PHASE 2: DEEP ORDERFLOW MICROSTRUCTURE — COMPLETE
- [x] Cumulative delta robust, VWAP-adjusted delta, signed volume
- [x] Orderflow imbalance multi-horizon with decay weighting (extended + hardened)
- [x] Footprint/orderflow divergence metrics (hardened)
- [x] VPIN-style toxicity proxy with finite-sample guards
- [x] Absorption detection, aggressive flow
- [x] Non-finite/division guards, property tests
### PHASE 3: VOLATILITY SURFACE & SKEW QUANTIFICATION (CRITICAL) — IN PROGRESS
- [ ] IV skew term structure (FIRST - DO THIS NOW)
- [ ] Put-call skew
- [ ] Risk reversal
- [ ] Max pain (already has basic impl; harden if gaps found)
- [ ] Term structure
### PHASE 4: REGIME-AWARE SIGNAL ENGINEERING (CRITICAL)
### PHASE 5: BACKTEST RIGOR & RISK (HIGH)
### PHASE 6: INTEGRATION, RESILIENCE & TESTS (HIGH)

## MANDATE (UNCOMPROMISING)
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. No placeholders/TODOs/FIXMEs. Full implementation with code AND tests. Complete ONE major item fully; leave heavy work for next agent. Never stop at scaffolding.

## EXECUTION RULES
- Worktree clean; do not create untracked junk.
- Run tests after changes (pytest). Maintain passing state.
- If you discover inefficiencies/blockers, fix them immediately before moving on.
- Prioritize by project name: crypto options orderflow + dealer positioning + surface dynamics.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_$(date -u +%Y-%m-%dT%H-%M-%SZ).md (AUTHORITATIVE - THIS FILE)
2. research_state/durable_handoff.md (MIRROR)
3. Prior LATEST files superseded.

EXECUTE NOW. START AT PHASE 3 FIRST ITEM (IV SKEW TERM STRUCTURE). NO DELAY. DO HEAVY WORK.
