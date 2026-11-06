# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T09:43:50Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v124 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified this session)
- **v123:** SHIPPED+GREEN/FINITE (this session). `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v123.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v123.py` (1 passed), artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v123/` (`version:"v123"`, `engine:Phase110UltraDeepQuantEngineV126`, `seed:1111203`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:123`, `hash_chain_len:123`). v123 hygiene CLEAN (0 forbidden tokens).
- **v122:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:Phase110UltraDeepQuantEngineV125`, `seed:1111202`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:122`.
- **v121:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:Phase110UltraDeepQuantEngineV124`, `seed:1111201`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:121`.
- **Gate:** v123/v122/v121 green. No bottlenecks. Fix any blocker immediately as part of v124 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v121-v123 src+test+artifacts.
- **Repo note:** Full suite has 171 collection errors in unrelated legacy tests (import/environment debt); phase110 targets are green. Do not let legacy collection noise block v124 delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V124` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v123 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV123Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV123Loop().run(); assert r['all_ok'] and r['version']=='v123'; print('ok123')
"
PYTHONPATH=$PWD python3 -m pytest -q tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v123.py
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v124.py`
- Import from v123: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV123Loop`, `Phase110UltraDeepQuantEngineV126`
- `class Phase110UltraDeepQuantEngineV127(Phase110UltraDeepQuantEngineV126)`, `seed=1111204`. Lineage helper range `126..82` (v126 down to v82). Implement 12 `*_deep_v126` methods calling `super().*_deep_v125` and stamping lineage v126..v82 + v124-specific flags (follow v123 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v124, cross_venue_arbitrage_surveillance_v124
  - of_vpin/imbalance_greeks_v124
  - sor_atomic_pvp_dvp_v124, latency_jitter_v124
  - asf_options_adverse_selection_mev_v124, slippage_lead_lag_v124
  - gdh_dealer_gamma_hedge_v124, vanna_charm_latency_v124
  - shm_margin_haircut_stress_v124, cross_margin_contagion_v124
  - cft_zero_trust_options_v124, autonomy_failover_v124
  - ptf_settlement_finality_worm_v124, attestation_merkle_bft_v124
  - mm_regime_switch_v124, delta_neutral_cross_venue_v124
  - cap_cross_margin_netting_v124, collateral_liquidation_stress_v124
  - obs_options_tca_attribution_v124, paper_to_live_attestation_v124
  - scr_settlement_custody_v124, settlement_finality_attestation_chain_v124
- Add composition companion methods `regime_mm_hedge_deep_v125` / `settlement_custody_resilience_deep_v125` (call `super().regime_mm_hedge_deep_v124` / `super().settlement_custody_resilience_deep_v124`, stamp `mm_deep_v125`/`scr_deep_v125`) — mirror v123 companions.
- **Loop:** inherit from v123 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v124`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v124`, cycles `124`. Engine `Phase110UltraDeepQuantEngineV127(seed=1111204)`. Use `*_deep_v126` methods. Composition gates `composition_mm_v124`/`composition_scr_v124` referencing companions stamped `mm_deep_v125`/`scr_deep_v125`. Domain gates loop range `122..82` (checking `*_deep_v122` down to `*_deep_v82`). Emit `version:"v124"`, `seed:1111204`, `engine:"Phase110UltraDeepQuantEngineV127"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v124.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=122, end=82)`. Assert compositions v124, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v124/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Run v124 test; spot-check v123/v122 still green. Do not regress prior phases.
- Grep for forbidden tokens on v124 src+test+artifacts → empty.
- Update handoff to point to **v125** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
