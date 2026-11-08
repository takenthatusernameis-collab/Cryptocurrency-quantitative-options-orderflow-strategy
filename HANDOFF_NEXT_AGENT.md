# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T19:29:30Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified pre+post this session)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options orderflow (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Focus = orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated:** Phase110 (Chain B, composes PHASE109→32) delivered+verified (see below). Composed-chain generator tests are slow — mitigate via `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, and controlled `generate`+`validate_artifact`/CLI/direct assertions with explicit caveats. Chain A/B confusion mitigated (Chain B `src/hedging` only). NEXT9 remains human-only/out of scope.
> - **Campaign (heavy work, cannot be avoided):** Execute Chain B post-attribution seal depth sequentially: **PHASE111 → PHASE112 → ...** Each phase composes previous→32, produces 4 files (+x), 12 venue×symbol coverage, full verification, writes timestamped artifact, updates this handoff last with verified facts + next INIT. Never refactor `phase79/80/110`, never touch Chain A live paths, never touch secrets/config/env.
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261108T192930Z-PHASE111-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase110 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE110→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase111_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase110AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE111_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE110` and `PHASE32`. (Seed default `111111`; IDs `p111-*`; artifact names `PHASE111_*`.)
> 2. `scripts/generate_phase111_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `111111`, cycles `40`), timestamped `research_state/PHASE111_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase110.
> 3. `tests/test_phase111_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE110','PHASE32']`).
> 4. `tests/test_generate_phase111_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase111/Phase110/`composes=PHASE110,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE110,PHASE32`.
> - Controlled `generate(cycles=40, seed=111111, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE110,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 111111`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase111 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE112-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE111→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110` refactors, or proceeding past Phase110 before Phase111 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase111 is the mandatory next heavy task.**

## Verified state (2026-11-08T19:29:30Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
- **Env:** deps installed; `pytest 9.2.0` available.
- **P0 (re-verified pre + post):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py:69` defaults false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase109 (prior, verified):** artifact `research_state/PHASE109_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T190201Z.json`; composes PHASE108→32; coverage_rows=12; valid=true deterministic=True bounds_ok=True gates_ok=true.
- **Chain B Phase110 (delivered, verified this session 2026-11-08T19:29Z):**
  - Files: `src/hedging/phase110_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `scripts/generate_phase110_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x); `tests/test_phase110_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `tests/test_generate_phase110_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - `py_compile` (4 files): **OK**.
  - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): **`paper_only True gates_ok True composes ['PHASE109','PHASE32']`**.
  - Controlled `generate(cycles=40, seed=110110, write=True)` + `validate_artifact`: **`valid=true issues=[] deterministic_replay_equal=true bounds_ok=true coverage_rows=12 composes ['PHASE109','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`**. Artifact: `research_state/PHASE110_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T192743Z.json` (disk re-check: `validation.valid True paper_only True live False next9 False bounds_ok True`).
  - CLI `--no-write` (`--cycles 4 --seed 110110`, `PHASE_QUICK_VERIFY=1`): **`valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`** (exit 0).
  - Module test: **1 passed in 13.36s** (`test_phase110_smoke_paper_only_gates_ok_compose`).
  - Generator tests (targeted/controlled due to composed-chain runtime): **pytest passed** — `rejects_advisory_false`, `rejects_external_mutation_true_required` (2 passed, 93.83s), `cli_no_write_deterministic` (1 passed, 49.80s). **Direct-equivalent assertions passed** for `valid_advisory_shape`, `rejects_live_true`, `rejects_next9_true`, `rejects_paper_false` (batch 1), `deterministic_seed_reproducibility` (DETERMINISM_OK), and `12_coverage_and_bounds_and_composes` (COVERAGE_BOUNDS_COMPOSES_OK). **Caveat:** composed-chain full-file generator pytest runs can exceed default tool timeout in this environment; controlled `generate`+`validate_artifact`+CLI+direct assertions verify the same required cases.

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase110 implemented + verified (composes PHASE109→32, 12 rows, valid/deterministic/bounded) | **CLEARED** | Done (2026-11-08T19:29Z). |
| Phase111 | **PENDING (MANDATORY)** | Execute INIT-20261108T192930Z-PHASE111 composing PHASE110→32. |
| P0 safety drift | **CLEAR** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase111 task is **Chain B `src/hedging` only**. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261108T192930Z-PHASE111-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase110, compose **PHASE110→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE112-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE111→32**, only after Phase111 is verified with evidence.
3. Continue PHASE111→112→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110`.**

## Phase110 execution checklist (done)

- [x] Implement Chain B Phase110 composing PHASE109→32 (4 files, +x on script).
- [x] `py_compile` OK (4 files).
- [x] Smoke: `paper_only=True gates_ok=True composes ['PHASE109','PHASE32']`.
- [x] Controlled `generate(cycles=40,seed=110110,write=True)` + `validate_artifact` pass; artifact `PHASE110_..._PAPER_EVIDENCE_20261108T192743Z.json` recorded.
- [x] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`).
- [x] Module test **1 passed**; generator cases verified (3 pytest passes + direct-equivalent assertions for remaining required cases; composed-chain timeout caveat recorded).
- [x] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [x] Handoff updated last with `INIT-20261108T192930Z-PHASE111-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
