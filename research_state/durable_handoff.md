# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-02T01:00:44Z
# Updated (UTC): 2026-11-02T01:00:44Z
# Project: Cryptocurrency-quantitative-options-orderflow-strategy
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution + regime-aware MM/hedging)

THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (2357 passed, 2 skipped, 0 failed) — verified 2026-11-02T01:00:44Z via `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q`. Working tree clean of placeholders/TODOs/FIXMEs/HACKs/XXX. NO ACTIVE BOTTLENECKS. ALL SESSIONS UNBLOCKED.

COMPLETED (DO NOT REDO):
- Phases 1-37: All complete. Phases 36 and 37 fully shipped with all deliverables, tests, and artifacts. Integrations intact.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-02T01:00:44Z
INITIAL TASK FOR NEXT SESSION: IMMEDIATELY ATTACK PHASE 38. PRIORITIZE BY REPO NAME - CRYPTO OPTIONS + ORDERFLOW. HEAVY QUANT IMPLEMENTATION ONLY. NO SCAFFOLDING, NO PLANNING DOCS, NO EXPLORATORY READS WITHOUT IMMEDIATE IMPLEMENTATION.

MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER):
1. VERIFY GATE: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q` -> MUST be GREEN. If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist anywhere -> FIX FIRST. Remove bottlenecks immediately.
2. DO NOT REDO PHASES 1-37. Extend them.
3. SHIP PHASE 38 END-TO-END THIS SESSION. Code + tests + artifacts. No stopping at scaffolding.
4. BEFORE ENDING: Update this file with fresh UTC timestamp, files changed, rationale. Re-verify gate GREEN. No session ends with Phase 38 incomplete.

BOTTLENECK POLICY (ENFORCED):
- If blocked by missing integration, missing data wiring, cross-module coupling, or unclear interfaces -> IMPLEMENT production-grade glue NOW (no stubs, no TODOs).
- If tests fail due to integration gaps -> FIX integration, not tests (unless tests themselves are incorrect relative to spec).
- Do not create planning handoffs, roadmaps, or design docs. Write production code.
- Do not "explore" - read only what's necessary to implement immediately.
- Every session MUST produce tangible file changes (src/tests/scripts/artifacts). If no code written -> you have not done the job.

## ACTIVE CAMPAIGN: PHASE 38 (ATTACK NOW - NO SCOPE CREEP DOWN, ONLY SCOPE UP TO INTEGRATE)
Goal: Extend Phase 37 orderflow routing loop with real-time risk monitoring, observability/telemetry, and continuous validation for crypto options + orderflow. Deterministic, finite numerics, PAPER-ONLY default with hard-gated live paths. Integrate tightly with Phases 17-37 (risk, margin, reallocation, regime, hedging, MM, routing).

DELIVERABLES (SHIP ALL - NO PARTIAL):
1. `src/risk/phase38_realtime_risk_monitor.py` - Real-time VaR/CVaR, Greeks limits (delta/gamma/vega/theta), exposure caps, drawdown guards, regime-aware breach actions
2. `src/observability/phase38_telemetry_observability.py` - Structured metrics/traces, counters/gauges/histograms, alerting hooks, deterministic serialization
3. `src/validation/phase38_continuous_validation.py` - Backtest/live parity checks, data drift detection, model drift, slippage tracking, automated validation gates
4. `src/integration/phase38_risk_obs_validation_loop.py` - Orchestrates all three with Phase 37 loop, regime filters, margin/reallocation hooks, hard-gated live paths
5. `scripts/run_phase38_risk_obs_validation_campaign.py` - Deterministic campaign runner producing all artifacts
6. `tests/test_phase38_risk_obs_validation.py` >= 40 substantive tests (cover limits, breaches, gating, parity, drift, determinism, edge cases)
7. Artifacts under `research_state/`: `PHASE38_RISK_MONITOR_REPORT.*`, `PHASE38_OBSERVABILITY_REPORT.*`, `PHASE38_CONTINUOUS_VALIDATION_REPORT.*`, `PHASE38_RISK_OBS_VALIDATION_LOOP_REPORT.*`, `PHASE38_CAMPAIGN_SUMMARY.*` (json/md/csv as appropriate)

ACCEPTANCE CRITERIA (HARD GATES):
- Gate GREEN: >= 2397 passed, 0 failed (expand tests from current 2357). All existing tests remain passing.
- Zero placeholders/TODOs/FIXMEs/HACKs/XXX anywhere in new/modified files.
- Deterministic outputs, finite numerics, no NaN/Inf leakage.
- PAPER-ONLY default. All live execution paths hard-gated with explicit flags + tests proving gating.
- Full integration with Phases 17-37. No duplication of completed logic - extend, compose, wire.
- Artifacts are concrete and produced by the campaign script.

## AUTO-ENFORCED NEXT CAMPAIGN (AFTER PHASE 38 ACCEPTANCE - NO NEW INSTRUCTIONS NEEDED)
Timestamp (UTC): 2026-11-02T01:00:44Z
PHASE 39: Live-Readiness Hardening, Kill-Switches & Disaster Recovery (CRYPTO OPTIONS + ORDERFLOW)
Goal: Extend Phase 38 with multi-layer kill-switches, circuit breakers, position limits by venue/regime, disaster recovery (state checkpoint/restore), incident logging, and pre-trade/post-trade validation. Deterministic, PAPER-ONLY by default, LIVE strictly hard-gated with multiple independent gates.
Deliverables (SHIP ALL):
1. `src/risk/phase39_kill_switches_circuit_breakers.py`
2. `src/recovery/phase39_disaster_recovery.py`
3. `src/validation/phase39_prepost_trade_validation.py`
4. `src/integration/phase39_live_readiness_loop.py`
5. `scripts/run_phase39_live_readiness_campaign.py`
6. `tests/test_phase39_live_readiness.py` >= 40 substantive tests
7. Artifacts under `research_state/`: PHASE39_KILL_SWITCH_REPORT.*, PHASE39_RECOVERY_REPORT.*, PHASE39_VALIDATION_REPORT.*, PHASE39_LIVE_READINESS_LOOP_REPORT.*, PHASE39_CAMPAIGN_SUMMARY.*

Acceptance: gate GREEN (>=2437 passed, 0 failed), no placeholders/TODOs/FIXMEs/HACKs/XXX, deterministic finite numerics, PAPER-ONLY default, LIVE paths require multiple hard gates + tests, integrate with Phases 17-38. Update THIS FILE with fresh UTC timestamp before ending.

## CONSTRAINTS (NON-NEGOTIABLE):
- NO placeholders/TODOs/FIXMEs/HACKs/XXX. Ever.
- Keep ALL existing tests passing. Add tests, don't break.
- Determinism + finite numerics. No random without seed. No NaN/Inf.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Before ending ANY session: update THIS FILE with fresh UTC timestamp, files changed (full paths), rationale. Run `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q` -> MUST be GREEN.
- NEVER stop at scaffolding. Implement, test, integrate, artifactize.
- Extend completed phases - never redo.

**ACTION NOW:** Ship Phase 38 end-to-end. Remove any bottlenecks. Keep gate GREEN. Auto-advance to Phase 39 on acceptance. No other tasks. No deviations.
