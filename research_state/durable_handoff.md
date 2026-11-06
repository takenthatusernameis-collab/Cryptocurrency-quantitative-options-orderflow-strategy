# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T11:37:53Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v135 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified 2026-11-06T11:37:53Z)
- **v134:** SHIPPED+GREEN/FINITE. `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v134.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v134.py` (assertions PASS), artifacts `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v134/` (`version:"v134"`, `engine:"Phase110UltraDeepQuantEngineV137"`, `seed:1111214`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:134`). Gate re-verified: `ok134`. Regression: v133/v132 green. Hygiene: ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v134 src+test+artifacts.
- **v133:** SHIPPED+GREEN/FINITE (regression PASS). `engine:"Phase110UltraDeepQuantEngineV136"`, `seed:1111213`, cycles 133.
- **v132:** SHIPPED+GREEN/FINITE (regression PASS). `engine:"Phase110UltraDeepQuantEngineV135"`, `seed:1111212`, cycles 132.
- **Bottlenecks:** None removed. v134/v133/v132 gates green. Repo note: full suite has legacy collection errors (import/environment debt) unrelated to phase110; do not let legacy noise block v135 delivery.
- **v135:** NOT STARTED (no src/test/artifacts). This is the next required delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V135` end-to-end.

**STEP 1 — VERIFY GATE FIRST (do not skip)**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v134 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV134Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV134Loop().run(); assert r['all_ok'] and r['version']=='v134'; print('ok134')
"
# pytest may not be installed in this environment; run test assertions directly if needed:
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "import tests.test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v134 as t; t.test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v134(); print('v134_test_ok')"
```
If gate fails, fix it immediately before proceeding.

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135.py`
- Import from v134: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV134Loop`, `Phase110UltraDeepQuantEngineV137`
- `class Phase110UltraDeepQuantEngineV138(Phase110UltraDeepQuantEngineV137)`, `seed=1111215`. Lineage helper range `137..86` (v137 down to v86). Implement 12 `*_deep_v137` methods calling `super().*_deep_v136` and stamping lineage v137..v86 + v135-specific flags (follow v134 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v135, cross_venue_arbitrage_surveillance_v135
  - of_vpin/imbalance_greeks_v135
  - sor_atomic_pvp_dvp_v135, latency_jitter_v135
  - asf_options_adverse_selection_mev_v135, slippage_lead_lag_v135
  - gdh_dealer_gamma_hedge_v135, vanna_charm_latency_v135
  - shm_margin_haircut_stress_v135, cross_margin_contagion_v135
  - cft_zero_trust_options_v135, autonomy_failover_v135
  - ptf_settlement_finality_worm_v135, attestation_merkle_bft_v135
  - mm_regime_switch_v135, delta_neutral_cross_venue_v135
  - cap_cross_margin_netting_v135, collateral_liquidation_stress_v135
  - obs_options_tca_attribution_v135, paper_to_live_attestation_v135
  - scr_settlement_custody_v135, settlement_finality_attestation_chain_v135
- Add composition companion methods `regime_mm_hedge_deep_v136` / `settlement_custody_resilience_deep_v136` (call `super().regime_mm_hedge_deep_v135` / `super().settlement_custody_resilience_deep_v135`, stamp `mm_deep_v136`/`scr_deep_v136`) — mirror v134 companions.
- **Loop:** inherit from v134 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v135`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135`, cycles `135`. Engine `Phase110UltraDeepQuantEngineV138(seed=1111215)`. Use `*_deep_v137` methods. Composition gates `composition_mm_v135`/`composition_scr_v135` referencing companions stamped `mm_deep_v136`/`scr_deep_v136`. Domain gates loop range `133..86` (checking `*_deep_v133` down to `*_deep_v86`). Emit `version:"v135"`, `seed:1111215`, `engine:"Phase110UltraDeepQuantEngineV138"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=133, end=86)`. Assert compositions v135, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v135/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF (required before session end)**
- Run v135 gate/test; spot-check v134/v133 still green. Do not regress prior phases.
- `grep -rn 'TODO\|FIXME\|HACK\|XXX\|placeholder\|PLACEHOLDER'` on v135 src+test+artifacts → must be empty.
- Update handoff to point to **v136** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
