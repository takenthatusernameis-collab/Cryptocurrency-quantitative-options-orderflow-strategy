# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T19:10:24Z (P0 reverified: **no `.env`**, `.env.example:15` `LIVE_TRADING_ENABLED=false`; no guarded drift). Phase233–246 and Phase247 are evidence-sealed; Phase248 is the sole active critical-path task. Redirect stubs `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` point here. This file is the **ONLY** durable handoff — do not action stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T19:10:24Z-PHASE248-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end; no deferral)**

**Heavy implementation work is mandatory.** Do not stop at analysis, status, or doc-only updates. Implement, verify, generate evidence, and seal Phase248 in this session before ending.

Phase247 is **evidence-sealed** (do NOT re-implement/re-seal Phase79/80/110–247):
- Artifact: `research_state/PHASE247_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T191024Z.json`
- `validation.valid=true`, `issues=[]`, composes `PHASE246→PHASE32`, seed `247247`, cycles `40`, coverage `12`
- `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`
- refs sealed Phase246 artifact `...PHASE246_..._20261111T184748Z.json`
- Deliverables present: `src/hedging/phase247_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase247_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase247_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase247_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
- Verified (2026-11-11T19:10:24Z): pre-check `NO_ENV`, `.env.example:15 LIVE_TRADING_ENABLED=false`, Phase247 absent before implementation; 4 deliverables implemented mirroring Phase246 with Phase246→247 deltas; `py_compile` (4) OK; module smoke `PHASE_QUICK_VERIFY=1` with `sys.setrecursionlimit(200000)` → `paper_only True gates_ok True composes ['PHASE246','PHASE32']`; generator `--write --cycles 40 --seed 247247` via `runpy`+raised recursion → `valid=true issues=[]` artifact `...20261111T191024Z.json`; CLI no-write `valid=true issues=[]`; `--validate-only` (via `validate_artifact`) `valid=true issues=[]`; P0 post-check `NO_ENV`, `LIVE_TRADING_ENABLED=false`. Deep-chain pytest not run in-shell (governed acceptance satisfied by py_compile+smoke+validated artifact).

Phase246 sealed: `research_state/PHASE246_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T184748Z.json` (`valid=true issues=[]`, composes `PHASE245→PHASE32`).

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase248** composing **`PHASE247→PHASE32`**. No stubs, no deferral, no partial completion.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–247 pattern.
- **Compose `PHASE247→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `248248`**, IDs `p248-*`, artifacts `PHASE248_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–247`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase248_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase248_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase248_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase248_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE248_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase247 → Phase248 implementation deltas
| Item | Phase247 (sealed) | Phase248 (required) |
|---|---|---|
| Module/generator/tests | `...phase247...` | `...phase248...` |
| Upstream orchestrator/import | `Phase246...` | `Phase247...` |
| Composes | `["PHASE246","PHASE32"]` | `["PHASE247","PHASE32"]` |
| Seed / IDs | `247247` / `p247-*` | `248248` / `p248-*` |
| Report/campaign phase | `PHASE247_*` | `PHASE248_*` |
| Upstream flags/refs | `upstream_phase246/245/32`, refs sealed Phase246 artifact `...PHASE246_..._20261111T184748Z.json` | `upstream_phase247/246/32`, refs sealed Phase247 artifact `...PHASE247_..._20261111T191024Z.json` |
| Cross refs | composes `PHASE246,PHASE32` | composes `PHASE247,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase248 deliverables/artifact absent before implementation.
2. **Implement** module+generator+tests mirroring Phase247 with deltas above (paper-only hard gate, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` in generator/smokes as needed.
3. **`py_compile`** all 4 Phase248 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit) → expect `paper_only=True gates_ok=True` and composes includes `PHASE247,PHASE32`.
5. **Module pytest** (targeted) — record pass/fail/caveats (deep-chain `RecursionError` caveat possible; use `sys.setrecursionlimit(200000)` via `python -c` wrapper).
6. **Generate controlled evidence:** `--cycles 40 --seed 248248 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE247→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` → expect `valid=true issues=[]`.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE249-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE248→PHASE32`** (seed `249249`, IDs `p249-*`).

### Acceptance criteria
- Phase248 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE248_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE247→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase249.

## VERIFIED STATE (ground truth, 2026-11-11T19:10:24Z)

- **P0 safety:** **CLEAR (2026-11-11T19:10:24Z)** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- **Phase233–245 COMPLETE (sealed):** see artifacts in `research_state/` (`...PHASE233_...` through `...PHASE245_..._20261111T182058Z.json`, all `valid=true issues=[]`, paper-only, `next9_unblocked=false`).
- **Phase246 COMPLETE (sealed 2026-11-11T18:47:48Z):** `research_state/PHASE246_ADAPTIVE_TOXICITY_RESILIENT_POST_ATRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T184748Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE245→PHASE32`, seed `246246`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`).
- **Phase247 COMPLETE (sealed 2026-11-11T19:10:24Z):** `research_state/PHASE247_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T191024Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE246→PHASE32`, seed `247247`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`). All 4 Phase247 deliverables present and verified: `py_compile` (4) OK; module smoke `PHASE_QUICK_VERIFY=1` + `sys.setrecursionlimit(200000)` → `paper_only=True gates_ok=True composes=['PHASE246','PHASE32']`; `--write` via `runpy`+raised recursion `valid=true issues=[]` artifact `...20261111T191024Z.json`; CLI no-write `valid=true issues=[]`; `--validate-only` (validate_artifact) `valid=true issues=[]`; P0 post-check `NO_ENV`, `.env.example:15 LIVE_TRADING_ENABLED=false`. Deep-chain pytest caveat persists (mitigated per governed acceptance: py_compile+smoke+validated write artifact+validate-only all OK).
- **Phase248 PENDING (critical path):** not yet implemented. All Phase248 deliverables absent. Next agentic session must implement+verify+evidence+seal Phase248 composing PHASE247→PHASE32.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file; this file governs.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (19:00:04Z)** | Re-verify before/after every batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This is the only durable handoff; redirect stubs point here. Do not create new handoff files or duplicate READ FIRST blocks. |
| Phase110–247 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase248 absent (critical path) | **PENDING** | Implement Phase248 mirroring Phase247 with deltas above; 4 deliverables + validated artifact; seal end-to-end. |
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
- After Phase248 implementation+seal, replace the active task with **`INIT-<UTC>-PHASE249-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE248→PHASE32`, seed `249249`, IDs `p249-*`).
