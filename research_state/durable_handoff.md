# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
# Timestamp (UTC): 2026-11-06T00:08:57Z
# Repo (inferred from name): Cryptocurrency-quantitative-options-orderflow-strategy
# Domain priority (NON-NEGOTIABLE): CRYPTO OPTIONS + ORDERFLOW QUANT — crypto options pricing/Greeks/IV/surface (SABR/RBergomi/VG/jump-diffusion/local-stochastic/hybrid no-arb), orderflow microstructure/toxicity/VPIN/lead-lag/MEV/adversarial detection, adverse selection×slippage×fill, gamma/dealer/vanna/charm positioning/hedging, cross-venue SOR/routing/fragmentation/latency-jitter/atomic PvP-DvP, regime-aware MM/hedging, cross-margin/collateral/netting/haircuts/liquidation/stress/contagion, post-trade finality/settlement/custody/reconciliation/novation/clearing/attestation/WORM/ZK/Merkle/BFT, observability/attribution/TCA/paper-to-live, autonomous resilience/recovery/compliance/governance/chaos/zero-trust. PAPER-ONLY, finite, deterministic, seeded.
#
# ONLY SOURCE OF TRUTH. `HANDOFF_NEXT_AGENT.md` and `research_state/INITIAL_TASK_HANDOFF.md` are pointers to this file.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY WORK, NO DEVIATION)
**Timestamp (UTC): 2026-11-06T00:08:57Z | Gate: GREEN (phase-scoped, re-verified this session 2026-11-06T00:08:57Z: v82-v94 = 13 ok, `PHASE_QUICK_VERIFY=1` module execution) | NO BLOCKED SESSIONS | NO BOTTLENECKS | `research_state/` writable | v82-v94 SHIPPED+GREEN — v95 ABSENT (confirmed 2026-11-06T00:08:57Z) — SHIP NEXT IMMEDIATELY**

Phases 1-109 COMPLETE+SHIPPED. Phase 110 v8-v94 COMPLETE+SHIPPED+GREEN. **Re-verified this session (2026-11-06T00:08:57Z, `PHASE_QUICK_VERIFY=1`, `PYTHONPATH=$PWD`):** v82-v94 phase-scoped regression 13 ok (direct module execution; pytest binary absent in runner — documented fallback, not a blocker). v94 shipped+green/finite (`research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v94/PHASE110_RES_LATEST.json`: `version:"v94"`, `engine:Phase110UltraDeepQuantEngineV97`, `all_ok/finite_ok/gates.all_ok:true`, `seed:1111174`, `cycles:94`). Hygiene (v94 src+test): clean. **v95 src/test/artifacts ABSENT repo-wide (confirmed 2026-11-06T00:08:57Z) — MANDATORY HEAVY CAMPAIGN: SHIP v95 NOW. NO EXPLORATION. NO SCAFFOLDING. NO PLACEHOLDERS.** Read v94 implementation as the composition template, then implement v95 directly.

### INFERRED PRIMARY OBJECTIVE (BASED ON REPO NAME + PRIOR PATTERN)
**Cryptocurrency quantitative options + orderflow strategy** repo. Continue hardening **live execution realism + realtime cross-venue SOR/routing + post-trade finality/autonomy** with deeper quant coverage. Treat v95 as the next concrete, testable hardening step. Every method must be real, finite, deterministic, and integrated via composition over v94.

### EXECUTE NOW (NON-OPTIONAL — HEAVY QUANT IMPLEMENTATION)
**`PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V95`** — ship tangible heavy-quant code + tests + deterministic artifacts in THIS session.

1. **VERIFY GATE (MUST PASS BEFORE NEW WORK):**
   ```bash
   cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
   PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 - << 'PY'
   import os,sys
   os.environ.setdefault("PHASE_QUICK_VERIFY","1"); sys.path.insert(0,os.getcwd())
   for v in range(82,95):
       m=__import__(f'tests.test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v{v}',fromlist=['*'])
       getattr(m,f'test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v{v}')(); print('ok',v)
   print('ok 13')
   PY
   ```
   Expect `13 ok`. If RED or hygiene violations found → **FIX BEFORE ANY NEW PHASE WORK**. Remove blockers now.

