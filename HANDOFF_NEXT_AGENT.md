# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-09T03:24:31Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified clean; Phase112–128 COMPLETE with Phase128 artifact sanity-checked; Phase129 UNSTARTED — mandatory bottleneck; no duplicate handoff sections)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated (verified 2026-11-09T03:24:31Z):**
>   - **P0 clear:** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example` sets `LIVE_TRADING_ENABLED=false`; `src/config/secrets.py` default false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
>   - **Phase128 (Chain B) COMPLETE:** 4 deliverables present in `src/hedging/`, `scripts/`, `tests/` (+x script). Artifact exists: `research_state/PHASE128_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T023626Z.json` (sanity-checked: `validation.valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `composes=['PHASE127','PHASE32']`, `gates_ok=true`, `venue_symbol_coverage` len **12**).
>   - **Phase129 absent (re-verified):** `find src/hedging scripts tests -maxdepth 1 -name '*phase129*'` → **0 files**. This is the **only active agent-removable bottleneck**.
>   - **Chain A/B confusion mitigated:** Phase129 is **Chain B `src/hedging` only**. No `src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*` substitution.
>   - **NEXT9 (A1–A7, human-only, session gate NO_GO, `next9_unblocked=false`)** remains out of scope and does **not** gate paper-only Chain B depth.
>   - **Composed-chain generator test caveat (from Phase128):** full pytest/in-process generator runs can time out under shell load. Use `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, or controlled `generate+validate`/CLI/direct assertions **with explicit caveats**; **never skip verification**.
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261109T032431Z-PHASE129-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase111–128 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE128→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128`. NO Chain A substitution.**
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase129_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase128AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE129_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE128` and `PHASE32`. (Seed default `129129`; IDs `p129-*`; artifact names `PHASE129_*`.)
> 2. `scripts/generate_phase129_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `129129`, cycles `40`), timestamped `research_state/PHASE129_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111–128.
> 3. `tests/test_phase129_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE128','PHASE32']`).
> 4. `tests/test_generate_phase129_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase129/Phase128/`composes=PHASE128,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE128,PHASE32`.
> - Controlled `generate(cycles=40, seed=129129, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE128,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 129129`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase129 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE130-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE129→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128` refactors, or proceeding past Phase128 before Phase129 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase129 is the mandatory next heavy task.**

## Verified state (refresh 2026-11-09T03:24:31Z)

- **Branch:** `main` (git repo present). **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`. **Working tree (at refresh check):** clean.
- **P0 (re-verified 2026-11-09T03:24:31Z):** sensitive diff → **empty**. `LIVE_TRADING_ENABLED=false` in `.env.example` and default in `src/config/secrets.py`. **No live capital/venue mutation/NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase112–128:** COMPLETE with Phase128 artifact sanity-checked (`valid=true`, composes PHASE127→32, 12 coverage, guards intact).
- **Phase129 status (re-verified 2026-11-09T03:24:31Z):** **no `*phase129*` files** in `src/hedging`, `scripts`, or `tests`. **ACTIVE MANDATORY BOTTLENECK — unstarted.**

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase112–128 implemented + artifact-verified (composes N-1→32, 12 rows) | **CLEARED** | Done through Phase128. |
| Phase129 not implemented (no `*phase129*` files) | **ACTIVE — MANDATORY (re-verified 2026-11-09T03:24:31Z)** | Execute `INIT-20261109T032431Z-PHASE129-POST-ATTRIBUTION-SEAL-DEPTH` composing PHASE128→32 (heavy deliverables+verification). |
| P0 safety drift | **CLEAR (re-verified)** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase129 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261109T032431Z-PHASE129-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111–128, compose **PHASE128→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
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
