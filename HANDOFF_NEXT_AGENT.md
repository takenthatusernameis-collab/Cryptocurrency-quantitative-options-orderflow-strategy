# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T18:33:57Z (repo: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified this session)**
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy — no shortcuts):**
> **`INIT-20261108T183357Z-PHASE107-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase106 exactly in structure/guardrails (module + paper-evidence generator + 2 test files). **Compose PHASE106→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110`. NO Chain A substitution** (`src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*`).
>
> **EXECUTE IN FULL (NON-OPTIONAL).** Deliverables (all required):
> 1. `src/hedging/phase107_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase106AdaptiveToxicityResilientPostAttributionSealOrchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase="PHASE107_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR"`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE106` and `PHASE32`. (Seed default `107107`; IDs `p107-*`; artifact names `PHASE107_*`.)
> 2. `scripts/generate_phase107_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI (default seed `107107`, cycles `40`), timestamped `research_state/PHASE107_*_PAPER_EVIDENCE_<UTC>.json` on `--write`. Include hang stubs/cache pattern per Phase106.
> 3. `tests/test_phase107_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes `['PHASE106','PHASE32']`).
> 4. `tests/test_generate_phase107_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no `artifact_path`; cross-refs Phase107/Phase106/`composes=PHASE106,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results/paths/caveats):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE106,PHASE32`.
> - Controlled `generate(cycles=40, seed=107107, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE106,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. **Record artifact path.**
> - CLI `--no-write` JSON (`PHASE_QUICK_VERIFY=1`, e.g. `--cycles 4 --seed 107107`): `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`. If timeout, run controlled generate+validate and **cite reason explicitly**.
> - Tests: run both Phase107 test files with `PHASE_QUICK_VERIFY=1 PYTHONPATH=.` and adequate timeout; **record pass counts**. Composed-chain generator tests are slow — run targeted, increase timeout, or use controlled fallbacks **with explicit caveats**; do not skip verification.
> - P0 re-verify (before/after): `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with verified facts + next mandatory `INIT-<UTC>-PHASE108-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE107→32).
>
> **NOT PROGRESS (explicitly forbidden):** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, Chain A substitution, `phase79/80/110` refactors, or proceeding to Phase108 before Phase107 is complete/verified.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src/hedging`, post-attribution seal depth) is active. **Phase107 is the mandatory next heavy task.**

## Verified state (2026-11-08T18:33:57Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
- **Env:** deps installed; `pytest 9.2.0` available.
- **P0 (re-verified 2026-11-08T18:33:57Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `.env.example:15 LIVE_TRADING_ENABLED=false`; `src/config/secrets.py:69` defaults false. **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase106 (delivered, verified 2026-11-08T18:22:30Z):** `src/hedging/phase106_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; `scripts/generate_phase106_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x); 2 Phase106 test files. Smoke: **`paper_only True gates_ok True composes ['PHASE105','PHASE32']`**. Controlled `generate(cycles=40, seed=106106, write=True)`+`validate_artifact`: **`valid=true issues=[] deterministic=true bounds_ok=true coverage_rows=12 composes=["PHASE105","PHASE32"] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`**. Artifact: `research_state/PHASE106_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T182009Z.json`. CLI `--no-write`: **valid/deterministic/gates_ok/artifact_path=null**. Tests: module **2 passed**; generator **6 passed targeted**; `test_rejects_live_next9_paper_false_advisory_false_external` timed out under 120s pytest but controlled equivalent passed (caveat recorded).
- **Chain A (risk, `src.risk/phase*_live_execution*`, `tests/test_phase106_live_execution*`):** **different chain — do not substitute for Chain B.**

## Bottlenecks (agent-removable now / remaining)

| Bottleneck | Status | Action (unblock) |
|---|---|---|
| Phase107 not implemented | **OPEN — mandatory heavy** | Execute `INIT-20261108T183357Z-PHASE107-POST-ATTRIBUTION-SEAL-DEPTH` end-to-end. |
| Composed-chain generator pytest runtime | **KNOWN, mitigated** | Use `PHASE_QUICK_VERIFY=1`, targeted runs, adequate timeout; fall back to controlled `generate`+`validate_artifact`+CLI for any timed-out case and **record explicit caveat**. |
| P0 safety drift | **CLEAR** | Re-verify before/after every change batch. |
| Chain A/B naming confusion (both have Phase106) | **MITIGATED** | Phase107 task is **Chain B `src/hedging` only**. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory — no avoidance)

1. **NOW (mandatory):** `INIT-20261108T183357Z-PHASE107-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase106, compose **PHASE106→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE108-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE107→32**, only after Phase107 is verified with evidence.
3. Continue PHASE108→109→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). **Never skip phases; never refactor `phase79/80/110`.**

## Phase107 execution checklist

- [ ] Implement Chain B Phase107 composing PHASE106→32 (4 files, +x on script).
- [ ] `py_compile` OK (4 files).
- [ ] Smoke: `paper_only=True gates_ok=True composes ['PHASE106','PHASE32']`.
- [ ] Controlled `generate(cycles=40,seed=107107,write=True)` + `validate_artifact` pass; artifact path recorded.
- [ ] CLI `--no-write` pass (or explicit cited fallback).
- [ ] Both test files run with `PHASE_QUICK_VERIFY=1`; pass counts recorded (caveats if any timeout).
- [ ] P0 re-verified empty diff / `LIVE_TRADING_ENABLED=false`.
- [ ] Handoff updated last with `INIT-<UTC>-PHASE108-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.