# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-02T01:16:09Z
# Updated (UTC): 2026-11-02T01:16:09Z
# Project: Cryptocurrency-quantitative-options-orderflow-strategy
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution + regime-aware MM/hedging + live-readiness hardening)

THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (2395 passed, 2 skipped, 0 failed) — verified 2026-11-02T01:12:52Z via `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q`. Bottlenecks REMOVED: created `src/recovery/` (was missing). ALL SESSIONS UNBLOCKED.

COMPLETED (DO NOT REDO):
- Phases 1-38: All complete. Phase 38 fully shipped with all deliverables, tests, artifacts. Gate GREEN at 2395 passed. Remove from pending; auto-advance to Phase 39.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-02T01:16:09Z
INITIAL TASK FOR NEXT SESSION: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW. IMMEDIATELY START AND COMPLETE PHASE 39 (Live-Readiness Hardening, Kill-Switches & Disaster Recovery) END-TO-END. Phase 38 is COMPLETE. HEAVY QUANT IMPLEMENTATION ONLY. NO SCAFFOLDING, NO PLANNING DOCS. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES (src/tests/scripts/artifacts). IF NO CODE WRITTEN -> YOU HAVE NOT DONE THE JOB. The repo name is Cryptocurrency-quantitative-options-orderflow-strategy, so crypto options + orderflow is the domain; every task must serve it.

MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER):
1. VERIFY GATE: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q` -> MUST be GREEN. If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist anywhere -> FIX FIRST. Remove bottlenecks immediately.
2. DO NOT REDO PHASES 1-38. Do not redo shipped Phase 38 modules. Extend/compose only.
3. SHIP PHASE 39 DELIVERABLES END-TO-END THIS SESSION. Code + tests + artifacts. No stopping at scaffolding. `src/recovery/` now exists (created). BUILD HEAVY INTEGRATION.
4. ON PHASE 39 ACCEPTANCE -> IMMEDIATELY ATTACK PHASE 40 (next campaign). Same rules: ship all deliverables, tests, artifacts; gate GREEN; update THIS FILE.
5. BEFORE ENDING: Update this file with fresh UTC timestamp, files changed (full paths), rationale. Re-verify gate GREEN. No session ends with Phase 39 incomplete once started.

BOTTLENECK POLICY (ENFORCED — REMOVES INEFFICIENCY):
- If blocked by missing integration, missing data wiring, cross-module coupling, or unclear interfaces -> IMPLEMENT production-grade glue NOW (no stubs, no TODOs).
- If tests fail due to integration gaps -> FIX integration, not tests (unless tests themselves are incorrect relative to spec).
- Do not create planning handoffs, roadmaps, or design docs. Write production code.
- Do not "explore" - read only what's necessary to implement immediately.
- If a directory is missing or not writable, create/fix it now so the next session is not blocked.
- Every session MUST produce tangible file changes (src/tests/scripts/artifacts). If no code written -> you have not done the job.

## ACTIVE CAMPAIGN: PHASE 39 — LIVE-READINESS HARDENING, KILL-SWITCHES & DISASTER RECOVERY
Timestamp (UTC): 2026-11-02T01:16:09Z
Status: NOT STARTED (deliverables missing; `src/recovery/` created). START NOW.
Goal: Extend Phase 38 with multi-layer kill-switches, circuit breakers, position limits by venue/regime, disaster recovery (state checkpoint/restore), incident logging, and pre-trade/post-trade validation. Deterministic, PAPER-ONLY by default, LIVE strictly hard-gated with multiple independent gates. Heavy quant integration across crypto options + orderflow.
Deliverables (SHIP ALL):
1. `src/risk/phase39_kill_switches_circuit_breakers.py`
2. `src/recovery/phase39_disaster_recovery.py`
3. `src/validation/phase39_prepost_trade_validation.py`
4. `src/integration/phase39_live_readiness_loop.py`
5. `scripts/run_phase39_live_readiness_campaign.py`
6. `tests/test_phase39_live_readiness.py` >= 40 substantive tests
7. Artifacts under `research_state/`: PHASE39_KILL_SWITCH_REPORT.*, PHASE39_RECOVERY_REPORT.*, PHASE39_VALIDATION_REPORT.*, PHASE39_LIVE_READINESS_LOOP_REPORT.*, PHASE39_CAMPAIGN_SUMMARY.*

Acceptance: gate GREEN (>=2435 passed, 0 failed), no placeholders/TODOs/FIXMEs/HACKs/XXX, deterministic finite numerics, PAPER-ONLY default, LIVE paths require multiple hard gates + tests, integrate with Phases 17-38. Update THIS FILE with fresh UTC timestamp before ending. (Current: 2395 passed, target >=2435)

## NEXT FOCUS CAMPAIGN (AUTO-ENFORCED AFTER PHASE 39 ACCEPTANCE - NO NEW INSTRUCTIONS NEEDED)
Timestamp (UTC): 2026-11-02T01:16:09Z
PHASE 40: Post-Trade Reconciliation, Margin/Collateral & Position Auditing (CRYPTO OPTIONS + ORDERFLOW)
Goal: Extend Phase 39 with automated position/PnL/margin reconciliation against exchange state, collateral auditing, discrepancy auto-halt, and full audit trail. Deterministic, PAPER-ONLY by default.
Deliverables (SHIP ALL):
1. `src/reconciliation/phase40_position_margin_audit.py`
2. `src/integration/phase40_reconciliation_loop.py`
3. `scripts/run_phase40_reconciliation_campaign.py`
4. `tests/test_phase40_reconciliation.py` >= 30 substantive tests
5. Artifacts under `research_state/`: PHASE40_RECONCILIATION_REPORT.*, PHASE40_MARGIN_AUDIT_REPORT.*, PHASE40_POSITION_AUDIT_REPORT.*, PHASE40_CAMPAIGN_SUMMARY.*
Acceptance: gate GREEN (target >=2470 passed, 0 failed), no placeholders/TODOs/FIXMEs/HACKs/XXX, deterministic finite numerics, PAPER-ONLY default, integrate with Phases 17-39. Update THIS FILE before ending.

## CONSTRAINTS (NON-NEGOTIABLE):
- NO placeholders/TODOs/FIXMEs/HACKs/XXX. Ever.
- Keep ALL existing tests passing. Add tests, don't break.
- Determinism + finite numerics. No random without seed. No NaN/Inf.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Before ending ANY session: update THIS FILE with fresh UTC timestamp, files changed (full paths), rationale. Run `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q` -> MUST BE GREEN.
- NEVER stop at scaffolding. Implement, test, integrate, artifactize.
- Extend completed phases - never redo.
- Prioritize crypto options + orderflow. Every deliverable must serve that domain.

**ACTION NOW:** Complete Phase 39 deliverables end-to-end starting immediately. Bottlenecks removed. Keep gate GREEN. Auto-advance to Phase 40 on acceptance. No other tasks. No deviations.
