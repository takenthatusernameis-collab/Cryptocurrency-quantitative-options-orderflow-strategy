# HEAVY WORK INITIAL TASK MESSAGE (FOR NEXT AGENTIC SESSION)

Timestamp (UTC): 2026-10-28T07-31-56Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Priority: CRITICAL - HEAVY QUANTITATIVE ENGINEERING
State: CLEAN, 65/65 TESTS PASSING. ALL PREVIOUS BOTTLENECKS REMOVED. NO PLACEHOLDERS ALLOWED.

## Project-name-derived spec
"Cryptocurrency-quantitative-options-orderflow-strategy" — mathematically correct, production-grade crypto options orderflow strategy.

## Bottlenecks Removed This Session
- Removed all tracked `__pycache__/*.pyc` from git index (staged deletions). Repository hygiene enforced.
- Verified 65/65 tests green; no blocked sessions.
- Established single durable handoff as source of truth.

## MANDATORY FOCUS CAMPAIGN (HEAVY QUANTITATIVE WORK ONLY)
### PHASE 1: ADVANCED GAMMA EXPOSURE & DEALER POSITIONING (CRITICAL)
- Net gamma exposure with correct put/call sign convention across strikes/expiries
- Gamma notional by delta bands (ATM/OTM/ITM), OI/volume weighting, numerical stability
- Refined gamma flip interpolation; robust handling of all-same-sign GEX
- Invariants and cross-check tests

### PHASE 2: DEEP ORDERFLOW MICROSTRUCTURE (CRITICAL)
- Cumulative delta with robust trade classification, VWAP-adjusted delta, signed volume
- Multi-horizon orderflow imbalance with decay weighting
- Footprint/orderflow divergence (delta divergence vs price, absorption detection)
- VPIN-style toxicity/proxy or trade intensity with finite-sample guards

### PHASE 3: VOLATILITY SURFACE & SKEW QUANTIFICATION (CRITICAL)
- Robust IV skew term structure (wing skew, butterfly), moneyness/Delta interpolation
- Risk reversal, put-call skew, calendar spread proxies; handle missing IVs
- Gamma-weighted max pain alongside robust OI-based max pain
- Term structure slope metrics integrated with regime detection

### PHASE 4: REGIME-AWARE SIGNAL ENGINEERING (CRITICAL)
- Cross-feature interactions (GEX×orderflow, skew×PCR) with conflict resolution
- Dispersion/entropy-based confidence calibration
- Regime detection with hysteresis/stability, deterministic
- Tight integration with sizing constraints

### PHASE 5: BACKTEST RIGOR & RISK (HIGH)
- Realistic fills, lot sizing, partial fills, slippage (linear/impact), caps, fees/commissions
- Drawdown controls, Kelly/fractional sizing, exposure limits, correlation-aware constraints
- Walk-forward hooks, numeric robustness (no NaN/Inf to metrics)
- Stress tests and metric invariants

### PHASE 6: INTEGRATION, RESILIENCE & TESTS (HIGH)
- Strict validation across all paths; eliminate silent failures
- Property-based tests for valid invariants
- Full vectorization where sensible without sacrificing correctness

## STARTING INSTRUCTION FOR NEXT AGENT
IMMEDIATELY START AT PHASE 1. Pick the HIGHEST-IMPACT uncompleted item in Phase 1. Implement FULLY with tests (code + tests). No cosmetic changes. No placeholders/TODOs. Leave the codebase requiring significant heavy quantitative work for subsequent agents.

GOLDEN RULE: Heavy engineering only. Mathematical correctness mandatory. Numerical stability required. Vectorize where sensible. Never deflect. Never add scaffolding.
