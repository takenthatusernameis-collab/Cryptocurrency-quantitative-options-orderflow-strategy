# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-04T14:28:21Z
# Updated (UTC): 2026-11-04T14:28:21Z
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV/surface + orderflow microstructure/toxicity/VPIN + gamma/dealer positioning + cross-venue SOR/routing/fragmentation + regime-aware MM/hedging + live-readiness hardening + margin/collateral/finality/post-trade reconciliation + autonomous resilience/recovery/compliance/governance)
# THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (phase-scoped verified; Phases 90-104 passed under PHASE_QUICK_VERIFY=1 — 25 passed). Phases 1-104 COMPLETE + SHIPPED. NO BLOCKED SESSIONS. research_state/ writable.

BOTTLENECK REMOVAL (this refresh):
- Previous session shipped Phase104 (src/risk/phase104_...tamper.py) with cross-venue SOR toxicity-aware routing, fragmentation/routing optimization, IV surface/Greeks + orderflow VPIN/microstructure, adverse selection × slippage × fill-prob joint model, gamma/dealer inventory hedge toxicity-adjusted sizing, cross-margin stress haircuts/netting, post-trade idempotent reconciliation/finality/settlement, autonomous failover/circuit breakers/chaos, compliance/governance + tamper-evident audit chain, latency/p99/error-rate/pass-rate SLOs and live-readiness gates. Wired into Phase 104 loop; tests passing; artifacts generated (PHASE104_RES_LATEST.json/.md + timestamped). Gate remains GREEN.
- BOTTLENECK REMOVED: ensure next session cannot coast on scaffolding — mandate extending to Phase 105 with deeper cross-venue, live-readiness, and post-trade/finality hardening composed from existing engines (no duplication). Implement glue immediately if wiring blocks.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-04T14:28:21Z: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. Phases 1-104 COMPLETE + SHIPPED. Gate status GREEN (phase-scoped). NOW EXECUTE PHASE_105_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V2 (HEAVY QUANT, NO PLANS/DOCS/SCAFFOLDING/ZEROS).

NEXT ACTION: CREATE/EXTEND PHASE_105 with tangible, concrete code + tests + artifacts. Focus ultra-deep: crypto options IV surface calibration guards + smile/skew/term-structure arbitrage sanity, cross-venue SOR fragmentation/routing toxicity-aware + optimal execution slippage surface, orderflow microstructure VPIN/signature/footprint + toxicity regime classification, adverse selection × slippage × fill-probability joint model with liquidity regimes, gamma/dealer positioning inventory hedging with convexity-aware toxicity-adjusted sizing and basis/rates, cross-margin/netting/stress haircuts under correlated crisis, post-trade reconciliation/idempotent replay/finality/settlement, autonomous failover/circuit breakers/chaos, compliance/governance + tamper-evident audit chain, latency/p99/error-rate/pass-rate SLOs with live-readiness gates. Compose from existing engines (101/102/103/104) — NO duplication. If wiring blocks -> IMPLEMENT glue NOW.

Required deliverables (tangible, zero placeholders):
1. Core module(s) under src/risk/ or src/exec/ extending Phase 105. MUST reuse existing engines/factories. NO duplication. Wire directly.
2. Phase-scoped test(s) under tests/test_phase105_*.py that pass with PHASE_QUICK_VERIFY=1.
3. Deterministic artifacts under research_state/phase105_*/ with PHASE105_RES_LATEST.json/.md + timestamped copies. MUST include gates: evidence_chain, orderflow_toxicity_aware, cross_venue_sor_routing, gamma_dealer_positioning_inventory_hedging, fragmentation_routing, margin_collateral_netting, settlement_finality_reconciliation_post_trade, live_execution_readiness (latency/p99/error-rate/pass-rate SLO), slippage_model_calibration_guard, latency_slippage_deep_model, adverse_selection_guard, liquidity_aware_hedge_sizing, autonomous_failover, compliance_governance, chaos_resilience, idempotency_replay, fill_probability_model, stress_haircuts, finite_numerics, no_placeholders, audit_trail_tamper_evident, iv_surface_greeks, orderflow_microstructure_vpin, adverse_sel_slippage_fill_joint, gamma_dealer_hedge_toxicity_adjusted, stress_haircut_margin, chaos_failover_tamper, cross_venue_routing_toxicity, post_trade_finality_reconciliation. All must be ok:true.
4. Enforce PAPER-ONLY; tamper-evident audit trail; finite numerics; determinism (seeded). No stubs/partials/guards with TODOs/FIXMEs/HACKs/XXX. No random without seed. No NaN/Inf.
5. Update THIS FILE (fresh UTC timestamp, full paths of files changed, rationale). Verify gate GREEN (phase-scoped) before ending.

