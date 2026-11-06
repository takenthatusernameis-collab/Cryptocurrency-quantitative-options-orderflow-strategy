# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T10:45:29Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v130 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified this session)
- **v129:** SHIPPED+GREEN/FINITE (this session). `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v129.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v129.py` (1 passed), artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v129/` (`version:"v129"`, `engine:Phase110UltraDeepQuantEngineV132`, `seed:1111209`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:129`, `hash_chain_len:129`). v129 hygiene CLEAN (0 forbidden tokens).
- **v128:** SHIPPED+GREEN/FINITE (this session). `engine:Phase110UltraDeepQuantEngineV131`, `seed:1111208`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:128`.
- **v127:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:Phase110UltraDeepQuantEngineV130`, `seed:1111207`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:127`.
- **Gate:** v129/v128/v127 green. No bottlenecks. Fix any blocker immediately as part of v130 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v127-v129 src+test+artifacts.
- **Repo note:** Full suite has 171 collection errors in unrelated legacy tests (import/environment debt); phase110 targets are green. Do not let legacy collection noise block v130 delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V130` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v129 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV129Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV129Loop().run(); assert r['all_ok'] and r['version']=='v129'; print('ok129')
"
PYTHONPATH=$PWD python3 -m pytest -q tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v129.py
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v130.py`
- Import from v129: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV129Loop`, `Phase110UltraDeepQuantEngineV132`
- `class Phase110UltraDeepQuantEngineV133(Phase110UltraDeepQuantEngineV132)`, `seed=1111210`. Lineage helper range `132..82` (v132 down to v82). Implement 12 `*_deep_v132` methods calling `super().*_deep_v131` and stamping lineage v132..v82 + v130-specific flags (follow v129 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v130, cross_venue_arbitrage_surveillance_v130
  - of_vpin/imbalance_greeks_v130
  - sor_atomic_pvp_dvp_v130, latency_jitter_v130
  - asf_options_adverse_selection_mev_v130, slippage_lead_lag_v130
  - gdh_dealer_gamma_hedge_v130, vanna_charm_latency_v130
  - shm_margin_haircut_stress_v130, cross_margin_contagion_v130
  - cft_zero_trust_options_v130, autonomy_failover_v130
  - ptf_settlement_finality_worm_v130, attestation_merkle_bft_v130
  - mm_regime_switch_v130, delta_neutral_cross_venue_v130
  - cap_cross_margin_netting_v130, collateral_liquidation_stress_v130
  - obs_options_tca_attribution_v130, paper_to_live_attestation_v130
  - scr_settlement_custody_v130, settlement_finality_attestation_chain_v130
- Add composition companion methods `regime_mm_hedge_deep_v131` / `settlement_custody_resilience_deep_v131` (call `super().regime_mm_hedge_deep_v130` / `super().settlement_custody_resilience_deep_v130`, stamp `mm_deep_v131`/`scr_deep_v131`) — mirror v129 companions.
- **Loop:** inherit from v129 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v130`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v130`, cycles `130`. Engine `Phase110UltraDeepQuantEngineV133(seed=1111210)`. Use `*_deep_v132` methods. Composition gates `composition_mm_v130`/`composition_scr_v130` referencing companions stamped `mm_deep_v131`/`scr_deep_v131`. Domain gates loop range `128..82` (checking `*_deep_v128` down to `*_deep_v82`). Emit `version:"v130"`, `seed:1111210`, `engine:"Phase110UltraDeepQuantEngineV133"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v130.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=128, end=82)`. Assert compositions v130, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v130/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Run v130 test; spot-check v129/v128 still green. Do not regress prior phases.
- Grep for forbidden tokens on v130 src+test+artifacts → empty.
- Update handoff to point to **v131** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
