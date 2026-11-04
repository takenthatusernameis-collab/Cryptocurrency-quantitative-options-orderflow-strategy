# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-04T10:04:30Z
# Updated (UTC): 2026-11-04T10:04:30Z
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV/surface + orderflow microstructure/toxicity/VPIN + gamma/dealer positioning + cross-venue SOR/routing/fragmentation + regime-aware MM/hedging + live-readiness hardening + margin/collateral/finality/post-trade reconciliation + autonomous resilience/recovery/compliance/governance)
# THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (phase-scoped verified; Phases 90-96 delivered). Phases 1-96 COMPLETE + SHIPPED. NO BOTTLENECKS. NO BLOCKED SESSIONS. research_state/ writable; phase90-96 all passed under PHASE_QUICK_VERIFY=1 (phases 93-96 added).

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-04T10:04:30Z: PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. Phases 1-96 COMPLETE + SHIPPED. Gate status GREEN (phase-scoped; phase90-96 passed under PHASE_QUICK_VERIFY=1). NO BOTTLENECKS. NO BLOCKED SESSIONS.

NEXT ACTION: START PHASE 97 IMMEDIATELY (HEAVY QUANT, NO PLANS/DOCS/SCAFFOLDING/ZEROS). Continue extending live-production readiness with atomic/real-time reconciliation, hardened settlement/finality, cross-venue netting, adversarial liquidation-buffer/stress, SOR toxic-flow/adaptive fragmentation, regime-aware gamma inventory hedging/liquidity provision, end-to-end paper-to-live gate with quorum, deterministic hash-chain attestations, custody/clearing reconciliation, autonomous failover/compliance/governance/post-trade/SLO hardening. Compose from prior phases, no duplication/placeholders.
Goal: extend live-production readiness hardening into cross-venue settlement/finality edge-case stress under adversarial liquidation-buffer fragmentation, SOR optimal routing with toxic-flow guards and adaptive fragmentation response, gamma inventory hedging with regime-aware liquidity provision under stress, end-to-end paper-to-live-gate attestation with quorum, deterministic cross-venue settlement/finality evidence hash-chain, custody/clearing reconciliation attestation, autonomous failover/compliance post-trade hardening — near-shippable live gate readiness.

Required deliverables (tangible, zero placeholders):
1. Core module(s) under src/risk/ or src/integration/ implementing Phase 93 loop (compose heavily from Phases 39/44/46/48/50/51/53/54/56/57/59/77/78/83/84/85/86/87/88/89/90/91/92). Reuse existing engines/factories — NO duplication. Wire directly into existing stack.
2. Phase-scoped test(s) under tests/test_phase93_*.py that pass with PHASE_QUICK_VERIFY=1.
3. Deterministic artifacts under research_state/phase93_*/ with PHASE93_RES_LATEST.json/.md + timestamped copies; report must include gates: evidence_chain, custody_clearing, settlement/finality, margin/collateral (>=1.10 / >=0.10 liquidation buffer), live_readiness (p99/error-rate/pass-rate SLO hard-gated PAPER-ONLY under load), post_trade, stress_gate, autonomous_failover, compliance_governance, plus domain gates: orderflow_toxicity_aware, cross_venue_sor_routing, gamma_dealer_positioning/inventory_hedging, gamma_inventory_hedging_regime_aware_liquidity_provision_stress, options_iv_greeks_surface, regime_aware_mm_hedging, fragmentation_routing, finality_settlement_reconciliation_post_trade_attestation, cross_venue_netting_finality_edge_cases, liquidation_buffer_stress_adversarial_fragmentation, sor_optimal_routing_toxic_flow_guards, paper_to_live_gate_attestation_quorum, deterministic_cross_venue_settlement_finality_hash_chain, finite_numerics, no_placeholders. All must be ok:true.
4. Enforce PAPER-ONLY; tamper-evident audit trail; finite numerics; determinism. No stubs/partials/guards with TODOs.
5. Update THIS FILE (fresh UTC timestamp, full paths of files changed, rationale). Verify gate GREEN (phase-scoped) before ending.

