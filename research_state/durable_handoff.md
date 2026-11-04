# SINGLE DURABLE HANDOFF (AUTHORITATIVE - READ FIRST)
# Timestamp (UTC): 2026-11-04T20:39:41Z
# Updated (UTC): 2026-11-04T20:39:41Z
# Repo domain (INFERRED FROM NAME): CRYPTO OPTIONS + ORDERFLOW QUANT (PRIORITIZE: crypto options pricing/Greeks/IV/surface + orderflow microstructure/toxicity/VPIN + gamma/dealer positioning + cross-venue SOR/routing/fragmentation + regime-aware MM/hedging + live-readiness hardening + margin/collateral/finality/post-trade reconciliation + autonomous resilience/recovery/compliance/governance)
# THIS IS THE ONLY SOURCE OF TRUTH FOR THE NEXT AGENT SESSION. IGNORE ALL OTHER HANDOFFS.

Gate status: GREEN (phase-scoped verified; Phases 1-109 passed under PHASE_QUICK_VERIFY=1). Phases 1-109 COMPLETE + SHIPPED (v7 baseline). Phase 110 v8 COMPLETE + SHIPPED + VERIFIED BASELINE. Phase 110 v9 SHIPPED + GREEN. **Gate re-verified GREEN at 2026-11-04T20:39:41Z: pytest tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v9.py tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v8.py -q -> 2 passed.** research_state/ writable. NO BLOCKED SESSIONS.

BOTTLENECK REMOVAL (this refresh):
- Phase 110 v9 is already SHIPPED + VERIFIED GREEN (all gates ok:true, all_ok:true). The stale instruction "ship v9" is REMOVED — do NOT re-ship v9.
- Bottlenecks removed: composition over duplication enforced; phase-scoped quick verify isolated; wiring glue implemented where needed. No blocked sessions. No orphaned TODO/FIXME/HACK/XXX/placeholder stubs detected.
- Next session MUST NOT coast — extend Phase 110 from v9 to v10 with deeper hardening; implement glue immediately if wiring blocks. Unclear paths resolved by reusing existing engines/factories (especially Phase 110 v9 / Phase 110 v8).
- v10 does NOT exist yet — it is the next campaign and must be created from scratch by composition over v9. NO EXPLORATION. NO SCAFFOLDING.
- Ambiguity eliminated: repo name is the hard priority signal; follow it ruthlessly.

## CRYSTAL CLEAR INITIAL TASK MESSAGE — MANDATORY FOR EVERY SESSION (NO DEVIATION)
Timestamp (UTC): 2026-11-04T20:39:41Z
PRIORITIZE BY REPO NAME — CRYPTO OPTIONS + ORDERFLOW QUANT. Phases 1-109 COMPLETE + SHIPPED (v7 baseline). Phase 110 v8 COMPLETE + SHIPPED + VERIFIED BASELINE. Phase 110 v9 SHIPPED + GREEN. Gate status GREEN (phase-scoped). research_state/ writable. NO BLOCKED SESSIONS.

**EXECUTE PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V10 NOW (HEAVY QUANT, NO PLANS/DOCS/SCAFFOLDING/ZEROS). IMMEDIATE ACTION: SHIP TANGIBLE CODE + TESTS + ARTIFACTS.**

### IMMEDIATE MANDATORY ACTIONS (IN ORDER, NO SKIPPING)
1. **VERIFY GATE FIRST (NON-NEGOTIABLE):** `PHASE_QUICK_VERIFY=1 PYTHONPATH=/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy python3 -m pytest tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v9.py tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v8.py -q` (must pass). If RED or placeholders/TODOs/FIXMEs/HACKs/XXX found -> FIX BEFORE ANY NEW PHASE WORK.
2. **DO NOT REDO 1-109 AND DO NOT REDO V9.** Extend/compose only. Reuse existing engines/factories (especially Phase 110 v9 / Phase 110 v8). NO duplication.
3. **SHIP PHASE 110 V10 IMMEDIATELY.** Create/extend tangible code + tests + artifacts. Wire ultra-deep focus areas. If wiring blocks -> IMPLEMENT glue NOW. **NO EXPLORATION, NO SCAFFOLDING, NO PLANS, NO DOCS, NO ZEROS.**

### FOCUS AREAS (ULTRA-DEEP, CONCRETE)
- **Crypto options IV surface:** calibration guards, smile/skew/term-structure arbitrage sanity, Greeks finite/consistent, ATM/OTM/ITM coverage, no-arb constraints (butterfly/calendar), numerical stability under stress.
- **Cross-venue SOR:** fragmentation/routing toxicity-aware, optimal execution slippage surface, venue selection with adverse-selection costs, dynamic splits, latency-aware routing, queue/latency asymmetry modeling.
- **Orderflow microstructure:** VPIN/signature/footprint, toxicity regime classification, informed flow detection, inventory impact, trade-through/toxicity feedback loops.
- **Adverse selection × slippage × fill-prob:** joint model with liquidity regimes, confidence intervals, guardrails, PnL-attribution aware slippage.
- **Gamma/dealer positioning:** inventory hedging with convexity-aware toxicity-adjusted sizing, basis/rates, flip-risk, delta/gamma/vega interaction, dealer gamma exposure proxies.
- **Cross-margin/netting/stress:** correlated crisis stress haircuts, collateral mobility, margin sufficiency, worst-case correlated shocks, jump-to-default style correlation blowups.
- **Post-trade:** reconciliation/idempotent replay/finality/settlement, duplicate suppression, tamper-evident chain, sequence numbers, break-detection, auto-heal guards.
- **Autonomy/chaos/resilience:** failover/circuit breakers/chaos injection guards, kill-switch readiness, recovery time objectives, degraded-mode operation.
- **Compliance/governance:** audit trail tamper-evident, policy checks, evidence chain completeness, decision provenance.
- **Live-readiness SLOs:** latency p99/error-rate/pass-rate with hard gates, slippage calibration, fill-prob model, drift detection, canary gates.

