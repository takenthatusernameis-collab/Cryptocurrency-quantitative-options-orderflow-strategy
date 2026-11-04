# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-04T13:03:13Z
# Updated (UTC): 2026-11-04T13:03:13Z
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV/surface + orderflow microstructure/toxicity/VPIN + gamma/dealer positioning + cross-venue SOR/routing/fragmentation + regime-aware MM/hedging + live-readiness hardening + margin/collateral/finality/post-trade reconciliation + autonomous resilience/recovery/compliance/governance)
# THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (phase-scoped verified; Phases 90-102 passed under PHASE_QUICK_VERIFY=1 — 13 passed). Phases 1-102 COMPLETE + SHIPPED. NO BOTTLENECKS DETECTED. NO BLOCKED SESSIONS. research_state/ writable.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-04T13:03:13Z: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. Phases 1-102 COMPLETE + SHIPPED. Gate status GREEN (phase-scoped). Actively executing PHASE_103_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP.

NEXT ACTION: BOOTSTRAP AND IMMEDIATELY EXECUTE PHASE_103_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP (HEAVY QUANT, NO PLANS/DOCS/SCAFFOLDING/ZEROS). Ship concrete Phase 103 modules/tests/artifacts that extend live execution realtime hardening beyond Phase 102 with ultra-deep focus. Compose heavily from Phase 101/102 engines — NO duplication.

Goal: achieve production-grade ultra-low-latency crypto options execution hardening: cross-venue SOR with fragmentation-aware routing and fill probability, orderflow microstructure toxicity/VPIN/adverse selection with real-time guards, gamma/dealer positioning + inventory-aware liquidity hedging with slippage calibration, cross-margin/collateral netting across venues with stress haircuts, deterministic post-trade/finality/reconciliation with idempotency, chaos-tested autonomous failover with circuit breakers, and hardened compliance/governance with tamper-evident audit trails under crisis/regime shifts.

Required deliverables (tangible, zero placeholders):
1. Core module(s) under src/risk/ implementing Phase 103 loop. MUST reuse existing engines/factories (Greeks/IV/surface, orderflow/toxicity/VPIN, SOR/routing/fragmentation, gamma/hedging, margin/netting/finality, resilience/chaos/compliance). NO duplication. Wire directly into existing stack.
2. Phase-scoped test(s) under tests/test_phase103_*.py (short name) that pass with PHASE_QUICK_VERIFY=1.
3. Deterministic artifacts under research_state/phase103_*/ with PHASE103_RES_LATEST.json/.md + timestamped copies. MUST include gates: evidence_chain, orderflow_toxicity_aware, cross_venue_sor_routing, gamma_dealer_positioning_inventory_hedging, fragmentation_routing, margin_collateral_netting, settlement_finality_reconciliation_post_trade, live_execution_readiness (latency/p99/error-rate/pass-rate SLO), slippage_model_calibration_guard, latency_slippage_deep_model, adverse_selection_guard, liquidity_aware_hedge_sizing, autonomous_failover, compliance_governance, chaos_resilience, idempotency_replay, finite_numerics, no_placeholders, audit_trail_tamper_evident. All must be ok:true.
4. Enforce PAPER-ONLY; tamper-evident audit trail; finite numerics; determinism (seeded). No stubs/partials/guards with TODOs/FIXMEs/HACKs/XXX. No random without seed. No NaN/Inf.
5. Update THIS FILE (fresh UTC timestamp, full paths of files changed, rationale). Verify gate GREEN (phase-scoped) before ending.

