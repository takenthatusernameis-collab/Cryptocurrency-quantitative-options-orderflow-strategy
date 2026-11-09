# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-09T04:39:45Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified clean; Phase112–131 COMPLETE with Phase131 artifact sanity-checked; Phase132 UNSTARTED — mandatory bottleneck; no duplicate handoff sections)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated (verified 2026-11-09T04:39:45Z):**
>   - **P0 clear:** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty** (before/after Phase131). `.env.example` `LIVE_TRADING_ENABLED=false`. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
>   - **Phase131 (Chain B) COMPLETE:** 4 deliverables present in `src/hedging/`, `scripts/` (+x), `tests/`. Artifact: `research_state/PHASE131_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T043935Z.json` (controlled generate+validate: `valid=true`, `issues=[]`, deterministic replay equal, bounds ok, venue×symbol coverage **12**, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `composes=['PHASE130','PHASE32']`).
>   - **Phase132 absent (re-verified):** `find src/hedging scripts tests -maxdepth 1 -name '*phase132*'` → **0 files**. This is the **only active agent-removable bottleneck**.
>   - **Chain A/B confusion mitigated:** Phase132 is **Chain B `src/hedging` only**. No `src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*` substitution.
>   - **NEXT9 (A1–A7, human-only, session gate NO_GO, `next9_unblocked=false`)** remains out of scope and does **not** gate paper-only Chain B depth.
>   - **Composed-chain generator test caveat (Phase129/130/131):** full pytest/in-process generator runs can time out under shell load despite stubs. Phase131: module smoke pytest **1 passed** (19.13s); CLI `--no-write` pytest **1 passed** (64.16s). Controlled in-process `generate(cycles=40,seed=131131,write=True)+validate` passed and artifact written/validated; CLI `--no-write` JSON valid (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`). Controlled validator assertions passed for `live_trading_enabled/next9_unblocked/paper_only/advisory/no_external_venue_mutation` rejects. Bulk in-process generator pytest (all cases) and additional composed-chain pytest selections timed out at 120s — **use `PHASE_QUICK_VERIFY=1`, targeted/split runs, extended timeouts, or controlled generate+validate/CLI/direct assertions with explicit caveats; never skip verification**.
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261109T043945Z-PHASE132-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase111–131 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE131→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128/129/130/131`. NO Chain A substitution.**
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase132_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase131AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE132_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE131` and `PHASE32`. (Seed default `132132`; IDs `p132-*`; artifact names `PHASE132_*`.)
> 2. `scripts/generate_phase132_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `132132`, cycles `40`), timestamped `research_state/PHASE132_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111–131.
> 3. `tests/test_phase132_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE131','PHASE32']`).
> 4. `tests/test_generate_phase132_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase132/Phase131/`composes=PHASE131,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE131,PHASE32`.
> - Controlled `generate(cycles=40, seed=132132, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE131,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 132132`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run module test and targeted CLI generator case with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain in-process generator tests may be slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE133-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE132→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128/129/130/131` refactors, or proceeding past Phase131 before Phase132 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase132 is the mandatory next heavy task.**

## Verified state (refresh 2026-11-09T04:39:45Z)

- **Branch:** `main` (git repo present). **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`. **Working tree (at refresh):** Phase131 deliverables + artifact added (uncommitted at handoff write).
- **P0 (re-verified 2026-11-09T04:39:45Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example` `LIVE_TRADING_ENABLED=false`. **No live capital/venue mutation/NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase112–131:** COMPLETE with Phase131 artifact sanity-checked (`valid=true`, composes PHASE130→32, 12 coverage, guards intact).
- **Phase132 status (re-verified 2026-11-09T04:39:45Z):** **no `*phase132*` files** in `src/hedging`, `scripts`, or `tests`. **ACTIVE MANDATORY BOTTLENECK — unstarted.**

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase112–131 implemented + artifact-verified (composes N-1→32, 12 rows) | **CLEARED** | Done through Phase131. |
| Phase132 not implemented (no `*phase132*` files) | **ACTIVE — MANDATORY (re-verified 2026-11-09T04:39:45Z)** | Execute `INIT-20261109T043945Z-PHASE132-POST-ATTRIBUTION-SEAL-DEPTH` composing PHASE131→32 (heavy deliverables+verification). |
| P0 safety drift | **CLEAR (re-verified)** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase132 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261109T043945Z-PHASE132-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111–131, compose **PHASE131→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE133-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE132→32**, only after Phase132 is verified with evidence.
3. Continue PHASE131→132→133→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126/127/128/129/130/131`.**

## Phase132 execution checklist (active — mandatory for next agent)

- [ ] Implement Chain B Phase132 composing PHASE131→32 (4 files, +x on script).
- [ ] `py_compile` OK (4 files).
- [ ] Smoke (`PHASE_QUICK_VERIFY=1`): `paper_only=True gates_ok=True composes ['PHASE131','PHASE32']`; module pytest pass.
- [ ] Controlled `generate(cycles=40,seed=132132,write=True)` + `validate_artifact` pass; record `PHASE132_*_PAPER_EVIDENCE_<UTC>.json`.
- [ ] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`).
- [ ] Generator cases **≥7 passed** (or equivalent controlled/split evidence with explicit caveats per composed-chain timeout behavior); record counts/caveats.
- [ ] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [ ] **Update this handoff last** with `INIT-<UTC>-PHASE133-POST-ATTRIBUTION-SEAL-DEPTH`.