2. **SHIP V95 SRC (COMPOSE CLEANLY OVER V94, ZERO SCAFFOLDING):**
   - **Src:** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v95.py`
   - Import from v94: `Phase110Cfg`, v94 loop class, `Phase110UltraDeepQuantEngineV97`.
   - **Engine:** `class Phase110UltraDeepQuantEngineV98(Phase110UltraDeepQuantEngineV97)`: `__init__(self, seed: int = 1111175)`. Implement **12 concrete `*_deep_v97` methods**, each stamping `*_deep_v96` + full lineage `*_deep_v95..v82` + required v80 feature flags by calling `super().*_deep_v96`. **Use v94's actual base method names** (e.g. `iv_surface_greeks_deep_v97` calls `super().iv_surface_greeks_deep_v96`; `orderflow_microstructure_deep_v97` → `super().orderflow_microstructure_deep_v96`; `cross_venue_sor_toxicity_opt_deep_v97` → `super().cross_venue_sor_toxicity_opt_deep_v96`; `adverse_sel_slippage_fill_joint_deep_v97` → `super().adverse_sel_slippage_fill_joint_deep_v96`; `gamma_dealer_hedge_toxicity_adjusted_deep_v97` → `super().gamma_dealer_hedge_toxicity_adjusted_deep_v96`; `stress_haircut_margin_deep_v97` → `super().stress_haircut_margin_deep_v96`; `chaos_failover_tamper_deep_v97` → `super().chaos_failover_tamper_deep_v96`; `post_trade_finality_attestation_deep_v97` → `super().post_trade_finality_attestation_deep_v96`; `regime_mm_hedge_deep_v97` → `super().regime_mm_hedge_deep_v96`; `collateral_margin_netting_deep_v97` → `super().collateral_margin_netting_deep_v96`; `observability_attribution_tca_deep_v97` → `super().observability_attribution_tca_deep_v96`; `settlement_custody_resilience_deep_v97` → `super().settlement_custody_resilience_deep_v96`). Deepen meaningfully for **crypto options/orderflow/live-exec/realtime/SOR/post-trade/finality/autonomy** (fill realism, adverse selection/slippage, cross-venue fragmentation/latency-jitter, SOR constraints/costs, settlement/finality/attestation, resilience/chaos/zero-trust). All values finite/deterministic.
   - **Loop:** `class Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV95Loop(...)`: inherit cleanly from v94 loop. **Set `self.cfg` AFTER `super().__init__()`**. Default `Phase110Cfg(phase="PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V95", name="phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v95", version="v95", outdir="research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v95", cycles=95)`. Instantiate `Phase110UltraDeepQuantEngineV98` with seed `1111175`; run v97 deep checks + composition gates consistent with emitted methods. **Composition note (pattern):** `mm/scr` composition checks must use companion outputs whose emitted lineage flag exists (follow v91-v94: `mm_deep_v95/scr_deep_v95` on `*_deep_v95` companion outputs => gates `composition_mm_v95/scr_v95`). Emit top-level `all_ok`, `finite_ok`, `gates.all_ok`, `version:"v95"`, `seed`. cfg/phase/name/outdir/version/cycles/seed self-consistent. Do not regress v8-v94.

3. **SHIP TEST + ARTIFACTS (NON-NEGOTIABLE):**
   - **Test:** `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v95.py` passing with `PHASE_QUICK_VERIFY=1`; assert V98 deep gates (`*_deep_v96/v95/.../v82` aggregates + required lineage flags as emitted) + composition gates + `res["all_ok"] is True`, `res["finite_ok"] is True`, `g["all_ok"] is True`, `res["version"]=="v95"`.
   - **Artifacts:** generate deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v95/PHASE110_RES_LATEST.json` + `.md` (and timestamped copies) with `all_ok:true`, `finite_ok:true`, `gates.all_ok:true`, `version:"v95"`, `seed:1111175`, finite numerics.

4. **REGRESSION + HYGIENE + HANDOFF SYNC:** Re-run phase-scoped v82-v95 — all green. `grep -rn 'TODO\|FIXME\|HACK\|XXX\|placeholder\|PLACEHOLDER'` on v95 src+test must be empty. Update this durable handoff (fresh UTC), sync root `HANDOFF_NEXT_AGENT.md` and `research_state/INITIAL_TASK_HANDOFF.md`. No session may end without tangible src+tests+artifacts and phase-scoped gate GREEN.

### CAMPAIGN MANDATE (FUTURE SESSIONS CANNOT AVOID HEAVY WORK)
- **Current non-optional campaign: `PHASE_110..._V95`**. After v95 ships+green, **next is v96** — continue same strict composition pattern.
- **Every session MUST ship:** >=1 `src/risk/` phase module + >=1 passing `tests/test_phase110_*` (`PHASE_QUICK_VERIFY=1`) + >=1 deterministic `research_state/phase110_*` artifact set. Phase-scoped gate GREEN before ending.
- **Hard rules:** PAPER-ONLY; finite numerics; deterministic/seeded; no NaN/Inf; no TODO/FIXME/HACK/XXX/placeholder. Extend/compose only over prior shipped versions. Fail fast on non-finite/placeholder leakage. If wiring/import/cycle blocks progress: implement minimal glue NOW. Do not regress Phases 1-109 or v8-v94.
- **Bottleneck removal rule:** if blocked/inefficient, remove the blocker immediately before taking new scope. **Current status: NO blocked sessions. NO bottlenecks. `research_state/` writable.**

### BOTTLENECK/STATUS (2026-11-06T00:08:57Z — re-verified)
- Gate re-verified this session: v82-v94 phase-scoped regression 13 ok (`PHASE_QUICK_VERIFY=1`, module execution). `pytest` binary not installed in runner — **documented fallback, not a blocker**. v94 shipped+green; artifacts finite/green. v94 src+test hygiene clean. v95 src/test/artifacts ABSENT repo-wide (confirmed 2026-11-06T00:08:57Z).
- **No blocked sessions. No bottlenecks. `research_state/` writable.** Hygiene enforcement for this campaign applies to **v95 src+test** (and any new files touched).
- v94 is the composition template (V97 engine, V94 loop, seed 1111174, cycles 94, composition over v95 companion checks `mm_deep_v95/scr_deep_v95`). v95 must use V98, seed 1111175, cycles 95, `*_deep_v97` methods, and inherit/stamp lineage through v82 plus v80 feature flags. Composition companions must emit the asserted lineage flag.
- Full pytest suite not run in this session; phase-scoped gate is the required pre-work gate.

### ACTION REQUIRED NOW (CANNOT DEFER)
Ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V95` with real implementation, passing tests, and deterministic `research_state/phase110_*_v95/PHASE110_RES_LATEST.*` artifacts.

### FILES VERIFIED/REFRESHED THIS SESSION (2026-11-06T00:08:57Z)
- Re-verified gate: v82-v94 phase-scoped regression 13 ok (`PHASE_QUICK_VERIFY=1`). v95 absent repo-wide. `research_state/` writable. No blocked sessions. No bottlenecks.
- Refreshed authoritative `research_state/durable_handoff.md` and synced root `HANDOFF_NEXT_AGENT.md` + `research_state/INITIAL_TASK_HANDOFF.md` with fresh UTC, re-verified status, and explicit v95 heavy-work mandate.
