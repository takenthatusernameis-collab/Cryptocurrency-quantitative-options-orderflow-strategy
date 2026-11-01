# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-11-01T13:30:00Z
Updated (UTC): 2026-11-01T13:31:30Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution)

THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (1211 passed, 2 skipped, 0 failed) — verified 2026-11-01T13:31:30Z via `python -m pytest tests/ -q`. Working tree clean. No bottlenecks; all sessions unblocked.

COMPLETED (DO NOT REDO):
- Phases 1-15: full pipeline through cross-venue orchestration complete.
- Phase 16: COMPLETE — advanced orderflow signal fusion + cross-asset options vol surface RV arb.
- Phase 17: COMPLETE — cross-asset options vol surface arb deepening + orderflow confirmation.
- Phase 18: COMPLETE — production observability, PnL attribution & live Greeks hardening.
- Phase 19: COMPLETE — live-capital execution hardening (paper->live gate, OMS, execution risk). Modules + script + tests + artifacts under research_state/ (PHASE19_*). Gate GREEN.
- Phase 20: COMPLETE — live-capital deployment & continuous validation (capital allocation, multi-strategy orchestration, live readiness gate, post-trade recon, drift detection, auto-recovery). Modules: src/capital/phase20_capital_allocator.py, src/orchestration/phase20_strategy_orchestrator.py, src/deployment/phase20_live_readiness_gate.py, src/reconciliation/phase20_post_trade_recon.py, src/monitoring/phase20_drift_detector.py, src/resilience/phase20_auto_recovery.py. Script: scripts/run_phase20_live_capital_campaign.py. Tests: tests/test_phase20_live_capital.py (30 passed). Artifacts: PHASE20_* under research_state/ (all 14). Gate GREEN.

BOTTLENECKS REMOVED: NONE (all prior bottlenecks resolved; gate GREEN).

## MANDATORY INITIAL TASK MESSAGE (EXECUTE IMMEDIATELY - NO DEVIATION)
Timestamp: 2026-11-01T13:31:30Z
PRIORITIZE BY REPO NAME: CRYPTO OPTIONS + ORDERFLOW. HEAVY QUANT IMPLEMENTATION ONLY.
ZERO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.
SHIP CODE + TESTS + ARTIFACTS EVERY SESSION. DO NOT STOP AT SCAFFOLDING. BUILD, INTEGRATE, TEST, VALIDATE.
DEFAULT PAPER-ONLY. HARD GATES FOR LIVE PATHS.
EVERY FUTURE AGENT MUST START HERE. NO EXPLORATION WITHOUT IMPLEMENTATION. NO ANALYSIS-ONLY RESPONSES.

### ACTIVE FOCUS CAMPAIGN: PHASE 21 — REAL-TIME RISK AGGREGATION, STRESS TESTING & PRE-TRADE VALIDATION (CRYPTO OPTIONS + ORDERFLOW)
Goal: Harden real-time risk aggregation across strategies/venues/symbols with deterministic stress testing and pre-trade validation. Build end-to-end integration on top of Phase 17-20: aggregate Greeks/VEGA/GAMMA/DELTA exposure, scenario shocks (spot/IV/liquidity), pre-trade risk checks with hard blocks, stress battery with deterministic seeds, risk attribution, and continuous risk monitoring. All paper-only by default with hard gating. No placeholders.

Deliverables (ALL REQUIRED):
1. `src/risk/phase21_risk_aggregator.py` — RiskAggregator: cross-strategy/venue/symbol aggregation, exposure limits, concentration checks, deterministic.
2. `src/risk/phase21_stress_tester.py` — StressTester: scenario shocks (spot ±5/10%, IV ±5/10 pts, liquidity shocks), PnL impact, breach detection, deterministic.
3. `src/risk/phase21_pre_trade_validator.py` — PreTradeValidator: order/intent validation against aggregated risk, hard blocks, override audit, deterministic.
4. `src/monitoring/phase21_risk_monitor.py` — RiskMonitor: real-time risk metrics, limit utilization, alerts, drift integration hooks.
5. `src/analytics/phase21_risk_attribution.py` — RiskAttribution: factor decomposition, venue/strategy attribution, deterministic.
6. `scripts/run_phase21_risk_stress_campaign.py` — CLI (--symbols, --venues, --strategies, --seed, --cycles, --paper-only required True, --enforce-gates, --outdir). Integrates Phase 17-20.
7. `tests/test_phase21_risk_stress.py` — >=60 substantive deterministic tests (fixed seeds, mocks, no network).
8. Artifacts: PHASE21_RISK_AGGREGATION_REPORT.json/md, PHASE21_STRESS_TESTING_REPORT.json/md, PHASE21_PRE_TRADE_VALIDATION_REPORT.json/md, PHASE21_RISK_MONITORING_REPORT.json/md, PHASE21_RISK_ATTRIBUTION_REPORT.json/md, PHASE21_RISK_STRESS_MASTER_REPORT.json/md under research_state/.
9. Determinism: identical seed -> identical artifacts. Finite numerics only. Strict serialization. Full integration with existing patterns.

### IMMEDIATE ACTIONS
- Read this file first. Verify gate GREEN (1211 passed). Phases 19-20 verified complete.
- Build Phase 21 end-to-end (modules + script + tests + artifacts). NO placeholders/TODOs.
- Run tests frequently; keep gate GREEN. Add tests for aggregation, stress scenarios, pre-trade blocks, monitoring, attribution.
- Update this file with fresh timestamp/files/notes on completion with `python -m pytest tests/ -q` result.

CONSTRAINTS (NON-NEGOTIABLE):
- No placeholders/TODOs/FIXMEs/HACKs/XXX. Implement fully end-to-end.
- Keep ALL existing tests passing. Only add tests/modules.
- Determinism + finite numerics. No NaN/Inf. Validate strictly.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Integrate with existing telemetry/serialization, resilience, monitoring, governance patterns.
- Before ending: update THIS FILE with fresh UTC timestamp, files changed, rationale, and run `python -m pytest tests/ -q` (must be GREEN).
- Ship code+tests+artifacts to completion. NO analysis-only. NO stopping at scaffolding.

**ACTION NOW:** Begin Phase 21 immediately. Prioritize crypto options + orderflow. Build heavy implementation.
