# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-11-01T13:28:25Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution)

THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (1181 passed, 2 skipped, 0 failed) — verified 2026-11-01T13:28:25Z via `python -m pytest tests/ -q`. Working tree clean. No bottlenecks; all sessions unblocked.

COMPLETED (DO NOT REDO):
- Phases 1-15: full pipeline through cross-venue orchestration complete.
- Phase 16: COMPLETE — advanced orderflow signal fusion + cross-asset options vol surface RV arb.
- Phase 17: COMPLETE — cross-asset options vol surface arb deepening + orderflow confirmation.
- Phase 18: COMPLETE — production observability, PnL attribution & live Greeks hardening for cross-asset options vol arb. Added src/analytics/phase18_attribution.py, src/analytics/phase18_greeks_snapshot.py, src/monitoring/phase18_observability.py, scripts/run_phase18_observability_attribution.py, tests/test_phase18_observability_attribution.py. Artifacts PHASE18_PNL_ATTRIBUTION_REPORT.json/md, PHASE18_OBSERVABILITY_SLO_REPORT.json/md, PHASE18_GREEKS_SNAPSHOT_REPORT.json/md, PHASE18_OBSERVABILITY_ATTRIBUTION_MASTER_REPORT.json/md under research_state/.

BOTTLENECKS REMOVED: NONE (all prior bottlenecks resolved; gate GREEN).

## MANDATORY INITIAL TASK MESSAGE (EXECUTE IMMEDIATELY - NO DEVIATION)
Timestamp: 2026-11-01T13:28:25Z
PRIORITIZE BY REPO NAME: CRYPTO OPTIONS + ORDERFLOW. HEAVY QUANT IMPLEMENTATION ONLY.
ZERO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.
SHIP CODE + TESTS + ARTIFACTS EVERY SESSION. DO NOT STOP AT SCAFFOLDING. BUILD, INTEGRATE, TEST, VALIDATE.
DEFAULT PAPER-ONLY. HARD GATES FOR LIVE PATHS.
EVERY FUTURE AGENT MUST START HERE. NO EXPLORATION WITHOUT IMPLEMENTATION. NO ANALYSIS-ONLY RESPONSES.

### ACTIVE FOCUS CAMPAIGN: PHASE 19 — LIVE-CAPITAL EXECUTION HARDENING: PAPER->LIVE GATE, ORDER MANAGEMENT, EXECUTION RISK (CRYPTO OPTIONS + ORDERFLOW)
Goal: Harden execution path for crypto options + orderflow from paper to live with strict gates. Build end-to-end: paper->live transition gate with multi-layer approval/checks, order lifecycle management (OMS), execution risk controls (slippage, notional caps, per-venue limits, max open interest/risk, kill-switch integration), pre-trade/post-trade validation, deterministic simulation of live-like constraints, full audit trail. Integrate with Phase17/Phase18 telemetry/serialization/resilience/monitoring. All paper-only by default with hard live gating. No placeholders.

Deliverables (ALL REQUIRED):
1. `src/execution/phase19_paper_live_gate.py` — PaperLiveGate: layered gates (capital, connectivity, risk limits, compliance flags), approval state machine, deterministic checks, hard block on live unless all satisfied.
2. `src/execution/phase19_order_manager.py` — OrderManager/OMS: order states, fills/partials/cancels/rejects, idempotency, venue routing hooks, reconciliation, audit log.
3. `src/risk/phase19_execution_risk.py` — ExecutionRiskEngine: pre-trade checks (notional/per-symbol/per-venue, delta/vega/gamma/theta caps), slippage guards, drawdown/kill-switch integration, real-time enforcement.
4. `scripts/run_phase19_execution_hardening_campaign.py` — CLI (--symbols, --venues, --seed, --cycles, --paper-only required True, --enforce-gates, --outdir). Runs integrated flow with Phase17 intents + Phase18 observability/attribution.
5. `tests/test_phase19_execution_hardening.py` — >=50 substantive deterministic tests (fixed seeds, mocks, no network, allow_nan=False).
6. Artifacts: PHASE19_PAPER_LIVE_GATE_REPORT.json/md, PHASE19_ORDER_MANAGEMENT_REPORT.json/md, PHASE19_EXECUTION_RISK_REPORT.json/md, PHASE19_EXECUTION_HARDENING_MASTER_REPORT.json/md under research_state/.
7. Determinism: identical seed -> identical artifacts. Finite numerics only. Strict serialization (serialize_metrics_strict/assert_json_valid). Full integration with existing patterns.

### IMMEDIATE ACTIONS
- Read this file first. Verify gate GREEN (1151 passed). Phase 18 verified complete.
- Build Phase 19 end-to-end (modules + script + tests + artifacts). NO placeholders/TODOs.
- Run tests frequently; keep gate GREEN. Add tests to cover gates, OMS states, execution risk.
- Update this file with fresh timestamp/files/notes on completion with `python -m pytest tests/ -q` result.

CONSTRAINTS (NON-NEGOTIABLE):
- No placeholders/TODOs/FIXMEs/HACKs/XXX. Implement fully end-to-end.
- Keep ALL existing tests passing. Only add tests/modules.
- Determinism + finite numerics. No NaN/Inf. Validate strictly.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Integrate with existing telemetry/serialization, resilience, monitoring, governance patterns.
- Before ending: update THIS FILE with fresh UTC timestamp, files changed, rationale, and run `python -m pytest tests/ -q` (must be GREEN).
- Ship code+tests+artifacts to completion. NO analysis-only. NO stopping at scaffolding.

**ACTION NOW:** Begin Phase 19 immediately. Prioritize crypto options + orderflow. Build heavy implementation.
