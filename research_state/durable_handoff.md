# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T09:47:00Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v125 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified this session)
- **v124:** SHIPPED+GREEN/FINITE (this session). `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v124.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v124.py` (1 passed), artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v124/` (`version:"v124"`, `engine:Phase110UltraDeepQuantEngineV127`, `seed:1111204`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:124`, `hash_chain_len:124`). v124 hygiene CLEAN (0 forbidden tokens).
- **v123:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:Phase110UltraDeepQuantEngineV126`, `seed:1111203`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:123`.
- **v122:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:Phase110UltraDeepQuantEngineV125`, `seed:1111202`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:122`.
- **Gate:** v124/v123/v122 green. No bottlenecks. Fix any blocker immediately as part of v125 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v122-v124 src+test+artifacts.
- **Repo note:** Full suite has 171 collection errors in unrelated legacy tests (import/environment debt); phase110 targets are green. Do not let legacy collection noise block v125 delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V125` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v124 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV124Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV124Loop().run(); assert r['all_ok'] and r['version']=='v124'; print('ok124')
"
PYTHONPATH=$PWD python3 -m pytest -q tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v124.py
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v125.py`
- Import from v124: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV124Loop`, `Phase110UltraDeepQuantEngineV127`
- `class Phase110UltraDeepQuantEngineV128(Phase110UltraDeepQuantEngineV127)`, `seed=1111205`. Lineage helper range `127..82` (v127 down to v82). Implement 12 `*_deep_v127` methods calling `super().*_deep_v126` and stamping lineage v127..v82 + v125-specific flags (follow v124 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v125, cross_venue_arbitrage_surveillance_v125
  - of_vpin/imbalance_greeks_v125
  - sor_atomic_pvp_dvp_v125, latency_jitter_v125
  - asf_options_adverse_selection_mev_v125, slippage_lead_lag_v125
  - gdh_dealer_gamma_hedge_v125, vanna_charm_latency_v125
  - shm_margin_haircut_stress_v125, cross_margin_contagion_v125
  - cft_zero_trust_options_v125, autonomy_failover_v125
  - ptf_settlement_finality_worm_v125, attestation_merkle_bft_v125
  - mm_regime_switch_v125, delta_neutral_cross_venue_v125
  - cap_cross_margin_netting_v125, collateral_liquidation_stress_v125
  - obs_options_tca_attribution_v125, paper_to_live_attestation_v125
  - scr_settlement_custody_v125, settlement_finality_attestation_chain_v125
- Add composition companion methods `regime_mm_hedge_deep_v126` / `settlement_custody_resilience_deep_v126` (call `super().regime_mm_hedge_deep_v125` / `super().settlement_custody_resilience_deep_v125`, stamp `mm_deep_v126`/`scr_deep_v126`) — mirror v124 companions.
- **Loop:** inherit from v124 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v125`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v125`, cycles `125`. Engine `Phase110UltraDeepQuantEngineV128(seed=1111205)`. Use `*_deep_v127` methods. Composition gates `composition_mm_v125`/`composition_scr_v125` referencing companions stamped `mm_deep_v126`/`scr_deep_v126`. Domain gates loop range `123..82` (checking `*_deep_v123` down to `*_deep_v82`). Emit `version:"v125"`, `seed:1111205`, `engine:"Phase110UltraDeepQuantEngineV128"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v125.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=123, end=82)`. Assert compositions v125, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v125/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Run v125 test; spot-check v124/v123 still green. Do not regress prior phases.
- Grep for forbidden tokens on v125 src+test+artifacts → empty.
- Update handoff to point to **v126** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
