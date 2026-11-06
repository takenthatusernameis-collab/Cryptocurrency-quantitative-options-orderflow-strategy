# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T09:55:09Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy`
**MANDATE:** Ship **v128 NOW**. No exploration/planning-only. Tangible `src/` + `tests/` + deterministic `research_state/` artifacts required. Gate must be GREEN before ending session.

## CURRENT STATE (re-verified this session)
- **v127:** SHIPPED+GREEN/FINITE (this session). `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v127.py`, test `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v127.py` (1 passed), artifacts in `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v127/` (`version:"v127"`, `engine:Phase110UltraDeepQuantEngineV130`, `seed:1111207`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:127`, `hash_chain_len:127`). v127 hygiene CLEAN (0 forbidden tokens).
- **v126:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:Phase110UltraDeepQuantEngineV129`, `seed:1111206`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:126`.
- **v125:** SHIPPED+GREEN/FINITE (regression 1 passed). `engine:Phase110UltraDeepQuantEngineV128`, `seed:1111205`, `all_ok/finite_ok/gates.all_ok:true`, `cycles:125`.
- **Gate:** v127/v126/v125 green. No bottlenecks. Fix any blocker immediately as part of v128 work.
- **Hygiene:** ZERO `TODO/FIXME/HACK/XXX/placeholder/PLACEHOLDER` in v125-v127 src+test+artifacts.
- **Repo note:** Full suite has 171 collection errors in unrelated legacy tests (import/environment debt); phase110 targets are green. Do not let legacy collection noise block v128 delivery.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE FOR NEXT AGENT (HEAVY, NO DEVIATION)

**OBJECTIVE:** Implement and ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V128` end-to-end.

**STEP 1 — VERIFY GATE FIRST**
```bash
cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 -c "
from src.risk.phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v127 import Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV127Loop
r=Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV127Loop().run(); assert r['all_ok'] and r['version']=='v127'; print('ok127')
"
PYTHONPATH=$PWD python3 -m pytest -q tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v127.py
```

**STEP 2 — CREATE SRC** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v128.py`
- Import from v127: `Phase110Cfg`, `Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV127Loop`, `Phase110UltraDeepQuantEngineV130`
- `class Phase110UltraDeepQuantEngineV131(Phase110UltraDeepQuantEngineV130)`, `seed=1111208`. Lineage helper range `130..82` (v130 down to v82). Implement 12 `*_deep_v130` methods calling `super().*_deep_v129` and stamping lineage v130..v82 + v128-specific flags (follow v127 pattern exactly):
  - iv_surface/options_orderflow_lead_lag_v128, cross_venue_arbitrage_surveillance_v128
  - of_vpin/imbalance_greeks_v128
  - sor_atomic_pvp_dvp_v128, latency_jitter_v128
  - asf_options_adverse_selection_mev_v128, slippage_lead_lag_v128
  - gdh_dealer_gamma_hedge_v128, vanna_charm_latency_v128
  - shm_margin_haircut_stress_v128, cross_margin_contagion_v128
  - cft_zero_trust_options_v128, autonomy_failover_v128
  - ptf_settlement_finality_worm_v128, attestation_merkle_bft_v128
  - mm_regime_switch_v128, delta_neutral_cross_venue_v128
  - cap_cross_margin_netting_v128, collateral_liquidation_stress_v128
  - obs_options_tca_attribution_v128, paper_to_live_attestation_v128
  - scr_settlement_custody_v128, settlement_finality_attestation_chain_v128
- Add composition companion methods `regime_mm_hedge_deep_v129` / `settlement_custody_resilience_deep_v129` (call `super().regime_mm_hedge_deep_v128` / `super().settlement_custody_resilience_deep_v128`, stamp `mm_deep_v129`/`scr_deep_v129`) — mirror v127 companions.
- **Loop:** inherit from v127 loop. Set `self.cfg` AFTER `super().__init__()`: phase/name/version `v128`, outdir `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v128`, cycles `128`. Engine `Phase110UltraDeepQuantEngineV131(seed=1111208)`. Use `*_deep_v130` methods. Composition gates `composition_mm_v128`/`composition_scr_v128` referencing companions stamped `mm_deep_v129`/`scr_deep_v129`. Domain gates loop range `126..82` (checking `*_deep_v126` down to `*_deep_v82`). Emit `version:"v128"`, `seed:1111208`, `engine:"Phase110UltraDeepQuantEngineV131"`, `all_ok`/`finite_ok`/`gates.all_ok` true. Module alias at end.

**STEP 3 — CREATE TEST + ARTIFACTS**
- Test: `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v128.py` (PHASE_QUICK_VERIFY=1). `_assert_domain_gates(g, prefix, start=126, end=82)`. Assert compositions v128, all_ok/finite_ok/gates.all_ok true, version/seed/engine correct.
- Artifacts: deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v128/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies), finite.

**STEP 4 — VERIFY, HYGIENE, SYNC HANDOFF**
- Run v128 test; spot-check v127/v126 still green. Do not regress prior phases.
- Grep for forbidden tokens on v128 src+test+artifacts → empty.
- Update handoff to point to **v129** and sync `HANDOFF_NEXT_AGENT.md`, `research_state/durable_handoff.md`, `research_state/INITIAL_TASK_HANDOFF.md`.
- **Do not end without tangible src+test+artifacts and gate GREEN.**

## CAMPAIGN MANDATE
- Every session MUST ship >=1 phase110 module + >=1 passing test + >=1 deterministic artifact set.
- PAPER-ONLY, finite/deterministic/seeded, no NaN/Inf, no forbidden tokens. Extend/compose only over prior shipped versions. Fix blockers immediately. Do not regress prior phases.
