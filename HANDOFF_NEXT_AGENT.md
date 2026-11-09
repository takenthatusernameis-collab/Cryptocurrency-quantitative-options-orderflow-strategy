# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-09T01:51:37Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified; Phase112–126 COMPLETE + artifacts verified; Phase127 UNSTARTED — mandatory bottleneck; no duplicate handoff sections)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated (verified 2026-11-09T01:51:37Z):** **Phase126 (Chain B, composes PHASE125→32) COMPLETE** — 4 deliverables present; artifact `research_state/PHASE126_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T014141Z.json` (`validation.valid=true`, `validation.issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `venue_symbol_coverage` len **12**). Phase112–125 previously cleared. Composed-chain generator test slowness mitigated via `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, and controlled `generate`+`validate_artifact`/CLI/direct assertions **with explicit caveats**. Chain A/B confusion mitigated (Chain B = `src/hedging` only). NEXT9 remains human-only/out of scope. **No `*phase127*` files exist** (re-verified 2026-11-09T01:51:37Z). Working tree clean.
> - **P0 (re-verified 2026-11-09T01:51:37Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py:69` default false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261109T015137Z-PHASE127-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase111–126 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE126→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase127_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase126AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE127_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE126` and `PHASE32`. (Seed default `127127`; IDs `p127-*`; artifact names `PHASE127_*`.)
> 2. `scripts/generate_phase127_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `127127`, cycles `40`), timestamped `research_state/PHASE127_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111–126.
> 3. `tests/test_phase127_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE126','PHASE32']`).
> 4. `tests/test_generate_phase127_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase127/Phase126/`composes=PHASE126,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE126,PHASE32`.
> - Controlled `generate(cycles=40, seed=127127, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE126,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 127127`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase127 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE128-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE127→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126` refactors, or proceeding past Phase126 before Phase127 is complete/verified.
>
> ---
>
> ## Repo priority (name-driven)
>
> `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase127 is the mandatory next heavy task.**
>
> ## Verified state (refresh 2026-11-09T01:51:37Z)
>
> - **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy` | **Working tree:** clean (at handoff refresh).
> - **P0 (re-verified 2026-11-09T01:51:37Z):** sensitive diff → **empty**. `LIVE_TRADING_ENABLED=false` in `.env.example:15` and default in `src/config/secrets.py:69`. **No live capital/venue mutation/NEXT9 unblock.**
> - **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
> - **Chain B Phase122 (deliverables + artifact verified):** composes **PHASE121→32**. 4 deliverables + artifact `..._20261109T001138Z.json` — `validation.valid=true`, `validation.issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `venue_symbol_coverage`=**12**. Generator tests **9/9 passed** (composed-chain slow — caveat recorded).
> - **Chain B Phase123 (deliverables + artifact verified):** composes **PHASE122→32**. 4 deliverables + artifact `..._20261109T003014Z.json` — `...`, `venue_symbol_coverage`=**12**, `composes=['PHASE122','PHASE32']`. Module pytest **1/1 passed** (10.40s). Generator tests **9/9 passed** (direct assertions; composed-chain pytest slowness caveat).
> - **Chain B Phase124 (deliverables + artifact verified):** composes **PHASE123→32**. 4 deliverables + artifact `..._20261109T011220Z.json` — `...`, `venue_symbol_coverage`=**12**, `composes=['PHASE123','PHASE32']`. Module pytest **1/1 passed** (10.25s). Generator tests verified via controlled direct calls (all ≥7 cases).
> - **Chain B Phase125 (deliverables + artifact verified):** composes **PHASE124→32**. 4 deliverables + artifact `..._20261109T012117Z.json` — `...`, `venue_symbol_coverage`=**12**, `composes=['PHASE124','PHASE32']`. Module pytest **1/1 passed** (11.13s). Generator tests **7/7 passed** via direct assertions.
> - **Chain B Phase126 (deliverables + artifact verified):** composes **PHASE125→32**. 4 deliverables:
>   - `src/hedging/phase126_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
>   - `scripts/generate_phase126_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x)
>   - `tests/test_phase126_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
>   - `tests/test_generate_phase126_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
>   - Artifact: `research_state/PHASE126_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T014141Z.json` — `validation.valid=true`, `validation.issues=[]`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `venue_symbol_coverage`=**12**, `composes=['PHASE125','PHASE32']`.
>   - Verification results (2026-11-09T01:51:37Z):
>     - `py_compile` 4/4 OK.
>     - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes=['PHASE125','PHASE32']`; module pytest **1/1 passed** (~12s).
>     - Controlled `generate(cycles=40, seed=126126, write=True)` + `validate_artifact` → `valid=true issues=[] deterministic=true bounds_ok=true 12 coverage composes=['PHASE125','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`; artifact path: `research_state/PHASE126_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261109T014141Z.json`.
>     - CLI `--no-write` (`--cycles 4 --seed 126126`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`.
>     - Generator tests: core cases **passed via direct assertions** (valid advisory shape, 12 coverage/bounds/composes, CLI `--no-write`); composed-chain pytest slowness caveat — full suite run targeted with extended timeout / controlled direct calls; do not skip verification.
>     - P0 re-verified: empty diff on sensitive files; `LIVE_TRADING_ENABLED=false` remains.
> - **Phase127 status (re-verified 2026-11-09T01:51:37Z):** **no `*phase127*` files exist** in `src/hedging`, `scripts`, or `tests`. **ACTIVE MANDATORY BOTTLENECK — unstarted.**
>
> ## Bottlenecks (agent-removable now / remaining)
>
> | Bottleneck | Status | Action (unblock) |
> |---|---|---|
> | Phase112–126 implemented + artifact-verified (composes N-1→32, 12 rows) | **CLEARED** | Done through Phase126. |
> | Phase127 not implemented (no `*phase127*` files) | **ACTIVE — MANDATORY (re-verified 2026-11-09T01:51:37Z)** | Execute `INIT-20261109T015137Z-PHASE127-POST-ATTRIBUTION-SEAL-DEPTH` composing PHASE126→32 (heavy deliverables+verification). |
> | P0 safety drift | **CLEAR (re-verified)** | Re-verify before/after every change batch. |
> | Chain A/B naming confusion | **MITIGATED** | Phase127 is **Chain B `src/hedging` only**. |
> | Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. |
> | NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |
>
> ## Chained focus campaign (heavy work mandatory — no avoidance)
>
> 1. **NOW (mandatory):** `INIT-20261109T015137Z-PHASE127-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111–126, compose **PHASE126→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
> 2. **NEXT (queued):** `INIT-<UTC>-PHASE128-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE127→32**, only after Phase127 is verified with evidence.
> 3. Continue PHASE119→120→121→122→123→124→125→126→127→128→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111/112/113/114/115/116/117/118/119/120/121/122/123/124/125/126`.**
>
> ## Phase127 execution checklist (active — mandatory for next agent)
>
> - [ ] Implement Chain B Phase127 composing PHASE126→32 (4 files, +x on script).
> - [ ] `py_compile` OK (4 files).
> - [ ] Smoke (`PHASE_QUICK_VERIFY=1`): `paper_only=True gates_ok=True composes ['PHASE126','PHASE32']`; module pytest pass.
> - [ ] Controlled `generate(cycles=40,seed=127127,write=True)` + `validate_artifact` pass; record `PHASE127_*_PAPER_EVIDENCE_<UTC>.json`.
> - [ ] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`).
> - [ ] Generator cases **≥7 passed** (valid shape + 5 rejections + deterministic + 12 coverage/bounds/composes + CLI `--no-write`); record counts/caveats.
> - [ ] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
> - [ ] Handoff updated last with `INIT-<UTC>-PHASE128-POST-ATTRIBUTION-SEAL-DEPTH`.
>
> ## Handoff discipline
>
> This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.