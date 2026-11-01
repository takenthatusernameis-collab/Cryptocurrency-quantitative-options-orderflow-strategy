# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-11-01T01:36:56Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow features/microstructure).
THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION.

Gate status: GREEN (633 passed, 2 skipped, 0 failed) — verified 2026-11-01T01:34:30Z via `python -m pytest tests/ -q`. Working tree clean.

COMPLETED (DO NOT REDO):
- Phases 1-4b: data/loaders, features, time-series/walk-forward/OOS, portfolio walk-forward, options hedging integrated.
- Phase 5: Regime OOS, Portfolio Scaling, Hedging Robustness, Campaign Resume Hardening, Telemetry/Serialization Hardening, Options Pricing/Greeks/IV Adversarial Audit — COMPLETE.
- Phase 6: Full End-to-End Integrated Campaign (Crypto Options + Orderflow) — COMPLETE.
- Phase 7: Production Execution, Real-Time Risk & Orderflow Microstructure Hardening (Crypto Options + Orderflow) — COMPLETE.
- Phase 8: Live Trading Readiness, Paper Trading & Deployment Hardening (Crypto Options + Orderflow) — COMPLETE.
- Phase 9: Production Monitoring, Observability & Continuous Validation (Crypto Options + Orderflow) — COMPLETE.
- Phase 10: Alpha Generation, Volatility Surface Relative Value & Orderflow Signal Fusion (Crypto Options + Orderflow) — SPEC READY (IMPLEMENT NOW).

BOTTLENECKS: NONE. Clean green baseline. All historical bottlenecks eliminated. No blockers. Do NOT create analysis-only or documentation-only sessions. Keep gate GREEN at all times.

## INITIAL TASK MESSAGE (EXECUTE IMMEDIATELY - NO DEVIATION)
Timestamp: 2026-11-01T01:36:56Z
PRIORITIZE BY REPO NAME: CRYPTO OPTIONS + ORDERFLOW. HEAVY QUANT IMPLEMENTATION ONLY.
ZERO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.
SHIP CODE + TESTS + ARTIFACTS EVERY SESSION. DO NOT STOP AT SCAFFOLDING. BUILD, INTEGRATE, TEST, VALIDATE.

## ACTIVE FOCUS CAMPAIGN: PHASE 10 — ALPHA GENERATION, VOLATILITY SURFACE RELATIVE VALUE & ORDERFLOW SIGNAL FUSION (CRYPTO OPTIONS + ORDERFLOW)
Goal: Fuse crypto options volatility-surface relative value with orderflow microstructure into deterministic, risk-aware trade intents. Validate with rigorous walk-forward OOS. Emit auditable artifacts. Must be unskippable heavy work.

### MANDATORY DELIVERABLES (SHIP ALL):
1. **Vol Surface RV Engine** (`src/alpha/vol_surface_rv.py`): IV skew/term-structure dislocation detector, vega-weighted residual scoring vs fitted surface (SABR/param or robust spline), butterfly/calendar no-arbitrage checks, liquidity-aware filters, ranked opportunity list with deterministic sorting.
2. **Orderflow Alpha Features** (`src/alpha/orderflow_alpha.py`): cumulative delta divergence, absorption/sweep detection, VPIN-lite imbalance, liquidity vacuum detector, footprint-aware rollups, strict schema validation, deterministic feature pipeline.
3. **Signal Fusion + Gating** (`src/alpha/signal_fusion.py`): regime-aware weighting (tie to existing regime), confidence scoring, hard risk gates (max |delta|, max |vega|, gamma band, liquidity min, DTE range), emit TradeIntent objects (symbol, side, qty/size, expiry, strike band, order type/limit logic, rationale hash).
4. **Sizing & Portfolio Construction** (`src/alpha/position_sizing.py`): Kelly-lite fractional with drawdown penalty, correlation-aware de-duplication, per-symbol/expiry/vega caps, concentration limits, deterministic rounding.
5. **Walk-Forward OOS** (`src/alpha/walkforward_oos.py`): anchored + rolling, purge/embargo, regime-stratified metrics (Sharpe, Sortino, Calmar, max DD, hit rate, turnover, win/loss, PnL by regime), bootstrap significance (block/bootstrap), deterministic seeds.
6. **Campaign Orchestrator + CLI** (`src/alpha/phase10_campaign.py`, `scripts/run_phase10_alpha_campaign.py`): end-to-end run with seed 42, symbols BTC/ETH, emit all artifacts, validate numerics, fail fast on NaN/Inf.
7. **Artifacts** (under `research_state/`, strict `allow_nan=False`): `PHASE10_ALPHA_REPORT.json/md`, `VOL_SURFACE_RV_REPORT.json/md`, `ORDERFLOW_ALPHA_REPORT.json/md`, `SIGNAL_FUSION_REPORT.json/md`, `WALKFORWARD_OOS_REPORT.json/md`, `SIZING_REPORT.json/md`. Every artifact must include timestamp, git SHA (if available), seed, symbols, counts.
8. **Tests** (`tests/test_phase10_alpha_vol_orderflow.py`): >= 80 substantive tests covering invariants, determinism (byte-identical rerun), edge cases, no-arbitrage, risk gates, sizing bounds, OOS finite/valid, schema, artifact validity. All must pass.

### CONSTRAINTS (NON-NEGOTIABLE):
- No placeholders/TODOs/FIXMEs/HACKs/XXX. Implement fully.
- Keep ALL existing tests passing. Add only (gate >=633 passing minimum).
- Determinism: same inputs + seed -> byte-identical artifacts and results.
- Correctness: finite numerics. No NaN/Inf in any artifact (`allow_nan=False`). Validate.
- Use existing project patterns/configs. Integrate cleanly with Phase 9 monitoring/observability where relevant.
- Update THIS FILE before ending the session with: fresh timestamp (UTC), files changed (code/tests/scripts/artifacts), rationale, verification results (`python -m pytest tests/ -q` must be GREEN).
- No analysis-only sessions. Every turn must advance code/tests/artifacts.
