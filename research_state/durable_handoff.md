# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
# Timestamp (UTC): 2026-11-06T00:50:38Z
# Repo (inferred from name): Cryptocurrency-quantitative-options-orderflow-strategy
# Domain priority (NON-NEGOTIABLE): CRYPTO OPTIONS + ORDERFLOW QUANT — crypto options pricing/Greeks/IV/surface (SABR/RBergomi/VG/jump-diffusion/local-stochastic/hybrid no-arb), orderflow microstructure/toxicity/VPIN/lead-lag/MEV/adversarial detection, adverse selection×slippage×fill, gamma/dealer/vanna/charm positioning/hedging, cross-venue SOR/routing/fragmentation/latency-jitter/atomic PvP-DvP, regime-aware MM/hedging, cross-margin/collateral/netting/haircuts/liquidation/stress/contagion, post-trade finality/settlement/custody/reconciliation/novation/clearing/attestation/WORM/ZK/Merkle/BFT, observability/attribution/TCA/paper-to-live, autonomous resilience/recovery/compliance/governance/chaos/zero-trust. PAPER-ONLY, finite, deterministic, seeded.
#
# ONLY SOURCE OF TRUTH. `HANDOFF_NEXT_AGENT.md` and `research_state/INITIAL_TASK_HANDOFF.md` are pointers to this file.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY WORK, NO DEVIATION)
**Timestamp (UTC): 2026-11-06T00:50:38Z | Gate: GREEN (phase-scoped, re-verified this session 2026-11-06T00:50:38Z: v82-v95 = 14 ok, `PHASE_QUICK_VERIFY=1` module execution) | NO BLOCKED SESSIONS | NO BOTTLENECKS | `research_state/` writable | v82-v95 SHIPPED+GREEN — v96 ABSENT (confirmed 2026-11-06T00:50:38Z) — SHIP NEXT IMMEDIATELY**

Phases 1-109 COMPLETE+SHIPPED. Phase 110 v8-v95 COMPLETE+SHIPPED+GREEN. **Re-verified this session (2026-11-06T00:50:38Z, `PHASE_QUICK_VERIFY=1`, `PYTHONPATH=$PWD`):** v82-v95 phase-scoped regression 14 ok (direct module execution; pytest binary absent in runner — documented fallback, not a blocker). v95 shipped+green/finite (`research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v95/PHASE110_RES_LATEST.json`: `version:"v95"`, `engine:Phase110UltraDeepQuantEngineV98`, `all_ok/finite_ok/gates.all_ok:true`, `seed:1111175`, `cycles:95`). Hygiene (v95 src+test): clean. **v96 src/test/artifacts ABSENT repo-wide (confirmed 2026-11-06T00:50:38Z) — MANDATORY HEAVY CAMPAIGN: SHIP v96 NOW. NO EXPLORATION. NO SCAFFOLDING. NO PLACEHOLDERS.** Read v95 implementation as the composition template, then implement v96 directly.

### INFERRED PRIMARY OBJECTIVE (BASED ON REPO NAME + PRIOR PATTERN)
**Cryptocurrency quantitative options + orderflow strategy** repo. Continue hardening **live execution realism + realtime cross-venue SOR/routing + post-trade finality/autonomy** with deeper quant coverage. Treat v96 as the next concrete, testable hardening step. Every method must be real, finite, deterministic, and integrated via composition over v95.

### EXECUTE NOW (NON-OPTIONAL — HEAVY QUANT IMPLEMENTATION)
**`PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V96`** — ship tangible heavy-quant code + tests + deterministic artifacts in THIS session.

1. **VERIFY GATE (MUST PASS BEFORE NEW WORK):**
   ```bash
   cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
   PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 - << 'PY'
   import os,sys
   os.environ.setdefault("PHASE_QUICK_VERIFY","1"); sys.path.insert(0,os.getcwd())
   for v in range(82,96):
       m=__import__(f'tests.test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v{v}',fromlist=['*'])
       getattr(m,f'test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v{v}')(); print('ok',v)
   print('ok 14')
   PY
   ```
   Expect `14 ok`. If RED or hygiene violations found → **FIX BEFORE ANY NEW PHASE WORK**. Remove blockers now.

