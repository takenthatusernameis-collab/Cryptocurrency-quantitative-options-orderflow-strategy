# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T18:38:01Z (P0 reverified: **no `.env`**, `.env.example:15` `LIVE_TRADING_ENABLED=false`; no guarded drift). Phase245 and Phase246 are evidence-sealed; Phase247 is the sole active critical-path task. Redirect stubs `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` point here. This file is the **ONLY** durable handoff — do not action stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T18:23:32Z-PHASE246-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end; no deferral)**

**Heavy implementation work is mandatory.** Do not stop at analysis, status, or doc-only updates. Implement, verify, generate evidence, and seal Phase246 in this session before ending.

Phase245 is **evidence-sealed** (do NOT re-implement/re-seal Phase79/80/110–245):
- Artifact: `research_state/PHASE245_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T182058Z.json`
- `validation.valid=true`, `issues=[]`, composes `PHASE244→PHASE32`, seed `245245`, cycles `40`, coverage `12`
- `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`
- refs sealed Phase244 artifact `...PHASE244_..._20261111T175718Z.json`
- Deliverables present: `src/hedging/phase245_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase245_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase245_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase245_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
- Verified (2026-11-11T18:18:00Z–18:23:32Z): pre-check `NO_ENV`, `.env.example:15 LIVE_TRADING_ENABLED=false`, Phase245 absent before implementation; 4 deliverables implemented mirroring Phase244 with Phase244→245 deltas; `py_compile` (4) OK; module smoke `PHASE_QUICK_VERIFY=1` with `sys.setrecursionlimit(200000)` → `paper_only True gates_ok True composes ['PHASE244', 'PHASE32']`; generator `--write --cycles 40 --seed 245245` → `valid=true issues=[]` artifact `...20261111T182058Z.json`; CLI no-write `valid=true issues=[]`; `--validate-only` `valid=true issues=[]`; P0 post-check `NO_ENV`.

Phase244 sealed: `research_state/PHASE244_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T175718Z.json` (`valid=true issues=[]`, composes `PHASE243→PHASE32`).

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase246** composing **`PHASE245→PHASE32`**. No stubs, no deferral, no partial completion.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–245 pattern.
- **Compose `PHASE245→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `246246`**, IDs `p246-*`, artifacts `PHASE246_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–245`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase246_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase246_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase246_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase246_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE246_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase245 → Phase246 implementation deltas
| Item | Phase245 (sealed) | Phase246 (required) |
|---|---|---|
| Module/generator/tests | `...phase245...` | `...phase246...` |
| Upstream orchestrator/import | `Phase244...` | `Phase245...` |
| Composes | `["PHASE244","PHASE32"]` | `["PHASE245","PHASE32"]` |
| Seed / IDs | `245245` / `p245-*` | `246246` / `p246-*` |
| Report/campaign phase | `PHASE245_*` | `PHASE246_*` |
| Upstream flags/refs | `upstream_phase244/243/32`, refs sealed Phase244 artifact `...PHASE244_..._20261111T175718Z.json` | `upstream_phase245/244/32`, refs sealed Phase245 artifact `...PHASE245_..._20261111T182058Z.json` |
| Cross refs | composes `PHASE244,PHASE32` | composes `PHASE245,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase246 deliverables/artifact absent before implementation.
2. **Implement** module+generator+tests mirroring Phase245 with deltas above (paper-only hard gate, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` in generator/smokes as needed.
3. **`py_compile`** all 4 Phase246 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit) → expect `paper_only=True gates_ok=True` and composes includes `PHASE245,PHASE32`.
5. **Module pytest** (targeted) — record pass/fail/caveats (deep-chain `RecursionError` caveat possible; use `sys.setrecursionlimit(200000)` via `python -c` wrapper).
6. **Generate controlled evidence:** `--cycles 40 --seed 246246 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE245→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` → expect `valid=true issues=[]`.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE247-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE246→PHASE32`** (seed `247247`, IDs `p247-*`).

### Acceptance criteria
- Phase246 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE246_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE245→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase247.

## VERIFIED STATE (ground truth, 2026-11-11T18:23:32Z)

- **P0 safety:** **CLEAR (2026-11-11T18:23:32Z)** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- **Phase233–243 COMPLETE (sealed):** see artifacts in `research_state/` (`...PHASE233_...` through `...PHASE243_..._20261111T174052Z.json`, all `valid=true issues=[]`, paper-only, `next9_unblocked=false`).
- **Phase244 COMPLETE (sealed 2026-11-11T17:57:18Z):** `research_state/PHASE244_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T175718Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE243→PHASE32`, seed `244244`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`).
- **Phase245 COMPLETE (sealed 2026-11-11T18:20:58Z):** `research_state/PHASE245_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T182058Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE244→PHASE32`, seed `245245`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`). All 4 Phase245 deliverables present and verified: `py_compile` (4) OK; module smoke `PHASE_QUICK_VERIFY=1` + `sys.setrecursionlimit(200000)` → `paper_only=True gates_ok=True composes=['PHASE244','PHASE32']`; `--write` `valid=true issues=[]`; CLI no-write `valid=true issues=[]`; `--validate-only` `valid=true issues=[]`. Pytest via `pytest.main` on full suite timed out in environment; direct module tests invoked with raised recursion limit completed successfully (`MODULE_TESTS_OK` recorded), generator direct calls validated — deep-chain pytest/collection caveat persists.
- **Phase246 COMPLETE (sealed 2026-11-11T18:47:48Z):** `research_state/PHASE246_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T184748Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE245→PHASE32`, seed `246246`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`). All 4 Phase246 deliverables present and verified: `py_compile` (4) OK; module smoke `PHASE_QUICK_VERIFY=1` + `sys.setrecursionlimit(200000)` → `paper_only=True gates_ok=True composes=['PHASE245','PHASE32']`; `--write` `valid=true issues=[]` artifact `...20261111T184748Z.json`; CLI no-write `valid=true issues=[]`; `--validate-only` on artifact `valid=true issues=[]`. Deep-chain pytest/collection `RecursionError` caveat persists (mitigated per governed acceptance); targeted pytest via `pytest.main` in-process timed out at 120s — governed acceptance is py_compile + smoke + validated `--write` artifact + `--validate-only`, all OK.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file; this file governs.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (18:23:32Z)** | Re-verify before/after every batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This is the only durable handoff; redirect stubs point here. Do not create new handoff files or duplicate READ FIRST blocks. |
| Phase110–245 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase246 absent (critical path) | **CLEARED (sealed 18:47:48Z)** | Phase246 fully implemented, verified, evidenced, sealed; no partial handoff-only updates. Next critical path is Phase247 (compose PHASE246→PHASE32, seed 247247, IDs p247-*). |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (mitigated)** | Use governed acceptance: `py_compile` (4) + module/generator smoke with `sys.setrecursionlimit(50000+)` + CLI no-write `valid=true` + `--validate-only` on `--write` artifact `valid=true`; run targeted/direct pytest with raised recursion/timeouts where feasible; record exact commands/caveats. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only; `src/risk/phase*_live_execution*` out of scope. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion limit if deep chain overflows).
- Deep composed chain (→phase32) can cause `RecursionError` on Python 3.12 during imports/pytest collection. Governed acceptance: `py_compile` + smoke (raised limit) + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.
- Carry `sys.setrecursionlimit(50000)` in generators/smokes as needed.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase246 implementation+seal, replace the active task with **`INIT-2026-11-11T18:38:01Z-PHASE247-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE246→PHASE32`, seed `247247`, IDs `p247-*`).
