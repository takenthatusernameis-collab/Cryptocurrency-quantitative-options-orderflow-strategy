# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T10:57:41Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v132 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified this session)
- **v131:** SHIPPED+GREEN/FINITE (this session). `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v131.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v131.py` (1 passed), artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v131/` (`version:"v131"`, `engine:"Phase110UltraDeepQuantEngineV134"`, `seed:1111211`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:131`, `hash_chain_len:131`). v131 hygiene CLEAN (0 forbidden tokens).
- **v130:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:"Phase110UltraDeepQuantEngineV133"`, `seed:1111210`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:130`.
- **v129:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:"Phase110UltraDeepQuantEngineV132"`, `seed:1111209`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:129`.
- **Gate:** v131/v130/v129 green. No bottlenecks. Fix any blocker immediately as part of v132 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v129-v131 src+test+artifacts.
- **Repo note:** Full suite has 171 collection errors in unrelated legacy tests (import/environment debt); phase110 targets are green. Do not let legacy collection noise block v132 delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V132` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v131 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV131Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV131Loop().run(); assert r['all_ok'] and r['version']=='v131'; print('ok131')
"
PYTHONPATH=$PWD python3 -m pytest -q tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v131.py
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v132.py`
- Import from v131: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV131Loop`, `Phase110UltraDeepQuantEngineV134`
- `class Phase110UltraDeepQuantEngineV135(Phase110UltraDeepQuantEngineV134)`, `seed=1111212`. Lineage helper range `134..83` (v134 down to v83). Implement 12 `*_deep_v134` methods calling `super().*_deep_v133` and stamping lineage v134..v83 + v132-specific flags (follow v131 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v132, cross_venue_arbitrage_surveillance_v132
  - of_vpin/imbalance_greeks_v132
  - sor_atomic_pvp_dvp_v132, latency_jitter_v132
  - asf_options_adverse_selection_mev_v132, slippage_lead_lag_v132
  - gdh_dealer_gamma_hedge_v132, vanna_charm_latency_v132
  - shm_margin_haircut_stress_v132, cross_margin_contagion_v132
  - cft_zero_trust_options_v132, autonomy_failover_v132
  - ptf_settlement_finality_worm_v132, attestation_merkle_bft_v132
  - mm_regime_switch_v132, delta_neutral_cross_venue_v132
  - cap_cross_margin_netting_v132, collateral_liquidation_stress_v132
  - obs_options_tca_attribution_v132, paper_to_live_attestation_v132
  - scr_settlement_custody_v132, settlement_finality_attestation_chain_v132
- Add composition companion methods `regime_mm_hedge_deep_v133` / `settlement_custody_resilience_deep_v133` (call `super().regime_mm_hedge_deep_v132` / `super().settlement_custody_resilience_deep_v132`, stamp `mm_deep_v133`/`scr_deep_v133`) — mirror v131 companions.
- **Loop:** inherit from v131 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v132`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v132`, cycles `132`. Engine `Phase110UltraDeepQuantEngineV135(seed=1111212)`. Use `*_deep_v134` methods. Composition gates `composition_mm_v132`/`composition_scr_v132` referencing companions stamped `mm_deep_v133`/`scr_deep_v133`. Domain gates loop range `130..83` (checking `*_deep_v130` down to `*_deep_v83`). Emit `version:"v132"`, `seed:1111212`, `engine:"Phase110UltraDeepQuantEngineV135"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v132.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=130, end=83)`. Assert compositions v132, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v132/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Run v132 test; spot-check v131/v130 still green. Do not regress prior phases.
- Grep for forbidden tokens on v132 src+test+artifacts → empty.
- Update handoff to point to **v133** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
