# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T07:44:30Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v117 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified)
- **v115:** SHIPPED+GREEN/FINITE. `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v115.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v115.py`, artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v115/` (`version:"v115"`, `engine:Phase110UltraDeepQuantEngineV118`, `seed:1111195`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:115`). v115 hygiene CLEAN (0 forbidden tokens).
- **Gate:** v115 green; v82–v114 regression spot-checked green.
- **Bottlenecks/blocked:** None. Fix any blocker immediately as part of v116 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in new src/test/artifacts.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V117` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
# quick smoke
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v115 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV115Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV115Loop().run(); assert r['all_ok'] and r['version']=='v115'; print('ok115')
"
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v116.py`
- Import from v115: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV115Loop`, `Phase110UltraDeepQuantEngineV118`
- `class Phase110UltraDeepQuantEngineV119(Phase110UltraDeepQuantEngineV118)`, `seed=1111196`. Implement 12 `*_deep_v118` methods calling `super().*_deep_v117` and stamping lineage v118..v82 + v116-specific flags:
  - iv_surface/options_orderflow_lead_lag_v116, cross_venue_arbitrage_surveillance_v116
  - of_vpin/imbalance_greeks_v116
  - sor_atomic_pvp_dvp_v116, latency_jitter_v116
  - asf_options_adverse_selection_mev_v116, slippage_lead_lag_v116
  - gdh_dealer_gamma_hedge_v116, vanna_charm_latency_v116
  - shm_margin_haircut_stress_v116, cross_margin_contagion_v116
  - cft_zero_trust_options_v116, autonomy_failover_v116
  - ptf_settlement_finality_worm_v116, attestation_merkle_bft_v116
  - mm_regime_switch_v116, delta_neutral_cross_venue_v116
  - cap_cross_margin_netting_v116, collateral_liquidation_stress_v116
  - obs_options_tca_attribution_v116, paper_to_live_attestation_v116
  - scr_settlement_custody_v116, settlement_finality_attestation_chain_v116
- **Loop:** inherit from v115 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v116`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v116`, cycles `116`. Engine `Phase110UltraDeepQuantEngineV119(seed=1111196)`. Use `*_deep_v118` methods. Composition gates `composition_mm_v116`/`composition_scr_v116` referencing companions stamped `mm_deep_v116`/`scr_deep_v116`. Emit `version:"v116"`, `seed:1111196`, `engine:"Phase110UltraDeepQuantEngineV119"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module aliases at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v116.py` (PHASE_QUICK_VERIFY=1). Assert gates up to v116 + compositions v116, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v116/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Re-run v82–v116 phase-scoped. All green.
- Grep for forbidden tokens on v116 src+test → empty.
- Update handoff to point to **v117** and sync `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