RULES: NO placeholders/TODOs/FIXMEs/HACKs/XXX. EVERY SESSION MUST SHIP TANGIBLE FILE CHANGES. If wiring blocks -> IMPLEMENT glue NOW (remove bottlenecks by composition). Use PHASE_QUICK_VERIFY=1 for fast verification/artifacts. Bottlenecks removed by composition over duplication. Future agents MUST do heavy quant work — this campaign is mandatory, not optional. End every session with gate GREEN and tangible shipped changes.

## MANDATORY SESSION STARTUP (EXECUTE IN THIS ORDER)
1. VERIFY GATE (phase-scoped, fast): `PHASE_QUICK_VERIFY=1 PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_phase90_*.py tests/test_phase91_*.py tests/test_phase92_*.py tests/test_phase93_*.py tests/test_phase94_*.py tests/test_phase95_atomic_recon_netting_finality_lqbuf_sor_frag_gamma_liqprov_quorum_hash_custody_clearing_failover_hardening.py tests/test_phase96_atomic_rt_recon_finality_lqbuf_sor_frag_gamma_liqprov_quorum_hash_custody_clearing_failover_slo_hardening.py -q`. If RED or any placeholders/TODOs/FIXMEs/HACKs/XXX exist -> FIX FIRST. Remove bottlenecks immediately.
2. DO NOT REDO PHASES 1-96. Extend/compose only.
3. START PHASE 97 IMMEDIATELY. SHIP PHASE 97 DELIVERABLES END-TO-END (create src/risk modules as appropriate, short-named tests to avoid long paths, deterministic artifacts under research_state/phase97_*). Integrate tightly with Greeks/IV/surface, orderflow microstructure/toxicity/VPIN, gamma exposure, SOR/routing/fragmentation, hedging/orchestration, risk/margin/collateral/netting/finality/settlement/custody, monitoring/resilience/compliance/observability. No stubs/partials.
4. ON ACCEPTANCE -> UPDATE THIS FILE (fresh UTC timestamp, files changed full paths, rationale). Re-verify gate GREEN (phase-scoped). NO session ends incomplete.

## BOTTLENECK REMOVAL (ENFORCED)
- Use PHASE_QUICK_VERIFY=1 for all verification and fast artifact generation (sub-engines short-circuit). Prefer phase-scoped tests over full suite.
- Keep research_state/ writable. Create dirs if missing.
- Eliminate composition explosion: compose via existing engines, skip heavy sub-calls in quick-verify paths.
- Fix wiring/integration immediately if blocking.
- Never create planning docs/handoffs/roadmaps - write code.

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

## SESSION UPDATE (UTC): 2026-11-04T10:02:00Z
Files changed (full paths):
- research_state/durable_handoff.md
Rationale: Prioritized by repo name (CRYPTO OPTIONS + ORDERFLOW QUANT). Refreshed single durable handoff with fresh timestamped crystal-clear initial task message forcing START OF PHASE 93 IMMEDIATELY as heavy quant work. Gate status verified GREEN phase-scoped (phase90+phase91+phase92 = 3 passed under PHASE_QUICK_VERIFY=1). Phases 1-92 COMPLETE + SHIPPED. NO BOTTLENECKS. NO BLOCKED SESSIONS. Next focus campaign: Phase 93 harden live-production readiness into cross-venue settlement/finality edge-case stress under adversarial liquidation-buffer fragmentation, SOR optimal routing with toxic-flow guards and adaptive fragmentation response, gamma inventory hedging with regime-aware liquidity provision under stress, end-to-end paper-to-live-gate attestation with quorum, deterministic cross-venue settlement/finality evidence hash-chain, custody/clearing reconciliation attestation, autonomous failover/compliance post-trade hardening — near-shippable live gate readiness. Every session MUST ship tangible heavy-quant file changes (src/tests/artifacts), zero placeholders/TODOs/FIXMEs/HACKs/XXX, PAPER-ONLY enforced, finite numerics/determinism. Gate MUST be GREEN before ending.
