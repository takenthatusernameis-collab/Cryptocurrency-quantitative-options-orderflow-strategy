# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T17:16:05Z (repo-priority: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified this session)**
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy):**
> **`INIT-20261108T171605Z-PHASE105-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src.hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**, mirror Phase104, **compose PHASE104→32**, 4 venues × 3 symbols = 12 coverage (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), orderflow→execution/risk→delta-neutral hedging→PnL attribution→reconciliation/monitoring evidence.
>
> **EXECUTE IN FULL. NON-OPTIONAL.** Deliver: `src/hedging/phase105_*`, `scripts/generate_phase105_*_paper_evidence.py` (+x), 2 test files (≥7 generator cases + module smoke), `py_compile` OK, module smoke `paper_only=True gates_ok=True composes PHASE104→PHASE32`, controlled `generate(cycles=40,seed=105105,write=True)` + `validate_artifact` → `validation.valid=true issues=[] deterministic bounds_ok coverage_rows=12 composes=[PHASE104,PHASE32] paper_only=true live_trading_enabled=false next9_unblocked=false`, CLI `--no-write` (or controlled fallback with explicit cited reason), valid timestamped `research_state/PHASE105_..._PAPER_EVIDENCE_<UTC>.json`, P0 re-verify, and **update this handoff last** with exact commands/results/artifact path/caveats + next mandatory `INIT-<UTC>-PHASE106-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE105→32).
>
> **NOT PROGRESS:** status-only reporting, doc-only edits (other than this final handoff update after real deliverables), partial stubs, skipped verification, chain substitution (Chain A `src.risk/phase105_live_execution*` / `tests/test_phase105_live_execution*` / risk `research_state/phase*` dirs are **NOT** Chain B Phase105), `phase79/80/110` refactors, or proceeding to Phase106 before Phase105 is complete.
>
> **SAFETY/P0 (re-verified 2026-11-08T17:16:05Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` (`.env.example:15`, `src/config/secrets.py:69`). **No live capital. No venue/config/credential mutation. No NEXT9 unblock.** NEXT9 is HUMAN-ONLY (A1–A7 missing; `next9_unblocked=false`; session gate NO_GO) and **does not gate** paper-only Chain B depth.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work remains paper-only.** Chain B (`src.hedging`, post-attribution seal depth) is the active depth chain; Phase100–104 delivered. Phase105 is next.

## State (verified 2026-11-08T17:16:05Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
- **Environment:** `pip install -r requirements.txt` applied (pydantic, pytest, pandas, numpy, scipy, etc. installed). `python -c "from src.hedging.phase104_adaptive_toxicity_resilient_post_attribution_seal_orchestrator import Phase104AdaptiveToxicityResilientPostAttributionSealOrchestrator"` → OK. `pytest` import OK.
- **Chain B (hedging, `src/hedging/phaseN_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`):** Phase100–104 delivered/committed (`f53b846eb` adds Phase104 module/script/tests/artifact). Phase104 artifact present: `research_state/PHASE104_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T163047Z.json` (`validation.valid=true`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`; top-level `phase/composes/coverage_rows/gates_ok` fields are null/absent in JSON — verify/normalize in Phase105 pattern if needed).
- **Chain B Phase105:** **NOT implemented** — no `src/hedging/phase105*`, no `scripts/generate_phase105*`, no Chain B PHASE105 tests, no `research_state/PHASE105_*` Chain B artifact (confirmed 2026-11-08T17:16:05Z).
- **Chain A (risk, `src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*` / `research_state/phase*_live_execution*` dirs):** different chain — **do not substitute** for Chain B.

## Bottlenecks (agent-removable addressed / remaining)

| Bottleneck | Status | Action |
|---|---|---|
| Stale/duplicated handoff (multiple READ FIRST blocks) | **REMOVED 2026-11-08T17:16:05Z** | This file is the single consolidated handoff. |
| P0 safety drift | **CLEAR** | `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` empty; `LIVE_TRADING_ENABLED=false`. Re-verify before/after changes. |
| Chain A/B confusion | **ADDRESSED** | Follow Chain B `src.hedging` pattern only for Phase105. |
| Phase105 not implemented | **OPEN (heavy, mandatory)** | Execute `INIT-20261108T171605Z-PHASE105-POST-ATTRIBUTION-SEAL-DEPTH` in full. |
| Python deps / tests unavailable (pydantic, pytest missing) | **RESOLVED 2026-11-08T17:16:05Z** | `pip install -r requirements.txt` applied; imports OK; pytest import OK. No longer blocking. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory, cannot be avoided)

1. **NOW (mandatory):** `INIT-20261108T171605Z-PHASE105-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase104, compose **PHASE104→32**, 12 coverage rows, full deliverables+verification+artifact+handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE106-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE105→32**, same Chain B pattern, after Phase105 verified.
3. Continue depth chain (PHASE106→107→108→…) only with verified artifacts; never skip a phase; never refactor `phase79/80/110`; every phase must produce its own timestamped paper evidence artifact with `validation.valid=true`.

## Execution checklist (Phase105)

- [ ] Read Phase104 module/script/tests as template; implement additive Chain B Phase105 composing PHASE104→32.
- [ ] `py_compile` all new/changed files.
- [ ] Module smoke: `paper_only=True`, `gates_ok=True`, composes includes PHASE104→PHASE32.
- [ ] Controlled: `generate(cycles=40, seed=105105, write=True)` + `validate_artifact` → `valid=true issues=[] bounds_ok coverage_rows=12 composes=[PHASE104,PHASE32] paper_only=true live_trading_enabled=false next9_unblocked=false`.
- [ ] CLI `--no-write` (or explicit cited fallback).
- [ ] Timestamped `research_state/PHASE105_..._PAPER_EVIDENCE_<UTC>.json`.
- [ ] P0 re-verify (no protected diffs, `LIVE_TRADING_ENABLED=false`).
- [ ] **Update this handoff last** with exact commands/results/artifact path/caveats + `INIT-<UTC>-PHASE106-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Do not append duplicate READ FIRST blocks; replace stale state in place with verified facts and exact timestamps/paths/commands. Final responses must not ask follow-up questions.
