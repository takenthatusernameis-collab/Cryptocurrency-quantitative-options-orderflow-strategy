# SINGLE DURABLE HANDOFF (AUTHORITATIVE — READ FIRST)
**Timestamp (UTC): 2026-11-06T00:58:30Z**
**Repo (inferred):** `Cryptocurrency-quantitative-options-orderflow-strategy` (crypto options + orderflow quantitative strategy)

**Status (re-verified this session, 2026-11-06T00:58:30Z):**
- Gate: **GREEN** (phase-scoped). `PYTHONPATH=$PWD PHASE_QUICK_VERIFY=1` module regression **v82–v95 = 14 ok**. `pytest` binary not installed in runner — documented fallback, **not a blocker**.
- v95 shipped+green/finite: `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v95/PHASE110_RES_LATEST.json` (`version:"v95"`, `engine:Phase110UltraDeepQuantEngineV98`, `all_ok/finite_ok/gates.all_ok:true`, `seed:1111175`, `cycles:95`).
- **v96 ABSENT** repo-wide (src/tests/research_state) — confirmed 2026-11-06T00:58:30Z.
- **No blocked sessions. No bottlenecks. `research_state/` writable.**
- Hygiene (v95 src+test): clean. Hygiene enforcement for this campaign applies to **v96 src+test** and any new files.

This file is the **only** source of truth. `HANDOFF_NEXT_AGENT.md` and `research_state/INITIAL_TASK_HANDOFF.md` are pointers.

## CRYSTAL-CLEAR INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (MANDATORY, HEAVY, NO DEVIATION)
**Ship `PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V96` NOW.** No exploration. No scaffolding. No placeholders. Read v95 as the composition template, then implement v96 directly.

### Domain priority (NON-NEGOTIABLE)
Crypto options pricing/Greeks/IV/surface (SABR/RBergomi/VG/jump-diffusion/local-stochastic/hybrid no-arb), orderflow microstructure/toxicity/VPIN/lead-lag/MEV/adversarial detection, adverse selection×slippage×fill, gamma/dealer/vanna/charm positioning/hedging, cross-venue SOR/routing/fragmentation/latency-jitter/atomic PvP-DvP, regime-aware MM/hedging, cross-margin/collateral/netting/haircuts/liquidation/stress/contagion, post-trade finality/settlement/custody/reconciliation/novation/clearing/attestation/WORM/ZK/Merkle/BFT, observability/attribution/TCA/paper-to-live, autonomous resilience/recovery/compliance/governance/chaos/zero-trust. **PAPER-ONLY, finite, deterministic, seeded.**

### 1) Verify gate before new work (must pass)
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
Expect `14 ok`. If RED or hygiene violations found → **fix before any new phase work**.

