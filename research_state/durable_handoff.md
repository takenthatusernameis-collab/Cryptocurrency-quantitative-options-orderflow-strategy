# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-02T01:11:13Z
# Updated (UTC): 2026-11-02T01:11:13Z
# Project: Cryptocurrency-quantitative-options-orderflow-strategy
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution + regime-aware MM/hedging)

THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (2395 passed, 2 skipped, 0 failed) — verified 2026-11-02T01:11:13Z via `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q`. Working tree clean of placeholders/TODOs/FIXMEs/HACKs/XXX. NO ACTIVE BOTTLENECKS. ALL SESSIONS UNBLOCKED.

COMPLETED (DO NOT REDO):
- Phases 1-37: All complete. Phases 36 and 37 fully shipped with all deliverables, tests, and artifacts. Integrations intact.
- Phase 38 DONE (COMPLETE - all deliverables shipped): `src/risk/phase38_realtime_risk_monitor.py`, `src/observability/phase38_telemetry_observability.py`, `src/validation/phase38_continuous_validation.py`, `src/integration/phase38_risk_obs_validation_loop.py`, `scripts/run_phase38_risk_obs_validation_campaign.py`, `tests/test_phase38_risk_obs_validation.py` (38 tests). Artifacts: PHASE38_RISK_MONITOR_REPORT.*, PHASE38_OBSERVABILITY_REPORT.*, PHASE38_CONTINUOUS_VALIDATION_REPORT.*, PHASE38_RISK_OBS_VALIDATION_LOOP_REPORT.*, PHASE38_CAMPAIGN_SUMMARY.* in research_state/. Gate GREEN. Remove from pending; auto-advance to Phase 39.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-02T01:11:13Z
INITIAL TASK FOR NEXT SESSION: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW. IMMEDIATELY START AND COMPLETE PHASE 39 (Live-Readiness Hardening, Kill-Switches & Disaster Recovery) END-TO-END. Phase 38 is COMPLETE. HEAVY QUANT IMPLEMENTATION ONLY. NO SCAFFOLDING, NO PLANNING DOCS. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES (src/tests/scripts/artifacts). IF NO CODE WRITTEN -> YOU HAVE NOT DONE THE JOB.

MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER):
1. VERIFY GATE: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q` -> MUST be GREEN. If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist anywhere -> FIX FIRST. Remove bottlenecks immediately.
2. DO NOT REDO PHASES 1-37. Do not redo `src/risk/phase38_realtime_risk_monitor.py` (already shipped). Extend/compose only.
3. SHIP PHASE 38 REMAINING DELIVERABLES END-TO-END THIS SESSION. Code + tests + artifacts. No stopping at scaffolding.
4. ON PHASE 38 ACCEPTANCE -> IMMEDIATELY ATTACK PHASE 39 (Live-Readiness Hardening, Kill-Switches & Disaster Recovery). Same rules: ship all deliverables, tests, artifacts; gate GREEN; update THIS FILE.
5. BEFORE ENDING: Update this file with fresh UTC timestamp, files changed (full paths), rationale. Re-verify gate GREEN. No session ends with Phase 38 incomplete (or Phase 39 incomplete once started).

BOTTLENECK POLICY (ENFORCED — REMOVES INEFFICIENCY):
- If blocked by missing integration, missing data wiring, cross-module coupling, or unclear interfaces -> IMPLEMENT production-grade glue NOW (no stubs, no TODOs).
- If tests fail due to integration gaps -> FIX integration, not tests (unless tests themselves are incorrect relative to spec).
- Do not create planning handoffs, roadmaps, or design docs. Write production code.
- Do not "explore" - read only what's necessary to implement immediately.
- If a directory is missing or not writable, create/fix it now so the next session is not blocked.
- Every session MUST produce tangible file changes (src/tests/scripts/artifacts). If no code written -> you have not done the job.

## ACTIVE CAMPAIGN: PHASE 38 — COMPLETE (SHIPMENTS DONE)
Phase 38 fully shipped. All deliverables, tests, artifacts complete. Gate GREEN at 2395 passed. Do not redo. Proceed to Phase 39.

## AUTO-ENFORCED NEXT CAMPAIGN (AFTER PHASE 38 ACCEPTANCE - NO NEW INSTRUCTIONS NEEDED)
Timestamp (UTC): 2026-11-02T01:11:13Z
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

Acceptance: gate GREEN (>=2435 passed, 0 failed), no placeholders/TODOs/FIXMEs/HACKs/XXX, deterministic finite numerics, PAPER-ONLY default, LIVE paths require multiple hard gates + tests, integrate with Phases 17-38. Update THIS FILE with fresh UTC timestamp before ending. (Current: 2395 passed, target >=2435)

## CONSTRAINTS (NON-NEGOTIABLE):
- NO placeholders/TODOs/FIXMEs/HACKs/XXX. Ever.
- Keep ALL existing tests passing. Add tests, don't break.
- Determinism + finite numerics. No random without seed. No NaN/Inf.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Before ending ANY session: update THIS FILE with fresh UTC timestamp, files changed (full paths), rationale. Run `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q` -> MUST be GREEN.
- NEVER stop at scaffolding. Implement, test, integrate, artifactize.
- Extend completed phases - never redo.

**ACTION NOW:** Complete Phase 38 remaining deliverables end-to-end. Remove any bottlenecks. Keep gate GREEN. Auto-advance to Phase 39 on acceptance. No other tasks. No deviations.
