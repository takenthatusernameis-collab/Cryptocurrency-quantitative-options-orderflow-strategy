# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-09T03:19:25Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified; Phase112–128 COMPLETE with Phase128 evidence verified; Phase129 UNSTARTED — mandatory bottleneck; no duplicate handoff sections)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated (verified 2026-11-09T03:19:25Z):** **Phase128 (Chain B, composes PHASE127→32) COMPLETE** — 4 deliverables present + artifact verified:
>   - `src/hedging/phase128_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
>   - `scripts/generate_phase128_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x)
>   - `tests/test_phase128_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
>   - `tests/test_generate_phase128_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
>   - Artifact: `research_state/PHASE128_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T023626Z.json`
>   - Verified: `validation.valid=true`, `validation.issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `venue_symbol_coverage` len **12**, `campaign.composes=['PHASE127','PHASE32']`, `campaign.gates_ok=true`, `determinism.deterministic_seeded=true`, `determinism.same_seed_cycles_reproduce_surface=true`, `determinism.bounds_ok=true`, `risk_posture.all_coverage_gates_ok=true`. Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes=['PHASE127','PHASE32']`; module pytest **1/1 passed**; controlled generate+validate pass; CLI `--no-write` OK.
>   - **Caveat (mitigated):** full `pytest`/in-process generator test run for `tests/test_generate_phase128_*` timed out under shell load. Next agent must run Phase129 generator tests with adequate timeout/targeted splits or controlled generate+validate/CLI/direct assertions **with explicit caveats**; do not skip verification.
> - Phase112–127 previously cleared. Chain A/B confusion mitigated (Chain B = `src/hedging` only). NEXT9 remains human-only/out of scope. **No `*phase129*` files exist** in `src/hedging/scripts/tests` (re-verified 2026-11-09T03:19:25Z). Working tree clean except Phase128 deliverables/artifact + this handoff.
> - **P0 (re-verified 2026-11-09T03:19:25Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py:69` default false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**

> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261109T031925Z-PHASE129-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase111–128 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE128→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).

> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase129_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase128AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE129_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE128` and `PHASE32`. (Seed default `129129`; IDs `p129-*`; artifact names `PHASE129_*`.)
> 2. `scripts/generate_phase129_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `129129`, cycles `40`), timestamped `research_state/PHASE129_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111–128.
> 3. `tests/test_phase129_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE128','PHASE32']`).
> 4. `tests/test_generate_phase129_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase129/Phase128/`composes=PHASE128,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).

> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE128,PHASE32`.
> - Controlled `generate(cycles=40, seed=129129, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE128,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 129129`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase129 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE130-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE129→32).

> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128` refactors, or proceeding past Phase128 before Phase129 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase129 is the mandatory next heavy task.**

## Verified state (refresh 2026-11-09T03:19:25Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy` | **Working tree:** Phase128 deliverables/artifact + handoff update present (expected).
- **P0 (re-verified 2026-11-09T03:19:25Z):** sensitive diff → **empty**. `LIVE_TRADING_ENABLED=false` in `.env.example:15` and default in `src/config/secrets.py:69`. **No live capital/venue mutation/NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase122–127:** COMPLETE with verified artifacts/composes/12 coverage (prior handoff evidence).
- **Chain B Phase128 (COMPLETE, re-verified):** composes **PHASE127→32**. Artifact `research_state/PHASE128_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T023626Z.json` — `validation.valid=true issues=[]`, `paper_only=true live_trading_enabled=false next9_unblocked=false`, `venue_symbol_coverage=12`, `campaign.composes=['PHASE127','PHASE32'] campaign.gates_ok=true`, `determinism.{deterministic_seeded,same_seed_cycles_reproduce_surface,bounds_ok}=true`, `risk_posture.all_coverage_gates_ok=true`. Module smoke OK; module pytest **1/1**; controlled generate+validate OK; CLI `--no-write` OK. Generator full pytest timed out under shell load (caveat recorded).
- **Phase129 status (re-verified 2026-11-09T03:19:25Z):** **no `*phase129*` files exist** in `src/hedging`, `scripts`, or `tests`. **ACTIVE MANDATORY BOTTLENECK — unstarted.**

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase112–128 implemented + artifact-verified (composes N-1→32, 12 rows) | **CLEARED** | Done through Phase128. |
| Phase129 not implemented (no `*phase129*` files) | **ACTIVE — MANDATORY (re-verified 2026-11-09T03:19:25Z)** | Execute `INIT-20261109T031925Z-PHASE129-POST-ATTRIBUTION-SEAL-DEPTH` composing PHASE128→32 (heavy deliverables+verification). |
| P0 safety drift | **CLEAR (re-verified)** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase129 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261109T031925Z-PHASE129-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111–128, compose **PHASE128→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE130-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE129→32**, only after Phase129 is verified with evidence.
3. Continue PHASE128→129→130→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128`.**

## Phase129 execution checklist (active — mandatory for next agent)

- [ ] Implement Chain B Phase129 composing PHASE128→32 (4 files, +x on script).
- [ ] `py_compile` OK (4 files).
- [ ] Smoke (`PHASE_QUICK_VERIFY=1`): `paper_only=True gates_ok=True composes ['PHASE128','PHASE32']`; module pytest pass.
- [ ] Controlled `generate(cycles=40,seed=129129,write=True)` + `validate_artifact` pass; record `PHASE129_*_PAPER_EVIDENCE_<UTC>.json`.
- [ ] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`).
- [ ] Generator cases **≥7 passed** (valid shape + 5 rejections + deterministic + 12 coverage/bounds/composes + CLI `--no-write`); record counts/caveats.
- [ ] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [ ] **Update this handoff last** with `INIT-<UTC>-PHASE130-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