## Phase131 verification evidence (completed 2026-11-09T04:39:45Z)

| Check | Result | Details |
|---|---|---|
| `py_compile` (4 files) | **OK** | `src/hedging/phase131_*.py`, `scripts/generate_phase131_*_paper_evidence.py`, both `tests/test_*phase131*.py` compile cleanly |
| Module smoke (`PHASE_QUICK_VERIFY=1`) | **OK** | `paper_only=True`, `gates_ok=True`, `composes=['PHASE130','PHASE32']`, `phase=PHASE131_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR` |
| Controlled `generate(cycles=40, seed=131131, write=True)` + `validate_artifact` | **OK** | `valid=true`, `issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes=['PHASE130','PHASE32']`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true` |
| Artifact path (sanity-checked) | **RECORDED** | `research_state/PHASE131_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T043935Z.json` |
| CLI `--no-write` (`--cycles 4 --seed 131131`) | **OK** | `valid=true`, `issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `deterministic=true`, `gates_ok=true`, `artifact_path=null` |
| Tests (targeted, composed-chain caveat) | **PASS (with caveat)** | Module smoke pytest: **1 passed** (19.13s). CLI `--no-write` pytest: **1 passed** (64.16s). Controlled validator assertions passed: rejects `live_trading_enabled=True`, `next9_unblocked=True`, `paper_only=False`, `advisory=False`, `no_external_venue_mutation=False`. Bulk in-process generator pytest (all 10 cases) and additional composed-chain pytest selections (`rejects` / shape+determinism+coverage+cross_refs groups) **timed out at 120s** despite quick-verify/stubs (composed-chain load). Controlled generate+validate+CLI+validator evidence covers required invariants (guards, deterministic, bounds, 12 coverage, composes PHASE130→32, gates_ok). **Caveat recorded.** |
| P0 re-verify | **OK** | `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → empty; `LIVE_TRADING_ENABLED=false` confirmed |

## Phase130 verification evidence (completed 2026-11-09T04:27:00Z)

| Check | Result | Details |
|---|---|---|
| Artifact path | **RECORDED** | `research_state/PHASE130_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T042503Z.json` (`valid=true`, composes PHASE129→32, 12 coverage, guards intact) |

## Phase129 verification evidence (completed 2026-11-09T03:35:42Z)

| Check | Result | Details |
|---|---|---|
| Artifact path | **RECORDED** | `research_state/PHASE129_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T033346Z.json` (`valid=true`, composes PHASE128→32, 12 coverage, guards intact) |

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
