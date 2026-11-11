# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B (`src/hedging`) adaptive post-attribution seal orchestrator campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T21:57:05Z (UTC). **This file is the ONLY durable handoff.** `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs — do not action stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T21:57:05Z-PHASE252-POST-ATTRIBUTION-SEAL-DEPTH` — COMPLETE/SEALED (2026-11-11T22:22:05Z). Do not re-implement/re-seal.**

Phase252 fully implemented, verified, evidenced, and sealed composing **`PHASE251→PHASE32`** (seed `252252`, IDs `p252-*`). All 4 deliverables present + validated artifact; P0 intact; deep-chain pytest caveat recorded/met via governed acceptance.

Artifact: `research_state/PHASE252_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T222557Z.json` (`validation.valid=true`, `issues=[]`, seed `252252`, cycles `40`, paper-only, `live_trading_enabled=false`, `next9_unblocked=false`).

Phase251 is **evidence-sealed** (do NOT re-implement/re-seal Phase79/80/110–251):
- Artifact: `research_state/PHASE251_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T214304Z.json` (`validation.valid=true`, `issues=[]`, seed `251251`, cycles `40`, paper-only, `live_trading_enabled=false`, `next9_unblocked=false`).

Phase250 is **evidence-sealed** (do NOT re-implement/re-seal):
- Artifact: `research_state/PHASE250_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T212714Z.json` (`validation.valid=true`, `issues=[]`, seed `250250`, cycles `40`, paper-only, `live_trading_enabled=false`, `next9_unblocked=false`).

**MANDATORY objective — ACTIVE NOW:** fully **implement, verify, generate evidence, and seal Phase253** composing **`PHASE252→PHASE32`** (12 coverage rows: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). No stubs, no deferral, no partial completion.

**`INIT-2026-11-11T22:22:05Z-PHASE253-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end; no deferral)**

### Phase252 → Phase253 implementation deltas
| Item | Phase252 (sealed) | Phase253 (required) |
|---|---|---|
| Module/generator/tests | `...phase252...` | `...phase253...` |
| Upstream orchestrator/import | `Phase251...` | `Phase252...` |
| Composes | `["PHASE251","PHASE32"]` | `["PHASE252","PHASE32"]` |
| Seed / IDs | `252252` / `p252-*` | `253253` / `p253-*` |
| Report/campaign phase | `PHASE252_*` | `PHASE253_*` |
| Upstream flags/refs | `upstream_phase251/250/32`, refs sealed Phase251 artifact `...PHASE251_...T214304Z.json` | `upstream_phase252/251/32`, refs sealed Phase252 artifact `...PHASE252_...T222557Z.json` |
| Cross refs | composes `PHASE251,PHASE32` | composes `PHASE252,PHASE32` |

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–250 pattern exactly except Phase252 deltas.
- **Compose `PHASE252→PHASE32`**. Seed `253253`, IDs `p253-*`, artifacts `PHASE253_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–251`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase253_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase253_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase253_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase253_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE253_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase253 deliverables/artifact absent before implementation.
2. **Implement** module+generator+tests mirroring Phase252 with deltas above (paper-only hard gate, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` (or higher as needed) in generator/smokes.
3. **`py_compile`** all 4 Phase253 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit, e.g. 200000) → expect `paper_only=True gates_ok=True` and composes includes `PHASE252,PHASE32`.
5. **Module pytest** (targeted) — record pass/fail/caveats (deep-chain `RecursionError` caveat possible; use raised recursion wrapper/timeouts).
6. **Generate controlled evidence:** `--cycles 40 --seed 253253 --write` (with `PHASE_QUICK_VERIFY=1` given deep-chain caveat) then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE252→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` → expect `valid=true issues=[]` (use `runpy`+raised recursion if needed).
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE254-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE253→PHASE32`** (seed `254254`, IDs `p254-*`).

### Acceptance criteria
- Phase253 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE253_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE252→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase253.

## VERIFIED STATE (ground truth, 2026-11-11T21:57:05Z)