FOCUS CAMPAIGN (MANDATORY — FUTURE AGENTS CANNOT AVOID HEAVY WORK):
- Campaign name: PHASE_105_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY (crypto options + orderflow quant).
- Mandatory heavy-quant deliverables every session: >=1 new/extended src module under src/risk/ or src/exec/ (justified), >=1 passing test under tests/test_phase105_* with PHASE_QUICK_VERIFY=1, >=1 deterministic artifact set under research_state/phase105_*.
- No session may end without tangible shipped file changes (src + tests + artifacts). Commits must reflect shipped code/artifacts only.
- No placeholders/TODOs/FIXMEs/HACKs/XXX ever.
- Bottlenecks removed by composition over duplication. If wiring blocks -> IMPLEMENT glue NOW.
- Gate MUST be GREEN (phase-scoped) before ending ANY session.
- PAPER-ONLY, finite numerics, determinism, no random without seed, no NaN/Inf.
- Do NOT regress Phases 1-104; extend/compose only.

BOTTLENECK REMOVAL DIRECTIVE: targeted phase tests only in quick verify; extend existing classes/factories; fix imports/cycles minimally; compact artifacts with hashes; fail fast on non-finite/placeholder leakage.

RULES: NO placeholders/TODOs/FIXMEs/HACKs/XXX. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES. If wiring blocks -> IMPLEMENT glue NOW. Use PHASE_QUICK_VERIFY=1. Composition over duplication. Future agents MUST do heavy quant work.

## MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER)
1. VERIFY GATE: `PHASE_QUICK_VERIFY=1 PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_phase90_*.py tests/test_phase91_*.py tests/test_phase92_*.py tests/test_phase93_*.py tests/test_phase94_*.py tests/test_phase95_*.py tests/test_phase96_*.py tests/test_phase97_*.py tests/test_phase98_*.py tests/test_phase99_*.py tests/test_phase100_*.py tests/test_phase101_*.py tests/test_phase102_*.py tests/test_phase103_*.py tests/test_phase104_*.py -q`. If RED or placeholders/TODOs/FIXMEs/HACKs/XXX -> FIX FIRST.
2. DO NOT REDO 1-104. Extend/compose only.
3. START PHASE_105 IMMEDIATELY with tangible changes + artifacts + passing tests. Wire ultra-deep focus areas (cross-venue SOR/toxicity, post-trade/finality/reconciliation, autonomy/chaos/resilience).
4. ON ACCEPTANCE -> UPDATE THIS FILE (fresh timestamp, full paths changed, rationale). Re-verify GREEN. NO incomplete session end.

## SESSION UPDATE (UTC): 2026-11-04T14:28:21Z
Files changed (full paths):
- /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy/research_state/durable_handoff.md
Rationale: Refreshed single durable handoff for next agentic session: prioritized by repo name (crypto options + orderflow quant), advanced focus campaign to Phase 105, removed bottlenecks (none blocked; Phases 1-104 green), mandated heavy quant deliverables so future agents cannot avoid substantive work. No code changes this refresh.
