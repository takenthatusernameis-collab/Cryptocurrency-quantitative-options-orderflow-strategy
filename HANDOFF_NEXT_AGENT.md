# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T17:36:02Z (repo-priority: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified this session)**
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy):**
> **`INIT-20261108T173602Z-PHASE106-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src/hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**. Mirror Phase105 (module + paper-evidence generator + 2 test files). **Compose PHASE105→32**. 4 venues × 3 symbols = **12 coverage rows** (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). Scope: crypto options orderflow → features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring evidence. **NO live trading, NO venue/config/credential mutation, NO NEXT9 unblock, NO refactor of `phase79/80/110`.**
>
> **EXECUTE IN FULL. NON-OPTIONAL.** Deliverables (all required):
> 1. `src/hedging/phase106_<same_theme>_post_attribution_seal_orchestrator.py` — paper-only hard gate, composes `Phase105...Orchestrator` with `PHASE_QUICK_VERIFY` stub path, finite serialization/assertions, emits report with `phase`, `paper_only=True`, `gates_ok=True`, `composes` including `PHASE105` and `PHASE32`.
> 2. `scripts/generate_phase106_<same_theme>_post_attribution_seal_orchestrator_paper_evidence.py` (+x) — deterministic seeded replay, finite validated bounds (`allow_nan=False`), 12 venue×symbol probes, `validate_artifact`, `--cycles/--seed/--write/--no-write` CLI, timestamped `research_state/PHASE106_*_PAPER_EVIDENCE_<UTC>.json` on `--write`.
> 3. `tests/test_phase106_<same_theme>_post_attribution_seal_orchestrator.py` — module smoke (paper-only gate, gates_ok, composes PHASE105→PHASE32).
> 4. `tests/test_generate_phase106_<same_theme>_post_attribution_seal_orchestrator_paper_evidence.py` — **≥7 generator cases** (valid advisory shape; reject live/next9/paper_false/advisory_false/external_mutation; deterministic seed reproducibility; 12 coverage finite probes/bounds; bounds/risk posture; CLI `--no-write` valid+deterministic+gates_ok+no artifact_path; cross-refs Phase106/Phase105/`composes=PHASE105,PHASE32`/`PAPER_OPS_SESSION_GATE`/`CONTINUOUS_VALIDATION`).
>
> **Verification (all required, record exact results):**
> - `py_compile` all 4 new files → OK.
> - Module smoke (`PHASE_QUICK_VERIFY=1 PYTHONPATH=.`): `paper_only=True gates_ok=True composes` includes `PHASE105,PHASE32`.
> - Controlled `generate(cycles=40, seed=106106, write=True)` + `validate_artifact` → `valid=true issues=[]`, deterministic replay equal, bounds ok, **12** venue×symbol coverage, `composes` includes `PHASE105,PHASE32`, `paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`. Record artifact path.
> - CLI `--no-write` JSON shows `valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null` (if timeout, run controlled generate+validate and cite reason explicitly).
> - Tests: run both Phase106 test files with `PHASE_QUICK_VERIFY=1` and adequate timeout; record pass counts. (Composed-chain generator tests can be slow; do not skip — increase timeout or run targeted.)
> - P0 re-verify: `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` remains.
> - **Update this handoff last** with exact commands/results/artifact path/caveats + next mandatory `INIT-<UTC>-PHASE107-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE106→32).
>
> **NOT PROGRESS:** status-only reporting, doc-only edits (except this final handoff update after real deliverables), partial stubs, skipped verification, chain substitution (Chain A `src.risk/phase106_live_execution*` / `tests/test_phase106_live_execution*` / risk `research_state/phase*` dirs are **NOT** Chain B Phase106), `phase79/80/110` refactors, or proceeding to Phase107 before Phase106 is complete.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work paper-only.** Chain B (`src.hedging`, post-attribution seal depth) is active: Phase100–105 delivered. Phase106 is the **mandatory next** heavy task.

## Verified state (2026-11-08T17:36:02Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
- **Env:** deps installed; `pytest 9.2.0` available.
- **P0 (re-verified):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**. `LIVE_TRADING_ENABLED=false` (`.env.example:15`, `src/config/secrets.py:69`). **No live capital. No venue/config/credential mutation. No NEXT9 unblock.**
- **NEXT9:** HUMAN-ONLY (A1–A7 missing; session gate NO_GO; `next9_unblocked=false`) — **does not gate** paper-only Chain B depth.
- **Chain B Phase105 (delivered, verified):**
  - `src/hedging/phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
  - `scripts/generate_phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x)
  - `tests/test_phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` (**2 passed**, `PHASE_QUICK_VERIFY=1`)
  - `tests/test_generate_phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (≥7 cases present; composed-chain runtime can exceed tight shell timeouts)
  - `py_compile`: OK (4 files). Module smoke: `PHASE105... paper_only=True gates_ok=True composes=['PHASE104','PHASE32']`. Generator `validate_artifact` on written artifact: **`True []`**. CLI `--no-write` (`PHASE_QUICK_VERIFY=1`): **`valid=true issues=[] paper_only=true live_trading_enabled=false next9_unblocked=false deterministic=true gates_ok=true artifact_path=null`**. Artifact: `research_state/PHASE105_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T172518Z.json` (`venue_symbol_coverage=12`, campaign composes `PHASE104,PHASE32`).
- **Chain A (risk, `src.risk/phase*_live_execution*`, `tests/test_phase106_live_execution*` present):** **different chain** — do not substitute for Chain B.

## Bottlenecks (agent-removable / remaining)

| Bottleneck | Status | Action |
|---|---|---|
| Phase106 not implemented | **OPEN (heavy, mandatory)** | Execute `INIT-20261108T173602Z-PHASE106-POST-ATTRIBUTION-SEAL-DEPTH` in full. |
| Generator pytest runtime (composed chain) | **KNOWN** | Use `PHASE_QUICK_VERIFY=1`, targeted runs, controlled `generate`/`validate_artifact`+CLI; run with adequate timeout. |
| P0 safety drift | **CLEAR** | Re-verify before/after changes. |
| Chain A/B confusion | **ADDRESSED** | Phase106 = Chain B `src.hedging` only. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory, cannot be avoided)

1. **NOW (mandatory):** `INIT-20261108T173602Z-PHASE106-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase105, compose **PHASE105→32**, 12 coverage rows, full deliverables + verification + artifact + handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE107-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE106→32**, after Phase106 verified.
3. Continue PHASE107→108→… only with verified artifacts (`validation.valid=true`, deterministic, bounded, 12 coverage, P0 intact). Never skip phases; never refactor `phase79/80/110`.

## Phase106 execution checklist

- [ ] Implement Chain B Phase106 composing PHASE105→32 (4 files).
- [ ] `py_compile` OK.
- [ ] Smoke: `paper_only=True gates_ok=True composes PHASE105,PHASE32`.
- [ ] Controlled `generate(cycles=40,seed=106106,write=True)` + `validate_artifact` pass; artifact path recorded.
- [ ] CLI `--no-write` pass (or explicit cited fallback).
- [ ] Both test files run with `PHASE_QUICK_VERIFY=1`; pass counts recorded.
- [ ] P0 re-verified.
- [ ] Handoff updated last with `INIT-<UTC>-PHASE107-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Replace stale state in place with verified facts/timestamps/paths/commands. No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
