# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-11-01T07:23:56Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution).
THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION.

Gate status: GREEN (957 passed, 2 skipped, 0 failed) — verified 2026-11-01T06:36:33Z via `python -m pytest tests/ -q`. Working tree clean.

COMPLETED (DO NOT REDO):
- Phases 1-14: full pipeline through live-capital deployment/orchestration complete.
- Phase 15 focus: NOT YET IMPLEMENTED (missing modules/tests/artifacts). BUILD HEAVY.

BOTTLENECKS: NONE. No blocked sessions. Only missing implementation for Phase 15 deliverables. Remove nothing — BUILD NOW.

## INITIAL TASK MESSAGE (EXECUTE IMMEDIATELY - NO DEVIATION)
Timestamp: 2026-11-01T06:37:10Z
PRIORITIZE BY REPO NAME: CRYPTO OPTIONS + ORDERFLOW. HEAVY QUANT IMPLEMENTATION ONLY.
ZERO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.
SHIP CODE + TESTS + ARTIFACTS EVERY SESSION. DO NOT STOP AT SCAFFOLDING. BUILD, INTEGRATE, TEST, VALIDATE.
DEFAULT PAPER-ONLY. HARD GATES FOR LIVE PATHS.

### ACTIVE FOCUS CAMPAIGN: PHASE 15 — CROSS-EXCHANGE ARBITRAGE, DELTA-NEUTRAL MARKET MAKING & LATENCY-OPTIMIZED EXECUTION (CRYPTO OPTIONS + ORDERFLOW)
Goal: Build production-grade cross-exchange arbitrage detection/execution with delta-neutral market making, inventory/risk controls, latency-aware routing, and deterministic backtesting. Emit auditable artifacts. No placeholders.

#### MANDATORY DELIVERABLES (SHIP ALL):
1. **Arbitrage Detector** (`src/arbitrage/arbitrage_detector.py`): cross-venue spread detection (Deribit/OKX/Binance), fee-adjusted net edge, stale-quote filtering, volatility/spread sanity, deterministic.
2. **Delta-Neutral MM Engine** (`src/marketmaking/delta_neutral_mm.py`): inventory skew, hedge sizing (options+perp), Greeks-aware delta neutrality, drawdown/inventory/risk caps, finite numerics.
3. **Latency-Aware Router** (`src/execution/latency_aware_router.py`): venue latency models, adaptive routing, cancel/replace, slippage tracking, paper-only hard gates.
4. **Arbitrage+MM Orchestrator** (`src/orchestration/crossvenue_orchestrator.py`): unified coordination, PnL tracking, kill-switch integration, state serialization.
5. **Campaign + CLI** (`src/deployment/phase15_campaign.py`, `scripts/run_phase15_crossvenue_campaign.py`): seed 42, symbols BTC/ETH, venues Deribit/OKX/Binance, artifacts under research_state, fail fast on NaN/Inf, paper-only enforced. Update `src/arbitrage/__init__.py` to export new APIs.
6. **Artifacts**: `PHASE15_CROSSVENUE_REPORT.json/md`, `ARBITRAGE_REPORT.json/md`, `DELTA_NEUTRAL_MM_REPORT.json/md`, `LATENCY_ROUTING_REPORT.json/md`, `CROSSVENUE_ORCHESTRATION_REPORT.json/md`. Include timestamp/git SHA/seed/symbols/venues/paper_only/status.
7. **Tests** (`tests/test_phase15_crossvenue.py`): >= 80 substantive tests covering edge cases, determinism, schema, finite numerics, fee-adjustment, stale-quote filtering, delta-neutral invariants, latency routing, paper-only gates, kill-switch. Keep gate GREEN (>=957 passing).

#### CONSTRAINTS (NON-NEGOTIABLE):
- No placeholders/TODOs/FIXMEs/HACKs/XXX. Implement fully.
- Keep ALL existing tests passing. Only add tests/modules.
- Determinism + finite numerics. No NaN/Inf. Validate strictly.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Integrate with existing telemetry/serialization, resilience, monitoring, governance patterns.
- Before ending: update THIS FILE with fresh UTC timestamp, files changed, rationale, and run `python -m pytest tests/ -q` (must be GREEN).
- Ship code+tests+artifacts to completion. NO analysis-only.

**ACTION NOW:** Create missing dirs/files, implement fully, add tests, run campaign, emit artifacts, verify gate GREEN, update this handoff.
