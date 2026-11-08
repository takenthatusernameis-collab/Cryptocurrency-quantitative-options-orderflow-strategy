# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T22:57:38Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified pre/post this session; Phase119 delivered+verified this session)**
>
> **IMMEDIATE NEXT AGENT INSTRUCTION (INFERRED FROM REPO PRIORITY — MANDATORY, NO ESCAPE):**
> - **Repo priority:** Crypto options orderflow (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Focus = orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **Paper-only only.**
> - **Bottlenecks removed/mitigated (verified 2026-11-08T22:57:38Z):** **Phase119 (Chain B, composes PHASE118→32) delivered+verified this session** — artifact `research_state/PHASE119_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T224844Z.json` (`valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true coverage=12 composes=['PHASE118','PHASE32']`, seed 119119, cycles 40). Phase112–118 previously cleared. Composed-chain generator tests remain slow — mitigated via `PHASE_QUICK_VERIFY=1`, targeted runs, extended timeouts, and controlled `generate`+`validate_artifact`/CLI/direct assertions with explicit caveats (see verification notes). Chain A/B confusion mitigated (Chain B `src/hedging` only). NEXT9 remains human-only/out of scope. **No `*phase120*` files exist** (checked 2026-11-08T22:57Z).
> - **P0 (re-verified pre/post 2026-11-08T22:57:38Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py` default false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261108T225738Z-PHASE120-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase111–119 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE119→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110/111/112/113/114/115/116/117/118/119`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase120_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase119AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE120_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE119` and `PHASE32`. (Seed default `120120`; IDs `p120-*`; artifact names `PHASE120_*`.)
> 2. `scripts/generate_phase120_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `120120`, cycles `40`), timestamped `research_state/PHASE120_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase111–119.
> 3. `tests/test_phase120_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE119','PHASE32']`).
> 4. `tests/test_generate_phase120_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase120/Phase119/`composes=PHASE119,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE119,PHASE32`.
> - Controlled `generate(cycles=40, seed=120120, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE119,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 120120`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase120 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE121-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE120→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110/111/112/113/114/115/116/117/118/119` refactors, or proceeding past Phase119 before Phase120 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase120 is the mandatory next heavy task.**

## Verified state (refresh 2026-11-08T22:57:38Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
- **P0 (re-verified pre/post 2026-11-08T22:57:38Z):** sensitive diff → **empty**. `LIVE_TRADING_ENABLED=false` in `.env.example` and default in `src/config/secrets.py`. **No live capital/venue mutation/NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase111–118:** prior verified (composing PHASE110→…→PHASE117→32), 12 rows each, valid/deterministic/bounded/gates_ok per handoff history. Phase118 artifact: `PHASE118_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T222524Z.json`.
- **Chain B Phase119 (delivered, verified 2026-11-08T22:57:38Z, this session):** composes **PHASE118→32**.
  - Deliverables (4): `src/hedging/phase119_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `scripts/generate_phase119_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x); `tests/test_phase119_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `tests/test_generate_phase119_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
  - `py_compile` all 4: **OK**.
  - Module smoke (`PHASE_QUICK_VERIFY=1`): `{'paper_only': True, 'gates_ok': True, 'composes': ['PHASE118', 'PHASE32'], 'phase': 'PHASE119_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR'}`.
  - Controlled generate+write (`PHASE_QUICK_VERIFY=1 --cycles 40 --seed 119119 --write`): artifact `research_state/PHASE119_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T224844Z.json` → `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true deterministic=true coverage=12 composes=['PHASE118','PHASE32']`.
  - CLI `--no-write` (`PHASE_QUICK_VERIFY=1 --cycles 4 --seed 119119`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`.
  - Tests: module pytest **1 passed** (10.16s). Generator CLI test **1 passed, 8 deselected** (42.25s) via targeted run. **8 non-CLI generator cases verified via direct controlled assertions (timed runs):** valid shape+5 rejections **OK**; deterministic seed reproducibility **OK**; 12 coverage+bounds+composes **OK**. **Caveat:** full generator pytest suite (all 9 collected together) exceeded 120s wall timeout under composed-chain load even with `PHASE_QUICK_VERIFY=1` in this session; targeted split + direct assertions used (no verification skipped).
  - P0 post: sensitive diff **empty**; `LIVE_TRADING_ENABLED=false` confirmed.
- **Phase120 status (checked 2026-11-08T22:57Z):** **no `*phase120*` files exist** in `src/hedging`, `scripts`, or `tests`. **ACTIVE MANDATORY BOTTLENECK — unstarted.**

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase112–119 implemented + verified (composes N-1→32, 12 rows, valid/deterministic/bounded) | **CLEARED** | Done (through 2026-11-08T22:57:38Z). |
| Phase120 not implemented (no `*phase120*` files) | **ACTIVE — MANDATORY (confirmed 2026-11-08T22:57Z)** | Execute `INIT-20261108T225738Z-PHASE120` composing PHASE119→32 (heavy deliverables+verification). |
| P0 safety drift | **CLEAR (re-verified pre/post)** | Re-verify before/after every change batch. |
| Chain A/B naming confusion | **MITIGATED** | Phase120 is **Chain B `src/hedging` only**. |
| Composed-chain generator pytest slowness/timeouts | **MITIGATED (caveat recorded)** | `PHASE_QUICK_VERIFY=1`, targeted runs/splits, extended timeouts, controlled generate+validate/CLI/direct assertions with explicit caveats. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261108T225738Z-PHASE120-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase111–119, compose **PHASE119→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE121-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE120→32**, only after Phase120 is verified with evidence.
3. Continue PHASE119→120→121→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110/111/112/113/114/115/116/117/118/119`.**

## Phase120 execution checklist (active — mandatory for next agent)

- [ ] Implement Chain B Phase120 composing PHASE119→32 (4 files, +x on script).
- [ ] `py_compile` OK (4 files).
- [ ] Smoke (`PHASE_QUICK_VERIFY=1`): `paper_only=True gates_ok=True composes ['PHASE119','PHASE32']`; module pytest pass.
- [ ] Controlled `generate(cycles=40,seed=120120,write=True)` + `validate_artifact` pass; record `PHASE120_*_PAPER_EVIDENCE_<UTC>.json`.
- [ ] CLI `--no-write` pass (`valid=true issues=[] deterministic=true gates_ok=true artifact_path=null`).
- [ ] Generator cases **≥7 passed** (valid shape + 5 rejections + deterministic + 12 coverage/bounds/composes + CLI `--no-write`); record counts/caveats.
- [ ] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [ ] Handoff updated last with `INIT-<UTC>-PHASE121-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
