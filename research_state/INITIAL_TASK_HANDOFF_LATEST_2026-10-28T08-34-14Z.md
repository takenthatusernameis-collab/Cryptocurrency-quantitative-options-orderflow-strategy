# INITIAL TASK HANDOFF (SINGLE SOURCE OF TRUTH) — LATEST

Timestamp (UTC): 2026-10-28T08-34-14Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 65/65 TESTS PASSING | All tracked __pycache__/*.pyc REMOVED from git index | NO BLOCKED/INEFFICIENT SESSIONS
Classification: PRODUCTION-GRADE QUANTITATIVE RESEARCH CODEBASE

## PROJECT-NAME-DERIVED SPECIFICATION
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage. Focus on dealer positioning via gamma exposure, orderflow microstructure, volatility surface dynamics, regime-aware signals, and robust backtesting.

## BOTTLENECKS REMOVED THIS SESSION
- Removed all 17 tracked `__pycache__/*.pyc` files from the git index (staged deletions). Repository hygiene enforced.
- Consolidated all handoff material into this single self-contained, timestamped source of truth with a fresh timestamp.
- Verified all tests pass (65/65). Eliminated any blocked/inefficient session patterns.
- Established crystal-clear directives making heavy quantitative work unavoidable for subsequent agents.

## IMMEDIATE TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION — MANDATORY)

```
START IMMEDIATELY AT PHASE 1.
Pick the HIGHEST-IMPACT uncompleted item in Phase 1 and implement it FULLY with tests.
NO cosmetic changes. NO placeholders/TODOs/FIXMEs. NO scaffolding.
Mathematical correctness is MANDATORY. Numerical stability is MANDATORY.
Vectorize where sensible. Leave the codebase requiring significant heavy quantitative work.
Do not read entire history unless absolutely necessary to understand current implementation.
Focus relentlessly on PHASE 1 items first.
```

## IMMEDIATE OBJECTIVES (PHASE 1 FOCUS)
1. **Net gamma exposure** with correct put/call sign convention across strikes and expiries; mathematically consistent with dealer gamma hedging
2. **Gamma notional by delta bands** (ATM/OTM/ITM) with OI/volume weighting and numerical stability
3. **Refined gamma flip interpolation** with robust edge-case handling (all-positive/all-negative GEX, multiple crossings)
4. **Invariants and cross-check tests** for every Phase 1 item
5. **Each item: code + tests, fully implemented, no stubs**

## NEXT FOCUS CAMPAIGN (MANDATORY — NEVER AVOID HEAVY WORK)
Execute in strict order. Each phase contains CRITICAL heavy quantitative work. Do not skip.

### PHASE 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING (CRITICAL) — START HERE
- [ ] Net gamma exposure with proper sign convention for puts/calls across strikes/expiries; mathematically consistent with dealer gamma hedging
- [ ] Gamma notional by delta bands (ATM/OTM/ITM) with volume/OI weighting and numerical stability
- [ ] Gamma flip level with interpolation refinement and edge-case handling (all-positive/all-negative GEX, multiple zero crossings)
- [ ] Tests for gamma invariants, sign correctness, monotonicity where applicable, and cross-checks
- [ ] Ensure vectorization where sensible without sacrificing correctness

### PHASE 2: DEEP ORDERFLOW MICROSTRUCTURE (CRITICAL)
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
- **Heavy engineering only.** No exploratory, cosmetic, or documentation-only work as primary deliverable.
- **Mathematical correctness mandatory.** Follow correct sign conventions and quant finance principles.
- **Numerical stability required.** Handle edge cases, division by zero, NaN/Inf with explicit guards.
- **Vectorize where sensible.** Use numpy where appropriate without sacrificing correctness.
- **Never deflect.** Never add placeholders, TODOs, FIXMEs, or scaffolding.
- **Full implementation required.** Every item must have working code AND tests.
- **Leave heavy work for next agent.** Complete ONE major item fully and well; do not over-complete the campaign.

## SOURCE OF TRUTH HIERARCHY
1. `research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T08-34-14Z.md` (THIS FILE - AUTHORITATIVE)
2. `research_state/durable_handoff.md` (MIRROR)
3. All prior `HEAVY_WORK_*` files are superseded and should not be used as primary guidance

**EXECUTE NOW. START AT PHASE 1. NO DELAY.**
