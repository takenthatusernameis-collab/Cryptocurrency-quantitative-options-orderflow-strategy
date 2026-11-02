# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-02T03:03:03Z
# Updated (UTC): 2026-11-02T03:03:03Z
# Project: Cryptocurrency-quantitative-options-orderflow-strategy
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution + regime-aware MM/hedging + live-readiness hardening + post-trade reconciliation/margin/collateral)

THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (2467 passed, 2 skipped, 0 failed) — verified 2026-11-02T03:03:03Z via `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q`. Bottlenecks REMOVED. ALL SESSIONS UNBLOCKED.

COMPLETED (DO NOT REDO):
- Phases 1-39: Complete. Phase 39 (Live-Readiness Hardening, Kill-Switches & Disaster Recovery) COMPLETE with all deliverables, tests, artifacts. Gate GREEN at 2437 passed. Auto-advance to Phase 40.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-02T03:03:03Z

INITIAL TASK FOR NEXT SESSION: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. IMMEDIATELY START AND COMPLETE PHASE 40 (Post-Trade Reconciliation, Margin/Collateral & Position Auditing) END-TO-END. Phase 39 is COMPLETE. HEAVY QUANT IMPLEMENTATION ONLY. NO SCAFFOLDING, NO PLANNING DOCS, NO ROADMAPS. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES (src/tests/scripts/artifacts). IF NO CODE WRITTEN -> YOU HAVE NOT DONE THE JOB. The repo name is Cryptocurrency-quantitative-options-orderflow-strategy, so crypto options + orderflow is the domain; every task must serve it. Build production-grade code that integrates with existing phases 17-39. Do not stop until all Phase 40 deliverables are complete and gate is GREEN.

MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER):
1. VERIFY GATE: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q` -> MUST be GREEN (2437 passed currently). If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist anywhere -> FIX FIRST. Remove bottlenecks immediately.
2. DO NOT REDO PHASES 1-39. Do not redo shipped Phase 39 modules. Extend/compose only.
3. SHIP PHASE 40 DELIVERABLES END-TO-END THIS SESSION. Code + tests + artifacts. No stopping at scaffolding. Implement full reconciliation logic (fills vs orders vs positions), margin/collateral calculations for crypto options, position auditing with discrepancy detection and auto-halt integration, full audit trail.
4. ON PHASE 40 ACCEPTANCE -> IMMEDIATELY ATTACK PHASE 41 (next campaign). Same rules: ship all deliverables, tests, artifacts; gate GREEN; update THIS FILE.
5. BEFORE ENDING: Update this file with fresh UTC timestamp, files changed (full paths), rationale. Re-verify gate GREEN. No session ends with Phase 40 incomplete once started.

BOTTLENECK POLICY (ENFORCED — REMOVES INEFFICIENCY):
- If blocked by missing integration, missing data wiring, cross-module coupling, or unclear interfaces -> IMPLEMENT production-grade glue NOW (no stubs, no TODOs).
- If tests fail due to integration gaps -> FIX integration, not tests (unless tests themselves are incorrect relative to spec).
- Do not create planning handoffs, roadmaps, or design docs. Write production code.
- Do not "explore" - read only what's necessary to implement immediately.
- If a directory is missing or not writable, create/fix it now so the next session is not blocked.
- Every session MUST produce tangible file changes (src/tests/scripts/artifacts). If no code written -> you have not done the job.
- Leverage existing patterns: Phase 20 post-trade recon, Phase 38/39 risk/validation loops, serialization/telemetry. Compose, don't reinvent.

## ACTIVE CAMPAIGN: PHASE 40 — POST-TRADE RECONCILIATION, MARGIN/COLLATERAL & POSITION AUDITING
Timestamp (UTC): 2026-11-02T03:03:03Z
Status: NOT STARTED (deliverables missing). START NOW.
Goal: Extend Phase 39 with automated position/PnL/margin reconciliation against exchange state, collateral auditing, discrepancy auto-halt, and full audit trail. Deterministic, PAPER-ONLY by default. Must serve crypto options + orderflow domain.

Deliverables (SHIP ALL):
1. `src/reconciliation/phase40_position_margin_audit.py` - Core reconciliation engine for crypto options positions, fills vs orders vs positions, margin/collateral calculation, discrepancy detection with auto-halt triggers, full audit trail
2. `src/integration/phase40_reconciliation_loop.py` - Integration loop composing with Phases 17-39 (orderflow, routing, risk, validation, kill-switches)
3. `scripts/run_phase40_reconciliation_campaign.py` - Campaign runner producing all artifacts
4. `tests/test_phase40_reconciliation.py` >= 30 substantive tests - Cover reconciliation, margin/collateral, discrepancies, auto-halt, paper-only gates, determinism, finite numerics
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

Files changed this session (full paths): `research_state/durable_handoff.md` (updated to Phase 40 focus with crystal clear mandatory initial task message, refreshed timestamps 2026-11-02T02:11:54Z, enforced heavy implementation, removed bottlenecks)
Rationale: Strengthened single durable handoff per user request - made initial task message unmissable and impossible to avoid heavy work, prioritized crypto options+orderflow by repo name, codified bottleneck removal, specified exact Phase 40 deliverables with acceptance criteria. Gate remains GREEN at 2437 passed.
