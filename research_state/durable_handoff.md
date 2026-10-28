# DURABLE HANDOFF — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T08-34-14Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: ACTIVE-HANDOFF | HEAD clean relative to origin/main
State: 65/65 TESTS PASSING | All tracked __pycache__/*.pyc removed from git index
Mandate: HEAVY QUANTITATIVE ENGINEERING ONLY — NO PLACEHOLDERS, NO SCAFFOLDING, NO COSMETIC WORK

## SINGLE SOURCE OF TRUTH
**Primary:** `research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T08-34-14Z.md`
**Mirror:** This file. Both are identical in content. The LATEST timestamped file is authoritative.

## PROJECT SPEC (Derived from Name)
Build a mathematically correct, production-grade **crypto options orderflow strategy** with rigorous numerical stability, correct dealer-positioning sign conventions, and full test coverage. Every implementation must be grounded in quant finance fundamentals.

## BOTTLENECKS REMOVED
- ✅ All tracked `__pycache__/*.pyc` files removed from git index (staged deletions)
- ✅ Consolidated handoffs into clear, unambiguous source of truth with fresh timestamps
- ✅ All existing tests pass (65/65). No blocked or inefficient sessions remain.
- ✅ Repository hygiene restored; working tree clean of tracked bytecode noise

## MANDATORY INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION)

```
IMMEDIATE ACTION REQUIRED - START NOW

You are continuing work on Cryptocurrency-quantitative-options-orderflow-strategy.
This is HEAVY QUANTITATIVE ENGINEERING. Do not do exploratory reading, documentation-only work, or cosmetic refactoring.

READ FIRST: research_state/INITIAL_TASK_HANDOFF_LATEST_2026-10-28T08-34-14Z.md

EXECUTION DIRECTIVE:
1. START AT PHASE 1 - Pick the SINGLE HIGHEST-IMPACT uncompleted item
2. IMPLEMENT FULLY - Code + tests, no stubs/TODOs/placeholders
3. MAKE IT MATHEMATICALLY CORRECT - Follow dealer gamma hedging conventions precisely
4. ENSURE NUMERICAL STABILITY - Handle all edge cases, division by zero, NaN/Inf explicitly
5. LEAVE HEAVY WORK FOR NEXT AGENT - Do not "complete" everything; do ONE major item completely and well, making subsequent phases clearly necessary

GOLDEN RULE: Mathematical correctness > elegance. Numerical stability > speed. Full implementation > scaffolding.
```

## NEXT FOCUS CAMPAIGN - EXECUTE IN ORDER, NEVER SKIP HEAVY WORK

### PHASE 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING (CRITICAL) ⚡ START HERE
- [ ] **Net gamma exposure with correct sign convention** across strikes/expiries; mathematically consistent with dealer gamma hedging (calls: +, puts: - in dealer positioning convention as implemented; verify rigorously)
- [ ] **Gamma notional by delta bands (ATM/OTM/ITM)** with OI/volume weighting and numerical stability; handle missing deltas gracefully
- [ ] **Gamma flip level interpolation refinement** - robust handling of all-positive/all-negative GEX, multiple crossings, flat regions, numerical precision
- [ ] **Gamma invariants & cross-check tests** - verify sums, signs, monotonicity where valid; property-based where sensible

### PHASE 2: DEEP ORDERFLOW MICROSTRUCTURE (CRITICAL)
- [ ] **Cumulative delta with robust trade classification** (aggressive/passive), VWAP-adjusted delta, signed volume with proper side handling
- [ ] **Multi-horizon orderflow imbalance** (tick/1m/5m) with exponential/time decay weighting
- [ ] **Footprint/orderflow divergence metrics** (delta divergence vs price, absorption detection, exhaustion signals)
- [ ] **VPIN-style toxicity proxy/trade intensity** with finite-sample guards, rolling windows, numerical stability

### PHASE 3: VOLATILITY SURFACE & SKEW QUANTIFICATION (CRITICAL)
- [ ] **Robust IV skew term structure** (wing skew, butterfly) with moneyness/delta interpolation; handle missing/outliers
- [ ] **Risk reversal, put-call skew, calendar spread proxies** with proper handling of missing IVs
- [ ] **Gamma-weighted max pain** alongside robust OI-based max pain; interpolation and edge cases
- [ ] **Term structure slope metrics integrated with regime detection**

### PHASE 4: REGIME-AWARE SIGNAL ENGINEERING (CRITICAL)
- [ ] **Cross-feature interactions** (GEX×orderflow, skew×PCR) with principled conflict resolution
- [ ] **Dispersion/entropy-based confidence calibration** with proper normalization
- [ ] **Regime detection with hysteresis/stability**; deterministic, no lookahead
- [ ] **Integration with position sizing constraints from backtest engine**

### PHASE 5: BACKTEST RIGOR & RISK (HIGH)
- [ ] **Realistic fills**: lot sizing, partial fills, slippage model (linear/impact), max slippage caps, fees/commissions
- [ ] **Risk controls**: drawdown controls, Kelly/fractional sizing, exposure limits, correlation-aware constraints
- [ ] **Walk-forward split logic hooks**, numeric robustness (no NaN/Inf leaking to metrics)
- [ ] **Stress tests** (gaps, liquidity droughts) and metric invariants (PnL consistency)

### PHASE 6: INTEGRATION, RESILIENCE & TESTS (HIGH)
- [ ] **Wire all features through main/workflow paths** with strict validation
- [ ] **Property-based tests** for monotonicity/invariants where mathematically valid
- [ ] **Eliminate silent failures**; explicit finite checks everywhere
- [ ] **Full vectorization where sensible without sacrificing correctness**

## ABSOLUTE MANDATES
- **Heavy engineering only.** Mathematical correctness mandatory. Numerical stability required.
- **Vectorize where sensible.** No placeholders, TODOs, FIXMEs, or "pass" stubs.
- **Test everything.** Every new function needs tests; existing tests must keep passing.
- **No deflection.** No cosmetic changes. No documentation-only work as the deliverable.
- **Leave work unfinished.** After completing ONE major item fully, the codebase must still require significant heavy quantitative work across remaining phases.
