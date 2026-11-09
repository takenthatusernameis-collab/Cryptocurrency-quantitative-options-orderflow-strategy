# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-09T00:23:46Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified; Phase122 COMPLETE + artifact verified; Phase123 UNSTARTED — mandatory bottleneck; no duplicate handoff sections)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated (verified 2026-11-09T00:23:46Z):** **Phase122 (Chain B, composes PHASE121→32) COMPLETE** — 4 deliverables present; artifact `research_state/PHASE122_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T001138Z.json` (`validation.valid=true`, `validation.issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `venue_symbol_coverage` len **12**). Phase112–121 previously cleared. Composed-chain generator test slowness mitigated via `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, and controlled `generate`+`validate_artifact`/CLI/direct assertions **with explicit caveats**. Chain A/B confusion mitigated (Chain B = `src/hedging` only). NEXT9 remains human-only/out of scope. **No `*phase123*` files exist** (re-verified 2026-11-09T00:23:46Z). Working tree clean.
> - **P0 (re-verified 2026-11-09T00:23:46Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py:69` default false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261109T002346Z-PHASE123-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase111–122 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE122→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase123_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase122AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE123_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE122` and `PHASE32`. (Seed default `123123`; IDs `p123-*`; artifact names `PHASE123_*`.)
> 2. `scripts/generate_phase123_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `123123`, cycles `40`), timestamped `research_state/PHASE123_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111–122.
> 3. `tests/test_phase123_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE122','PHASE32']`).
> 4. `tests/test_generate_phase123_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase123/Phase122/`composes=PHASE122,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE122,PHASE32`.
> - Controlled `generate(cycles=40, seed=123123, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE122,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 123123`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase123 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE124-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE123→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122` refactors, or proceeding past Phase122 before Phase123 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase123 is the mandatory next heavy task.**

## Verified state (refresh 2026-11-09T00:23:46Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy` | **Working tree:** clean (at handoff refresh).
- **P0 (re-verified 2026-11-09T00:23:46Z):** sensitive diff → **empty**. `LIVE_TRADING_ENABLED=false` in `.env.example:15` and default in `src/config/secrets.py:69`. **No live capital/venue mutation/NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase122 (deliverables + artifact verified):** composes **PHASE121→32**.
  - Deliverables (4): `src/hedging/phase122_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `scripts/generate_phase122_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; `tests/test_phase122_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `tests/test_generate_phase122_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - Artifact: `research_state/PHASE122_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T001138Z.json` — `validation.valid=true`, `validation.issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `venue_symbol_coverage`=**12**.
  - Prior evidence (from handoff history): `py_compile` 4/4 OK; module smoke `paper_only=True gates_ok=True composes=['PHASE121','PHASE32']`; controlled generate (cycles=40, seed=122122) `valid=true issues=[] deterministic=true bounds_ok=true 12 coverage composes=['PHASE121','PHASE32']`; CLI `--no-write` `valid=true artifact_path=null`; generator tests **9/9 passed** (composed-chain slow — caveat recorded).
- **Phase123 status (re-verified 2026-11-09T00:23:46Z):** **no `*phase123*` files exist** in `src/hedging`, `scripts`, or `tests`. **ACTIVE MANDATORY BOTTLENECK — unstarted.**

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase112–122 implemented + artifact-verified (composes N-1→32, 12 rows) | **CLEARED** | Done through Phase122. |
| Phase123 not implemented (no `*phase123*` files) | **ACTIVE — MANDATORY (re-verified 2026-11-09T00:23:46Z)** | Execute `INIT-20261109T002346Z-PHASE123-POST-ATTRIBUTION-SEAL-DEPTH` composing PHASE122→32 (heavy deliverables+verification). |
| P0 safety drift | **CLEAR (re-verified)** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase123 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261109T002346Z-PHASE123-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111–122, compose **PHASE122→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE124-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE123→32**, only after Phase123 is verified with evidence.
3. Continue PHASE119→120→121→122→123→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122`.**

## Phase123 execution checklist (active — mandatory for next agent)

- [ ] Implement Chain B Phase123 composing PHASE122→32 (4 files, +x on script).
- [ ] `py_compile` OK (4 files).
- [ ] Smoke (`PHASE_QUICK_VERIFY=1`): `paper_only=True gates_ok=True composes ['PHASE122','PHASE32']`; module pytest pass.
- [ ] Controlled `generate(cycles=40,seed=123123,write=True)` + `validate_artifact` pass; record `PHASE123_*_PAPER_EVIDENCE_<UTC>.json`.
- [ ] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`).
- [ ] Generator cases **≥7 passed** (valid shape + 5 rejections + deterministic + 12 coverage/bounds/composes + CLI `--no-write`); record counts/caveats.
- [ ] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [ ] Handoff updated last with `INIT-<UTC>-PHASE124-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
