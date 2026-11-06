# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T08:49:31Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v120 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified this session)
- **v119:** SHIPPED+GREEN/FINITE. `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v119.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v119.py` (1 passed), artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v119/` (`version:"v119"`, `engine:Phase110UltraDeepQuantEngineV122`, `seed:1111199`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:119`, `hash_chain_len:119`). v119 hygiene CLEAN (0 forbidden tokens). v118 regression green.
- **v118:** SHIPPED+GREEN/FINITE (`version:"v118"`, `engine:Phase110UltraDeepQuantEngineV121`, `seed:1111198`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:118`).
- **Gate:** v119/v118 green. No bottlenecks. Fix any blocker immediately as part of v120 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v118/v119 src+test+artifacts.
- **Repo note:** Full suite has 171 collection errors in unrelated legacy tests (import/environment debt); phase110 targets are green. Do not let legacy collection noise block v120 delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V120` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v119 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV119Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV119Loop().run(); assert r['all_ok'] and r['version']=='v119'; print('ok119')
"
PYTHONPATH=$PWD python3 -m pytest -q tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v119.py
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v120.py`
- Import from v119: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV119Loop`, `Phase110UltraDeepQuantEngineV122`
- `class Phase110UltraDeepQuantEngineV123(Phase110UltraDeepQuantEngineV122)`, `seed=1111200`. Lineage helper range `122..81` (v122 down to v82). Implement 12 `*_deep_v122` methods calling `super().*_deep_v121` and stamping lineage v122..v82 + v120-specific flags (follow v119 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v120, cross_venue_arbitrage_surveillance_v120
  - of_vpin/imbalance_greeks_v120
  - sor_atomic_pvp_dvp_v120, latency_jitter_v120
  - asf_options_adverse_selection_mev_v120, slippage_lead_lag_v120
  - gdh_dealer_gamma_hedge_v120, vanna_charm_latency_v120
  - shm_margin_haircut_stress_v120, cross_margin_contagion_v120
  - cft_zero_trust_options_v120, autonomy_failover_v120
  - ptf_settlement_finality_worm_v120, attestation_merkle_bft_v120
  - mm_regime_switch_v120, delta_neutral_cross_venue_v120
  - cap_cross_margin_netting_v120, collateral_liquidation_stress_v120
  - obs_options_tca_attribution_v120, paper_to_live_attestation_v120
  - scr_settlement_custody_v120, settlement_finality_attestation_chain_v120
- Add composition companion methods `regime_mm_hedge_deep_v121` / `settlement_custody_resilience_deep_v121` (call `super().regime_mm_hedge_deep_v120` / `super().settlement_custody_resilience_deep_v120`, stamp `mm_deep_v121`/`scr_deep_v121`) — mirror v119 companions.
- **Loop:** inherit from v119 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v120`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v120`, cycles `120`. Engine `Phase110UltraDeepQuantEngineV123(seed=1111200)`. Use `*_deep_v122` methods. Composition gates `composition_mm_v120`/`composition_scr_v120` referencing companions stamped `mm_deep_v121`/`scr_deep_v121`. Domain gates loop range `118..82` (checking `*_deep_v118` down to `*_deep_v82`). Emit `version:"v120"`, `seed:1111200`, `engine:"Phase110UltraDeepQuantEngineV123"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v120.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=119, end=82)`. Assert compositions v120, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v120/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Run v120 test; spot-check v119/v118 still green. Do not regress prior phases.
- Grep for forbidden tokens on v120 src+test+artifacts → empty.
- Update handoff to point to **v121** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
