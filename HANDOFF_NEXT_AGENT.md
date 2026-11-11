# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B (`src/hedging`) adaptive post-attribution seal orchestrator campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T21:29:00Z (UTC). **This file is the ONLY durable handoff.** `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs — do not action stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T21:29:00Z-PHASE251-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end; no deferral)**

**Heavy implementation work is mandatory.** Do not stop at analysis, status, or doc-only updates. Implement, verify, generate evidence, and seal Phase251 in this session before ending.

Phase250 is **evidence-sealed** (do NOT re-implement/re-seal Phase79/80/110–250):
- Artifact: `research_state/PHASE250_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T212714Z.json` (`validation.valid=true`, `issues=[]`, seed `250250`, cycles `40`, paper-only, `live_trading_enabled=false`, `next9_unblocked=false`).

Phase249 is **evidence-sealed** (do NOT re-implement/re-seal):
- Artifact: `research_state/PHASE249_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T202606Z.json` (`validation.valid=true`, `issues=[]`, seed `249249`, cycles `40`, composes `PHASE248→PHASE32`, coverage=12, deterministic_replay_equal=true, bounds_ok=true, paper-only, `live_trading_enabled=false`, `next9_unblocked=false`).

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase251** composing **`PHASE250→PHASE32`** (12 coverage rows: Deribit/OKX/Bybit/Binance × BTC/ETH/SOL). No stubs, no deferral, no partial completion.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–250 pattern exactly except Phase251 deltas.
- **Compose `PHASE250→PHASE32`**. Seed `251251`, IDs `p251-*`, artifacts `PHASE251_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–250`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase251_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase251_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase251_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase251_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE251_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase250 → Phase251 implementation deltas
| Item | Phase250 (sealed) | Phase251 (required) |
|---|---|---|
| Module/generator/tests | `...phase250...` | `...phase251...` |
| Upstream orchestrator/import | `Phase249...` | `Phase250...` |
| Composes | `["PHASE249","PHASE32"]` | `["PHASE250","PHASE32"]` |
| Seed / IDs | `250250` / `p250-*` | `251251` / `p251-*` |
| Report/campaign phase | `PHASE250_*` | `PHASE251_*` |
| Upstream flags/refs | `upstream_phase249/248/32`, refs sealed Phase249 artifact `...PHASE249_...T202606Z.json` | `upstream_phase250/249/32`, refs sealed Phase250 artifact `...PHASE250_...T212714Z.json` |
| Cross refs | composes `PHASE249,PHASE32` | composes `PHASE250,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase251 deliverables/artifact absent before implementation.
2. **Implement** module+generator+tests mirroring Phase250 with deltas above (paper-only hard gate, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` (or higher as needed) in generator/smokes.
3. **`py_compile`** all 4 Phase251 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit, e.g. 200000) → expect `paper_only=True gates_ok=True` and composes includes `PHASE250,PHASE32`.
5. **Module pytest** (targeted) — record pass/fail/caveats (deep-chain `RecursionError` caveat possible; use raised recursion wrapper/timeouts).
6. **Generate controlled evidence:** `--cycles 40 --seed 251251 --write` (with `PHASE_QUICK_VERIFY=1` given deep-chain caveat) then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE250→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` → expect `valid=true issues=[]` (use `runpy`+raised recursion if needed).
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE252-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE251→PHASE32`** (seed `252252`, IDs `p252-*`).

### Acceptance criteria
- Phase251 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE251_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE250→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase252.

## VERIFIED STATE (ground truth, 2026-11-11T21:29:00Z)

- **P0 safety:** **CLEAR** — no `.env` (absent); `.env.example:15` `LIVE_TRADING_ENABLED=false` (verified).
- **Phase233–250 COMPLETE (sealed):** prior post-attribution seal phases evidenced in `research_state/` (`valid=true issues=[]`, paper-only, `next9_unblocked=false`) — do not re-seal.
  - Phase250 COMPLETE (sealed 2026-11-11T21:27:14Z): `research_state/PHASE250_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T212714Z.json` (`valid=true`, `issues=[]`, seed `250250`, cycles `40`, composes `PHASE249→PHASE32`, coverage=12, paper-only, `next9_unblocked=false`). 4 deliverables present in `src/hedging/`, `scripts/`, `tests/`.
  - Phase250 verification record: `py_compile` 4 files OK; module smoke `PHASE_QUICK_VERIFY=1` `gates_ok=True composes=['PHASE249','PHASE32']`; CLI `--write` `valid=true issues=[]` artifact `...PHASE250_...T212714Z.json`; `--validate-only` `valid=true issues=[]`; CLI no-write smoke `valid=true issues=[]`; pytest 5 passed (121s, deep-chain caveat).
- **Phase251 PENDING (critical path):** not implemented; `src/hedging/phase251*`, `scripts/generate_phase251*`, `tests/*phase251*`, and `research_state/PHASE251_*` absent. **Active task = implement+verify+evidence+seal Phase251 composing `PHASE250→PHASE32` (seed `251251`, IDs `p251-*`).**
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (21:29:00Z)** | Re-verify before/after batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This file is sole durable handoff; stubs redirect here. Do not create duplicates. |
| Phase110–250 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase251 absent (critical path) | **PENDING — ACTIVE NOW** | Implement Phase251 (compose `PHASE250→PHASE32`, seed `251251`, `p251-*`), 4 deliverables + validated artifact; seal end-to-end. |
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
- After Phase251 seal, replace active task with **`INIT-<UTC>-PHASE252-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE251→PHASE32`, seed `252252`, IDs `p252-*`).
# SECONDARY HANDOFF — REDIRECT STUB (NOT ACTIONABLE)

**Refreshed:** 2026-11-11T21:29:00Z
**Status:** SUPERSEDED. This file is not a task source.

**Single durable handoff (READ FIRST):** `HANDOFF_NEXT_AGENT.md`
- **Active mandatory task:** `INIT-2026-11-11T21:29:00Z-PHASE251-POST-ATTRIBUTION-SEAL-DEPTH` (Chain B `src/hedging`, paper-only, compose `PHASE250→PHASE32`, seed `251251`, IDs `p251-*`). Implement+verify+evidence+seal Phase251 end-to-end; then advance to `INIT-<UTC>-PHASE252-POST-ATTRIBUTION-SEAL-DEPTH`.
- Phase250 COMPLETE/sealed: `research_state/PHASE250_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T212714Z.json` (`valid=true`, `issues=[]`).

**Guards:** NO live trading, no `.env`, `.env.example:15` `LIVE_TRADING_ENABLED=false`, NEXT9 `next9_unblocked=false` (human-only). Do not action this file.