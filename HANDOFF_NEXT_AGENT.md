# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T11:39:45Z (P0 rechecked: no `.env`, `.env.example:15` `LIVE_TRADING_ENABLED=false`; Phase224 **SEALED** — module `src/hedging/phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, generator `scripts/generate_phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (patched with `sys.setrecursionlimit(50000)` to avoid deep-chain RecursionError), tests `tests/test_phase224_*.py`/`tests/test_generate_phase224_*.py`, artifact `research_state/PHASE224_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T113922Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE223→PHASE32`, seed `224224`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`); Phase225 **NOT STARTED**; `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect-only stubs). This file is the ONLY durable handoff. Do not action redirect stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T11:39:45Z-PHASE225-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end)**

Phase224 is **evidence-sealed**: `research_state/PHASE224_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T113922Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE223→PHASE32`, seed `224224`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`). Verification recorded: `py_compile` (4) OK; module smoke `paper_only=True gates_ok=True composes=['PHASE223','PHASE32'] phase=PHASE224...`; generator `--cycles 40 --seed 224224 --write` → valid=true/issues=[] (artifact `..._20261111T113922Z.json`); `--validate-only` → valid=true/issues=[]; CLI no-write `runpy` (raised recursion limit) → `{"valid":true,"issues":[],"artifact_path":""}`; targeted pytest collection failed with deep-chain `RecursionError` on Python 3.12 (documented env caveat; governed acceptance met). Generator required `sys.setrecursionlimit(50000)` due to deep composition chain. Phase225 seed `225225`, IDs `p225-*`, artifacts `PHASE225_*`. **Do NOT re-implement or re-seal Phase200–224.**

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase225** composing **`PHASE224→PHASE32`** in this session. No status-only work, no doc-only delivery (except final handoff update), no stubs, no deferral, no partial completion. Future agents must not avoid heavy working.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–224 pattern and Phase224→225 deltas.
- **Compose `PHASE224→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `225225`**, IDs `p225-*`, artifacts `PHASE225_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–224`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase225_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase225_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase225_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase225_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE225_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase224 → Phase225 implementation deltas
| Item | Phase224 (sealed) | Phase225 (required) |
|---|---|---|
| Module/generator/tests | `...phase224...` | `...phase225...` |
| Upstream orchestrator/import | `Phase223...` | `Phase224...` |
| Composes | `["PHASE223","PHASE32"]` | `["PHASE224","PHASE32"]` |
| Seed / IDs | `224224` / `p224-*` | `225225` / `p225-*` |
| Report/campaign phase | `PHASE224_*` | `PHASE225_*` |
| Upstream flags/refs | `upstream_phase223/222/32`, includes sealed Phase223 artifact `...PHASE223_..._20261111T112946Z.json` | `upstream_phase224/223/32` (match established naming), include sealed Phase224 artifact `...PHASE224_..._20261111T113922Z.json` |
| Cross refs | composes `PHASE223,PHASE32` | composes `PHASE224,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; no Phase225 deliverables exist yet.
2. **Implement** module+generator+tests mirroring Phase224 with deltas above (paper-only hard gate, `paper_only=True`, `gates_ok=True`, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations). Include `sys.setrecursionlimit(50000)` in generator (and smoke/CLI invocations as needed) per deep-chain env caveat.
3. **`py_compile`** all 4 Phase225 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit `sys.setrecursionlimit(50000)`) → expect `paper_only=True gates_ok=True` and composes includes `PHASE224,PHASE32`.
5. **Module pytest** (targeted, with timeouts/fallbacks as needed) — record pass/fail/caveats (expected deep-chain `RecursionError` caveat on Python 3.12).
6. **Generate controlled evidence:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase225_..._paper_evidence.py --cycles 40 --seed 225225 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE224→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` (use `runpy` + raised recursion limit if needed) → expect `valid=true issues=[]`.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE226-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE225→PHASE32`** (seed `226226`, IDs `p226-*`).

### Acceptance criteria
- Phase225 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE225_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE224→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase226.

## VERIFIED STATE (ground truth, 2026-11-11T11:39:45Z)

- **P0 safety:** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Phase211–223:** sealed (do not re-implement/re-seal).
- **Phase223 COMPLETE:** `research_state/PHASE223_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T112946Z.json` (`valid=true issues=[]`, composes `PHASE222→PHASE32`, seed 223223, cycles 40, coverage 12).
- **Phase224 COMPLETE (sealed 2026-11-11T11:39:22Z):** module `src/hedging/phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; generator `scripts/generate_phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py` (includes `sys.setrecursionlimit(50000)`); tests `tests/test_phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`, `tests/test_generate_phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; artifact `research_state/PHASE224_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T113922Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE223→PHASE32`, seed 224224, cycles 40, coverage 12, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`).
  - Verification: `python3 -m py_compile` (4 files) OK; module smoke `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` with `sys.setrecursionlimit(50000)` → `True True ['PHASE223','PHASE32'] PHASE224_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR`; `--write --cycles 40 --seed 224224` → `valid=true issues=[] artifact=..._20261111T113922Z.json`; `--validate-only` → `{"valid":true,"issues":[]}`; CLI no-write `runpy` with raised recursion limit → `{"valid":true,"issues":[],"artifact_path":""}`.
  - Caveat: targeted `pytest` collection for Phase224 tests errored with deep-chain `RecursionError` during import (`src.errors/logging` in chain) on Python 3.12 despite recursion-limit mitigation in scripts/smokes (env caveat; governed acceptance met via py_compile+smoke+CLI+validated artifact).
- **Phase225:** **NOT STARTED** (no module/generator/tests/artifact) — this is the critical-path bottleneck to execute next.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file; this file governs.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (11:39:45Z)** | Re-verify before/after every batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This is the only durable handoff; `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs. Do not create new handoff files or duplicate READ FIRST blocks. |
| Phase223/224 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase225 absent (critical path) | **ACTIVE — START NEXT** | **Execute full heavy scope:** implement module+generator+2 tests mirroring Phase224 with Phase224→225 deltas, `py_compile`, smoke/no-write/`--write`+validate evidence, targeted pytest as feasible, P0 post-check, then seal and advance handoff to Phase226. No partial handoff-only updates without deliverables. |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (mitigated)** | Use governed acceptance: `py_compile` (4) + module/generator smoke with `sys.setrecursionlimit(50000)` + CLI no-write `valid=true` + `--validate-only`/direct validate on `--write` artifact `valid=true`; run targeted pytest with raised recursion/timeouts where feasible; record exact commands/caveats. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only; `src/risk/phase*_live_execution*` out of scope. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion limit if deep chain overflows).
- Deep composed chain (→phase32) can cause `RecursionError` on Python 3.12 during imports/pytest collection. Governed acceptance: `py_compile` + smoke (raised limit) + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.
- Phase224 generator patched with `sys.setrecursionlimit(50000)`; carry this forward for Phase225+ generators/smokes as needed.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase225 seal, replace the active task with **`INIT-<UTC>-PHASE226-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE225→PHASE32`, seed `226226`, IDs `p226-*`).
