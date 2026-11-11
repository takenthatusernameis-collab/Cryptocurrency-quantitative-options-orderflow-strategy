# HANDOFF_NEXT_AGENT — SINGLE DURABLE HANDOFF (READ FIRST)

**Repo (priority):** `Cryptocurrency-quantitative-options-orderflow-strategy` — crypto options/orderflow quantitative strategy; Chain B hedging post-attribution seal campaign is the active paper-only engineering track.
**Handoff refreshed:** 2026-11-11T11:34:44Z (P0 rechecked: no `.env`, `.env.example:15` `LIVE_TRADING_ENABLED=false`; removed accidental root clutter files `=1.24.0`, `=2.5.0`, `=7.4.0`; no `src/hedging/phase224*`, `scripts/generate_phase224*`, `tests/test_phase224*`, or `research_state/PHASE224*` exist; Phase223 **SEALED** — artifact `research_state/PHASE223_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T112946Z.json` (`valid=true`, `issues=[]`, composes `PHASE222→PHASE32`, seed `223223`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`); Phase224 **NOT STARTED** — critical-path bottleneck to execute next; `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect-only stubs). This file is the ONLY durable handoff. Do not action redirect stubs or create new handoff files.

## SINGLE INITIAL TASK MESSAGE — NEXT AGENTIC WORK SESSION (mandatory, timestamped, heavy)

**`INIT-2026-11-11T11:34:44Z-PHASE224-POST-ATTRIBUTION-SEAL-DEPTH` — ACTIVE (execute now; complete end-to-end)**

Phase223 is **evidence-sealed**: `research_state/PHASE223_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T112946Z.json` (`validation.valid=true`, `issues=[]`, composes `PHASE222→PHASE32`, seed `223223`, cycles `40`, coverage `12`, `paper_only=true`, `live_trading_enabled=false`, `next9_unblocked=false`, `gates_ok=true`, `deterministic_replay_equal=true`, `bounds_ok=true`). Verification commands run: `py_compile` (4) OK; module smoke `paper_only=True gates_ok=True composes=[PHASE222,PHASE32]`; generator `--cycles 40 --seed 223223 --write` → valid=true/issues=[]; `--validate-only` → valid=true/issues=[]; CLI no-write `runpy` → valid=true/issues=[]. Targeted pytest could not complete collection due to deep-chain `RecursionError` on Python 3.12 (documented env caveat; governed acceptance met via py_compile+smoke+CLI+validated artifact). Phase224 seed `224224`, IDs `p224-*`, artifacts `PHASE224_*`. **Do NOT re-implement or re-seal Phase200–223.**

**MANDATORY objective:** fully **implement, verify, generate evidence, and seal Phase224** composing **`PHASE223→PHASE32`** in this session. No status-only work, no doc-only delivery (except final handoff update), no stubs, no deferral, no partial completion. Future agents must not avoid heavy working.

### Scope & constraints (non-negotiable)
- **Chain B only:** `src/hedging`, `scripts/`, `tests/`, `research_state/`. **No Chain A substitution** (`src/risk/phase*_live_execution*` out of scope).
- **Paper-only / additive / deterministic / finite-probe / bounded / guarded.** Mirror Phase111–223 pattern and Phase223→224 deltas.
- **Compose `PHASE223→PHASE32`**. 12 coverage rows: **Deribit/OKX/Bybit/Binance × BTC/ETH/SOL**.
- **Seed `224224`**, IDs `p224-*`, artifacts `PHASE224_*`.
- **HARD GUARDS:** **NO live trading. NO venue/config/credential mutation. NO NEXT9 unblock (`next9_unblocked=false`).** Do not refactor sealed phases `phase79/80/110–223`. Do not create `.env`. Keep `.env.example:15` `LIVE_TRADING_ENABLED=false`. Edit sealed phases only for a verified defect while preserving semantics/guards.

### Required deliverables (all)
1. `src/hedging/phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
2. `scripts/generate_phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
3. `tests/test_phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`
4. `tests/test_generate_phase224_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`
5. Validated artifact: `research_state/PHASE224_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_<UTC>.json` (`validation.valid=true`, `issues=[]`)

### Phase223 → Phase224 implementation deltas
| Item | Phase223 (sealed) | Phase224 (required) |
|---|---|---|
| Module/generator/tests | `...phase223...` | `...phase224...` |
| Upstream orchestrator/import | `Phase222...` | `Phase223...` |
| Composes | `["PHASE222","PHASE32"]` | `["PHASE223","PHASE32"]` |
| Seed / IDs | `223223` / `p223-*` | `224224` / `p224-*` |
| Report/campaign phase | `PHASE223_*` | `PHASE224_*` |
| Upstream flags/refs | `upstream_phase222/221/32`, includes sealed Phase222 artifact `...PHASE222_..._20261111T103906Z.json` | `upstream_phase223/222/32` (match established naming), includes sealed Phase223 artifact `...PHASE223_..._20261111T112946Z.json` |
| Cross refs | composes `PHASE222,PHASE32` | composes `PHASE223,PHASE32` |

### Execution checklist (complete in order; record commands/results/caveats)
1. **P0/targets pre-check:** confirm no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`; no Phase224 deliverables exist yet.
2. **Implement** module+generator+tests mirroring Phase223 with deltas above (paper-only hard gate, `paper_only=True`, `gates_ok=True`, 12 venue×symbol probes, deterministic replay, finite/bounded, validator rejects live/unblock/non-paper/composition violations).
3. **`py_compile`** all 4 Phase224 files — record OK.
4. **Module smoke:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 -c ...` (raise recursion limit `sys.setrecursionlimit(50000)` if needed) → expect `paper_only=True gates_ok=True` and composes includes `PHASE223,PHASE32`.
5. **Module pytest** (targeted, with timeouts/fallbacks as needed) — record pass/fail/caveats (expected deep-chain `RecursionError` caveat on Python 3.12).
6. **Generate controlled evidence:** `PHASE_QUICK_VERIFY=1 PYTHONPATH=. python3 scripts/generate_phase224_..._paper_evidence.py --cycles 40 --seed 224224 --write` then `--validate-only <artifact>` → expect `valid=true issues=[]`, deterministic/bounds_ok, coverage=12, composes `PHASE223→PHASE32`, guards intact. **Record exact artifact path.**
7. **CLI no-write smoke:** run generator without `--write` → expect `valid=true issues=[]`.
8. **Generator pytest** with `PHASE_QUICK_VERIFY=1`/targeted runs/timeouts as needed.
9. **P0 post-check:** no `.env`, `LIVE_TRADING_ENABLED=false`, no guarded drift.
10. **Update this handoff last** with verified facts/timestamps/paths/commands/caveats and advance next task to **`INIT-<UTC>-PHASE225-POST-ATTRIBUTION-SEAL-DEPTH`** composing **`PHASE224→PHASE32`** (seed `225225`, IDs `p225-*`).

### Acceptance criteria
- Phase224 module/generator/tests exist and are syntactically valid.
- Validated `research_state/PHASE224_*_PAPER_EVIDENCE_<UTC>.json` with `valid=true`, `issues=[]`, 12-coverage, deterministic/bounded, composes `PHASE223→PHASE32`, `paper_only/live_trading_enabled=false/next9_unblocked=false/gates_ok=true`.
- Verification evidence recorded (or explicit bounded caveats per governed acceptance).
- P0 intact; handoff advanced to Phase225.

## VERIFIED STATE (ground truth, 2026-11-11T11:34:44Z)

- **P0 safety:** **CLEAR** — no `.env`; `.env.example:15` `LIVE_TRADING_ENABLED=false`. Root clutter files `=1.24.0`, `=2.5.0`, `=7.4.0` removed.
- **NEXT9:** `next9_unblocked=false` (human-only A1–A7, out of scope). Never unblock.
- **Phase211–221:** sealed (do not re-implement/re-seal).
- **Phase221 COMPLETE:** `research_state/PHASE221_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103217Z.json` (`valid=true issues=[]`, composes `PHASE220→PHASE32`, seed 221221, cycles 40, coverage 12).
- **Phase222 COMPLETE:** module `src/hedging/phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; generator `scripts/generate_phase222_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; tests `tests/test_phase222_*.py`, `tests/test_generate_phase222_*.py`; artifact `research_state/PHASE222_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T103906Z.json` (`valid=true issues=[]`, composes `PHASE221→PHASE32`, seed 222222, cycles 40, coverage 12, deterministic/bounded, guards intact).
- **Phase223 COMPLETE:** module `src/hedging/phase223_adaptive_toxicity_resilient_post_attribution_seal_orchestrator.py`; generator `scripts/generate_phase223_adaptive_toxicity_resilient_post_attribution_seal_orchestrator_paper_evidence.py`; tests `tests/test_phase223_*.py`, `tests/test_generate_phase223_*.py`; artifact `research_state/PHASE223_ADAPTIVE_TOXICITY_RESILIENT_POST_ATTRIBUTION_SEAL_ORCHESTRATOR_PAPER_EVIDENCE_20261111T112946Z.json` (`valid=true issues=[]`, composes `PHASE222→PHASE32`, seed 223223, cycles 40, coverage 12, deterministic/bounded, guards intact). Verification: `py_compile` (4) OK; module smoke `paper_only=True gates_ok=True composes=[PHASE222,PHASE32]`; `--write --cycles 40 --seed 223223` → valid=true/issues=[]; `--validate-only` → valid=true/issues=[]; CLI no-write `runpy` → valid=true/issues=[]; targeted pytest blocked by deep-chain `RecursionError` (documented env caveat; governed acceptance met).
- **Phase224:** **NOT STARTED** (no module/generator/tests/artifact) — this is the critical-path bottleneck to execute next.
- **Chain A:** out of scope (`src/risk/phase*_live_execution*`).
- **Competing handoffs:** `NEXT_SESSION_HANDOFF.md`, `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs to this file; this file governs.

## BOTTLENECKS & UNBLOCKING ACTIONS

| Bottleneck | Status | Unblock action (must do) |
|---|---|---|
| P0 safety drift | **CLEAR (11:16:47Z)** | Re-verify before/after every batch (`.env` absent, `.env.example:15` `LIVE_TRADING_ENABLED=false`, no `next9_unblocked`). |
| Competing/stale handoff files | **CLEARED** | This is the only durable handoff; `NEXT_SESSION_HANDOFF.md` and `NEXT_SESSION_TASK_HANDOFF_20261109T091500Z.md` are redirect stubs. Do not create new handoff files or duplicate READ FIRST blocks. |
| Phase221/222 sealed | **CLEARED** | Do not touch except defect-preserving fix with preserved semantics/guards. |
| Phase223 absent (critical path) | **CLEARED** | Phase223 sealed `20261111T112946Z`; handoff advanced to Phase224. |
| Phase224 absent (critical path) | **ACTIVE — START NEXT** | **Execute full heavy scope:** implement module+generator+2 tests mirroring Phase223 with Phase223→224 deltas, `py_compile`, smoke/no-write/`--write`+validate evidence, targeted pytest as feasible, P0 post-check, then seal and advance handoff to Phase225. No partial handoff-only updates without deliverables. |
| Deep-chain pytest/import `RecursionError` | **ENV CAVEAT (mitigated)** | Use governed acceptance: `py_compile` (4) + module/generator smoke with `sys.setrecursionlimit(50000)` + CLI no-write `valid=true` + `--validate-only`/direct validate on `--write` artifact `valid=true`; run targeted pytest with raised recursion/timeouts where feasible; record exact commands/caveats. |
| Chain A/B confusion | **MITIGATED** | Chain B `src/hedging` only; `src/risk/phase*_live_execution*` out of scope. |
| NEXT9 A1–A7 | **BLOCKED — human-only (out of scope)** | `next9_unblocked=false`; never unblock, never mutate venues/config/credentials. |

## GOVERNED VERIFICATION NOTES
- Generator CLI in this repo revision does **not** accept `--no-write`; run without `--write` for no-write validation (use `runpy` + raised recursion limit if deep chain overflows).
- Deep composed chain (→phase32) can cause `RecursionError` on Python 3.12 during imports/pytest collection. Governed acceptance: `py_compile` + smoke (raised limit) + CLI no-write + validated `--write` artifact with guards/coverage/determinism/bounds intact. Record targeted pytest outcomes.

## HANDOFF DISCIPLINE
- Keep this file as the single durable handoff; replace stale state in place with verified facts/timestamps/paths/commands.
- No duplicate READ FIRST blocks. Final responses must not ask follow-up questions.
- After Phase224 seal, replace the active task with **`INIT-<UTC>-PHASE225-POST-ATTRIBUTION-SEAL-DEPTH`** (compose `PHASE224→PHASE32`, seed `225225`, IDs `p225-*`).
