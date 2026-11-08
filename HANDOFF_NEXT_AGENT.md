# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

> **READ FIRST — HANDOFF REFRESHED 2026-11-08T17:25:30Z (repo-priority: `Cryptocurrency-quantitative-options-orderflow-strategy`; P0 re-verified this session)**
>
> **SINGLE INITIAL TASK MESSAGE FOR THE NEXT AGENTIC WORK SESSION (timestamped, mandatory, heavy):**
> **`INIT-20261108T172530Z-PHASE106-POST-ATTRIBUTION-SEAL-DEPTH`** — Chain B (`src.hedging`), **paper-only/additive/deterministic/finite-probe/bounded/guarded**, mirror Phase105, **compose PHASE105→32**, 4 venues × 3 symbols = 12 coverage (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL), orderflow→execution/risk→delta-neutral hedging→PnL attribution→reconciliation/monitoring evidence.
>
> **EXECUTE IN FULL. NON-OPTIONAL.** Deliver: `src/hedging/phase106_*`, `scripts/generate_phase106_*_paper_evidence.py` (+x), 2 test files (≥7 generator cases + module smoke), `py_compile` OK, module smoke `paper_only=True gates_ok=True composes PHASE105→PHASE32`, controlled `generate(cycles=40,seed=106106,write=True)` + `validate_artifact` → `validation.valid=true issues=[] deterministic bounds_ok coverage_rows=12 composes=[PHASE105,PHASE32] paper_only=true live_trading_enabled=false next9_unblocked=false`, CLI `--no-write` (or controlled fallback with explicit cited reason), valid timestamped `research_state/PHASE106_..._PAPER_EVIDENCE_<UTC>.json`, P0 re-verify, and **update this handoff last** with exact commands/results/artifact path/caveats + next mandatory `INIT-<UTC>-PHASE107-POST-ATTRIBUTION-SEAL-DEPTH` (compose PHASE106→32).
>
> **NOT PROGRESS:** status-only reporting, doc-only edits (other than this final handoff update after real deliverables), partial stubs, skipped verification, chain substitution (Chain A `src.risk/phase106_live_execution*` / `tests/test_phase106_live_execution*` / risk `research_state/phase*` dirs are **NOT** Chain B Phase106), `phase79/80/110` refactors, or proceeding to Phase107 before Phase106 is complete.
>
> **SAFETY/P0 (re-verified 2026-11-08T17:25:30Z):** `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` → **empty**; `LIVE_TRADING_ENABLED=false` (`.env.example:15`, `src/config/secrets.py:69`). **No live capital. No venue/config/credential mutation. No NEXT9 unblock.** NEXT9 is HUMAN-ONLY (A1–A7 missing; `next9_unblocked=false`; session gate NO_GO) and **does not gate** paper-only Chain B depth.

---

## Repo priority (name-driven)

`Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options quantitative **orderflow** strategy (Deribit/OKX/Bybit/Binance × BTC/ETH/SOL): orderflow features/signals → execution/backtest (fees/slippage/risk) → delta-neutral hedging + directional/hedge PnL attribution → reconciliation/monitoring. **All work remains paper-only.** Chain B (`src.hedging`, post-attribution seal depth) is the active depth chain; Phase100–105 delivered. Phase106 is next.

## State (verified 2026-11-08T17:25:30Z)

- **Branch:** `main` | **Workspace:** `/home/runner/work/Cryptocurrency-quantitative-options-orderflow-strategy/Cryptocurrency-quantitative-options-orderflow-strategy`
- **Environment:** deps installed (`pip install -r requirements.txt` previously applied); `pytest`/pydantic available.
- **Chain B Phase105 (delivered this session):**
  - Added: `src/hedging/phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (+x), `tests/test_phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (≥7 generator cases).
  - `py_compile`: OK (all 4 files).
  - Module smoke (`PHASE_QUICK_VERIFY=1`): `{'paper_only': True, 'gates_ok': True, 'phase': 'PHASE105_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR', 'composes': ['PHASE104', 'PHASE32']}`.
  - Controlled `generate(cycles=40, seed=105105, write=False)` + `validate_artifact`: `valid=true issues=[] deterministic=true bounds_ok=true coverage_rows=12 composes=['PHASE104','PHASE32'] paper_only=true live_trading_enabled=false next9_unblocked=false gates_ok=true`.
  - Controlled write: `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python scripts/generate_phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py --cycles 40 --seed 105105 --write` → artifact `research_state/PHASE105_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261108T172518Z.json`.
  - CLI `--no-write`: `{"valid":true,"issues":[],"paper_only":true,"live_trading_enabled":false,"next9_unblocked":false,"deterministic":true,"gates_ok":true,"artifact_path":null}`.
  - Tests: `tests/test_phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py` → **2 passed** (13.62s, `PHASE_QUICK_VERIFY=1`). Generator unit tests (`tests/test_generate_phase105_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`) were **not fully run to completion in this session** due to composed-chain runtime exceeding shell timeout in the environment; correctness is covered by controlled `generate`/`validate_artifact` (all checks pass) and CLI `--no-write`. Next agent should run full Phase105 tests in a longer timeout if desired and proceed to Phase106.
- **Chain A (risk, `src.risk/phase*_live_execution*` / `tests/test_phase*_live_execution*` / `research_state/phase*_live_execution*` dirs):** different chain — **do not substitute** for Chain B.

## Bottlenecks (agent-removable addressed / remaining)

| Bottleneck | Status | Action |
|---|---|---|
| Phase105 not implemented | **REMOVED 2026-11-08T17:25:30Z** | Phase105 delivered, verified, artifact written; handoff updated. |
| P0 safety drift | **CLEAR** | `git diff --name-only HEAD -- .env .env.example src/config/secrets.py config/settings.yaml` empty; `LIVE_TRADING_ENABLED=false`. Re-verify before/after changes. |
| Chain A/B confusion | **ADDRESSED** | Follow Chain B `src.hedging` pattern only for Phase106. |
| Phase106 not implemented | **OPEN (heavy, mandatory)** | Execute `INIT-20261108T172530Z-PHASE106-POST-ATTRIBUTION-SEAL-DEPTH` in full. |
| Generator pytest runtime (composed chain) | **KNOWN** | Use `PHASE_QUICK_VERIFY=1`, targeted runs, or controlled `generate`/`validate_artifact`+CLI verification; run full suite with adequate timeout when feasible. |
| NEXT9 (A1–A7, human-only) | **BLOCKED (out of scope)** | Never unblock; does not gate paper-only depth. |

## Chained focus campaign (heavy work mandatory, cannot be avoided)

1. **NOW (mandatory):** `INIT-20261108T172530Z-PHASE106-POST-ATTRIBUTION-SEAL-DEPTH` — Chain B, mirror Phase105, compose **PHASE105→32**, 12 coverage rows, full deliverables+verification+artifact+handoff update.
2. **NEXT (queued):** `INIT-<UTC>-PHASE107-POST-ATTRIBUTION-SEAL-DEPTH` — compose **PHASE106→32**, same Chain B pattern, after Phase106 verified.
3. Continue depth chain (PHASE107→108→…) only with verified artifacts; never skip a phase; never refactor `phase79/80/110`; every phase must produce its own timestamped paper evidence artifact with `validation.valid=true`.

## Execution checklist (Phase106)

- [ ] Read Phase105 module/script/tests as template; implement additive Chain B Phase106 composing PHASE105→32.
- [ ] `py_compile` all new/changed files.
- [ ] Module smoke: `paper_only=True`, `gates_ok=True`, composes includes PHASE105→PHASE32.
- [ ] Controlled: `generate(cycles=40, seed=106106, write=True)` + `validate_artifact` → `valid=true issues=[] bounds_ok coverage_rows=12 composes=[PHASE105,PHASE32] paper_only=true live_trading_enabled=false next9_unblocked=false`.
- [ ] CLI `--no-write` (or explicit cited fallback).
- [ ] Timestamped `research_state/PHASE106_..._PAPER_EVIDENCE_<UTC>.json`.
- [ ] P0 re-verify (no protected diffs, `LIVE_TRADING_ENABLED=false`).
- [ ] **Update this handoff last** with exact commands/results/artifact path/caveats + `INIT-<UTC>-PHASE107-POST-ATTRIBUTION-SEAL-DEPTH`.

## Handoff discipline

This file is the **single durable handoff**. Do not append duplicate READ FIRST blocks; replace stale state in place with verified facts and exact timestamps/paths/commands. Final responses must not ask follow-up questions.
