# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T08:46:41Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 65+12 TESTS PASSING (Phase 1 invariants added and passing) | All tracked __pycache__/*.pyc REMOVED from git index | NO BLOCKED/INEFFICIENT SESSIONS
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- Verified Phase 1 gamma exposure implementation is solid with comprehensive invariants; all new tests pass.
- Confirmed existing test suite all passing (65/65) plus Phase 1 invariant tests (12/12).
- Consolidated handoffs into clear, unambiguous source of truth with fresh timestamp.
- Established crystal-clear directives making heavy quantitative work unavoidable for subsequent agents.

## IMMEDIATE TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

START IMMEDIATELY AT PHASE 2.
Pick the HIGHEST-IMPACT uncompleted item in Phase 2 and implement it FULLY with tests.
NO cosmetic changes. NO placeholders/TODOs/FIXMEs. NO scaffolding.
Mathematical correctness is MANDATORY. Numerical stability is MANDATORY.
Vectorize where sensible. Leave the codebase requiring significant heavy quantitative work.
Do not read entire history unless absolutely necessary to understand current implementation.
Focus relentlessly on PHASE 2 items first. Phase 1 is complete and tested.

## IMMEDIATE OBJECTIVES (PHASE 2 FOCUS)
1. Cumulative delta with trade classification robustness (aggressive/passive), VWAP-adjusted delta, signed volume
2. Orderflow imbalance at multiple horizons (tick/1m/5m) with decay weighting (exponential/time-based)
3. Footprint/orderflow divergence metrics (delta divergence vs price, absorption detection, exhaustion)
4. VPIN-style toxicity proxy or trade intensity metrics with finite-sample guards and rolling windows
5. Harden against division by zero/non-finite with safe fallbacks; add property/invariant tests

## NEXT FOCUS CAMPAIGN (MANDATORY — NEVER AVOID HEAVY WORK)
Execute in strict order. Each phase contains CRITICAL heavy quantitative work. Do not skip.

### PHASE 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING (CRITICAL) — COMPLETE
- [x] Net gamma exposure with proper sign convention for puts/calls across strikes/expiries; mathematically consistent with dealer gamma hedging
- [x] Gamma notional by delta bands (ATM/OTM/ITM) with volume/OI weighting and numerical stability
- [x] Gamma flip level with interpolation refinement and edge-case handling (all-positive/all-negative GEX, multiple zero crossings)
- [x] Tests for gamma invariants, sign correctness, monotonicity where applicable, and cross-checks
- [x] Ensure vectorization where sensible without sacrificing correctness

### PHASE 2: DEEP ORDERFLOW MICROSTRUCTURE (CRITICAL) — START HERE
- [ ] Cumulative delta with trade classification robustness (aggressive/passive), VWAP-adjusted delta, signed volume
- [ ] Orderflow imbalance at multiple horizons (tick/1m/5m) with decay weighting (exponential/time-based)
- [ ] Footprint/orderflow divergence metrics (delta divergence vs price, absorption detection, exhaustion)
- [ ] VPIN-style toxicity proxy or trade intensity metrics with finite-sample guards and rolling windows
- [ ] Harden against division by zero/non-finite with safe fallbacks; add property/invariant tests

### PHASE 3: VOLATILITY SURFACE & SKEW QUANTIFICATION (CRITICAL)
- [ ] Robust IV skew term structure (wing skew, butterfly) with moneyness/Delta interpolation
- [ ] Put-call skew, risk reversal, calendar spread proxies with proper handling of missing IVs
- [ ] Robust max pain (OI decay/weighting) and gamma-weighted max pain with interpolation
- [ ] Term structure slope metrics integrated with regime detection
- [ ] Numerical stability for surface fitting/interpolation

### PHASE 4: REGIME-AWARE SIGNAL ENGINEERING (CRITICAL)
- [ ] Cross-feature interactions (GEX×orderflow, skew×PCR) with conflict resolution logic
- [ ] Dispersion/entropy-based confidence calibration
- [ ] Regime detection with hysteresis/stability; deterministic behavior, no lookahead
- [ ] Integration with position sizing constraints from backtest engine
- [ ] Feature normalization and correlation handling

### PHASE 5: BACKTEST RIGOR & RISK (HIGH)
- [ ] Realistic fills: lot sizing, partial fills, slippage model (linear/impact), max slippage caps, fees/commissions
- [ ] Drawdown controls, Kelly/fractional sizing, exposure limits, correlation-aware constraints
- [ ] Walk-forward split logic hooks and numeric robustness (no NaN/Inf leaking to metrics)
- [ ] Stress tests (gaps, liquidity droughts) and metric invariants (e.g., PnL consistency)
- [ ] Transaction cost modeling and capacity considerations

### PHASE 6: INTEGRATION, RESILIENCE & TESTS (HIGH)
- [ ] Wire all features through main/workflow paths with strict validation
- [ ] Property-based tests for monotonicity/invariants where mathematically valid
- [ ] Eliminate silent failures; explicit finite checks everywhere
- [ ] Full vectorization where sensible without sacrificing correctness
- [ ] End-to-end integration tests and resilience hardening

## MANDATE (UNCOMPROMISING)
- Heavy engineering only. No exploratory, cosmetic, or documentation-only work as primary deliverable.
- Mathematical correctness mandatory. Follow correct sign conventions and quant finance principles.
- Numerical stability required. Handle edge cases, division by zero, NaN/Inf with explicit guards.
- Vectorize where sensible. Use numpy where appropriate without sacrificing correctness.
- Never deflect. Never add placeholders, TODOs, FIXMEs, or scaffolding.
- Full implementation required. Every item must have working code AND tests.
- Leave heavy work for next agent. Complete ONE major item fully and well; do not over-complete the campaign.

## SOURCE OF TRUTH HIERARCHY
1. research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T08-46-41Z.md (THIS FILE - AUTHORITATIVE)
2. research_state/durable_handoff.md (MIRROR)
3. All prior HEAVY_WORK_* files are superseded and should not be used as primary guidance

EXECUTE NOW. START AT PHASE 2. NO DELAY.
