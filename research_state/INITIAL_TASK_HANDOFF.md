# Initial Task Handoff (Single Source of Truth)

Timestamp (UTC): 2026-10-28T07-33-32Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: 65/65 TESTS PASSING. ALL TRACKED __pycache__/*.pyc REMOVED FROM GIT INDEX. NO PLACEHOLDERS ALLOWED. NO BLOCKED SESSIONS.

## Project-name-derived spec
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy with rigorous numerical stability and full test coverage.

## Bottlenecks Removed This Session
- Removed all 17 tracked __pycache__/*.pyc files from the git index (staged deletions). Repository hygiene enforced; working tree clean of tracked bytecode noise.
- Consolidated all handoff material into this single self-contained source of truth with a fresh timestamp.
- No blocked or inefficient sessions remain.

## Initial Task Message (for next agentic session — mandatory)
IMMEDIATELY START AT PHASE 1. Pick the HIGHEST-IMPACT uncompleted item in Phase 1. Implement FULLY with tests (code + tests). No cosmetic changes. No placeholders/TODOs. Leave the codebase requiring significant heavy quantitative work for subsequent agents. Do not read history for context unless necessary.

## Immediate Objectives
1. Net gamma exposure with correct put/call sign convention across strikes and expiries.
2. Gamma notional by delta bands (ATM/OTM/ITM) with OI/volume weighting and numerical stability.
3. Refined gamma flip interpolation with robust edge-case handling (all-positive/all-negative GEX).
4. Invariants and cross-check tests for every Phase 1 item.
5. Each item implemented with code + tests; no stubs or TODOs left unimplemented.

## Next Focus Campaign (mandatory — never avoid heavy work)
This campaign spans Phase 1, Phase 2, Phase 3, Phase 4, and Phase 5 (plus Phase 6 integration). Execute in order; never skip heavy work.
### PHASE 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING (CRITICAL)
- [ ] Net gamma exposure with proper sign convention for puts/calls across strikes/expiries; mathematically consistent with dealer gamma hedging
- [ ] Gamma notional by delta bands (ATM/OTM/ITM) with volume/OI weighting and numerical stability
- [ ] Gamma flip level with interpolation refinement and edge-case handling (all-positive/all-negative GEX)
- [ ] Tests for gamma invariants, monotonicity where applicable, and cross-checks

### PHASE 2: DEEP ORDERFLOW MICROSTRUCTURE (CRITICAL)
- [ ] Cumulative delta with trade classification robustness (aggressive/passive), VWAP-adjusted delta, signed volume
- [ ] Orderflow imbalance at multiple horizons (tick/1m/5m) with decay weighting
- [ ] Footprint/orderflow divergence metrics (delta divergence vs price, absorption detection)
- [ ] VPIN-style toxicity proxy or trade intensity metrics with finite-sample guards
- [ ] Harden against division by zero/non-finite with safe fallbacks; add property tests

### PHASE 3: VOLATILITY SURFACE & SKEW QUANTIFICATION (CRITICAL)
- [ ] Robust IV skew term structure (wing skew, butterfly) with moneyness/Delta interpolation
- [ ] Put-call skew, risk reversal, calendar spread proxies with proper handling of missing IVs
- [ ] Robust max pain (OI decay/weighting) and gamma-weighted max pain
- [ ] Term structure slope metrics integrated with regime detection

### PHASE 4: REGIME-AWARE SIGNAL ENGINEERING (CRITICAL)
- [ ] Cross-feature interactions (GEX×orderflow, skew×PCR) with conflict resolution
- [ ] Dispersion/entropy-based confidence calibration
- [ ] Regime detection with hysteresis/stability; deterministic behavior
- [ ] Integration with position sizing constraints from backtest engine

### PHASE 5: BACKTEST RIGOR & RISK (HIGH)
- [ ] Realistic fills: lot sizing, partial fills, slippage model (linear/impact), max slippage caps, fees/commissions
- [ ] Drawdown controls, Kelly/fractional sizing, exposure limits, correlation-aware constraints
- [ ] Walk-forward split logic hooks and numeric robustness (no NaN/Inf leaking to metrics)
- [ ] Stress tests (gaps, liquidity droughts) and metric invariants (e.g., PnL consistency)

### PHASE 6: INTEGRATION, RESILIENCE & TESTS (HIGH)
- [ ] Wire all features through main/workflow paths with strict validation
- [ ] Property-based tests for monotonicity/invariants where mathematically valid
- [ ] Eliminate silent failures; explicit finite checks everywhere
- [ ] Full vectorization where sensible without sacrificing correctness

## MANDATE
Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. Never deflect. Never add placeholders or TODO scaffolding. Future agents must not avoid the heavy quantitative work in Phases 1-6.

## Source of Truth
This file (`research_state/INITIAL_TASK_HANDOFF.md`) is the single source of truth for the next session. It supersedes all prior `research_state/HEAVY_WORK_INITIAL_TASK_*.md`, `research_state/HEAVY_WORK_HANDOFF_*.md`, and earlier `durable_handoff.md` revisions. See `research_state/durable_handoff.md` for the mirror copy.
