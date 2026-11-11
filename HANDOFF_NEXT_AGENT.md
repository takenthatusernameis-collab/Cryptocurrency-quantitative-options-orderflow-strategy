# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T17:31:16Z (P0 reverified: **no `.env`**, `.env.example:15` `LIVE_TRADING_ENABLED=false`; no guarded drift). Phase243 is evidence-sealed; Phase244 is the sole active critical-path task. Redirect stubs `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` point here. This file is the **ONLY** durable handoff — do not action stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T17:31:16Z-PHASE244-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end; no deferral)**

**Heavy implementation work is mandatory.** Do not stop at analysis, status, or doc-only updates. Implement, verify, generate evidence, and seal Phase244 in this session before ending.

Phase243 is **evidence-sealed** (do NOT re-implement/re-seal Phase79/80/110–243):
- Artifact: `research_state/PHASE243_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T174052Z.json`
- `validation.valid=true`, `issues=[]`, composes `PHASE242→PHASE32`, seed `243243`, cycles `40`, coverage `12`
- `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`
- refs sealed Phase242 artifact `...PHASE242_..._20261111T171858Z.json` (per Phase243 module/chain)
- Deliverables present: `src/hedging/phase243_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase243_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase243_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase243_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
- Verified: `py_compile` (4) OK; module smoke `paper_only=True gates_ok=True` composes `PHASE242,PHASE32`; `--write` artifact `valid=true issues=[]`; CLI no-write `valid=true issues=[]`; pytest 5 passed.

Phase242 sealed: `research_state/PHASE242_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T171858Z.json` (`valid=true issues=[]`, composes `PHASE241→PHASE32`).

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase244** composing **`PHASE243→PHASE32`**. No stubs, no deferral, no partial completion.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–243 pattern.
- **Compose `PHASE243→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `244244`**, IDs `p244-*`, artifacts `PHASE244_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–243`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase244_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase244_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase244_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase244_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE244_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase243 → Phase244 implementation deltas
| Item | Phase243 (sealed) | Phase244 (required) |
|---|---|---|
| Module/generator/tests | `...phase243...` | `...phase244...` |
| Upstream orchestrator/import | `Phase242...` | `Phase243...` |
| Composes | `["PHASE242","PHASE32"]` | `["PHASE243","PHASE32"]` |
| Seed / IDs | `243243` / `p243-*` | `244244` / `p244-*` |
| Report/campaign phase | `PHASE243_*` | `PHASE244_*` |
| Upstream flags/refs | `upstream_phase242/241/32`, refs sealed Phase242 artifact `...PHASE242_..._20261111T171858Z.json` | `upstream_phase243/242/32`, refs sealed Phase243 artifact `...PHASE243_..._20261111T174052Z.json` |
| Cross refs | composes `PHASE242,PHASE32` | composes `PHASE243,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase244 deliverables/artifact absent before implementation.
2. **Implement** module+generator+tests mirroring Phase243 with deltas above (paper-only hard gate, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` in generator/smokes as needed.
3. **`py_compile`** all 4 Phase244 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit) → expect `paper_only=True gates_ok=True` and composes includes `PHASE243,PHASE32`.
5. **Module pytest** (targeted) — record pass/fail/caveats (deep-chain `RecursionError` caveat possible).
6. **Generate controlled evidence:** `--cycles 40 --seed 244244 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE243→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` → expect `valid=true issues=[]`.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE245-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE244→PHASE32`** (seed `245245`, IDs `p245-*`).

### Acceptance criteria
- Phase244 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE244_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE243→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase245.

## VERIFIED STATE (ground truth, 2026-11-11T17:31:16Z)

- **P0 safety:** **CLEAR (2026-11-11T17:31:16Z)** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- **Phase233–241 COMPLETE (sealed):** see artifacts in `research_state/` (`...PHASE233_..._20261111T135740Z.json` through `...PHASE241_..._20261111T162848Z.json`, all `valid=true issues=[]`, paper-only, `next9_unblocked=false`).
- **Phase242 COMPLETE (sealed 2026-11-11T17:18:58Z):** `research_state/PHASE242_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T171858Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE241→PHASE32`, seed `242242`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`).
- **Phase243 COMPLETE (sealed 2026-11-11T17:40:52Z):** `research_state/PHASE243_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T174052Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE242→PHASE32`, seed `243243`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`). All 4 Phase243 deliverables present and verified.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file; this file governs.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (17:31:16Z)** | Re-verify before/after every batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This is the only durable handoff; redirect stubs point here. Do not create new handoff files or duplicate READ FIRST blocks. |
| Phase110–243 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase244 absent (critical path) | **ACTIVE — START NOW** | **Execute full heavy scope:** implement module+generator+2 tests mirroring Phase243 with Phase243→244 deltas, `py_compile`, smoke/no-write/`--write`+validate evidence, targeted pytest as feasible, P0 post-check, then seal and advance handoff to Phase245. No partial handoff-only updates without deliverables. |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (mitigated)** | Use governed acceptance: `py_compile` (4) + module/generator smoke with `sys.setrecursionlimit(50000)` + CLI no-write `valid=true` + `--validate-only` on `--write` artifact `valid=true`; run targeted pytest with raised recursion/timeouts where feasible; record exact commands/caveats. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only; `src/risk/phase*_live_execution*` out of scope. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion limit if deep chain overflows).
- Deep composed chain (→phase32) can cause `RecursionError` on Python 3.12 during imports/pytest collection. Governed acceptance: `py_compile` + smoke (raised limit) + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.
- Carry `sys.setrecursionlimit(50000)` in generators/smokes as needed.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase244 implementation+seal, replace the active task with **`INIT-<UTC>-PHASE245-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE244→PHASE32`, seed `245245`, IDs `p245-*`).
