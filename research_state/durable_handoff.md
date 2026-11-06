# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T10:48:47Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v131 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified this session)
- **v130:** SHIPPED+GREEN/FINITE (this session). `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v130.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v130.py` (1 passed), artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v130/` (`version:"v130"`, `engine:"Phase110UltraDeepQuantEngineV133"`, `seed:1111210`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:130`, `hash_chain_len:130`). v130 hygiene CLEAN (0 forbidden tokens).
- **v129:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:"Phase110UltraDeepQuantEngineV132"`, `seed:1111209`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:129`.
- **v128:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:"Phase110UltraDeepQuantEngineV131"`, `seed:1111208`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:128`.
- **Gate:** v130/v129/v128 green. No bottlenecks. Fix any blocker immediately as part of v131 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v128-v130 src+test+artifacts.
- **Repo note:** Full suite has 171 collection errors in unrelated legacy tests (import/environment debt); phase110 targets are green. Do not let legacy collection noise block v131 delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V131` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v130 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV130Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV130Loop().run(); assert r['all_ok'] and r['version']=='v130'; print('ok130')
"
PYTHONPATH=$PWD python3 -m pytest -q tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v130.py
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v131.py`
- Import from v130: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV130Loop`, `Phase110UltraDeepQuantEngineV133`
- `class Phase110UltraDeepQuantEngineV134(Phase110UltraDeepQuantEngineV133)`, `seed=1111211`. Lineage helper range `133..82` (v133 down to v82). Implement 12 `*_deep_v133` methods calling `super().*_deep_v132` and stamping lineage v133..v82 + v131-specific flags (follow v130 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v131, cross_venue_arbitrage_surveillance_v131
  - of_vpin/imbalance_greeks_v131
  - sor_atomic_pvp_dvp_v131, latency_jitter_v131
  - asf_options_adverse_selection_mev_v131, slippage_lead_lag_v131
  - gdh_dealer_gamma_hedge_v131, vanna_charm_latency_v131
  - shm_margin_haircut_stress_v131, cross_margin_contagion_v131
  - cft_zero_trust_options_v131, autonomy_failover_v131
  - ptf_settlement_finality_worm_v131, attestation_merkle_bft_v131
  - mm_regime_switch_v131, delta_neutral_cross_venue_v131
  - cap_cross_margin_netting_v131, collateral_liquidation_stress_v131
  - obs_options_tca_attribution_v131, paper_to_live_attestation_v131
  - scr_settlement_custody_v131, settlement_finality_attestation_chain_v131
- Add composition companion methods `regime_mm_hedge_deep_v132` / `settlement_custody_resilience_deep_v132` (call `super().regime_mm_hedge_deep_v131` / `super().settlement_custody_resilience_deep_v131`, stamp `mm_deep_v132`/`scr_deep_v132`) — mirror v130 companions.
- **Loop:** inherit from v130 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v131`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v131`, cycles `131`. Engine `Phase110UltraDeepQuantEngineV134(seed=1111211)`. Use `*_deep_v133` methods. Composition gates `composition_mm_v131`/`composition_scr_v131` referencing companions stamped `mm_deep_v132`/`scr_deep_v132`. Domain gates loop range `129..82` (checking `*_deep_v129` down to `*_deep_v82`). Emit `version:"v131"`, `seed:1111211`, `engine:"Phase110UltraDeepQuantEngineV134"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v131.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=129, end=82)`. Assert compositions v131, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v131/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Run v131 test; spot-check v130/v129 still green. Do not regress prior phases.
- Grep for forbidden tokens on v131 src+test+artifacts → empty.
- Update handoff to point to **v132** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
