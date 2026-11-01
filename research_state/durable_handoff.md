# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-11-01T01:34:01Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE BY REPO NAME -> crypto options pricing/Greeks/IV + orderflow features/microstructure). THIS IS THE ONLY SOURCE OF TRUTH FOR NEXT AGENT SESSION.

Gate status: GREEN (633 passed, 2 skipped, 0 failed) — verified 2026-11-01T01:34:01Z via `python -m pytest tests/ -q`. Working tree clean.

COMPLETED (DO NOT REDO):
- Phases 1-4b: data/loaders, features, time-series/walk-forward/OOS, portfolio walk-forward, options hedging integrated.
- Phase 5: Regime OOS, Portfolio Scaling, Hedging Robustness, Campaign Resume Hardening, Telemetry/Serialization Hardening, Options Pricing/Greeks/IV Adversarial Audit — COMPLETE.
- Phase 6: Full End-to-End Integrated Campaign (Crypto Options + Orderflow) — COMPLETE.
- Phase 7: Production Execution, Real-Time Risk & Orderflow Microstructure Hardening (Crypto Options + Orderflow) — COMPLETE.
- Phase 8: Live Trading Readiness, Paper Trading & Deployment Hardening (Crypto Options + Orderflow) — COMPLETE.
- Phase 9: Production Monitoring, Observability & Continuous Validation (Crypto Options + Orderflow) — COMPLETE.

BOTTLENECKS: NONE IDENTIFIED. Clean green baseline. All prior bottlenecks eliminated. No blockers. Keep gate GREEN at all times. Do not create analysis-only sessions.

## INITIAL TASK MESSAGE (FOR NEXT AGENTIC WORK SESSION - EXECUTE IMMEDIATELY, NO DEVIATION)
Timestamp: 2026-11-01T01:34:01Z
BY REPO NAME - CRYPTO OPTIONS + ORDERFLOW IS THE DOMAIN. HEAVY QUANT IMPLEMENTATION ONLY. NO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY. SHIP CODE/TESTS/ARTIFACTS EVERY SESSION.
PRIORITIZE BY REPO NAME. LEAVE MOST RELEVANT INFERRED TIMESTAMPED CLEAR INITIAL TASK. REMOVE BOTTLENECKS. BUILD NEXT FOCUS CAMPAIGN SO HEAVY WORK IS UNAVOIDABLE.

## ACTIVE FOCUS CAMPAIGN: PHASE 10 — ALPHA GENERATION, VOLATILITY SURFACE RELATIVE VALUE & ORDERFLOW SIGNAL FUSION (CRYPTO OPTIONS + ORDERFLOW)
Domain priority (from repo name): crypto options pricing/Greeks/IV + orderflow features/microstructure. Build a heavy, production-grade alpha layer that fuses options volatility-surface signals with orderflow microstructure into deterministic, risk-aware trade intents, with walk-forward OOS validation and artifact emission. Keep Phase 9 infra intact. Gate must stay GREEN (>=633 passed). Ship code + tests + artifacts. Update THIS FILE before ending with fresh timestamp, files changed, rationale, verification results.

### Scope (heavy, non-avoidable):
1. Volatility surface relative-value engine: IV skew/term-structure dislocation detector, vega-weighted residual scoring, deterministic no-arbitrage checks (butterfly/calendar), output ranked opportunity list.
2. Orderflow alpha features: cumulative delta divergence, absorption/sweep detection, VPIN-lite imbalance, liquidity vacuum detector, deterministic feature pipeline with schema validation.
3. Signal fusion + gating: combine vol-surface and orderflow alphas with regime-aware weights, confidence scoring, hard risk gates (max vega, delta band, liquidity min), emit trade intents (symbol, side, size, expiry, strike band, limit price).
4. Position sizing & portfolio construction: Kelly-lite fractional sizing with drawdown penalty, correlation-aware de-dup, max exposure caps, deterministic.
5. Walk-forward OOS evaluation: anchored + rolling windows, purge/embargo, regime-stratified metrics (Sharpe, Sortino, max DD, hit rate, turnover), bootstrap significance, deterministic.
6. Artifacts: PHASE10_ALPHA_REPORT, VOL_SURFACE_RV_REPORT, ORDERFLOW_ALPHA_REPORT, SIGNAL_FUSION_REPORT, WALKFORWARD_OOS_REPORT, SIZING_REPORT (strict allow_nan=False, timestamped) under research_state/.
7. Tests: >=80 substantive tests in tests/test_phase10_alpha_vol_orderflow.py covering invariants, determinism (byte-identical rerun), edge cases, no-arbitrage, risk gates, sizing bounds, OOS metrics finite, schema, artifact validity.
8. CLI: scripts/run_phase10_alpha_campaign.py emitting artifacts with seed 42, symbols BTC/ETH.

### Constraints:
- No placeholders/TODOs/FIXMEs/HACKs/XXX. No analysis-only sessions.
- Keep all existing tests passing; add only.
- Determinism: same inputs -> byte-identical outputs/artifacts.
- Correctness: finite numerics, no NaN/Inf in artifacts (allow_nan=False).
- Update this handoff on completion with fresh timestamp + verification.