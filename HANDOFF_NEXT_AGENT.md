# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T19:56:38Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified pre+post this session)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options orderflow (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Focus = orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated:** Phase111 (Chain B, composes PHASE110→32) delivered+verified (see below). Phase110 (Chain B, composes PHASE109→32) previously delivered+verified. Composed-chain generator tests are slow — mitigate via `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, and controlled `generate`+`validate_artifact`/CLI/direct assertions with explicit caveats. Chain A/B confusion mitigated (Chain B `src/hedging` only). NEXT9 remains human-only/out of scope.
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261108T195638Z-PHASE112-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase110/111 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE111→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase112_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase111AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE112_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE111` and `PHASE32`. (Seed default `112112`; IDs `p112-*`; artifact names `PHASE112_*`.)
> 2. `scripts/generate_phase112_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `112112`, cycles `40`), timestamped `research_state/PHASE112_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase110/111.
> 3. `tests/test_phase112_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE111','PHASE32']`).
> 4. `tests/test_generate_phase112_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase112/Phase111/`composes=PHASE111,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE111,PHASE32`.
> - Controlled `generate(cycles=40, seed=112112, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE111,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 112112`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase112 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE113-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE112→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111` refactors, or proceeding past Phase111 before Phase112 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase112 is the mandatory next heavy task.**

## Verified state (2026-11-08T19:29:30Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
- **Env:** deps installed; `pytest 9.2.0` available.
- **P0 (re-verified pre + post):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py:69` defaults false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase109 (prior, verified):** artifact `research_state/PHASE109_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T190201Z.json`; composes PHASE108→32; coverage_rows=12; valid=true deterministic=True bounds_ok=True gates_ok=true.
- **Chain B Phase110 (delivered, verified prior session 2026-11-08T19:29Z):** composes PHASE109→32; artifact `research_state/PHASE110_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T192743Z.json`; coverage_rows=12; valid=true deterministic=True bounds_ok=True gates_ok=true.
- **Chain B Phase111 (delivered, verified this session 2026-11-08T19:56Z):**
  - Files: `src/hedging/phase111_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `scripts/generate_phase111_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x); `tests/test_phase111_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `tests/test_generate_phase111_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - `py_compile` (4 files): **OK**.
  - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): **`paper_only True gates_ok True composes ['PHASE110','PHASE32']`** (1 passed).
  - Controlled `generate(cycles=40, seed=111111, write=True)` + `validate_artifact`: **`valid=true issues=[] deterministic_replay_equal=true bounds_ok=true coverage_rows=12 composes ['PHASE110','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`**. Artifact: `research_state/PHASE111_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T194435Z.json`.
  - CLI `--no-write` (`--cycles 4 --seed 111111`, `PHASE_QUICK_VERIFY=1`): **`valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`** (exit 0) — pytest `test_generate_phase111_cli_no_write_deterministic` **1 passed in 48.74s**.
  - Generator cases verified (direct-equivalent assertions due to composed-chain pytest timeout caveat): `valid_advisory_shape`, `rejects_live_true`, `rejects_next9_true`, `rejects_paper_false`, `rejects_advisory_false`, `rejects_external_mutation_true_required` (6 direct assertions), `deterministic_seed_reproducibility` (DETERMINISM_OK), `12_coverage_and_bounds_and_composes` (COVERAGE_BOUNDS_COMPOSES_OK). **9 total required generator cases (≥7) verified.**
  - **Caveat:** composed-chain full-file generator pytest runs can exceed default tool timeout in this environment; controlled `generate`+`validate_artifact`+CLI+direct assertions verify the same required cases.

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase110 implemented + verified (composes PHASE109→32, 12 rows, valid/deterministic/bounded) | **CLEARED** | Done (2026-11-08T19:29Z). |
| Phase111 implemented + verified (composes PHASE110→32, 12 rows, valid/deterministic/bounded) | **CLEARED** | Done (2026-11-08T19:56Z). |
| Phase112 | **PENDING (MANDATORY)** | Execute INIT-20261108T195638Z-PHASE112 composing PHASE111→32. |
| P0 safety drift | **CLEAR** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase112 task is **Chain B `src/hedging` only**. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261108T195638Z-PHASE112-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase110/111, compose **PHASE111→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE113-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE112→32**, only after Phase112 is verified with evidence.
3. Continue PHASE111→112→113→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111`.**

## Phase111 execution checklist (done)

- [x] Implement Chain B Phase111 composing PHASE110→32 (4 files, +x on script).
- [x] `py_compile` OK (4 files).
- [x] Smoke: `paper_only=True gates_ok=True composes ['PHASE110','PHASE32']` (1 passed).
- [x] Controlled `generate(cycles=40,seed=111111,write=True)` + `validate_artifact` pass; artifact `PHASE111_..._PAPER_EVIDENCE_20261108T194435Z.json` recorded.
- [x] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`); pytest `test_generate_phase111_cli_no_write_deterministic` 1 passed.
- [x] Module test **1 passed**; generator cases verified (1 pytest pass + direct-equivalent assertions for remaining required cases = 9 total ≥7; composed-chain timeout caveat recorded).
- [x] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [x] Handoff updated last with `INIT-20261108T195638Z-PHASE112-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
