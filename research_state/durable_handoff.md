# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T07:50:00Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v118 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified)
- **v117:** SHIPPED+GREEN/FINITE. `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v117.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v117.py`, artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v117/` (`version:"v117"`, `engine:Phase110UltraDeepQuantEngineV120`, `seed:1111197`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:117`). v117 hygiene CLEAN (0 forbidden tokens).
- **v116:** SHIPPED+GREEN/FINITE (`version:"v116"`, `engine:Phase110UltraDeepQuantEngineV119`, `seed:1111196`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:116`).
- **Gate:** v117 green; v82–v116 regression spot-checked green.
- **Bottlenecks/blocked:** None. Fix any blocker immediately as part of v118 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in new src/test/artifacts.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V118` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
# quick smoke
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v117 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV117Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV117Loop().run(); assert r['all_ok'] and r['version']=='v117'; print('ok117')
"
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v118.py`
- Import from v117: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV117Loop`, `Phase110UltraDeepQuantEngineV120`
- `class Phase110UltraDeepQuantEngineV121(Phase110UltraDeepQuantEngineV120)`, `seed=1111198`. Implement 12 `*_deep_v120` methods calling `super().*_deep_v119` and stamping lineage v120..v82 + v118-specific flags:
  - iv_surface/options_orderflow_lead_lag_v118, cross_venue_arbitrage_surveillance_v118
  - of_vpin/imbalance_greeks_v118
  - sor_atomic_pvp_dvp_v118, latency_jitter_v118
  - asf_options_adverse_selection_mev_v118, slippage_lead_lag_v118
  - gdh_dealer_gamma_hedge_v118, vanna_charm_latency_v118
  - shm_margin_haircut_stress_v118, cross_margin_contagion_v118
  - cft_zero_trust_options_v118, autonomy_failover_v118
  - ptf_settlement_finality_worm_v118, attestation_merkle_bft_v118
  - mm_regime_switch_v118, delta_neutral_cross_venue_v118
  - cap_cross_margin_netting_v118, collateral_liquidation_stress_v118
  - obs_options_tca_attribution_v118, paper_to_live_attestation_v118
  - scr_settlement_custody_v118, settlement_finality_attestation_chain_v118
- **Loop:** inherit from v117 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v118`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v118`, cycles `118`. Engine `Phase110UltraDeepQuantEngineV121(seed=1111198)`. Use `*_deep_v120` methods. Composition gates `composition_mm_v118`/`composition_scr_v118` referencing companions stamped `mm_deep_v118`/`scr_deep_v118`. Emit `version:"v118"`, `seed:1111198`, `engine:"Phase110UltraDeepQuantEngineV121"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module aliases at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v118.py` (PHASE_QUICK_VERIFY=1). Assert gates up to v118 + compositions v118, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v118/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Re-run v82–v118 phase-scoped. All green.
- Grep for forbidden tokens on v118 src+test → empty.
- Update handoff to point to **v119** and sync `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.

(End of file - total 55 lines)
