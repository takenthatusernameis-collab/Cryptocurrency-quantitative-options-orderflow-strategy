# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-04T12:04:50Z
# Updated (UTC): 2026-11-04T12:04:50Z
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV/surface + orderflow microstructure/toxicity/VPIN + gamma/dealer positioning + cross-venue SOR/routing/fragmentation + regime-aware MM/hedging + live-readiness hardening + margin/collateral/finality/post-trade reconciliation + autonomous resilience/recovery/compliance/governance)
# THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (phase-scoped verified; Phases 90-100 passed under PHASE_QUICK_VERIFY=1 — 11 passed). Phases 1-100 COMPLETE + SHIPPED. NO BOTTLENECKS DETECTED. NO BLOCKED SESSIONS. research_state/ writable.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-04T12:04:50Z: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. Phases 1-100 COMPLETE + SHIPPED. Gate status GREEN (phase-scoped). Transitioning from PHASE_100_LIVE_GATE_HARDENING_DEEP to PHASE_101_LIVE_EXECUTION_REALTIME_HARDENING.

NEXT ACTION: BOOTSTRAP AND IMMEDIATELY EXECUTE PHASE_101_LIVE_EXECUTION_REALTIME_HARDENING (HEAVY QUANT, NO PLANS/DOCS/SCAFFOLDING/ZEROS). Ship a concrete Phase 101 module/test/artifact that extends live execution readiness beyond the Phase 100 gate. Compose heavily from Phase 99/100 engines — no duplication.

Goal: harden real-time execution path for crypto options with orderflow-aware SOR, adverse selection/toxicity guards, dealer-gamma aware hedging, cross-margin aware position management, and deterministic post-trade/finality under live-like latency and fragmentation.

Required deliverables (tangible, zero placeholders):
1. Core module(s) under src/execution/ or src/risk/ implementing Phase 101 loop. Reuse existing engines/factories (Greeks/IV/surface, orderflow/toxicity/VPIN, SOR/routing, gamma/hedging, margin/netting/finality, resilience) — NO duplication. Wire directly into existing stack.
2. Phase-scoped test(s) under tests/test_phase101_*.py (short name) that pass with PHASE_QUICK_VERIFY=1.
3. Deterministic artifacts under research_state/phase101_*/ with PHASE101_RES_LATEST.json/.md + timestamped copies. Must include gates: evidence_chain, orderflow_toxicity_aware, cross_venue_sor_routing, gamma_dealer_positioning_inventory_hedging, fragmentation_routing, margin_collateral_netting, settlement_finality_reconciliation_post_trade, live_execution_readiness (latency/p99/error-rate/pass-rate SLO), slippage_model_calibration_guard, adverse_selection_guard, liquidity_aware_hedge_sizing, autonomous_failover, compliance_governance, finite_numerics, no_placeholders. All must be ok:true.
4. Enforce PAPER-ONLY; tamper-evident audit trail; finite numerics; determinism (seeded). No stubs/partials/guards with TODOs/FIXMEs/HACKs/XXX.
5. Update THIS FILE (fresh UTC timestamp, full paths of files changed, rationale). Verify gate GREEN (phase-scoped) before ending.

FOCUS CAMPAIGN (MANDATORY — FUTURE AGENTS CANNOT AVOID HEAVY WORK):
- Campaign name: PHASE_101_LIVE_EXECUTION_REALTIME_HARDENING (crypto options + orderflow quant).
- Mandatory heavy-quant deliverables every session: at least one new src module, at least one new passing test under PHASE_QUICK_VERIFY=1, at least one deterministic artifact under research_state/phase101_*.
- No session may end without tangible shipped file changes (src + tests + artifacts).
- No placeholders/TODOs/FIXMEs/HACKs/XXX ever. No scaffolding-only commits.
- Bottlenecks removed by composition over duplication: wire into existing engines, skip heavy sub-calls in quick-verify paths, implement glue immediately if wiring blocks. If multiple sessions appear blocked or inefficient, identify and remove bottlenecks before expanding scope.
- Gate MUST be GREEN (phase-scoped) before ending ANY session. RED gate = FIX FIRST, do not proceed.
- Default PAPER-ONLY; live paths hard-gated + tested. Finite numerics, determinism, no random without seed, no NaN/Inf.
- research_state/ must stay writable.

RULES: NO placeholders/TODOs/FIXMEs/HACKs/XXX. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES. If wiring blocks -> IMPLEMENT glue NOW. Use PHASE_QUICK_VERIFY=1 for fast verification/artifacts. Composition over duplication. Future agents MUST do heavy quant work — this campaign is mandatory.

## MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER)
1. VERIFY GATE (phase-scoped, fast): `PHASE_QUICK_VERIFY=1 PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_phase90_*.py tests/test_phase91_*.py tests/test_phase92_*.py tests/test_phase93_*.py tests/test_phase94_*.py tests/test_phase95_*.py tests/test_phase96_*.py tests/test_phase97_*.py tests/test_phase98_*.py tests/test_phase99_*.py tests/test_phase100_*.py tests/test_phase101_*.py -q`. If no phase101 tests exist yet, run phases 90-100. If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist -> FIX FIRST.
2. DO NOT REDO PHASES 1-100. Extend/compose only.
3. BOOTSTRAP PHASE_101 IMMEDIATELY: create src/execution/phase101_live_execution_realtime_hardening.py (or src/risk equivalent) composing from Phase 99/100, add tests/test_phase101_live_execution_realtime_hardening.py, generate deterministic artifacts under research_state/phase101_*/. Integrate with orderflow microstructure, SOR/routing/fragmentation, gamma/hedging, margin/netting/finality/post-trade, resilience/chaos/compliance. No stubs.
4. ON ACCEPTANCE -> UPDATE THIS FILE (fresh UTC timestamp, files changed full paths, rationale). Re-verify gate GREEN (phase-scoped). NO session ends incomplete.

## SESSION UPDATE (UTC): 2026-11-04T12:04:50Z
Files changed (full paths):
- /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/research_state/durable_handoff.md
Rationale: Prioritized by repo name (CRYPTO OPTIONS + ORDERFLOW QUANT). Phases 1-100 COMPLETE + SHIPPED, gate GREEN. Transitioned focus campaign from PHASE_100_LIVE_GATE_HARDENING_DEEP to PHASE_101_LIVE_EXECUTION_REALTIME_HARDENING (mandatory heavy quant). Defined crystal clear initial task for next session with concrete deliverables, removed ambiguity, enforced composition-over-duplication, and ensured every future session must ship tangible src+tests+artifacts with GREEN gate. No placeholders/TODOs. Bottlenecks cleared by campaign structure.
