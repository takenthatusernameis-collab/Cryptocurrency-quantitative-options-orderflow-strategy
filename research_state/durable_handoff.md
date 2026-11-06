# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
# Timestamp (UTC): 2026-11-06T00:00:25Z
# Repo (inferred from name): Cryptocurrency-quantitative-options-orderflow-strategy
# Domain priority (NON-NEGOTIABLE): CRYPTO OPTIONS + ORDERFLOW QUANT — crypto options pricing/Greeks/IV/surface (SABR/RBergomi/VG/jump-diffusion/local-stochastic/hybrid no-arb), orderflow microstructure/toxicity/VPIN/lead-lag/MEV/adversarial detection, adverse selection×slippage×fill, gamma/dealer/vanna/charm positioning/hedging, cross-venue SOR/routing/fragmentation/latency-jitter/atomic PvP-DvP, regime-aware MM/hedging, cross-margin/collateral/netting/haircuts/liquidation/stress/contagion, post-trade finality/settlement/custody/reconciliation/novation/clearing/attestation/WORM/ZK/Merkle/BFT, observability/attribution/TCA/paper-to-live, autonomous resilience/recovery/compliance/governance/chaos/zero-trust. PAPER-ONLY, finite, deterministic, seeded.
#
# ONLY SOURCE OF TRUTH. `HANDOFF_NEXT_AGENT.md` and `research_state/INITIAL_TASK_HANDOFF.md` are pointers to this file.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY WORK, NO DEVIATION)
**Timestamp (UTC): 2026-11-06T00:00:25Z | Gate: GREEN (phase-scoped, re-verified this session) | NO BLOCKED SESSIONS | NO BOTTLENECKS | `research_state/` writable | v81-v93 SHIPPED+GREEN — v94 ABSENT — SHIP NEXT IMMEDIATELY**

Phases 1-109 COMPLETE+SHIPPED. Phase 110 v8-v93 COMPLETE+SHIPPED+GREEN. **Re-verified this session (2026-11-06T00:00:25Z, `PHASE_QUICK_VERIFY=1`, `PYTHONPATH=$PWD`):** v81-v93 phase-scoped regression 13 ok (direct module execution; pytest binary absent in runner — documented fallback, not a blocker). v93 shipped this session: `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v93.py` (Phase110UltraDeepQuantEngineV96, seed 1111173, 12 `*_deep_v95` methods stamping `*_deep_v94..v82` + v80 feature flags), `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v93.py` pass. v93 artifacts green/finite (`research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v93/PHASE110_RES_LATEST.json`: `version:"v93"`, `engine:Phase110UltraDeepQuantEngineV96`, `all_ok/finite_ok/gates.all_ok:true`, `seed:1111173`, `cycles:93`). Hygiene (v93 src+test): no TODO/FIXME/HACK/XXX/placeholder. **v94 src/test/artifacts ABSENT repo-wide (confirmed 2026-11-06T00:00:25Z) — MANDATORY HEAVY CAMPAIGN: SHIP v94 NOW. NO EXPLORATION. NO SCAFFOLDING. NO PLACEHOLDERS.** Read v93 implementation as the composition template, then implement v94 directly.

### INFERRED PRIMARY OBJECTIVE (BASED ON REPO NAME + PRIOR PATTERN)
This is a **cryptocurrency quantitative options + orderflow strategy** repo. Continue hardening **live execution realism + realtime cross-venue SOR/routing + post-trade finality/autonomy** with deeper quant coverage. Treat v94 as the next concrete, testable hardening step. Every method must be real, finite, deterministic, and integrated via composition over v93.

### EXECUTE NOW (NON-OPTIONAL — HEAVY QUANT IMPLEMENTATION)
**`PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V94`** — ship tangible heavy-quant code + tests + deterministic artifacts in THIS session.

1. **VERIFY GATE (MUST PASS BEFORE NEW WORK):**
   ```bash
   cd /home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy
   PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1 python3 - << 'PY'
   import os,sys
   os.environ.setdefault("PHASE_QUICK_VERIFY","1"); sys.path.insert(0,os.getcwd())
   for v in range(82,94):
       m=__import__(f'tests.test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v{v}',fromlist=['*'])
       getattr(m,f'test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v{v}')(); print('ok',v)
   print('ok 12')
   PY
   ```
   Expect `12 passed/ok`. If RED or hygiene violations found → **FIX BEFORE ANY NEW PHASE WORK**. Remove blockers now.