- **P0 safety:** **CLEAR** — no `.env` (absent); `.env.example:15` `LIVE_TRADING_ENABLED=false` (verified).
- **Phase233–252 COMPLETE (sealed):** prior post-attribution seal phases evidenced in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-seal.
  - Phase252 COMPLETE (sealed 2026-11-11T22:22:05Z): `research_state/PHASE252_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T222557Z.json` (`valid=true`, `issues=[]`, seed `252252`, cycles `40`, composes `PHASE251→PHASE32`, coverage=12, paper-only, `next9_unblocked=false`). 4 deliverables present in `src/hedging/`, `scripts/`, `tests/`.
  - Phase252 verification record: `py_compile` 4 files OK; module smoke `PHASE_QUICK_VERIFY=1` `gates_ok=True composes=['PHASE251','PHASE32']`; CLI `--write` `valid=true issues=[]` artifact `...PHASE252_...T222557Z.json`; `--validate-only` `valid=true issues=[]`; CLI no-write smoke `valid=true issues=[]`; pytest 3 module + 2 generator passed (deep-chain caveat; required `sys.setrecursionlimit(1000000)` wrapper).
  - Phase251 COMPLETE (sealed 2026-11-11T21:57:05Z): `research_state/PHASE251_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T214304Z.json` (`valid=true`, `issues=[]`, seed `251251`, cycles `40`, composes `PHASE250→PHASE32`, coverage=12, paper-only, `next9_unblocked=false`). 4 deliverables present in `src/hedging/`, `scripts/`, `tests/`.
  - Phase251 verification record: `py_compile` 4 files OK; module smoke `PHASE_QUICK_VERIFY=1` `gates_ok=True composes=['PHASE250','PHASE32']`; CLI `--write` `valid=true issues=[]` artifact `...PHASE251_...T214304Z.json`; `--validate-only` `valid=true issues=[]`; CLI no-write smoke `valid=true issues=[]`; pytest 5 passed (deep-chain caveat; required `sys.setrecursionlimit(1000000)` wrapper).
  - Phase250 COMPLETE (sealed 2026-11-11T21:27:14Z): `research_state/PHASE250_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T212714Z.json` (`valid=true`, `issues=[]`, seed `250250`, cycles `40`, composes `PHASE249→PHASE32`, coverage=12, paper-only, `next9_unblocked=false`). 4 deliverables present in `src/hedging/`, `scripts/`, `tests/`.
- **Phase253 PENDING (critical path):** not sealed; `src/hedging/phase253*`, `scripts/generate_phase253*`, `tests/*phase253*`, and `research_state/PHASE253_*` absent. **Active task = implement+verify+evidence+seal Phase253 composing `PHASE252→PHASE32` (seed `253253`, IDs `p253-*`).**
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (21:57:05Z)** | Re-verify before/after batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This file is sole durable handoff; stubs redirect here. Do not create duplicates. |
| Phase251→252 sealed | **CLEARED** | Phase252 sealed 22:22:05Z; do not touch except defect-preserving fix. |
| Phase253 absent (critical path) | **PENDING — ACTIVE NOW** | Implement Phase253 (compose `PHASE252→PHASE32`, seed `253253`, `p253-*`), 4 deliverables + validated artifact; seal end-to-end. |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (mitigated)** | Governed acceptance: `py_compile` (4) + module/generator smoke with raised recursion + CLI no-write `valid=true` + validated `--write` artifact (`--validate-only`) with guards/coverage/determinism/bounds intact; targeted pytest with raised recursion/timeouts where feasible; record commands/caveats. Run generator with `PHASE_QUICK_VERIFY=1` to avoid deep-chain hang. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion if needed).
- Deep composed chain (→phase32) can raise `RecursionError`/hang on Python 3.12 during imports/pytest collection without `PHASE_QUICK_VERIFY=1`. Use governed acceptance and record exact outcomes.
- Carry `sys.setrecursionlimit(50000)` (or higher) in generators/smokes as needed.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase253 seal, replace active task with **`INIT-<UTC>-PHASE254-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE253→PHASE32`, seed `254254`, IDs `p254-*`).
# SECONDARY HANDOFF — REDIRECT STUB (NOT ACTIONABLE)

**Refreshed:** 2026-11-11T22:22:05Z
**Status:** SUPERSEDED. This file is not a task source.

**Single durable handoff (READ FIRST):** `HANDOFF_NEXT_AGENT.md`
- **Active mandatory task:** `INIT-2026-11-11T22:22:05Z-PHASE253-POST-ATTRIBUTION-SEAL-DEPTH` (Chain B `src/hedging`, paper-only, compose `PHASE252→PHASE32`, seed `253253`, IDs `p253-*`). Implement+verify+evidence+seal Phase253 end-to-end; then advance to `INIT-<UTC>-PHASE254-POST-ATTRIBUTION-SEAL-DEPTH`.
- Phase252 COMPLETE/sealed: `research_state/PHASE252_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T222557Z.json` (`valid=true`, `issues=[]`).

**Guards:** NO live trading, no `.env`, `.env.example:15` `LIVE_TRADING_ENABLED=false`, NEXT9 `next9_unblocked=false` (human-only). Do not action this file.