### 2) Ship v96 src (compose over v95; zero scaffolding)
- **Src:** `src/risk/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96.py`
- Import from v95: `Phase110Cfg`, v95 loop class, `Phase110UltraDeepQuantEngineV98`.
- **Engine:** `class Phase110UltraDeepQuantEngineV99(Phase110UltraDeepQuantEngineV98)`, `__init__(self, seed: int = 1111176)`. Implement **12 concrete `*_deep_v98` methods**; each must stamp `*_deep_v97` + full lineage `*_deep_v96..v82` + required v80 feature flags by calling the corresponding `super().*_deep_v97` (follow v95 base names: `iv_surface_greeks_deep_v98`→`iv_surface_greeks_deep_v97`, `orderflow_microstructure_deep_v98`→`orderflow_microstructure_deep_v97`, `cross_venue_sor_toxicity_opt_deep_v98`→`cross_venue_sor_toxicity_opt_deep_v97`, `adverse_sel_slippage_fill_joint_deep_v98`→`adverse_sel_slippage_fill_joint_deep_v97`, `gamma_dealer_hedge_toxicity_adjusted_deep_v98`→`gamma_dealer_hedge_toxicity_adjusted_deep_v97`, `stress_haircut_margin_deep_v98`→`stress_haircut_margin_deep_v97`, `chaos_failover_tamper_deep_v98`→`chaos_failover_tamper_deep_v97`, `post_trade_finality_attestation_deep_v98`→`post_trade_finality_attestation_deep_v97`, `regime_mm_hedge_deep_v98`→`regime_mm_hedge_deep_v97`, `collateral_margin_netting_deep_v98`→`collateral_margin_netting_deep_v97`, `observability_attribution_tca_deep_v98`→`observability_attribution_tca_deep_v97`, `settlement_custody_resilience_deep_v98`→`settlement_custody_resilience_deep_v97`). Deepen meaningfully for crypto options/orderflow/live-exec/realtime/SOR/post-trade/finality/autonomy. All values finite/deterministic.
- **Loop:** inherit cleanly from v95; **set `self.cfg` AFTER `super().__init__()`**. Default `Phase110Cfg(phase="PHASE_110_LIVE_EXECUTION_REALTIME_HARDENING_ULTRA_DEEP_CROSSVENUE_SOR_POSTTRADE_FINALITY_AUTONOMY_V96", name="phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96", version="v96", outdir="research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96", cycles=96)`. Instantiate `Phase110UltraDeepQuantEngineV99(seed=1111176)`. Run v98 deep checks + composition gates consistent with emitted methods. **Composition pattern (v91-v95):** `mm/scr` gates must reference companion outputs whose lineage flag is emitted (e.g., `mm_deep_v96/scr_deep_v96` on `*_deep_v96` companions => `composition_mm_v96/scr_v96`). Emit `all_ok`, `finite_ok`, `gates.all_ok`, `version:"v96"`, `seed`. Do not regress v8–v95.

### 3) Ship test + deterministic artifacts
- **Test:** `tests/test_phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96.py` passing with `PHASE_QUICK_VERIFY=1`; assert V99 deep gates (`*_deep_v97/v96/.../v82` aggregates + required lineage flags as emitted) + composition gates + `res["all_ok"] is True`, `res["finite_ok"] is True`, `g["all_ok"] is True`, `res["version"]=="v96"`.
- **Artifacts:** deterministic `research_state/phase110_live_execution_realtime_hardening_ultra_deep_cross_venue_sor_post_trade_finality_autonomy_v96/PHASE110_RES_LATEST.json` + `.md` (+ timestamped copies) with `all_ok:true`, `finite_ok:true`, `gates.all_ok:true`, `version:"v96"`, `seed:1111176`, finite numerics.

### 4) Regression + hygiene + handoff sync (before ending session)
- Re-run phase-scoped **v82–v96** — all green.
- `grep -rn 'TODO\|FIXME\|HACK\|XXX\|placeholder\|PLACEHOLDER'` on v96 src+test must be empty.
- Update this durable handoff (fresh UTC), sync root `HANDOFF_NEXT_AGENT.md` and `research_state/INITIAL_TASK_HANDOFF.md`. No session may end without tangible src+tests+artifacts and phase-scoped gate GREEN.

### Campaign mandate (future sessions cannot avoid heavy work)
- After v96 ships+green, **next is v97** (same strict composition pattern).
- **Every session MUST ship:** >=1 `src/risk/` phase module + >=1 passing `tests/test_phase110_*` (`PHASE_QUICK_VERIFY=1`) + >=1 deterministic `research_state/phase110_*` artifact set.
- **Hard rules:** PAPER-ONLY; finite numerics; deterministic/seeded; no NaN/Inf; no TODO/FIXME/HACK/XXX/placeholder. Extend/compose only over prior shipped versions. Fail fast on non-finite/placeholder leakage. If wiring/import/cycle blocks progress: implement minimal glue NOW. Do not regress Phases 1–109 or v8–v95.
- **Bottleneck removal:** if blocked/inefficient, remove the blocker immediately before taking new scope. Current status: none.

### Files verified/refreshed this session (2026-11-06T00:58:30Z)
- Re-verified gate: v82–v95 = 14 ok (`PHASE_QUICK_VERIFY=1`). v96 absent repo-wide. `research_state/` writable. No blocked sessions/bottlenecks.
- Refreshed `research_state/durable_handoff.md`; synced `HANDOFF_NEXT_AGENT.md` and `research_state/INITIAL_TASK_HANDOFF.md`.
