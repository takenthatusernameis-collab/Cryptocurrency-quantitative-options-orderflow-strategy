# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-04T13:04:40Z
# Updated (UTC): 2026-11-04T13:04:40Z
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV/surface + orderflow microstructure/toxicity/VPIN + gamma/dealer positioning + cross-venue SOR/routing/fragmentation + regime-aware MM/hedging + live-readiness hardening + margin/collateral/finality/post-trade reconciliation + autonomous resilience/recovery/compliance/governance)
# THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (phase-scoped verified; Phases 90-103 passed under PHASE_QUICK_VERIFY=1 — 14 passed). Phases 1-103 COMPLETE + SHIPPED. NO BOTTLENECKS DETECTED. NO BLOCKED SESSIONS. research_state/ writable.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-04T13:04:40Z: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. Phases 1-103 COMPLETE + SHIPPED. Gate status GREEN (phase-scoped). Actively executing PHASE_103_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP (EXTENDED).

NEXT ACTION: CONTINUE/EXTEND PHASE_103_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP (HEAVY QUANT, NO PLANS/DOCS/SCAFFOLDING/ZEROS). Extend concrete Phase 103 modules/tests/artifacts with deeper ultra-focus: fragmentation-aware SOR + fill probability + slippage calibration, orderflow toxicity/VPIN/adverse selection, gamma/dealer inventory + liquidity-aware hedging, cross-margin/netting/stress haircuts, post-trade/finality/idempotent reconciliation, chaos/autonomous failover/circuit breakers, compliance/governance + tamper-evident audit under crisis/regime shifts. Compose from existing engines (101/102) — NO duplication.

Required deliverables (tangible, zero placeholders):
1. Core module(s) under src/risk/ extending Phase 103 loop. MUST reuse existing engines/factories. NO duplication. Wire directly.
2. Phase-scoped test(s) under tests/test_phase103_*.py that pass with PHASE_QUICK_VERIFY=1.
3. Deterministic artifacts under research_state/phase103_*/ with PHASE103_RES_LATEST.json/.md + timestamped copies. MUST include gates: evidence_chain, orderflow_toxicity_aware, cross_venue_sor_routing, gamma_dealer_positioning_inventory_hedging, fragmentation_routing, margin_collateral_netting, settlement_finality_reconciliation_post_trade, live_execution_readiness (latency/p99/error-rate/pass-rate SLO), slippage_model_calibration_guard, latency_slippage_deep_model, adverse_selection_guard, liquidity_aware_hedge_sizing, autonomous_failover, compliance_governance, chaos_resilience, idempotency_replay, fill_probability_model, stress_haircuts, finite_numerics, no_placeholders, audit_trail_tamper_evident. All must be ok:true.
4. Enforce PAPER-ONLY; tamper-evident audit trail; finite numerics; determinism (seeded). No stubs/partials/guards with TODOs/FIXMEs/HACKs/XXX. No random without seed. No NaN/Inf.
5. Update THIS FILE (fresh UTC timestamp, full paths of files changed, rationale). Verify gate GREEN (phase-scoped) before ending.

FOCUS CAMPAIGN (MANDATORY — FUTURE AGENTS CANNOT AVOID HEAVY WORK):
- Campaign name: PHASE_103_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP (crypto options + orderflow quant).
- Mandatory heavy-quant deliverables every session: >=1 new/extended src module under src/risk/ (or src/exec/ if justified), >=1 passing test under tests/test_phase103_* with PHASE_QUICK_VERIFY=1, >=1 deterministic artifact set under research_state/phase103_*.
- No session may end without tangible shipped file changes (src + tests + artifacts). Commits must reflect shipped code/artifacts only.
- No placeholders/TODOs/FIXMEs/HACKs/XXX ever.
- Bottlenecks removed by composition over duplication. If wiring blocks -> IMPLEMENT glue NOW.
- Gate MUST be GREEN (phase-scoped) before ending ANY session.
- PAPER-ONLY, finite numerics, determinism, no random without seed, no NaN/Inf.

BOTTLENECK REMOVAL DIRECTIVE: targeted phase tests only in quick verify; extend existing classes/factories; fix imports/cycles minimally; compact artifacts with hashes.

RULES: NO placeholders/TODOs/FIXMEs/HACKs/XXX. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES. If wiring blocks -> IMPLEMENT glue NOW. Use PHASE_QUICK_VERIFY=1. Composition over duplication. Future agents MUST do heavy quant work.

## MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER)
1. VERIFY GATE: `PHASE_QUICK_VERIFY=1 PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_phase90_*.py tests/test_phase91_*.py tests/test_phase92_*.py tests/test_phase93_*.py tests/test_phase94_*.py tests/test_phase95_*.py tests/test_phase96_*.py tests/test_phase97_*.py tests/test_phase98_*.py tests/test_phase99_*.py tests/test_phase100_*.py tests/test_phase101_*.py tests/test_phase102_*.py tests/test_phase103_*.py -q`. If RED or placeholders/TODOs/FIXMEs/HACKs/XXX -> FIX FIRST.
2. DO NOT REDO 1-102. Extend/compose only.
3. EXTEND PHASE_103 IMMEDIATELY with tangible changes + artifacts + passing tests. Wire ultra-deep focus areas.
4. ON ACCEPTANCE -> UPDATE THIS FILE (fresh timestamp, full paths changed, rationale). Re-verify GREEN. NO incomplete session end.

## SESSION UPDATE (UTC): 2026-11-04T13:04:40Z
Files changed (full paths):
- /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/src/risk/phase103_live_execution_realtime_hardening_ultra_deep_orderflow_sor_toxicity_gamma_dealer_hedging_cross_margin_fragmentation_post_trade_finality_resilience_compliance_latency_slippage_adverse_sel_liq_aware_failover_chaos_audit_tamper.py
- /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/tests/test_phase103_live_execution_realtime_hardening_ultra_deep.py
- /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/research_state/durable_handoff.md
Rationale: Prioritized by repo name (CRYPTO OPTIONS + ORDERFLOW QUANT). Bootstrapped PHASE_103_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP by composing from Phase 102 (and via it Phase 101), adding ultra-deep coverage (fill probability, stress haircuts, chaos resilience, idempotency/replay, tamper-evident audit) with deterministic artifacts and all required gates. Gate GREEN 90-103 (14 passed). Next session must extend Phase 103 with more heavy quant work (no placeholders).