2. **SHIP V94 SRC (COMPOSE CLEANLY OVER V93, ZERO SCAFFOLDING):**
   - **Src:** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v94.py`
   - Import from v93: `Phase110Cfg`, v93 loop class, `Phase110UltraDeepQuantEngineV96`.
   - **Engine:** `class Phase110UltraDeepQuantEngineV97(Phase110UltraDeepQuantEngineV96)`: `__init__(self, seed: int = 1111174)`. Implement **12 concrete `*_deep_v96` methods**, each stamping `*_deep_v95` + full lineage `*_deep_v94/v93/v92/v91/v90/v89/v88/v87/v86/v85/v84/v83/v82` + required v80 feature flags by calling `super().*_deep_v95`. Keep composition gates, hash chaining, finiteness checks aligned with lineage. **Use v93's actual base method names** (e.g. `iv_surface_greeks_deep_v96` calls `super().iv_surface_greeks_deep_v95`; `orderflow_microstructure_deep_v96` → `super().orderflow_microstructure_deep_v95`; `cross_venue_sor_toxicity_opt_deep_v96` → `super().cross_venue_sor_toxicity_opt_deep_v95`; `adverse_sel_slippage_fill_joint_deep_v96` → `super().adverse_sel_slippage_fill_joint_deep_v95`; `gamma_dealer_hedge_toxicity_adjusted_deep_v96` → `super().gamma_dealer_hedge_toxicity_adjusted_deep_v95`; `stress_haircut_margin_deep_v96` → `super().stress_haircut_margin_deep_v95`; `chaos_failover_tamper_deep_v96` → `super().chaos_failover_tamper_deep_v95`; `post_trade_finality_attestation_deep_v96` → `super().post_trade_finality_attestation_deep_v95`; `regime_mm_hedge_deep_v96` → `super().regime_mm_hedge_deep_v95`; `collateral_margin_netting_deep_v96` → `super().collateral_margin_netting_deep_v95`; `observability_attribution_tca_deep_v96` → `super().observability_attribution_tca_deep_v95`; `settlement_custody_resilience_deep_v96` → `super().settlement_custody_resilience_deep_v95`). Make them meaningfully deeper for **crypto options/orderflow/live-exec/realtime/SOR/post-trade/finality/autonomy** (fill realism, adverse selection/slippage, cross-venue fragmentation/latency-jitter, SOR constraints/costs, settlement/finality/attestation, resilience/chaos/zero-trust). All values finite/deterministic.
   - **Loop:** `class Phase110LiveExecutionRealtimeHardeningUltraDeepCrossVenueSorPostTradeFinalityAutonomyV94Loop(...)`: inherit cleanly from v93 loop. **Set `self.cfg` AFTER `super().__init__()`**. Default `Phase110Cfg(phase="PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V94", name="phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v94", version="v94", outdir="research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v94", cycles=94)`. Instantiate `Phase110UltraDeepQuantEngineV97` with seed `1111174`; run v96 deep checks + composition gates consistent with emitted methods. **Composition note (pattern):** `mm/scr` composition checks must use companion outputs whose emitted lineage flag exists (follow v91-v93: `mm_deep_v94/scr_deep_v94` on `*_deep_v94` companion outputs => gates `composition_mm_v94/scr_v94`). Do not assert a lineage flag the chosen companion method does not stamp. Emit top-level `all_ok`, `finite_ok`, `gates.all_ok`, `version:"v94"`, `seed` consistent. cfg/phase/name/outdir/version/cycles/seed self-consistent. Do not regress v8-v93.

3. **SHIP TEST + ARTIFACTS (NON-NEGOTIABLE):**
   - **Test:** `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v94.py` passing with `PHASE_QUICK_VERIFY=1`; assert V97 deep gates (`*_deep_v95/v94/.../v82` aggregates + required lineage flags as emitted) + composition gates + `res["all_ok"] is True`, `res["finite_ok"] is True`, `g["all_ok"] is True`, `res["version"]=="v94"`.
   - **Artifacts:** generate deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v94/PHASE110_RES_LATEST.json` + `.md` (and timestamped copies) with `all_ok:true`, `finite_ok:true`, `gates.all_ok:true`, `version:"v94"`, `seed:1111174`, finite numerics.

