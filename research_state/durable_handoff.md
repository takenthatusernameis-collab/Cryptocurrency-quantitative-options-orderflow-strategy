# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-11-01T17:15:02Z
Updated (UTC): 2026-11-01T17:15:02Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution)

THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (1353 passed, 2 skipped, 0 failed) — verified 2026-11-01T17:15:02Z via `python -m pytest tests/ -q`. Working tree clean. NO BOTTLENECKS. ALL SESSIONS UNBLOCKED.

COMPLETED (DO NOT REDO):
- Phases 1-23: All complete including cross-venue orchestration, advanced orderflow fusion, production observability/PnL/Greeks, live-capital hardening, real-time risk/stress/pre-trade, advanced execution optimization/smart routing/fill prediction/TCA, Phase 23 adaptive orderflow alpha + regime-aware signal fusion + alpha decay monitoring. Gate GREEN.
- PHASE 24 COMPLETE (2026-11-01T17:15:02Z): Production live paper trading loop, cross-venue orderflow execution & continuous auto-healing observability loop. Added `src/execution/phase24_live_trading_loop.py`, `src/execution/phase24_cross_venue_router.py`, `src/resilience/phase24_auto_healer_loop.py`, `src/telemetry/phase24_observability_loop.py`, `scripts/run_phase24_production_campaign.py`, `tests/test_phase24_production_loop.py` (31 passed). Artifacts written to `research_state/`: PHASE24_LIVE_TRADING_REPORT.*, PHASE24_CROSS_VENUE_REPORT.*, PHASE24_AUTO_HEALER_REPORT.*, PHASE24_OBSERVABILITY_REPORT.*, PHASE24_PRODUCTION_MASTER_REPORT.*. All paper-only, gated, deterministic, finite-numerics enforced. Integration with Phase 17-23 verified. No placeholders/TODOs.

BOTTLENECKS REMOVED: NONE. Any inefficiencies must be removed by direct implementation.

## MANDATORY INITIAL TASK MESSAGE — PHASE 25 (EXECUTE IMMEDIATELY - NO DEVIATION)
Timestamp (UTC): 2026-11-01T17:15:02Z
PRIORITIZE BY REPO NAME: CRYPTO OPTIONS + ORDERFLOW. HEAVY QUANT IMPLEMENTATION ONLY.
ZERO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.
SHIP CODE + TESTS + ARTIFACTS EVERY SESSION. DO NOT STOP AT SCAFFOLDING. BUILD, INTEGRATE, TEST, VALIDATE.
DEFAULT PAPER-ONLY. HARD GATES FOR LIVE PATHS.

### ACTIVE FOCUS CAMPAIGN: PHASE 25 — CRYPTO OPTIONS VOL SURFACE CONSTRUCTION, ORDERFLOW-DRIVEN IV SKEW/RISK REVERSAL & DELTA-HEDGING OPTIMIZER (CRYPTO OPTIONS + ORDERFLOW)
Goal: Build production-grade crypto options vol surface construction integrating orderflow microstructure signals (bid/ask imbalance, toxicity, tape) with cross-venue IV data, term structure & skew/RR calibration, SABR/local-vol style calibration with orderflow adjustments, and a delta-hedging optimizer for live paper loop. Integrate with Phase 17-24. All paper-only by default with hard gating. No placeholders.

### DELIVERABLES (ALL REQUIRED):
1. `src/options/phase25_vol_surface.py` — VolSurface: cross-venue IV aggregation, orderflow-adjusted skew/RR, term structure, SABR/local-vol calibration, deterministic.
2. `src/options/phase25_iv_skew_orderflow.py` — IVSkewOrderflow: orderflow-driven IV skew/RR adjustments, liquidity-weighted, deterministic.
3. `src/hedging/phase25_delta_hedge_optimizer.py` — DeltaHedgeOptimizer: delta-hedging optimizer (cost-aware, liquidity-aware, cross-venue), circuit-breakers, deterministic.
4. `src/execution/phase25_options_paper_loop.py` — OptionsPaperLoop: integrates vol surface + skew/orderflow + hedging optimizer into Phase 24 paper loop, deterministic.
5. `scripts/run_phase25_options_vol_hedge_campaign.py` — CLI (--symbols, --venues, --underlyings BTC/ETH/SOL/XRP, --expiries, --modes paper/live gated, --cycles, --seed, --enforce-gates, --outdir). Integrates Phase 17-24.
6. `tests/test_phase25_options_vol_hedge.py` — >=70 substantive deterministic tests (fixed seeds, mocks, no network).
7. Artifacts: PHASE25_VOL_SURFACE_REPORT.json/md, PHASE25_IV_SKEW_ORDERFLOW_REPORT.json/md, PHASE25_DELTA_HEDGE_OPTIMIZER_REPORT.json/md, PHASE25_OPTIONS_PAPER_LOOP_REPORT.json/md, PHASE25_OPTIONS_VOL_HEDGE_MASTER_REPORT.json/md under research_state/.

### IMMEDIATE ACTIONS
- Read this file first. Verify gate GREEN. Phase 24 verified complete (modules+script+tests+artifacts exist). Complete Phase 25.
- Build Phase 25 end-to-end (all modules+script+>=70 tests+artifacts). NO placeholders/TODOs.
- Run tests frequently; keep gate GREEN.
- Update this file with fresh timestamp/files/notes on completion with `python -m pytest tests/ -q` result.

### CONSTRAINTS (NON-NEGOTIABLE):
- No placeholders/TODOs/FIXMEs/HACKs/XXX. Implement fully end-to-end.
- Keep ALL existing tests passing. Only add tests/modules.
- Determinism + finite numerics. No NaN/Inf. Validate strictly.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Integrate with Phase 17-24 (live trading loop, cross-venue router, auto-healer, observability, orderflow alpha/fusion/decay).
- Before ending: update THIS FILE with fresh UTC timestamp, files changed, rationale, and run `python -m pytest tests/ -q` (must be GREEN).
- Ship code+tests+artifacts to completion. NO analysis-only. NO stopping at scaffolding.

**ACTION NOW:** Begin Phase 25 immediately. Prioritize crypto options + orderflow. Build heavy implementation. Do not deviate.
