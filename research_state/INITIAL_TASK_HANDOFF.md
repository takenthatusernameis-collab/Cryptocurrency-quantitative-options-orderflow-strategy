# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T07:46:00Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v117 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified)
- **v116:** SHIPPED+GREEN/FINITE. `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v116.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v116.py`, artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v116/` (`version:"v116"`, `engine:Phase110UltraDeepQuantEngineV119`, `seed:1111196`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:116`). v116 hygiene CLEAN (0 forbidden tokens).
- **v115:** SHIPPED+GREEN/FINITE (`version:"v115"`, `engine:Phase110UltraDeepQuantEngineV118`, `seed:1111195`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:115`).
- **Gate:** v116 green; v82–v115 regression spot-checked green.
- **Bottlenecks/blocked:** None. Fix any blocker immediately as part of v117 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in new src/test/artifacts.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V117` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
# quick smoke
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v116 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV116Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV116Loop().run(); assert r['all_ok'] and r['version']=='v116'; print('ok116')
"
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v117.py`
- Import from v116: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV116Loop`, `Phase110UltraDeepQuantEngineV119`
- `class Phase110UltraDeepQuantEngineV120(Phase110UltraDeepQuantEngineV119)`, `seed=1111197`. Implement 12 `*_deep_v119` methods calling `super().*_deep_v118` and stamping lineage v119..v82 + v117-specific flags:
  - iv_surface/options_orderflow_lead_lag_v117, cross_venue_arbitrage_surveillance_v117
  - of_vpin/imbalance_greeks_v117
  - sor_atomic_pvp_dvp_v117, latency_jitter_v117
  - asf_options_adverse_selection_mev_v117, slippage_lead_lag_v117
  - gdh_dealer_gamma_hedge_v117, vanna_charm_latency_v117
  - shm_margin_haircut_stress_v117, cross_margin_contagion_v117
  - cft_zero_trust_options_v117, autonomy_failover_v117
  - ptf_settlement_finality_worm_v117, attestation_merkle_bft_v117
  - mm_regime_switch_v117, delta_neutral_cross_venue_v117
  - cap_cross_margin_netting_v117, collateral_liquidation_stress_v117
  - obs_options_tca_attribution_v117, paper_to_live_attestation_v117
  - scr_settlement_custody_v117, settlement_finality_attestation_chain_v117
- **Loop:** inherit from v116 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v117`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v117`, cycles `117`. Engine `Phase110UltraDeepQuantEngineV120(seed=1111197)`. Use `*_deep_v119` methods. Composition gates `composition_mm_v117`/`composition_scr_v117` referencing companions stamped `mm_deep_v117`/`scr_deep_v117`. Emit `version:"v117"`, `seed:1111197`, `engine:"Phase110UltraDeepQuantEngineV120"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module aliases at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v117.py` (PHASE_QUICK_VERIFY=1). Assert gates up to v117 + compositions v117, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v117/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Re-run v82–v117 phase-scoped. All green.
- Grep for forbidden tokens on v117 src+test → empty.
- Update handoff to point to **v118** and sync `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.

(End of file - total 55 lines)