# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-03T14:54:15Z
# Updated (UTC): 2026-11-03T14:54:15Z
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV/surface + orderflow microstructure/toxicity/VPIN + gamma/dealer positioning + cross-venue SOR/routing/fragmentation + regime-aware MM/hedging + live-readiness hardening + margin/collateral/finality/post-trade reconciliation + autonomous resilience/recovery/compliance/governance)
# THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (phase-scoped verified; Phase 76 tests pass). Phases 1-76 COMPLETE + SHIPPED.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-03T14:54:15Z

INITIAL TASK FOR NEXT SESSION: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. Phases 69-76 COMPLETE + SHIPPED.
NEXT: SHIP PHASE 77 END-TO-END THIS SESSION. Focus ruthlessly on PRODUCTION-CRITICAL crypto options + orderflow gaps: autonomous real-time gamma/dealer positioning exposure management + cross-venue delta/gamma/vega hedging with toxicity-aware routing + dynamic position limits with pre-trade risk checks + options liquidity seeking with inventory skew + kill-switch integration + full attestation trail.
Compose heavily from Phases 17-76 (do not reinvent). Generate deterministic artifacts under research_state/phase77_* (JSON + MD). Update THIS FILE with timestamp/files changed/rationale before ending.
HEAVY QUANT IMPLEMENTATION ONLY. NO SCAFFOLDING. NO PLANS. NO ROADMAPS. NO DESIGN DOCS. NO placeholders/TODOs/FIXMEs/HACKs/XXX. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES (src/tests/scripts/artifacts). IF NO CODE WRITTEN -> YOU HAVE NOT DONE THE JOB.
Build production-grade code that composes with existing stack. Do not stop until all deliverables complete and gate GREEN. If blocked by wiring/integration -> IMPLEMENT glue NOW.

## MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER)
1. VERIFY GATE (phase-scoped, fast): `PHASE_QUICK_VERIFY=1 PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_phase76_*.py tests/test_phase75_*.py tests/test_phase74_*.py -q` (or focused set). If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist -> FIX FIRST. Remove bottlenecks immediately.
2. DO NOT REDO PHASES 1-76. Extend/compose only.
3. SHIP PHASE 77 DELIVERABLES END-TO-END (create src/alpha|hedging|risk|integration modules as appropriate, tests, deterministic artifacts under research_state/phase77_*). Integrate tightly with Greeks/IV/surface, orderflow microstructure/toxicity, gamma exposure, SOR/routing/fragmentation, hedging/orchestration, risk/margin/collateral/finality/settlement, monitoring/resilience/compliance. No stubs/partials.
4. ON ACCEPTANCE -> UPDATE THIS FILE (fresh UTC timestamp, files changed full paths, rationale). Re-verify gate GREEN (phase-scoped). NO session ends incomplete.

## BOTTLENECK REMOVAL (ENFORCED)
- Use PHASE_QUICK_VERIFY=1 for all verification and fast artifact generation (sub-engines short-circuit). Prefer phase-scoped tests over full suite.
- Keep research_state/ writable. Create dirs if missing.
- Eliminate composition explosion: compose via existing engines, skip heavy sub-calls in quick-verify paths.
- Fix wiring/integration immediately if blocking.
- Never create planning docs/handoffs/roadmaps - write code.

## PHASE 77 - MANDATORY DELIVERABLES (SHIP ALL)
**Core modules (src/):**
- `src/alpha/phase77_execution_alpha_gamma_dealer_positioning_hedge_engine.py` - Real-time gamma/dealer positioning exposure management for crypto options + orderflow: Greeks aggregation, gamma exposure, vanna/charm aware hedging signals, toxicity-aware gating, deterministic PAPER-ONLY. Compose Phases 17-76.
- `src/hedging/phase77_adaptive_toxicity_resilient_cross_venue_gamma_hedge_orchestrator.py` - Cross-venue delta/gamma/vega hedging orchestration with inventory skew, liquidity fragmentation/adverse selection awareness, venue throttling, deterministic PAPER-ONLY. Compose Phases 17-76.
- `src/integration/phase77_autonomous_production_gamma_risk_pretrade_kill_switch_enforcement_loop.py` - Pre-trade risk checks, dynamic position limits, gamma risk budgets, kill-switch attestation, auto-hedge/de-risk on breach, deterministic artifacts; PAPER-ONLY. Compose Phases 17-76.

**Tests (tests/):**
- `tests/test_phase77_execution_alpha_gamma_dealer_positioning_hedge_engine.py`
- `tests/test_phase77_adaptive_toxicity_resilient_cross_venue_gamma_hedge_orchestrator.py`
- `tests/test_phase77_autonomous_production_gamma_risk_pretrade_kill_switch_enforcement_loop.py`

**Acceptance:** all implemented/wired, tests pass (phase-scoped green), deterministic artifacts under research_state/phase77_*, no placeholders/TODOs/FIXMEs/HACKs/XXX, PAPER-ONLY enforced, update this file before ending.

## COMPLETED (DO NOT REDO)
- Phases 1-76: Complete and shipped. Artifacts under research_state/phase*_*/PHASE*_*. All prior campaigns finished.

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
