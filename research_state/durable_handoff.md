# Durable Handoff — Cryptocurrency Quantitative Options Orderflow Strategy

Timestamp (UTC): 2026-10-28T07-31-56Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Run Context: ACTIVE-HANDOFF. HEAD clean relative to origin/main. Working tree has tracked pycache removal staged. 65 tests passing. Heavy engineering only.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION — MANDATORY)

See `research_state/HEAVY_WORK_INITIAL_TASK_2026-10-28T07-31-56Z.md` for the full timestamped message. This file supersedes all earlier `research_state/HEAVY_WORK_INITIAL_TASK_*.md`, `research_state/HEAVY_WORK_HANDOFF_*.md`, and previous `durable_handoff.md` revisions.

**PRIORITY 1: HEAVY QUANTITATIVE IMPLEMENTATION — NO SCAFFOLDING, NO PLACEHOLDERS**

Project name is the spec: "Cryptocurrency-quantitative-options-orderflow-strategy". Build a mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage.

### BOTTLENECKS REMOVED THIS SESSION
- Removed all tracked `__pycache__/*.pyc` from git index (staged deletions). Clean repo hygiene restored.
- Verified 65/65 tests passing. No blocked sessions.
- Consolidated handoff to single source of truth with fresh timestamp.

### NEXT FOCUS CAMPAIGN (MANDATORY - NEVER AVOID HEAVY WORK)
#### PHASE 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING (CRITICAL)
- [ ] Implement net gamma exposure with proper sign convention for puts/calls across strikes/expiries; ensure mathematical consistency with dealer gamma hedging
- [ ] Add gamma notional by delta bands (ATM/OTM/ITM) with volume/OI weighting and numerical stability
- [ ] Compute gamma flip with interpolation refinement and edge case handling (all-positive/all-negative GEX)
- [ ] Add tests for gamma invariants, monotonicity where applicable, and cross-checks

#### PHASE 2: DEEP ORDERFLOW MICROSTRUCTURE (CRITICAL)
- [ ] Implement cumulative delta with trade classification robustness (aggressive/passive), VWAP-adjusted delta, and signed volume
- [ ] Add orderflow imbalance at multiple horizons (tick/1m/5m) with decay weighting
- [ ] Implement footprint/orderflow divergence metrics (delta divergence vs price, absorption detection)
- [ ] Add VPIN-style toxicity proxy or trade intensity metrics with finite-sample guards
- [ ] Harden against division by zero/non-finite with safe fallbacks; add property tests

#### PHASE 3: VOLATILITY SURFACE & SKEW QUANTIFICATION (CRITICAL)
- [ ] Implement robust IV skew term structure (wing skew, butterfly) with moneyness/Delta interpolation
- [ ] Add put-call skew, risk reversal, calendar spread proxies with proper handling of missing IVs
- [ ] Compute max pain more robustly (with OI decay/weighting) and add gamma-weighted max pain
- [ ] Add term structure slope metrics and regime classification integration

#### PHASE 4: REGIME-AWARE SIGNAL ENGINEERING (CRITICAL)
- [ ] Strengthen composite signal with cross-feature interactions (GEX×orderflow, skew×PCR) and conflict resolution
- [ ] Improve confidence calibration with dispersion/entropy-based measures and out-of-sample style checks
- [ ] Add regime detection with hysteresis and stability; ensure deterministic behavior
- [ ] Integrate signals with position sizing constraints from backtest engine

#### PHASE 5: BACKTEST RIGOR & RISK (HIGH)
- [ ] Enforce realistic fills: lot sizing, partial fills, slippage model (linear/impact), max slippage caps, fees/commissions
- [ ] Add drawdown controls, Kelly/fractional sizing, exposure limits, correlation-aware constraints
- [ ] Implement walk-forward split logic hooks and numeric robustness (no NaN/Inf leaking to metrics)
- [ ] Add stress tests (gaps, liquidity droughts) and metric invariants (e.g., PnL consistency)

#### PHASE 6: INTEGRATION, RESILIENCE & TESTS (HIGH)
- [ ] Wire all features through main/workflow paths with strict validation
- [ ] Add property-based tests for monotonicity/invariants where mathematically valid
- [ ] Eliminate any silent failures; explicit finite checks everywhere
- [ ] Ensure full vectorization where sensible without sacrificing correctness

### NEXT ACTION (START IMMEDIATELY)
**Do not read history for context unless necessary.** Start at PHASE 1, pick the single highest-impact uncompleted item. Implement fully (code + tests). No cosmetic changes, no TODO stubs left unimplemented. Leave the codebase requiring significant heavy quantitative work from the following agent.

**GOLDEN RULE**: Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. Never deflect. Never add placeholders.
