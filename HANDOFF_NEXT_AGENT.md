# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T12:30:22Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v136 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified 2026-11-06T12:30:22Z)
- **v135:** SHIPPED+GREEN/FINITE. `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135.py` (assertions PASS), artifacts `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135/` (`version:"v135"`, `engine:"Phase110UltraDeepQuantEngineV138"`, `seed:1111215`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:135`). Gate re-verified: `ok135`. Regression: v134/v133 green. Hygiene: ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v135 src+test+artifacts.
- **v134:** SHIPPED+GREEN/FINITE (regression PASS). `engine:"Phase110UltraDeepQuantEngineV137"`, `seed:1111214`, cycles 134.
- **v133:** SHIPPED+GREEN/FINITE (regression PASS). `engine:"Phase110UltraDeepQuantEngineV136"`, `seed:1111213`, cycles 133.
- **Bottlenecks:** None removed. v135/v134/v133 gates green. Repo note: full suite has legacy collection errors (import/environment debt) unrelated to phase110; do not let legacy noise block v136 delivery.
- **v136:** NOT STARTED (no src/test/artifacts). This is the next required delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V136` end-to-end.

**STEP 1 — VERIFY GATE FIRST (do not skip)**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV135Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV135Loop().run(); assert r['all_ok'] and r['version']=='v135'; print('ok135')
"
# pytest may not be installed in this environment; run test assertions directly if needed:
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "import tests.test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135 as t; t.test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135(); print('v135_test_ok')"
```
If gate fails, fix it immediately before proceeding.

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v136.py`
- Import from v135: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV135Loop`, `Phase110UltraDeepQuantEngineV138`
- `class Phase110UltraDeepQuantEngineV139(Phase110UltraDeepQuantEngineV138)`, `seed=1111216`. Lineage helper range `138..87` (v138 down to v87). Implement 12 `*_deep_v138` methods calling `super().*_deep_v137` and stamping lineage v138..v87 + v136-specific flags (follow v135 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v136, cross_venue_arbitrage_surveillance_v136
  - of_vpin/imbalance_greeks_v136
  - sor_atomic_pvp_dvp_v136, latency_jitter_v136
  - asf_options_adverse_selection_mev_v136, slippage_lead_lag_v136
  - gdh_dealer_gamma_hedge_v136, vanna_charm_latency_v136
  - shm_margin_haircut_stress_v136, cross_margin_contagion_v136
  - cft_zero_trust_options_v136, autonomy_failover_v136
  - ptf_settlement_finality_worm_v136, attestation_merkle_bft_v136
  - mm_regime_switch_v136, delta_neutral_cross_venue_v136
  - cap_cross_margin_netting_v136, collateral_liquidation_stress_v136
  - obs_options_tca_attribution_v136, paper_to_live_attestation_v136
  - scr_settlement_custody_v136, settlement_finality_attestation_chain_v136
- Add composition companion methods `regime_mm_hedge_deep_v137` / `settlement_custody_resilience_deep_v137` (call `super().regime_mm_hedge_deep_v136` / `super().settlement_custody_resilience_deep_v136`, stamp `mm_deep_v137`/`scr_deep_v137`) — mirror v135 companions.
- **Loop:** inherit from v135 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v136`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v136`, cycles `136`. Engine `Phase110UltraDeepQuantEngineV139(seed=1111216)`. Use `*_deep_v138` methods. Composition gates `composition_mm_v136`/`composition_scr_v136` referencing companions stamped `mm_deep_v137`/`scr_deep_v137`. Domain gates loop range `134..87` (checking `*_deep_v134` down to `*_deep_v87`). Emit `version:"v136"`, `seed:1111216`, `engine:"Phase110UltraDeepQuantEngineV139"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v136.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=134, end=87)`. Assert compositions v136, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v136/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF (required before session end)**
- Run v136 gate/test; spot-check v135/v134 still green. Do not regress prior phases.
- `grep -rn 'TODO\|FIXME\|HACK\|XXX\|placeholder\|PLACEHOLDER'` on v136 src+test+artifacts → must be empty.
- Update handoff to point to **v137** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
