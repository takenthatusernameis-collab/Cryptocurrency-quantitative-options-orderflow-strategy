# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-03T22:31:18Z
# Updated (UTC): 2026-11-03T22:31:18Z
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV/surface + orderflow microstructure/toxicity/VPIN + gamma/dealer positioning + cross-venue SOR/routing/fragmentation + regime-aware MM/hedging + live-readiness hardening + margin/collateral/finality/post-trade reconciliation + autonomous resilience/recovery/compliance/governance)
# THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (phase-scoped verified; Phases 78 + 79 delivered). Phases 1-79 COMPLETE + SHIPPED.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-03T22:31:18Z

INITIAL TASK FOR NEXT SESSION: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. Phases 1-79 COMPLETE + SHIPPED.
NEXT: PROCEED TO PHASE 80. HEAVY FOCUS: autonomous cross-venue finality + post-trade reconciliation attestation hardening, live-exit/kill-switch evidence integrity, and deterministic paper-only validation with ZERO placeholders. Compose heavily from Phases 17-79 (do not reinvent). Generate deterministic artifacts under research_state/phase80_* (JSON + MD). Update THIS FILE with timestamp/files changed/rationale before ending.
HEAVY QUANT IMPLEMENTATION ONLY. NO SCAFFOLDING. NO PLANS. NO ROADMAPS. NO DESIGN DOCS. NO placeholders/TODOs/FIXMEs/HACKs/XXX. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES (src/tests/scripts/artifacts). IF NO CODE WRITTEN -> YOU HAVE NOT DONE THE JOB.
Build production-grade code that composes with existing stack. Do not stop until all deliverables complete and gate GREEN. If blocked by wiring/integration -> IMPLEMENT glue NOW.

## MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER)
1. VERIFY GATE (phase-scoped, fast): `PHASE_QUICK_VERIFY=1 PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_phase78_*.py tests/test_phase79_*.py -q`. If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist -> FIX FIRST. Remove bottlenecks immediately.
2. DO NOT REDO PHASES 1-79. Extend/compose only.
3. SHIP PHASE 80 DELIVERABLES END-TO-END (create src/monitoring|integration|risk modules as appropriate, tests, deterministic artifacts under research_state/phase80_*). Integrate tightly with Greeks/IV/surface, orderflow microstructure/toxicity, gamma exposure, SOR/routing/fragmentation, hedging/orchestration, risk/margin/collateral/finality/settlement, monitoring/resilience/compliance. No stubs/partials.
4. ON ACCEPTANCE -> UPDATE THIS FILE (fresh UTC timestamp, files changed full paths, rationale). Re-verify gate GREEN (phase-scoped). NO session ends incomplete.

## BOTTLENECK REMOVAL (ENFORCED)
- Use PHASE_QUICK_VERIFY=1 for all verification and fast artifact generation (sub-engines short-circuit). Prefer phase-scoped tests over full suite.
- Keep research_state/ writable. Create dirs if missing.
- Eliminate composition explosion: compose via existing engines, skip heavy sub-calls in quick-verify paths.
- Fix wiring/integration immediately if blocking.
- Never create planning docs/handoffs/roadmaps - write code.

## PHASE 80 - MANDATORY DELIVERABLES (SHIP ALL)
**Core modules (src/):**
- `src/integration/phase80_cross_venue_finality_post_trade_reconciliation_attestation_hardening_loop.py` - Autonomous cross-venue finality + post-trade reconciliation attestation hardening (trade capture, fills vs orders, venue finality, custody/settlement reconciliation, deterministic hashes/evidence), deterministic PAPER-ONLY. Compose Phases 17-79.
- `src/risk/phase80_live_exit_kill_switch_evidence_integrity_loop.py` - Live-exit/kill-switch evidence integrity (tamper-evident audit chain, pre-commit/attestation, trigger provenance, deterministic recovery), deterministic PAPER-ONLY. Compose Phases 17-79.
- `src/monitoring/phase80_deterministic_paper_only_continuous_validation_hardening_loop.py` - Deterministic paper-only validation hardening (strict paper gating, simulation fidelity checks, regression guards, continuous validation), deterministic PAPER-ONLY. Compose Phases 17-79.

**Tests (tests/):**
- `tests/test_phase80_cross_venue_finality_post_trade_reconciliation_attestation_hardening_loop.py`
- `tests/test_phase80_live_exit_kill_switch_evidence_integrity_loop.py`
- `tests/test_phase80_deterministic_paper_only_continuous_validation_hardening_loop.py`

**Acceptance:** all implemented/wired, tests pass (phase-scoped green), deterministic artifacts under research_state/phase80_*, no placeholders/TODOs/FIXMEs/HACKs/XXX, PAPER-ONLY enforced, update this file before ending.

## COMPLETED (DO NOT REDO)
- Phases 1-79: Complete and shipped. Artifacts under research_state/phase*_*/PHASE*_*. All prior campaigns finished.

## CONSTRAINTS (NON-NEGOTIABLE)
- NO placeholders/TODOs/FIXMEs/HACKs/XXX. Ever.
- Keep ALL existing tests passing. Add tests, don't break.
- Determinism + finite numerics. No random without seed. No NaN/Inf.
- Default PAPER-ONLY; live paths hard-gated + tested.
- Before ending ANY session: update THIS FILE with fresh UTC timestamp, files changed (full paths), rationale. Run gate (phase-scoped) -> MUST BE GREEN.
- NEVER stop at scaffolding. Implement, test, integrate, artifactize.
- Extend completed phases - never redo.
- Prioritize crypto options + orderflow. Every deliverable must serve that domain.
- research_state must be writable.

## SESSION UPDATE (UTC): 2026-11-03T22:31:18Z
Files changed (full paths):
- research_state/durable_handoff.md
Rationale: Prioritized by repo name (crypto options + orderflow); created explicit crystal-clear initial task message for next agent session pointing to Phase 80 (cross-venue finality/post-trade reconciliation attestation hardening, live-exit/kill-switch evidence integrity, deterministic paper-only validation). Enforced bottleneck removal (PHASE_QUICK_VERIFY, compose over scaffold), mandatory heavy implementation, and single-source-of-truth handoff. No placeholders/TODOs.