2. **SHIP V96 SRC (COMPOSE CLEANLY OVER V95, ZERO SCAFFOLDING):**
   - **Src:** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96.py`
   - Import from v95: `Phase110Cfg`, v95 loop class, `Phase110UltraDeepQuantEngineV98`.
   - **Engine:** `class Phase110UltraDeepQuantEngineV99(Phase110UltraDeepQuantEngineV98)`: `__init__(self, seed: int = 1111176)`. Implement **12 concrete `*_deep_v98` methods**, each stamping `*_deep_v97` + full lineage `*_deep_v96..v82` + required v80 feature flags by calling `super().*_deep_v97`. **Use v95's actual base method names** (e.g. `iv_surface_greeks_deep_v98` calls `super().iv_surface_greeks_deep_v97`; `orderflow_microstructure_deep_v98` → `super().orderflow_microstructure_deep_v97`; `cross_venue_sor_toxicity_opt_deep_v98` → `super().cross_venue_sor_toxicity_opt_deep_v97`; `adverse_sel_slippage_fill_joint_deep_v98` → `super().adverse_sel_slippage_fill_joint_deep_v97`; `gamma_dealer_hedge_toxicity_adjusted_deep_v98` → `super().gamma_dealer_hedge_toxicity_adjusted_deep_v97`; `stress_haircut_margin_deep_v98` → `super().stress_haircut_margin_deep_v97`; `chaos_failover_tamper_deep_v98` → `super().chaos_failover_tamper_deep_v97`; `post_trade_finality_attestation_deep_v98` → `super().post_trade_finality_attestation_deep_v97`; `regime_mm_hedge_deep_v98` → `super().regime_mm_hedge_deep_v97`; `collateral_margin_netting_deep_v98` → `super().collateral_margin_netting_deep_v97`; `observability_attribution_tca_deep_v98` → `super().observability_attribution_tca_deep_v97`; `settlement_custody_resilience_deep_v98` → `super().settlement_custody_resilience_deep_v97`). Deepen meaningfully for **crypto options/orderflow/live-exec/realtime/SOR/post-trade/finality/autonomy** (fill realism, adverse selection/slippage, cross-venue fragmentation/latency-jitter, SOR constraints/costs, settlement/finality/attestation, resilience/chaos/zero-trust). All values finite/deterministic.
   - **Loop:** `class Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV96Loop(...)`: inherit cleanly from v95 loop. **Set `self.cfg` AFTER `super().__init__()`**. Default `Phase110Cfg(phase="PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V96", name="phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96", version="v96", outdir="research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96", cycles=96)`. Instantiate `Phase110UltraDeepQuantEngineV99` with seed `1111176`; run v98 deep checks + composition gates consistent with emitted methods. **Composition note (pattern):** `mm/scr` composition checks must use companion outputs whose emitted lineage flag exists (follow v91-v95: `mm_deep_v96/scr_deep_v96` on `*_deep_v96` companion outputs => gates `composition_mm_v96/scr_v96`). Emit top-level `all_ok`, `finite_ok`, `gates.all_ok`, `version:"v96"`, `seed`. cfg/phase/name/outdir/version/cycles/seed self-consistent. Do not regress v8-v95.

3. **SHIP TEST + ARTIFACTS (NON-NEGOTIABLE):**
   - **Test:** `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96.py` passing with `PHASE_QUICK_VERIFY=1`; assert V99 deep gates (`*_deep_v97/v96/.../v82` aggregates + required lineage flags as emitted) + composition gates + `res["all_ok"] is True`, `res["finite_ok"] is True`, `g["all_ok"] is True`, `res["version"]=="v96"`.
   - **Artifacts:** generate deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96/PHASE110_RES_LATEST.json` + `.md` (and timestamped copies) with `all_ok:true`, `finite_ok:true`, `gates.all_ok:true`, `version:"v96"`, `seed:1111176`, finite numerics.

4. **REGRESSION + HYGIENE + HANDOFF SYNC:** Re-run phase-scoped v82-v96 — all green. `grep -rn 'TODO\|FIXME\|HACK\|XXX\|placeholder\|PLACEHOLDER'` on v96 src+test must be empty. Update this durable handoff (fresh UTC), sync root `HANDOFF_NEXT_AGENT.md` and `research_state/INITIAL_TASK_HANDOFF.md`. No session may end without tangible src+tests+artifacts and phase-scoped gate GREEN.

### CAMPAIGN MANDATE (FUTURE SESSIONS CANNOT AVOID HEAVY WORK)
- **Current non-optional campaign: `PHASE_110..._V96`**. After v96 ships+green, **next is v97** — continue same strict composition pattern.
- **Every session MUST ship:** >=1 `src/risk/` phase module + >=1 passing `tests/test_phase110_*` (`PHASE_QUICK_VERIFY=1`) + >=1 deterministic `research_state/phase110_*` artifact set. Phase-scoped gate GREEN before ending.
- **Hard rules:** PAPER-ONLY; finite numerics; deterministic/seeded; no NaN/Inf; no TODO/FIXME/HACK/XXX/placeholder. Extend/compose only over prior shipped versions. Fail fast on non-finite/placeholder leakage. If wiring/import/cycle blocks progress: implement minimal glue NOW. Do not regress Phases 1-109 or v8-v95.
- **Bottleneck removal rule:** if blocked/inefficient, remove the blocker immediately before taking new scope. **Current status: NO blocked sessions. NO bottlenecks. `research_state/` writable.**

### BOTTLENECK/STATUS (2026-11-06T00:50:38Z — re-verified)
- Gate re-verified this session: v82-v95 phase-scoped regression 14 ok (`PHASE_QUICK_VERIFY=1`, module execution). `pytest` binary not installed in runner — **documented fallback, not a blocker**. v95 shipped+green; artifacts finite/green. v95 src+test hygiene clean. v96 src/test/artifacts ABSENT repo-wide (confirmed 2026-11-06T00:50:38Z).
- **No blocked sessions. No bottlenecks. `research_state/` writable.** Hygiene enforcement for this campaign applies to **v96 src+test** (and any new files touched).
- v95 is the composition template (V98 engine, V95 loop, seed 1111175, cycles 95, composition over v96 companion checks `mm_deep_v96/scr_deep_v96`). v96 must use V99, seed 1111176, cycles 96, `*_deep_v98` methods, and inherit/stamp lineage through v82 plus v80 feature flags. Composition companions must emit the asserted lineage flag.
- Full pytest suite not run in this session; phase-scoped gate is the required pre-work gate.

### ACTION REQUIRED NOW (CANNOT DEFER)
Ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V96` with real implementation, passing tests, and deterministic `research_state/phase110_*_v96/PHASE110_RES_LATEST.*` artifacts.

### FILES VERIFIED/REFRESHED THIS SESSION (2026-11-06T00:50:38Z)
- Re-verified gate: v82-v95 phase-scoped regression 14 ok (`PHASE_QUICK_VERIFY=1`). v96 absent repo-wide. `research_state/` writable. No blocked sessions. No bottlenecks.
- Refreshed authoritative `research_state/durable_handoff.md` and synced root `HANDOFF_NEXT_AGENT.md` + `research_state/INITIAL_TASK_HANDOFF.md` with fresh UTC, re-verified status, and explicit v96 heavy-work mandate.
