# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
Timestamp (UTC): 2026-11-01T13:30:00Z
Project: Cryptocurrency-quantitative-options-orderflow-strategy
Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution)

THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (1181 passed, 2 skipped, 0 failed) — verified 2026-11-01T13:30:00Z via `python -m pytest tests/ -q`. Working tree clean. No bottlenecks; all sessions unblocked.

COMPLETED (DO NOT REDO):
- Phases 1-15: full pipeline through cross-venue orchestration complete.
- Phase 16: COMPLETE — advanced orderflow signal fusion + cross-asset options vol surface RV arb.
- Phase 17: COMPLETE — cross-asset options vol surface arb deepening + orderflow confirmation.
- Phase 18: COMPLETE — production observability, PnL attribution & live Greeks hardening.
- Phase 19: COMPLETE — live-capital execution hardening (paper->live gate, OMS, execution risk). Modules + script + tests + artifacts under research_state/ (PHASE19_*). Gate GREEN.

BOTTLENECKS REMOVED: NONE (all prior bottlenecks resolved; gate GREEN).

## MANDATORY INITIAL TASK MESSAGE (EXECUTE IMMEDIATELY - NO DEVIATION)
Timestamp: 2026-11-01T13:30:00Z
PRIORITIZE BY REPO NAME: CRYPTO OPTIONS + ORDERFLOW. HEAVY QUANT IMPLEMENTATION ONLY.
ZERO PLACEHOLDERS, TODOs, FIXMEs, HACKs, XXX. PRODUCTION-GRADE. CORRECTNESS + DETERMINISM MANDATORY.
SHIP CODE + TESTS + ARTIFACTS EVERY SESSION. DO NOT STOP AT SCAFFOLDING. BUILD, INTEGRATE, TEST, VALIDATE.
DEFAULT PAPER-ONLY. HARD GATES FOR LIVE PATHS.
EVERY FUTURE AGENT MUST START HERE. NO EXPLORATION WITHOUT IMPLEMENTATION. NO ANALYSIS-ONLY RESPONSES.

### ACTIVE FOCUS CAMPAIGN: PHASE 20 — LIVE CAPITAL DEPLOYMENT & CONTINUOUS VALIDATION: CAPITAL ALLOCATION, MULTI-STRATEGY ORCHESTRATION, DRIFT DETECTION, AUTO-RECOVERY (CRYPTO OPTIONS + ORDERFLOW)
Goal: Move from hardened execution to live-capital deployment with strict continuous validation. Build end-to-end: capital allocation engine across strategies/venues with risk budgets, multi-strategy orchestration & scheduling, live trading readiness gate (final go/no-go), post-trade reconciliation & settlement, drift/anomaly detection (PnL, Greeks, fills, latency), auto-recovery & circuit-breaker escalation, deterministic simulation of live constraints, full audit trail. Integrate with Phase17 intents + Phase18 observability/attribution + Phase19 OMS/risk/gates. All paper-only by default with hard live gating. No placeholders.

Deliverables (ALL REQUIRED):
1. `src/capital/phase20_capital_allocator.py` — CapitalAllocator: risk-budget allocation, per-strategy/per-venue caps, Kelly-ish sizing with hard limits, rebalance hooks, deterministic.
2. `src/orchestration/phase20_strategy_orchestrator.py` — StrategyOrchestrator: multi-strategy scheduling, priority/dependency ordering, resource locks, deterministic execution plan.
3. `src/deployment/phase20_live_readiness_gate.py` — LiveReadinessGate: final go/no-go across capital/connectivity/risk/compliance/drift, approval state machine, hard block unless all satisfied.
4. `src/reconciliation/phase20_post_trade_recon.py` — PostTradeRecon: fills vs orders vs positions, discrepancy detection, settlement checks, audit log.
5. `src/monitoring/phase20_drift_detector.py` — DriftDetector: PnL/Greeks/fills/latency drift, anomaly scoring, alert hooks.
6. `src/resilience/phase20_auto_recovery.py` — AutoRecovery: circuit-breaker escalation, restart/retry policies, safe-mode transitions.
7. `scripts/run_phase20_live_capital_campaign.py` — CLI (--symbols, --venues, --strategies, --seed, --cycles, --paper-only required True, --enforce-gates, --outdir). Runs integrated flow with Phase17/18/19.
8. `tests/test_phase20_live_capital.py` — >=60 substantive deterministic tests (fixed seeds, mocks, no network, allow_nan=False).
9. Artifacts: PHASE20_CAPITAL_ALLOCATION_REPORT.json/md, PHASE20_STRATEGY_ORCHESTRATION_REPORT.json/md, PHASE20_LIVE_READINESS_REPORT.json/md, PHASE20_POST_TRADE_RECON_REPORT.json/md, PHASE20_DRIFT_DETECTION_REPORT.json/md, PHASE20_AUTO_RECOVERY_REPORT.json/md, PHASE20_LIVE_CAPITAL_MASTER_REPORT.json/md under research_state/.
10. Determinism: identical seed -> identical artifacts. Finite numerics only. Strict serialization. Full integration with existing patterns.

### IMMEDIATE ACTIONS
- Read this file first. Verify gate GREEN (1181 passed). Phase 19 verified complete.
- Build Phase 20 end-to-end (modules + script + tests + artifacts). NO placeholders/TODOs.
- Run tests frequently; keep gate GREEN. Add tests to cover allocation, orchestration, readiness, recon, drift, recovery.
- Update this file with fresh timestamp/files/notes on completion with `python -m pytest tests/ -q` result.

CONSTRAINTS (NON-NEGOTIABLE):
- No placeholders/TODOs/FIXMEs/HACKs/XXX. Implement fully end-to-end.
- Keep ALL existing tests passing. Only add tests/modules.
- Determinism + finite numerics. No NaN/Inf. Validate strictly.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Integrate with existing telemetry/serialization, resilience, monitoring, governance patterns.
- Before ending: update THIS FILE with fresh UTC timestamp, files changed, rationale, and run `python -m pytest tests/ -q` (must be GREEN).
- Ship code+tests+artifacts to completion. NO analysis-only. NO stopping at scaffolding.

**ACTION NOW:** Begin Phase 20 immediately. Prioritize crypto options + orderflow. Build heavy implementation.
EOF
echo done