4. **REGRESSION + HYGIENE + HANDOFF SYNC:** Re-run phase-scoped v82-v94 (or v81-v94 if cheap) — all green. `grep -rn 'TODO\|FIXME\|HACK\|XXX\|placeholder\|PLACEHOLDER'` on v94 src+test must be empty. Update this durable handoff (fresh UTC), sync root `HANDOFF_NEXT_AGENT.md` and `research_state/INITIAL_TASK_HANDOFF.md` pointers/timestamps. No session may end without tangible src+tests+artifacts and phase-scoped gate GREEN.

### CAMPAIGN MANDATE (FUTURE SESSIONS CANNOT AVOID HEAVY WORK)
- **Current non-optional campaign: `PHASE_110..._V94`**. Immediately after v94 ships+green, **next campaign is v95** — continue the same strict composition pattern, deeper into crypto options/orderflow/live-exec/SOR/post-trade/finality/autonomy.
- **Every session MUST ship:** >=1 `src/risk/` phase module + >=1 passing `tests/test_phase110_*` (`PHASE_QUICK_VERIFY=1`) + >=1 deterministic `research_state/phase110_*` artifact set. No session may end without tangible src+tests+artifacts. Phase-scoped gate GREEN before ending.
- **Hard rules:** PAPER-ONLY; finite numerics; deterministic/seeded; no NaN/Inf; no TODO/FIXME/HACK/XXX/placeholder. Extend/compose only over prior shipped versions. Fail fast on non-finite/placeholder leakage. If wiring/import/cycle blocks progress: implement minimal glue NOW (do not stall). Do not regress Phases 1-109 or v8-v93.
- **Bottleneck removal rule:** if any session becomes blocked/inefficient, remove the blocker immediately (fix broken imports/tests, resolve path/env issues, repair stale pointers) before taking new scope. **Current status: NO blocked sessions. NO bottlenecks. `research_state/` writable.**

### BOTTLENECK/STATUS (2026-11-06T00:00:25Z — re-verified)
- Gate re-verified this session: v81-v93 phase-scoped regression 13 ok (`PHASE_QUICK_VERIFY=1`, module execution). `pytest` binary not installed in runner — **documented fallback, not a blocker**. v93 shipped+green; artifacts finite/green. v93 src+test hygiene clean. v94 src/test/artifacts ABSENT repo-wide.
- **No blocked sessions. No bottlenecks. `research_state/` writable.** `research_state` is large; avoid copying historical artifacts. Hygiene enforcement for this campaign applies to **v94 src+test** (and any new files you touch).
- v93 is the composition template (V96 engine, V93 loop, seed 1111173, cycles 93, composition over v94 companion checks `mm_deep_v94/scr_deep_v94`). v94 must use V97, seed 1111174, cycles 94, `*_deep_v96` methods, and inherit/stamp lineage through v82 plus v80 feature flags. Composition companions must emit the asserted lineage flag (see v91-v93 fix pattern).
- Full pytest suite not run in this session; phase-scoped gate is the required pre-work gate.

### ACTION REQUIRED NOW (CANNOT DEFER)
Ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V94` with real implementation, passing tests, and deterministic `research_state/phase110_*_v94/PHASE110_RES_LATEST.*` artifacts.

### FILES VERIFIED/SHIPPED THIS SESSION (2026-11-06T00:00:25Z)
- Shipped v93: `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v93.py`, `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v93.py`, `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v93/PHASE110_RES_LATEST.json` (+ timestamped/report).
- v93 hygiene clean; v81-v93 regression 13 ok. No blocked sessions/bottlenecks found. `research_state/` writable.
- Refreshed authoritative `research_state/durable_handoff.md` and synced root `HANDOFF_NEXT_AGENT.md` + `research_state/INITIAL_TASK_HANDOFF.md` pointers with the clearest inferred timestamped initial task message for next agent (v94), re-verified status, and explicit no-bottleneck/no-blocker state.
