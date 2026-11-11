# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B (`src/hedging`) adaptive post-attribution seal orchestrator campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T20:26:06Z (UTC). **This file is the ONLY durable handoff.** `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs — do not action stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T20:26:06Z-PHASE250-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end; no deferral)**

**Heavy implementation work is mandatory.** Do not stop at analysis, status, or doc-only updates. Implement, verify, generate evidence, and seal Phase250 in this session before ending.

Phase248 is **evidence-sealed** (do NOT re-implement/re-seal Phase79/80/110–248):
- Artifact: `research_state/PHASE248_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T194827Z.json`
- Observed: `validation.valid=true`, `issues=[]`, seed `248248`, cycles `40`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false` (composes/coverage/gates per sealed evidence contract; treat artifact as source of truth).
- Deliverables present: `src/hedging/phase248_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase248_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase248_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase248_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.

Phase249 is **evidence-sealed** (do NOT re-implement/re-seal):
- Artifact: `research_state/PHASE249_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T202606Z.json` (`validation.valid=true`, `issues=[]`, seed `249249`, cycles `40`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, composes `PHASE248→PHASE32`, coverage=12, deterministic_replay_equal=true, bounds_ok=true).
- Deliverables present: `src/hedging/phase249_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `scripts/generate_phase249_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`, `tests/test_phase249_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase249_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`.
- Verification record: `py_compile` 4 files OK; module smoke `PHASE_QUICK_VERIFY=1` `gates_ok=True composes=['PHASE248','PHASE32']`; CLI no-write `valid=true issues=[]`; `--write` artifact path above; `--validate-only` `valid=true issues=[]` exit 0. Deep-chain pytest collection hit `RecursionError`/timeout on Python 3.12 (governed caveat: smokes + validate-only substitute; record caveat).

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase250** composing **`PHASE249→PHASE32`** (12 coverage rows: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). No stubs, no deferral, no partial completion.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–248 pattern.
- **Compose `PHASE248→PHASE32`**. Seed `249249`, IDs `p249-*`, artifacts `PHASE249_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–248`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase249_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase249_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase249_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase249_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE249_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase249 → Phase250 implementation deltas
| Item | Phase249 (sealed) | Phase250 (required) |
|---|---|---|
| Module/generator/tests | `...phase249...` | `...phase250...` |
| Upstream orchestrator/import | `Phase248...` | `Phase249...` |
| Composes | `["PHASE248","PHASE32"]` | `["PHASE249","PHASE32"]` |
| Seed / IDs | `249249` / `p249-*` | `250250` / `p250-*` |
| Report/campaign phase | `PHASE249_*` | `PHASE250_*` |
| Upstream flags/refs | `upstream_phase248/247/32`, refs sealed Phase248 artifact `research_state/PHASE248_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T194827Z.json` | `upstream_phase249/248/32`, refs sealed Phase249 artifact `research_state/PHASE249_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T202606Z.json` |
| Cross refs | composes `PHASE248,PHASE32` | composes `PHASE249,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase249 deliverables/artifact absent before implementation.
2. **Implement** module+generator+tests mirroring Phase248 with deltas above (paper-only hard gate, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` (or higher as needed) in generator/smokes.
3. **`py_compile`** all 4 Phase249 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit, e.g. 200000) → expect `paper_only=True gates_ok=True` and composes includes `PHASE248,PHASE32`.
5. **Module pytest** (targeted) — record pass/fail/caveats (deep-chain `RecursionError` caveat possible; use raised recursion wrapper).
6. **Generate controlled evidence:** `--cycles 40 --seed 249249 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE248→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` → expect `valid=true issues=[]` (use `runpy`+raised recursion if needed).
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE251-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE250→PHASE32`** (seed `251251`, IDs `p251-*`).

### Phase249 execution record (complete, this session)
- Commands run: `py_compile` ×4 OK; module smoke `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (recursionlimit 200000) → `paper_only=True gates_ok=True composes=['PHASE248','PHASE32']`; CLI no-write `python3 scripts/generate_phase249...py --cycles 40 --seed 249249` → `valid=true issues=[]`; `--write` → artifact `research_state/PHASE249_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T202606Z.json`; `--validate-only` → `valid=true issues=[]` exit 0.
- P0 post-check: no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; no guarded drift.
- Caveat: deep-chain pytest collection `RecursionError`/timeout (Python 3.12) — governed acceptance applied (py_compile + smokes + validate-only recorded).

### Acceptance criteria
- Phase250 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE250_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE249→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase251.

## VERIFIED STATE (ground truth, 2026-11-11T20:10:47Z)

- **P0 safety:** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- **Phase233–247 COMPLETE (sealed):** prior post-attribution seal phases evidenced in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-seal.
- **Phase248 COMPLETE (sealed 2026-11-11T19:48:27Z):** `research_state/PHASE248_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T194827Z.json` (`valid=true`, `issues=[]`, seed `248248`, cycles `40`, paper-only, `next9_unblocked=false`). 4 deliverables present.
- **Phase249 COMPLETE (sealed 2026-11-11T20:26:06Z):** `research_state/PHASE249_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T202606Z.json` (`valid=true`, `issues=[]`, seed `249249`, cycles `40`, composes `PHASE248→PHASE32`, coverage=12, paper-only, `next9_unblocked=false`). 4 deliverables present.
- **Phase250 PENDING (critical path):** not implemented; `src/hedging/phase250*`, `scripts/generate_phase250*`, `tests/*phase250*` absent. Next session must implement+verify+evidence+seal Phase250 composing `PHASE249→PHASE32` (seed `250250`, IDs `p250-*`).
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (20:09:10Z)** | Re-verify before/after batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This file is sole durable handoff; stubs redirect here. Do not create duplicates. |
| Phase110–248 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase249 absent (critical path) | **CLEARED** | Phase249 sealed end-to-end 2026-11-11T20:26:06Z; artifact `...T202606Z.json` (`valid=true`, `issues=[]`). |
| Phase250 absent (critical path) | **PENDING — ACTIVE NOW** | Implement Phase250 (compose `PHASE249→PHASE32`, seed `250250`, `p250-*`), 4 deliverables + validated artifact; seal end-to-end. |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (mitigated)** | Governed acceptance: `py_compile` (4) + module/generator smoke with raised recursion + CLI no-write `valid=true` + validated `--write` artifact (`--validate-only`) with guards/coverage/determinism/bounds intact; targeted pytest with raised recursion/timeouts where feasible; record commands/caveats. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion if deep chain overflows).
- Deep composed chain (→phase32) can raise `RecursionError` on Python 3.12 during imports/pytest collection. Use governed acceptance and record exact outcomes.
- Carry `sys.setrecursionlimit(50000)` (or higher) in generators/smokes as needed.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase250 seal, replace active task with **`INIT-<UTC>-PHASE251-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE250→PHASE32`, seed `251251`, IDs `p251-*`).
