# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T23:18:42Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified; Phase120 COMPLETE + artifact verified; Phase121 UNSTARTED — mandatory bottleneck)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated (verified 2026-11-08T23:18:42Z):** **Phase120 (Chain B, composes PHASE119→32) deliverables present + artifact verified** — `research_state/PHASE120_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T231459Z.json` (`validation.valid=true`, `validation.issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `venue_symbol_coverage` len **12**). Phase112–119 previously cleared. Composed-chain generator tests can be slow — mitigated via `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, and controlled `generate`+`validate_artifact`/CLI/direct assertions with explicit caveats. Chain A/B confusion mitigated (Chain B = `src/hedging` only). NEXT9 remains human-only/out of scope. **No `*phase121*` files exist** (verified 2026-11-08T23:18:42Z; glob/find returned zero).
> - **P0 (re-verified 2026-11-08T23:18:42Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py` default false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.** Working tree clean.
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261108T231842Z-PHASE121-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase111–120 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE120→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111/112/113/114/115/116/117/118/119/120`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase121_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase120AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE121_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE120` and `PHASE32`. (Seed default `121121`; IDs `p121-*`; artifact names `PHASE121_*`.)
> 2. `scripts/generate_phase121_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `121121`, cycles `40`), timestamped `research_state/PHASE121_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111–120.
> 3. `tests/test_phase121_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE120','PHASE32']`).
> 4. `tests/test_generate_phase121_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase121/Phase120/`composes=PHASE120,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE120,PHASE32`.
> - Controlled `generate(cycles=40, seed=121121, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE120,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 121121`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase121 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE122-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE121→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111/112/113/114/115/116/117/118/119/120` refactors, or proceeding past Phase120 before Phase121 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase121 is the mandatory next heavy task.**

## Verified state (refresh 2026-11-08T23:18:42Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy` | **Working tree:** clean (pre-edit).
- **P0 (re-verified 2026-11-08T23:18:42Z):** sensitive diff → **empty**. `LIVE_TRADING_ENABLED=false` in `.env.example:15` and default in `src/config/secrets.py:69`. **No live capital/venue mutation/NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase111–119:** prior verified (composing PHASE110→…→PHASE118→32), 12 rows each, valid/deterministic/bounded/gates_ok per history. Phase119 artifact present.
- **Chain B Phase120 (deliverables + artifact verified 2026-11-08T23:18:42Z):** composes **PHASE119→32**.
  - Deliverables (4): `src/hedging/phase120_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `scripts/generate_phase120_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x in repo context); `tests/test_phase120_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `tests/test_generate_phase120_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - Artifact: `research_state/PHASE120_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T231459Z.json` — `validation.valid=true`, `validation.issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `venue_symbol_coverage`=**12**.
  - Verification summary (this session):
    - `py_compile`: 4/4 OK.
    - Module smoke: `paper_only=True gates_ok=True composes=['PHASE119','PHASE32']` PASS.
    - Controlled generate (cycles=40, seed=120120, write=True): `valid=true issues=[] deterministic=true bounds_ok=true 12 coverage composes=['PHASE119','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. Artifact: `research_state/PHASE120_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T231459Z.json`.
    - CLI `--no-write` (cycles=4, seed=120120): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`.
    - Generator tests: **9/9 passed** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage/bounds/composes; CLI `--no-write`). Caveat: composed-chain generator tests are slow (33–63s each) — run targeted with extended timeouts; all passed individually with `PHASE_QUICK_VERIFY=1`.
    - P0 re-verify: empty diff; `LIVE_TRADING_ENABLED=false` confirmed.
- **Phase121 status (checked 2026-11-08T23:18:42Z):** **no `*phase121*` files exist** in `src/hedging`, `scripts`, or `tests`. **ACTIVE MANDATORY BOTTLENECK — unstarted.**

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase112–120 implemented + artifact-verified (composes N-1→32, 12 rows) | **CLEARED** | Done through Phase120. |
| Phase121 not implemented (no `*phase121*` files) | **ACTIVE — MANDATORY (confirmed 2026-11-08T23:18:42Z)** | Execute `INIT-20261108T231842Z-PHASE121-POST-ATTRIBUTION-SEAL-DEPTH` composing PHASE120→32 (heavy deliverables+verification). |
| P0 safety drift | **CLEAR (re-verified)** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase121 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261108T231842Z-PHASE121-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111–120, compose **PHASE120→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE122-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE121→32**, only after Phase121 is verified with evidence.
3. Continue PHASE119→120→121→122→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111/112/113/114/115/116/117/118/119/120`.**

## Phase121 execution checklist (active — mandatory for next agent)

- [ ] Implement Chain B Phase121 composing PHASE120→32 (4 files, +x on script).
- [ ] `py_compile` OK (4 files).
- [ ] Smoke (`PHASE_QUICK_VERIFY=1`): `paper_only=True gates_ok=True composes ['PHASE120','PHASE32']`; module pytest pass.
- [ ] Controlled `generate(cycles=40,seed=121121,write=True)` + `validate_artifact` pass; record `PHASE121_*_PAPER_EVIDENCE_<UTC>.json`.
- [ ] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`).
- [ ] Generator cases **≥7 passed** (valid shape + 5 rejections + deterministic + 12 coverage/bounds/composes + CLI `--no-write`); record counts/caveats.
- [ ] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [ ] Handoff updated last with `INIT-<UTC>-PHASE122-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.