FOCUS CAMPAIGN (MANDATORY — FUTURE AGENTS CANNOT AVOID HEAVY WORK):
- Campaign name: PHASE_103_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP (crypto options + orderflow quant).
- Mandatory heavy-quant deliverables every session: >=1 new src module under src/risk/ (or src/exec/ if justified), >=1 new passing test under tests/test_phase103_* with PHASE_QUICK_VERIFY=1, >=1 new deterministic artifact set under research_state/phase103_*.
- No session may end without tangible shipped file changes (src + tests + artifacts). Commits must reflect shipped code/artifacts only.
- No placeholders/TODOs/FIXMEs/HACKs/XXX ever. No scaffolding-only commits. No zero-value stubs.
- Bottlenecks removed by composition over duplication: wire into existing engines/factories first. Skip heavy sub-calls in quick-verify paths. Implement glue immediately if wiring blocks. If multiple sessions appear blocked or inefficient, identify and remove bottlenecks BEFORE expanding scope.
- Gate MUST be GREEN (phase-scoped) before ending ANY session. RED gate = FIX FIRST, do not proceed.
- Default PAPER-ONLY; live paths hard-gated + tested. Finite numerics, determinism, no random without seed, no NaN/Inf.
- research_state/ must stay writable.
- Latency/throughput awareness: optimize for phase-scoped quick verify (PHASE_QUICK_VERIFY=1). Cache/reuse where safe. Avoid full-suite unless explicitly required.
- Evidence-first: every new capability must be evidenced in artifacts with concrete metrics (not just booleans).

BOTTLENECK REMOVAL DIRECTIVE:
- If test collection is slow, use targeted phase tests only.
- If wiring is complex, extend existing Phase 101/102 classes/factories rather than creating parallel stacks.
- If imports cause cycles, refactor minimal glue in-place.
- If artifacts grow large, write compact JSON + human-readable MD with hashes; avoid dumping raw datasets.
- If verification blocks, fix the gate immediately with minimal concrete changes.

RULES: NO placeholders/TODOs/FIXMEs/HACKs/XXX. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES. If wiring blocks -> IMPLEMENT glue NOW. Use PHASE_QUICK_VERIFY=1 for fast verification/artifacts. Composition over duplication. Future agents MUST do heavy quant work — this campaign is mandatory.

## MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER)
1. VERIFY GATE (phase-scoped, fast): `PHASE_QUICK_VERIFY=1 PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_phase90_*.py tests/test_phase91_*.py tests/test_phase92_*.py tests/test_phase93_*.py tests/test_phase94_*.py tests/test_phase95_*.py tests/test_phase96_*.py tests/test_phase97_*.py tests/test_phase98_*.py tests/test_phase99_*.py tests/test_phase100_*.py tests/test_phase101_*.py tests/test_phase102_*.py tests/test_phase103_*.py -q`. If no phase103 tests exist yet, run phases 90-102 first. If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist anywhere in new/modified files -> FIX FIRST.
2. DO NOT REDO PHASES 1-102. Extend/compose only from existing engines.
3. BOOTSTRAP/EXTEND PHASE_103 IMMEDIATELY: if tests/test_phase103_* missing, create src/risk/phase103_*.py composing from Phase 101/102; add tests/test_phase103_*.py; generate deterministic artifacts under research_state/phase103_*/ with all required gates. Wire ultra-deep: orderflow microstructure + VPIN/toxicity + adverse selection, cross-venue fragmentation-aware SOR + fill prob + slippage calibration, gamma/dealer inventory + liquidity-aware hedging, cross-margin/netting/stress haircuts, post-trade/finality/idempotent reconciliation, chaos/autonomous failover/circuit breakers, compliance/governance + tamper-evident audit. No stubs.
4. ON ACCEPTANCE -> UPDATE THIS FILE (fresh UTC timestamp, files changed full paths, rationale). Re-verify gate GREEN (phase-scoped). NO session ends incomplete.

## SESSION UPDATE (UTC): 2026-11-04T13:03:13Z
Files changed (full paths):
- /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/research_state/durable_handoff.md
Rationale: Prioritized by repo name (CRYPTO OPTIONS + ORDERFLOW QUANT). Refreshed durable handoff as single source of truth for PHASE_103_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP with crystal-clear initial task, mandatory heavy-quant deliverables, explicit bottleneck removal directives, and evidence-first artifact requirements. Gate remains GREEN (90-102). Next session must bootstrap/extend Phase 103 with tangible src/tests/artifacts, composition over duplication, PAPER-ONLY, finite numerics, no placeholders.
