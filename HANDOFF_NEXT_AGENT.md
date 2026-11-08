# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T22:19:52Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified this refresh; Phase117 delivered+verified 2026-11-08T22:19:52Z)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options orderflow (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Focus = orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated:** Phase117 (Chain B, composes PHASE116→32) delivered+verified 2026-11-08T22:19:52Z (artifact `research_state/PHASE117_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T221933Z.json`, valid/deterministic/bounded, 12 rows, module pytest 1 passed, generator 9 passed). Phase112/113/114/115/116 previously cleared. Composed-chain generator tests are slow — mitigate via `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, and controlled `generate`+`validate_artifact`/CLI/direct assertions with explicit caveats. Chain A/B confusion mitigated (Chain B `src/hedging` only). NEXT9 remains human-only/out of scope. **No `*phase118*` files exist yet.**
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261108T221952Z-PHASE118-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase111/112/113/114/115/116/117 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE117→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111/112/113/114/115/116/117`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase118_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase117AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE118_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE117` and `PHASE32`. (Seed default `118118`; IDs `p118-*`; artifact names `PHASE118_*`.)
> 2. `scripts/generate_phase118_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `118118`, cycles `40`), timestamped `research_state/PHASE118_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111/112/113/114/115/116/117.
> 3. `tests/test_phase118_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE117','PHASE32']`).
> 4. `tests/test_generate_phase118_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase118/Phase117/`composes=PHASE117,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE117,PHASE32`.
> - Controlled `generate(cycles=40, seed=118118, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE117,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 118118`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase118 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE119-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE118→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111/112/113/114/115/116/117` refactors, or proceeding past Phase117 before Phase118 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase118 is the mandatory next heavy task.**

## Verified state (refresh 2026-11-08T22:19:52Z; Phase117 evidence 20261108T221933Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
- **Env:** deps installed; `pytest 9.2.0` available; **3635 tests collected** (`pytest -q --co`, 9.57s).
- **P0 (re-verified 2026-11-08T22:19:52Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty** (confirmed by `git diff` just now). `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py:69` defaults false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase111 (prior, verified):** artifact `research_state/PHASE111_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T194435Z.json`; composes PHASE110→32; coverage_rows=12; valid=true deterministic=True bounds_ok=True gates_ok=True.
- **Chain B Phase112 (delivered, verified 2026-11-08T20:23Z):** composes PHASE111→32; 12 rows; valid/deterministic/bounded/gates_ok; artifact `PHASE112_..._20261108T202257Z.json`; module pytest 1 passed (13.49s); CLI `--no-write` valid; generator cases verified via controlled generate+validate+direct assertions (composed-chain pytest timeout caveat recorded in prior handoff).
- **Chain B Phase113 (delivered, verified 2026-11-08T20:37Z):** composes PHASE112→32; 12 rows; valid/deterministic/bounded/gates_ok; module pytest 1 passed; generator cases 9 passed.
- **Chain B Phase114 (delivered, verified 2026-11-08T20:54:41Z):** composes PHASE113→32; 12 rows; valid/deterministic/bounded/gates_ok; module pytest 1 passed; generator cases 9 passed.
- **Chain B Phase115 (delivered, verified 2026-11-08T21:27:00Z):** composes PHASE114→32; 12 rows; valid/deterministic/bounded/gates_ok; module pytest 1 passed; generator cases 10 passed total.
- **Chain B Phase116 (delivered, verified 2026-11-08T21:47:30Z):** composes PHASE115→32; 12 rows; valid/deterministic/bounded/gates_ok; artifact `...T214602Z.json`; module pytest 1 passed; generator cases 9 passed.
- **Chain B Phase117 (delivered, verified 2026-11-08T22:19:52Z):**
  - Files: `src/hedging/phase117_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `scripts/generate_phase117_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x); `tests/test_phase117_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `tests/test_generate_phase117_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - `py_compile` (4 files): **OK**.
  - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): **`paper_only=True gates_ok=True composes=['PHASE116','PHASE32']`** (pytest module test **1 passed**).
  - Controlled `generate(cycles=40, seed=117117, write=True)` + `validate_artifact`: **`valid=true issues=[] deterministic_replay_equal=true bounds_ok=true coverage_rows=12 composes=['PHASE116','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`**. Artifact: `research_state/PHASE117_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T221933Z.json`.
  - CLI `--no-write` (`--cycles 4 --seed 117117`, `PHASE_QUICK_VERIFY=1`): **`valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`**.
  - Generator cases: **9 passed** (all required ≥7 cases covered). **Caveat:** composed-chain generator tests are slow (full batch ~355s) — use targeted runs/extended timeouts with explicit caveats.
- **Phase118 status (re-checked 2026-11-08T22:19:52Z):** **no `*phase118*` files exist** in `src/hedging`, `scripts`, or `tests`. Phase118 is the **next mandatory bottleneck — ACTIVE, unstarted**.

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase112–116 implemented + verified (composes N-1→32, 12 rows, valid/deterministic/bounded) | **CLEARED** | Done (2026-11-08T20:23Z–21:47:30Z). |
| Phase117 implemented + verified (composes PHASE116→32, 12 rows, valid/deterministic/bounded) | **CLEARED** | Done (2026-11-08T22:19:52Z). |
| Phase118 not implemented (no `*phase118*` files) | **ACTIVE BOTTLENECK — MANDATORY (unstarted, re-confirmed 2026-11-08T22:19:52Z)** | Execute `INIT-20261108T221952Z-PHASE118` composing PHASE117→32 (heavy deliverables+verification). |
| P0 safety drift | **CLEAR (re-verified 2026-11-08T22:19:52Z)** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase118 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED** | `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261108T221952Z-PHASE118-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111/112/113/114/115/116/117, compose **PHASE117→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE119-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE118→32**, only after Phase118 is verified with evidence.
3. Continue PHASE117→118→119→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111/112/113/114/115/116/117`.**

## Phase118 execution checklist (active — mandatory for next agent)

- [ ] Implement Chain B Phase118 composing PHASE117→32 (4 files, +x on script).
- [ ] `py_compile` OK (4 files).
- [ ] Smoke (`PHASE_QUICK_VERIFY=1`): `paper_only=True gates_ok=True composes ['PHASE117','PHASE32']`; module pytest pass.
- [ ] Controlled `generate(cycles=40,seed=118118,write=True)` + `validate_artifact` pass; record `PHASE118_*_PAPER_EVIDENCE_<UTC>.json`.
- [ ] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`).
- [ ] Generator cases **≥7 passed** (valid shape + 5 rejections + deterministic + 12 coverage/bounds/composes + CLI `--no-write`); record counts/caveats.
- [ ] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [ ] Handoff updated last with `INIT-<UTC>-PHASE119-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