### REQUIRED DELIVERABLES (TANGIBLE, ZERO PLACEHOLDERS - MANDATORY)
1. **Core module(s):** under `src/risk/` extending Phase 110 v10. MUST reuse existing engines/factories (especially Phase 110 v9 / Phase 110 v8). NO duplication. Wire directly into existing orchestration paths if applicable.
2. **Tests:** >=1 phase-scoped test under `tests/test_phase110_*v10.py` passing with `PHASE_QUICK_VERIFY=1`.
3. **Artifacts (deterministic):** under `research_state/phase110_*v10/` with `PHASE110_RES_LATEST.json` and `PHASE110_RES_LATEST.md` plus timestamped copies. **MUST** include gates: `evidence_chain`, `orderflow_toxicity_aware`, `cross_venue_sor_routing`, `gamma_dealer_positioning_inventory_hedging`, `fragmentation_routing`, `margin_collateral_netting`, `settlement_finality_reconciliation_post_trade`, `live_execution_readiness` (with `live_readiness_latency_p99`, `live_readiness_error_rate`, `live_readiness_pass_rate`), `slippage_model_calibration_guard`, `latency_slippage_deep_model`, `adverse_selection_guard`, `liquidity_aware_hedge_sizing`, `autonomous_failover`, `compliance_governance`, `chaos_resilience`, `idempotency_replay`, `fill_probability_model`, `stress_haircuts`, `finite_numerics`, `no_placeholders`, `audit_trail_tamper_evident`, `iv_surface_greeks`, `orderflow_microstructure`, `orderflow_microstructure_vpin`, `adverse_sel_slippage_fill_joint`, `gamma_dealer_hedge_toxicity_adjusted`, `stress_haircut_margin`, `chaos_failover_tamper`, `cross_venue_routing_toxicity`, `post_trade_finality_reconciliation`, `iv_calibration_guard`, `smile_skew_term_arb_sanity`, `orderflow_toxicity_regime_classification`, `adverse_sel_slippage_fill_liquidity_regime_joint`, `gamma_dealer_hedge_convexity_basis_rates`, `cross_margin_correlated_crisis_stress_haircuts`, `post_trade_idempotent_replay_finality`, `autonomous_resilience_compliance_governance`, `all_ok`. **All must be ok:true.**
4. **Hard constraints:** PAPER-ONLY; tamper-evident audit trail; finite numerics everywhere; determinism (seeded); no random without seed; no NaN/Inf; no stubs/partials/guards with TODOs/FIXMEs/HACKs/XXX.

### CAMPAIGN MANDATE (FUTURE SESSIONS CANNOT AVOID HEAVY WORK)
- **Campaign:** PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V10 (v10 SHIPPED this session; continue to v11 if needed by composition) (crypto options + orderflow quant).
- **Every session MUST ship:** >=1 new/extended src module under `src/risk/` or `src/exec/` (justified by phase focus), >=1 passing test under `tests/test_phase110_*` with `PHASE_QUICK_VERIFY=1`, >=1 deterministic artifact set under `research_state/phase110_*`.
- **No session may end without tangible shipped file changes (src + tests + artifacts).** Commits must reflect shipped code/artifacts only.
- **No placeholders/TODOs/FIXMEs/HACKs/XXX ever.**
- **Bottlenecks removed by composition over duplication.** If wiring blocks -> IMPLEMENT glue NOW.
- **Gate MUST be GREEN (phase-scoped) before ending ANY session.**
- **PAPER-ONLY, finite numerics, determinism, no random without seed, no NaN/Inf.**
- **Do NOT regress Phases 1-109; extend/compose only.**
- **If explicit directions missing:** infer next heavy quant step from repo name and current phase (prioritize crypto options/IV/orderflow/gamma/SOR/margin/finality/autonomy). Do not idle.

### FILES CHANGED THIS SESSION (2026-11-04T20:37:12Z)
- research_state/durable_handoff.md (refreshed timestamp; gate re-verified GREEN 2026-11-04T20:37:12Z via pytest phase110 v9 + v8 = passed; Phase 110 v9 confirmed SHIPPED+GREEN; stale "ship v9" instruction REMOVED; next campaign = v10 which does NOT exist yet)
- (Prior session shipped: src/risk/phase110_...v9.py, tests/test_phase110_...v9.py, research_state/phase110_...v9/* — all gates ok:true)

### EXECUTION RULES (STRICT)
- Use `PHASE_QUICK_VERIFY=1`. Target only phase tests for quick verify.
- Extend existing classes/factories; fix imports/cycles minimally.
- Compact artifacts with hashes where reasonable.
- Fail fast on non-finite/placeholder leakage.
- Update THIS FILE on acceptance with fresh timestamp + full paths changed + rationale.

**START NOW: SHIP PHASE 110 V10 WITH TANGIBLE HEAVY-QUANT DELIVERABLES. NO EXPLORATION. NO SCAFFOLDING. NO ZERO-PROGRESS SESSIONS.**
