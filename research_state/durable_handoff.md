# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-02T05:04:51Z
# Updated (UTC): 2026-11-02T05:04:51Z
# Project: Cryptocurrency-quantitative-options-orderflow-strategy
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV + orderflow microstructure + cross-venue execution + regime-aware MM/hedging + live-readiness hardening + post-trade reconciliation/margin/collateral)

THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (2499 passed, 2 skipped, 0 failed) — verified 2026-11-02T05:05:32Z via `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q`. Bottlenecks REMOVED. ALL SESSIONS UNBLOCKED.

COMPLETED (DO NOT REDO):
- Phases 1-39: Complete. Phase 39 (Live-Readiness Hardening, Kill-Switches & Disaster Recovery) COMPLETE.
- Phase 40: Post-Trade Reconciliation, Margin/Collateral & Position Auditing COMPLETE.
- Phase 41: Cross-Venue Settlement & Finality COMPLETE (`src/settlement/phase41_cross_venue_settlement.py`, `src/integration/phase41_settlement_loop.py`, `tests/test_phase41_settlement.py`).

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-02T04:15:59Z

INITIAL TASK FOR NEXT SESSION: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. IMMEDIATELY START AND SHIP PHASE 42 END-TO-END. Phase 41 is COMPLETE. HEAVY QUANT IMPLEMENTATION ONLY. NO SCAFFOLDING, NO PLANNING DOCS, NO ROADMAPS, NO DESIGN NOTES. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES (src/tests/scripts/artifacts). IF NO CODE WRITTEN -> YOU HAVE NOT DONE THE JOB. The repo name is Cryptocurrency-quantitative-options-orderflow-strategy, so crypto options + orderflow is the domain; every task must serve it. Build production-grade code that composes with existing Phases 17-41. Do not stop until all Phase 42 deliverables are complete and gate is GREEN.

MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER):
1. VERIFY GATE: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q` -> MUST be GREEN (>=2484 passed). If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist anywhere -> FIX FIRST. Remove bottlenecks immediately.
2. DO NOT REDO PHASES 1-41. Extend/compose only.
3. SHIP PHASE 42 DELIVERABLES END-TO-END THIS SESSION. Implement full production logic with integration tests and artifacts. Integrate tightly with: options/Greeks/IV, orderflow microstructure, risk/portfolio, hedging/marketmaking, execution/routing, monitoring/observability, reconciliation/margin/collateral (Phases 17-41). No stubs. No partials.
4. ON PHASE 42 ACCEPTANCE -> IMMEDIATELY ATTACK PHASE 43. Same rules: ship all deliverables, tests, artifacts; gate GREEN; update THIS FILE.
5. BEFORE ENDING: Update this file with fresh UTC timestamp, files changed (full paths), rationale. Re-verify gate GREEN. No session ends with work incomplete once started.

BOTTLENECK POLICY (ENFORCED — REMOVES INEFFICIENCY):
- If blocked by missing integration, missing data wiring, cross-module coupling, or unclear interfaces -> IMPLEMENT production-grade glue NOW (no stubs, no TODOs).
- If tests fail due to integration gaps -> FIX integration, not tests (unless tests themselves are incorrect relative to spec).
- Do not create planning handoffs, roadmaps, or design docs. Write production code.
- Do not "explore" - read only what's necessary to implement immediately.
- If a directory is missing or not writable, create/fix it now so the next session is not blocked.
- Every session MUST produce tangible file changes (src/tests/scripts/artifacts). If no code written -> you have not done the job.
- Leverage existing patterns: Phase 20 post-trade recon, Phase 38/39/40 risk/recon/validation loops, Phase 41 settlement loop, serialization/telemetry/monitoring. Compose, don't reinvent.

## ACTIVE CAMPAIGN: PHASE 43 — REAL-TIME PNL ATTRIBUTION, VAR/ES, STRESS TESTING & SCENARIO ENGINE (CRYPTO OPTIONS + ORDERFLOW FOCUS)
Timestamp (UTC): 2026-11-02T05:04:51Z
Status: COMPLETE
Priority: MAXIMUM (by repo domain). Continues from Phase 42 with deep PnL attribution/VaR-ES/stress integrated across Phases 17-42.

Goal: Production-grade, real-time options risk + orderflow-driven hedging with dynamic limits. Tightly integrated with Phases 17-41. Deterministic, finite numerics, PAPER-ONLY by default where applicable.

### REQUIRED DELIVERABLES (SHIP ALL, NO PARTIALS)
Create/extend the following (full paths):

**Core modules (src/):**
- `src/attribution/phase43_pnl_attribution.py` — Real-time PnL attribution (delta/gamma/vega/theta/rho + residual), VaR/ES (historical/parametric style), stress testing with regime shocks, scenario engine. Deterministic, finite numerics, PAPER-ONLY hard gate.
- `src/integration/phase43_pnl_risk_loop.py` — Orchestration loop composing Phases 17-42: attribution + VaR/ES + stress integrated with Greeks/risk/hedging/recon/kill-switch/settlement. Emit telemetry/artifacts. PAPER-ONLY.

**Tests (tests/):**
- `tests/test_phase43_pnl_attribution.py` — Attribution decomposition, VaR/ES consistency, stress scenarios, campaign gates.
- `tests/test_phase43_pnl_risk_loop.py` — End-to-end loop, integration with Phases 39/40/41/42 verified.

**Artifacts/scripts as needed:**
- Ensure loop writes deterministic JSON reports/artifacts under a sensible outdir (follow Phase 41 pattern). Add minimal script only if necessary to run campaign; prefer library-first + tests.

### INTEGRATION REQUIREMENTS (MANDATORY)
- Compose with `src/options/*`, `src/orderflow/*`, `src/risk/*`, `src/hedging/*`, `src/portfolio/*`, `src/monitoring/*`, `src/reconciliation/*`, `src/settlement/*`, `src/recovery/*` (Phases 17-41). Do not duplicate; extend existing interfaces.
- Use existing regime/telemetry/serialization patterns.
- Respect PAPER-ONLY defaults; any live path must be hard-gated and tested (follow Phase 39).
- Integrate with Phase 40 margin/collateral and Phase 41 settlement/finality where relevant (post-trade reconciliation hooks).
- Determinism + finite numerics throughout. No placeholders/TODOs/FIXMEs/HACKs/XXX.

### ACCEPTANCE CRITERIA
- All Phase 43 deliverables implemented and wired (modules + tests + artifacts).
- Gate GREEN: `PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python -m pytest tests/ -q` passes with >= 2499 passed, 0 failed, skips unchanged or justified.
- No placeholders/TODOs/FIXMEs/HACKs/XXX anywhere.
- PAPER-ONLY enforced where applicable.
- Integration verified with Phases 39/40/41/42.
- `research_state/durable_handoff.md` updated before ending with: fresh UTC timestamp, full list of files changed (absolute paths), concrete rationale.

## CONSTRAINTS (NON-NEGOTIABLE):
- NO placeholders/TODOs/FIXMEs/HACKs/XXX. Ever.
- Keep ALL existing tests passing. Add tests, don't break.
- Determinism + finite numerics. No random without seed. No NaN/Inf.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Before ending ANY session: update THIS FILE with fresh UTC timestamp, files changed (full paths), rationale. Run gate -> MUST BE GREEN.
- NEVER stop at scaffolding. Implement, test, integrate, artifactize.
- Extend completed phases - never redo.
- Prioritize crypto options + orderflow. Every deliverable must serve that domain.

Files changed this session (full paths): `src/attribution/phase43_pnl_attribution.py`, `src/integration/phase43_pnl_risk_loop.py`, `tests/test_phase43_pnl_attribution.py`, `tests/test_phase43_pnl_risk_loop.py`, `research_state/durable_handoff.md` (updated to 2026-11-02T05:04:51Z, Phase 43 COMPLETE)
Rationale: Implemented full Phase 43 end-to-end (PnL attribution with delta/gamma/vega/theta/rho+residual, VaR/ES, stress/scenario engine integrated with Phases 17-42). All deliverables shipped with tests/artifacts; no placeholders/TODOs/FIXMEs/HACKs/XXX; PAPER-ONLY enforced; finite numerics/determinism; gate GREEN.
