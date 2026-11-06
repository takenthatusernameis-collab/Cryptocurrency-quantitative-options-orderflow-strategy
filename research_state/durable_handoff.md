# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T09:42:00Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v123 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified this session)
- **v122:** SHIPPED+GREEN/FINITE. `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v122.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v122.py` (1 passed), artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v122/` (`version:"v122"`, `engine:Phase110UltraDeepQuantEngineV125`, `seed:1111202`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:122`, `hash_chain_len:122`). v122 hygiene CLEAN (0 forbidden tokens). v121/v120 regression green.
- **v121:** SHIPPED+GREEN/FINITE (`version:"v121"`, `engine:Phase110UltraDeepQuantEngineV124`, `seed:1111201`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:121`).
- **v120:** SHIPPED+GREEN/FINITE (`version:"v120"`, `engine:Phase110UltraDeepQuantEngineV123`, `seed:1111200`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:120`).
- **Gate:** v122/v121/v120 green. No bottlenecks. Fix any blocker immediately as part of v123 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v120-v122 src+test+artifacts.
- **Repo note:** Full suite has 171 collection errors in unrelated legacy tests (import/environment debt); phase110 targets are green. Do not let legacy collection noise block v123 delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V123` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v122 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV122Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV122Loop().run(); assert r['all_ok'] and r['version']=='v122'; print('ok122')
"
PYTHONPATH=$PWD python3 -m pytest -q tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v122.py
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v123.py`
- Import from v122: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV122Loop`, `Phase110UltraDeepQuantEngineV125`
- `class Phase110UltraDeepQuantEngineV126(Phase110UltraDeepQuantEngineV125)`, `seed=1111203`. Lineage helper range `125..82` (v125 down to v82). Implement 12 `*_deep_v125` methods calling `super().*_deep_v124` and stamping lineage v125..v82 + v123-specific flags (follow v122 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v123, cross_venue_arbitrage_surveillance_v123
  - of_vpin/imbalance_greeks_v123
  - sor_atomic_pvp_dvp_v123, latency_jitter_v123
  - asf_options_adverse_selection_mev_v123, slippage_lead_lag_v123
  - gdh_dealer_gamma_hedge_v123, vanna_charm_latency_v123
  - shm_margin_haircut_stress_v123, cross_margin_contagion_v123
  - cft_zero_trust_options_v123, autonomy_failover_v123
  - ptf_settlement_finality_worm_v123, attestation_merkle_bft_v123
  - mm_regime_switch_v123, delta_neutral_cross_venue_v123
  - cap_cross_margin_netting_v123, collateral_liquidation_stress_v123
  - obs_options_tca_attribution_v123, paper_to_live_attestation_v123
  - scr_settlement_custody_v123, settlement_finality_attestation_chain_v123
- Add composition companion methods `regime_mm_hedge_deep_v124` / `settlement_custody_resilience_deep_v124` (call `super().regime_mm_hedge_deep_v123` / `super().settlement_custody_resilience_deep_v123`, stamp `mm_deep_v124`/`scr_deep_v124`) — mirror v122 companions.
- **Loop:** inherit from v122 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v123`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v123`, cycles `123`. Engine `Phase110UltraDeepQuantEngineV126(seed=1111203)`. Use `*_deep_v125` methods. Composition gates `composition_mm_v123`/`composition_scr_v123` referencing companions stamped `mm_deep_v124`/`scr_deep_v124`. Domain gates loop range `121..82` (checking `*_deep_v121` down to `*_deep_v82`). Emit `version:"v123"`, `seed:1111203`, `engine:"Phase110UltraDeepQuantEngineV126"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v123.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=121, end=82)`. Assert compositions v123, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v123/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Run v123 test; spot-check v122/v121 still green. Do not regress prior phases.
- Grep for forbidden tokens on v123 src+test+artifacts → empty.
- Update handoff to point to **v124** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
