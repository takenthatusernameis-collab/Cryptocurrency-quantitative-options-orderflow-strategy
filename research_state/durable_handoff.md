# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-11-01T06:31:26Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow features/microstructure).
THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION.

Gate status: GREEN (957 passed, 2 skipped, 0 failed) — verified 2026-11-01T06:31:26Z via `python -m pytest tests/ -q`. Working tree clean.

COMPLETED (DO NOT REDO):
- Phases 1-4b: data/loaders, features, time-series/walk-forward/OOS, portfolio walk-forward, options hedging integrated.
- Phase 5: Regime OOS, Portfolio Scaling, Hedging Robustness, Campaign Resume Hardening, Telemetry/Serialization Hardening, Options Pricing/Greeks/IV Adversarial Audit — COMPLETE.
- Phase 6: Full End-to-End Integrated Campaign (Crypto Options + Orderflow) — COMPLETE.
- Phase 7: Production Execution, Real-Time Risk & Orderflow Microstructure Hardening (Crypto Options + Orderflow) — COMPLETE.
- Phase 8: Live Trading Readiness, Paper Trading & Deployment Hardening (Crypto Options + Orderflow) — COMPLETE.
- Phase 9: Production Monitoring, Observability & Continuous Validation (Crypto Options + Orderflow) — COMPLETE.
- Phase 10: Alpha Generation, Volatility Surface Relative Value & Orderflow Signal Fusion (Crypto Options + Orderflow) — COMPLETE.
- Phase 11: Production Live Execution, Continuous Alpha Optimization & Performance Attribution (Crypto Options + Orderflow) — COMPLETE.
- Phase 12: Integrated Campaign / Live Readiness (Crypto Options + Orderflow) — COMPLETE.
- Phase 13: Production Deployment, Continuous Monitoring, Auto-Healing & Model Governance (Crypto Options + Orderflow) — COMPLETE.
- Phase 14: Live Capital Deployment, Multi-Strategy Portfolio Orchestration & Real Exchange Execution (Crypto Options + Orderflow) — COMPLETE (957 passed, 2 skipped).

FILES CHANGED (this session): research_state/durable_handoff.md (handoff refresh: fresh timestamp, gate re-verified, Phase 15 focus campaign re-affirmed).

BOTTLENECKS: NONE. Clean green baseline. No blocked/inefficient sessions. Phase 15 deliverables not yet built — `src/marketmaking/`, `src/orchestration/`, `src/execution/latency_aware_router.py`, `scripts/run_phase15_crossvenue_campaign.py`, `tests/test_phase15_crossvenue.py`, and phase-15 artifacts are missing. `src/arbitrage/` contains only `__init__.py`. These are the next heavy-quant build items, not blockers.

## INITIAL TASK MESSAGE (EXECUTE IMMEDIATELY - NO DEVIATION)
Timestamp: 2026-11-01T06:31:26Z
PRIORITIZE BY REPO NAME: CRYPTO OPTIONS + ORDERFLOW. HEAVY QUANT IMPLEMENTATION ONLY.
ZERO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.
SHIP CODE + TESTS + ARTIFACTS EVERY SESSION. DO NOT STOP AT SCAFFOLDING. BUILD, INTEGRATE, TEST, VALIDATE.

### ACTIVE FOCUS CAMPAIGN: PHASE 15 — CROSS-EXCHANGE ARBITRAGE, DELTA-NEUTRAL MARKET MAKING & LATENCY-OPTIMIZED EXECUTION (CRYPTO OPTIONS + ORDERFLOW)
Goal: Build production-grade cross-exchange arbitrage detection/execution with delta-neutral market making, inventory/risk controls, latency-aware routing, and deterministic backtesting. Default PAPER-ONLY with hard live gates. Emit auditable artifacts. No placeholders.

#### MANDATORY DELIVERABLES (SHIP ALL):
1. **Arbitrage Detector** (`src/arbitrage/arbitrage_detector.py`): cross-venue spread detection (Deribit/OKX/Binance), fee-adjusted net edge, stale-quote filtering, deterministic.
2. **Delta-Neutral MM Engine** (`src/marketmaking/delta_neutral_mm.py`): inventory skew, hedge sizing (options+perp), Greeks-aware, risk caps.
3. **Latency-Aware Router** (`src/execution/latency_aware_router.py`): venue latency models, adaptive routing, cancel/replace, slippage tracking, paper-only.
4. **Arbitrage+MM Orchestrator** (`src/orchestration/crossvenue_orchestrator.py`): unified coordination, PnL tracking, kill-switch integration.
5. **Campaign + CLI** (`src/deployment/phase15_campaign.py`, `scripts/run_phase15_crossvenue_campaign.py`): seed 42, symbols BTC/ETH, venues Deribit/OKX/Binance, artifacts under research_state, fail fast on NaN/Inf, paper-only enforced.
6. **Artifacts**: `PHASE15_CROSSVENUE_REPORT.json/md`, `ARBITRAGE_REPORT.json/md`, `DELTA_NEUTRAL_MM_REPORT.json/md`, `LATENCY_ROUTING_REPORT.json/md`, `CROSSVENUE_ORCHESTRATION_REPORT.json/md`. Include timestamp/git SHA/seed/symbols/venues/paper_only.
7. **Tests** (`tests/test_phase15_crossvenue.py`): >= 80 substantive tests covering edge cases, determinism, schema, finite numerics, paper-only gates. Keep gate GREEN.

#### CONSTRAINTS (NON-NEGOTIABLE):
- No placeholders/TODOs/FIXMEs/HACKs/XXX. Implement fully.
- Keep ALL existing tests passing. Add only (gate >=957 passing minimum).
- Determinism + finite numerics. No NaN/Inf. Validate strictly.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Integrate with existing telemetry/serialization, resilience, monitoring, governance patterns.
- Update THIS FILE before ending session with fresh timestamp, files changed, rationale, `python -m pytest tests/ -q` GREEN.
- No analysis-only. Ship code/tests/artifacts to completion.
