# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T20:54:42Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified this refresh; Phase114 verified 2026-11-08T20:54:41Z)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options orderflow (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Focus = orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated:** Phase114 (Chain B, composes PHASE113→32) delivered+verified 2026-11-08T20:54:41Z (artifact `research_state/PHASE114_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T205441Z.json`, valid/deterministic/bounded, 12 rows, module pytest 1 passed, generator 9 passed). Phase112/113 previously cleared. Composed-chain generator tests are slow — mitigate via `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, and controlled `generate`+`validate_artifact`/CLI/direct assertions with explicit caveats. Chain A/B confusion mitigated (Chain B `src/hedging` only). NEXT9 remains human-only/out of scope. **No `*phase115*` files exist yet.**
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261108T205442Z-PHASE115-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase111/112/113/114 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE114→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111/112/113/114`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase115_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase114AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE115_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE114` and `PHASE32`. (Seed default `115115`; IDs `p115-*`; artifact names `PHASE115_*`.)
> 2. `scripts/generate_phase115_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `115115`, cycles `40`), timestamped `research_state/PHASE115_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111/112/113/114.
> 3. `tests/test_phase115_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE114','PHASE32']`).
> 4. `tests/test_generate_phase115_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase115/Phase114/`composes=PHASE114,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE114,PHASE32`.
> - Controlled `generate(cycles=40, seed=115115, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE114,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 115115`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase115 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE116-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE115→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111/112/113/114` refactors, or proceeding past Phase114 before Phase115 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase115 is the mandatory next heavy task.**

## Verified state (refresh 2026-11-08T20:54:42Z; Phase114 evidence 2026-11-08T20:54:41Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
- **Env:** deps installed; `pytest 9.2.0` available; **3635 tests collected** (`pytest -q --co`, 9.57s).
- **P0 (re-verified 2026-11-08T20:54:42Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py:69` defaults false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase111 (prior, verified):** artifact `research_state/PHASE111_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T194435Z.json`; composes PHASE110→32; coverage_rows=12; valid=true deterministic=True bounds_ok=True gates_ok=true.
- **Chain B Phase112 (delivered, verified 2026-11-08T20:23Z):** composes PHASE111→32; 12 rows; valid/deterministic/bounded/gates_ok; artifact `PHASE112_..._20261108T202257Z.json`; module pytest 1 passed (13.49s); CLI `--no-write` valid; generator cases verified via controlled generate+validate+direct assertions (composed-chain pytest timeout caveat recorded in prior handoff).
- **Chain B Phase113 (delivered, verified 2026-11-08T20:37Z):**
  - Files: `src/hedging/phase113_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `scripts/generate_phase113_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x); `tests/test_phase113_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `tests/test_generate_phase113_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - `py_compile` (4 files): **OK**.
  - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): **`paper_only=True gates_ok=True composes=['PHASE112','PHASE32']`** (pytest module test **1 passed in 13.29s**).
  - Controlled `generate(cycles=40, seed=113113, write=True)` + `validate_artifact`: **`valid=true issues=[] deterministic_replay_equal=true bounds_ok=true coverage_rows=12 composes=['PHASE112','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`**. Artifact: `research_state/PHASE113_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T203422Z.json`.
  - CLI `--no-write` (`--cycles 4 --seed 113113`, `PHASE_QUICK_VERIFY=1`): **`valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`**.
  - Generator cases: **9 passed** (all required ≥7 cases covered). **Caveat:** composed-chain generator tests are slow (39–188s individual); full batch may hit environment timeouts — use targeted runs/controlled fallbacks with explicit caveats.
- **Chain B Phase114 (delivered, verified 2026-11-08T20:54:41Z):**
  - Files: `src/hedging/phase114_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `scripts/generate_phase114_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x); `tests/test_phase114_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `tests/test_generate_phase114_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - `py_compile` (4 files): **OK**.
  - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): **`paper_only=True gates_ok=True composes=['PHASE113','PHASE32']`** (pytest module test **1 passed in 13.11s**).
  - Controlled `generate(cycles=40, seed=114114, write=True)` + `validate_artifact`: **`valid=true issues=[] deterministic_replay_equal=true bounds_ok=true coverage_rows=12 composes=['PHASE113','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`**. Artifact: `research_state/PHASE114_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T205441Z.json`.
  - CLI `--no-write` (`--cycles 4 --seed 114114`, `PHASE_QUICK_VERIFY=1`): **`valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`**.
  - Generator cases: **9 passed** (all required ≥7 cases covered). **Caveat:** composed-chain generator tests are slow (full batch 397s; individual 39–188s) — use targeted runs/extended timeouts with explicit caveats.
- **Phase115 status (checked 2026-11-08T20:54:42Z):** **no `*phase115*` files exist** in `src/hedging`, `scripts`, or `tests`. Phase115 is the **next mandatory bottleneck**.

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase112 implemented + verified (composes PHASE111→32, 12 rows, valid/deterministic/bounded) | **CLEARED** | Done (2026-11-08T20:23Z). |
| Phase113 implemented + verified (composes PHASE112→32, 12 rows, valid/deterministic/bounded) | **CLEARED** | Done (2026-11-08T20:37Z). |
| Phase114 implemented + verified (composes PHASE113→32, 12 rows, valid/deterministic/bounded) | **CLEARED** | Done (2026-11-08T20:54:41Z). |
| Phase115 not implemented (no `*phase115*` files) | **ACTIVE BOTTLENECK — MANDATORY** | Execute `INIT-20261108T205442Z-PHASE115` composing PHASE114→32 (heavy deliverables+verification). |
| P0 safety drift | **CLEAR (re-verified 2026-11-08T20:54:42Z)** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase115 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED** | `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261108T205442Z-PHASE115-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111/112/113/114, compose **PHASE114→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE116-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE115→32**, only after Phase115 is verified with evidence.
3. Continue PHASE114→115→116→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111/112/113/114`.**

## Phase115 execution checklist (active — mandatory for next agent)

- [ ] Implement Chain B Phase115 composing PHASE114→32 (4 files, +x on script).
- [ ] `py_compile` OK (4 files).
- [ ] Smoke (`PHASE_QUICK_VERIFY=1`): `paper_only=True gates_ok=True composes ['PHASE114','PHASE32']`; module pytest pass.
- [ ] Controlled `generate(cycles=40,seed=115115,write=True)` + `validate_artifact` pass; record `PHASE115_*_PAPER_EVIDENCE_<UTC>.json`.
- [ ] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`).
- [ ] Generator cases **≥7 passed** (valid shape + 5 rejections + deterministic + 12 coverage/bounds/composes + CLI `--no-write`); record counts/caveats.
- [ ] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [ ] Handoff updated last with `INIT-<UTC>-PHASE116-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
